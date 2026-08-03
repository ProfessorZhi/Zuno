from __future__ import annotations

"""PHASE22 official synthetic corpus live ingestion (Task F).

Consumes the frozen PR #107 artifacts only:

- ``source_upload_manifest.json`` (8 sources, corpus hash, per-source hash)
- the official corpus files under ``candidate-dataset/corpus/``
- ``canonical_ir_manifest.json`` (24 chunks, 15 entities, 5 relations)

One corpus KnowledgeVersion binds all documents. Every ID is reconciled
against the official manifest; any count/ID mismatch marks the corpus run
FAILED. Security decisions are issued by the Security owner in advance; the
runtime only validates them.
"""


import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text

from zuno.knowledge.ingestion.canonical_runtime import (
    CANONICAL_STATE_KV_READY,
    CanonicalCorpusReceipt,
    Phase22CanonicalIngestionRuntime,
    canonical_security_resource_ref,
)
from zuno.knowledge.storage.canonical_facts import CanonicalIngestionFactsStore
from zuno.platform.contracts import canonical_sha256
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

EVIDENCE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression"
)
SOURCE_MANIFEST_PATH = EVIDENCE_ROOT / "source_upload_manifest.json"
IR_MANIFEST_PATH = EVIDENCE_ROOT / "canonical_ir_manifest.json"
# the manifest source_path already carries the corpus/ prefix
CORPUS_DIR = EVIDENCE_ROOT / "candidate-dataset"

PRINCIPAL_ID = "principal:corpus-runner"
KNOWLEDGE_SPACE_ID = "space::tenant_auroralis::workspace_regression::phase22-synthetic"
# The frozen manifest was prepared with candidate facts under the official
# tenant (source rows, 59 legacy chunks, marked runtime_ingested: false in the
# source manifest). The corpus verification run pins an isolated tenant so the
# real runtime ingestion reconciles cleanly against the official manifest
# without colliding with the preparation candidates. All corpus identity
# fields (source ids, hashes, document ids) still come from the frozen
# manifest unchanged.
VERIFICATION_TENANT = "tenant_auroralis_verify"
VERIFICATION_WORKSPACE = "workspace_regression_verify"


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
        f"{DATABASE_URL} / {MINIO_ENDPOINT}; official corpus test skipped"
    ),
)


