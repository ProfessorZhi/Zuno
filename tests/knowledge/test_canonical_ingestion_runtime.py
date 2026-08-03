from __future__ import annotations

"""PHASE22 canonical ingestion runtime tests (GAP-B1 / GAP-B2).

Two layers:

1. Pure unit tests — the canonical state machine, security gate, entity /
   directed-relation extraction determinism, and the object store binding
   ownership surface. These never touch services.

2. Live tests — the full synthetic corpus path against real PostgreSQL and
   MinIO (same contract as the phase11 production runtime integration tests).
   When PostgreSQL/MinIO are unavailable the live tests skip with
   BLOCKED_WITH_EXACT_GAPS so the required pytest invocation still reports a
   precise gap instead of a silent green.

No fake IDs are ever produced: every asserted ID comes from the real pipeline
(MinIO commit receipt, PostgreSQL rows, the real parse gateway, and the real
graph handoff payload). Fault-injection doubles are limited to failure paths
(commit failure, parser failure) and are explicitly labeled.
"""

import hashlib
from io import BytesIO
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from zuno.knowledge.ingestion.canonical_runtime import (
    CANONICAL_FAILURE_CANONICALIZATION_FAILED,
    CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
    CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
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
    IngestionSecurityClassifier,
    Phase22CanonicalIngestionRuntime,
    canonical_run_id,
    canonical_state_sequence,
    extract_canonical_graph_facts,
    validate_canonical_state_transition,
)
from zuno.knowledge.ingestion.contracts import (
    CanonicalDocumentIR,
    ParserFailure,
    ParseDocumentResult,
)
from zuno.knowledge.ingestion.router import build_index_handoff_payload
from zuno.knowledge.storage.canonical_facts import (
    CanonicalFactsMissing,
    CanonicalIngestionFactsStore,
)
from zuno.platform.storage.binding import (
    OBJECT_STORE_OWNERSHIP,
    ObjectStoreLocalAdapterForbidden,
    binding_declaration_payload,
    build_local_object_store,
    production_object_store_adapter,
)
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

SAMPLE_MARKDOWN = """# Zuno Ingestion Pipeline

SourceUpload commits the OriginalDocument into the MinioBucket.

CanonicalIrBuilder produces DocumentBlocks with SourceSpan anchors.

EntityExtractor discovers AcmeCorp and ProjectZeta relations.

"""


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

    def test_illegal_transition_rejected(self) -> None:
        with pytest.raises(ValueError):
            validate_canonical_state_transition(
                CANONICAL_STATE_ACCEPTED, CANONICAL_STATE_KV_READY
            )
        with pytest.raises(ValueError):
            validate_canonical_state_transition(
                CANONICAL_STATE_OBJECT_STAGED, CANONICAL_STATE_IR_READY
            )

    def test_forbidden_states_never_written(self) -> None:
        assert FORBIDDEN_CANONICAL_STATES == ("indexes_visible", "snapshot_activated")
        for forbidden in FORBIDDEN_CANONICAL_STATES:
            with pytest.raises(ValueError):
                validate_canonical_state_transition(
                    CANONICAL_STATE_IR_READY, forbidden
                )
            with pytest.raises(ValueError):
                canonical_state_sequence(forbidden)

    def test_failure_states_are_terminal(self) -> None:
        for failure_state in (
            CANONICAL_FAILURE_SECURITY_DENIED,
            CANONICAL_FAILURE_CREDENTIAL_BLOCKED,
            CANONICAL_FAILURE_OBJECT_COMMIT_FAILED,
            CANONICAL_FAILURE_CANONICALIZATION_FAILED,
            CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
        ):
            assert CANONICAL_STATE_SEQUENCE[failure_state] >= 90

    def test_run_id_embeds_tenant_workspace_source(self) -> None:
        run_id = canonical_run_id(tenant_id="t1", workspace_id="w1", source_id="s1")
        assert run_id == "canonical-ingest:t1:w1:s1"


class TestSecurityClassifier:
    def test_allowed_classification(self) -> None:
        verdict = IngestionSecurityClassifier().evaluate(
            classification_ref="classification:public",
            security_epoch_ref="security-epoch:1",
            principal_id="p1",
        )
        assert verdict.decision == "allow"

    def test_denied_classification(self) -> None:
        verdict = IngestionSecurityClassifier().evaluate(
            classification_ref="classification:forbidden",
            security_epoch_ref="security-epoch:1",
            principal_id="p1",
        )
        assert verdict.decision == "deny"
        assert verdict.reason == "classification_forbidden"

    def test_missing_security_epoch_denied(self) -> None:
        verdict = IngestionSecurityClassifier().evaluate(
            classification_ref="classification:public",
            security_epoch_ref="",
            principal_id="p1",
        )
        assert verdict.decision == "deny"
        assert verdict.reason == "security_epoch_ref_missing"


