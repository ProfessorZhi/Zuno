from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Engine, text
from sqlalchemy.engine import Connection

from zuno.platform.contracts import canonical_json, canonical_sha256


class SecurityPersistenceError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SecurityPrincipalContextReceipt:
    principal_context_id: str
    tenant_id: str
    epoch_ref: str
    context_hash: str


@dataclass(frozen=True, slots=True)
class SecurityEpochReceipt:
    epoch_ref: str
    tenant_id: str
    generation: int
    policy_bundle_hash: str


@dataclass(frozen=True, slots=True)
class SecurityAuthorizationReceipt:
    decision_id: str
    tenant_id: str
    decision: str
    decision_hash: str


@dataclass(frozen=True, slots=True)
class SecurityApprovalRequestReceipt:
    approval_request_id: str
    tenant_id: str
    status: str
    prepared_action_hash: str


@dataclass(frozen=True, slots=True)
class SecurityApprovalDecisionReceipt:
    approval_decision_id: str
    approval_request_id: str
    decision: str
    decision_hash: str


@dataclass(frozen=True, slots=True)
class SecurityOutboxReceipt:
    event_id: str
    tenant_id: str
    payload_hash: str


class SecurityUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._active = False

    def __enter__(self) -> SecurityRepository:
        if self._active:
            raise RuntimeError("SecurityUnitOfWork cannot be nested")
        self._active = True
        self._context = self.engine.begin()
        try:
            self.connection = self._context.__enter__()
            return SecurityRepository(self.connection)
        except BaseException:
            self._active = False
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            self._context.__exit__(exc_type, exc, tb)
        finally:
            self._active = False


class SecurityRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def record_principal_context(
        self,
        *,
        principal_context_id: str,
        tenant_id: str,
        user_principal_id: str,
        epoch_ref: str,
        agent_principal_id: str | None = None,
        task_principal_id: str | None = None,
        session_principal_id: str | None = None,
        run_id: str | None = None,
        status: str = "active",
    ) -> SecurityPrincipalContextReceipt:
        payload = {
            "principal_context_id": principal_context_id,
            "tenant_id": tenant_id,
            "user_principal_id": user_principal_id,
            "agent_principal_id": agent_principal_id,
            "task_principal_id": task_principal_id,
            "session_principal_id": session_principal_id,
            "run_id": run_id,
            "epoch_ref": epoch_ref,
        }
        context_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_principal_contexts(
                    principal_context_id, tenant_id, user_principal_id,
                    agent_principal_id, task_principal_id, session_principal_id,
                    run_id, epoch_ref, context_hash, status
                ) VALUES (
                    :principal_context_id, :tenant_id, :user_principal_id,
                    :agent_principal_id, :task_principal_id, :session_principal_id,
                    :run_id, :epoch_ref, :context_hash, :status
                )
                """
            ),
            {**payload, "context_hash": context_hash, "status": status},
        )
        return SecurityPrincipalContextReceipt(
            principal_context_id=principal_context_id,
            tenant_id=tenant_id,
            epoch_ref=epoch_ref,
            context_hash=context_hash,
        )

    def record_effective_epoch(
        self,
        *,
        epoch_ref: str,
        tenant_id: str,
        policy_bundle_ref: str,
        policy_bundle: dict[str, Any],
        action_set_version: str,
        principal_context_hash: str,
        generation: int,
        status: str = "active",
    ) -> SecurityEpochReceipt:
        policy_bundle_hash = canonical_sha256(policy_bundle)
        self.connection.execute(
            text(
                """
                INSERT INTO security_effective_epochs(
                    epoch_ref, tenant_id, policy_bundle_ref, policy_bundle_hash,
                    action_set_version, principal_context_hash, generation, status
                ) VALUES (
                    :epoch_ref, :tenant_id, :policy_bundle_ref, :policy_bundle_hash,
                    :action_set_version, :principal_context_hash, :generation, :status
                )
                """
            ),
            {
                "epoch_ref": epoch_ref,
                "tenant_id": tenant_id,
                "policy_bundle_ref": policy_bundle_ref,
                "policy_bundle_hash": policy_bundle_hash,
                "action_set_version": action_set_version,
                "principal_context_hash": principal_context_hash,
                "generation": generation,
                "status": status,
            },
        )
        return SecurityEpochReceipt(
            epoch_ref=epoch_ref,
            tenant_id=tenant_id,
            generation=generation,
            policy_bundle_hash=policy_bundle_hash,
        )

    def record_authorization_decision(
        self,
        *,
        decision_id: str,
        tenant_id: str,
        principal_context_id: str,
        epoch_ref: str,
        resource_ref: str,
        action: str,
        decision: str,
        reason_code: str,
        prepared_action_hash: str | None = None,
    ) -> SecurityAuthorizationReceipt:
        payload = {
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "principal_context_id": principal_context_id,
            "epoch_ref": epoch_ref,
            "resource_ref": resource_ref,
            "action": action,
            "decision": decision,
            "reason_code": reason_code,
            "prepared_action_hash": prepared_action_hash,
        }
        decision_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_authorization_decisions(
                    decision_id, tenant_id, principal_context_id, epoch_ref,
                    resource_ref, action, decision, reason_code,
                    prepared_action_hash, decision_hash
                ) VALUES (
                    :decision_id, :tenant_id, :principal_context_id, :epoch_ref,
                    :resource_ref, :action, :decision, :reason_code,
                    :prepared_action_hash, :decision_hash
                )
                """
            ),
            {**payload, "decision_hash": decision_hash},
        )
        return SecurityAuthorizationReceipt(
            decision_id=decision_id,
            tenant_id=tenant_id,
            decision=decision,
            decision_hash=decision_hash,
        )

    def request_approval(
        self,
        *,
        approval_request_id: str,
        tenant_id: str,
        decision_id: str,
        prepared_action_hash: str,
        requested_by_principal_id: str,
        required_approver_policy_ref: str,
        deadline_at: datetime,
        status: str = "pending",
    ) -> SecurityApprovalRequestReceipt:
        self.connection.execute(
            text(
                """
                INSERT INTO security_approval_requests(
                    approval_request_id, tenant_id, decision_id, prepared_action_hash,
                    requested_by_principal_id, required_approver_policy_ref,
                    status, deadline_at
                ) VALUES (
                    :approval_request_id, :tenant_id, :decision_id,
                    :prepared_action_hash, :requested_by_principal_id,
                    :required_approver_policy_ref, :status, :deadline_at
                )
                """
            ),
            {
                "approval_request_id": approval_request_id,
                "tenant_id": tenant_id,
                "decision_id": decision_id,
                "prepared_action_hash": prepared_action_hash,
                "requested_by_principal_id": requested_by_principal_id,
                "required_approver_policy_ref": required_approver_policy_ref,
                "status": status,
                "deadline_at": deadline_at,
            },
        )
        return SecurityApprovalRequestReceipt(
            approval_request_id=approval_request_id,
            tenant_id=tenant_id,
            status=status,
            prepared_action_hash=prepared_action_hash,
        )

    def decide_approval(
        self,
        *,
        approval_decision_id: str,
        tenant_id: str,
        approval_request_id: str,
        approver_principal_id: str,
        decision: str,
    ) -> SecurityApprovalDecisionReceipt:
        payload = {
            "approval_decision_id": approval_decision_id,
            "tenant_id": tenant_id,
            "approval_request_id": approval_request_id,
            "approver_principal_id": approver_principal_id,
            "decision": decision,
        }
        decision_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_approval_decisions(
                    approval_decision_id, tenant_id, approval_request_id,
                    approver_principal_id, decision, decision_hash
                ) VALUES (
                    :approval_decision_id, :tenant_id, :approval_request_id,
                    :approver_principal_id, :decision, :decision_hash
                )
                """
            ),
            {**payload, "decision_hash": decision_hash},
        )
        self.connection.execute(
            text(
                """
                UPDATE security_approval_requests
                SET status = :status
                WHERE approval_request_id = :approval_request_id
                """
            ),
            {"approval_request_id": approval_request_id, "status": decision},
        )
        return SecurityApprovalDecisionReceipt(
            approval_decision_id=approval_decision_id,
            approval_request_id=approval_request_id,
            decision=decision,
            decision_hash=decision_hash,
        )

    def enqueue_security_event(
        self,
        *,
        event_id: str,
        tenant_id: str,
        aggregate_id: str,
        topic: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> SecurityOutboxReceipt:
        self._reject_secret_material(payload)
        payload_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_outbox_events(
                    event_id, tenant_id, aggregate_id, topic, payload,
                    payload_hash, idempotency_key, status
                ) VALUES (
                    :event_id, :tenant_id, :aggregate_id, :topic,
                    CAST(:payload AS jsonb), :payload_hash, :idempotency_key, 'pending'
                )
                """
            ),
            {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "aggregate_id": aggregate_id,
                "topic": topic,
                "payload": canonical_json(payload),
                "payload_hash": payload_hash,
                "idempotency_key": idempotency_key,
            },
        )
        return SecurityOutboxReceipt(event_id=event_id, tenant_id=tenant_id, payload_hash=payload_hash)

    def _reject_secret_material(self, payload: Any) -> None:
        forbidden_keys = {"secret", "secret_material", "plaintext", "material", "value"}
        if isinstance(payload, dict):
            for key, value in payload.items():
                if str(key).lower() in forbidden_keys:
                    raise SecurityPersistenceError("security events must not persist secret material")
                self._reject_secret_material(value)
        elif isinstance(payload, (list, tuple)):
            for item in payload:
                self._reject_secret_material(item)


__all__ = [
    "SecurityApprovalDecisionReceipt",
    "SecurityApprovalRequestReceipt",
    "SecurityAuthorizationReceipt",
    "SecurityEpochReceipt",
    "SecurityOutboxReceipt",
    "SecurityPersistenceError",
    "SecurityPrincipalContextReceipt",
    "SecurityRepository",
    "SecurityUnitOfWork",
]
