from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_sha256
from zuno.platform.database.foundation import InfrastructureRepository


class ProductPersistenceConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ProductCommandSubmission:
    tenant_id: str
    workspace_id: str
    conversation_id: str
    principal_id: str
    active_agent_version_id: str
    submission_id: str
    client_request_id: str
    raw_intent_ref: str
    command_id: str
    command_kind: str
    owner_module: str
    runtime_request_ref: str
    payload: dict[str, Any]
    journal_sequence_no: int
    outbox_message_id: str
    message_id: str | None = None

    @property
    def request_hash(self) -> str:
        return canonical_sha256(self.payload)


@dataclass(frozen=True, slots=True)
class ProductCommandReceiptRef:
    command_id: str
    receipt_id: str
    status: str
    duplicate: bool = False


@dataclass(frozen=True, slots=True)
class ProductProjectionEventRef:
    projection_event_id: str
    source_watermark: int
    redaction_decision_ref: str
    gap_detected: bool = False
    duplicate: bool = False


@dataclass(frozen=True, slots=True)
class ProductActionTokenRef:
    action_token_id: str
    target_ref: str
    command_kind: str
    effective_security_epoch_ref: str
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ProductActionTokenStatusRef:
    action_token_id: str
    used_at: datetime | None
    revoked_at: datetime | None


@dataclass(frozen=True, slots=True)
class ProductActionCommandRef:
    action_token_id: str
    command_id: str
    receipt_id: str
    status: str
    target_ref: str
    used_at: datetime


@dataclass(frozen=True, slots=True)
class ProductStreamCursorRef:
    cursor_id: str
    projection_event_id: str
    last_sequence_no: int
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class ProductProjectionEventView:
    projection_event_id: str
    source_module: str
    source_event_id: str
    source_watermark: int
    redaction_decision_ref: str
    gap_detected: bool
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ProductAgentAssetRef:
    ref_id: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentCatalogEntryView:
    catalog_entry_id: str
    agent_definition_id: str
    latest_version_id: str
    publication_id: str
    visibility_scope: str
    status: str
    display_name: str
    description: str
    definition_status: str


@dataclass(frozen=True, slots=True)
class ProductAgentDefinitionView:
    agent_definition_id: str
    tenant_id: str
    workspace_id: str
    owner_principal_id: str
    display_name: str
    description: str
    status: str


@dataclass(frozen=True, slots=True)
class ProductAgentDraftView:
    draft_id: str
    agent_definition_id: str
    draft_hash: str
    draft_payload_json: dict[str, Any]
    status: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ProductAgentVersionView:
    agent_version_id: str
    agent_definition_id: str
    version_no: int
    config_hash: str
    configuration_json: dict[str, Any]
    primary_agent_core_profile_ref: str
    status: str
    created_at: datetime


class ProductUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "ProductRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return ProductRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class ProductRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create_agent_definition(
        self,
        *,
        agent_definition_id: str,
        tenant_id: str,
        workspace_id: str,
        owner_principal_id: str,
        display_name: str,
        status: str = "DRAFT",
    ) -> ProductAgentAssetRef:
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_definitions (
                    agent_definition_id, tenant_id, workspace_id, owner_principal_id,
                    display_name, status, aggregate_version
                )
                VALUES (
                    :agent_definition_id, :tenant_id, :workspace_id, :owner_principal_id,
                    :display_name, :status, 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "agent_definition_id": agent_definition_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "owner_principal_id": owner_principal_id,
                "display_name": display_name,
                "status": status,
            },
        )
        return ProductAgentAssetRef(agent_definition_id, status)

    def create_agent_draft(
        self,
        *,
        draft_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_definition_id: str,
        draft_payload: dict[str, Any],
        status: str = "DRAFT",
    ) -> ProductAgentAssetRef:
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_drafts (
                    draft_id, tenant_id, workspace_id, agent_definition_id,
                    draft_hash, draft_payload_json, status
                )
                VALUES (
                    :draft_id, :tenant_id, :workspace_id, :agent_definition_id,
                    :draft_hash, :draft_payload_json, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "draft_id": draft_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_definition_id": agent_definition_id,
                "draft_hash": canonical_sha256(draft_payload),
                "draft_payload_json": draft_payload,
                "status": status,
            },
        )
        return ProductAgentAssetRef(draft_id, status)

    def create_agent_version(
        self,
        *,
        agent_version_id: str,
        tenant_id: str,
        agent_definition_id: str,
        version_no: int,
        configuration_payload: dict[str, Any],
        primary_agent_core_profile_ref: str,
        status: str = "PUBLISHED",
    ) -> ProductAgentAssetRef:
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_versions (
                    agent_version_id, tenant_id, agent_definition_id, version_no,
                    config_hash, configuration_json, primary_agent_core_profile_ref, status
                )
                VALUES (
                    :agent_version_id, :tenant_id, :agent_definition_id, :version_no,
                    :config_hash, :configuration_json, :primary_agent_core_profile_ref, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "agent_version_id": agent_version_id,
                "tenant_id": tenant_id,
                "agent_definition_id": agent_definition_id,
                "version_no": version_no,
                "config_hash": canonical_sha256(configuration_payload),
                "configuration_json": configuration_payload,
                "primary_agent_core_profile_ref": primary_agent_core_profile_ref,
                "status": status,
            },
        )
        return ProductAgentAssetRef(agent_version_id, status)

    def ensure_runtime_agent_version(
        self,
        *,
        agent_version_id: str,
        tenant_id: str,
        workspace_id: str,
        owner_principal_id: str,
        display_name: str,
        primary_agent_core_profile_ref: str,
    ) -> ProductAgentAssetRef:
        agent_definition_id = f"agent-definition:{agent_version_id}"
        config_hash = canonical_sha256(
            {
                "agent_version_id": agent_version_id,
                "display_name": display_name,
                "primary_agent_core_profile_ref": primary_agent_core_profile_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_definitions (
                    agent_definition_id, tenant_id, workspace_id, owner_principal_id,
                    display_name, status, aggregate_version
                )
                VALUES (
                    :agent_definition_id, :tenant_id, :workspace_id, :owner_principal_id,
                    :display_name, 'ACTIVE', 1
                )
                ON CONFLICT (agent_definition_id) DO NOTHING
                """
            ),
            {
                "agent_definition_id": agent_definition_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "owner_principal_id": owner_principal_id,
                "display_name": display_name,
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_versions (
                    agent_version_id, tenant_id, agent_definition_id, version_no,
                    config_hash, configuration_json, primary_agent_core_profile_ref, status
                )
                VALUES (
                    :agent_version_id, :tenant_id, :agent_definition_id, 1,
                    :config_hash, :configuration_json, :primary_agent_core_profile_ref, 'PUBLISHED'
                )
                ON CONFLICT (agent_version_id) DO NOTHING
                """
            ),
            {
                "agent_version_id": agent_version_id,
                "tenant_id": tenant_id,
                "agent_definition_id": agent_definition_id,
                "config_hash": config_hash,
                "configuration_json": {
                    "agent_version_id": agent_version_id,
                    "display_name": display_name,
                    "primary_agent_core_profile_ref": primary_agent_core_profile_ref,
                },
                "primary_agent_core_profile_ref": primary_agent_core_profile_ref,
            },
        )
        return ProductAgentAssetRef(agent_version_id, "PUBLISHED")

    def publish_agent_version(
        self,
        *,
        publication_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_version_id: str,
        publication_scope: str,
        publication_payload: dict[str, Any],
    ) -> ProductAgentAssetRef:
        self._ensure_agent_version_status(agent_version_id=agent_version_id, status="PUBLISHED")
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_publications (
                    publication_id, tenant_id, workspace_id, agent_version_id,
                    publication_scope, publication_hash, status
                )
                VALUES (
                    :publication_id, :tenant_id, :workspace_id, :agent_version_id,
                    :publication_scope, :publication_hash, 'PUBLISHED'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "publication_id": publication_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_version_id": agent_version_id,
                "publication_scope": publication_scope,
                "publication_hash": canonical_sha256(publication_payload),
            },
        )
        return ProductAgentAssetRef(publication_id, "PUBLISHED")

    def install_agent_version(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_version_id: str,
        principal_id: str,
        installation_scope: str,
        status: str = "ACTIVE",
    ) -> ProductAgentAssetRef:
        self._ensure_agent_version_status(agent_version_id=agent_version_id, status="PUBLISHED")
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_installations (
                    installation_id, tenant_id, workspace_id, agent_version_id,
                    principal_id, installation_scope, status
                )
                VALUES (
                    :installation_id, :tenant_id, :workspace_id, :agent_version_id,
                    :principal_id, :installation_scope, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "installation_id": installation_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_version_id": agent_version_id,
                "principal_id": principal_id,
                "installation_scope": installation_scope,
                "status": status,
            },
        )
        return ProductAgentAssetRef(installation_id, status)

    def revoke_agent_installation(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
    ) -> ProductAgentAssetRef:
        result = self.connection.execute(
            text(
                """
                UPDATE product_agent_installations
                SET status = 'REVOKED'
                WHERE installation_id = :installation_id
                  AND tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND principal_id = :principal_id
                """
            ),
            {
                "installation_id": installation_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "principal_id": principal_id,
            },
        )
        if result.rowcount != 1:
            raise ProductPersistenceConflict("Product AgentInstallation revoke target not found")
        return ProductAgentAssetRef(installation_id, "REVOKED")

    def revoke_agent_publication(
        self,
        *,
        publication_id: str,
        tenant_id: str,
        workspace_id: str,
    ) -> ProductAgentAssetRef:
        row = self.connection.execute(
            text(
                """
                UPDATE product_agent_publications
                SET status = 'REVOKED'
                WHERE publication_id = :publication_id
                  AND tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                RETURNING agent_version_id
                """
            ),
            {
                "publication_id": publication_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
            },
        ).mappings().first()
        if row is None:
            raise ProductPersistenceConflict("Product AgentPublication revoke target not found")
        self.connection.execute(
            text(
                """
                UPDATE product_agent_catalog_entries
                SET status = 'REVOKED'
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND latest_version_id = :agent_version_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_version_id": row["agent_version_id"],
            },
        )
        return ProductAgentAssetRef(publication_id, "REVOKED")

    def upsert_catalog_entry(
        self,
        *,
        catalog_entry_id: str,
        tenant_id: str,
        workspace_id: str,
        agent_definition_id: str,
        latest_version_id: str,
        visibility_scope: str,
        status: str = "VISIBLE",
    ) -> ProductAgentAssetRef:
        self._ensure_agent_version_status(agent_version_id=latest_version_id, status="PUBLISHED")
        self.connection.execute(
            text(
                """
                INSERT INTO product_agent_catalog_entries (
                    catalog_entry_id, tenant_id, workspace_id, agent_definition_id,
                    latest_version_id, visibility_scope, status
                )
                VALUES (
                    :catalog_entry_id, :tenant_id, :workspace_id, :agent_definition_id,
                    :latest_version_id, :visibility_scope, :status
                )
                ON CONFLICT (tenant_id, workspace_id, agent_definition_id)
                DO UPDATE SET
                    latest_version_id = EXCLUDED.latest_version_id,
                    visibility_scope = EXCLUDED.visibility_scope,
                    status = EXCLUDED.status
                """
            ),
            {
                "catalog_entry_id": catalog_entry_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_definition_id": agent_definition_id,
                "latest_version_id": latest_version_id,
                "visibility_scope": visibility_scope,
                "status": status,
            },
        )
        return ProductAgentAssetRef(catalog_entry_id, status)

    def list_catalog_entries(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
    ) -> tuple[ProductAgentCatalogEntryView, ...]:
        rows = self.connection.execute(
            text(
                """
                SELECT catalog.catalog_entry_id,
                       catalog.agent_definition_id,
                       catalog.latest_version_id,
                       coalesce(publication.publication_id, '') AS publication_id,
                       catalog.visibility_scope,
                       catalog.status,
                       definition.display_name,
                       coalesce(definition.description, '') AS description,
                       definition.status AS definition_status
                FROM product_agent_catalog_entries catalog
                JOIN product_agent_definitions definition
                  ON definition.tenant_id = catalog.tenant_id
                 AND definition.workspace_id = catalog.workspace_id
                 AND definition.agent_definition_id = catalog.agent_definition_id
                LEFT JOIN product_agent_publications publication
                  ON publication.tenant_id = catalog.tenant_id
                 AND publication.workspace_id = catalog.workspace_id
                 AND publication.agent_version_id = catalog.latest_version_id
                 AND publication.status = 'PUBLISHED'
                WHERE catalog.tenant_id = :tenant_id
                  AND catalog.workspace_id = :workspace_id
                  AND catalog.status = 'VISIBLE'
                ORDER BY catalog.catalog_entry_id
                """
            ),
            {"tenant_id": tenant_id, "workspace_id": workspace_id},
        ).mappings().all()
        return tuple(
            ProductAgentCatalogEntryView(
                catalog_entry_id=str(row["catalog_entry_id"]),
                agent_definition_id=str(row["agent_definition_id"]),
                latest_version_id=str(row["latest_version_id"]),
                publication_id=str(row["publication_id"]),
                visibility_scope=str(row["visibility_scope"]),
                status=str(row["status"]),
                display_name=str(row["display_name"]),
                description=str(row["description"]),
                definition_status=str(row["definition_status"]),
            )
            for row in rows
        )

    def get_agent_definition(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        agent_definition_id: str,
    ) -> ProductAgentDefinitionView | None:
        row = self.connection.execute(
            text(
                """
                SELECT agent_definition_id, tenant_id, workspace_id, owner_principal_id,
                       display_name, coalesce(description, '') AS description, status
                FROM product_agent_definitions
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND agent_definition_id = :agent_definition_id
                LIMIT 1
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_definition_id": agent_definition_id,
            },
        ).mappings().first()
        if row is None:
            return None
        return ProductAgentDefinitionView(
            agent_definition_id=str(row["agent_definition_id"]),
            tenant_id=str(row["tenant_id"]),
            workspace_id=str(row["workspace_id"]),
            owner_principal_id=str(row["owner_principal_id"]),
            display_name=str(row["display_name"]),
            description=str(row["description"]),
            status=str(row["status"]),
        )

    def get_latest_agent_draft(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        agent_definition_id: str,
    ) -> ProductAgentDraftView | None:
        row = self.connection.execute(
            text(
                """
                SELECT draft_id, agent_definition_id, draft_hash,
                       coalesce(draft_payload_json, '{}'::json) AS draft_payload_json,
                       status, created_at
                FROM product_agent_drafts
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND agent_definition_id = :agent_definition_id
                ORDER BY created_at DESC, draft_id DESC
                LIMIT 1
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "agent_definition_id": agent_definition_id,
            },
        ).mappings().first()
        if row is None:
            return None
        return ProductAgentDraftView(
            draft_id=str(row["draft_id"]),
            agent_definition_id=str(row["agent_definition_id"]),
            draft_hash=str(row["draft_hash"]),
            draft_payload_json=dict(row["draft_payload_json"] or {}),
            status=str(row["status"]),
            created_at=row["created_at"],
        )

    def get_latest_agent_version(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        agent_definition_id: str,
    ) -> ProductAgentVersionView | None:
        row = self.connection.execute(
            text(
                """
                SELECT agent_version_id, agent_definition_id, version_no, config_hash,
                       coalesce(configuration_json, '{}'::json) AS configuration_json,
                       primary_agent_core_profile_ref, status, created_at
                FROM product_agent_versions
                WHERE tenant_id = :tenant_id
                  AND agent_definition_id = :agent_definition_id
                ORDER BY version_no DESC, created_at DESC, agent_version_id DESC
                LIMIT 1
                """
            ),
            {
                "tenant_id": tenant_id,
                "agent_definition_id": agent_definition_id,
            },
        ).mappings().first()
        if row is None:
            return None
        _ = workspace_id
        return ProductAgentVersionView(
            agent_version_id=str(row["agent_version_id"]),
            agent_definition_id=str(row["agent_definition_id"]),
            version_no=int(row["version_no"]),
            config_hash=str(row["config_hash"]),
            configuration_json=dict(row["configuration_json"] or {}),
            primary_agent_core_profile_ref=str(row["primary_agent_core_profile_ref"]),
            status=str(row["status"]),
            created_at=row["created_at"],
        )

    def submit_command(self, command: ProductCommandSubmission) -> ProductCommandReceiptRef:
        self._ensure_conversation(command)
        existing = self.connection.execute(
            text(
                """
                SELECT s.submission_id, s.request_hash, c.command_id
                FROM product_submissions s
                JOIN product_commands c ON c.submission_id = s.submission_id
                WHERE s.tenant_id = :tenant_id
                  AND s.workspace_id = :workspace_id
                  AND s.client_request_id = :client_request_id
                ORDER BY c.journal_sequence_no
                LIMIT 1
                """
            ),
            {
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "client_request_id": command.client_request_id,
            },
        ).mappings().first()
        if existing is not None:
            if existing["request_hash"] != command.request_hash:
                raise ProductPersistenceConflict("same client_request_id with different request_hash")
            receipt = self._append_receipt(
                str(existing["command_id"]),
                command.tenant_id,
                "DUPLICATE",
                {"duplicate_of_submission": existing["submission_id"]},
            )
            return ProductCommandReceiptRef(str(existing["command_id"]), receipt, "DUPLICATE", duplicate=True)

        message_id = command.message_id or f"message:{command.submission_id}"
        self.connection.execute(
            text(
                """
                INSERT INTO product_submissions (
                    submission_id, tenant_id, workspace_id, conversation_id,
                    client_request_id, request_hash, raw_intent_ref, status
                )
                VALUES (
                    :submission_id, :tenant_id, :workspace_id, :conversation_id,
                    :client_request_id, :request_hash, :raw_intent_ref, 'ACCEPTED'
                )
                """
            ),
            {
                "submission_id": command.submission_id,
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "conversation_id": command.conversation_id,
                "client_request_id": command.client_request_id,
                "request_hash": command.request_hash,
                "raw_intent_ref": command.raw_intent_ref,
            },
        )
        message_sequence_no = int(
            self.connection.execute(
                text(
                    """
                    SELECT coalesce(max(sequence_no), 0) + 1
                    FROM product_messages
                    WHERE conversation_id = :conversation_id
                    """
                ),
                {"conversation_id": command.conversation_id},
            ).scalar_one()
        )
        self.connection.execute(
            text(
                """
                INSERT INTO product_messages (
                    message_id, tenant_id, workspace_id, conversation_id,
                    submission_id, principal_id, message_role, message_hash,
                    sequence_no, publication_ref
                )
                VALUES (
                    :message_id, :tenant_id, :workspace_id, :conversation_id,
                    :submission_id, :principal_id, 'USER', :message_hash,
                    :sequence_no, null
                )
                """
            ),
            {
                "message_id": message_id,
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "conversation_id": command.conversation_id,
                "submission_id": command.submission_id,
                "principal_id": command.principal_id,
                "message_hash": command.request_hash,
                "sequence_no": message_sequence_no,
            },
        )
        journal_sequence_no = int(
            self.connection.execute(
                text(
                    """
                    SELECT coalesce(max(journal_sequence_no), 0) + 1
                    FROM product_commands
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                    """
                ),
                {
                    "tenant_id": command.tenant_id,
                    "workspace_id": command.workspace_id,
                },
            ).scalar_one()
        )
        self.connection.execute(
            text(
                """
                INSERT INTO product_commands (
                    command_id, tenant_id, workspace_id, submission_id, command_kind,
                    owner_module, runtime_request_ref, payload_hash, journal_sequence_no,
                    outbox_message_id, status
                )
                VALUES (
                    :command_id, :tenant_id, :workspace_id, :submission_id, :command_kind,
                    :owner_module, :runtime_request_ref, :payload_hash, :journal_sequence_no,
                    :outbox_message_id, 'DISPATCH_COMMITTED'
                )
                """
            ),
            {
                "command_id": command.command_id,
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "submission_id": command.submission_id,
                "command_kind": command.command_kind,
                "owner_module": command.owner_module,
                "runtime_request_ref": command.runtime_request_ref,
                "payload_hash": command.request_hash,
                "journal_sequence_no": journal_sequence_no,
                "outbox_message_id": command.outbox_message_id,
            },
        )
        receipt = self._append_receipt(
            command.command_id,
            command.tenant_id,
            "ACCEPTED",
            {"runtime_request_ref": command.runtime_request_ref},
        )
        InfrastructureRepository(self.connection).enqueue_outbox(
            event_id=command.outbox_message_id,
            tenant_id=command.tenant_id,
            aggregate_id=command.command_id,
            topic="product.runtime_request.dispatch",
            idempotency_key=command.client_request_id,
            ordering_key=command.conversation_id,
            payload={
                "contract_name": "RuntimeRequest",
                "producer_module": "Product Surface",
                "consumer_module": "Agent Core",
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "conversation_id": command.conversation_id,
                "submission_id": command.submission_id,
                "message_id": message_id,
                "command_id": command.command_id,
                "runtime_request_ref": command.runtime_request_ref,
                "active_agent_version_id": command.active_agent_version_id,
                "principal_id": command.principal_id,
                "payload_hash": command.request_hash,
            },
        )
        return ProductCommandReceiptRef(command.command_id, receipt, "ACCEPTED")

    def append_owner_receipt(
        self,
        *,
        tenant_id: str,
        command_id: str,
        status: str,
        owner_receipt_ref: str,
        payload: dict[str, Any],
    ) -> str:
        if payload.get("domain_success_ref"):
            raise ProductPersistenceConflict("Product receipt cannot claim owner domain success")
        if self._has_owner_receipt(command_id=command_id, tenant_id=tenant_id):
            payload = {
                "late_owner_receipt": True,
                "late_reason": "owner_receipt_after_prior_owner_receipt",
                "reported_owner_status": status,
                "reported_owner_receipt_ref": owner_receipt_ref,
                "owner_payload": payload,
            }
            status = "LATE_OWNER_RECEIPT"
        return self._append_receipt(
            command_id,
            tenant_id,
            status,
            payload,
            owner_receipt_ref=owner_receipt_ref,
        )

    def record_projection_event(
        self,
        *,
        projection_event_id: str,
        tenant_id: str,
        workspace_id: str,
        source_module: str,
        source_event_id: str,
        source_watermark: int,
        projection_payload: dict[str, Any],
        redaction_decision_ref: str,
        gap_detected: bool = False,
    ) -> ProductProjectionEventRef:
        existing = self.connection.execute(
            text(
                """
                SELECT projection_event_id, source_watermark, redaction_decision_ref, gap_detected
                FROM product_projection_events
                WHERE tenant_id = :tenant_id
                  AND source_module = :source_module
                  AND source_event_id = :source_event_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "source_module": source_module,
                "source_event_id": source_event_id,
            },
        ).mappings().first()
        if existing is not None:
            return ProductProjectionEventRef(
                projection_event_id=str(existing["projection_event_id"]),
                source_watermark=int(existing["source_watermark"]),
                redaction_decision_ref=str(existing["redaction_decision_ref"]),
                gap_detected=bool(existing["gap_detected"]),
                duplicate=True,
            )
        self.connection.execute(
            text(
                """
                INSERT INTO product_projection_events (
                    projection_event_id, tenant_id, workspace_id, source_module,
                    source_event_id, source_watermark, projection_hash,
                    redaction_decision_ref, gap_detected
                )
                VALUES (
                    :projection_event_id, :tenant_id, :workspace_id, :source_module,
                    :source_event_id, :source_watermark, :projection_hash,
                    :redaction_decision_ref, :gap_detected
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "projection_event_id": projection_event_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "source_module": source_module,
                "source_event_id": source_event_id,
                "source_watermark": source_watermark,
                "projection_hash": canonical_sha256(projection_payload),
                "redaction_decision_ref": redaction_decision_ref,
                "gap_detected": gap_detected,
            },
        )
        return ProductProjectionEventRef(
            projection_event_id=projection_event_id,
            source_watermark=source_watermark,
            redaction_decision_ref=redaction_decision_ref,
            gap_detected=gap_detected,
        )

    def record_projection_rebuild(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        rebuild_id: str,
        reason: str,
        now: datetime | None = None,
    ) -> ProductProjectionEventRef:
        now = now or datetime.now(timezone.utc)
        self.connection.execute(
            text(
                """
                UPDATE product_stream_cursors cursor
                SET expires_at = :now
                WHERE cursor.tenant_id = :tenant_id
                  AND EXISTS (
                      SELECT 1
                      FROM product_projection_events event
                      WHERE event.projection_event_id = cursor.projection_event_id
                        AND event.workspace_id = :workspace_id
                  )
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "now": now,
            },
        )
        return self.record_projection_event(
            projection_event_id=f"projection-rebuild:{rebuild_id}",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            source_module="Product Projection Rebuild",
            source_event_id=rebuild_id,
            source_watermark=self.next_projection_watermark(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
            ),
            projection_payload={
                "rebuild_id": rebuild_id,
                "reason": reason,
                "workspace_id": workspace_id,
            },
            redaction_decision_ref=f"redaction:{rebuild_id}:rebuild",
            gap_detected=True,
        )

    def issue_action_token(
        self,
        *,
        action_token_id: str,
        tenant_id: str,
        principal_id: str,
        target_ref: str,
        command_kind: str,
        effective_security_epoch_ref: str,
        nonce: str,
        expires_at: datetime,
    ) -> ProductActionTokenRef:
        existing = self.connection.execute(
            text(
                """
                SELECT action_token_id, target_ref, command_kind, effective_security_epoch_ref, expires_at
                FROM product_action_tokens
                WHERE tenant_id = :tenant_id
                  AND nonce = :nonce
                """
            ),
            {"tenant_id": tenant_id, "nonce": nonce},
        ).mappings().first()
        if existing is not None:
            return ProductActionTokenRef(
                action_token_id=str(existing["action_token_id"]),
                target_ref=str(existing["target_ref"]),
                command_kind=str(existing["command_kind"]),
                effective_security_epoch_ref=str(existing["effective_security_epoch_ref"]),
                expires_at=existing["expires_at"],
            )
        token_hash = canonical_sha256(
            {
                "principal_id": principal_id,
                "target_ref": target_ref,
                "command_kind": command_kind,
                "effective_security_epoch_ref": effective_security_epoch_ref,
                "nonce": nonce,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO product_action_tokens (
                    action_token_id, tenant_id, principal_id, target_ref, command_kind,
                    effective_security_epoch_ref, token_hash, nonce, expires_at
                )
                VALUES (
                    :action_token_id, :tenant_id, :principal_id, :target_ref, :command_kind,
                    :effective_security_epoch_ref, :token_hash, :nonce, :expires_at
                )
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "target_ref": target_ref,
                "command_kind": command_kind,
                "effective_security_epoch_ref": effective_security_epoch_ref,
                "token_hash": token_hash,
                "nonce": nonce,
                "expires_at": expires_at,
            },
        )
        return ProductActionTokenRef(
            action_token_id=action_token_id,
            target_ref=target_ref,
            command_kind=command_kind,
            effective_security_epoch_ref=effective_security_epoch_ref,
            expires_at=expires_at,
        )

    def consume_action_token(
        self,
        *,
        action_token_id: str,
        tenant_id: str,
        principal_id: str,
        now: datetime | None = None,
    ) -> ProductActionTokenStatusRef:
        now = now or datetime.now(timezone.utc)
        row = self.connection.execute(
            text(
                """
                SELECT action_token_id, expires_at, used_at, revoked_at
                FROM product_action_tokens
                WHERE action_token_id = :action_token_id
                  AND tenant_id = :tenant_id
                  AND principal_id = :principal_id
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
            },
        ).mappings().first()
        if row is None:
            raise ProductPersistenceConflict("unknown product action token")
        if row["revoked_at"] is not None:
            raise ProductPersistenceConflict("revoked action token cannot be consumed")
        if row["used_at"] is not None:
            raise ProductPersistenceConflict("action token replay detected")
        if row["expires_at"] <= now:
            raise ProductPersistenceConflict("expired action token cannot be consumed")
        self.connection.execute(
            text(
                """
                UPDATE product_action_tokens
                SET used_at = :used_at
                WHERE action_token_id = :action_token_id
                  AND tenant_id = :tenant_id
                  AND principal_id = :principal_id
                  AND used_at IS NULL
                  AND revoked_at IS NULL
                  AND expires_at > :used_at
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "used_at": now,
            },
        )
        return ProductActionTokenStatusRef(
            action_token_id=action_token_id,
            used_at=now,
            revoked_at=row["revoked_at"],
        )

    def consume_action_token_as_command(
        self,
        *,
        action_token_id: str,
        tenant_id: str,
        principal_id: str,
        client_request_id: str,
        raw_intent_ref: str,
        payload: dict[str, Any] | None = None,
        now: datetime | None = None,
    ) -> ProductActionCommandRef:
        token = self.connection.execute(
            text(
                """
                SELECT target_ref, command_kind
                FROM product_action_tokens
                WHERE action_token_id = :action_token_id
                  AND tenant_id = :tenant_id
                  AND principal_id = :principal_id
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
            },
        ).mappings().first()
        if token is None:
            raise ProductPersistenceConflict("unknown product action token")
        target_ref = str(token["target_ref"])
        source = self.connection.execute(
            text(
                """
                SELECT c.workspace_id, s.conversation_id, t.active_agent_version_id
                FROM product_commands c
                JOIN product_submissions s ON s.submission_id = c.submission_id
                JOIN product_conversation_threads t ON t.conversation_id = s.conversation_id
                WHERE c.tenant_id = :tenant_id
                  AND c.runtime_request_ref = :target_ref
                ORDER BY c.journal_sequence_no
                LIMIT 1
                """
            ),
            {"tenant_id": tenant_id, "target_ref": target_ref},
        ).mappings().first()
        if source is None:
            raise ProductPersistenceConflict("action token target command unavailable")
        consumed = self.consume_action_token(
            action_token_id=action_token_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            now=now,
        )
        if consumed.used_at is None:
            raise ProductPersistenceConflict("product action token consume did not persist used_at")
        command_id = f"command:{client_request_id}"
        receipt = self.submit_command(
            ProductCommandSubmission(
                tenant_id=tenant_id,
                workspace_id=str(source["workspace_id"]),
                conversation_id=str(source["conversation_id"]),
                principal_id=principal_id,
                active_agent_version_id=str(source["active_agent_version_id"]),
                submission_id=f"submission:{client_request_id}",
                client_request_id=client_request_id,
                raw_intent_ref=raw_intent_ref,
                command_id=command_id,
                command_kind=str(token["command_kind"]),
                owner_module="Agent Core",
                runtime_request_ref=target_ref,
                payload={
                    "action_token_id": action_token_id,
                    "target_ref": target_ref,
                    **dict(payload or {}),
                },
                journal_sequence_no=1,
                outbox_message_id=f"outbox:{command_id}",
            )
        )
        return ProductActionCommandRef(
            action_token_id=action_token_id,
            command_id=receipt.command_id,
            receipt_id=receipt.receipt_id,
            status=receipt.status,
            target_ref=target_ref,
            used_at=consumed.used_at,
        )

    def revoke_action_token(
        self,
        *,
        action_token_id: str,
        tenant_id: str,
        principal_id: str,
        now: datetime | None = None,
    ) -> ProductActionTokenStatusRef:
        now = now or datetime.now(timezone.utc)
        row = self.connection.execute(
            text(
                """
                SELECT action_token_id, used_at, revoked_at
                FROM product_action_tokens
                WHERE action_token_id = :action_token_id
                  AND tenant_id = :tenant_id
                  AND principal_id = :principal_id
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
            },
        ).mappings().first()
        if row is None:
            raise ProductPersistenceConflict("unknown product action token")
        if row["used_at"] is not None:
            raise ProductPersistenceConflict("consumed action token cannot be revoked")
        if row["revoked_at"] is not None:
            raise ProductPersistenceConflict("action token already revoked")
        self.connection.execute(
            text(
                """
                UPDATE product_action_tokens
                SET revoked_at = :revoked_at
                WHERE action_token_id = :action_token_id
                  AND tenant_id = :tenant_id
                  AND principal_id = :principal_id
                  AND used_at IS NULL
                  AND revoked_at IS NULL
                """
            ),
            {
                "action_token_id": action_token_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "revoked_at": now,
            },
        )
        return ProductActionTokenStatusRef(
            action_token_id=action_token_id,
            used_at=row["used_at"],
            revoked_at=now,
        )

    def open_stream_cursor(
        self,
        *,
        cursor_id: str,
        tenant_id: str,
        principal_id: str,
        projection_event_id: str,
        last_sequence_no: int,
        effective_security_epoch_ref: str,
        expires_at: datetime,
        reauthorized_at: datetime | None = None,
    ) -> ProductStreamCursorRef:
        reauthorized_at = reauthorized_at or datetime.now(timezone.utc)
        self.connection.execute(
            text(
                """
                INSERT INTO product_stream_cursors (
                    cursor_id, tenant_id, principal_id, projection_event_id,
                    last_sequence_no, effective_security_epoch_ref, expires_at, reauthorized_at
                )
                VALUES (
                    :cursor_id, :tenant_id, :principal_id, :projection_event_id,
                    :last_sequence_no, :effective_security_epoch_ref, :expires_at, :reauthorized_at
                )
                ON CONFLICT (cursor_id) DO UPDATE SET
                    projection_event_id = EXCLUDED.projection_event_id,
                    last_sequence_no = EXCLUDED.last_sequence_no,
                    effective_security_epoch_ref = EXCLUDED.effective_security_epoch_ref,
                    expires_at = EXCLUDED.expires_at,
                    reauthorized_at = EXCLUDED.reauthorized_at
                """
            ),
            {
                "cursor_id": cursor_id,
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "projection_event_id": projection_event_id,
                "last_sequence_no": last_sequence_no,
                "effective_security_epoch_ref": effective_security_epoch_ref,
                "expires_at": expires_at,
                "reauthorized_at": reauthorized_at,
            },
        )
        return ProductStreamCursorRef(
            cursor_id=cursor_id,
            projection_event_id=projection_event_id,
            last_sequence_no=last_sequence_no,
            expires_at=expires_at,
        )

    def list_projection_events(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        last_event_id: str | None = None,
        limit: int = 100,
        now: datetime | None = None,
    ) -> tuple[ProductProjectionEventView, ...]:
        now = now or datetime.now(timezone.utc)
        last_sequence_no = 0
        if last_event_id:
            cursor = self.connection.execute(
                text(
                    """
                    SELECT last_sequence_no, expires_at
                    FROM product_stream_cursors
                    WHERE cursor_id = :last_event_id
                      AND tenant_id = :tenant_id
                      AND principal_id = :principal_id
                    """
                ),
                {
                    "last_event_id": last_event_id,
                    "tenant_id": tenant_id,
                    "principal_id": principal_id,
                },
            ).mappings().first()
            if cursor is not None:
                if cursor["expires_at"] <= now:
                    return (
                        ProductProjectionEventView(
                            projection_event_id=f"resync:{last_event_id}",
                            source_module="Product Surface",
                            source_event_id=last_event_id,
                            source_watermark=int(cursor["last_sequence_no"]),
                            redaction_decision_ref="redaction:resync-required",
                            gap_detected=True,
                            created_at=now,
                        ),
                    )
                last_sequence_no = int(cursor["last_sequence_no"])
            else:
                event = self.connection.execute(
                    text(
                        """
                        SELECT source_watermark
                        FROM product_projection_events
                        WHERE projection_event_id = :last_event_id
                          AND tenant_id = :tenant_id
                          AND workspace_id = :workspace_id
                        """
                    ),
                    {
                        "last_event_id": last_event_id,
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                    },
                ).mappings().first()
                if event is None:
                    return (
                        ProductProjectionEventView(
                            projection_event_id=f"resync:{last_event_id}",
                            source_module="Product Surface",
                            source_event_id=last_event_id,
                            source_watermark=0,
                            redaction_decision_ref="redaction:unknown-cursor",
                            gap_detected=True,
                            created_at=now,
                        ),
                    )
                last_sequence_no = int(event["source_watermark"])

        rows = self.connection.execute(
            text(
                """
                SELECT projection_event_id, source_module, source_event_id, source_watermark,
                       redaction_decision_ref, gap_detected, created_at
                FROM product_projection_events
                WHERE tenant_id = :tenant_id
                  AND workspace_id = :workspace_id
                  AND source_watermark > :last_sequence_no
                ORDER BY source_watermark, projection_event_id
                LIMIT :limit
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "last_sequence_no": last_sequence_no,
                "limit": limit,
            },
        ).mappings().all()
        return tuple(
            ProductProjectionEventView(
                projection_event_id=str(row["projection_event_id"]),
                source_module=str(row["source_module"]),
                source_event_id=str(row["source_event_id"]),
                source_watermark=int(row["source_watermark"]),
                redaction_decision_ref=str(row["redaction_decision_ref"]),
                gap_detected=bool(row["gap_detected"]),
                created_at=row["created_at"],
            )
            for row in rows
        )

    def next_projection_watermark(self, *, tenant_id: str, workspace_id: str) -> int:
        return int(
            self.connection.execute(
                text(
                    """
                    SELECT coalesce(max(source_watermark), 0) + 1
                    FROM product_projection_events
                    WHERE tenant_id = :tenant_id
                      AND workspace_id = :workspace_id
                    """
                ),
                {"tenant_id": tenant_id, "workspace_id": workspace_id},
            ).scalar_one()
        )

    def _ensure_conversation(self, command: ProductCommandSubmission) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO product_conversation_threads (
                    conversation_id, tenant_id, workspace_id, principal_id,
                    active_agent_version_id, status
                )
                VALUES (
                    :conversation_id, :tenant_id, :workspace_id, :principal_id,
                    :active_agent_version_id, 'OPEN'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "conversation_id": command.conversation_id,
                "tenant_id": command.tenant_id,
                "workspace_id": command.workspace_id,
                "principal_id": command.principal_id,
                "active_agent_version_id": command.active_agent_version_id,
            },
        )

    def _ensure_agent_version_status(self, *, agent_version_id: str, status: str) -> None:
        row = self.connection.execute(
            text(
                """
                SELECT status
                FROM product_agent_versions
                WHERE agent_version_id = :agent_version_id
                """
            ),
            {"agent_version_id": agent_version_id},
        ).mappings().first()
        if row is None:
            raise ProductPersistenceConflict("unknown Product AgentVersion")
        if row["status"] != status:
            raise ProductPersistenceConflict(f"Product AgentVersion must be {status}")

    def _has_owner_receipt(self, *, command_id: str, tenant_id: str) -> bool:
        row = self.connection.execute(
            text(
                """
                SELECT 1
                FROM product_command_receipts
                WHERE command_id = :command_id
                  AND tenant_id = :tenant_id
                  AND owner_receipt_ref IS NOT NULL
                LIMIT 1
                """
            ),
            {"command_id": command_id, "tenant_id": tenant_id},
        ).scalar_one_or_none()
        return row is not None

    def _append_receipt(
        self,
        command_id: str,
        tenant_id: str,
        status: str,
        payload: dict[str, Any],
        *,
        owner_receipt_ref: str | None = None,
    ) -> str:
        command_exists = self.connection.execute(
            text(
                """
                SELECT 1
                FROM product_commands
                WHERE command_id = :command_id
                  AND tenant_id = :tenant_id
                """
            ),
            {"command_id": command_id, "tenant_id": tenant_id},
        ).scalar_one_or_none()
        if command_exists is None:
            raise ProductPersistenceConflict("owner receipt target unavailable")
        latest = self.connection.execute(
            text(
                """
                SELECT coalesce(max(receipt_version), 0)
                FROM product_command_receipts
                WHERE command_id = :command_id
                """
            ),
            {"command_id": command_id},
        ).scalar_one()
        version = int(latest) + 1
        receipt_id = f"{command_id}:receipt:{version}"
        self.connection.execute(
            text(
                """
                INSERT INTO product_command_receipts (
                    receipt_id, tenant_id, command_id, receipt_version, status,
                    owner_receipt_ref, receipt_hash, domain_success_ref
                )
                VALUES (
                    :receipt_id, :tenant_id, :command_id, :receipt_version, :status,
                    :owner_receipt_ref, :receipt_hash, null
                )
                """
            ),
            {
                "receipt_id": receipt_id,
                "tenant_id": tenant_id,
                "command_id": command_id,
                "receipt_version": version,
                "status": status,
                "owner_receipt_ref": owner_receipt_ref,
                "receipt_hash": canonical_sha256(payload),
            },
        )
        return receipt_id


def stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


__all__ = [
    "ProductActionCommandRef",
    "ProductActionTokenRef",
    "ProductActionTokenStatusRef",
    "ProductAgentAssetRef",
    "ProductAgentCatalogEntryView",
    "ProductCommandReceiptRef",
    "ProductCommandSubmission",
    "ProductPersistenceConflict",
    "ProductProjectionEventRef",
    "ProductProjectionEventView",
    "ProductRepository",
    "ProductStreamCursorRef",
    "ProductUnitOfWork",
    "stable_json",
]
