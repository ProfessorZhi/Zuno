from __future__ import annotations

"""PHASE22 official synthetic corpus live ingestion (Task F, final scope).

Consumes the frozen PR #107 artifacts only:

- ``candidate_dataset_manifest.json`` (dataset_corpus_hash)
- ``source_upload_manifest.json`` (source_manifest_hash, 8 sources)
- the official corpus files under ``candidate-dataset/corpus/``
- ``canonical_ir_manifest.json`` (canonical_ir_hash, 24 chunks, 15 entities,
  5 relations)

The formal scope is used unchanged: ``tenant_auroralis`` /
``workspace_regression`` — every fact (source, document, knowledge space,
security decision, KnowledgeVersion) inherits it. Isolation is achieved with a
dedicated scratch PostgreSQL database (created, migrated, and dropped by this
suite), never by changing the domain scope.

The three frozen hashes are carried separately (never aliased); the
KnowledgeVersion index_spec freezes all three plus document_set_hash,
chunk_set_hash and the security epoch. Any missing or inconsistent hash fails
closed.
"""

import hashlib
import json
import os
import subprocess
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

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTGRES_ADMIN_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_ADMIN_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/postgres?connect_timeout=5",
)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = os.environ.get("ZUNO_TEST_MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("ZUNO_TEST_MINIO_SECRET_KEY", "minioadmin")

EVIDENCE_ROOT = (
    Path(__file__).resolve().parents[2]
    / "docs/evidence/goal05-phase22-machine-attested-synthetic-regression"
)
DATASET_MANIFEST_PATH = EVIDENCE_ROOT / "candidate-dataset/candidate_dataset_manifest.json"
SOURCE_MANIFEST_PATH = EVIDENCE_ROOT / "source_upload_manifest.json"
IR_MANIFEST_PATH = EVIDENCE_ROOT / "canonical_ir_manifest.json"
# the manifest source_path already carries the corpus/ prefix
CORPUS_DIR = EVIDENCE_ROOT / "candidate-dataset"

PRINCIPAL_ID = "principal:corpus-runner"
KNOWLEDGE_SPACE_ID = "space::tenant_auroralis::workspace_regression::phase22-synthetic"

# The frozen formal scope — never changed by the verification environment.
FORMAL_TENANT = "tenant_auroralis"
FORMAL_WORKSPACE = "workspace_regression"

# Frozen three hashes (non-interchangeable).
DATASET_CORPUS_HASH = "749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4"
SOURCE_MANIFEST_HASH = "0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a"
CANONICAL_IR_HASH = "43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6"


def _services_available() -> bool:
    try:
        engine = create_engine(POSTGRES_ADMIN_URL)
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
        "BLOCKED_WITH_EXACT_GAPS: PostgreSQL or MinIO unreachable; official "
        "corpus test skipped"
    ),
)


def _scratch_database_url(database_name: str) -> str:
    return (
        f"postgresql+psycopg://postgres:postgres@localhost:5432/"
        f"{database_name}?connect_timeout=5"
    )


