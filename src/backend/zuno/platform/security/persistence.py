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


@dataclass(frozen=True, slots=True)
class SecurityAuditRequirementReceipt:
    audit_requirement_id: str
    tenant_id: str
    decision_id: str
    requirement_hash: str


class PostgresSecurityApprovalFactSink:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def record_tool_approval_fact(self, fact: dict[str, Any]) -> None:
        tenant_id = str(fact.get("workspace_id") or fact.get("tenant_id") or "")
        if not tenant_id:
            raise SecurityPersistenceError("security approval fact missing tenant boundary")
        approval_id = str(fact.get("approval_id") or "")
        if not approval_id:
            raise SecurityPersistenceError("security approval fact missing approval_id")
        status = str(fact.get("status") or "")
        prepared_action_hash = str(fact.get("prepared_action_hash") or "")
        if len(prepared_action_hash) != 64:
            raise SecurityPersistenceError("security approval fact missing prepared_action_hash")

        epoch_ref = f"security-epoch:{tenant_id}:{fact.get('task_id') or 'task'}"
        principal_context_id = f"principal-context:{tenant_id}:{fact.get('task_id') or 'task'}"
        decision_id = f"authorization-decision:{approval_id}"
        approval_request_id = f"approval-request:{approval_id}"
        outbox_event_id = f"security-event:{approval_id}:{status}"

        with SecurityUnitOfWork(self.engine) as repo:
            repo.ensure_effective_epoch(
                epoch_ref=epoch_ref,
                tenant_id=tenant_id,
                policy_bundle_ref="policy:tool-runtime",
                policy_bundle={
                    "security_decision": fact.get("security_decision"),
                    "required_approval": fact.get("required_approval"),
                },
                action_set_version="tool-runtime:v1",
                principal_context_hash=canonical_sha256(
                    {
                        "workspace_id": fact.get("workspace_id"),
                        "user_id": fact.get("user_id"),
                        "task_id": fact.get("task_id"),
                    }
                ),
                generation=1,
            )
            repo.ensure_principal_context(
                principal_context_id=principal_context_id,
                tenant_id=tenant_id,
                user_principal_id=str(fact.get("user_id") or "unknown-user"),
                agent_principal_id="tool-runtime",
                task_principal_id=str(fact.get("task_id") or "unknown-task"),
                session_principal_id=str(fact.get("trace_id") or "unknown-trace"),
                run_id=str(fact.get("tool_request_id") or approval_id),
                epoch_ref=epoch_ref,
            )
            security_decision = (
                "DENY" if status == "failed_closed_before_effect" else "REQUIRES_APPROVAL"
            )
            repo.ensure_authorization_decision(
                decision_id=decision_id,
                tenant_id=tenant_id,
                principal_context_id=principal_context_id,
                epoch_ref=epoch_ref,
                resource_ref=str(fact.get("tool_id") or "tool"),
                action=str(fact.get("required_approval") or "tool"),
                decision=security_decision,
                reason_code=str(fact.get("security_decision") or "approval_required"),
                prepared_action_hash=prepared_action_hash,
            )
            repo.ensure_audit_requirement(
                audit_requirement_id=f"audit-requirement:{approval_id}:{status}",
                tenant_id=tenant_id,
                decision_id=decision_id,
                audit_channel_id="security-audit:tool-runtime",
                status="failed_closed" if status == "failed_closed_before_effect" else "required",
            )
            if status != "failed_closed_before_effect":
                repo.ensure_approval_request(
                    approval_request_id=approval_request_id,
                    tenant_id=tenant_id,
                    decision_id=decision_id,
                    prepared_action_hash=prepared_action_hash,
                    requested_by_principal_id=str(fact.get("user_id") or "unknown-user"),
                    required_approver_policy_ref="approval-policy:tool-runtime",
                )
            if status == "approved_before_effect":
                repo.ensure_approval_decision(
                    approval_decision_id=f"approval-decision:{approval_id}",
                    tenant_id=tenant_id,
                    approval_request_id=approval_request_id,
                    approver_principal_id=str(fact.get("user_id") or "unknown-user"),
                    decision="approved",
                )
            repo.ensure_security_event(
                event_id=outbox_event_id,
                tenant_id=tenant_id,
                aggregate_id=decision_id,
                topic=f"security.tool_approval.{status}",
                payload={
                    "approval_id": approval_id,
                    "approval_request_id": approval_request_id,
                    "prepared_action_hash": prepared_action_hash,
                    "status": status,
                    "audit_ref": fact.get("audit_ref"),
                    "credential_refs": fact.get("credential_refs") or [],
                    "sandbox": fact.get("sandbox") or {},
                },
                idempotency_key=f"security-approval:{approval_id}:{status}",
            )


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

    def ensure_principal_context(
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
                ON CONFLICT (principal_context_id) DO NOTHING
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

    def ensure_effective_epoch(
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
                ON CONFLICT (epoch_ref) DO NOTHING
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

    def ensure_authorization_decision(
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
                ON CONFLICT (decision_id) DO NOTHING
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

    def ensure_approval_request(
        self,
        *,
        approval_request_id: str,
        tenant_id: str,
        decision_id: str,
        prepared_action_hash: str,
        requested_by_principal_id: str,
        required_approver_policy_ref: str,
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
                    :required_approver_policy_ref, :status, now() + interval '5 minutes'
                )
                ON CONFLICT (approval_request_id) DO NOTHING
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

    def ensure_approval_decision(
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
                ON CONFLICT (approval_request_id) DO NOTHING
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

    def ensure_audit_requirement(
        self,
        *,
        audit_requirement_id: str,
        tenant_id: str,
        decision_id: str,
        audit_channel_id: str,
        status: str = "required",
    ) -> SecurityAuditRequirementReceipt:
        payload = {
            "audit_requirement_id": audit_requirement_id,
            "tenant_id": tenant_id,
            "decision_id": decision_id,
            "audit_channel_id": audit_channel_id,
            "status": status,
        }
        requirement_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_audit_requirements(
                    audit_requirement_id, tenant_id, decision_id, audit_channel_id,
                    requirement_hash, status
                ) VALUES (
                    :audit_requirement_id, :tenant_id, :decision_id, :audit_channel_id,
                    :requirement_hash, :status
                )
                ON CONFLICT (audit_requirement_id) DO NOTHING
                """
            ),
            {**payload, "requirement_hash": requirement_hash},
        )
        return SecurityAuditRequirementReceipt(
            audit_requirement_id=audit_requirement_id,
            tenant_id=tenant_id,
            decision_id=decision_id,
            requirement_hash=requirement_hash,
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

    def ensure_security_event(
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
                ON CONFLICT (tenant_id, idempotency_key) DO NOTHING
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
    "SecurityAuditRequirementReceipt",
    "SecurityAuthorizationReceipt",
    "SecurityEpochReceipt",
    "SecurityOutboxReceipt",
    "SecurityPersistenceError",
    "SecurityPrincipalContextReceipt",
    "PostgresSecurityApprovalFactSink",
    "SecurityRepository",
    "SecurityUnitOfWork",
]
