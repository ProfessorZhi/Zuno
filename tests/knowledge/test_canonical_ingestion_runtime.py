from __future__ import annotations

"""PHASE22 canonical ingestion runtime tests (GAP-B1 / GAP-B2 hardened).

Layers:

1. Pure unit tests — the declarative state machine (normal, failure, retry,
   reconciliation transitions; forbidden states), run-key helpers, and the
   Security resource-ref contract.

2. Live tests against real PostgreSQL + MinIO — the full pipeline with real
   IDs, Security-owned decision validation, idempotency, tenant isolation,
   receipt truth from owner tables, measured quality, and reconciliation.
   Fault/resume scenarios live in
   ``tests/integration/test_phase22_canonical_ingestion_live.py``.

No fake IDs: every asserted ID comes from real pipeline output. Fault
injection doubles are limited to failure paths and are explicitly labeled.
"""

import hashlib
import os
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from zuno.knowledge.ingestion.canonical_runtime import (
    CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
    CANONICAL_FAILURE_OBJECT_STAGE_FAILED,
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    CANONICAL_FAILURE_SECURITY_DENIED,
    CANONICAL_STATE_ACCEPTED,
    CANONICAL_STATE_IR_READY,
    CANONICAL_STATE_KV_READY,
    CANONICAL_STATE_OBJECT_COMMITTED,
    CANONICAL_STATE_OBJECT_STAGED,
    CANONICAL_STATE_SEQUENCE,
    FORBIDDEN_CANONICAL_STATES,
    CanonicalIngestionConflictError,
    CanonicalSourceIngestCommand,
    Phase22CanonicalIngestionRuntime,
    canonical_run_id,
    canonical_security_resource_ref,
    canonical_state_sequence,
    validate_canonical_state_transition,
)
from zuno.knowledge.ingestion.contracts import (
    ParserFailure,
    ParseDocumentResult,
)
from zuno.knowledge.storage.canonical_facts import (
    CanonicalFactsMissing,
    CanonicalIngestionFactsStore,
)
from zuno.knowledge.storage.canonical_run_store import (
    CANONICAL_STATE_TRANSITIONS,
    CanonicalRunStateConflict,
    CanonicalRunStateError,
)
from zuno.platform.security.persistence import SecurityUnitOfWork
from zuno.platform.storage.durable import DurableMinioObjectStore
from zuno.platform.storage.object_store import (
    MinioObjectStore,
    ObjectHashMismatchError,
)

DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = os.environ.get("ZUNO_TEST_MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("ZUNO_TEST_MINIO_SECRET_KEY", "minioadmin")

SAMPLE_MARKDOWN = (
    "# Zuno Ingestion Pipeline\n\n"
    "SourceUpload commits the OriginalDocument into the MinioBucket.\n"
    "CanonicalIrBuilder produces DocumentBlocks with SourceSpan anchors.\n"
    "EntityExtractor discovers AcmeCorp and ProjectZeta relations.\n"
).encode("utf-8")


# ---------------------------------------------------------------------------
# pure unit tests
# ---------------------------------------------------------------------------

class TestCanonicalStateMachine:
    def test_happy_path_transitions_all_legal(self) -> None:
        path = [
            CANONICAL_STATE_ACCEPTED,
            CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_STATE_IR_READY,
            CANONICAL_STATE_KV_READY,
        ]
        for from_state, to_state in zip(path, path[1:]):
            validate_canonical_state_transition(from_state, to_state)

    def test_illegal_transitions_rejected(self) -> None:
        # stage failure must never be recorded as object_commit_failed
        with pytest.raises(ValueError):
            validate_canonical_state_transition(
                CANONICAL_STATE_ACCEPTED, CANONICAL_FAILURE_OBJECT_COMMIT_FAILED
            )
        with pytest.raises(ValueError):
            validate_canonical_state_transition(
                CANONICAL_STATE_ACCEPTED, CANONICAL_STATE_KV_READY
            )
        with pytest.raises(ValueError):
            validate_canonical_state_transition(
                CANONICAL_STATE_OBJECT_STAGED, CANONICAL_STATE_IR_READY
            )

    def test_stage_failure_is_a_distinct_state(self) -> None:
        assert CANONICAL_FAILURE_OBJECT_STAGE_FAILED in CANONICAL_STATE_TRANSITIONS[
            CANONICAL_STATE_ACCEPTED
        ]
        assert CANONICAL_FAILURE_OBJECT_COMMIT_FAILED not in CANONICAL_STATE_TRANSITIONS[
            CANONICAL_STATE_ACCEPTED
        ]

    def test_forbidden_states_never_written(self) -> None:
        assert FORBIDDEN_CANONICAL_STATES == ("indexes_visible", "snapshot_activated")
        for forbidden in FORBIDDEN_CANONICAL_STATES:
            with pytest.raises(ValueError):
                validate_canonical_state_transition(
                    CANONICAL_STATE_IR_READY, forbidden
                )
            with pytest.raises(ValueError):
                canonical_state_sequence(forbidden)

    def test_explicit_retry_transitions(self) -> None:
        # retry: plan and facts remain valid, only execution failed
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_OBJECT_STAGE_FAILED] == (
            CANONICAL_STATE_OBJECT_STAGED,
        )
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_OBJECT_COMMIT_FAILED] == (
            CANONICAL_STATE_OBJECT_COMMITTED,
        )
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_CANONICALIZATION_FAILED] == (
            CANONICAL_STATE_OBJECT_COMMITTED,
        )

    def test_reconciliation_design(self) -> None:
        # unknown side effects enter reconciliation from any active state
        for active in (
            CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_STATE_IR_READY,
        ):
            assert CANONICAL_FAILURE_RECONCILIATION_REQUIRED in CANONICAL_STATE_TRANSITIONS[active]
        # the success terminal only leaves through the designed reconciliation edge
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_STATE_KV_READY] == (
            CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
        )
        # reconciliation resumes through explicit transitions
        assert set(CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_RECONCILIATION_REQUIRED]) == {
            CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_STATE_IR_READY,
        }

    def test_terminal_states_have_no_ordinary_outgoing_edges(self) -> None:
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_SECURITY_DENIED] == ()
        assert CANONICAL_STATE_TRANSITIONS[CANONICAL_FAILURE_CREDENTIAL_BLOCKED] == ()

    def test_run_id_and_sequence(self) -> None:
        assert canonical_run_id(tenant_id="t1", workspace_id="w1", source_id="s1") == (
            "canonical-ingest:t1:w1:s1"
        )
        assert CANONICAL_STATE_SEQUENCE[CANONICAL_STATE_KV_READY] == 5
        assert canonical_state_sequence(CANONICAL_FAILURE_RECONCILIATION_REQUIRED) == 95

    def test_security_resource_ref_contract(self) -> None:
        ref = canonical_security_resource_ref(
            tenant_id="t1", workspace_id="w1", source_id="s1"
        )
        assert ref == "ingestion:source:t1:w1:s1"


# ---------------------------------------------------------------------------
# live tests (real PostgreSQL + real MinIO)
# ---------------------------------------------------------------------------

def _services_available() -> bool:
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        engine.dispose()
        MinioObjectStore(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        ).client.bucket_exists("zuno")
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _services_available(),
    reason=(
        "BLOCKED_WITH_EXACT_GAPS: PostgreSQL or MinIO unreachable at "
        f"{DATABASE_URL} / {MINIO_ENDPOINT}; live canonical ingestion tests skipped"
    ),
)


@pytest.fixture(scope="module")
def live_environment():
    engine = create_engine(DATABASE_URL)
    minio = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )
    bucket = f"zuno-phase22-cc-b1b2-{uuid4().hex[:12]}"
    durable = DurableMinioObjectStore(
        store=minio, engine=engine, owner="phase22.cc_b1_b2"
    )
    runtime = Phase22CanonicalIngestionRuntime(
        engine=engine,
        object_store=durable,
        bucket=bucket,
        worker_id="phase22-test-worker",
    )
    try:
        yield {
            "engine": engine,
            "minio": minio,
            "bucket": bucket,
            "durable": durable,
            "runtime": runtime,
            "facts": CanonicalIngestionFactsStore(engine),
        }
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()


