from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.database.capability import CapabilityRepository, CapabilitySupplyChainConflict
from zuno.platform.database.capability.domain import CapabilityVersionInput
from zuno.platform.database.foundation import create_foundation_engine
from zuno.platform.database.knowledge import KnowledgeCutoverConflict, KnowledgeRepository
from zuno.platform.database.knowledge.domain import KnowledgeVersionDraft
from zuno.platform.database.product import ProductCommandSubmission, ProductPersistenceConflict, ProductRepository


REPO_ROOT = Path(__file__).resolve().parents[2]
DATABASE_URL = os.environ.get(
    "ZUNO_TEST_POSTGRES_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/zuno?connect_timeout=5",
)


@pytest.fixture(scope="session", autouse=True)
def migrated_postgres() -> None:
    env = {
        **os.environ,
        "PGCONNECT_TIMEOUT": os.environ.get("PGCONNECT_TIMEOUT", "5"),
        "ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS": os.environ.get("ZUNO_ALEMBIC_LOCK_TIMEOUT_SECONDS", "5"),
    }
    result = subprocess.run(
        ["alembic", "-c", "infra/db/alembic.ini", "upgrade", "head"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture()
def engine(migrated_postgres):
    engine = create_foundation_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                TRUNCATE
                    infra_outbox_events,
                    infra_outbox_sequences,
                    capability_transition_events,
                    capability_selection_results,
                    capability_availability_snapshots,
                    capability_installations,
                    capability_conformance_records,
                    capability_provider_bindings,
                    skill_versions,
                    capability_versions,
                    capability_definitions,
                    knowledge_citation_lineage,
                    knowledge_evidence_records,
                    knowledge_retrieval_rounds,
                    knowledge_query_runs,
                    knowledge_cutover_decisions,
                    knowledge_index_build_jobs,
                    knowledge_chunks,
                    knowledge_snapshots,
                    knowledge_domain_versions,
                    product_stream_cursors,
                    product_action_tokens,
                    product_projection_events,
                    product_command_receipts,
                    product_commands,
                    product_messages,
                    product_submissions,
                    product_conversation_threads,
                    product_agent_versions,
                    product_agent_definitions
                RESTART IDENTITY
                """
            )
        )
    try:
        yield engine
    finally:
        engine.dispose()


def _seed_product_agent_version(conn) -> None:
    conn.execute(
        text(
            """
            INSERT INTO product_agent_definitions (
                agent_definition_id, tenant_id, workspace_id, owner_principal_id,
                display_name, status, aggregate_version
            )
            VALUES ('agent-def:wave-a', 'tenant-a', 'workspace-a', 'principal-a', 'Wave A Agent', 'ACTIVE', 1)
            """
        )
    )
    conn.execute(
        text(
            """
            INSERT INTO product_agent_versions (
                agent_version_id, tenant_id, agent_definition_id, version_no,
                config_hash, primary_agent_core_profile_ref, status
            )
            VALUES (
                'agent-version:wave-a', 'tenant-a', 'agent-def:wave-a', 1,
                repeat('a', 64), 'agent-core-profile:default', 'PUBLISHED'
            )
            """
        )
    )


def _product_command(client_request_id: str, payload: dict[str, str], command_id: str) -> ProductCommandSubmission:
    return ProductCommandSubmission(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        conversation_id="conversation:wave-a",
        principal_id="principal-a",
        active_agent_version_id="agent-version:wave-a",
        submission_id=f"submission:{command_id}",
        client_request_id=client_request_id,
        raw_intent_ref="object://intent/wave-a",
        command_id=command_id,
        command_kind="CREATE_RUNTIME_REQUEST",
        owner_module="Agent Core",
        runtime_request_ref="runtime-request:wave-a",
        payload=payload,
        journal_sequence_no=1,
        outbox_message_id=f"outbox:{command_id}",
    )


def test_phase09_product_command_is_idempotent_and_receipt_does_not_claim_domain_success(engine) -> None:
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        first = repo.submit_command(_product_command("client:1", {"query": "renewal"}, "command:1"))
        duplicate = repo.submit_command(_product_command("client:1", {"query": "renewal"}, "command:2"))

        assert first.status == "ACCEPTED"
        assert duplicate.status == "DUPLICATE"
        assert duplicate.command_id == first.command_id
        second = repo.submit_command(_product_command("client:2", {"query": "summary"}, "command:4"))
        assert second.status == "ACCEPTED"

        product_rows = conn.execute(
            text(
                """
                SELECT
                    (SELECT count(*) FROM product_submissions) AS submissions,
                    (SELECT count(*) FROM product_messages) AS messages,
                    (SELECT count(*) FROM product_commands) AS commands,
                    (SELECT count(*) FROM product_command_receipts WHERE status = 'ACCEPTED') AS accepted_receipts,
                    (SELECT count(*) FROM infra_outbox_events WHERE topic = 'product.runtime_request.dispatch') AS dispatch_events
                """
            )
        ).mappings().one()
        assert dict(product_rows) == {
            "submissions": 2,
            "messages": 2,
            "commands": 2,
            "accepted_receipts": 2,
            "dispatch_events": 2,
        }
        dispatch = conn.execute(
            text(
                """
                SELECT aggregate_id, payload ->> 'consumer_module' AS consumer_module,
                       payload ->> 'message_id' AS message_id, ordering_sequence
                FROM infra_outbox_events
                WHERE event_id = 'outbox:command:1'
                """
            )
        ).mappings().one()
        assert dispatch["aggregate_id"] == "command:1"
        assert dispatch["consumer_module"] == "Agent Core"
        assert dispatch["message_id"] == "message:submission:command:1"
        assert dispatch["ordering_sequence"] == 1

        with pytest.raises(ProductPersistenceConflict):
            repo.submit_command(_product_command("client:1", {"query": "different"}, "command:3"))

        with pytest.raises(ProductPersistenceConflict):
            repo.append_owner_receipt(
                tenant_id="tenant-a",
                command_id="command:1",
                status="ACCEPTED",
                owner_receipt_ref="owner:receipt",
                payload={"domain_success_ref": "agent-run:success"},
            )


def test_phase09_product_projection_stream_cursor_and_action_token_are_persisted(engine) -> None:
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        receipt = repo.submit_command(_product_command("client:projection", {"query": "renewal"}, "command:projection"))
        watermark = repo.next_projection_watermark(tenant_id="tenant-a", workspace_id="workspace-a")
        projection = repo.record_projection_event(
            projection_event_id="projection:command:projection:accepted",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_module="Product Surface",
            source_event_id=receipt.command_id,
            source_watermark=watermark,
            projection_payload={
                "command_id": receipt.command_id,
                "receipt_id": receipt.receipt_id,
                "status": receipt.status,
            },
            redaction_decision_ref="redaction:projection:server",
        )
        action = repo.issue_action_token(
            action_token_id="action-token:command:projection:cancel",
            tenant_id="tenant-a",
            principal_id="principal-a",
            target_ref="runtime-request:wave-a",
            command_kind="CANCEL_RUNTIME_REQUEST",
            effective_security_epoch_ref="security-epoch:wave-a",
            nonce="nonce:command:projection:cancel",
            expires_at=now + timedelta(minutes=5),
        )
        cursor = repo.open_stream_cursor(
            cursor_id="cursor:command:projection:1",
            tenant_id="tenant-a",
            principal_id="principal-a",
            projection_event_id=projection.projection_event_id,
            last_sequence_no=projection.source_watermark,
            effective_security_epoch_ref="security-epoch:wave-a",
            expires_at=now + timedelta(minutes=15),
            reauthorized_at=now,
        )

        rows = conn.execute(
            text(
                """
                SELECT
                    (SELECT count(*) FROM product_projection_events) AS projection_events,
                    (SELECT count(*) FROM product_stream_cursors) AS stream_cursors,
                    (SELECT count(*) FROM product_action_tokens WHERE used_at IS NULL AND revoked_at IS NULL) AS active_tokens
                """
            )
        ).mappings().one()
        assert dict(rows) == {
            "projection_events": 1,
            "stream_cursors": 1,
            "active_tokens": 1,
        }
        assert action.command_kind == "CANCEL_RUNTIME_REQUEST"
        assert cursor.last_sequence_no == projection.source_watermark

        replay = repo.record_projection_event(
            projection_event_id="projection:command:projection:duplicate",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_module="Product Surface",
            source_event_id=receipt.command_id,
            source_watermark=999,
            projection_payload={"different": "payload"},
            redaction_decision_ref="redaction:projection:server",
        )
        assert replay.duplicate is True
        assert replay.projection_event_id == projection.projection_event_id

        since_event = repo.list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            last_event_id=projection.projection_event_id,
        )
        assert since_event == ()

        expired = repo.open_stream_cursor(
            cursor_id="cursor:expired",
            tenant_id="tenant-a",
            principal_id="principal-a",
            projection_event_id=projection.projection_event_id,
            last_sequence_no=projection.source_watermark,
            effective_security_epoch_ref="security-epoch:wave-a",
            expires_at=now - timedelta(seconds=1),
            reauthorized_at=now - timedelta(minutes=20),
        )
        resync = repo.list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            last_event_id=expired.cursor_id,
            now=now,
        )
        assert len(resync) == 1
        assert resync[0].projection_event_id == f"resync:{expired.cursor_id}"
        assert resync[0].gap_detected is True


def _knowledge_draft() -> KnowledgeVersionDraft:
    return KnowledgeVersionDraft(
        knowledge_version_id="knowledge-version:wave-a",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        knowledge_space_id="knowledge-space:wave-a",
        version_no=1,
        document_set={"documents": ["document-version:1"]},
        source_span_manifest={"spans": ["source-span:1"]},
        index_spec={"bm25": True, "vector": True},
        security_epoch_ref="security-epoch:wave-a",
    )


def test_phase12_knowledge_version_requires_visible_indexes_before_cutover_and_pins_snapshot(engine) -> None:
    with engine.begin() as conn:
        repo = KnowledgeRepository(conn)
        repo.create_version(_knowledge_draft())
        repo.append_chunk(
            chunk_id="chunk:1",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:wave-a",
            document_version_id="document-version:1",
            source_span_ref="source-span:1",
            chunk_payload={"text": "Renewal terms are annual."},
            acl_ref="acl:internal",
            authority_ref="authority:policy",
        )
        repo.record_index_visibility(
            job_id="job:bm25",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:wave-a",
            index_kind="BM25",
            lease_ref="lease:bm25",
            fencing_token=1,
            attempt_no=1,
            write_batch={"chunk": "chunk:1"},
            visibility_receipt_ref="visible:bm25",
        )
        with pytest.raises(KnowledgeCutoverConflict):
            repo.mark_ready(knowledge_version_id="knowledge-version:wave-a")

        repo.record_index_visibility(
            job_id="job:vector",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:wave-a",
            index_kind="VECTOR",
            lease_ref="lease:vector",
            fencing_token=1,
            attempt_no=1,
            write_batch={"chunk": "chunk:1"},
            visibility_receipt_ref="visible:vector",
        )
        repo.mark_ready(knowledge_version_id="knowledge-version:wave-a")
        repo.create_snapshot(
            snapshot_id="snapshot:wave-a",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:wave-a",
            snapshot_payload={"version": "knowledge-version:wave-a"},
            serving_watermark_ref="watermark:1",
        )
        repo.cutover(
            cutover_id="cutover:wave-a",
            tenant_id="tenant-a",
            knowledge_space_id="knowledge-space:wave-a",
            to_version_id="knowledge-version:wave-a",
            expected_generation=2,
            decision_payload={"visibility": "verified"},
        )
        repo.start_query_run(
            query_run_id="query-run:wave-a",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_core_decision_ref="agent-core-decision:retrieve",
            snapshot_id="snapshot:wave-a",
            request_payload={"query": "renewal terms"},
        )
        repo.start_retrieval_round(
            round_id="round:1",
            query_run_id="query-run:wave-a",
            round_no=1,
            retriever_set={"bm25": True, "vector": True},
        )
        repo.commit_evidence(
            evidence_id="evidence:1",
            query_run_id="query-run:wave-a",
            round_id="round:1",
            chunk_id="chunk:1",
            source_span_ref="source-span:1",
            evidence_payload={"quote": "Renewal terms are annual."},
            authority_ref="authority:policy",
        )

        status = conn.execute(
            text("SELECT status FROM knowledge_domain_versions WHERE knowledge_version_id = 'knowledge-version:wave-a'")
        ).scalar_one()
        assert status == "ACTIVE"


def test_phase14_capability_blocks_unverified_skill_and_model_only_active_binding(engine) -> None:
    with engine.begin() as conn:
        repo = CapabilityRepository(conn)
        repo.publish_capability_version(
            CapabilityVersionInput(
                capability_definition_id="capability:def:read",
                capability_version_id="capability:version:read:v1",
                tenant_id="tenant-a",
                semantic_identity="knowledge.standard.retrieve",
                owner_module="Knowledge",
                version_no=1,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_profile_ref="risk:read-only",
            )
        )
        with pytest.raises(CapabilitySupplyChainConflict):
            repo.publish_skill_version(
                skill_version_id="skill:bad:v1",
                tenant_id="tenant-a",
                skill_identity="bad.skill",
                version_no=1,
                metadata={},
                instruction={},
                resource_manifest={},
                signature_ref="signature:missing",
                verified=False,
            )

        repo.propose_binding(
            binding_id="binding:model-only",
            capability_version_id="capability:version:read:v1",
            provider_instance_ref="provider:tool-runtime",
            tool_definition_ref="tool-definition:read:v1",
            mapping_payload={"input": "query"},
            proposal_source="MODEL_PROPOSED",
        )
        repo.record_conformance(
            conformance_id="conformance:model-only",
            binding_id="binding:model-only",
            report_payload={"passed": True},
            covers_input=True,
            covers_output=True,
            covers_idempotency=True,
            covers_reconciliation=True,
            covers_security=True,
        )
        repo.create_availability_snapshot(
            snapshot_id="cap-snapshot:1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            security_epoch_ref="epoch:1",
            source_generation=1,
            visible_candidates=("binding:model-only",),
            ttl_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        repo.record_selection(
            selection_id="selection:1",
            snapshot_id="cap-snapshot:1",
            requirement={"capability": "knowledge.standard.retrieve"},
            selected_binding_id=None,
            candidate_summary={"rejected": ["binding:model-only"]},
            rejection_reason_codes=["MODEL_PROPOSED_NOT_ACTIVE"],
        )
        repo.record_selection(
            selection_id="selection:1",
            snapshot_id="cap-snapshot:1",
            requirement={"capability": "knowledge.standard.retrieve"},
            selected_binding_id=None,
            candidate_summary={"rejected": ["binding:model-only"]},
            rejection_reason_codes=["MODEL_PROPOSED_NOT_ACTIVE"],
        )

        binding_status = conn.execute(
            text("SELECT status FROM capability_provider_bindings WHERE binding_id = 'binding:model-only'")
        ).scalar_one()
        assert binding_status == "PROPOSED"
        dispatch = conn.execute(
            text(
                """
                SELECT aggregate_id, payload ->> 'consumer_module' AS consumer_module,
                       payload ->> 'snapshot_id' AS snapshot_id, ordering_sequence
                FROM infra_outbox_events
                WHERE topic = 'capability.selection.committed'
                """
            )
        ).mappings().one()
        assert dispatch["aggregate_id"] == "selection:1"
        assert dispatch["consumer_module"] == "Agent Core"
        assert dispatch["snapshot_id"] == "cap-snapshot:1"
        assert dispatch["ordering_sequence"] == 1
