from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_sha256


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

    @property
    def request_hash(self) -> str:
        return canonical_sha256(self.payload)


@dataclass(frozen=True, slots=True)
class ProductCommandReceiptRef:
    command_id: str
    receipt_id: str
    status: str
    duplicate: bool = False


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
                "journal_sequence_no": command.journal_sequence_no,
                "outbox_message_id": command.outbox_message_id,
            },
        )
        receipt = self._append_receipt(
            command.command_id,
            command.tenant_id,
            "ACCEPTED",
            {"runtime_request_ref": command.runtime_request_ref},
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
    ) -> None:
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
    ) -> None:
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

    def _append_receipt(
        self,
        command_id: str,
        tenant_id: str,
        status: str,
        payload: dict[str, Any],
        *,
        owner_receipt_ref: str | None = None,
    ) -> str:
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
    "ProductCommandReceiptRef",
    "ProductCommandSubmission",
    "ProductPersistenceConflict",
    "ProductRepository",
    "ProductUnitOfWork",
    "stable_json",
]