def issue_security_decision(
    engine,
    *,
    tenant_id: str,
    workspace_id: str,
    source_id: str,
    source_hash: str,
    principal_id: str,
    epoch_ref: str,
    decision: str = "USE_ONLY",
) -> str:
    """Security Owner issues an authorization decision (the runtime never does)."""
    with SecurityUnitOfWork(engine) as repo:
        repo.ensure_principal_context(
            principal_context_id=f"pc:{tenant_id}:{principal_id}",
            tenant_id=tenant_id,
            user_principal_id=principal_id,
            epoch_ref=epoch_ref,
        )
        repo.ensure_effective_epoch(
            epoch_ref=epoch_ref,
            tenant_id=tenant_id,
            policy_bundle_ref="policy-bundle:phase22:v1",
            policy_bundle={"version": "v1"},
            action_set_version="v1",
            principal_context_hash="b" * 64,
            generation=1,
            status="active",
        )
        decision_id = f"decision:{tenant_id}:{source_id}:1"
        repo.ensure_authorization_decision(
            decision_id=decision_id,
            tenant_id=tenant_id,
            principal_context_id=f"pc:{tenant_id}:{principal_id}",
            epoch_ref=epoch_ref,
            resource_ref=canonical_security_resource_ref(
                tenant_id=tenant_id, workspace_id=workspace_id, source_id=source_id
            ),
            action="ingestion.source.upload",
            decision=decision,
            reason_code="phase22_synthetic_corpus",
            prepared_action_hash=source_hash,
        )
        return decision_id


def new_environment(bucket: str) -> dict:
    suffix = uuid4().hex[:8]
    return {
        "tenant_id": f"tenant-{suffix}",
        "workspace_id": f"workspace-{suffix}",
        "knowledge_space_id": f"space-{suffix}",
        "principal_id": f"principal-{suffix}",
        "source_id": f"source-{suffix}",
        "document_id": f"doc-{suffix}",
        "epoch_ref": f"security-epoch:tenant-{suffix}:1",
        "bucket": bucket,
    }


def build_command(env: dict, **overrides) -> CanonicalSourceIngestCommand:
    content = overrides.pop("content", SAMPLE_MARKDOWN)
    source_hash = hashlib.sha256(content).hexdigest()
    decision_id = overrides.pop("security_decision_ref", None) or issue_security_decision(
        overrides.pop("_engine"),
        tenant_id=env["tenant_id"],
        workspace_id=env["workspace_id"],
        source_id=env["source_id"],
        source_hash=source_hash,
        principal_id=env["principal_id"],
        epoch_ref=env["epoch_ref"],
        decision=overrides.pop("_decision", "USE_ONLY"),
    )
    return CanonicalSourceIngestCommand(
        tenant_id=env["tenant_id"],
        workspace_id=env["workspace_id"],
        principal_id=env["principal_id"],
        source_id=env["source_id"],
        document_id=env["document_id"],
        filename="pipeline.md",
        mime_type="text/markdown",
        content=content,
        classification="global/open",
        security_epoch_ref=env["epoch_ref"],
        security_decision_ref=decision_id,
        knowledge_space_id=env["knowledge_space_id"],
        corpus_manifest_ref="corpus:unit-test",
        source_set_ref="corpus:unit-test",
        trace_id=f"trace-{uuid4().hex[:8]}",
        bucket=env["bucket"],
        **{k: v for k, v in overrides.items() if k != "_engine"},
    )


def minimal_ir_manifest(env: dict) -> dict:
    suffix = env["source_id"].split("-")[-1]
    return {
        "source_manifest_hash": "corpus:unit-test",
        "documents": [
            {
                "document_id": env["document_id"],
                "document_version_id": f"document-version::{env['document_id']}::abc",
            }
        ],
        "chunks": [
            {
                "chunk_id": f"chunk::{env['document_id']}::001",
                "document_id": env["document_id"],
                "text_hash": "c" * 64,
                "ordinal": 1,
                "security_scope": "global/open",
            }
        ],
        "entities": [
            {
                "entity_id": f"entity::org:Acme{suffix}",
                "entity_ref": f"org:Acme{suffix}",
                "label": "Acme",
                "chunk_id": f"chunk::{env['document_id']}::001",
                "document_id": env["document_id"],
            }
        ],
        "relations": [],
    }