def _reset_verification_tenant(engine) -> None:
    """Clean this suite's own artifacts under the isolated verification tenant
    so reruns are deterministic. Never touches the official tenant or the
    CC-A preparation candidate facts."""
    with engine.begin() as connection:
        for table in (
            "security_authorization_decisions",
            "security_principal_contexts",
            "security_effective_epochs",
            "canonical_ingestion_runs",
            "knowledge_relations",
            "knowledge_entities",
            "knowledge_chunks",
            "knowledge_domain_versions",
            "ingestion_quality_gate_decisions",
            "ingestion_source_spans",
            "ingestion_review_decision_receipts",
            "ingestion_review_tasks",
            "ingestion_parse_snapshots",
            "ingestion_parse_leases",
            "ingestion_parse_attempts",
            "ingestion_parse_jobs",
            "ingestion_parse_plans",
            "ingestion_document_versions",
            "ingestion_source_objects",
        ):
            connection.execute(
                text(f"DELETE FROM {table} WHERE tenant_id = :tenant_id"),
                {"tenant_id": VERIFICATION_TENANT},
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
    bucket = f"zuno-phase22-corpus-{uuid4().hex[:12]}"
    durable = DurableMinioObjectStore(store=minio, engine=engine, owner="phase22.corpus")
    runtime = Phase22CanonicalIngestionRuntime(
        engine=engine,
        object_store=durable,
        bucket=bucket,
        worker_id="phase22-corpus-worker",
    )
    _reset_verification_tenant(engine)
    try:
        yield {"engine": engine, "minio": minio, "bucket": bucket, "runtime": runtime}
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_corpus_security_decisions(engine, source_manifest: dict) -> dict[str, str]:
    """The Security owner issues one decision per official source."""
    tenant_id = VERIFICATION_TENANT
    workspace_id = VERIFICATION_WORKSPACE
    epoch_ref = f"security-epoch:{tenant_id}:phase22-corpus"
    decision_refs: dict[str, str] = {}
    with SecurityUnitOfWork(engine) as repo:
        repo.ensure_principal_context(
            principal_context_id=f"pc:{tenant_id}:{PRINCIPAL_ID}",
            tenant_id=tenant_id,
            user_principal_id=PRINCIPAL_ID,
            epoch_ref=epoch_ref,
        )
        repo.ensure_effective_epoch(
            epoch_ref=epoch_ref,
            tenant_id=tenant_id,
            policy_bundle_ref="policy-bundle:phase22:corpus-v1",
            policy_bundle={"version": "corpus-v1"},
            action_set_version="v1",
            principal_context_hash="b" * 64,
            generation=1,
            status="active",
        )
        for source in source_manifest["sources"]:
            source_id = str(source["source_id"])
            decision_id = f"decision:{tenant_id}:{source_id}:1"
            repo.ensure_authorization_decision(
                decision_id=decision_id,
                tenant_id=tenant_id,
                principal_context_id=f"pc:{tenant_id}:{PRINCIPAL_ID}",
                epoch_ref=epoch_ref,
                resource_ref=canonical_security_resource_ref(
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    source_id=source_id,
                ),
                action="ingestion.source.upload",
                decision="USE_ONLY",
                reason_code="phase22_official_corpus",
                prepared_action_hash=str(source["source_hash"]),
            )
            decision_refs[source_id] = decision_id
    return decision_refs


class TestPhase22OfficialCorpus:
    def test_official_corpus_ingests_with_full_reconciliation(self, live_env) -> None:
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        assert CORPUS_DIR.exists(), f"official corpus dir missing: {CORPUS_DIR}"
        assert source_manifest["source_count"] == 8
        assert ir_manifest["chunk_count"] == 24
        assert ir_manifest["entity_count"] == 15
        assert ir_manifest["relation_count"] == 5

        # corpus file hashes must match the frozen source manifest (LF
        # normalization, matching the frozen extractor's byte basis)
        for source in source_manifest["sources"]:
            path = CORPUS_DIR / str(source["source_path"])
            observed = hashlib.sha256(
                path.read_bytes().replace(b"\r\n", b"\n")
            ).hexdigest()
            assert observed == str(source["source_hash"]), source["source_id"]

        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_corpus_manifest(ir_manifest)

        corpus: CanonicalCorpusReceipt = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{VERIFICATION_TENANT}:phase22-corpus",
            tenant_id=VERIFICATION_TENANT,
            workspace_id=VERIFICATION_WORKSPACE,
        )
        assert corpus.reconciled is True, corpus.mismatch
        assert corpus.source_count == 8
        assert corpus.document_count == 8
        assert corpus.chunk_count == 24
        assert corpus.entity_count == 15
        assert corpus.relation_count == 5
        assert len(corpus.run_ids) == 8
        assert len(corpus.source_ids) == 8
        assert corpus.knowledge_version_id

        # all 8 runs reached knowledge_version_ready
        facts = CanonicalIngestionFactsStore(live_env["engine"])
        for run_id in corpus.run_ids:
            run_fact = runtime.runs.current_fact(
                run_id=run_id,
                tenant_id=VERIFICATION_TENANT,
            )
            assert run_fact.current_state == CANONICAL_STATE_KV_READY

        # one corpus KnowledgeVersion bound to the full document set
        tenant_id = VERIFICATION_TENANT
        workspace_id = VERIFICATION_WORKSPACE
        version = facts.knowledge_version_fact(
            tenant_id=tenant_id,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        expected_document_set = {
            str(source["source_id"]): str(source["source_hash"])
            for source in source_manifest["sources"]
        }
        assert version.document_set_hash == canonical_sha256(expected_document_set)
        assert version.workspace_id == workspace_id
        # chunk facts bound to the corpus version, all 24 present
        chunks = facts.chunk_facts(
            tenant_id=tenant_id,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        assert len(chunks) == 24

    def test_official_corpus_rerun_is_idempotent(self, live_env) -> None:
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_corpus_manifest(ir_manifest)

        first = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{VERIFICATION_TENANT}:phase22-corpus",
            tenant_id=VERIFICATION_TENANT,
            workspace_id=VERIFICATION_WORKSPACE,
        )
        second = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{VERIFICATION_TENANT}:phase22-corpus",
            tenant_id=VERIFICATION_TENANT,
            workspace_id=VERIFICATION_WORKSPACE,
        )
        assert second.reconciled is True
        assert second.knowledge_version_id == first.knowledge_version_id
        assert second.chunk_ids == first.chunk_ids
        assert second.entity_ids == first.entity_ids
        assert second.relation_ids == first.relation_ids
        assert len(second.run_ids) == 8

    def test_entity_relation_facts_bound_to_corpus_version(self, live_env) -> None:
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_corpus_manifest(ir_manifest)
        corpus = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{VERIFICATION_TENANT}:phase22-corpus",
            tenant_id=VERIFICATION_TENANT,
            workspace_id=VERIFICATION_WORKSPACE,
        )
        tenant_id = VERIFICATION_TENANT
        workspace_id = VERIFICATION_WORKSPACE

        entities = runtime.entities_relations.entity_facts(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        relations = runtime.entities_relations.relation_facts(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        assert len(entities) == 15
        assert len(relations) == 5
        # every relation endpoint is a persisted entity in the same scope
        entity_ids = {entity.entity_id for entity in entities}
        for relation in relations:
            assert relation.from_entity_id in entity_ids
            assert relation.to_entity_id in entity_ids
            assert relation.from_entity_id != relation.to_entity_id
            assert len(relation.relation_hash) == 64
        # relation hashes are deterministic and verifiable
        from zuno.knowledge.storage.entity_relation_facts import relation_fact_hash

        for relation in relations:
            expected = relation_fact_hash(
                {
                    "relation_id": relation.relation_id,
                    "tenant_id": relation.tenant_id,
                    "workspace_id": relation.workspace_id,
                    "knowledge_version_id": relation.knowledge_version_id,
                    "from_entity_id": relation.from_entity_id,
                    "to_entity_id": relation.to_entity_id,
                    "relation_kind": relation.relation_kind,
                    "source_chunk_id": relation.source_chunk_id,
                    "source_span_ref": relation.source_span_ref,
                    "authority_ref": relation.authority_ref,
                }
            )
            assert expected == relation.relation_hash

    def test_entity_relation_cross_tenant_isolation(self, live_env) -> None:
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_corpus_manifest(ir_manifest)
        corpus = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{VERIFICATION_TENANT}:phase22-corpus",
            tenant_id=VERIFICATION_TENANT,
            workspace_id=VERIFICATION_WORKSPACE,
        )
        tenant_id = VERIFICATION_TENANT
        other_tenant = f"tenant-other-{uuid4().hex[:8]}"
        runtime.entities_relations.entity_facts_cross_tenant(
            owner_tenant_id=tenant_id,
            other_tenant_id=other_tenant,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        runtime.entities_relations.relation_facts_cross_tenant(
            owner_tenant_id=tenant_id,
            other_tenant_id=other_tenant,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        # foreign tenant sees no facts bound to this version
        assert runtime.entities_relations.entity_facts(
            tenant_id=other_tenant,
            workspace_id=VERIFICATION_WORKSPACE,
            knowledge_version_id=corpus.knowledge_version_id,
        ) == ()
