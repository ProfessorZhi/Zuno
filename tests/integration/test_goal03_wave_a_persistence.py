from __future__ import annotations

import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.capability import (
    CapabilityActivationConflict,
    CapabilityRepository,
    CapabilitySupplyChainConflict,
)
from zuno.platform.database.capability.domain import CapabilityVersionInput
from zuno.platform.database.foundation import FencingRejectedError, InfrastructureRepository, create_foundation_engine
from zuno.platform.database.knowledge import (
    KnowledgeCutoverConflict,
    KnowledgeEvidenceConflict,
    KnowledgeRepository,
)
from zuno.platform.database.knowledge.domain import KnowledgeVersionDraft
from zuno.platform.database.product import ProductCommandSubmission, ProductPersistenceConflict, ProductRepository
from zuno.api.services.capability import CapabilityService
from zuno.api.services.product import ProductService


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
                    infra_delivery_watermarks,
                    infra_inbox_messages,
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
                    product_agent_catalog_entries,
                    product_agent_installations,
                    product_agent_publications,
                    product_agent_drafts,
                    product_agent_versions,
                    product_agent_definitions,
                    agent_domain_events,
                    agent_domain_runs,
                    agent_task_contracts,
                    agent_goal_versions
                RESTART IDENTITY CASCADE
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


def test_phase09_product_owner_receipts_are_append_only_and_versioned(engine) -> None:
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        receipt = repo.submit_command(_product_command("client:receipt", {"query": "renewal"}, "command:receipt"))

        first_owner_receipt = repo.append_owner_receipt(
            tenant_id="tenant-a",
            command_id=receipt.command_id,
            status="REJECTED",
            owner_receipt_ref="owner:receipt:1",
            payload={"owner_status": "rejected", "owner_port": "Agent Core"},
        )
        late_owner_receipt = repo.append_owner_receipt(
            tenant_id="tenant-a",
            command_id=receipt.command_id,
            status="OWNER_TIMEOUT",
            owner_receipt_ref="owner:receipt:2",
            payload={"owner_status": "timeout", "owner_port": "Agent Core"},
        )

        receipt_rows = conn.execute(
            text(
                """
                SELECT receipt_version, receipt_id, status, owner_receipt_ref, receipt_hash
                FROM product_command_receipts
                WHERE command_id = :command_id
                ORDER BY receipt_version
                """
            ),
            {"command_id": receipt.command_id},
        ).mappings().all()
        assert [row["receipt_version"] for row in receipt_rows] == [1, 2, 3]
        assert [row["status"] for row in receipt_rows] == ["ACCEPTED", "REJECTED", "LATE_OWNER_RECEIPT"]
        assert receipt_rows[1]["owner_receipt_ref"] == "owner:receipt:1"
        assert receipt_rows[2]["owner_receipt_ref"] == "owner:receipt:2"
        assert first_owner_receipt == f"{receipt.command_id}:receipt:2"
        assert late_owner_receipt == f"{receipt.command_id}:receipt:3"
        assert receipt_rows[0]["receipt_id"] == f"{receipt.command_id}:receipt:1"
        assert receipt_rows[0]["receipt_hash"] != receipt_rows[1]["receipt_hash"]
        assert receipt_rows[1]["receipt_hash"] != receipt_rows[2]["receipt_hash"]
        expected_late_hash = canonical_sha256(
            {
                "late_owner_receipt": True,
                "late_reason": "owner_receipt_after_prior_owner_receipt",
                "reported_owner_status": "OWNER_TIMEOUT",
                "reported_owner_receipt_ref": "owner:receipt:2",
                "owner_payload": {"owner_status": "timeout", "owner_port": "Agent Core"},
            }
        )
        assert receipt_rows[2]["receipt_hash"] == expected_late_hash


def test_phase09_product_owner_receipt_rejects_unknown_command(engine) -> None:
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)

        with pytest.raises(ProductPersistenceConflict, match="owner receipt target unavailable"):
            repo.append_owner_receipt(
                tenant_id="tenant-a",
                command_id="command:missing",
                status="REJECTED",
                owner_receipt_ref="owner:missing",
                payload={"owner_status": "rejected"},
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

        consumed = repo.consume_action_token(
            action_token_id=action.action_token_id,
            tenant_id="tenant-a",
            principal_id="principal-a",
            now=now,
        )
        assert consumed.used_at == now
        with pytest.raises(ProductPersistenceConflict, match="replay detected"):
            repo.consume_action_token(
                action_token_id=action.action_token_id,
                tenant_id="tenant-a",
                principal_id="principal-a",
                now=now,
            )

        revoked = repo.issue_action_token(
            action_token_id="action-token:command:projection:revoke",
            tenant_id="tenant-a",
            principal_id="principal-a",
            target_ref="runtime-request:wave-a",
            command_kind="CANCEL_RUNTIME_REQUEST",
            effective_security_epoch_ref="security-epoch:wave-a",
            nonce="nonce:command:projection:revoke",
            expires_at=now + timedelta(minutes=5),
        )
        revoked_status = repo.revoke_action_token(
            action_token_id=revoked.action_token_id,
            tenant_id="tenant-a",
            principal_id="principal-a",
            now=now,
        )
        assert revoked_status.revoked_at == now
        with pytest.raises(ProductPersistenceConflict, match="revoked action token"):
            repo.consume_action_token(
                action_token_id=revoked.action_token_id,
                tenant_id="tenant-a",
                principal_id="principal-a",
                now=now,
            )

        cancel_token = repo.issue_action_token(
            action_token_id="action-token:command:projection:cancel-command",
            tenant_id="tenant-a",
            principal_id="principal-a",
            target_ref="runtime-request:wave-a",
            command_kind="CANCEL_RUNTIME_REQUEST",
            effective_security_epoch_ref="security-epoch:wave-a",
            nonce="nonce:command:projection:cancel-command",
            expires_at=now + timedelta(minutes=5),
        )
        cancel_command = repo.consume_action_token_as_command(
            action_token_id=cancel_token.action_token_id,
            tenant_id="tenant-a",
            principal_id="principal-a",
            client_request_id="client:projection:cancel",
            raw_intent_ref="object://intent/wave-a/cancel",
            payload={"reason": "user_cancel"},
            now=now,
        )
        assert cancel_command.status == "ACCEPTED"
        assert cancel_command.target_ref == "runtime-request:wave-a"
        cancel_row = conn.execute(
            text(
                """
                SELECT c.command_kind, c.runtime_request_ref,
                       r.status AS receipt_status,
                       o.topic,
                       o.payload ->> 'consumer_module' AS consumer_module
                FROM product_commands c
                JOIN product_command_receipts r ON r.command_id = c.command_id
                JOIN infra_outbox_events o ON o.aggregate_id = c.command_id
                WHERE c.command_id = :command_id
                """
            ),
            {"command_id": cancel_command.command_id},
        ).mappings().one()
        assert dict(cancel_row) == {
            "command_kind": "CANCEL_RUNTIME_REQUEST",
            "runtime_request_ref": "runtime-request:wave-a",
            "receipt_status": "ACCEPTED",
            "topic": "product.runtime_request.dispatch",
            "consumer_module": "Agent Core",
        }
        with pytest.raises(ProductPersistenceConflict, match="replay detected"):
            repo.consume_action_token_as_command(
                action_token_id=cancel_token.action_token_id,
                tenant_id="tenant-a",
                principal_id="principal-a",
                client_request_id="client:projection:cancel:replay",
                raw_intent_ref="object://intent/wave-a/cancel-replay",
                now=now,
            )

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

        wrong_principal_resync = repo.list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-b",
            last_event_id=cursor.cursor_id,
            now=now,
        )
        assert len(wrong_principal_resync) == 1
        assert wrong_principal_resync[0].projection_event_id == f"resync:{cursor.cursor_id}"
        assert wrong_principal_resync[0].redaction_decision_ref == "redaction:unknown-cursor"
        assert wrong_principal_resync[0].gap_detected is True

        rebuild = repo.record_projection_rebuild(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            rebuild_id="rebuild:projection:1",
            reason="projection_gap_rebuild",
            now=now,
        )
        assert rebuild.projection_event_id == "projection-rebuild:rebuild:projection:1"
        assert rebuild.gap_detected is True
        rebuild_replay = repo.record_projection_rebuild(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            rebuild_id="rebuild:projection:1",
            reason="projection_gap_rebuild",
            now=now,
        )
        assert rebuild_replay.duplicate is True
        rebuild_events = repo.list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            last_event_id=projection.projection_event_id,
            now=now,
        )
        assert [event.projection_event_id for event in rebuild_events] == [
            "projection-rebuild:rebuild:projection:1"
        ]
        assert rebuild_events[0].gap_detected is True
        expired_after_rebuild = repo.list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            last_event_id=cursor.cursor_id,
            now=now,
        )
        assert expired_after_rebuild[0].projection_event_id == f"resync:{cursor.cursor_id}"
        assert expired_after_rebuild[0].gap_detected is True


