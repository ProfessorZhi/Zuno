from __future__ import annotations

"""PHASE22 canonical ingestion runtime (GAP-B1 / GAP-B2 hardening).

Single canonical ingestion runtime. The state machine is declared in
:mod:`zuno.knowledge.storage.canonical_run_store` and every transition is
persisted atomically (read current -> validate transition -> update current
fact -> append history/outbox -> commit one UoW).

Security ownership: the runtime never issues or approves decisions. It only
validates a Security-owned decision (``security_authorization_decisions`` via
the Security repository's ``validate_pre_effect_authorization``) and fails
closed on missing, stale, mismatched or denied decisions.

Every step is idempotent and resume-safe: after a crash the runtime reads the
durable checkpoint (``canonical_ingestion_runs.current_state``) and continues
from the last completed step without duplicating objects, facts, attempts,
chunks, entities, relations, versions or outbox events. Unknown physical side
effects enter ``reconciliation_required``; failures only leave through
explicitly designed retry transitions.

Quality is measured by the existing deterministic quality contract
(``HumanReviewRuntime``); perfect scores are never manufactured.

Entity and directed-relation facts are consumed from the formal canonical IR
manifest (frozen extractor output) into PostgreSQL domain tables; Neo4j
remains an index/read-model owner.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any

from sqlalchemy import Engine, text

from zuno.knowledge.ingestion.contracts import CanonicalDocumentIR, ParseDocumentRequest, ParseJobSnapshot
from zuno.knowledge.ingestion.gateway import ParseGateway
from zuno.knowledge.ingestion.review import HumanReviewRuntime
from zuno.knowledge.ingestion.source_object_commit import (
    SourceObjectCommitError,
    SourceObjectCommitRuntime,
)
from zuno.knowledge.storage.canonical_facts import (
    CanonicalFactsMissing,
    CanonicalIngestionFactsStore,
    DocumentVersionFact,
    ParseSnapshotFact,
)
from zuno.knowledge.storage.canonical_run_store import (
    CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
    CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    CANONICAL_FAILURE_SECURITY_DENIED,
    CANONICAL_INGESTION_FAILURE_STATES,
    CANONICAL_INGESTION_SUCCESS_STATES,
    CANONICAL_STATE_ACCEPTED,
    CANONICAL_STATE_IR_READY,
    CANONICAL_STATE_KV_READY,
    CANONICAL_STATE_OBJECT_COMMITTED,
    CANONICAL_STATE_OBJECT_STAGED,
    CANONICAL_STATE_SEQUENCE,
    CANONICAL_STATE_TRANSITIONS,
    FORBIDDEN_CANONICAL_STATES,
    CanonicalIngestionRunStore,
    CanonicalRunStateConflict,
    CanonicalRunStateError,
    CanonicalRunStateTerminal,
    canonical_run_id,
    canonical_state_sequence,
    validate_canonical_state_transition,
)
from zuno.knowledge.storage.entity_relation_facts import (
    CanonicalEntityFact,
    CanonicalRelationFact,
    EntityRelationFactsStore,
)
from zuno.platform.contracts import CrossModuleEnvelopeV1, canonical_json, canonical_sha256
from zuno.platform.database.ingestion import IngestionPersistenceError, IngestionUnitOfWork
from zuno.platform.database.knowledge.domain import (
    KnowledgeRepository,
    KnowledgeUnitOfWork,
    KnowledgeVersionDraft,
)
from zuno.platform.security.persistence import SecurityUnitOfWork
from zuno.platform.storage.binding import assert_binding_is_production_durable
from zuno.platform.storage.durable import DurableMinioObjectStore
from zuno.platform.storage.object_store import ObjectHashMismatchError

PACKAGE_A_PARSE_CONTRACT_NAME = "zuno.ingestion.parse.requested"

# Official authority for the frozen canonical IR extractor output.
CANONICAL_IR_MANIFEST_AUTHORITY = "authority:canonical-ir-manifest:v1.0.0"

# Re-exported state machine symbols for backward compatibility.
__all__ = [
    "CANONICAL_FAILURE_CANONICALIZATION_FAILED",
    "CANONICAL_FAILURE_CREDENTIAL_BLOCKED",
    "CANONICAL_FAILURE_OBJECT_COMMIT_FAILED",
    "CANONICAL_FAILURE_OBJECT_STAGE_FAILED",
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
    "Phase22CanonicalIngestionRuntime",
    "canonical_run_id",
    "canonical_state_sequence",
    "validate_canonical_state_transition",
]

# --- Commands and receipts -----------------------------------------------------

SECURITY_INGESTION_ACTION = "ingestion.source.upload"


def canonical_security_resource_ref(
    *, tenant_id: str, workspace_id: str, source_id: str
) -> str:
    return f"ingestion:source:{tenant_id}:{workspace_id}:{source_id}"


@dataclass(frozen=True, slots=True)
class CanonicalSourceIngestCommand:
    tenant_id: str
    workspace_id: str
    principal_id: str
    source_id: str
    document_id: str
    filename: str
    mime_type: str
    content: bytes
    classification: str
    security_epoch_ref: str
    security_decision_ref: str
    knowledge_space_id: str
    corpus_manifest_ref: str
    source_set_ref: str
    trace_id: str
    bucket: str | None = None
    deadline_at: datetime | None = None


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
    parse_snapshot_id: str | None
    canonical_ir_ref: str | None
    knowledge_version_id: str | None
    chunk_ids: tuple[str, ...] = ()
    entity_ids: tuple[str, ...] = ()
    relation_ids: tuple[str, ...] = ()
    state_version: int = 0
    attempt_number: int = 1
    idempotent: bool = False
    failure_code: str | None = None
    transitions: tuple[dict[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CanonicalCorpusReceipt:
    tenant_id: str
    workspace_id: str
    knowledge_space_id: str
    corpus_hash: str
    source_count: int
    document_count: int
    chunk_count: int
    entity_count: int
    relation_count: int
    knowledge_version_id: str
    run_ids: tuple[str, ...]
    source_ids: tuple[str, ...]
    document_version_ids: tuple[str, ...]
    chunk_ids: tuple[str, ...]
    entity_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    reconciled: bool
    mismatch: tuple[str, ...] = ()


class CanonicalIngestionConflictError(RuntimeError):
    pass


class CanonicalIngestionError(RuntimeError):
    pass


class CanonicalSecurityDenied(CanonicalIngestionError):
    pass


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
        fault_hook: Any = None,
    ) -> None:
        if object_store is not None:
            assert_binding_is_production_durable(object_store)
        if not str(bucket or "").strip():
            raise ValueError("canonical ingestion bucket must not be empty")
        self.engine = engine
        self.object_store = object_store
        self.bucket = bucket
        self.worker_id = worker_id
        # test-only extension point: invoked after each durable step with the
        # step name; raising simulates a crash at that boundary (same pattern
        # as DurableMinioObjectStore._after_physical_commit)
        self.fault_hook = fault_hook
        self.commit_runtime = SourceObjectCommitRuntime()
        self.review_runtime = HumanReviewRuntime()
        self.runs = CanonicalIngestionRunStore(engine)
        self.facts = CanonicalIngestionFactsStore(engine)
        self.entities_relations = EntityRelationFactsStore(engine)
        self._corpus_manifest: dict[str, Any] | None = None
        self._corpus_sources: list[dict[str, Any]] | None = None

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
        payload_hash = self._command_payload_hash(command, source_sha256)
        self.runs.ensure_run(
            run_id=run_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_set_ref=command.source_set_ref,
            corpus_manifest_ref=command.corpus_manifest_ref,
            idempotency_key=f"{run_id}:{source_sha256}",
            payload_hash=payload_hash,
        )
        current = self.runs.current_fact(run_id=run_id, tenant_id=tenant_id)
        return self._resume_from_checkpoint(command=command, current=current)

    # --- checkpoint resume -------------------------------------------------------

    def _resume_from_checkpoint(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        current: Any,
    ) -> CanonicalIngestionReceipt:
        # Idempotency contract: a replayed run must carry the same command
        # identity (content hash included); different content for the same
        # immutable SourceObject is a conflict, never a silent replay.
        expected_payload_hash = self._command_payload_hash(
            command, self._source_hash(command)
        )
        if current.payload_hash != expected_payload_hash:
            raise CanonicalIngestionConflictError(
                f"immutable SourceObject {command.source_id} cannot change "
                "content hash or identity"
            )
        state = current.current_state
        if state == CANONICAL_STATE_KV_READY:
            return self._receipt_from_owner_tables(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                workspace_id=current.workspace_id,
                source_id=command.source_id,
                idempotent=True,
            )
        if state in CANONICAL_INGESTION_FAILURE_STATES:
            return self._receipt_from_owner_tables(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                workspace_id=current.workspace_id,
                source_id=command.source_id,
                idempotent=True,
            )
        if state == CANONICAL_STATE_ACCEPTED:
            try:
                self._validate_security_decision(command=command, current=current)
            except CanonicalSecurityDenied as exc:
                self.runs.transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    to_state=CANONICAL_FAILURE_SECURITY_DENIED,
                    expected_from_state=CANONICAL_STATE_ACCEPTED,
                    source_id=command.source_id,
                    source_hash=self._source_hash(command),
                    last_error_code=str(exc),
                    last_error_detail=str(exc),
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            if self.object_store is None:
                self.runs.transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    to_state=CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
                    expected_from_state=CANONICAL_STATE_ACCEPTED,
                    source_id=command.source_id,
                    source_hash=self._source_hash(command),
                    last_error_code="object_store_binding_missing",
                    last_error_detail="no production object store binding configured",
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            # --- stage ------------------------------------------------------------
            try:
                ticket = self.object_store.stage(
                    bucket=self.bucket,
                    committed_object_name=self._object_name(command),
                    content=command.content,
                )
            except Exception as exc:  # noqa: BLE001 - physical failure maps to state
                self.runs.transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    to_state=CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
                    expected_from_state=CANONICAL_STATE_ACCEPTED,
                    source_id=command.source_id,
                    source_hash=self._source_hash(command),
                    last_error_code="object_stage_failed",
                    last_error_detail=str(exc),
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            self.runs.transition(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                to_state=CANONICAL_STATE_OBJECT_STAGED,
                expected_from_state=CANONICAL_STATE_ACCEPTED,
                source_id=command.source_id,
                source_hash=self._source_hash(command),
                outbox_payload={"object_ref": ticket.object_ref},
            )
            state = CANONICAL_STATE_OBJECT_STAGED
            self._fire_fault_hook("object_staged")
        if state == CANONICAL_STATE_OBJECT_STAGED:
            # --- commit ------------------------------------------------------------
            try:
                staged = self.object_store.stage(
                    bucket=self.bucket,
                    committed_object_name=self._object_name(command),
                    content=command.content,
                )
                committed_receipt = self.object_store.commit(staged)
            except ObjectHashMismatchError as exc:
                self._fail_transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    expected_from_state=CANONICAL_STATE_OBJECT_STAGED,
                    to_state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                    command=command,
                    failure_code="object_hash_mismatch",
                    detail=str(exc),
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            except Exception as exc:  # noqa: BLE001
                self._fail_transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    expected_from_state=CANONICAL_STATE_OBJECT_STAGED,
                    to_state=CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
                    command=command,
                    failure_code="object_commit_failed",
                    detail=str(exc),
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            self.runs.transition(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                to_state=CANONICAL_STATE_OBJECT_COMMITTED,
                expected_from_state=CANONICAL_STATE_OBJECT_STAGED,
                source_id=command.source_id,
                source_hash=self._source_hash(command),
                outbox_payload={"object_ref": f"s3://{committed_receipt.bucket}/{committed_receipt.object_name}"},
            )
            state = CANONICAL_STATE_OBJECT_COMMITTED
            self._fire_fault_hook("object_committed")
        if state == CANONICAL_STATE_OBJECT_COMMITTED:
            # --- committed object manifest repair (idempotent) --------------------------
            # The object_committed checkpoint promises a visible manifest;
            # resume verifies it and re-commits idempotently when the manifest
            # is missing (physical object present, manifest uncertain).
            self._ensure_committed_object(command=command)
            # --- source/document facts + parse ----------------------------------------
            try:
                document_fact, parse_snapshot = self._ensure_source_document_and_ir(
                    command=command,
                    source_sha256=self._source_hash(command),
                )
            except CanonicalIngestionError as exc:
                self._fail_transition(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    expected_from_state=CANONICAL_STATE_OBJECT_COMMITTED,
                    to_state=CANONICAL_FAILURE_CANONICALIZATION_FAILED,
                    command=command,
                    failure_code=exc.args[0] if exc.args else "canonicalization_failed",
                    detail=str(exc),
                )
                return self._receipt_from_owner_tables(
                    run_id=current.run_id,
                    tenant_id=current.tenant_id,
                    workspace_id=current.workspace_id,
                    source_id=command.source_id,
                    idempotent=False,
                )
            self.runs.transition(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                to_state=CANONICAL_STATE_IR_READY,
                expected_from_state=CANONICAL_STATE_OBJECT_COMMITTED,
                source_id=command.source_id,
                source_hash=self._source_hash(command),
                outbox_payload={
                    "document_version_id": document_fact.document_version_id,
                    "parse_snapshot_id": parse_snapshot.parse_snapshot_id,
                },
            )
            state = CANONICAL_STATE_IR_READY
            self._fire_fault_hook("canonical_ir_ready")
        if state == CANONICAL_STATE_IR_READY:
            # --- knowledge facts finalize (corpus binding) -----------------------------
            knowledge_version_id = self._ensure_document_knowledge_facts(
                command=command,
                source_sha256=self._source_hash(command),
            )
            self._fire_fault_hook("knowledge_facts_committed")
            self.runs.transition(
                run_id=current.run_id,
                tenant_id=current.tenant_id,
                to_state=CANONICAL_STATE_KV_READY,
                expected_from_state=CANONICAL_STATE_IR_READY,
                source_id=command.source_id,
                source_hash=self._source_hash(command),
                knowledge_version_id=knowledge_version_id,
                outbox_payload={
                    "knowledge_version_id": knowledge_version_id,
                },
            )
            self._fire_fault_hook("knowledge_version_ready")
        return self._receipt_from_owner_tables(
            run_id=current.run_id,
            tenant_id=current.tenant_id,
            workspace_id=current.workspace_id,
            source_id=command.source_id,
            idempotent=False,
        )

    def retry(self, command: CanonicalSourceIngestCommand) -> CanonicalIngestionReceipt:
        """Explicit retry: plan and facts remain valid, only execution failed.

        Retries are only legal through the declared retry transitions
        (``object_stage_failed -> object_staged``,
        ``object_commit_failed -> object_committed``,
        ``canonicalization_failed -> canonical_ir_ready``).
        """
        run_id = canonical_run_id(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            source_id=command.source_id,
        )
        current = self.runs.current_fact(run_id=run_id, tenant_id=command.tenant_id)
        retry_targets = {
            CANONICAL_FAILURE_OBJECT_STAGE_FAILED: CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_FAILURE_OBJECT_COMMIT_FAILED: CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_FAILURE_CANONICALIZATION_FAILED: CANONICAL_STATE_OBJECT_COMMITTED,
        }
        target = retry_targets.get(current.current_state)
        if target is None:
            raise CanonicalIngestionError(
                f"run {run_id} is not retryable from {current.current_state!r}"
            )
        self.runs.transition(
            run_id=run_id,
            tenant_id=command.tenant_id,
            to_state=target,
            expected_from_state=current.current_state,
            attempt_number=current.attempt_number + 1,
            source_id=command.source_id,
            source_hash=self._source_hash(command),
        )
        refreshed = self.runs.current_fact(run_id=run_id, tenant_id=command.tenant_id)
        return self._resume_from_checkpoint(command=command, current=refreshed)

    def reconcile(self, *, run_id: str, tenant_id: str) -> CanonicalIngestionReceipt:
        """Verify the physical world against the durable state; unknown side
        effects transition the run to ``reconciliation_required``."""
        current = self.runs.current_fact(run_id=run_id, tenant_id=tenant_id)
        state = current.current_state
        if state in CANONICAL_INGESTION_FAILURE_STATES:
            return self._receipt_from_owner_tables(
                run_id=run_id,
                tenant_id=tenant_id,
                workspace_id=current.workspace_id,
                source_id=current.source_set_ref or "",
                idempotent=True,
            )
        source = self.facts.source_object_fact_optional(
            tenant_id=tenant_id, source_id=self._source_id_from_run(current)
        )
        if source is not None and self.object_store is not None:
            bucket, object_name = _split_object_ref(source.storage_uri)
            try:
                manifest = self.facts.object_manifest_fact_optional(
                    object_ref=source.storage_uri
                )
            except CanonicalFactsMissing:
                manifest = None
            if manifest is None or manifest.visibility not in {"visible", "restored"}:
                return self._reconcile_fail(
                    current=current,
                    tenant_id=tenant_id,
                    failure_code="object_manifest_missing",
                    detail="committed object manifest is not visible",
                )
            if str(manifest.content_hash) != str(source.source_sha256):
                return self._reconcile_fail(
                    current=current,
                    tenant_id=tenant_id,
                    failure_code="object_manifest_hash_mismatch",
                    detail="manifest hash disagrees with source fact hash",
                )
            try:
                observed = self.object_store.store.read_object(
                    bucket=bucket, object_name=object_name
                )
                observed_hash = hashlib.sha256(observed).hexdigest()
            except Exception as exc:  # noqa: BLE001
                return self._reconcile_fail(
                    current=current,
                    tenant_id=tenant_id,
                    failure_code="object_readback_failed",
                    detail=f"committed object readback failed: {exc}",
                )
            if observed_hash != str(source.source_sha256):
                return self._reconcile_fail(
                    current=current,
                    tenant_id=tenant_id,
                    failure_code="object_bytes_mismatch",
                    detail="committed object bytes disagree with source fact hash",
                )
        return self._receipt_from_owner_tables(
            run_id=run_id,
            tenant_id=tenant_id,
            workspace_id=current.workspace_id,
            source_id=self._source_id_from_run(current),
            idempotent=True,
        )

    def resume_after_reconcile(
        self, command: CanonicalSourceIngestCommand, *, to_state: str
    ) -> CanonicalIngestionReceipt:
        """Explicit reconciliation-resume transition after unknown side effects
        are confirmed and facts re-verified."""
        run_id = canonical_run_id(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            source_id=command.source_id,
        )
        current = self.runs.current_fact(run_id=run_id, tenant_id=command.tenant_id)
        if current.current_state != CANONICAL_FAILURE_RECONCILIATION_REQUIRED:
            raise CanonicalIngestionError(
                f"run {run_id} is not awaiting reconciliation "
                f"({current.current_state!r})"
            )
        self.runs.transition(
            run_id=run_id,
            tenant_id=command.tenant_id,
            to_state=to_state,
            expected_from_state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
            attempt_number=current.attempt_number + 1,
            source_id=command.source_id,
            source_hash=self._source_hash(command),
        )
        refreshed = self.runs.current_fact(run_id=run_id, tenant_id=command.tenant_id)
        return self._resume_from_checkpoint(command=command, current=refreshed)

    # --- security ownership (Task D) ----------------------------------------------

    def _validate_security_decision(self, *, command: CanonicalSourceIngestCommand, current: Any) -> None:
        """Validate a Security-owned decision; fail closed on any mismatch.

        The runtime never issues decisions. The decision must exist, belong to
        the tenant, bind the exact source content hash, carry an active
        security epoch, be an ALLOW for the ingestion action, and reference the
        exact source resource scope.
        """
        source_hash = self._source_hash(command)
        decision_row = self._security_decision_row(
            decision_id=command.security_decision_ref,
            tenant_id=command.tenant_id,
        )
        if decision_row is None:
            raise CanonicalSecurityDenied("security_decision_missing")
        if str(decision_row["decision"]) == "DENY":
            raise CanonicalSecurityDenied("security_decision_denied")
        if str(decision_row["action"]) != SECURITY_INGESTION_ACTION:
            raise CanonicalSecurityDenied("security_decision_action_mismatch")
        expected_resource = canonical_security_resource_ref(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            source_id=command.source_id,
        )
        if str(decision_row["resource_ref"]) != expected_resource:
            raise CanonicalSecurityDenied("security_decision_resource_mismatch")
        if str(decision_row["epoch_ref"]) != command.security_epoch_ref:
            raise CanonicalSecurityDenied("security_decision_epoch_mismatch")
        if str(decision_row["prepared_action_hash"] or "") != source_hash:
            raise CanonicalSecurityDenied("security_decision_action_hash_mismatch")
        principal = self._security_principal_row(
            principal_context_id=str(decision_row["principal_context_id"])
        )
        if principal is None or str(principal["tenant_id"]) != command.tenant_id:
            raise CanonicalSecurityDenied("security_decision_principal_scope_mismatch")
        if str(principal["user_principal_id"]) != command.principal_id:
            raise CanonicalSecurityDenied("security_decision_principal_mismatch")
        try:
            with SecurityUnitOfWork(self.engine) as repo:
                receipt = repo.validate_pre_effect_authorization(
                    decision_id=command.security_decision_ref,
                    tenant_id=command.tenant_id,
                    prepared_action_hash=source_hash,
                    require_approved_request=True,
                )
        except Exception as exc:  # noqa: BLE001 - Security owner rejects
            raise CanonicalSecurityDenied(f"security_decision_invalid:{exc}") from exc
        if receipt.decision != "USE_ONLY":
            raise CanonicalSecurityDenied("security_decision_not_allow")

    def _security_decision_row(self, *, decision_id: str, tenant_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT decision_id, tenant_id, principal_context_id, epoch_ref,
                           resource_ref, action, decision, reason_code,
                           prepared_action_hash, decision_hash
                    FROM security_authorization_decisions
                    WHERE decision_id = :decision_id AND tenant_id = :tenant_id
                    """
                ),
                {"decision_id": decision_id, "tenant_id": tenant_id},
            ).mappings().first()
        return None if row is None else dict(row)

    def _security_principal_row(self, *, principal_context_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT principal_context_id, tenant_id, user_principal_id
                    FROM security_principal_contexts
                    WHERE principal_context_id = :principal_context_id
                    """
                ),
                {"principal_context_id": principal_context_id},
            ).mappings().first()
        return None if row is None else dict(row)

    # --- durable steps -----------------------------------------------------------

    def _ensure_source_document_and_ir(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        source_sha256: str,
    ) -> tuple[DocumentVersionFact, ParseSnapshotFact]:
        """Idempotent source/document facts + canonical IR parse.

        Checkpoint: existing parse snapshot for the document version. When the
        snapshot exists the whole step is skipped (facts reused).
        """
        existing_source = self.facts.source_object_fact_optional(
            tenant_id=command.tenant_id, source_id=command.source_id
        )
        if existing_source is not None:
            if str(existing_source.source_sha256) != source_sha256:
                raise CanonicalIngestionConflictError(
                    f"immutable SourceObject {command.source_id} cannot change "
                    "content hash"
                )
            document = self.facts.document_version_fact_for_source(
                tenant_id=command.tenant_id, source_id=command.source_id
            )
            try:
                snapshot = self.facts.parse_snapshot_fact_for_document(
                    tenant_id=command.tenant_id,
                    document_version_id=document.document_version_id,
                )
                return document, snapshot
            except CanonicalFactsMissing:
                pass
            document_version_id = document.document_version_id
            parse_plan_id, parse_job_id = self._ensure_plan_and_job(
                command=command,
                source_sha256=source_sha256,
                document_version_id=document_version_id,
                source_object_id=command.source_id,
            )
        else:
            document_version_id = f"document-version:{command.source_id}:1"
            parse_plan_id = f"parse-plan:{command.source_id}:1"
            parse_job_id = f"parse-job:{command.source_id}:1"
            idempotency_key = f"parse:{command.tenant_id}:{command.workspace_id}:{source_sha256}:1"
            envelope = self._parse_requested_envelope(
                command=command,
                document_version_id=document_version_id,
                parse_plan_id=parse_plan_id,
                parse_job_id=parse_job_id,
                object_ref=f"s3://{self.bucket}/{self._object_name(command)}",
                object_manifest_ref=(
                    f"object-manifest:s3://{self.bucket}/{self._object_name(command)}"
                ),
                content_hash=source_sha256,
                size_bytes=len(command.content),
                idempotency_key=idempotency_key,
            )
            with IngestionUnitOfWork(self.engine) as repo:
                source = repo.record_source_object(
                    source_object_id=command.source_id,
                    tenant_id=command.tenant_id,
                    workspace_id=command.workspace_id,
                    filename=command.filename,
                    mime_type=command.mime_type,
                    declared_format=self._declared_format(command.mime_type, command.filename),
                    storage_uri=f"s3://{self.bucket}/{self._object_name(command)}",
                    object_manifest_ref=(
                        f"object-manifest:s3://{self.bucket}/{self._object_name(command)}"
                    ),
                    source_sha256=source_sha256,
                    size_bytes=len(command.content),
                    classification_ref=command.classification,
                    security_epoch_ref=command.security_epoch_ref,
                )
                document = repo.record_document_version(
                    document_version_id=document_version_id,
                    tenant_id=command.tenant_id,
                    workspace_id=command.workspace_id,
                    source_object_id=source.ref,
                    version_no=1,
                    content_hash=source_sha256,
                    metadata={
                        "filename": command.filename,
                        "mime_type": command.mime_type,
                        "corpus_manifest_ref": command.corpus_manifest_ref,
                        "document_id": command.document_id,
                    },
                    immutability_ref=f"immutability:{document_version_id}",
                )
                plan = repo.record_parse_plan(
                    parse_plan_id=parse_plan_id,
                    tenant_id=command.tenant_id,
                    document_version_id=document.ref,
                    parser_route={"primary": "native_markdown"},
                    parser_policy_ref="parser-policy:phase22-canonical",
                    parser_bundle={"parser": "native_markdown", "version": "phase22-canonical-v1"},
                    quality_policy_ref="quality-policy:phase22-canonical",
                    security_decision_ref=command.security_decision_ref,
                )
                job = repo.record_parse_job(
                    parse_job_id=parse_job_id,
                    tenant_id=command.tenant_id,
                    parse_plan_id=plan.ref,
                    document_version_id=document.ref,
                    idempotency_key=idempotency_key,
                    status="queued",
                )
                if not self._outbox_event_exists(envelope.message_id):
                    repo.enqueue_parse_requested(envelope=envelope)
            self._fire_fault_hook("source_document_facts_committed")
        # --- canonical parse (idempotent, fenced) -----------------------------------
        content = self._read_and_verify_object(command, source_sha256)
        attempt_id, fencing_token = self._ensure_parse_attempt(
            command=command,
            parse_job_id=parse_job_id,
            document_version_id=document_version_id,
            source_sha256=source_sha256,
        )
        request = ParseDocumentRequest(
            document_id=command.document_id,
            source_id=command.source_id,
            document_version_id=document_version_id,
            parse_plan_id=parse_plan_id,
            parse_job_id=parse_job_id,
            parse_attempt_id=attempt_id,
            parse_idempotency_key=(
                f"parse:{command.tenant_id}:{command.workspace_id}:{source_sha256}:1"
            ),
            source_object_ref=f"s3://{self.bucket}/{self._object_name(command)}",
            source_object_manifest={
                "object_manifest_ref": (
                    f"object-manifest:s3://{self.bucket}/{self._object_name(command)}"
                ),
                "content_hash": source_sha256,
                "size_bytes": len(command.content),
                "parser_policy_ref": "parser-policy:phase22-canonical",
                "lineage_ref": f"lineage:{command.source_id}:{document_version_id}",
                "workspace_id": command.workspace_id,
                "classification_ref": command.classification,
                "security_epoch_ref": command.security_epoch_ref,
            },
            workspace_id=command.workspace_id,
            source_uri=f"s3://{self.bucket}/{self._object_name(command)}",
            mime_type=command.mime_type,
            source_bytes=content,
            hash=source_sha256,
            security_policy_ref=command.security_decision_ref,
            security_epoch_ref=command.security_epoch_ref,
        )
        result = ParseGateway.submit_parse_job(request)
        if result.status != "succeeded" or result.document is None:
            failure = result.failure
            self._fail_parse_attempt(
                command=command,
                parse_job_id=parse_job_id,
                parse_attempt_id=attempt_id,
                fencing_token=fencing_token,
                failure_code=(
                    failure.failure_classification if failure else result.status
                ),
            )
            raise CanonicalIngestionError(
                "canonicalization_failed: "
                f"{failure.failure_classification if failure else result.status}: "
                f"{failure.reason if failure else result.status}"
            )
        parse_snapshot_id = f"parse-snapshot:{command.source_id}:1"
        with IngestionUnitOfWork(self.engine) as repo:
            snapshot = repo.record_parse_snapshot(
                parse_snapshot_id=parse_snapshot_id,
                tenant_id=command.tenant_id,
                parse_job_id=parse_job_id,
                parse_attempt_id=attempt_id,
                document_version_id=document_version_id,
                canonical_ir=result.document.model_dump(mode="json"),
                canonical_ir_ref=f"canonical-ir:{parse_snapshot_id}",
                canonical_ir_schema_ref=result.document.metadata.ir_schema_version,
                parser_id=result.document.metadata.parser_id,
                parser_version=result.document.metadata.parser_version,
            )
            parse_snapshot_model = ParseGateway.get_job_snapshot(result.job_id)
            quality_gate, _review_task = self.review_runtime.evaluate(
                document=result.document,
                parse_snapshot=parse_snapshot_model,
                security_epoch_ref=command.security_epoch_ref,
                reviewer_principal_id=command.principal_id,
                security_decision_ref=command.security_decision_ref,
                idempotency_key=(
                    f"quality:{command.tenant_id}:{command.source_id}:1"
                ),
                trace_id=command.trace_id,
            )
            measured_confidence = self._quality_metric(
                quality_gate, "min_block_confidence"
            )
            repo.record_quality_decision(
                quality_decision_id=f"quality:{parse_snapshot_id}",
                tenant_id=command.tenant_id,
                parse_snapshot_id=snapshot.ref,
                coverage_score=measured_confidence,
                confidence_score=measured_confidence,
                decision=(
                    "publish"
                    if HumanReviewRuntime.can_publish_snapshot(gate=quality_gate)
                    else "human_review"
                ),
                review_task_ref=quality_gate.review_task_id,
            )
            repo.commit_parse_attempt_if_current(
                parse_attempt_id=attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=command.tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                domain_commit_ref=f"domain-commit:{attempt_id}:{snapshot.ref}",
            )
            self._fire_fault_hook("parse_snapshot_committed")
        document_fact = self.facts.document_version_fact_for_source(
            tenant_id=command.tenant_id, source_id=command.source_id
        )
        snapshot_fact = self.facts.parse_snapshot_fact(
            tenant_id=command.tenant_id, parse_snapshot_id=parse_snapshot_id
        )
        return document_fact, snapshot_fact

    def _ensure_plan_and_job(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        source_sha256: str,
        document_version_id: str,
        source_object_id: str,
    ) -> tuple[str, str]:
        """Reuse plan/job rows when the source fact already exists (resume)."""
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT plan.parse_plan_id, job.parse_job_id
                    FROM ingestion_parse_plans AS plan
                    JOIN ingestion_parse_jobs AS job
                      ON job.parse_plan_id = plan.parse_plan_id
                    WHERE plan.document_version_id = :document_version_id
                      AND plan.tenant_id = :tenant_id
                    ORDER BY job.created_at
                    LIMIT 1
                    """
                ),
                {"document_version_id": document_version_id, "tenant_id": command.tenant_id},
            ).mappings().first()
        if row is not None:
            return str(row["parse_plan_id"]), str(row["parse_job_id"])
        plan_id = f"parse-plan:{source_object_id}:1"
        job_id = f"parse-job:{source_object_id}:1"
        idempotency_key = f"parse:{command.tenant_id}:{command.workspace_id}:{source_sha256}:1"
        with IngestionUnitOfWork(self.engine) as repo:
            plan = repo.record_parse_plan(
                parse_plan_id=plan_id,
                tenant_id=command.tenant_id,
                document_version_id=document_version_id,
                parser_route={"primary": "native_markdown"},
                parser_policy_ref="parser-policy:phase22-canonical",
                parser_bundle={"parser": "native_markdown", "version": "phase22-canonical-v1"},
                quality_policy_ref="quality-policy:phase22-canonical",
                security_decision_ref=command.security_decision_ref,
            )
            job = repo.record_parse_job(
                parse_job_id=job_id,
                tenant_id=command.tenant_id,
                parse_plan_id=plan.ref,
                document_version_id=document_version_id,
                idempotency_key=idempotency_key,
                status="queued",
            )
        return plan.ref, job.ref

    def _ensure_parse_attempt(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        parse_job_id: str,
        document_version_id: str,
        source_sha256: str,
    ) -> tuple[str, int]:
        """Claim or reuse the fenced parse attempt (no duplicate attempts)."""
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT parse_attempt_id, status, fencing_token
                    FROM ingestion_parse_attempts
                    WHERE parse_job_id = :parse_job_id
                    ORDER BY attempt_no
                    LIMIT 1
                    """
                ),
                {"parse_job_id": parse_job_id},
            ).mappings().first()
        if row is not None and str(row["status"]) in {"lease_claimed", "running"}:
            # crash-resume: the same fenced attempt continues
            parse_attempt_id = str(row["parse_attempt_id"])
            fencing_token = int(row["fencing_token"])
            with IngestionUnitOfWork(self.engine) as repo:
                repo.renew_parse_attempt_lease(
                    parse_attempt_id=parse_attempt_id,
                    parse_job_id=parse_job_id,
                    tenant_id=command.tenant_id,
                    worker_id=self.worker_id,
                    fencing_token=fencing_token,
                    lease_ttl_seconds=60,
                )
            return parse_attempt_id, fencing_token
        # first claim, or a previous attempt is terminal (failed/lease_lost):
        # a NEW attempt number is claimed (repo-compatible recovery semantics;
        # the parse snapshot uniqueness guard prevents duplicate snapshots)
        with IngestionUnitOfWork(self.engine) as repo:
            attempt = repo.claim_parse_attempt_lease(
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                source_object_id=command.source_id,
                document_version_id=document_version_id,
                parse_plan_id=f"parse-plan:{command.source_id}:1",
                parse_job_id=parse_job_id,
                worker_id=self.worker_id,
                idempotency_key=(
                    f"parse:{command.tenant_id}:{command.workspace_id}:"
                    f"{source_sha256}:1:attempt:1"
                ),
                security_epoch_ref=command.security_epoch_ref,
                lease_ttl_seconds=60,
            )
            parse_attempt_id = attempt.ref
            fencing_token = int(attempt.payload_hash or "0")
            repo.mark_parse_attempt_running(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=command.tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
            )
            return parse_attempt_id, fencing_token

    def _fail_parse_attempt(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        parse_job_id: str,
        parse_attempt_id: str,
        fencing_token: int,
        failure_code: str,
    ) -> None:
        with IngestionUnitOfWork(self.engine) as repo:
            repo.fail_parse_attempt(
                parse_attempt_id=parse_attempt_id,
                parse_job_id=parse_job_id,
                tenant_id=command.tenant_id,
                worker_id=self.worker_id,
                fencing_token=fencing_token,
                status="failed",
                failure_code=failure_code,
            )

    # --- knowledge facts (official manifest consumption) ----------------------------

    def _ensure_document_knowledge_facts(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        source_sha256: str,
    ) -> str:
        """Record this document's official chunk/entity/relation facts into the
        corpus knowledge version. The official manifest records are the frozen
        extractor output; every insert is idempotent."""
        manifest = self._require_corpus_manifest(command)
        knowledge_version_id = self._ensure_corpus_knowledge_version(
            command=command, manifest=manifest, source_sha256=source_sha256
        )
        chunks_by_id = {str(chunk["chunk_id"]): chunk for chunk in manifest.get("chunks", [])}
        document_chunks = [
            chunk
            for chunk in manifest.get("chunks", [])
            if str(chunk.get("document_id")) == command.document_id
        ]
        document_version_id = self._manifest_document_version_id(
            manifest=manifest, document_id=command.document_id
        )
        with KnowledgeUnitOfWork(self.engine) as repo:
            for chunk in document_chunks:
                chunk_id = str(chunk["chunk_id"])
                span_ref = f"source-span:{document_version_id}:{chunk_id}"
                repo.append_chunk(
                    chunk_id=chunk_id,
                    tenant_id=command.tenant_id,
                    knowledge_version_id=knowledge_version_id,
                    document_version_id=document_version_id,
                    source_span_ref=span_ref,
                    chunk_payload={
                        "chunk_id": chunk_id,
                        "text_hash": str(chunk["text_hash"]),
                        "ordinal": int(chunk.get("ordinal") or 0),
                    },
                    acl_ref=str(chunk.get("security_scope") or "workspace"),
                    authority_ref=CANONICAL_IR_MANIFEST_AUTHORITY,
                )
        # entity facts are corpus-level and idempotent: record ALL official
        # entities so that any relation (whose endpoints may be anchored in
        # other documents) has its from/to facts persisted regardless of the
        # per-document finalize order.
        for entity in manifest.get("entities", []):
            entity_ref = str(entity.get("entity_ref") or "")
            kind, _, name = entity_ref.partition(":")
            chunk_id = str(entity.get("chunk_id") or "")
            entity_document_id = str(entity.get("document_id") or "")
            entity_document_version = self._manifest_document_version_id(
                manifest=manifest, document_id=entity_document_id
            )
            span_ref = f"source-span:{entity_document_version}:{chunk_id}"
            self.entities_relations.record_entity_fact(
                entity_id=str(entity["entity_id"]),
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                knowledge_version_id=knowledge_version_id,
                entity_kind=kind or "unknown",
                canonical_name=name or entity_ref,
                source_chunk_id=chunk_id,
                source_span_ref=span_ref,
                authority_ref=CANONICAL_IR_MANIFEST_AUTHORITY,
            )
        # relation facts for this document (all entities already recorded)
        for relation in manifest.get("relations", []):
            if str(relation.get("document_id")) != command.document_id:
                continue
            evidence_chunks = relation.get("evidence_chunk_ids") or []
            chunk_id = str(evidence_chunks[0]) if evidence_chunks else ""
            span_ref = f"source-span:{document_version_id}:{chunk_id}"
            self.entities_relations.record_relation_fact(
                relation_id=str(relation["relation_id"]),
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                knowledge_version_id=knowledge_version_id,
                from_entity_id="entity::" + str(relation["from"]),
                to_entity_id="entity::" + str(relation["to"]),
                relation_kind=str(relation["kind"]),
                source_chunk_id=chunk_id,
                source_span_ref=span_ref,
                authority_ref=CANONICAL_IR_MANIFEST_AUTHORITY,
            )
        return knowledge_version_id

    def _ensure_corpus_knowledge_version(
        self,
        *,
        command: CanonicalSourceIngestCommand,
        manifest: dict[str, Any],
        source_sha256: str,
    ) -> str:
        """One corpus knowledge version, idempotent by document_set_hash."""
        document_set = self._corpus_document_set(command=command, manifest=manifest)
        document_set_hash = canonical_sha256(document_set)
        existing = self.facts.knowledge_version_for_document_set(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            knowledge_space_id=command.knowledge_space_id,
            document_set_hash=document_set_hash,
        )
        if existing is not None:
            return existing.knowledge_version_id
        source_span_manifest = {
            str(chunk["chunk_id"]): (
                f"source-span:{self._manifest_document_version_id(manifest=manifest, document_id=str(chunk['document_id']))}:{chunk['chunk_id']}"
            )
            for chunk in manifest.get("chunks", [])
        }
        corpus_hash = str(manifest.get("source_manifest_hash") or "")
        index_spec = {
            "corpus_hash": corpus_hash,
            "source_manifest_hash": corpus_hash,
            "chunk_policy_version": "canonical-ir-manifest-v1",
            "source_span_required": True,
            "index_kinds": ["bm25", "vector", "graph"],
        }
        with KnowledgeUnitOfWork(self.engine) as repo:
            version_no = repo.next_version_no(
                tenant_id=command.tenant_id,
                workspace_id=command.workspace_id,
                knowledge_space_id=command.knowledge_space_id,
            )
            knowledge_version_id = (
                f"knowledge-version:{command.tenant_id}:{command.workspace_id}:"
                f"{command.knowledge_space_id}:{version_no}"
            )
            repo.create_version(
                KnowledgeVersionDraft(
                    knowledge_version_id=knowledge_version_id,
                    tenant_id=command.tenant_id,
                    workspace_id=command.workspace_id,
                    knowledge_space_id=command.knowledge_space_id,
                    version_no=version_no,
                    document_set=document_set,
                    source_span_manifest=source_span_manifest,
                    index_spec=index_spec,
                    security_epoch_ref=command.security_epoch_ref,
                )
            )
        rechecked = self.facts.knowledge_version_for_document_set(
            tenant_id=command.tenant_id,
            workspace_id=command.workspace_id,
            knowledge_space_id=command.knowledge_space_id,
            document_set_hash=document_set_hash,
        )
        if rechecked is not None:
            return rechecked.knowledge_version_id
        return knowledge_version_id

    # --- official corpus orchestration (Task F) --------------------------------------

    def ingest_official_corpus(
        self,
        *,
        source_manifest: dict[str, Any],
        corpus_dir: Any,
        ir_manifest: dict[str, Any],
        security_decision_refs: dict[str, str],
        knowledge_space_id: str,
        security_epoch_ref: str,
        bucket: str | None = None,
        tenant_id: str | None = None,
        workspace_id: str | None = None,
    ) -> CanonicalCorpusReceipt:
        """Ingest the official synthetic corpus end to end.

        ``source_manifest`` is the frozen PR #107 source-upload manifest,
        ``ir_manifest`` the frozen canonical IR manifest, and ``corpus_dir``
        the directory holding the official corpus files. Security decisions
        are issued by the Security owner in advance (the runtime never issues
        them); ``security_decision_refs`` maps source_id -> decision_id.
        """
        effective_bucket = bucket or self.bucket
        self.load_corpus_sources(source_manifest)
        # Tenant/workspace are infrastructure scope columns; the corpus
        # identity (source ids, hashes, document ids) always comes from the
        # frozen manifest. A caller may pin the verification tenant to avoid
        # colliding with pre-existing candidate facts for the official tenant.
        tenant_id = tenant_id or str(source_manifest["sources"][0]["tenant_id"])
        workspace_id = workspace_id or str(source_manifest["sources"][0]["workspace_id"])
        corpus_hash = str(source_manifest["source_manifest_hash"])
        run_ids: list[str] = []
        source_ids: list[str] = []
        for source in source_manifest["sources"]:
            source_id = str(source["source_id"])
            document_id = str(source["document_id"])
            source_hash = str(source["source_hash"])
            decision_ref = security_decision_refs.get(source_id)
            if not decision_ref:
                raise CanonicalIngestionError(
                    f"missing Security-owned decision for {source_id}"
                )
            path = corpus_dir / str(source["source_path"])
            # The frozen manifest hashes were computed over LF-normalized
            # content; git autocrlf on Windows checkouts can materialize CRLF.
            # Normalize deterministically so the manifest contract holds
            # regardless of checkout line endings.
            content = path.read_bytes().replace(b"\r\n", b"\n")
            observed_hash = hashlib.sha256(content).hexdigest()
            if observed_hash != source_hash:
                raise CanonicalIngestionError(
                    f"corpus file hash mismatch for {source_id}: "
                    f"expected {source_hash}, observed {observed_hash}"
                )
            command = CanonicalSourceIngestCommand(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                principal_id=str(source.get("principal_id") or "principal:corpus-runner"),
                source_id=source_id,
                document_id=document_id,
                filename=str(source["source_path"]).rsplit("/", 1)[-1],
                mime_type=str(source.get("content_type") or "text/markdown").split(";")[0].strip(),
                content=content,
                classification=str(source.get("security_scope") or "global/open"),
                security_epoch_ref=security_epoch_ref,
                security_decision_ref=decision_ref,
                knowledge_space_id=knowledge_space_id,
                corpus_manifest_ref=corpus_hash,
                source_set_ref=f"corpus:{corpus_hash[:16]}",
                trace_id=f"trace:{source_id}",
                bucket=effective_bucket,
            )
            receipt = self.ingest(command)
            run_ids.append(receipt.run_id)
            source_ids.append(receipt.source_id)
            if receipt.state != CANONICAL_STATE_KV_READY:
                raise CanonicalIngestionError(
                    f"official corpus source {source_id} did not reach "
                    f"knowledge_version_ready: {receipt.state}"
                )
        return self.reconcile_official_corpus(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_space_id=knowledge_space_id,
            corpus_hash=corpus_hash,
            ir_manifest=ir_manifest,
            document_set={
                str(source["source_id"]): str(source["source_hash"])
                for source in source_manifest["sources"]
            },
            run_ids=tuple(run_ids),
            source_ids=tuple(source_ids),
        )

    def reconcile_official_corpus(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        knowledge_space_id: str,
        corpus_hash: str,
        ir_manifest: dict[str, Any],
        document_set: dict[str, str],
        run_ids: tuple[str, ...] = (),
        source_ids: tuple[str, ...] = (),
    ) -> CanonicalCorpusReceipt:
        """Reconcile the persisted facts against the official manifest counts."""
        expected_chunk_ids = tuple(
            sorted(str(chunk["chunk_id"]) for chunk in ir_manifest.get("chunks", []))
        )
        expected_entity_ids = tuple(
            sorted(str(entity["entity_id"]) for entity in ir_manifest.get("entities", []))
        )
        expected_relation_ids = tuple(
            sorted(str(relation["relation_id"]) for relation in ir_manifest.get("relations", []))
        )
        expected_document_ids = tuple(
            sorted(str(doc["document_id"]) for doc in ir_manifest.get("documents", []))
        )
        knowledge_version = self.facts.knowledge_version_for_document_set(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_space_id=knowledge_space_id,
            document_set_hash=canonical_sha256(document_set),
        )
        mismatch: list[str] = []
        if knowledge_version is None:
            mismatch.append("knowledge_version_missing")
            return CanonicalCorpusReceipt(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                knowledge_space_id=knowledge_space_id,
                corpus_hash=corpus_hash,
                source_count=len(source_ids),
                document_count=len(expected_document_ids),
                chunk_count=len(expected_chunk_ids),
                entity_count=len(expected_entity_ids),
                relation_count=len(expected_relation_ids),
                knowledge_version_id="",
                run_ids=run_ids,
                source_ids=source_ids,
                document_version_ids=(),
                chunk_ids=(),
                entity_ids=(),
                relation_ids=(),
                reconciled=False,
                mismatch=mismatch,
            )
        kv_id = knowledge_version.knowledge_version_id
        chunk_facts = self.facts.chunk_facts(tenant_id=tenant_id, knowledge_version_id=kv_id)
        entity_facts = self.entities_relations.entity_facts(
            tenant_id=tenant_id, workspace_id=workspace_id, knowledge_version_id=kv_id
        )
        relation_facts = self.entities_relations.relation_facts(
            tenant_id=tenant_id, workspace_id=workspace_id, knowledge_version_id=kv_id
        )
        observed_chunk_ids = tuple(sorted(fact.chunk_id for fact in chunk_facts))
        observed_entity_ids = tuple(sorted(fact.entity_id for fact in entity_facts))
        observed_relation_ids = tuple(sorted(fact.relation_id for fact in relation_facts))
        if observed_chunk_ids != expected_chunk_ids:
            mismatch.append("chunk_ids_mismatch")
        if observed_entity_ids != expected_entity_ids:
            mismatch.append("entity_ids_mismatch")
        if observed_relation_ids != expected_relation_ids:
            mismatch.append("relation_ids_mismatch")
        if len(source_ids) != len(expected_document_ids):
            mismatch.append("source_count_mismatch")
        return CanonicalCorpusReceipt(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_space_id=knowledge_space_id,
            corpus_hash=corpus_hash,
            source_count=len(source_ids),
            document_count=len(expected_document_ids),
            chunk_count=len(expected_chunk_ids),
            entity_count=len(expected_entity_ids),
            relation_count=len(expected_relation_ids),
            knowledge_version_id=kv_id,
            run_ids=run_ids,
            source_ids=source_ids,
            document_version_ids=(),
            chunk_ids=observed_chunk_ids,
            entity_ids=observed_entity_ids,
            relation_ids=observed_relation_ids,
            reconciled=not mismatch,
            mismatch=tuple(mismatch),
        )

    # --- readback (owner tables only) --------------------------------------------------

    def get_run(self, *, run_id: str, tenant_id: str) -> CanonicalIngestionReceipt:
        current = self.runs.current_fact(run_id=run_id, tenant_id=tenant_id)
        return self._receipt_from_owner_tables(
            run_id=run_id,
            tenant_id=tenant_id,
            workspace_id=current.workspace_id,
            source_id=self._source_id_from_run(current),
            idempotent=True,
        )

    def _receipt_from_owner_tables(
        self,
        *,
        run_id: str,
        tenant_id: str,
        workspace_id: str,
        source_id: str,
        idempotent: bool,
    ) -> CanonicalIngestionReceipt:
        current = self.runs.current_fact(run_id=run_id, tenant_id=tenant_id)
        source = self.facts.source_object_fact_optional(
            tenant_id=tenant_id, source_id=source_id
        )
        document: DocumentVersionFact | None = None
        snapshot: ParseSnapshotFact | None = None
        if source is not None:
            try:
                document = self.facts.document_version_fact_for_source(
                    tenant_id=tenant_id, source_id=source_id
                )
            except CanonicalFactsMissing:
                document = None
        if document is not None:
            try:
                snapshot = self.facts.parse_snapshot_fact_for_document(
                    tenant_id=tenant_id,
                    document_version_id=document.document_version_id,
                )
            except CanonicalFactsMissing:
                snapshot = None
        knowledge_version_id = current.knowledge_version_id
        chunk_ids: tuple[str, ...] = ()
        entity_ids: tuple[str, ...] = ()
        relation_ids: tuple[str, ...] = ()
        if knowledge_version_id:
            chunk_ids = tuple(
                fact.chunk_id
                for fact in self.facts.chunk_facts(
                    tenant_id=tenant_id,
                    knowledge_version_id=knowledge_version_id,
                )
            )
            entity_ids = tuple(
                fact.entity_id
                for fact in self.entities_relations.entity_facts(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                )
            )
            relation_ids = tuple(
                fact.relation_id
                for fact in self.entities_relations.relation_facts(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    knowledge_version_id=knowledge_version_id,
                )
            )
        object_manifest_hash = None
        if source is not None:
            manifest = self.facts.object_manifest_fact_optional(
                object_ref=source.storage_uri
            )
            if manifest is not None:
                object_manifest_hash = manifest.content_hash
        return CanonicalIngestionReceipt(
            run_id=run_id,
            state=current.current_state,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_id=source_id,
            source_sha256=source.source_sha256 if source is not None else "",
            object_ref=source.storage_uri if source is not None else None,
            object_manifest_ref=source.object_manifest_ref if source is not None else None,
            object_manifest_hash=object_manifest_hash,
            document_id=source.source_object_id if source is not None else None,
            document_version_id=(
                document.document_version_id if document is not None else None
            ),
            parse_snapshot_id=(
                snapshot.parse_snapshot_id if snapshot is not None else None
            ),
            canonical_ir_ref=(
                snapshot.canonical_ir_ref if snapshot is not None else None
            ),
            knowledge_version_id=knowledge_version_id,
            chunk_ids=chunk_ids,
            entity_ids=entity_ids,
            relation_ids=relation_ids,
            state_version=current.state_version,
            attempt_number=current.attempt_number,
            idempotent=idempotent,
            failure_code=current.last_error_code,
            transitions=tuple(
                {
                    "to_state": item["to_state"],
                    "from_state": item["from_state"],
                    "state_version": item["state_version"],
                }
                for item in self.runs.history(run_id=run_id, tenant_id=tenant_id)
            ),
        )

    # --- internal helpers ------------------------------------------------------------

    def _outbox_event_exists(self, event_id: str) -> bool:
        with self.engine.connect() as connection:
            row = connection.execute(
                text(
                    "SELECT event_id FROM infra_outbox_events WHERE event_id = :event_id"
                ),
                {"event_id": event_id},
            ).first()
        return row is not None

    def _ensure_committed_object(self, *, command: CanonicalSourceIngestCommand) -> None:
        """Verify the committed object manifest and repair it idempotently.

        The committed key is deterministic; re-staging and re-committing the
        same bytes never creates a second object or a conflicting manifest.
        """
        object_ref = f"s3://{self.bucket}/{self._object_name(command)}"
        manifest = self.facts.object_manifest_fact_optional(object_ref=object_ref)
        if manifest is not None and manifest.visibility in {"visible", "restored"}:
            return
        staged = self.object_store.stage(
            bucket=self.bucket,
            committed_object_name=self._object_name(command),
            content=command.content,
        )
        self.object_store.commit(staged)

    def _fire_fault_hook(self, step: str) -> None:
        """Invoke the test-only crash injection point after a durable step."""
        if self.fault_hook is not None:
            self.fault_hook(step)

    def _fail_transition(
        self,
        *,
        run_id: str,
        tenant_id: str,
        expected_from_state: str,
        to_state: str,
        command: CanonicalSourceIngestCommand,
        failure_code: str,
        detail: str,
    ) -> None:
        self.runs.transition(
            run_id=run_id,
            tenant_id=tenant_id,
            to_state=to_state,
            expected_from_state=expected_from_state,
            source_id=command.source_id,
            source_hash=self._source_hash(command),
            last_error_code=failure_code,
            last_error_detail=detail,
        )

    def _reconcile_fail(
        self,
        *,
        current: Any,
        tenant_id: str,
        failure_code: str,
        detail: str,
    ) -> CanonicalIngestionReceipt:
        self.runs.transition(
            run_id=current.run_id,
            tenant_id=tenant_id,
            to_state=CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
            expected_from_state=current.current_state,
            source_id=self._source_id_from_run(current),
            last_error_code=failure_code,
            last_error_detail=detail,
        )
        return self._receipt_from_owner_tables(
            run_id=current.run_id,
            tenant_id=tenant_id,
            workspace_id=current.workspace_id,
            source_id=self._source_id_from_run(current),
            idempotent=False,
        )

    def _read_and_verify_object(
        self,
        command: CanonicalSourceIngestCommand,
        source_sha256: str,
    ) -> bytes:
        content = self.object_store.store.read_object(
            bucket=self.bucket, object_name=self._object_name(command)
        )
        actual_hash = hashlib.sha256(content).hexdigest()
        if actual_hash != source_sha256 or len(content) != len(command.content):
            raise CanonicalIngestionError(
                "object_bytes_mismatch: MinIO readback does not match source hash"
            )
        return content

    def _require_corpus_manifest(self, command: CanonicalSourceIngestCommand) -> dict[str, Any]:
        manifest = getattr(self, "_corpus_manifest", None)
        if manifest is None:
            raise CanonicalIngestionError(
                "official corpus manifest is not loaded; ingest_official_corpus "
                "must provide it before per-source finalize"
            )
        if str(manifest.get("source_manifest_hash")) != command.corpus_manifest_ref:
            raise CanonicalIngestionError("corpus manifest hash mismatch")
        return manifest

    def _corpus_document_set(
        self, *, command: CanonicalSourceIngestCommand, manifest: dict[str, Any]
    ) -> dict[str, str]:
        # the frozen source-upload manifest is the single corpus; the document
        # set spans all its sources regardless of the scoping tenant override.
        # The runner registers the source manifest via ingest_official_corpus.
        sources = self._corpus_sources
        if sources is None:
            sources = manifest.get("sources", [])
        return {
            str(source["source_id"]): str(source["source_hash"])
            for source in sources
        }

    def _manifest_document_version_id(
        self, *, manifest: dict[str, Any], document_id: str
    ) -> str:
        for document in manifest.get("documents", []):
            if str(document["document_id"]) == document_id:
                return str(document["document_version_id"])
        raise CanonicalIngestionError(f"manifest document missing: {document_id}")

    def load_corpus_manifest(self, manifest: dict[str, Any]) -> None:
        """Attach the official canonical IR manifest to the runtime (the frozen
        extractor output consumed by the knowledge-facts steps)."""
        self._corpus_manifest = manifest

    def load_corpus_sources(self, source_manifest: dict[str, Any]) -> None:
        """Attach the frozen source-upload manifest (corpus document set)."""
        self._corpus_sources = list(source_manifest.get("sources") or [])

    @staticmethod
    def _source_hash(command: CanonicalSourceIngestCommand) -> str:
        return hashlib.sha256(command.content).hexdigest()

    @staticmethod
    def _command_payload_hash(command: CanonicalSourceIngestCommand, source_sha256: str) -> str:
        return canonical_sha256(
            {
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "source_id": command.source_id,
                "document_id": command.document_id,
                "source_hash": source_sha256,
                "classification": command.classification,
                "security_epoch_ref": command.security_epoch_ref,
                "security_decision_ref": command.security_decision_ref,
                "corpus_manifest_ref": command.corpus_manifest_ref,
            }
        )

    @staticmethod
    def _source_id_from_run(current: Any) -> str:
        """Decode the source component of the canonical run key (the run key is
        the persisted composite identity created at ``ensure_run``)."""
        run_id = str(current.run_id)
        if run_id.startswith("canonical-ingest:"):
            parts = run_id.split(":")
            if len(parts) == 4:
                return parts[3]
        return ""

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
            "document_id": command.document_id,
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
            "classification_ref": command.classification,
            "principal_id": command.principal_id,
            "parser_policy_ref": "parser-policy:phase22-canonical",
            "quality_policy_ref": "quality-policy:phase22-canonical",
            "security_decision_ref": command.security_decision_ref,
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
            data_classification=command.classification,
            occurred_at=now,
            created_at=now,
            deadline_at=command.deadline_at,
            payload=payload,
            payload_hash=canonical_sha256(payload),
            payload_schema_hash=canonical_sha256(
                {"schema": "zuno.ingestion.parse.requested.v1"}
            ),
        )

    @staticmethod
    def _quality_metric(quality_gate, name: str) -> float:
        """Read a measured quality metric from the deterministic quality
        contract. Never manufactures a perfect score by construction."""
        for metric in quality_gate.metrics:
            if metric.name == name:
                return float(metric.value)
        return 0.0


def _split_object_ref(object_ref: str) -> tuple[str, str]:
    if not object_ref.startswith("s3://"):
        raise CanonicalIngestionError(f"invalid object ref: {object_ref}")
    remainder = object_ref[len("s3://"):]
    bucket, _, object_name = remainder.partition("/")
    if not bucket or not object_name:
        raise CanonicalIngestionError(f"invalid object ref: {object_ref}")
    return bucket, object_name


class CanonicalGraphFactsArtifact:
    """Deprecated placeholder retained for import compatibility."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError(
            "graph facts are now PostgreSQL domain facts "
            "(knowledge_entities / knowledge_relations)"
        )