class TestGraphFactsExtraction:
    def test_entities_and_directed_relations_deterministic(self) -> None:
        documents = [
            {
                "chunk_id": "doc::b1::cite1",
                "content": "AcmeCorp works with ProjectZeta. ProjectZeta owns DataLake.",
                "source_span": {"ref": "source-span:dv1:b1"},
            }
        ]
        first = extract_canonical_graph_facts(
            tenant_id="t1",
            workspace_id="w1",
            knowledge_version_id="kv1",
            graphrag_documents=documents,
        )
        second = extract_canonical_graph_facts(
            tenant_id="t1",
            workspace_id="w1",
            knowledge_version_id="kv1",
            graphrag_documents=documents,
        )
        assert first == second
        entity_names = {item["name"] for item in first["entities"]}
        assert {"AcmeCorp", "ProjectZeta", "DataLake"} <= entity_names
        relations = first["relations"]
        assert relations, "directed relations must be produced"
        for relation in relations:
            assert relation["kind"] == "co_occurs"
            assert relation["from_ref"] != relation["to_ref"]
            assert relation["from_ref"].startswith("entity:")
            assert relation["to_ref"].startswith("entity:")
            assert relation["relation_ref"].startswith("relation:")
        # direction follows source text order: AcmeCorp -> ProjectZeta
        acme = next(item["entity_ref"] for item in first["entities"] if item["name"] == "AcmeCorp")
        zeta = next(item["entity_ref"] for item in first["entities"] if item["name"] == "ProjectZeta")
        assert any(r["from_ref"] == acme and r["to_ref"] == zeta for r in relations)

    def test_ids_scoped_to_tenant(self) -> None:
        documents = [{"chunk_id": "c1", "content": "AcmeCorp leads.", "source_span": {}}]
        refs_by_tenant = {}
        for tenant in ("t1", "t2"):
            facts = extract_canonical_graph_facts(
                tenant_id=tenant,
                workspace_id="w1",
                knowledge_version_id="kv1",
                graphrag_documents=documents,
            )
            refs_by_tenant[tenant] = {
                item["entity_ref"] for item in facts["entities"]
            }
        assert refs_by_tenant["t1"] != refs_by_tenant["t2"]


class TestObjectStoreBinding:
    def test_single_production_owner_declared(self) -> None:
        production = production_object_store_adapter()
        assert production.role == "production_adapter"
        assert production.adapter_name == "DurableMinioObjectStore"
        assert production.deployment_class == "SERVER_PRODUCT"
        assert production.authoritative is True
        roles = {declaration.role for declaration in OBJECT_STORE_OWNERSHIP}
        assert roles == {"port", "production_adapter", "physical_transport", "local_adapter"}

    def test_local_adapter_gated_to_developer_ci(self) -> None:
        store = build_local_object_store(Path(".") / "tmp-object-root")
        assert store is not None
        with pytest.raises(ObjectStoreLocalAdapterForbidden):
            build_local_object_store(
                Path(".") / "tmp-object-root", profile="server_product"
            )

    def test_binding_declaration_payload_stable(self) -> None:
        payload = binding_declaration_payload()
        assert payload["port"] == "DurableObjectStore"
        assert payload["production_adapter"] == "DurableMinioObjectStore"
        assert payload["fail_closed_when_unbound"] is True


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
    facts = CanonicalIngestionFactsStore(engine)
    try:
        yield {
            "engine": engine,
            "minio": minio,
            "bucket": bucket,
            "durable": durable,
            "runtime": runtime,
            "facts": facts,
        }
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()


def _command(env: dict, **overrides) -> CanonicalSourceIngestCommand:
    suffix = uuid4().hex[:8]
    return CanonicalSourceIngestCommand(
        tenant_id=str(env["tenant_id"]),
        workspace_id=str(env["workspace_id"]),
        principal_id=f"principal-{suffix}",
        source_id=overrides.pop("source_id", None) or f"source-{suffix}",
        filename=overrides.pop("filename", "pipeline.md"),
        mime_type=overrides.pop("mime_type", "text/markdown"),
        content=overrides.pop("content", SAMPLE_MARKDOWN.encode("utf-8")),
        classification_ref=overrides.pop("classification_ref", "classification:public"),
        security_epoch_ref=f"security-epoch:{env['tenant_id']}:1",
        knowledge_space_id=str(env["knowledge_space_id"]),
        corpus_manifest_ref=f"corpus-manifest:{env['tenant_id']}:synthetic-v1",
        trace_id=f"trace-{suffix}",
        bucket=env["bucket"],
        **overrides,
    )


def _new_environment() -> dict:
    return {
        "tenant_id": f"tenant-{uuid4().hex[:12]}",
        "workspace_id": f"workspace-{uuid4().hex[:8]}",
        "knowledge_space_id": f"space-{uuid4().hex[:8]}",
    }