def test_phase09_product_agent_assets_publish_install_and_catalog(engine) -> None:
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        draft = repo.create_agent_draft(
            draft_id="agent-draft:wave-a",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_definition_id="agent-def:wave-a",
            draft_payload={
                "display_name": "Wave A Agent",
                "primary_agent_core_profile_ref": "agent-core-profile:default",
            },
        )
        publication = repo.publish_agent_version(
            publication_id="agent-publication:wave-a",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_version_id="agent-version:wave-a",
            publication_scope="WORKSPACE",
            publication_payload={"channel": "workspace_catalog"},
        )
        installation = repo.install_agent_version(
            installation_id="agent-installation:wave-a",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_version_id="agent-version:wave-a",
            principal_id="principal-a",
            installation_scope="USER",
        )
        catalog = repo.upsert_catalog_entry(
            catalog_entry_id="agent-catalog:wave-a",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_definition_id="agent-def:wave-a",
            latest_version_id="agent-version:wave-a",
            visibility_scope="WORKSPACE",
        )
        entries = repo.list_catalog_entries(tenant_id="tenant-a", workspace_id="workspace-a")

        assert draft.status == "DRAFT"
        assert publication.status == "PUBLISHED"
        assert installation.status == "ACTIVE"
        assert catalog.status == "VISIBLE"
        assert [entry.catalog_entry_id for entry in entries] == ["agent-catalog:wave-a"]
        assert entries[0].latest_version_id == "agent-version:wave-a"

        conn.execute(
            text(
                """
                UPDATE product_agent_versions
                SET status = 'REVOKED'
                WHERE agent_version_id = 'agent-version:wave-a'
                """
            )
        )
        with pytest.raises(ProductPersistenceConflict, match="Product AgentVersion must be PUBLISHED"):
            repo.install_agent_version(
                installation_id="agent-installation:revoked",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                agent_version_id="agent-version:wave-a",
                principal_id="principal-a",
                installation_scope="USER",
            )


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


