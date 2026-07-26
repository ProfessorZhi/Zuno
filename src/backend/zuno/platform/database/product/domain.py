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
                SELECT projection_event_id, source_watermark, gap_detected
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
            gap_detected=gap_detected,
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
    "ProductActionTokenRef",
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