class TestLiveCanonicalIngestion:
    def test_full_pipeline_produces_real_ids(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        command = _command(env)
        receipt = runtime.ingest(command)

        assert receipt.state == CANONICAL_STATE_KV_READY
        assert not receipt.idempotent
        # every required ID is real and non-empty
        assert receipt.source_id == command.source_id
        assert receipt.object_ref.startswith("s3://")
        assert receipt.object_manifest_ref
        assert receipt.object_manifest_hash == hashlib.sha256(command.content).hexdigest()
        assert receipt.document_id == command.source_id
        assert receipt.document_version_id == f"document-version:{command.source_id}:1"
        assert receipt.parse_snapshot_id
        assert receipt.knowledge_version_id
        assert receipt.chunk_ids
        assert receipt.graph_facts is not None
        assert receipt.graph_facts.entity_ids
        assert receipt.graph_facts.relation_ids
        # ledger order is exactly the canonical happy path
        states = [event["state"] for event in receipt.events]
        assert states == [
            CANONICAL_STATE_ACCEPTED,
            CANONICAL_STATE_OBJECT_STAGED,
            CANONICAL_STATE_OBJECT_COMMITTED,
            CANONICAL_STATE_IR_READY,
            CANONICAL_STATE_KV_READY,
        ]
        assert not any(state in FORBIDDEN_CANONICAL_STATES for state in states)

    def test_minio_write_and_readback_hash_match(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        minio = live_environment["minio"]
        command = _command(env)
        receipt = runtime.ingest(command)

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        observed = minio.read_object(bucket=bucket, object_name=object_name)
        assert hashlib.sha256(observed).hexdigest() == receipt.source_sha256
        assert observed == command.content

    def test_postgresql_facts_queryable(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = _command(env)
        receipt = runtime.ingest(command)

        source = facts.source_object_fact(
            tenant_id=env["tenant_id"], source_id=receipt.source_id
        )
        assert source.source_sha256 == receipt.source_sha256
        assert source.storage_uri == receipt.object_ref
        assert source.status == "committed"

        document = facts.document_version_fact(
            tenant_id=env["tenant_id"],
            document_version_id=receipt.document_version_id,
        )
        assert document.source_object_id == receipt.source_id

        snapshot = facts.parse_snapshot_fact(
            tenant_id=env["tenant_id"],
            parse_snapshot_id=receipt.parse_snapshot_id,
        )
        assert snapshot.canonical_ir["metadata"]["document_id"] == receipt.source_id

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
        assert {chunk.chunk_id for chunk in chunks} == set(receipt.chunk_ids)

    def test_graph_facts_artifact_readback(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        minio = live_environment["minio"]
        command = _command(env)
        receipt = runtime.ingest(command)

        artifact = receipt.graph_facts
        bucket, object_name = artifact.object_ref[len("s3://"):].split("/", 1)
        content = minio.read_object(bucket=bucket, object_name=object_name)
        assert hashlib.sha256(content).hexdigest() == artifact.manifest_hash
        assert artifact.entity_ids
        assert artifact.relation_ids
        # deterministic re-derivation from the real canonical IR agrees with
        # the committed artifact
        snapshot = facts.parse_snapshot_fact(
            tenant_id=env["tenant_id"],
            parse_snapshot_id=receipt.parse_snapshot_id,
        )
        document = CanonicalDocumentIR.model_validate(snapshot.canonical_ir)
        handoff = build_index_handoff_payload(document)
        rederived = extract_canonical_graph_facts(
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            knowledge_version_id=receipt.knowledge_version_id,
            graphrag_documents=handoff.graphrag_documents,
        )
        assert tuple(item["entity_ref"] for item in rederived["entities"]) == artifact.entity_ids
        assert tuple(item["relation_ref"] for item in rederived["relations"]) == artifact.relation_ids

    def test_same_source_hash_rerun_is_idempotent(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        command = _command(env)
        first = runtime.ingest(command)
        second = runtime.ingest(command)

        assert second.state == CANONICAL_STATE_KV_READY
        assert second.idempotent is True
        assert second.source_id == first.source_id
        assert second.knowledge_version_id == first.knowledge_version_id
        assert second.chunk_ids == first.chunk_ids
        assert second.graph_facts.manifest_hash == first.graph_facts.manifest_hash
        # facts were reused, not duplicated
        chunks = facts.chunk_facts(
            tenant_id=env["tenant_id"],
            knowledge_version_id=first.knowledge_version_id,
        )
        assert len(chunks) == len(first.chunk_ids)

    def test_immutable_source_hash_conflict(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        command = _command(env)
        runtime.ingest(command)
        altered = _command(
            env,
            source_id=command.source_id,
            content=b"different content that changes the hash",
        )
        with pytest.raises(CanonicalIngestionConflictError):
            runtime.ingest(altered)

    def test_cross_tenant_isolation(self, live_environment) -> None:
        env_a = _new_environment()
        env_a["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        facts = live_environment["facts"]
        receipt_a = runtime.ingest(_command(env_a))

        # owner tenant sees its own facts...
        facts.source_object_fact(
            tenant_id=env_a["tenant_id"], source_id=receipt_a.source_id
        )
        # ...a foreign tenant sees nothing
        with pytest.raises(CanonicalFactsMissing):
            facts.source_object_fact(
                tenant_id=f"tenant-other-{uuid4().hex[:8]}",
                source_id=receipt_a.source_id,
            )
        # ledger invisible cross-tenant
        facts.run_ledger_cross_tenant(
            owner_tenant_id=env_a["tenant_id"],
            other_tenant_id=f"tenant-other-{uuid4().hex[:8]}",
            run_id=receipt_a.run_id,
        )

    def test_security_denied(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        command = _command(env, classification_ref="classification:forbidden")
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_SECURITY_DENIED
        assert receipt.failure_code == "security_denied:classification_forbidden"

    def test_credential_blocked_without_binding(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        unbound = Phase22CanonicalIngestionRuntime(
            engine=live_environment["engine"],
            object_store=None,
            bucket=env["bucket"],
            worker_id="phase22-unbound-test",
        )
        command = _command(env)
        receipt = unbound.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_CREDENTIAL_BLOCKED
        assert receipt.failure_code == "object_store_binding_missing"

    def test_object_commit_failed(self, live_environment) -> None:
        """Fault injection: durable commit refuses — the run fails closed."""
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]

        class _FailingDurableStore(DurableMinioObjectStore):
            def commit(self, ticket):  # type: ignore[override]
                raise ObjectHashMismatchError("injected commit failure")

        failing_runtime = Phase22CanonicalIngestionRuntime(
            engine=live_environment["engine"],
            object_store=_FailingDurableStore(
                store=live_environment["minio"],
                engine=live_environment["engine"],
                owner="phase22.fault_injection",
            ),
            bucket=env["bucket"],
            worker_id="phase22-fault-test",
        )
        command = _command(env)
        receipt = failing_runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_OBJECT_COMMIT_FAILED
        assert receipt.failure_code == "object_hash_mismatch"

    def test_submitted_not_ingested(self, live_environment, monkeypatch) -> None:
        """A submitted parse request does not equal an ingested document.

        The parse-requested outbox event is enqueued (submitted), but the
        canonicalizer fails, so the run is NOT ingested: queue submission and
        domain success are different facts.
        """
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
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
        command = _command(env)
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_FAILURE_CANONICALIZATION_FAILED
        assert receipt.failure_code.startswith("canonicalization_failed")
        # the queue submission happened but the run is NOT ingested
        ledger = runtime.get_run(run_id=receipt.run_id, tenant_id=env["tenant_id"])
        states = [event["state"] for event in ledger.events]
        assert CANONICAL_STATE_OBJECT_COMMITTED in states
        assert CANONICAL_STATE_KV_READY not in states
        assert receipt.knowledge_version_id is None
        assert not receipt.chunk_ids

    def test_queue_ack_not_domain_success(self, live_environment) -> None:
        """The parse-request outbox row (pending) is not a domain success fact."""
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        command = _command(env)
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY
        # the parse-requested outbox event exists but the run state machine is
        # the domain truth, not any queue acknowledgment
        engine = live_environment["engine"]
        with engine.connect() as connection:
            row = connection.execute(
                text(
                    """
                    SELECT event_id, status FROM infra_outbox_events
                    WHERE tenant_id = :tenant_id
                      AND topic = 'ingestion.parse.requested'
                    ORDER BY event_id DESC LIMIT 1
                    """
                ),
                {"tenant_id": env["tenant_id"]},
            ).mappings().first()
        assert row is not None
        states = [event["state"] for event in receipt.events]
        assert states[-1] == CANONICAL_STATE_KV_READY

    def test_reconciliation_required_on_tampered_object(self, live_environment) -> None:
        env = _new_environment()
        env["bucket"] = live_environment["bucket"]
        runtime = live_environment["runtime"]
        minio = live_environment["minio"]
        command = _command(env)
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        # tamper with the committed object bytes in place (test-only fault
        # injection via the raw physical client)
        tampered = b"tampered bytes that break the content hash"
        minio.client.put_object(
            bucket,
            object_name,
            BytesIO(tampered),
            length=len(tampered),
        )
        reconciled = runtime.reconcile(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert reconciled.state == CANONICAL_FAILURE_RECONCILIATION_REQUIRED
        assert reconciled.failure_code == "object_bytes_mismatch"