def _knowledge_draft_for(version_id: str, version_no: int) -> KnowledgeVersionDraft:
    return KnowledgeVersionDraft(
        knowledge_version_id=version_id,
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        knowledge_space_id="knowledge-space:wave-a",
        version_no=version_no,
        document_set={"documents": [f"document-version:{version_no}"]},
        source_span_manifest={"spans": [f"source-span:{version_no}"]},
        index_spec={"bm25": True, "vector": True},
        security_epoch_ref=f"security-epoch:wave-a:{version_no}",
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
            expected_generation=repo.next_cutover_expected_generation(
                tenant_id="tenant-a",
                knowledge_space_id="knowledge-space:wave-a",
            ),
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


def test_phase12_knowledge_index_visibility_rejects_stale_fencing_and_conflicting_batches(engine) -> None:
    with engine.begin() as conn:
        repo = KnowledgeRepository(conn)
        repo.create_version(_knowledge_draft_for("knowledge-version:index-fencing", 7))
        repo.append_chunk(
            chunk_id="chunk:index-fencing",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:index-fencing",
            document_version_id="document-version:index-fencing",
            source_span_ref="source-span:index-fencing",
            chunk_payload={"text": "Policy index fencing evidence."},
            acl_ref="acl:internal",
            authority_ref="authority:policy",
        )
        repo.record_index_visibility(
            job_id="job:index-fencing:bm25:1",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:index-fencing",
            index_kind="BM25",
            lease_ref="lease:index-fencing:bm25:1",
            fencing_token=2,
            attempt_no=1,
            write_batch={"chunk": "chunk:index-fencing", "target": "bm25"},
            visibility_receipt_ref="visible:index-fencing:bm25:1",
        )
        repo.record_index_visibility(
            job_id="job:index-fencing:bm25:1",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:index-fencing",
            index_kind="BM25",
            lease_ref="lease:index-fencing:bm25:1",
            fencing_token=2,
            attempt_no=1,
            write_batch={"chunk": "chunk:index-fencing", "target": "bm25"},
            visibility_receipt_ref="visible:index-fencing:bm25:1",
        )
        with pytest.raises(KnowledgeCutoverConflict, match="conflicting Knowledge index visibility job"):
            repo.record_index_visibility(
                job_id="job:index-fencing:bm25:1",
                tenant_id="tenant-a",
                knowledge_version_id="knowledge-version:index-fencing",
                index_kind="BM25",
                lease_ref="lease:index-fencing:bm25:1",
                fencing_token=2,
                attempt_no=1,
                write_batch={"chunk": "chunk:index-fencing", "target": "bm25", "conflict": True},
                visibility_receipt_ref="visible:index-fencing:bm25:1",
            )
        with pytest.raises(KnowledgeCutoverConflict, match="stale Knowledge index visibility fencing token"):
            repo.record_index_visibility(
                job_id="job:index-fencing:bm25:stale",
                tenant_id="tenant-a",
                knowledge_version_id="knowledge-version:index-fencing",
                index_kind="BM25",
                lease_ref="lease:index-fencing:bm25:stale",
                fencing_token=1,
                attempt_no=2,
                write_batch={"chunk": "chunk:index-fencing", "target": "bm25", "stale": True},
                visibility_receipt_ref="visible:index-fencing:bm25:stale",
            )
        with pytest.raises(KnowledgeCutoverConflict, match="conflicting Knowledge index visibility write batch"):
            repo.record_index_visibility(
                job_id="job:index-fencing:bm25:conflict",
                tenant_id="tenant-a",
                knowledge_version_id="knowledge-version:index-fencing",
                index_kind="BM25",
                lease_ref="lease:index-fencing:bm25:conflict",
                fencing_token=2,
                attempt_no=1,
                write_batch={"chunk": "chunk:index-fencing", "target": "bm25", "different": True},
                visibility_receipt_ref="visible:index-fencing:bm25:conflict",
            )
        repo.record_index_visibility(
            job_id="job:index-fencing:bm25:recovered",
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:index-fencing",
            index_kind="BM25",
            lease_ref="lease:index-fencing:bm25:recovered",
            fencing_token=3,
            attempt_no=2,
            write_batch={"chunk": "chunk:index-fencing", "target": "bm25", "recovered": True},
            visibility_receipt_ref="visible:index-fencing:bm25:recovered",
        )
        count = conn.execute(
            text(
                """
                SELECT count(*)
                FROM knowledge_index_build_jobs
                WHERE knowledge_version_id = 'knowledge-version:index-fencing'
                  AND index_kind = 'BM25'
                  AND status = 'VISIBLE'
                """
            )
        ).scalar_one()
        assert count == 2


def test_phase12_knowledge_cutover_race_rollback_and_deleted_source_taint_strict_evidence(engine) -> None:
    with engine.begin() as conn:
        repo = KnowledgeRepository(conn)
        for version_no in (1, 2):
            version_id = f"knowledge-version:rollback:{version_no}"
            repo.create_version(_knowledge_draft_for(version_id, version_no))
            repo.append_chunk(
                chunk_id=f"chunk:rollback:{version_no}",
                tenant_id="tenant-a",
                knowledge_version_id=version_id,
                document_version_id=f"document-version:{version_no}",
                source_span_ref=f"source-span:{version_no}",
                chunk_payload={"text": f"Policy version {version_no}."},
                acl_ref="acl:internal",
                authority_ref="authority:policy",
            )
            for index_kind in ("BM25", "VECTOR"):
                repo.record_index_visibility(
                    job_id=f"job:rollback:{version_no}:{index_kind.lower()}",
                    tenant_id="tenant-a",
                    knowledge_version_id=version_id,
                    index_kind=index_kind,
                    lease_ref=f"lease:rollback:{version_no}:{index_kind.lower()}",
                    fencing_token=1,
                    attempt_no=1,
                    write_batch={"chunk": f"chunk:rollback:{version_no}", "index_kind": index_kind},
                    visibility_receipt_ref=f"visible:rollback:{version_no}:{index_kind.lower()}",
                )
            repo.mark_ready(knowledge_version_id=version_id)
            repo.create_snapshot(
                snapshot_id=f"snapshot:rollback:{version_no}",
                tenant_id="tenant-a",
                knowledge_version_id=version_id,
                snapshot_payload={"version": version_id},
                serving_watermark_ref=f"watermark:rollback:{version_no}",
            )

        repo.cutover(
            cutover_id="cutover:rollback:1",
            tenant_id="tenant-a",
            knowledge_space_id="knowledge-space:wave-a",
            to_version_id="knowledge-version:rollback:1",
            expected_generation=1,
            decision_payload={"to": 1},
        )
        with pytest.raises(KnowledgeCutoverConflict, match="stale Knowledge cutover generation"):
            repo.cutover(
                cutover_id="cutover:rollback:stale",
                tenant_id="tenant-a",
                knowledge_space_id="knowledge-space:wave-a",
                to_version_id="knowledge-version:rollback:2",
                expected_generation=1,
                decision_payload={"to": "stale"},
            )
        repo.cutover(
            cutover_id="cutover:rollback:2",
            tenant_id="tenant-a",
            knowledge_space_id="knowledge-space:wave-a",
            to_version_id="knowledge-version:rollback:2",
            expected_generation=2,
            decision_payload={"to": 2},
            from_version_id="knowledge-version:rollback:1",
        )
        repo.cutover(
            cutover_id="cutover:rollback:restore-1",
            tenant_id="tenant-a",
            knowledge_space_id="knowledge-space:wave-a",
            to_version_id="knowledge-version:rollback:1",
            expected_generation=3,
            decision_payload={"rollback_to": 1},
            from_version_id="knowledge-version:rollback:2",
            rollback_of_cutover_id="cutover:rollback:2",
        )
        active = conn.execute(
            text(
                """
                SELECT knowledge_version_id
                FROM knowledge_domain_versions
                WHERE knowledge_space_id = 'knowledge-space:wave-a'
                  AND status = 'ACTIVE'
                """
            )
        ).scalar_one()
        assert active == "knowledge-version:rollback:1"

        repo.start_query_run(
            query_run_id="query-run:deleted-source",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_core_decision_ref="agent-core-decision:deleted-source",
            snapshot_id="snapshot:rollback:1",
            request_payload={"query": "policy"},
        )
        repo.start_retrieval_round(
            round_id="round:deleted-source:1",
            query_run_id="query-run:deleted-source",
            round_no=1,
            retriever_set={"bm25": True, "vector": True},
        )
        repo.start_query_run(
            query_run_id="query-run:other",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            agent_core_decision_ref="agent-core-decision:other",
            snapshot_id="snapshot:rollback:1",
            request_payload={"query": "other"},
        )
        repo.start_retrieval_round(
            round_id="round:other:1",
            query_run_id="query-run:other",
            round_no=1,
            retriever_set={"bm25": True},
        )
        with pytest.raises(KnowledgeEvidenceConflict, match="RetrievalRound mismatch"):
            repo.commit_evidence(
                evidence_id="evidence:deleted-source:bad-round",
                query_run_id="query-run:deleted-source",
                round_id="round:other:1",
                chunk_id="chunk:rollback:1",
                source_span_ref="source-span:1",
                evidence_payload={"quote": "Policy version 1."},
                authority_ref="authority:policy",
            )
        with pytest.raises(KnowledgeEvidenceConflict, match="snapshot version mismatch"):
            repo.commit_evidence(
                evidence_id="evidence:deleted-source:bad-version",
                query_run_id="query-run:deleted-source",
                round_id="round:deleted-source:1",
                chunk_id="chunk:rollback:2",
                source_span_ref="source-span:2",
                evidence_payload={"quote": "Policy version 2."},
                authority_ref="authority:policy",
            )
        repo.append_chunk(
            chunk_id="chunk:tenant-b",
            tenant_id="tenant-b",
            knowledge_version_id="knowledge-version:rollback:1",
            document_version_id="document-version:tenant-b",
            source_span_ref="source-span:tenant-b",
            chunk_payload={"text": "Cross tenant evidence."},
            acl_ref="acl:tenant-b",
            authority_ref="authority:policy",
        )
        with pytest.raises(KnowledgeEvidenceConflict, match="tenant ACL mismatch"):
            repo.commit_evidence(
                evidence_id="evidence:deleted-source:bad-tenant",
                query_run_id="query-run:deleted-source",
                round_id="round:deleted-source:1",
                chunk_id="chunk:tenant-b",
                source_span_ref="source-span:tenant-b",
                evidence_payload={"quote": "Cross tenant evidence."},
                authority_ref="authority:policy",
            )
        with pytest.raises(KnowledgeEvidenceConflict, match="authority mismatch"):
            repo.commit_evidence(
                evidence_id="evidence:deleted-source:bad-authority",
                query_run_id="query-run:deleted-source",
                round_id="round:deleted-source:1",
                chunk_id="chunk:rollback:1",
                source_span_ref="source-span:1",
                evidence_payload={"quote": "Policy version 1."},
                authority_ref="authority:other",
            )
        with pytest.raises(KnowledgeEvidenceConflict, match="SourceSpan mismatch"):
            repo.commit_evidence(
                evidence_id="evidence:deleted-source:bad-span",
                query_run_id="query-run:deleted-source",
                round_id="round:deleted-source:1",
                chunk_id="chunk:rollback:1",
                source_span_ref="source-span:other",
                evidence_payload={"quote": "Policy version 1."},
                authority_ref="authority:policy",
            )
        repo.commit_evidence(
            evidence_id="evidence:deleted-source:1",
            query_run_id="query-run:deleted-source",
            round_id="round:deleted-source:1",
            chunk_id="chunk:rollback:1",
            source_span_ref="source-span:1",
            evidence_payload={"quote": "Policy version 1."},
            authority_ref="authority:policy",
        )
        repo.commit_citation_lineage(
            citation_lineage_id="citation:deleted-source:1",
            evidence_id="evidence:deleted-source:1",
            document_version_id="document-version:1",
            source_span_ref="source-span:1",
            span_text="Policy version 1.",
            authorization_ref="authorization:source-span:1",
        )
        assert repo.strict_evidence_ids(query_run_id="query-run:deleted-source") == ("evidence:deleted-source:1",)

        repo.mark_source_deleted(
            tenant_id="tenant-a",
            knowledge_version_id="knowledge-version:rollback:1",
            document_version_id="document-version:1",
            source_span_ref="source-span:1",
            deletion_ref="delete:source-span:1",
        )
        assert repo.strict_evidence_ids(query_run_id="query-run:deleted-source") == ()
        tainted = conn.execute(
            text("SELECT deleted_or_tainted FROM knowledge_citation_lineage WHERE citation_lineage_id = 'citation:deleted-source:1'")
        ).scalar_one()
        assert tainted is True


def test_phase14_capability_blocks_unverified_skill_and_model_only_active_binding(engine) -> None:
    with engine.begin() as conn:
        repo = CapabilityRepository(conn)
        with pytest.raises(CapabilitySupplyChainConflict, match="unverified CapabilityVersion"):
            repo.publish_capability_version(
                CapabilityVersionInput(
                    capability_definition_id="capability:def:unverified",
                    capability_version_id="capability:version:unverified:v1",
                    tenant_id="tenant-a",
                    semantic_identity="knowledge.unverified.retrieve",
                    owner_module="Knowledge",
                    version_no=1,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    risk_profile_ref="risk:read-only",
                    source_ref="source:capability:unverified",
                    license_ref="license:mit",
                    dependency_refs=("dependency:knowledge-runtime",),
                    runtime_requirement_refs=("runtime:postgres",),
                    signature_ref="signature:capability:unverified",
                    verification_ref="verification:capability:unverified",
                    verified=False,
                )
            )
        with pytest.raises(CapabilitySupplyChainConflict, match="supply-chain verification"):
            repo.publish_capability_version(
                CapabilityVersionInput(
                    capability_definition_id="capability:def:incomplete",
                    capability_version_id="capability:version:incomplete:v1",
                    tenant_id="tenant-a",
                    semantic_identity="knowledge.incomplete.retrieve",
                    owner_module="Knowledge",
                    version_no=1,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                    risk_profile_ref="risk:read-only",
                    source_ref="source:capability:incomplete",
                    license_ref="license:mit",
                    dependency_refs=(),
                    runtime_requirement_refs=("runtime:postgres",),
                    signature_ref="signature:capability:incomplete",
                    verification_ref="verification:capability:incomplete",
                    verified=True,
                )
            )
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
                source_ref="source:capability:read:v1",
                license_ref="license:capability:read:mit",
                dependency_refs=("dependency:knowledge-runtime",),
                runtime_requirement_refs=("runtime:postgres", "runtime:tool-control-plane"),
                signature_ref="signature:capability:read:v1",
                verification_ref="verification:capability:read:v1",
                verified=True,
            )
        )
        verified_version = conn.execute(
            text(
                """
                SELECT source_ref, license_ref, signature_ref, verification_ref,
                       supply_chain_verified, char_length(supply_chain_hash) AS hash_len
                FROM capability_versions
                WHERE capability_version_id = 'capability:version:read:v1'
                """
            )
        ).mappings().one()
        assert dict(verified_version) == {
            "source_ref": "source:capability:read:v1",
            "license_ref": "license:capability:read:mit",
            "signature_ref": "signature:capability:read:v1",
            "verification_ref": "verification:capability:read:v1",
            "supply_chain_verified": True,
            "hash_len": 64,
        }
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
        repo.record_selection(
            selection_id="selection:deterministic:a",
            snapshot_id="cap-snapshot:1",
            requirement={"capability": "knowledge.standard.retrieve"},
            selected_binding_id=None,
            candidate_summary={
                "candidates": [
                    {"binding_id": "binding:b", "reason": "quota_exhausted"},
                    {"binding_id": "binding:a", "reason": "model_proposed"},
                ],
                "rejected": ["binding:b", "binding:a", "binding:a"],
            },
            rejection_reason_codes=["QUOTA_EXHAUSTED", "MODEL_PROPOSED_NOT_ACTIVE", "QUOTA_EXHAUSTED"],
        )
        repo.record_selection(
            selection_id="selection:deterministic:b",
            snapshot_id="cap-snapshot:1",
            requirement={"capability": "knowledge.standard.retrieve"},
            selected_binding_id=None,
            candidate_summary={
                "rejected": ["binding:a", "binding:b"],
                "candidates": [
                    {"reason": "model_proposed", "binding_id": "binding:a"},
                    {"reason": "quota_exhausted", "binding_id": "binding:b"},
                ],
            },
            rejection_reason_codes=["MODEL_PROPOSED_NOT_ACTIVE", "QUOTA_EXHAUSTED"],
        )

        binding_status = conn.execute(
            text("SELECT status FROM capability_provider_bindings WHERE binding_id = 'binding:model-only'")
        ).scalar_one()
        assert binding_status == "PROPOSED"
        deterministic_rows = conn.execute(
            text(
                """
                SELECT selection_id, candidate_summary_hash, selection_hash, rejection_reason_codes
                FROM capability_selection_results
                WHERE selection_id IN ('selection:deterministic:a', 'selection:deterministic:b')
                ORDER BY selection_id
                """
            )
        ).mappings().all()
        assert deterministic_rows[0]["candidate_summary_hash"] == deterministic_rows[1]["candidate_summary_hash"]
        assert deterministic_rows[0]["selection_hash"] == deterministic_rows[1]["selection_hash"]
        assert deterministic_rows[0]["rejection_reason_codes"] == [
            "MODEL_PROPOSED_NOT_ACTIVE",
            "QUOTA_EXHAUSTED",
        ]
        deterministic_payload = conn.execute(
            text(
                """
                SELECT payload
                FROM infra_outbox_events
                WHERE event_id = 'outbox:selection:deterministic:a'
                """
            )
        ).scalar_one()
        assert deterministic_payload["candidate_summary"]["deterministic_candidate_order"] == [
            "binding:a",
            "binding:b",
        ]
        assert deterministic_payload["candidate_summary"]["rejected"] == ["binding:a", "binding:b"]
        assert deterministic_payload["rejection_reason_codes"] == [
            "MODEL_PROPOSED_NOT_ACTIVE",
            "QUOTA_EXHAUSTED",
        ]
        dispatch = conn.execute(
            text(
                """
                SELECT aggregate_id, payload ->> 'consumer_module' AS consumer_module,
                       payload ->> 'snapshot_id' AS snapshot_id, ordering_sequence
                FROM infra_outbox_events
                WHERE topic = 'capability.selection.committed'
                  AND event_id = 'outbox:selection:1'
                """
            )
        ).mappings().one()
        assert dispatch["aggregate_id"] == "selection:1"
        assert dispatch["consumer_module"] == "Agent Core"
        assert dispatch["snapshot_id"] == "cap-snapshot:1"
        assert dispatch["ordering_sequence"] == 1
        consumed = CapabilityService.consume_selection_event(
            event_id="outbox:selection:1",
            worker_id="agent-core-selection-worker",
            engine=conn,
        )
        assert consumed.selection_id == "selection:1"
        assert consumed.snapshot_id == "cap-snapshot:1"
        assert consumed.inbox_first_seen is True
        assert consumed.outbox_status == "published"
        persisted = conn.execute(
            text(
                """
                SELECT i.status AS inbox_status,
                       o.status AS outbox_status
                FROM infra_inbox_messages i
                JOIN infra_outbox_events o ON o.event_id = i.message_id
                WHERE i.consumer = 'agent-core-capability-selection'
                  AND i.message_id = 'outbox:selection:1'
                """
            )
        ).mappings().one()
        assert dict(persisted) == {
            "inbox_status": "processed",
            "outbox_status": "published",
        }


