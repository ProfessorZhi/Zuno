from __future__ import annotations

"""PHASE22 canonical ingestion resume / fault matrix (Task G).

Real PostgreSQL + real MinIO crash-and-resume tests at every durable
boundary. A crash simulation hook (test-only extension point on the runtime)
raises after a durable step; the next ingest() reads the durable checkpoint
(``canonical_ingestion_runs.current_state``) and resumes without duplicating
objects, source/document facts, parse attempts, snapshots, chunks, entities,
relations, versions or outbox events. Unknown physical side effects enter
``reconciliation_required``; nothing is blindly retried.
"""


import hashlib
import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from zuno.knowledge.ingestion.canonical_runtime import (
    CANONICAL_FAILURE_RECONCILIATION_REQUIRED,
    CANONICAL_STATE_KV_READY,
    CANONICAL_STATE_OBJECT_COMMITTED,
    CanonicalSourceIngestCommand,
    Phase22CanonicalIngestionRuntime,
    canonical_security_resource_ref,
)
from zuno.platform.security.persistence import SecurityUnitOfWork
from zuno.platform.storage.durable import DurableMinioObjectStore
from zuno.platform.storage.object_store import MinioObjectStore

DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = os.environ.get("ZUNO_TEST_MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("ZUNO_TEST_MINIO_SECRET_KEY", "minioadmin")

CONTENT = (
    "# Crash Recovery Document\n\n"
    "AcmeCorp builds ProjectZeta and ProjectZeta owns DataLakeStorage.\n"
    "The pipeline resumes from the last durable checkpoint after any crash.\n"
).encode("utf-8")


class CrashSimulation(RuntimeError):
    pass


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
        f"{DATABASE_URL} / {MINIO_ENDPOINT}; resume/fault tests skipped"
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
    bucket = f"zuno-phase22-fault-{uuid4().hex[:12]}"
    durable = DurableMinioObjectStore(store=minio, engine=engine, owner="phase22.fault")
    runtime = Phase22CanonicalIngestionRuntime(
        engine=engine,
        object_store=durable,
        bucket=bucket,
        worker_id="phase22-fault-worker",
    )
    try:
        yield {"engine": engine, "minio": minio, "bucket": bucket, "runtime": runtime}
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()


def issue_security_decision(engine, *, env: dict) -> str:
    source_hash = hashlib.sha256(CONTENT).hexdigest()
    with SecurityUnitOfWork(engine) as repo:
        repo.ensure_principal_context(
            principal_context_id=f"pc:{env['tenant_id']}:{env['principal_id']}",
            tenant_id=env["tenant_id"],
            user_principal_id=env["principal_id"],
            epoch_ref=env["epoch_ref"],
        )
        repo.ensure_effective_epoch(
            epoch_ref=env["epoch_ref"],
            tenant_id=env["tenant_id"],
            policy_bundle_ref="policy-bundle:phase22:v1",
            policy_bundle={"version": "v1"},
            action_set_version="v1",
            principal_context_hash="b" * 64,
            generation=1,
            status="active",
        )
        decision_id = f"decision:{env['tenant_id']}:{env['source_id']}:1"
        repo.ensure_authorization_decision(
            decision_id=decision_id,
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
            reason_code="phase22_fault_matrix",
            prepared_action_hash=source_hash,
        )
        return decision_id


def new_env(bucket: str) -> dict:
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


def build_command(env: dict, decision_id: str) -> CanonicalSourceIngestCommand:
    return CanonicalSourceIngestCommand(
        tenant_id=env["tenant_id"],
        workspace_id=env["workspace_id"],
        principal_id=env["principal_id"],
        source_id=env["source_id"],
        document_id=env["document_id"],
        filename="crash.md",
        mime_type="text/markdown",
        content=CONTENT,
        classification="global/open",
        security_epoch_ref=env["epoch_ref"],
        security_decision_ref=decision_id,
        knowledge_space_id=env["knowledge_space_id"],
        corpus_manifest_ref="corpus:fault-matrix",
        source_set_ref="corpus:fault-matrix",
        trace_id=f"trace-{uuid4().hex[:8]}",
        bucket=env["bucket"],
    )


def minimal_manifest(env: dict) -> dict:
    return {
        "source_manifest_hash": "corpus:fault-matrix",
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
                "entity_id": f"entity::org:Acme{env['source_id'].split('-')[-1]}",
                "entity_ref": f"org:Acme{env['source_id'].split('-')[-1]}",
                "label": "Acme",
                "chunk_id": f"chunk::{env['document_id']}::001",
                "document_id": env["document_id"],
            }
        ],
        "relations": [],
    }