class TestLiveCanonicalIngestion:
    def test_full_pipeline_produces_real_ids(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        assert receipt.state == CANONICAL_STATE_KV_READY
        assert not receipt.idempotent
        assert receipt.source_id == env["source_id"]
        assert receipt.object_ref.startswith("s3://")
        assert receipt.document_version_id
        assert receipt.parse_snapshot_id
        assert receipt.knowledge_version_id
        assert receipt.chunk_ids == (f"chunk::{env['document_id']}::001",)
        assert receipt.entity_ids == (f"entity::org:Acme{env['source_id'].split('-')[-1]}",)
        assert receipt.transitions[-1]["to_state"] == CANONICAL_STATE_KV_READY
        states = [t["to_state"] for t in receipt.transitions]
        assert states == [
            CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_STATE_IR_READY,
            CANONICAL_STATE_KV_READY,
        ]
        assert not any(s in FORBIDDEN_CANONICAL_STATES for s in states)

    def test_security_denied_without_decision(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        runtime = live_environment["runtime"]
        command = CanonicalSourceIngestCommand(
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            principal_id=env["principal_id"],
            source_id=env["source_id"],
            document_id=env["document_id"],
            filename="pipeline.md",
            mime_type="text/markdown",
            content=SAMPLE_MARKDOWN,
            classification="global/open",
            security_epoch_ref=env["epoch_ref"],
            security_decision_ref="decision:missing",
            knowledge_space_id=env["knowledge_space_id"],
            corpus_manifest_ref="corpus:unit-test",
            source_set_ref="corpus:unit-test",
            trace_id=f"trace-{uuid4().hex[:8]}",
            bucket=env["bucket"],
        )
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_SECURITY_DENIED
        assert receipt.failure_code == "security_decision_missing"

    def test_security_denied_on_hash_mismatch(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        # decision issued for a DIFFERENT content hash
        issue_security_decision(
            engine,
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            source_id=env["source_id"],
            source_hash="e" * 64,
            principal_id=env["principal_id"],
            epoch_ref=env["epoch_ref"],
        )
        command = build_command(env, _engine=engine, security_decision_ref=f"decision:{env['tenant_id']}:{env['source_id']}:1")
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_SECURITY_DENIED
        assert receipt.failure_code == "security_decision_action_hash_mismatch"

    def test_credential_blocked_without_binding(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        unbound = Phase22CanonicalIngestionRuntime(
            engine=engine,
            object_store=None,
            bucket=env["bucket"],
            worker_id="phase22-unbound-test",
        )
        command = build_command(env, _engine=engine)
        receipt = unbound.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_CREDENTIAL_BLOCKED
        assert receipt.failure_code == "object_store_binding_missing"

    def test_minio_write_and_readback_hash_match(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        minio = live_environment["minio"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        observed = minio.read_object(bucket=bucket, object_name=object_name)
        assert hashlib.sha256(observed).hexdigest() == receipt.source_sha256
        assert observed == command.content

    def test_postgresql_facts_queryable(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        source = facts.source_object_fact(
            tenant_id=env["tenant_id"], source_id=receipt.source_id
        )
        assert source.status == "committed"
        assert source.storage_uri == receipt.object_ref

        document = facts.document_version_fact(
            tenant_id=env["tenant_id"],
            document_version_id=receipt.document_version_id,
        )
        assert document.source_object_id == receipt.source_id

        snapshot = facts.parse_snapshot_fact(
            tenant_id=env["tenant_id"],
            parse_snapshot_id=receipt.parse_snapshot_id,
        )
        assert snapshot.canonical_ir["metadata"]["document_id"] == env["document_id"]

        version = facts.knowledge_version_fact(
            tenant_id=env["tenant_id"],
            knowledge_version_id=receipt.knowledge_version_id,
        )
        assert version.status == "BUILDING"

        chunks = facts.chunk_facts(
            tenant_id=env["tenant_id"],
            knowledge_version_id=receipt.knowledge_version_id,
        )
        assert len(chunks) == len(receipt.chunk_ids)

    def test_entity_relation_facts_queryable_by_scope(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        entities = runtime.entities_relations.entity_facts(
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            knowledge_version_id=receipt.knowledge_version_id,
        )
        assert tuple(e.entity_id for e in entities) == receipt.entity_ids
        assert entities[0].authority_ref.startswith("authority:canonical-ir-manifest")
        assert len(entities[0].entity_hash) == 64

    def test_same_source_hash_rerun_is_idempotent(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        first = runtime.ingest(command)
        second = runtime.ingest(command)

        assert second.idempotent is True
        assert second.state == CANONICAL_STATE_KV_READY
        assert second.knowledge_version_id == first.knowledge_version_id
        assert second.chunk_ids == first.chunk_ids
        assert second.entity_ids == first.entity_ids
        chunks = facts.chunk_facts(
            tenant_id=env["tenant_id"],
            knowledge_version_id=first.knowledge_version_id,
        )
        assert len(chunks) == len(first.chunk_ids)
        entities = runtime.entities_relations.entity_facts(
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            knowledge_version_id=first.knowledge_version_id,
        )
        assert len(entities) == len(first.entity_ids)

    def test_immutable_source_hash_conflict(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        runtime.ingest(command)
        altered_content = b"different content that changes the hash"
        altered_hash = hashlib.sha256(altered_content).hexdigest()
        # Security issues a NEW decision for the ALTERED content; the
        # immutability guard must then reject the same source_id
        with SecurityUnitOfWork(engine) as repo:
            repo.ensure_authorization_decision(
                decision_id=f"decision:{env['tenant_id']}:{env['source_id']}:2",
                tenant_id=env["tenant_id"],
                principal_context_id=f"pc:{env['tenant_id']}:{env['principal_id']}",
                epoch_ref=env["epoch_ref"],
                resource_ref=canonical_security_resource_ref(
                    tenant_id=env["tenant_id"],
                    workspace_id=env["workspace_id"],
                    source_id=env["source_id"],
                ),
                action="ingestion.source.upload",
                decision="USE_ONLY",
                reason_code="phase22_immutability_test",
                prepared_action_hash=altered_hash,
            )
        altered = build_command(
            env,
            _engine=engine,
            content=altered_content,
            security_decision_ref=f"decision:{env['tenant_id']}:{env['source_id']}:2",
        )
        with pytest.raises(CanonicalIngestionConflictError):
            runtime.ingest(altered)

    def test_cross_tenant_isolation(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        facts.source_object_fact(
            tenant_id=env["tenant_id"], source_id=receipt.source_id
        )
        with pytest.raises(CanonicalFactsMissing):
            facts.source_object_fact(
                tenant_id=f"tenant-other-{uuid4().hex[:8]}",
                source_id=receipt.source_id,
            )
        with pytest.raises(CanonicalRunStateError):
            runtime.get_run(
                run_id=receipt.run_id,
                tenant_id=f"tenant-other-{uuid4().hex[:8]}",
            )
        runtime.entities_relations.entity_facts_cross_tenant(
            owner_tenant_id=env["tenant_id"],
            other_tenant_id=f"tenant-other-{uuid4().hex[:8]}",
            knowledge_version_id=receipt.knowledge_version_id,
        )

    def test_quality_is_measured_not_manufactured(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT coverage_score, confidence_score, decision
                    FROM ingestion_quality_gate_decisions
                    WHERE parse_snapshot_id = :parse_snapshot_id
                      AND tenant_id = :tenant_id
                    """
                ),
                {
                    "parse_snapshot_id": receipt.parse_snapshot_id,
                    "tenant_id": env["tenant_id"],
                },
            ).mappings().first()
        assert row is not None
        # measured values from the deterministic quality contract: the stored
        # IR's min block confidence — not 1.0/1.0 manufactured by construction
        snapshot = live_environment["facts"].parse_snapshot_fact(
            tenant_id=env["tenant_id"],
            parse_snapshot_id=receipt.parse_snapshot_id,
        )
        ir = snapshot.canonical_ir
        block_confidences = [float(b.get("confidence") or 0.0) for b in ir["blocks"]] or [0.0]
        expected = min(block_confidences)
        assert float(row["coverage_score"]) == expected
        assert float(row["confidence_score"]) == expected
        assert row["decision"] in {"publish", "human_review"}

    def test_receipt_truth_from_owner_tables(self, live_environment) -> None:
        """Receipt fields are read from owner tables, not naming conventions."""
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)

        reread = runtime.get_run(run_id=receipt.run_id, tenant_id=env["tenant_id"])
        assert reread.document_version_id == receipt.document_version_id
        # object_manifest_hash comes from the manifest row, not the source hash
        manifest = facts.object_manifest_fact(object_ref=receipt.object_ref)
        assert reread.object_manifest_hash == manifest.content_hash
        assert reread.object_manifest_hash == receipt.source_sha256
        # parse snapshot id comes from the owner row
        assert reread.parse_snapshot_id == receipt.parse_snapshot_id
        # run state comes from the run owner table
        run_fact = runtime.runs.current_fact(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert run_fact.current_state == CANONICAL_STATE_KV_READY
        assert run_fact.state_version == 5
        assert reread.state_version == 5

    def test_submitted_not_ingested(self, live_environment, monkeypatch) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]

        def _failing_parse(request):  # type: ignore[no-untyped-def]
            return ParseDocumentResult(
                job_id=request.parse_job_id or "job",
                status="failed",
                failure=ParserFailure(
                    parser_id="native_markdown",
                    format="markdown",
                    reason="injected canonicalization failure",
                    retryable=False,
                    failure_classification="parser_failure",
                ),
            )

        monkeypatch.setattr(
            "zuno.knowledge.ingestion.gateway.ParseGateway.submit_parse_job",
            staticmethod(_failing_parse),
        )
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_CANONICALIZATION_FAILED
        assert receipt.knowledge_version_id is None
        assert not receipt.chunk_ids
        # queue submission happened but the run is NOT ingested
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT event_id FROM infra_outbox_events
                    WHERE tenant_id = :tenant_id
                      AND topic = 'ingestion.parse.requested'
                    """
                ),
                {"tenant_id": env["tenant_id"]},
            ).mappings().first()
        assert row is not None
        states = [t["to_state"] for t in receipt.transitions]
        assert CANONICAL_STATE_OBJECT_COMMITTED in states
        assert CANONICAL_STATE_KV_READY not in states

    def test_explicit_retry_after_stage_failure(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]

        class _FailingStageStore(DurableMinioObjectStore):
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.fail_next = True

            def stage(self, **kwargs: Any):  # type: ignore[override]
                if self.fail_next:
                    self.fail_next = False
                    raise ConnectionError("injected stage failure")
                return super().stage(**kwargs)

        failing_runtime = Phase22CanonicalIngestionRuntime(
            engine=engine,
            object_store=_FailingStageStore(
                store=live_environment["minio"],
                engine=engine,
                owner="phase22.fault_injection",
            ),
            bucket=env["bucket"],
            worker_id="phase22-fault-test",
        )
        command = build_command(env, _engine=engine)
        failing_runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = failing_runtime.ingest(command)
        # stage failure is recorded as object_stage_failed, never
        # accepted -> object_commit_failed
        assert receipt.state == CANONICAL_FAILURE_OBJECT_STAGE_FAILED
        assert receipt.failure_code == "object_stage_failed"

        retried = failing_runtime.retry(command)
        assert retried.state == CANONICAL_STATE_KV_READY
        assert retried.attempt_number == 2

    def test_reconciliation_on_tampered_object(self, live_environment) -> None:
        from io import BytesIO

        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        minio = live_environment["minio"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        tampered = b"tampered bytes that break the content hash"
        minio.client.put_object(
            bucket, object_name, BytesIO(tampered), length=len(tampered)
        )
        reconciled = runtime.reconcile(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert reconciled.state == CANONICAL_FAILURE_RECONCILIATION_REQUIRED
        assert reconciled.failure_code == "object_bytes_mismatch"
        # restore the bytes and resume through the explicit reconciliation edge
        minio.client.put_object(
            bucket,
            object_name,
            BytesIO(command.content),
            length=len(command.content),
        )
        resumed = runtime.resume_after_reconcile(
            command, to_state=CANONICAL_STATE_OBJECT_COMMITTED
        )
        assert resumed.state == CANONICAL_STATE_KV_READY

    def test_terminal_state_rejects_ordinary_overwrite(self, live_environment) -> None:
        env = new_environment(live_environment["bucket"])
        engine = live_environment["engine"]
        runtime = live_environment["runtime"]
        command = build_command(env, _engine=engine)
        runtime.load_corpus_manifest(minimal_ir_manifest(env))
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY
        # an ordinary overwrite of the success terminal is rejected by the
        # declarative state machine (kv_ready has only the reconciliation edge)
        with pytest.raises(ValueError):
            runtime.runs.transition(
                run_id=receipt.run_id,
                tenant_id=env["tenant_id"],
                to_state=CANONICAL_STATE_OBJECT_STAGED,
                expected_from_state=CANONICAL_STATE_KV_READY,
            )
        # the durable state is unchanged
        run_fact = runtime.runs.current_fact(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert run_fact.current_state == CANONICAL_STATE_KV_READY
        assert run_fact.state_version == 5