def test_phase14_capability_installation_activation_uses_cas_and_revocation_filters_snapshot(engine) -> None:
    with engine.begin() as conn:
        repo = CapabilityRepository(conn)
        repo.publish_capability_version(
            CapabilityVersionInput(
                capability_definition_id="capability:def:active-read",
                capability_version_id="capability:version:active-read:v1",
                tenant_id="tenant-a",
                semantic_identity="knowledge.standard.retrieve",
                owner_module="Knowledge",
                version_no=1,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                risk_profile_ref="risk:read-only",
                source_ref="source:capability:active-read:v1",
                license_ref="license:capability:active-read:mit",
                dependency_refs=("dependency:knowledge-runtime",),
                runtime_requirement_refs=("runtime:postgres", "runtime:tool-control-plane"),
                signature_ref="signature:capability:active-read:v1",
                verification_ref="verification:capability:active-read:v1",
                verified=True,
            )
        )
        repo.propose_binding(
            binding_id="binding:active-read",
            capability_version_id="capability:version:active-read:v1",
            provider_instance_ref="provider:tool-runtime",
            tool_definition_ref="tool-definition:read:v1",
            mapping_payload={"input": "query"},
            proposal_source="CURATED",
        )
        with pytest.raises(CapabilitySupplyChainConflict, match="active verified binding"):
            repo.install_capability(
                installation_id="installation:unverified-active-read",
                tenant_id="tenant-a",
                workspace_id="workspace-a",
                capability_version_id="capability:version:active-read:v1",
                policy_ref="policy:install",
            )
        repo.record_conformance(
            conformance_id="conformance:active-read",
            binding_id="binding:active-read",
            report_payload={"passed": True},
            covers_input=True,
            covers_output=True,
            covers_idempotency=True,
            covers_reconciliation=True,
            covers_security=True,
        )
        for suffix in ("unhealthy", "quota", "capacity"):
            repo.propose_binding(
                binding_id=f"binding:{suffix}",
                capability_version_id="capability:version:active-read:v1",
                provider_instance_ref=f"provider:{suffix}",
                tool_definition_ref=f"tool-definition:{suffix}:v1",
                mapping_payload={"input": suffix},
                proposal_source="CURATED",
            )
            repo.record_conformance(
                conformance_id=f"conformance:{suffix}",
                binding_id=f"binding:{suffix}",
                report_payload={"passed": True, "suffix": suffix},
                covers_input=True,
                covers_output=True,
                covers_idempotency=True,
                covers_reconciliation=True,
                covers_security=True,
            )
        repo.install_capability(
            installation_id="installation:active-read",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            capability_version_id="capability:version:active-read:v1",
            policy_ref="policy:install",
        )
        repo.activate_installation(
            installation_id="installation:active-read",
            tenant_id="tenant-a",
            expected_generation=0,
            activation_ref="activation:active-read:1",
            policy_epoch_ref="policy-epoch:1",
            outbox_message_id="outbox:activation:active-read:1",
        )
        with pytest.raises(CapabilityActivationConflict, match="stale capability transition generation"):
            repo.activate_installation(
                installation_id="installation:active-read",
                tenant_id="tenant-a",
                expected_generation=0,
                activation_ref="activation:active-read:stale",
                policy_epoch_ref="policy-epoch:stale",
                outbox_message_id="outbox:activation:active-read:stale",
            )

        repo.create_availability_snapshot(
            snapshot_id="cap-snapshot:active",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            security_epoch_ref="epoch:1",
            source_generation=1,
            visible_candidates=("binding:active-read", "binding:unhealthy", "binding:quota", "binding:capacity"),
            ttl_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            runtime_signals={
                "binding:active-read": {"health": "healthy", "quota_remaining": 1, "capacity_remaining": 1},
                "binding:unhealthy": {"health": "degraded", "quota_remaining": 1, "capacity_remaining": 1},
                "binding:quota": {"health": "healthy", "quota_remaining": 0, "capacity_remaining": 1},
                "binding:capacity": {"health": "healthy", "quota_remaining": 1, "capacity_remaining": 0},
            },
        )
        active_hash = conn.execute(
            text(
                """
                SELECT snapshot_hash
                FROM capability_availability_snapshots
                WHERE snapshot_id = 'cap-snapshot:active'
                """
            )
        ).scalar_one()
        only_active_hash = canonical_sha256({"candidates": ["binding:active-read"]})
        assert active_hash == only_active_hash

        repo.revoke_installation(
            installation_id="installation:active-read",
            tenant_id="tenant-a",
            expected_generation=1,
            revocation_ref="revocation:active-read:2",
            policy_epoch_ref="policy-epoch:2",
            outbox_message_id="outbox:revocation:active-read:2",
        )
        repo.create_availability_snapshot(
            snapshot_id="cap-snapshot:revoked",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            security_epoch_ref="epoch:2",
            source_generation=2,
            visible_candidates=("binding:active-read",),
            ttl_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        revoked_hash = conn.execute(
            text(
                """
                SELECT snapshot_hash
                FROM capability_availability_snapshots
                WHERE snapshot_id = 'cap-snapshot:revoked'
                """
            )
        ).scalar_one()
        transition_rows = conn.execute(
            text(
                """
                SELECT status, policy_ref
                FROM capability_installations
                WHERE installation_id = 'installation:active-read'
                """
            )
        ).mappings().one()
        assert dict(transition_rows) == {
            "status": "REVOKED",
            "policy_ref": "policy-epoch:2",
        }
        assert active_hash != revoked_hash
        assert conn.execute(text("SELECT count(*) FROM capability_transition_events")).scalar_one() == 2
        outbox_rows = conn.execute(
            text(
                """
                SELECT event_id, aggregate_id, topic, payload ->> 'transition_id' AS transition_id,
                       payload ->> 'consumer_module' AS consumer_module, ordering_sequence, status
                FROM infra_outbox_events
                WHERE topic = 'capability.transition.committed'
                ORDER BY ordering_sequence
                """
            )
        ).mappings().all()
        assert [dict(row) for row in outbox_rows] == [
            {
                "event_id": "outbox:activation:active-read:1",
                "aggregate_id": "installation:active-read",
                "topic": "capability.transition.committed",
                "transition_id": "activation:active-read:1",
                "consumer_module": "Agent Core",
                "ordering_sequence": 1,
                "status": "pending",
            },
            {
                "event_id": "outbox:revocation:active-read:2",
                "aggregate_id": "installation:active-read",
                "topic": "capability.transition.committed",
                "transition_id": "revocation:active-read:2",
                "consumer_module": "Agent Core",
                "ordering_sequence": 2,
                "status": "pending",
            },
        ]

        infra_repo = InfrastructureRepository(conn)
        assert infra_repo.claim_outbox(
            worker_id="capability-crashed-worker",
            limit=1,
            topics=("capability.transition.committed",),
        ) == ["outbox:activation:active-read:1"]
        activation_record = infra_repo.load_claimed_outbox_event(
            event_id="outbox:activation:active-read:1",
            worker_id="capability-crashed-worker",
        )
        assert activation_record.idempotency_key == "activation:active-read:1"
        assert activation_record.ordering_key == "installation:active-read"
        assert activation_record.ordering_sequence == 1
        with pytest.raises(FencingRejectedError):
            infra_repo.complete_outbox(
                event_id="outbox:activation:active-read:1",
                worker_id="capability-wrong-worker",
            )
        failure = infra_repo.record_outbox_publish_failure(
            event_id="outbox:activation:active-read:1",
            worker_id="capability-crashed-worker",
            error_code="CrashBeforeAck",
            max_attempts=3,
            base_backoff_seconds=0,
            max_backoff_seconds=0,
        )
        assert (failure.status, failure.publish_attempts, failure.retry_count) == ("pending", 1, 1)
        conn.execute(
            text(
                """
                UPDATE infra_outbox_events
                SET next_attempt_at = now()
                WHERE event_id = 'outbox:activation:active-read:1'
                """
            )
        )
        assert (
            infra_repo.claim_outbox_event(
                event_id="outbox:revocation:active-read:2",
                worker_id="capability-out-of-order-worker",
            )
            is False
        )

        assert infra_repo.claim_outbox(
            worker_id="capability-recovery-worker",
            limit=1,
            topics=("capability.transition.committed",),
        ) == ["outbox:activation:active-read:1"]
        recovered_record = infra_repo.load_claimed_outbox_event(
            event_id="outbox:activation:active-read:1",
            worker_id="capability-recovery-worker",
        )
        assert recovered_record.payload_hash == activation_record.payload_hash
        infra_repo.complete_outbox(
            event_id="outbox:activation:active-read:1",
            worker_id="capability-recovery-worker",
        )
        first_receipt = infra_repo.record_inbox_receipt(
            consumer="agent-core-capability-transition",
            message_id=recovered_record.event_id,
            payload=recovered_record.payload,
            tenant_id="tenant-a",
            ordering_key=recovered_record.ordering_key,
            ordering_sequence=recovered_record.ordering_sequence,
        )
        duplicate_receipt = infra_repo.record_inbox_receipt(
            consumer="agent-core-capability-transition",
            message_id=recovered_record.event_id,
            payload=recovered_record.payload,
            tenant_id="tenant-a",
            ordering_key=recovered_record.ordering_key,
            ordering_sequence=recovered_record.ordering_sequence,
        )
        assert first_receipt.first_seen is True
        assert duplicate_receipt.first_seen is False
        assert duplicate_receipt.payload_hash == first_receipt.payload_hash

        consumed = CapabilityService.consume_transition_event(
            event_id="outbox:revocation:active-read:2",
            worker_id="capability-next-worker",
            engine=conn,
        )
        assert consumed.event_id == "outbox:revocation:active-read:2"
        assert consumed.transition_id == "revocation:active-read:2"
        assert consumed.aggregate_ref == "installation:active-read"
        assert consumed.committed_generation == 2
        assert consumed.inbox_first_seen is True
        assert consumed.outbox_status == "published"
        processed = conn.execute(
            text(
                """
                SELECT status
                FROM infra_inbox_messages
                WHERE consumer = 'agent-core-capability-transition'
                  AND message_id = 'outbox:revocation:active-read:2'
                """
            )
        ).scalar_one()
        published = conn.execute(
            text(
                """
                SELECT status
                FROM infra_outbox_events
                WHERE event_id = 'outbox:revocation:active-read:2'
                """
            )
        ).scalar_one()
        assert (processed, published) == ("processed", "published")


def test_phase09_product_runtime_dispatch_creates_agent_run_and_owner_receipt(engine) -> None:
    submission = ProductCommandSubmission(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        conversation_id="conversation:dispatch:1",
        principal_id="principal-a",
        active_agent_version_id="agent-version:wave-a",
        submission_id="submission:dispatch:1",
        client_request_id="client-request:dispatch:1",
        raw_intent_ref="raw-intent:dispatch:1",
        command_id="command:dispatch:1",
        command_kind="RUN",
        owner_module="Agent Core",
        runtime_request_ref="runtime-request:dispatch:1",
        payload={
            "goal": "dispatch product runtime request to Agent Core",
            "payload_hash": "d" * 64,
        },
        journal_sequence_no=1,
        outbox_message_id="outbox:dispatch:1",
    )

    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        receipt = repo.submit_command(submission)
        assert receipt.status == "ACCEPTED"

    consume_result = ProductService.consume_runtime_request_dispatch(
        event_id="outbox:dispatch:1",
        worker_id="product-dispatch-worker",
        engine=engine,
    )

    assert consume_result.inbox_first_seen is True
    assert consume_result.agent_run_id == "agent-run:runtime-request:dispatch:1"
    assert consume_result.agent_run_status == "CREATED"
    assert consume_result.owner_receipt_ref == "owner-receipt:outbox:dispatch:1:agent-run-created"
    assert consume_result.outbox_status == "published"

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM agent_domain_runs")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM agent_goal_versions")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM agent_task_contracts")).scalar_one() == 1
        assert conn.execute(
            text(
                """
                SELECT status, receipt_version, owner_receipt_ref
                FROM product_command_receipts
                WHERE command_id = 'command:dispatch:1'
                ORDER BY receipt_version
                """
            )
        ).mappings().all() == [
            {
                "status": "ACCEPTED",
                "receipt_version": 1,
                "owner_receipt_ref": None,
            },
            {
                "status": "ACCEPTED",
                "receipt_version": 2,
                "owner_receipt_ref": "owner-receipt:outbox:dispatch:1:agent-run-created",
            },
        ]
        inbox_row = conn.execute(
            text(
                """
                SELECT status, consumer, message_id
                FROM infra_inbox_messages
                WHERE message_id = 'outbox:dispatch:1'
                """
            )
        ).mappings().one()
        assert dict(inbox_row) == {
            "status": "processed",
            "consumer": "agent-core-product-runtime-dispatch",
            "message_id": "outbox:dispatch:1",
        }