def crash_runtime(live_env, crash_at: str) -> Phase22CanonicalIngestionRuntime:
    """Runtime that raises after the given durable step (crash simulation)."""

    def hook(step: str) -> None:
        if step == crash_at:
            raise CrashSimulation(f"simulated crash at {step}")

    return Phase22CanonicalIngestionRuntime(
        engine=live_env["engine"],
        object_store=DurableMinioObjectStore(
            store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
        ),
        bucket=live_env["bucket"],
        worker_id=f"phase22-fault-{crash_at}",
        fault_hook=hook,
    )


CRASH_POINTS = [
    "object_staged",                    # 1. after object_staged
    "object_committed",                 # 2. after object_committed
    "source_document_facts_committed",  # 3. after DocumentVersion commit
    "parse_snapshot_committed",         # 4. after ParseSnapshot commit
    "knowledge_facts_committed",        # 5/6. after Chunk/Entity/Relation commit
    "knowledge_version_ready",          # 7. after KV commit, before receipt
]


class TestPhase22ResumeFaultMatrix:
    @pytest.mark.parametrize("crash_at", CRASH_POINTS)
    def test_crash_resume_no_duplicates(self, live_env, crash_at: str) -> None:
        env = new_env(live_env["bucket"])
        decision_id = issue_security_decision(live_env["engine"], env=env)
        command = build_command(env, decision_id)

        crashed = crash_runtime(live_env, crash_at)
        crashed.load_corpus_manifest(minimal_manifest(env))
        with pytest.raises(CrashSimulation):
            crashed.ingest(command)

        # durable checkpoint holds the run at the last completed step
        from zuno.knowledge.ingestion.canonical_runtime import canonical_run_id

        run_fact = crashed.runs.current_fact(
            run_id=canonical_run_id(
                tenant_id=env["tenant_id"],
                workspace_id=env["workspace_id"],
                source_id=env["source_id"],
            ),
            tenant_id=env["tenant_id"],
        )
        # scenario 7 crashes after the KnowledgeVersion transition but before
        # the receipt returns — the durable checkpoint is already kv_ready
        if crash_at != "knowledge_version_ready":
            assert run_fact.current_state != CANONICAL_STATE_KV_READY

        # resume with a fresh runtime instance that keeps the crashed
        # worker's identity (restart semantics: the lease is fenced to the
        # worker_id; a different worker must wait for lease expiry instead)
        resumed = Phase22CanonicalIngestionRuntime(
            engine=live_env["engine"],
            object_store=DurableMinioObjectStore(
                store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
            ),
            bucket=live_env["bucket"],
            worker_id=f"phase22-fault-{crash_at}",
        )
        resumed.load_corpus_manifest(minimal_manifest(env))
        receipt = resumed.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY
        assert receipt.transitions[-1]["to_state"] == CANONICAL_STATE_KV_READY

        # no duplicated facts
        engine = live_env["engine"]
        with engine.connect() as connection:
            source_count = connection.execute(
                text(
                    """
                    SELECT count(*) FROM ingestion_source_objects
                    WHERE tenant_id = :tenant_id AND source_object_id = :source_id
                    """
                ),
                {"tenant_id": env["tenant_id"], "source_id": env["source_id"]},
            ).scalar_one()
            attempt_count = connection.execute(
                text(
                    """
                    SELECT count(*) FROM ingestion_parse_attempts
                    WHERE tenant_id = :tenant_id AND parse_job_id = :parse_job_id
                    """
                ),
                {
                    "tenant_id": env["tenant_id"],
                    "parse_job_id": f"parse-job:{env['source_id']}:1",
                },
            ).scalar_one()
            snapshot_count = connection.execute(
                text(
                    """
                    SELECT count(*) FROM ingestion_parse_snapshots
                    WHERE tenant_id = :tenant_id
                      AND document_version_id = :document_version_id
                    """
                ),
                {
                    "tenant_id": env["tenant_id"],
                    "document_version_id": f"document-version:{env['source_id']}:1",
                },
            ).scalar_one()
        assert source_count == 1
        assert attempt_count == 1
        assert snapshot_count == 1
        chunks = resumed.facts.chunk_facts(
            tenant_id=env["tenant_id"],
            knowledge_version_id=receipt.knowledge_version_id,
        )
        assert len(chunks) == 1
        entities = resumed.entities_relations.entity_facts(
            tenant_id=env["tenant_id"],
            workspace_id=env["workspace_id"],
            knowledge_version_id=receipt.knowledge_version_id,
        )
        assert len(entities) == 1
        run_fact = resumed.runs.current_fact(
            run_id=canonical_run_id(
                tenant_id=env["tenant_id"],
                workspace_id=env["workspace_id"],
                source_id=env["source_id"],
            ),
            tenant_id=env["tenant_id"],
        )
        assert run_fact.current_state == CANONICAL_STATE_KV_READY
        assert run_fact.state_version == 5

    def test_physical_object_without_manifest_reconciles(self, live_env) -> None:
        """Scenario 8: physical object exists but the manifest is uncertain."""
        from io import BytesIO

        env = new_env(live_env["bucket"])
        decision_id = issue_security_decision(live_env["engine"], env=env)
        command = build_command(env, decision_id)
        runtime = Phase22CanonicalIngestionRuntime(
            engine=live_env["engine"],
            object_store=DurableMinioObjectStore(
                store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
            ),
            bucket=live_env["bucket"],
            worker_id="phase22-reconcile-worker",
        )
        runtime.load_corpus_manifest(minimal_manifest(env))
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY

        # remove the manifest row (fault injection: manifest uncertainty)
        engine = live_env["engine"]
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM infra_object_manifests WHERE object_ref = :object_ref"),
                {"object_ref": receipt.object_ref},
            )
        reconciled = runtime.reconcile(
            run_id=receipt.run_id, tenant_id=env["tenant_id"]
        )
        assert reconciled.state == CANONICAL_FAILURE_RECONCILIATION_REQUIRED
        assert reconciled.failure_code == "object_manifest_missing"

        # restore through the explicit reconciliation edge: commit recreates
        # the manifest from the committed object and the run completes
        resumed = runtime.resume_after_reconcile(
            command, to_state=CANONICAL_STATE_OBJECT_COMMITTED
        )
        assert resumed.state == CANONICAL_STATE_KV_READY

    def test_domain_state_behind_manifest_resumes(self, live_env) -> None:
        """Scenario 9: manifest exists but domain state was not updated."""
        env = new_env(live_env["bucket"])
        decision_id = issue_security_decision(live_env["engine"], env=env)
        command = build_command(env, decision_id)
        runtime = Phase22CanonicalIngestionRuntime(
            engine=live_env["engine"],
            object_store=DurableMinioObjectStore(
                store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
            ),
            bucket=live_env["bucket"],
            worker_id="phase22-stale-state-worker",
        )
        runtime.load_corpus_manifest(minimal_manifest(env))
        receipt = runtime.ingest(command)
        assert receipt.state == CANONICAL_STATE_KV_READY

        # fault injection: reset the durable run state to accepted (the
        # physical world and manifest are ahead of the domain state)
        engine = live_env["engine"]
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    UPDATE canonical_ingestion_runs
                    SET current_state = 'accepted', state_version = 1
                    WHERE run_id = :run_id AND tenant_id = :tenant_id
                    """
                ),
                {"run_id": receipt.run_id, "tenant_id": env["tenant_id"]},
            )
        replayed = runtime.ingest(command)
        assert replayed.state == CANONICAL_STATE_KV_READY
        # no duplicates despite the replay over existing facts
        with engine.connect() as connection:
            source_count = connection.execute(
                text(
                    """
                    SELECT count(*) FROM ingestion_source_objects
                    WHERE tenant_id = :tenant_id AND source_object_id = :source_id
                    """
                ),
                {"tenant_id": env["tenant_id"], "source_id": env["source_id"]},
            ).scalar_one()
        assert source_count == 1

    def test_duplicate_worker_claim_is_idempotent(self, live_env) -> None:
        """Scenario 10: duplicate messages / duplicate worker claims."""
        env = new_env(live_env["bucket"])
        decision_id = issue_security_decision(live_env["engine"], env=env)
        command = build_command(env, decision_id)

        worker_a = Phase22CanonicalIngestionRuntime(
            engine=live_env["engine"],
            object_store=DurableMinioObjectStore(
                store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
            ),
            bucket=live_env["bucket"],
            worker_id="phase22-worker-a",
        )
        worker_b = Phase22CanonicalIngestionRuntime(
            engine=live_env["engine"],
            object_store=DurableMinioObjectStore(
                store=live_env["minio"], engine=live_env["engine"], owner="phase22.fault"
            ),
            bucket=live_env["bucket"],
            worker_id="phase22-worker-b",
        )
        manifest = minimal_manifest(env)
        worker_a.load_corpus_manifest(manifest)
        worker_b.load_corpus_manifest(manifest)
        first = worker_a.ingest(command)
        assert first.state == CANONICAL_STATE_KV_READY
        # second worker's claim reads the durable checkpoint and returns the
        # same facts instead of re-executing
        second = worker_b.ingest(command)
        assert second.state == CANONICAL_STATE_KV_READY
        assert second.idempotent is True
        assert second.knowledge_version_id == first.knowledge_version_id
        engine = live_env["engine"]
        with engine.connect() as connection:
            attempt_count = connection.execute(
                text(
                    """
                    SELECT count(*) FROM ingestion_parse_attempts
                    WHERE tenant_id = :tenant_id AND parse_job_id = :parse_job_id
                    """
                ),
                {
                    "tenant_id": env["tenant_id"],
                    "parse_job_id": f"parse-job:{env['source_id']}:1",
                },
            ).scalar_one()
        assert attempt_count == 1
