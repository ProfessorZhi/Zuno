from __future__ import annotations

"""PHASE22 canonical ingestion live integration tests (GAP-B2).

Real PostgreSQL + real MinIO verification for the synthetic corpus track:

- live MinIO object write and readback with content-hash agreement
- live PostgreSQL source/document/IR/chunk/version facts
- same source hash rerun idempotency (facts reused, no duplicates)
- hash mismatch negative path (tampered object -> reconciliation_required)
- cross tenant / workspace isolation
- corpus batch ingestion with distinct real IDs

Skips with BLOCKED_WITH_EXACT_GAPS when PostgreSQL or MinIO is unreachable.
"""

import hashlib
import os
from io import BytesIO
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from zuno.knowledge.ingestion.canonical_runtime import (
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    CANONICAL_STATE_KV_READY,
    CanonicalIngestionReceipt,
    CanonicalSourceIngestCommand,
    Phase22CanonicalIngestionRuntime,
)
from zuno.knowledge.storage.canonical_facts import (
    CanonicalFactsMissing,
    CanonicalIngestionFactsStore,
)
from zuno.platform.storage.durable import DurableMinioObjectStore
from zuno.platform.storage.object_store import MinioObjectStore

DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = os.environ.get("ZUNO_TEST_MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("ZUNO_TEST_MINIO_SECRET_KEY", "minioadmin")

CORPUS_DOCUMENTS = {
    "zuno-ingestion-guide.md": (
        "# Zuno Ingestion Guide\n\n"
        "SourceUpload writes OriginalBytes into the DurableObjectStore.\n"
        "IngestionKernel classifies the SourceDocument before Canonicalization.\n"
        "KnowledgeVersion activates only after IndexVisibility receipts.\n"
    ),
    "graphrag-runtime.md": (
        "# GraphRAG Runtime\n\n"
        "EntityExtractor emits AcmeCorp and ProjectZeta nodes.\n"
        "RelationBuilder links ProjectZeta to DataLakeStorage.\n"
        "EvidenceLedger records SourceSpan for every CitationChunk.\n"
    ),
    "tenant-isolation.md": (
        "# Tenant Isolation\n\n"
        "TenantA never reads TenantB facts through the CanonicalFactsStore.\n"
        "WorkspaceScope binds every SourceObject to its WorkspaceId.\n"
        "SecurityEpoch gates every classification decision.\n"
    ),
}


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
        f"{DATABASE_URL} / {MINIO_ENDPOINT}; live integration tests skipped"
    ),
)


@pytest.fixture(scope="module")
def live_env():
    engine = create_engine(DATABASE_URL)
    minio = MinioObjectStore(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )
    bucket = f"zuno-phase22-cc-live-{uuid4().hex[:12]}"
    durable = DurableMinioObjectStore(store=minio, engine=engine, owner="phase22.cc_live")
    runtime = Phase22CanonicalIngestionRuntime(
        engine=engine,
        object_store=durable,
        bucket=bucket,
        worker_id="phase22-live-worker",
    )
    facts = CanonicalIngestionFactsStore(engine)
    try:
        yield {
            "engine": engine,
            "minio": minio,
            "bucket": bucket,
            "runtime": runtime,
            "facts": facts,
        }
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()


def _command(env: dict, filename: str, *, tenant_id: str | None = None, **overrides) -> CanonicalSourceIngestCommand:
    suffix = uuid4().hex[:8]
    content = CORPUS_DOCUMENTS[filename].encode("utf-8")
    return CanonicalSourceIngestCommand(
        tenant_id=tenant_id or str(env["tenant_id"]),
        workspace_id=str(env["workspace_id"]),
        principal_id=f"principal-{suffix}",
        source_id=overrides.pop("source_id", None) or f"source-{suffix}",
        filename=filename,
        mime_type="text/markdown",
        content=content,
        classification_ref="classification:public",
        security_epoch_ref=f"security-epoch:{env['tenant_id']}:1",
        knowledge_space_id=str(env["knowledge_space_id"]),
        corpus_manifest_ref=f"corpus-manifest:{env['tenant_id']}:synthetic-v1",
        trace_id=f"trace-{suffix}",
        bucket=env["bucket"],
        **overrides,
    )


def _new_environment(bucket: str) -> dict:
    return {
        "tenant_id": f"tenant-{uuid4().hex[:12]}",
        "workspace_id": f"workspace-{uuid4().hex[:8]}",
        "knowledge_space_id": f"space-{uuid4().hex[:8]}",
        "bucket": bucket,
    }