def test_phase09_product_runtime_dispatch_owner_unavailable_retries_without_partial_owner_facts(
    engine, monkeypatch
) -> None:
    from zuno.api.services.product import command_service

    submission = ProductCommandSubmission(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        conversation_id="conversation:dispatch-owner-fail:1",
        principal_id="principal-a",
        active_agent_version_id="agent-version:wave-a",
        submission_id="submission:dispatch-owner-fail:1",
        client_request_id="client-request:dispatch-owner-fail:1",
        raw_intent_ref="raw-intent:dispatch-owner-fail:1",
        command_id="command:dispatch-owner-fail:1",
        command_kind="RUN",
        owner_module="Agent Core",
        runtime_request_ref="runtime-request:dispatch-owner-fail:1",
        payload={
            "goal": "dispatch product runtime request to unavailable Agent Core",
            "payload_hash": "e" * 64,
        },
        journal_sequence_no=1,
        outbox_message_id="outbox:dispatch-owner-fail:1",
    )

    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        ProductRepository(conn).submit_command(submission)

    original_record_agent_run = command_service.AgentDomainRepository.record_agent_run

    def unavailable_owner(self, run):
        raise RuntimeError("agent-core-owner-unavailable")

    monkeypatch.setattr(command_service.AgentDomainRepository, "record_agent_run", unavailable_owner)

    failed = ProductService.consume_runtime_request_dispatch(
        event_id="outbox:dispatch-owner-fail:1",
        worker_id="product-dispatch-worker",
        engine=engine,
    )

    assert failed.agent_run_id == "agent-run:runtime-request:dispatch-owner-fail:1"
    assert failed.agent_run_status == "owner_unavailable"
    assert failed.owner_receipt_ref is None
    assert failed.inbox_first_seen is False
    assert failed.outbox_status == "pending"

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM agent_domain_runs")).scalar_one() == 0
        assert conn.execute(text("SELECT count(*) FROM agent_goal_versions")).scalar_one() == 0
        assert conn.execute(text("SELECT count(*) FROM agent_task_contracts")).scalar_one() == 0
        assert conn.execute(
            text(
                """
                SELECT count(*)
                FROM product_command_receipts
                WHERE command_id = 'command:dispatch-owner-fail:1'
                  AND owner_receipt_ref IS NOT NULL
                """
            )
        ).scalar_one() == 0
        assert conn.execute(
            text(
                """
                SELECT count(*)
                FROM infra_inbox_messages
                WHERE consumer = 'agent-core-product-runtime-dispatch'
                  AND message_id = 'outbox:dispatch-owner-fail:1'
                """
            )
        ).scalar_one() == 0
        outbox = conn.execute(
            text(
                """
                SELECT status, retry_count, publish_attempts, last_error_code
                FROM infra_outbox_events
                WHERE event_id = 'outbox:dispatch-owner-fail:1'
                """
            )
        ).mappings().one()
        assert dict(outbox) == {
            "status": "pending",
            "retry_count": 1,
            "publish_attempts": 1,
            "last_error_code": "AgentCoreOwnerUnavailable:RuntimeError",
        }

    monkeypatch.setattr(command_service.AgentDomainRepository, "record_agent_run", original_record_agent_run)

    recovered = ProductService.consume_runtime_request_dispatch(
        event_id="outbox:dispatch-owner-fail:1",
        worker_id="product-dispatch-recovery-worker",
        engine=engine,
    )

    assert recovered.inbox_first_seen is True
    assert recovered.agent_run_status == "CREATED"
    assert recovered.owner_receipt_ref == "owner-receipt:outbox:dispatch-owner-fail:1:agent-run-created"
    assert recovered.outbox_status == "published"

    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM agent_domain_runs")).scalar_one() == 1
        assert conn.execute(
            text(
                """
                SELECT status
                FROM infra_inbox_messages
                WHERE consumer = 'agent-core-product-runtime-dispatch'
                  AND message_id = 'outbox:dispatch-owner-fail:1'
                """
            )
        ).scalar_one() == "processed"


