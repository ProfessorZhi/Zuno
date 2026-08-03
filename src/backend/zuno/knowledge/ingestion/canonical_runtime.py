from __future__ import annotations

"""PHASE22 canonical ingestion runtime (GAP-B1 / GAP-B2).

Drives the real synthetic corpus path end to end with real IDs and real
verification:

    Source Upload
    -> Security / Classification
    -> Object Staged (MinIO staging key, hash verified)
    -> MinIO Object Commit (durable adapter + PostgreSQL object manifest)
    -> PostgreSQL Source Fact / Document / DocumentVersion Fact
    -> Canonical Document IR (real ParseGateway)
    -> Chunk facts (knowledge_chunks)
    -> Entity / Directed Relation facts (deterministic extraction over the
       real graph handoff payload, persisted as a hash-verified object
       artifact under the tenant/workspace object scope)
    -> KnowledgeVersion fact (knowledge_domain_versions)

State machine (recorded as tenant-scoped PostgreSQL domain state events in
``ingestion_outbox_events`` — idempotent, queryable, no migration needed):

    accepted -> object_staged -> object_committed -> canonical_ir_ready
              -> knowledge_version_ready

Failure states: security_denied, credential_blocked, object_commit_failed,
canonicalization_failed, reconciliation_required.

``indexes_visible`` and ``snapshot_activated`` are explicitly forbidden here:
they belong to the index-visibility and snapshot-activation workers.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import re
from typing import Any

from sqlalchemy import Engine

from zuno.knowledge.ingestion.contracts import CanonicalDocumentIR, ParseDocumentRequest
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.knowledge.ingestion.router import build_index_handoff_payload
from zuno.knowledge.ingestion.source_object_commit import (
    SourceObjectCommitError,
    SourceObjectCommitRuntime,
)
from zuno.knowledge.storage.canonical_facts import (
    CANONICAL_INGESTION_FACTS_EVENT_TYPE,
    CanonicalFactsMissing,
    CanonicalIngestionFactsStore,
)
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_json, canonical_sha256
from zuno.platform.database.ingestion import IngestionUnitOfWork
from zuno.platform.database.knowledge.domain import (
    KnowledgeRepository,
    KnowledgeUnitOfWork,
    KnowledgeVersionDraft,
)
from zuno.platform.storage.binding import assert_binding_is_production_durable
from zuno.platform.storage.durable import DurableMinioObjectStore
from zuno.platform.storage.object_store import ObjectHashMismatchError

PACKAGE_A_PARSE_CONTRACT_NAME = "zuno.ingestion.parse.requested"
PACKAGE_A_PARSE_REQUESTED_TOPIC = "ingestion.parse.requested"

# --- Canonical ingestion state machine ---------------------------------------

CANONICAL_STATE_ACCEPTED = "accepted"
CANONICAL_STATE_OBJECT_STAGED = "object_staged"
CANONICAL_STATE_OBJECT_COMMITTED = "object_committed"
CANONICAL_STATE_IR_READY = "canonical_ir_ready"
CANONICAL_STATE_KV_READY = "knowledge_version_ready"

CANONICAL_FAILURE_SECURITY_DENIED = "security_denied"
CANONICAL_FAILURE_CREDENTIAL_BLOCKED = "credential_blocked"
CANONICAL_FAILURE_OBJECT_COMMIT_FAILED = "object_commit_failed"
CANONICAL_FAILURE_CANONICALIZATION_FAILED = "canonicalization_failed"
CANONICAL_FAILURE_RECONCILIATION_REQUIRED = "reconciliation_required"

# States this worker must never write (owned by downstream workers).
FORBIDDEN_CANONICAL_STATES = ("indexes_visible", "snapshot_activated")

CANONICAL_STATE_SEQUENCE: dict[str, int] = {
    CANONICAL_STATE_ACCEPTED: 1,
    CANONICAL_STATE_OBJECT_STAGED: 2,
    CANONICAL_STATE_OBJECT_COMMITTED: 3,
    CANONICAL_STATE_IR_READY: 4,
    CANONICAL_STATE_KV_READY: 5,
    CANONICAL_FAILURE_SECURITY_DENIED: 90,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED: 91,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED: 92,
    CANONICAL_FAILURE_CANONICALIZATION_FAILED: 93,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED: 94,
}

CANONICAL_INGESTION_SUCCESS_STATES = (
    CANONICAL_STATE_ACCEPTED,
    CANONICAL_STATE_OBJECT_STAGED,
    CANONICAL_STATE_OBJECT_COMMITTED,
    CANONICAL_STATE_IR_READY,
    CANONICAL_STATE_KV_READY,
)
CANONICAL_INGESTION_FAILURE_STATES = (
    CANONICAL_FAILURE_SECURITY_DENIED,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
    CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
)

CANONICAL_STATE_TRANSITIONS: dict[str, tuple[str, ...]] = {
    CANONICAL_STATE_ACCEPTED: (
        CANONICAL_STATE_OBJECT_STAGED,
        CANONICAL_FAILURE_SECURITY_DENIED,
        CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    ),
    CANONICAL_STATE_OBJECT_STAGED: (
        CANONICAL_STATE_OBJECT_COMMITTED,
        CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
    ),
    CANONICAL_STATE_OBJECT_COMMITTED: (
        CANONICAL_STATE_IR_READY,
        CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    ),
    CANONICAL_STATE_IR_READY: (CANONICAL_STATE_KV_READY,),
    CANONICAL_STATE_KV_READY: (),
    CANONICAL_FAILURE_SECURITY_DENIED: (),
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED: (),
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED: (),
    CANONICAL_FAILURE_CANONICALIZATION_FAILED: (),
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED: (),
}


def validate_canonical_state_transition(from_state: str, to_state: str) -> None:
    """Pure state machine guard; raises on illegal or forbidden transitions."""
    if to_state in FORBIDDEN_CANONICAL_STATES:
        raise ValueError(
            f"canonical ingestion must not write {to_state!r}: it is owned by "
            "the index-visibility / snapshot-activation workers"
        )
    if from_state not in CANONICAL_STATE_TRANSITIONS:
        raise ValueError(f"unknown canonical ingestion state: {from_state!r}")
    if to_state not in CANONICAL_STATE_TRANSITIONS[from_state]:
        raise ValueError(
            f"illegal canonical ingestion transition: {from_state!r} -> {to_state!r}"
        )


def canonical_state_sequence(state: str) -> int:
    if state not in CANONICAL_STATE_SEQUENCE:
        raise ValueError(f"unknown canonical ingestion state: {state!r}")
    return CANONICAL_STATE_SEQUENCE[state]


def canonical_run_id(*, tenant_id: str, workspace_id: str, source_id: str) -> str:
    return f"canonical-ingest:{tenant_id}:{workspace_id}:{source_id}"


# --- Security / classification gate -------------------------------------------

@dataclass(frozen=True, slots=True)
class IngestionSecurityVerdict:
    decision: str  # "allow" | "deny"
    reason: str


DENIED_CLASSIFICATIONS = frozenset({"classification:forbidden", "classification:denied"})


class IngestionSecurityClassifier:
    """Deterministic upload security / classification gate.

    Mirrors the module-02 contract: Security owns the decision, Input executes
    and records it. The gate validates that the upload carries a security
    epoch and a classification, and denies known-forbidden classifications.
    """

    def __init__(self, denied_classifications: frozenset[str] = DENIED_CLASSIFICATIONS) -> None:
        self.denied_classifications = denied_classifications

    def evaluate(
        self,
        *,
        classification_ref: str,
        security_epoch_ref: str,
        principal_id: str | None,
    ) -> IngestionSecurityVerdict:
        if not str(security_epoch_ref or "").strip():
            return IngestionSecurityVerdict(
                decision="deny", reason="security_epoch_ref_missing"
            )
        if not str(classification_ref or "").strip():
            return IngestionSecurityVerdict(
                decision="deny", reason="classification_ref_missing"
            )
        if str(classification_ref).strip() in self.denied_classifications:
            return IngestionSecurityVerdict(
                decision="deny", reason="classification_forbidden"
            )
        return IngestionSecurityVerdict(decision="allow", reason="classification_allowed")


# --- Commands and receipts -----------------------------------------------------

@dataclass(frozen=True, slots=True)
class CanonicalSourceIngestCommand:
    tenant_id: str
    workspace_id: str
    principal_id: str
    source_id: str
    filename: str
    mime_type: str
    content: bytes
    classification_ref: str
    security_epoch_ref: str
    knowledge_space_id: str
    corpus_manifest_ref: str
    trace_id: str
    bucket: str | None = None
    deadline_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class CanonicalGraphFactsArtifact:
    object_ref: str
    object_manifest_ref: str
    manifest_hash: str
    entity_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CanonicalIngestionReceipt:
    run_id: str
    state: str
    tenant_id: str
    workspace_id: str
    source_id: str
    source_sha256: str
    object_ref: str | None
    object_manifest_ref: str | None
    object_manifest_hash: str | None
    document_id: str | None
    document_version_id: str | None
    parse_plan_id: str | None
    parse_job_id: str | None
    parse_snapshot_id: str | None
    canonical_ir_ref: str | None
    chunk_ids: tuple[str, ...] = ()
    knowledge_version_id: str | None = None
    graph_facts: CanonicalGraphFactsArtifact | None = None
    idempotent: bool = False
    failure_code: str | None = None
    events: tuple[dict[str, Any], ...] = field(default_factory=tuple)


class CanonicalIngestionConflictError(RuntimeError):
    pass


class CanonicalIngestionError(RuntimeError):
    pass


# --- Entity / directed relation extraction -------------------------------------

_ENTITY_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]{2,}\b")


def _stable_id(*parts: str, prefix: str, length: int = 16) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:length]}"


def extract_canonical_graph_facts(
    *,
    tenant_id: str,
    workspace_id: str,
    knowledge_version_id: str,
    graphrag_documents: list[dict[str, Any]],
) -> dict[str, Any]:
    """Deterministic entity / directed-relation extraction over the real graph
    handoff payload (the same graphrag documents the graph index adapter
    consumes).

    Entities are capitalized tokens anchored to their chunk; relations are
    directed edges between consecutive distinct entities in source text order
    (kind ``co_occurs``). All IDs are content-derived and stable across reruns.
    """
    entities: dict[str, dict[str, Any]] = {}
    relations: dict[str, dict[str, Any]] = {}
    ordered_documents = sorted(
        graphrag_documents,
        key=lambda document: str(document.get("chunk_id") or ""),
    )
    for document in ordered_documents:
        chunk_id = str(document.get("chunk_id") or "")
        content = str(document.get("content") or "")
        span = dict(document.get("source_span") or {})
        source_span_ref = str(
            span.get("ref")
            or span.get("source_span_ref")
            or document.get("source_span_ref")
            or f"source-span:{chunk_id}"
        )
        occurrences: list[tuple[int, str]] = []
        for match in _ENTITY_TOKEN_RE.finditer(content):
            occurrences.append((match.start(), match.group()))
        chunk_entities: list[str] = []
        for position, name in sorted(occurrences):
            if name in chunk_entities:
                continue
            chunk_entities.append(name)
            entity_ref = _stable_id(
                tenant_id, workspace_id, knowledge_version_id, name,
                prefix="entity",
            )
            entities.setdefault(
                entity_ref,
                {
                    "entity_ref": entity_ref,
                    "name": name,
                    "chunk_id": chunk_id,
                    "source_span_ref": source_span_ref,
                },
            )
        for from_name, to_name in zip(chunk_entities, chunk_entities[1:]):
            if from_name == to_name:
                continue
            from_ref = _stable_id(
                tenant_id, workspace_id, knowledge_version_id, from_name,
                prefix="entity",
            )
            to_ref = _stable_id(
                tenant_id, workspace_id, knowledge_version_id, to_name,
                prefix="entity",
            )
            relation_ref = _stable_id(
                tenant_id, workspace_id, knowledge_version_id,
                from_ref, "co_occurs", to_ref,
                prefix="relation",
            )
            relations.setdefault(
                relation_ref,
                {
                    "relation_ref": relation_ref,
                    "from_ref": from_ref,
                    "to_ref": to_ref,
                    "kind": "co_occurs",
                    "chunk_id": chunk_id,
                    "source_span_ref": source_span_ref,
                },
            )
    return {
        "schema_version": "canonical-graph-facts-v1",
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "knowledge_version_id": knowledge_version_id,
        "entities": [
            entities[entity_ref]
            for entity_ref in sorted(entities)
        ],
        "relations": [
            relations[relation_ref]
            for relation_ref in sorted(relations)
        ],
    }


# --- Runtime ------------------------------------------------------------------

class Phase22CanonicalIngestionRuntime:
    """Canonical ingestion runtime for the PHASE22 synthetic corpus."""

    def __init__(
        self,
        *,
        engine: Engine,
        object_store: DurableMinioObjectStore | None,
        bucket: str,
        worker_id: str = "phase22-cc-b1-b2",
        security_classifier: IngestionSecurityClassifier | None = None,
    ) -> None:
        if object_store is not None:
            assert_binding_is_production_durable(object_store)
        if not str(bucket or "").strip():
            raise ValueError("canonical ingestion bucket must not be empty")
        self.engine = engine
        self.object_store = object_store
        self.bucket = bucket
        self.worker_id = worker_id
        self.classifier = security_classifier or IngestionSecurityClassifier()
        self.commit_runtime = SourceObjectCommitRuntime()
        self.facts = CanonicalIngestionFactsStore(engine)

    # --- entry point -----------------------------------------------------------

    def ingest(self, command: CanonicalSourceIngestCommand) -> CanonicalIngestionReceipt:
        tenant_id = command.tenant_id
        workspace_id = command.workspace_id
        run_id = canonical_run_id(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=command.source_id,
        )
        source_sha256 = hashlib.sha256(command.content).hexdigest()
        replay = self._load_replay(
            run_id=run_id,
            tenant_id=tenant_id,
            source_id=command.source_id,
            source_sha256=source_sha256,
        )
        if replay is not None:
            return replay
        if self.object_store is None:
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code="object_store_binding_missing",
                detail="no production object store binding configured",
            )
        verdict = self.classifier.evaluate(
            classification_ref=command.classification_ref,
            security_epoch_ref=command.security_epoch_ref,
            principal_id=command.principal_id,
        )
        if verdict.decision != "allow":
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_SECURITY_DENIED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code=f"security_denied:{verdict.reason}",
                detail=verdict.reason,
            )
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=CANONICAL_STATE_ACCEPTED,
            source_id=command.source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={
                "classification_ref": command.classification_ref,
                "security_epoch_ref": command.security_epoch_ref,
                "knowledge_space_id": command.knowledge_space_id,
                "corpus_manifest_ref": command.corpus_manifest_ref,
            },
        )
        # --- stage ----------------------------------------------------------------
        committed_object_name = self._object_name(command)
        try:
            ticket = self.object_store.stage(
                bucket=self.bucket,
                committed_object_name=committed_object_name,
                content=command.content,
            )
        except Exception as exc:  # noqa: BLE001 - physical failure maps to state
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code="object_stage_failed",
                detail=str(exc),
            )
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=CANONICAL_STATE_OBJECT_STAGED,
            source_id=command.source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={"object_ref": ticket.object_ref},
        )
        # --- commit ----------------------------------------------------------------
        try:
            committed_receipt = self.object_store.commit(ticket)
        except ObjectHashMismatchError as exc:
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code="object_hash_mismatch",
                detail=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code="object_commit_failed",
                detail=str(exc),
            )
        # --- PostgreSQL source / document facts + parse request ----------------------
        try:
            source_commit = self.commit_runtime.commit_from_physical_receipt(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                source_id=command.source_id,
                filename=command.filename,
                mime_type=command.mime_type,
                owner_id=command.principal_id,
                committed_receipt=committed_receipt,
                object_manifest_ref=(
                    f"object-manifest:s3://{committed_receipt.bucket}/"
                    f"{committed_receipt.object_name}"
                ),
                classification_ref=command.classification_ref,
                security_epoch_ref=command.security_epoch_ref,
                expected_sha256=source_sha256,
                expected_size_bytes=len(command.content),
                expected_object_prefix=f"{tenant_id}/{workspace_id}/",
            )
        except SourceObjectCommitError as exc:
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code="object_receipt_validation_failed",
                detail=str(exc),
            )
        document_version_id = f"document-version:{command.source_id}:1"
        parse_plan_id = f"parse-plan:{command.source_id}:1"
        parse_job_id = f"parse-job:{command.source_id}:1"
        idempotency_key = f"parse:{tenant_id}:{workspace_id}:{source_sha256}:1"
        envelope = self._parse_requested_envelope(
            command=command,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            parse_job_id=parse_job_id,
            object_ref=source_commit.object_ref,
            object_manifest_ref=source_commit.object_manifest_ref,
            content_hash=source_sha256,
            size_bytes=len(command.content),
            idempotency_key=idempotency_key,
        )
        with IngestionUnitOfWork(self.engine) as repo:
            source = repo.record_source_object(
                source_object_id=command.source_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                filename=command.filename,
                mime_type=command.mime_type,
                declared_format=self._declared_format(command.mime_type, command.filename),
                storage_uri=source_commit.object_ref,
                object_manifest_ref=source_commit.object_manifest_ref,
                source_sha256=source_sha256,
                size_bytes=len(command.content),
                classification_ref=command.classification_ref,
                security_epoch_ref=command.security_epoch_ref,
            )
            document = repo.record_document_version(
                document_version_id=document_version_id,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                source_object_id=source.ref,
                version_no=1,
                content_hash=source_sha256,
                metadata={
                    "filename": command.filename,
                    "mime_type": command.mime_type,
                    "corpus_manifest_ref": command.corpus_manifest_ref,
                },
                immutability_ref=f"immutability:{document_version_id}",
            )
            plan = repo.record_parse_plan(
                parse_plan_id=parse_plan_id,
                tenant_id=tenant_id,
                document_version_id=document.ref,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref="parser-policy:phase22-canonical",
                parser_bundle={"parser": "native_markdown", "version": "phase22-canonical-v1"},
                quality_policy_ref="quality-policy:phase22-canonical",
                security_decision_ref=command.classification_ref,
            )
            job = repo.record_parse_job(
                parse_job_id=parse_job_id,
                tenant_id=tenant_id,
                parse_plan_id=plan.ref,
                document_version_id=document.ref,
                idempotency_key=idempotency_key,
                status="queued",
            )
            repo.enqueue_parse_requested(envelope=envelope)
            attempt = repo.claim_parse_attempt_lease(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                source_object_id=command.source_id,
                document_version_id=document.ref,
                parse_plan_id=plan.ref,
                parse_job_id=job.ref,
                worker_id=self.worker_id,
                idempotency_key=f"{idempotency_key}:attempt:1",
                security_epoch_ref=command.security_epoch_ref,
                lease_ttl_seconds=60,
            )
            parse_attempt_id = attempt.ref
            fencing_token = int(attempt.payload_hash or "0")
            repo.mark_parse_attempt_running(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=job.ref,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
            )
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=CANONICAL_STATE_OBJECT_COMMITTED,
            source_id=command.source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={
                "object_ref": source_commit.object_ref,
                "object_manifest_ref": source_commit.object_manifest_ref,
                "document_version_id": document.ref,
                "parse_job_id": job.ref,
                "outbox_event_id": envelope.message_id,
            },
        )
        # --- canonical parse ----------------------------------------------------------
        try:
            canonical_document = self._parse_committed_source(
                command=command,
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                source_sha256=source_sha256,
                source_commit=source_commit,
                document_version_id=document.ref,
                parse_plan_id=plan.ref,
                parse_job_id=job.ref,
                parse_attempt_id=parse_attempt_id,
                idempotency_key=idempotency_key,
            )
        except CanonicalIngestionError as exc:
            with IngestionUnitOfWork(self.engine) as repo:
                repo.fail_parse_attempt(
                    parse_attempt_id=parse_attempt_id,
                    parse_job_id=job.ref,
                    tenant_id=tenant_id,
                    worker_id=self.worker_id,
                    fencing_token=fencing_token,
                    status="failed",
                    failure_code=exc.args[0] if exc.args else "canonicalization_failed",
                )
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_CANONICALIZATION_FAILED,
                source_id=command.source_id,
                source_sha256=source_sha256,
                failure_code=exc.args[0] if exc.args else "canonicalization_failed",
                detail=str(exc),
            )
        parse_snapshot_id = f"parse-snapshot:{command.source_id}:1"
        with IngestionUnitOfWork(self.engine) as repo:
            snapshot = repo.record_parse_snapshot(
                parse_snapshot_id=parse_snapshot_id,
                tenant_id=tenant_id,
                parse_job_id=job.ref,
                parse_attempt_id=parse_attempt_id,
                document_version_id=document.ref,
                canonical_ir=canonical_document.model_dump(mode="json"),
                canonical_ir_ref=f"canonical-ir:{parse_snapshot_id}",
                canonical_ir_schema_ref=canonical_document.metadata.ir_schema_version,
                parser_id=canonical_document.metadata.parser_id,
                parser_version=canonical_document.metadata.parser_version,
            )
            repo.record_quality_decision(
                quality_decision_id=f"quality:{parse_snapshot_id}",
                tenant_id=tenant_id,
                parse_snapshot_id=snapshot.ref,
                coverage_score=1.0,
                confidence_score=1.0,
                decision="publish",
            )
            repo.commit_parse_attempt_if_current(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=job.ref,
                tenant_id=tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                domain_commit_ref=(
                    f"domain-commit:{parse_attempt_id}:{snapshot.ref}"
                ),
            )
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=CANONICAL_STATE_IR_READY,
            source_id=command.source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={
                "parse_snapshot_id": snapshot.ref,
                "canonical_ir_ref": f"canonical-ir:{parse_snapshot_id}",
                "ir_schema_version": canonical_document.metadata.ir_schema_version,
            },
        )
        # --- knowledge version + chunk facts -------------------------------------------
        handoff = build_index_handoff_payload(canonical_document)
        knowledge_version_id, chunk_ids = self._record_knowledge_version_facts(
            command=command,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            document=canonical_document,
            document_version_id=document.ref,
            source_sha256=source_sha256,
            handoff=handoff,
        )
        # --- entity / directed relation facts artifact ----------------------------------
        graph_facts = extract_canonical_graph_facts(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            graphrag_documents=handoff.graphrag_documents,
        )
        artifact = self._commit_graph_facts_artifact(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=knowledge_version_id,
            graph_facts=graph_facts,
        )
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=CANONICAL_STATE_KV_READY,
            source_id=command.source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={
                "knowledge_version_id": knowledge_version_id,
                "chunk_ids": list(chunk_ids),
                "chunk_count": len(chunk_ids),
                "entity_count": len(graph_facts["entities"]),
                "relation_count": len(graph_facts["relations"]),
                "graph_facts_object_ref": artifact.object_ref,
            },
        )
        return self._receipt_from_run(
            run_id=run_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=command.source_id,
            source_sha256=source_sha256,
            document_id=command.source_id,
            document_version_id=document.ref,
            parse_plan_id=plan.ref,
            parse_job_id=job.ref,
            parse_snapshot_id=snapshot.ref,
            knowledge_version_id=knowledge_version_id,
            chunk_ids=chunk_ids,
            graph_facts=artifact,
            state=CANONICAL_STATE_KV_READY,
            object_ref=source_commit.object_ref,
            object_manifest_ref=source_commit.object_manifest_ref,
            object_manifest_hash=committed_receipt.content_hash,
            idempotent=False,
        )

    # --- readback -----------------------------------------------------------------

    def get_run(self, *, run_id: str, tenant_id: str) -> CanonicalIngestionReceipt:
        """Re-read a run from the PostgreSQL ledger and facts."""
        states = self.facts.run_state_facts(tenant_id=tenant_id, run_id=run_id)
        if not states:
            raise CanonicalFactsMissing(
                f"canonical ingestion run has no ledger facts: {run_id}"
            )
        last_state = states[-1].state
        last_payload = states[-1].payload
        source_id = str(last_payload.get("source_id") or "")
        source_sha256 = str(last_payload.get("source_sha256") or "")
        workspace_id = str(last_payload.get("workspace_id") or "")
        source = None
        if source_id:
            source = self.facts.source_object_fact_optional(
                tenant_id=tenant_id, source_id=source_id
            )
        knowledge_version_id = (
            str(last_payload.get("knowledge_version_id") or "")
            if last_state == CANONICAL_STATE_KV_READY
            else None
        )
        chunk_ids: tuple[str, ...] = ()
        graph_facts = None
        if last_state == CANONICAL_STATE_KV_READY:
            chunk_ids = tuple(
                str(item) for item in (last_payload.get("chunk_ids") or [])
            )
            graph_facts = self._graph_facts_artifact_from_ledger(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_version_id=knowledge_version_id,
            )
        document_version_id = (
            f"document-version:{source.source_object_id}:1"
            if source is not None
            else None
        )
        parse_snapshot_id = (
            f"parse-snapshot:{source.source_object_id}:1"
            if source is not None
            else None
        )
        return CanonicalIngestionReceipt(
            run_id=run_id,
            state=last_state,
            tenant_id=tenant_id,
            workspace_id=workspace_id or (source.workspace_id if source else ""),
            source_id=source_id,
            source_sha256=source_sha256,
            object_ref=source.storage_uri if source is not None else None,
            object_manifest_ref=source.object_manifest_ref if source is not None else None,
            object_manifest_hash=source.source_sha256 if source is not None else None,
            document_id=source.source_object_id if source is not None else None,
            document_version_id=document_version_id,
            parse_plan_id=(
                f"parse-plan:{source.source_object_id}:1"
                if source is not None
                else None
            ),
            parse_job_id=(
                f"parse-job:{source.source_object_id}:1"
                if source is not None
                else None
            ),
            parse_snapshot_id=parse_snapshot_id,
            canonical_ir_ref=(
                f"canonical-ir:{parse_snapshot_id}"
                if parse_snapshot_id is not None
                else None
            ),
            chunk_ids=chunk_ids,
            knowledge_version_id=knowledge_version_id,
            graph_facts=graph_facts,
            failure_code=str(last_payload.get("failure_code") or ""),
            idempotent=True,
            events=tuple(
                {
                    "state": state_fact.state,
                    "outbox_event_id": state_fact.outbox_event_id,
                    "payload_hash": state_fact.payload_hash,
                }
                for state_fact in states
            ),
        )

    def reconcile(self, *, run_id: str, tenant_id: str) -> CanonicalIngestionReceipt:
        """Reconcile a run whose physical world may disagree with its ledger.

        Any unknown side effect (physical object present without a ledger
        state, ledger says committed but the manifest/readback disagrees)
        transitions the run to ``reconciliation_required``.
        """
        states = self.facts.run_state_facts(tenant_id=tenant_id, run_id=run_id)
        if not states:
            raise CanonicalIngestionError(
                "reconciliation_required: run has no ledger facts"
            )
        last_state = states[-1].state
        if last_state in CANONICAL_INGESTION_FAILURE_STATES:
            return self.get_run(run_id=run_id, tenant_id=tenant_id)
        payload = states[-1].payload
        source_id = str(payload.get("source_id") or "")
        source_sha256 = str(payload.get("source_sha256") or "")
        workspace_id = str(payload.get("workspace_id") or "")
        source = self.facts.source_object_fact_optional(
            tenant_id=tenant_id, source_id=source_id
        )
        if source is None:
            return self._fail(
                run_id=run_id,
                tenant_id=tenant_id,
                state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
                source_id=source_id,
                source_sha256=source_sha256,
                workspace_id=workspace_id,
                failure_code="unknown_side_effect_source_missing",
                detail="ledger has states but no PostgreSQL source fact",
            )
        if canonical_state_sequence(last_state) >= canonical_state_sequence(
            CANONICAL_STATE_OBJECT_COMMITTED
        ):
            manifest = self._manifest(source.storage_uri)
            if manifest is None or manifest.visibility not in {"visible", "restored"}:
                return self._fail(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
                    source_id=source_id,
                    source_sha256=source_sha256,
                    workspace_id=workspace_id,
                    failure_code="object_manifest_missing",
                    detail=f"manifest for {source.storage_uri} is not visible",
                )
            if str(manifest.content_hash) != str(source_sha256):
                return self._fail(
                    run_id=run_id,
                    tenant_id=tenant_id,
                    state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
                    source_id=source_id,
                    source_sha256=source_sha256,
                    workspace_id=workspace_id,
                    failure_code="object_manifest_hash_mismatch",
                    detail="manifest hash disagrees with source fact hash",
                )
            if self.object_store is not None:
                try:
                    bucket, object_name = _split_object_ref(source.storage_uri)
                    content = self.object_store.store.read_object(
                        bucket=bucket, object_name=object_name
                    )
                    observed_hash = hashlib.sha256(content).hexdigest()
                except Exception as exc:  # noqa: BLE001
                    return self._fail(
                        run_id=run_id,
                        tenant_id=tenant_id,
                        state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
                        source_id=source_id,
                        source_sha256=source_sha256,
                        workspace_id=workspace_id,
                        failure_code="object_readback_failed",
                        detail=f"committed object readback failed: {exc}",
                    )
                if observed_hash != str(source_sha256):
                    return self._fail(
                        run_id=run_id,
                        tenant_id=tenant_id,
                        state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
                        source_id=source_id,
                        source_sha256=source_sha256,
                        workspace_id=workspace_id,
                        failure_code="object_bytes_mismatch",
                        detail="committed object bytes disagree with source fact hash",
                    )
        return self.get_run(run_id=run_id, tenant_id=tenant_id)

    # --- internal helpers ------------------------------------------------------------

    def _record_state_event(
        self,
        *,
        run_id: str,
        tenant_id: str,
        state: str,
        source_id: str,
        source_sha256: str,
        workspace_id: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        sequence = canonical_state_sequence(state)
        payload = {
            "run_id": run_id,
            "state": state,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id or "",
            "source_id": source_id,
            "source_sha256": source_sha256,
            **(detail or {}),
        }
        outbox_event_id = _bounded_id(
            f"outbox:{run_id}:{sequence:02d}:", state, budget=150
        )
        with IngestionUnitOfWork(self.engine) as repo:
            repo.enqueue_outbox_event(
                outbox_event_id=outbox_event_id,
                tenant_id=tenant_id,
                aggregate_ref=run_id,
                event_type="ingestion.canonical_ingestion.state_changed",
                payload=payload,
                idempotency_key=_bounded_id(f"{run_id}:", state, budget=120),
            )

    def _fail(
        self,
        *,
        run_id: str,
        tenant_id: str,
        state: str,
        source_id: str,
        source_sha256: str,
        failure_code: str,
        detail: str,
        workspace_id: str | None = None,
    ) -> CanonicalIngestionReceipt:
        self._record_state_event(
            run_id=run_id,
            tenant_id=tenant_id,
            state=state,
            source_id=source_id,
            source_sha256=source_sha256,
            workspace_id=workspace_id,
            detail={"failure_code": failure_code, "detail": detail},
        )
        return CanonicalIngestionReceipt(
            run_id=run_id,
            state=state,
            tenant_id=tenant_id,
            workspace_id=workspace_id or "",
            source_id=source_id,
            source_sha256=source_sha256,
            object_ref=None,
            object_manifest_ref=None,
            object_manifest_hash=None,
            document_id=None,
            document_version_id=None,
            parse_plan_id=None,
            parse_job_id=None,
            parse_snapshot_id=None,
            canonical_ir_ref=None,
            failure_code=failure_code,
            idempotent=False,
        )

    def _load_replay(
        self,
        *,
        run_id: str,
        tenant_id: str,
        source_id: str,
        source_sha256: str,
    ) -> CanonicalIngestionReceipt | None:
        source = self.facts.source_object_fact_optional(
            tenant_id=tenant_id, source_id=source_id
        )
        if source is None:
            return None
        if str(source.source_sha256) != source_sha256:
            raise CanonicalIngestionConflictError(
                f"immutable SourceObject {source_id} cannot change content hash"
            )
        states = self.facts.run_state_facts(tenant_id=tenant_id, run_id=run_id)
        if not states:
            return None
        return self.get_run(run_id=run_id, tenant_id=tenant_id)

    def _parse_committed_source(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        tenant_id: str,
        workspace_id: str,
        source_sha256: str,
        source_commit: Any,
        document_version_id: str,
        parse_plan_id: str,
        parse_job_id: str,
        parse_attempt_id: str,
        idempotency_key: str,
    ) -> CanonicalDocumentIR:
        bucket, object_name = _split_object_ref(source_commit.object_ref)
        try:
            content = self.object_store.store.read_object(
                bucket=bucket, object_name=object_name
            )
        except Exception as exc:  # noqa: BLE001
            raise CanonicalIngestionError(
                f"object_readback_failed: {exc}"
            ) from exc
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != source_sha256 or len(content) != len(command.content):
            raise CanonicalIngestionError(
                "object_bytes_mismatch: MinIO readback does not match source hash"
            )
        request = ParseDocumentRequest(
            document_id=command.source_id,
            source_id=command.source_id,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            parse_job_id=parse_job_id,
            parse_attempt_id=parse_attempt_id,
            parse_idempotency_key=idempotency_key,
            source_object_ref=source_commit.object_ref,
            source_object_manifest={
                "object_manifest_ref": source_commit.object_manifest_ref,
                "content_hash": source_sha256,
                "size_bytes": len(command.content),
                "parser_policy_ref": "parser-policy:phase22-canonical",
                "lineage_ref": (
                    f"lineage:{command.source_id}:{document_version_id}"
                ),
                "workspace_id": workspace_id,
                "classification_ref": command.classification_ref,
                "security_epoch_ref": command.security_epoch_ref,
            },
            workspace_id=workspace_id,
            source_uri=source_commit.object_ref,
            mime_type=command.mime_type,
            source_bytes=content,
            hash=source_sha256,
            security_policy_ref=command.classification_ref,
            security_epoch_ref=command.security_epoch_ref,
        )
        result = ParseGateway.submit_parse_job(request)
        if result.status != "succeeded" or result.document is None:
            failure = result.failure
            raise CanonicalIngestionError(
                "canonicalization_failed: "
                f"{failure.failure_classification if failure else result.status}: "
                f"{failure.reason if failure else result.status}"
            )
        return result.document

    def _record_knowledge_version_facts(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        tenant_id: str,
        workspace_id: str,
        document: CanonicalDocumentIR,
        document_version_id: str,
        source_sha256: str,
        handoff: Any,
    ) -> tuple[str, tuple[str, ...]]:
        chunk_documents = sorted(
            handoff.bm25_documents,
            key=lambda item: str(item.get("chunk_id") or ""),
        )
        chunk_ids = tuple(str(item.get("chunk_id") or "") for item in chunk_documents)
        with KnowledgeUnitOfWork(self.engine) as repo:
            version_no = repo.next_version_no(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_space_id=command.knowledge_space_id,
            )
            knowledge_version_id = (
                f"knowledge-version:{tenant_id}:{workspace_id}:"
                f"{command.knowledge_space_id}:{version_no}"
            )
            document_set = {command.source_id: source_sha256}
            source_span_manifest = {
                block.block_id: (
                    f"source-span:{document_version_id}:{block.block_id}"
                )
                for block in document.blocks
            }
            index_spec = {
                "chunk_policy_version": "citation_sized_with_parent_context",
                "parser_contract_version": document.metadata.ir_schema_version,
                "source_span_required": True,
                "index_kinds": ["bm25", "vector", "graph"],
            }
            repo.create_version(
                KnowledgeVersionDraft(
                    knowledge_version_id=knowledge_version_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_space_id=command.knowledge_space_id,
                    version_no=version_no,
                    document_set=document_set,
                    source_span_manifest=source_span_manifest,
                    index_spec=index_spec,
                    security_epoch_ref=command.security_epoch_ref,
                )
            )
            authority_ref = (
                f"authority:parser:{document.metadata.parser_id}:"
                f"{document.metadata.parser_version}"
            )
            for chunk in chunk_documents:
                metadata = dict(chunk.get("metadata") or {})
                span = dict(metadata.get("source_span") or {})
                block_id = str(metadata.get("block_id") or "")
                source_span_ref = (
                    str(span.get("ref") or "")
                    or f"source-span:{document_version_id}:{block_id}"
                )
                repo.append_chunk(
                    chunk_id=str(chunk["chunk_id"]),
                    tenant_id=tenant_id,
                    knowledge_version_id=knowledge_version_id,
                    document_version_id=document_version_id,
                    source_span_ref=source_span_ref,
                    chunk_payload=chunk,
                    acl_ref=str(metadata.get("acl_scope") or "workspace"),
                    authority_ref=authority_ref,
                )
        return knowledge_version_id, chunk_ids

    def _commit_graph_facts_artifact(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
        graph_facts: dict[str, Any],
    ) -> CanonicalGraphFactsArtifact:
        content = canonical_json(graph_facts).encode("utf-8")
        object_name = (
            f"{tenant_id}/{workspace_id}/canonical-graph-facts/"
            f"{knowledge_version_id}/graph-facts.json"
        )
        ticket = self.object_store.stage(
            bucket=self.bucket,
            committed_object_name=object_name,
            content=content,
        )
        receipt = self.object_store.commit(ticket)
        manifest_hash = hashlib.sha256(content).hexdigest()
        if receipt.content_hash != manifest_hash:
            raise CanonicalIngestionError(
                "graph facts artifact hash mismatch after commit"
            )
        object_ref = f"s3://{receipt.bucket}/{receipt.object_name}"
        object_manifest_ref = f"object-manifest:{object_ref}"
        facts_digest = hashlib.sha256(
            f"{tenant_id}:{knowledge_version_id}".encode("utf-8")
        ).hexdigest()[:20]
        payload = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "knowledge_version_id": knowledge_version_id,
            "object_ref": object_ref,
            "object_manifest_ref": object_manifest_ref,
            "manifest_hash": manifest_hash,
            "entity_count": len(graph_facts["entities"]),
            "relation_count": len(graph_facts["relations"]),
            "entity_ids": [item["entity_ref"] for item in graph_facts["entities"]],
            "relation_ids": [item["relation_ref"] for item in graph_facts["relations"]],
        }
        with IngestionUnitOfWork(self.engine) as repo:
            repo.enqueue_outbox_event(
                outbox_event_id=f"outbox:facts:{facts_digest}",
                tenant_id=tenant_id,
                aggregate_ref=_facts_aggregate_ref(
                    tenant_id=tenant_id, workspace_id=workspace_id
                ),
                event_type=CANONICAL_INGESTION_FACTS_EVENT_TYPE,
                payload=payload,
                idempotency_key=f"facts:{facts_digest}",
            )
        return CanonicalGraphFactsArtifact(
            object_ref=object_ref,
            object_manifest_ref=object_manifest_ref,
            manifest_hash=manifest_hash,
            entity_ids=tuple(
                item["entity_ref"] for item in graph_facts["entities"]
            ),
            relation_ids=tuple(
                item["relation_ref"] for item in graph_facts["relations"]
            ),
        )

    def _graph_facts_artifact_from_ledger(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_version_id: str,
    ) -> CanonicalGraphFactsArtifact | None:
        if not knowledge_version_id:
            return None
        event = self.facts.run_facts_event(
            tenant_id=tenant_id,
            run_id=_facts_aggregate_ref(
                tenant_id=tenant_id, workspace_id=workspace_id
            ),
        )
        if event is None:
            return None
        payload = event["payload"]
        if str(payload.get("knowledge_version_id")) != knowledge_version_id:
            return None
        return CanonicalGraphFactsArtifact(
            object_ref=str(payload["object_ref"]),
            object_manifest_ref=str(payload["object_manifest_ref"]),
            manifest_hash=str(payload["manifest_hash"]),
            entity_ids=tuple(str(item) for item in (payload.get("entity_ids") or [])),
            relation_ids=tuple(str(item) for item in (payload.get("relation_ids") or [])),
        )

    def _receipt_from_run(
        self,
        *,
        run_id: str,
        tenant_id: str,
        workspace_id: str,
        source_id: str,
        source_sha256: str,
        document_id: str,
        document_version_id: str,
        parse_plan_id: str,
        parse_job_id: str,
        parse_snapshot_id: str,
        knowledge_version_id: str | None,
        chunk_ids: tuple[str, ...],
        graph_facts: CanonicalGraphFactsArtifact | None,
        state: str,
        object_ref: str | None,
        object_manifest_ref: str | None,
        object_manifest_hash: str | None,
        idempotent: bool,
    ) -> CanonicalIngestionReceipt:
        states = self.facts.run_state_facts(tenant_id=tenant_id, run_id=run_id)
        return CanonicalIngestionReceipt(
            run_id=run_id,
            state=state,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=source_id,
            source_sha256=source_sha256,
            object_ref=object_ref,
            object_manifest_ref=object_manifest_ref,
            object_manifest_hash=object_manifest_hash,
            document_id=document_id,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            parse_job_id=parse_job_id,
            parse_snapshot_id=parse_snapshot_id,
            canonical_ir_ref=(
                f"canonical-ir:{parse_snapshot_id}" if parse_snapshot_id else None
            ),
            chunk_ids=chunk_ids,
            knowledge_version_id=knowledge_version_id,
            graph_facts=graph_facts,
            idempotent=idempotent,
            events=tuple(
                {
                    "state": state_fact.state,
                    "outbox_event_id": state_fact.outbox_event_id,
                    "payload_hash": state_fact.payload_hash,
                }
                for state_fact in states
            ),
        )

    @staticmethod
    def _object_name(command: CanonicalSourceIngestCommand) -> str:
        safe_name = command.filename.replace("\\", "/").split("/")[-1]
        return (
            f"{command.tenant_id}/{command.workspace_id}/source/"
            f"{command.source_id}/{safe_name}"
        )

    @staticmethod
    def _declared_format(mime_type: str, filename: str) -> str:
        lowered = filename.lower()
        if mime_type == "text/markdown" or lowered.endswith(".md"):
            return "markdown"
        if mime_type.startswith("text/"):
            return "text"
        return "unknown"

    def _parse_requested_envelope(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        document_version_id: str,
        parse_plan_id: str,
        parse_job_id: str,
        object_ref: str,
        object_manifest_ref: str,
        content_hash: str,
        size_bytes: int,
        idempotency_key: str,
    ) -> CrossModuleEnvelopeV1:
        payload = {
            "tenant_id": command.tenant_id,
            "workspace_id": command.workspace_id,
            "source_object_id": command.source_id,
            "document_version_id": document_version_id,
            "parse_plan_id": parse_plan_id,
            "parse_job_id": parse_job_id,
            "object_ref": object_ref,
            "object_manifest_ref": object_manifest_ref,
            "content_hash": content_hash,
            "size_bytes": size_bytes,
            "filename": command.filename,
            "mime_type": command.mime_type,
            "declared_format": self._declared_format(command.mime_type, command.filename),
            "classification_ref": command.classification_ref,
            "principal_id": command.principal_id,
            "parser_policy_ref": "parser-policy:phase22-canonical",
            "quality_policy_ref": "quality-policy:phase22-canonical",
            "security_decision_ref": command.classification_ref,
            "security_epoch_ref": command.security_epoch_ref,
            "max_attempts": 1,
        }
        now = datetime.now(timezone.utc)
        return CrossModuleEnvelopeV1(
            contract_name=PACKAGE_A_PARSE_CONTRACT_NAME,
            contract_version="v1",
            contract_bundle_version="wave1",
            message_id=f"outbox:{parse_job_id}",
            producer_module="workspace.file_upload",
            consumer_module="ingestion.parser_worker",
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            correlation_id=command.trace_id,
            idempotency_key=idempotency_key,
            aggregate_type="ParseJob",
            aggregate_id=parse_job_id,
            effective_security_epoch_ref=command.security_epoch_ref,
            trace_id=command.trace_id,
            data_classification=command.classification_ref,
            occurred_at=now,
            created_at=now,
            deadline_at=command.deadline_at,
            payload=payload,
            payload_hash=canonical_sha256(payload),
            payload_schema_hash=canonical_sha256(
                {"schema": "zuno.ingestion.parse.requested.v1"}
            ),
        )

    def _manifest(self, object_ref: str) -> Any | None:
        from zuno.platform.database.foundation import InfrastructureUnitOfWork

        with InfrastructureUnitOfWork(self.engine) as repository:
            return repository.object_manifest(object_ref=object_ref)


def _bounded_id(prefix: str, value: str, budget: int) -> str:
    """Deterministic identifier that fits the persistence column width."""
    candidate = f"{prefix}{value}"
    if len(candidate) <= budget:
        return candidate
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"{prefix}{digest}"


def _facts_aggregate_ref(*, tenant_id: str, workspace_id: str) -> str:
    digest = hashlib.sha256(
        f"{tenant_id}:{workspace_id}".encode("utf-8")
    ).hexdigest()[:20]
    return f"canonical-facts:{digest}"


def _split_object_ref(object_ref: str) -> tuple[str, str]:
    if not object_ref.startswith("s3://"):
        raise CanonicalIngestionError(f"invalid object ref: {object_ref}")
    remainder = object_ref[len("s3://"):]
    bucket, _, object_name = remainder.partition("/")
    if not bucket or not object_name:
        raise CanonicalIngestionError(f"invalid object ref: {object_ref}")
    return bucket, object_name


__all__ = [
    "CANONICAL_FAILURE_CANONICALIZATION_FAILED",
    "CANONICAL_FAILURE_CREDENTIAL_BLOCKED",
    "CANONICAL_FAILURE_OBJECT_COMMIT_FAILED",
    "CANONICAL_FAILURE_RECONCILIATION_REQUIRED",
    "CANONICAL_FAILURE_SECURITY_DENIED",
    "CANONICAL_INGESTION_FAILURE_STATES",
    "CANONICAL_INGESTION_SUCCESS_STATES",
    "CANONICAL_STATE_ACCEPTED",
    "CANONICAL_STATE_IR_READY",
    "CANONICAL_STATE_KV_READY",
    "CANONICAL_STATE_OBJECT_COMMITTED",
    "CANONICAL_STATE_OBJECT_STAGED",
    "CANONICAL_STATE_SEQUENCE",
    "CANONICAL_STATE_TRANSITIONS",
    "CanonicalGraphFactsArtifact",
    "CanonicalIngestionConflictError",
    "CanonicalIngestionError",
    "CanonicalIngestionReceipt",
    "CanonicalSourceIngestCommand",
    "FORBIDDEN_CANONICAL_STATES",
    "IngestionSecurityClassifier",
    "IngestionSecurityVerdict",
    "Phase22CanonicalIngestionRuntime",
    "canonical_run_id",
    "canonical_state_sequence",
    "extract_canonical_graph_facts",
    "validate_canonical_state_transition",
]