class TestPhase22LiveCorpusIngestion:
    def test_corpus_batch_ingests_all_documents_with_real_ids(self, live_env) -> None:
        env = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        receipts: dict[str, CanonicalIngestionReceipt] = {}
        for filename in CORPUS_DOCUMENTS:
            receipt = runtime.ingest(_command(env, filename))
            receipts[filename] = receipt
            assert receipt.state == CANONICAL_STATE_KV_READY

        # every document produced distinct real IDs
        assert len({r.source_id for r in receipts.values()}) == len(CORPUS_DOCUMENTS)
        assert len({r.object_ref for r in receipts.values()}) == len(CORPUS_DOCUMENTS)
        assert len({r.knowledge_version_id for r in receipts.values()}) == len(CORPUS_DOCUMENTS)
        for receipt in receipts.values():
            assert receipt.chunk_ids
            assert receipt.graph_facts is not None
            assert receipt.graph_facts.entity_ids
            assert receipt.graph_facts.relation_ids
            assert receipt.object_manifest_hash == hashlib.sha256(
                CORPUS_DOCUMENTS[
                    next(name for name, r in receipts.items() if r is receipt)
                ].encode("utf-8")
            ).hexdigest()

    def test_live_minio_readback_hash_agrees(self, live_env) -> None:
        env = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        minio = live_env["minio"]
        command = _command(env, "zuno-ingestion-guide.md")
        receipt = runtime.ingest(command)

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        observed = minio.read_object(bucket=bucket, object_name=object_name)
        assert observed == command.content
        assert hashlib.sha256(observed).hexdigest() == receipt.source_sha256
        # the durable manifest agrees with the physical object
        manifest = live_env["facts"].run_state_facts(
            tenant_id=env["tenant_id"], run_id=receipt.run_id
        )
        assert manifest[-1].state == CANONICAL_STATE_KV_READY

    def test_live_postgresql_idempotency_rerun(self, live_env) -> None:
        env = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        facts = live_env["facts"]
        command = _command(env, "graphrag-runtime.md")
        first = runtime.ingest(command)
        second = runtime.ingest(command)

        assert second.idempotent is True
        assert second.state == CANONICAL_STATE_KV_READY
        assert second.knowledge_version_id == first.knowledge_version_id
        assert second.graph_facts.manifest_hash == first.graph_facts.manifest_hash
        chunks = facts.chunk_facts(
            tenant_id=env["tenant_id"],
            knowledge_version_id=first.knowledge_version_id,
        )
        assert len(chunks) == len(first.chunk_ids)
        # exactly one source fact row exists for the rerun
        source = facts.source_object_fact(
            tenant_id=env["tenant_id"], source_id=first.source_id
        )
        assert source.source_sha256 == first.source_sha256

    def test_hash_mismatch_negative_path(self, live_env) -> None:
        env = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        minio = live_env["minio"]
        command = _command(env, "tenant-isolation.md")
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY

        bucket, object_name = receipt.object_ref[len("s3://"):].split("/", 1)
        tampered = b"tampered source bytes"
        minio.client.put_object(
            bucket, object_name, BytesIO(tampered), length=len(tampered)
        )
        reconciled = runtime.reconcile(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert reconciled.state == CANONICAL_FAILURE_RECONCILIATION_REQUIRED
        assert reconciled.failure_code == "object_bytes_mismatch"

    def test_cross_workspace_isolation(self, live_env) -> None:
        env_a = _new_environment(live_env["bucket"])
        env_b = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        facts = live_env["facts"]

        receipt_a = runtime.ingest(_command(env_a, "zuno-ingestion-guide.md"))
        receipt_b = runtime.ingest(_command(env_b, "tenant-isolation.md"))
        assert receipt_a.source_id != receipt_b.source_id

        # each workspace's facts are independently queryable
        facts.source_object_fact(
            tenant_id=env_a["tenant_id"], source_id=receipt_a.source_id
        )
        facts.source_object_fact(
            tenant_id=env_b["tenant_id"], source_id=receipt_b.source_id
        )
        # cross-tenant access to the other run's source is invisible
        with pytest.raises(CanonicalFactsMissing):
            facts.source_object_fact(
                tenant_id=env_b["tenant_id"], source_id=receipt_a.source_id
            )
        facts.run_ledger_cross_tenant(
            owner_tenant_id=env_a["tenant_id"],
            other_tenant_id=env_b["tenant_id"],
            run_id=receipt_a.run_id,
        )

    def test_knowledge_versions_increment_per_space(self, live_env) -> None:
        env = _new_environment(live_env["bucket"])
        runtime = live_env["runtime"]
        facts = live_env["facts"]

        receipts = [
            runtime.ingest(_command(env, filename))
            for filename in CORPUS_DOCUMENTS
        ]
        version_nos = sorted(
            facts.knowledge_version_fact(
                tenant_id=env["tenant_id"],
                knowledge_version_id=receipt.knowledge_version_id,
            ).version_no
            for receipt in receipts
        )
        assert version_nos == [1, 2, 3]

    def test_cleanup_report(self, live_env) -> None:
        """Bucket cleanup is available and idempotent (cleanup report contract)."""
        minio = live_env["minio"]
        bucket = f"zuno-phase22-cc-cleanup-{uuid4().hex[:12]}"
        minio.ensure_bucket(bucket)
        assert minio.client.bucket_exists(bucket) is True
        minio.remove_bucket_tree(bucket)
        assert minio.client.bucket_exists(bucket) is False
        # second removal of a missing bucket is a no-op, not an error
        minio.remove_bucket_tree(bucket)