def test_phase09_product_projection_rebuild_worker_consumes_owner_outbox(engine) -> None:
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        _seed_product_agent_version(conn)
        repo = ProductRepository(conn)
        receipt = repo.submit_command(
            _product_command("client:rebuild-worker", {"query": "renewal"}, "command:rebuild-worker")
        )
        projection = repo.record_projection_event(
            projection_event_id="projection:rebuild-worker:accepted",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            source_module="Product Surface",
            source_event_id=receipt.command_id,
            source_watermark=repo.next_projection_watermark(tenant_id="tenant-a", workspace_id="workspace-a"),
            projection_payload={"command_id": receipt.command_id},
            redaction_decision_ref="redaction:rebuild-worker:server",
        )
        cursor = repo.open_stream_cursor(
            cursor_id="cursor:rebuild-worker:1",
            tenant_id="tenant-a",
            principal_id="principal-a",
            projection_event_id=projection.projection_event_id,
            last_sequence_no=projection.source_watermark,
            effective_security_epoch_ref="security-epoch:wave-a",
            expires_at=now + timedelta(minutes=5),
            reauthorized_at=now,
        )
        InfrastructureRepository(conn).enqueue_outbox(
            event_id="outbox:projection-rebuild:1",
            tenant_id="tenant-a",
            aggregate_id="workspace-a",
            topic="product.projection.rebuild.requested",
            idempotency_key="projection-rebuild:workspace-a:1",
            ordering_key="workspace-a",
            payload={
                "contract_name": "ProductProjectionRebuildRequest",
                "producer_module": "Agent Core",
                "consumer_module": "Product Surface",
                "tenant_id": "tenant-a",
                "workspace_id": "workspace-a",
                "rebuild_id": "rebuild:owner:1",
                "reason": "agent_core_projection_gap",
            },
        )

    result = ProductService.consume_projection_rebuild_request(
        event_id="outbox:projection-rebuild:1",
        worker_id="product-projection-worker",
        engine=engine,
    )

    assert result.inbox_first_seen is True
    assert result.projection_status == "recorded"
    assert result.projection_event_id == "projection-rebuild:rebuild:owner:1"
    assert result.outbox_status == "published"
    after_rebuild = datetime.now(timezone.utc)

    with engine.connect() as conn:
        projection_rows = conn.execute(
            text(
                """
                SELECT projection_event_id, gap_detected, source_module
                FROM product_projection_events
                WHERE projection_event_id = 'projection-rebuild:rebuild:owner:1'
                """
            )
        ).mappings().one()
        assert dict(projection_rows) == {
            "projection_event_id": "projection-rebuild:rebuild:owner:1",
            "gap_detected": True,
            "source_module": "Product Projection Rebuild",
        }
        inbox_row = conn.execute(
            text(
                """
                SELECT status, consumer
                FROM infra_inbox_messages
                WHERE message_id = 'outbox:projection-rebuild:1'
                """
            )
        ).mappings().one()
        assert dict(inbox_row) == {
            "status": "processed",
            "consumer": "product-projection-rebuild-worker",
        }
        resync = ProductRepository(conn).list_projection_events(
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="principal-a",
            last_event_id=cursor.cursor_id,
            now=after_rebuild,
        )
        assert resync[0].projection_event_id == f"resync:{cursor.cursor_id}"
        assert resync[0].gap_detected is True