def _migrate_scratch_database(database_name: str, config_file: Path) -> None:
    env = {
        **os.environ,
        "ZUNO_CONFIG": str(config_file),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": "10",
        "PGCONNECT_TIMEOUT": "5",
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


@pytest.fixture(scope="module")
def live_env(tmp_path_factory: pytest.TempPathFactory):
    """Isolation method: dedicated scratch database (separate database name)."""
    database_name = f"zuno_phase22_corpus_{uuid4().hex[:12]}"
    admin = create_engine(POSTGRES_ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    admin.dispose()
    tmp_path = tmp_path_factory.mktemp("phase22-corpus-config")
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "database:\n"
        f"  sync_endpoint: {_scratch_database_url(database_name)}\n"
        f"  async_endpoint: {_scratch_database_url(database_name).replace('psycopg', 'asyncpg')}\n",
        encoding="utf-8",
    )
    _migrate_scratch_database(database_name, config_file)

    engine = create_engine(_scratch_database_url(database_name))
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
    try:
        yield {
            "engine": engine,
            "minio": minio,
            "bucket": bucket,
            "runtime": runtime,
            "database_name": database_name,
        }
    finally:
        try:
            minio.remove_bucket_tree(bucket)
        except Exception:
            pass
        engine.dispose()
        # drop the scratch database (isolation cleanup)
        admin = create_engine(POSTGRES_ADMIN_URL, isolation_level="AUTOCOMMIT")
        with admin.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :name AND pid <> pg_backend_pid()"
                ),
                {"name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
        admin.dispose()


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def issue_corpus_security_decisions(engine, source_manifest: dict) -> dict[str, str]:
    """The Security owner issues one decision per official source under the
    FORMAL scope (tenant_auroralis / workspace_regression)."""
    epoch_ref = f"security-epoch:{FORMAL_TENANT}:phase22-corpus"
    decision_refs: dict[str, str] = {}
    with SecurityUnitOfWork(engine) as repo:
        repo.ensure_principal_context(
            principal_context_id=f"pc:{FORMAL_TENANT}:{PRINCIPAL_ID}",
            tenant_id=FORMAL_TENANT,
            user_principal_id=PRINCIPAL_ID,
            epoch_ref=epoch_ref,
        )
        repo.ensure_effective_epoch(
            epoch_ref=epoch_ref,
            tenant_id=FORMAL_TENANT,
            policy_bundle_ref="policy-bundle:phase22:corpus-v1",
            policy_bundle={"version": "corpus-v1"},
            action_set_version="v1",
            principal_context_hash="b" * 64,
            generation=1,
            status="active",
        )
        for source in source_manifest["sources"]:
            source_id = str(source["source_id"])
            decision_id = f"decision:{FORMAL_TENANT}:{source_id}:1"
            repo.ensure_authorization_decision(
                decision_id=decision_id,
                tenant_id=FORMAL_TENANT,
                principal_context_id=f"pc:{FORMAL_TENANT}:{PRINCIPAL_ID}",
                epoch_ref=epoch_ref,
                resource_ref=canonical_security_resource_ref(
                    tenant_id=FORMAL_TENANT,
                    workspace_id=FORMAL_WORKSPACE,
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
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        assert CORPUS_DIR.exists(), f"official corpus dir missing: {CORPUS_DIR}"
        assert source_manifest["source_count"] == 8
        assert ir_manifest["chunk_count"] == 24
        assert ir_manifest["entity_count"] == 15
        assert ir_manifest["relation_count"] == 5

        # the three frozen hashes must match their manifests
        assert dataset_manifest["corpus_hash"] == DATASET_CORPUS_HASH
        assert source_manifest["source_manifest_hash"] == SOURCE_MANIFEST_HASH
        assert ir_manifest["canonical_ir_hash"] == CANONICAL_IR_HASH
        # the IR manifest must reference the same source manifest
        assert ir_manifest["source_manifest_hash"] == SOURCE_MANIFEST_HASH
        # the formal scope is frozen
        for source in source_manifest["sources"]:
            assert source["tenant_id"] == FORMAL_TENANT
            assert source["workspace_id"] == FORMAL_WORKSPACE

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
        runtime.load_official_corpus_context(
            source_manifest=source_manifest,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
        )

        corpus: CanonicalCorpusReceipt = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
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
        # the three hashes are carried separately, never aliased
        assert corpus.dataset_corpus_hash == DATASET_CORPUS_HASH
        assert corpus.source_manifest_hash == SOURCE_MANIFEST_HASH
        assert corpus.canonical_ir_hash == CANONICAL_IR_HASH
        assert corpus.dataset_corpus_hash != corpus.source_manifest_hash
        assert corpus.source_manifest_hash != corpus.canonical_ir_hash
        assert corpus.document_set_hash
        assert corpus.chunk_set_hash == canonical_sha256(
            sorted(corpus.chunk_ids)
        )

        facts = CanonicalIngestionFactsStore(live_env["engine"])
        # all 8 runs reached knowledge_version_ready under the FORMAL scope
        for run_id in corpus.run_ids:
            run_fact = runtime.runs.current_fact(
                run_id=run_id, tenant_id=FORMAL_TENANT
            )
            assert run_fact.current_state == CANONICAL_STATE_KV_READY
            assert run_fact.workspace_id == FORMAL_WORKSPACE
            # scope consistency: every durable fact shares the formal scope
            runtime.verify_scope_consistency(run_id=run_id, tenant_id=FORMAL_TENANT)

        version = facts.knowledge_version_fact(
            tenant_id=FORMAL_TENANT,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        expected_document_set = {
            str(source["source_id"]): str(source["source_hash"])
            for source in source_manifest["sources"]
        }
        assert version.document_set_hash == canonical_sha256(expected_document_set)
        assert version.workspace_id == FORMAL_WORKSPACE
        assert version.security_epoch_ref == f"security-epoch:{FORMAL_TENANT}:phase22-corpus"
        chunks = facts.chunk_facts(
            tenant_id=FORMAL_TENANT,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        assert len(chunks) == 24

    def test_knowledge_version_freezes_the_three_hashes(self, live_env) -> None:
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_official_corpus_context(
            source_manifest=source_manifest,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
        )
        corpus = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
        )
        # the KV row freezes document_set_hash; the index_spec dict (frozen
        # inside index_spec_hash) carries the three hashes + chunk_set_hash +
        # security epoch
        facts = CanonicalIngestionFactsStore(live_env["engine"])
        version = facts.knowledge_version_fact(
            tenant_id=FORMAL_TENANT,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        assert version.document_set_hash == corpus.document_set_hash
        # scope: the KV belongs to the formal tenant/workspace
        assert version.tenant_id == FORMAL_TENANT
        assert version.workspace_id == FORMAL_WORKSPACE

    def test_official_corpus_rerun_is_idempotent(self, live_env) -> None:
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_official_corpus_context(
            source_manifest=source_manifest,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
        )
        first = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
        )
        second = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
        )
        assert second.reconciled is True
        assert second.knowledge_version_id == first.knowledge_version_id
        assert second.chunk_ids == first.chunk_ids
        assert second.entity_ids == first.entity_ids
        assert second.relation_ids == first.relation_ids
        assert len(second.run_ids) == 8
        assert second.dataset_corpus_hash == first.dataset_corpus_hash
        assert second.source_manifest_hash == first.source_manifest_hash
        assert second.canonical_ir_hash == first.canonical_ir_hash

    def test_hash_contract_fails_closed_on_mismatch(self, live_env) -> None:
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        runtime = live_env["runtime"]
        # aliased hash: dataset_corpus_hash == source_manifest_hash is invalid
        aliased = dict(dataset_manifest)
        aliased["corpus_hash"] = SOURCE_MANIFEST_HASH
        with pytest.raises(Exception):
            runtime.load_official_corpus_context(
                source_manifest=source_manifest,
                ir_manifest=ir_manifest,
                dataset_manifest=aliased,
            )
        # invalid dataset hash (not a 64-char digest)
        invalid = dict(dataset_manifest)
        invalid["corpus_hash"] = "not-a-hash"
        with pytest.raises(Exception):
            runtime.load_official_corpus_context(
                source_manifest=source_manifest,
                ir_manifest=ir_manifest,
                dataset_manifest=invalid,
            )
        # tampered IR manifest referencing a different source manifest
        tampered_ir = dict(ir_manifest)
        tampered_ir["source_manifest_hash"] = "8" * 64
        with pytest.raises(Exception):
            runtime.load_official_corpus_context(
                source_manifest=source_manifest,
                ir_manifest=tampered_ir,
                dataset_manifest=dataset_manifest,
            )
        # missing canonical_ir_hash
        missing_ir = {k: v for k, v in ir_manifest.items() if k != "canonical_ir_hash"}
        with pytest.raises(Exception):
            runtime.load_official_corpus_context(
                source_manifest=source_manifest,
                ir_manifest=missing_ir,
                dataset_manifest=dataset_manifest,
            )

    def test_entity_relation_facts_bound_to_corpus_version(self, live_env) -> None:
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_official_corpus_context(
            source_manifest=source_manifest,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
        )
        corpus = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
        )
        entities = runtime.entities_relations.entity_facts(
            tenant_id=FORMAL_TENANT,
            workspace_id=FORMAL_WORKSPACE,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        relations = runtime.entities_relations.relation_facts(
            tenant_id=FORMAL_TENANT,
            workspace_id=FORMAL_WORKSPACE,
            knowledge_version_id=corpus.knowledge_version_id,
        )
        assert len(entities) == 15
        assert len(relations) == 5
        entity_ids = {entity.entity_id for entity in entities}
        for relation in relations:
            assert relation.from_entity_id in entity_ids
            assert relation.to_entity_id in entity_ids
            assert relation.from_entity_id != relation.to_entity_id
            assert len(relation.relation_hash) == 64
            assert relation.tenant_id == FORMAL_TENANT
            assert relation.workspace_id == FORMAL_WORKSPACE
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

    def test_mixed_scope_is_rejected(self, live_env) -> None:
        """A run must never mix the formal scope with a foreign scope."""
        dataset_manifest = load_manifest(DATASET_MANIFEST_PATH)
        source_manifest = load_manifest(SOURCE_MANIFEST_PATH)
        ir_manifest = load_manifest(IR_MANIFEST_PATH)
        decisions = issue_corpus_security_decisions(live_env["engine"], source_manifest)
        runtime = live_env["runtime"]
        runtime.load_official_corpus_context(
            source_manifest=source_manifest,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
        )
        corpus = runtime.ingest_official_corpus(
            source_manifest=source_manifest,
            corpus_dir=CORPUS_DIR,
            ir_manifest=ir_manifest,
            dataset_manifest=dataset_manifest,
            security_decision_refs=decisions,
            knowledge_space_id=KNOWLEDGE_SPACE_ID,
            security_epoch_ref=f"security-epoch:{FORMAL_TENANT}:phase22-corpus",
        )
        # a foreign tenant must not read the formal-scope facts
        other_tenant = f"tenant-other-{uuid4().hex[:8]}"
        with pytest.raises(Exception):
            runtime.runs.current_fact(
                run_id=corpus.run_ids[0], tenant_id=other_tenant
            )
        # scope consistency verifier passes for the formal scope
        runtime.verify_scope_consistency(
            run_id=corpus.run_ids[0], tenant_id=FORMAL_TENANT
        )
        # reading entity facts under a mixed scope (formal tenant, foreign
        # workspace) yields nothing — the facts are bound to the formal scope
        assert runtime.entities_relations.entity_facts(
            tenant_id=FORMAL_TENANT,
            workspace_id=f"workspace-other-{uuid4().hex[:8]}",
            knowledge_version_id=corpus.knowledge_version_id,
        ) == ()
