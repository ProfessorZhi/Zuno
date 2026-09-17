from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
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
    expires_at: datetime | None = None


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
    audit_channel_id: str
    status: str
    requirement_hash: str


@dataclass(frozen=True, slots=True)
class SecuritySecretRefReceipt:
    secret_ref: str
    tenant_id: str
    audience: str
    scope_hash: str


@dataclass(frozen=True, slots=True)
class SecuritySecretLeaseReceipt:
    lease_id: str
    tenant_id: str
    secret_ref: str
    audience: str
    lease_hash: str


@dataclass(frozen=True, slots=True)
class SecurityRedactionDecisionReceipt:
    redaction_id: str
    tenant_id: str
    decision: str
    decision_hash: str


def authorization_decision_hash(
    *,
    decision_id: str,
    tenant_id: str,
    principal_context_id: str,
    epoch_ref: str,
    resource_ref: str,
    action: str,
    decision: str,
    reason_code: str,
    prepared_action_hash: str | None,
    expires_at: datetime | None = None,
) -> str:
    payload: dict[str, Any] = {
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
    if expires_at is not None:
        payload["expires_at"] = expires_at.isoformat()
    return canonical_sha256(payload)


class PostgresSecurityApprovalEventSink:
    """Durable approval-event projection.

    This sink records tool approval lifecycle events for audit/observability.
    It does not create SecurityEpoch, AuthorizationDecision, ApprovalDecision,
    or AuditRequirement authority facts; those remain owned by the canonical
    Security / Tool Gateway paths.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def record_tool_approval_fact(self, fact: dict[str, Any]) -> None:
        tenant_id = str(fact.get("tenant_id") or "").strip()
        if not tenant_id:
            raise SecurityPersistenceError("security approval event missing tenant boundary")
        workspace_id = str(fact.get("workspace_id") or "").strip()
        if not workspace_id:
            raise SecurityPersistenceError("security approval event missing workspace boundary")
        approval_id = str(fact.get("approval_id") or "").strip()
        if not approval_id:
            raise SecurityPersistenceError("security approval event missing approval_id")
        status = str(fact.get("status") or "").strip()
        if not status:
            raise SecurityPersistenceError("security approval event missing status")
        prepared_action_hash = str(fact.get("prepared_action_hash") or "").strip()
        if len(prepared_action_hash) != 64:
            raise SecurityPersistenceError("security approval event missing prepared_action_hash")

        event_id = f"security-approval-event:{approval_id}:{status}"
        aggregate_id = f"tool-approval:{approval_id}"
        payload = {
            "approval_id": approval_id,
            "tool_request_id": str(fact.get("tool_request_id") or ""),
            "tool_id": str(fact.get("tool_id") or ""),
            "workspace_id": workspace_id,
            "user_id": str(fact.get("user_id") or ""),
            "task_id": str(fact.get("task_id") or ""),
            "trace_id": str(fact.get("trace_id") or ""),
            "approval_decision_ref": str(fact.get("approval_decision_ref") or ""),
            "approval_adapter_ref": str(fact.get("approval_adapter_ref") or ""),
            "required_approval": str(fact.get("required_approval") or ""),
            "prepared_action_hash": prepared_action_hash,
            "status": status,
            "security_decision": str(fact.get("security_decision") or ""),
            "audit_ref": str(fact.get("audit_ref") or ""),
        }
        with SecurityUnitOfWork(self.engine) as repo:
            repo.ensure_security_event(
                event_id=event_id,
                tenant_id=tenant_id,
                aggregate_id=aggregate_id,
                topic=f"security.tool_approval.{status}",
                payload=payload,
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
        workspace_id: str | None = None,
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
        if workspace_id is not None:
            payload["workspace_id"] = workspace_id
        context_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_principal_contexts(
                    principal_context_id, tenant_id, user_principal_id, workspace_id,
                    agent_principal_id, task_principal_id, session_principal_id,
                    run_id, epoch_ref, context_hash, status
                ) VALUES (
                    :principal_context_id, :tenant_id, :user_principal_id, :workspace_id,
                    :agent_principal_id, :task_principal_id, :session_principal_id,
                    :run_id, :epoch_ref, :context_hash, :status
                )
                ON CONFLICT (principal_context_id) DO NOTHING
                """
            ),
            {**payload, "workspace_id": workspace_id, "context_hash": context_hash, "status": status},
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
        values = {
            "epoch_ref": epoch_ref,
            "tenant_id": tenant_id,
            "policy_bundle_ref": policy_bundle_ref,
            "policy_bundle_hash": policy_bundle_hash,
            "action_set_version": action_set_version,
            "principal_context_hash": principal_context_hash,
            "generation": generation,
            "status": status,
        }
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
            values,
        )
        row = self.connection.execute(
            text(
                """
                SELECT epoch_ref, tenant_id, policy_bundle_ref, policy_bundle_hash,
                       action_set_version, principal_context_hash, generation, status
                FROM security_effective_epochs
                WHERE epoch_ref = :epoch_ref
                """
            ),
            {"epoch_ref": epoch_ref},
        ).mappings().one()
        persisted_identity = {
            "epoch_ref": str(row["epoch_ref"]),
            "tenant_id": str(row["tenant_id"]),
            "policy_bundle_ref": str(row["policy_bundle_ref"]),
            "policy_bundle_hash": str(row["policy_bundle_hash"]),
            "action_set_version": str(row["action_set_version"]),
            "principal_context_hash": str(row["principal_context_hash"]),
            "generation": int(row["generation"]),
        }
        expected_identity = {key: value for key, value in values.items() if key != "status"}
        if persisted_identity != expected_identity:
            raise SecurityPersistenceError(
                "effective security epoch identity was reused with different content"
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
        expires_at: datetime | None = None,
    ) -> SecurityAuthorizationReceipt:
        payload: dict[str, Any] = {
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
        if expires_at is not None:
            payload["expires_at"] = expires_at.isoformat()
        decision_hash = authorization_decision_hash(
            decision_id=decision_id,
            tenant_id=tenant_id,
            principal_context_id=principal_context_id,
            epoch_ref=epoch_ref,
            resource_ref=resource_ref,
            action=action,
            decision=decision,
            reason_code=reason_code,
            prepared_action_hash=prepared_action_hash,
            expires_at=expires_at,
        )
        self.connection.execute(
            text(
                """
                INSERT INTO security_authorization_decisions(
                    decision_id, tenant_id, principal_context_id, epoch_ref,
                    resource_ref, action, decision, reason_code,
                    prepared_action_hash, decision_hash, expires_at
                ) VALUES (
                    :decision_id, :tenant_id, :principal_context_id, :epoch_ref,
                    :resource_ref, :action, :decision, :reason_code,
                    :prepared_action_hash, :decision_hash, :expires_at
                )
                ON CONFLICT (decision_id) DO NOTHING
                """
            ),
            {**{k: v for k, v in payload.items() if k != "expires_at"},
             "decision_hash": decision_hash, "expires_at": expires_at},
        )
        row = self.connection.execute(
            text(
                """
                SELECT decision_id, tenant_id, principal_context_id, epoch_ref,
                       resource_ref, action, decision, reason_code,
                       prepared_action_hash, decision_hash, expires_at
                FROM security_authorization_decisions
                WHERE decision_id = :decision_id
                """
            ),
            {"decision_id": decision_id},
        ).mappings().one()
        persisted: dict[str, Any] = {
            "decision_id": str(row["decision_id"]),
            "tenant_id": str(row["tenant_id"]),
            "principal_context_id": str(row["principal_context_id"]),
            "epoch_ref": str(row["epoch_ref"]),
            "resource_ref": str(row["resource_ref"]),
            "action": str(row["action"]),
            "decision": str(row["decision"]),
            "reason_code": str(row["reason_code"]),
            "prepared_action_hash": None
            if row["prepared_action_hash"] is None
            else str(row["prepared_action_hash"]),
        }
        if row["expires_at"] is not None:
            persisted["expires_at"] = row["expires_at"].isoformat()
        if persisted != payload or str(row["decision_hash"]) != decision_hash:
            raise SecurityPersistenceError(
                "authorization decision identity was reused with different content"
            )
        return SecurityAuthorizationReceipt(
            decision_id=decision_id,
            tenant_id=tenant_id,
            decision=decision,
            decision_hash=decision_hash,
            expires_at=row["expires_at"],
        )

    def read_authorization_decision_fact(
        self,
        *,
        decision_id: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Read the Security-owner authorization fact for the workspace
        Security decision resolver (PHASE22 product wiring).

        Returns the owner-recorded fact fields (or ``None`` when the owner
        has no such fact). The resolver maps the fact to the runtime
        ``SecurityDecisionRef``; Agent Core re-verifies hash / epoch / scope
        before any tool step. The caller never mints its own allow decision.
        """
        row = self.connection.execute(
            text(
                """
                SELECT d.decision_id, d.tenant_id, d.principal_context_id,
                       d.epoch_ref, d.resource_ref, d.action, d.decision,
                       d.reason_code, d.prepared_action_hash, d.decision_hash,
                       d.created_at AS issued_at, d.expires_at,
                       e.status AS epoch_status, p.user_principal_id, p.workspace_id
                FROM security_authorization_decisions d
                JOIN security_effective_epochs e
                     ON e.epoch_ref = d.epoch_ref AND e.tenant_id = d.tenant_id
                LEFT JOIN security_principal_contexts p
                     ON p.principal_context_id = d.principal_context_id
                WHERE d.decision_id = :decision_id AND d.tenant_id = :tenant_id
                """
            ),
            {"decision_id": decision_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            return None
        return dict(row)

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
        persisted = self.read_audit_requirement(
            audit_requirement_id=audit_requirement_id,
            tenant_id=tenant_id,
        )
        if persisted is None:
            raise SecurityPersistenceError("audit requirement could not be persisted")
        if (
            persisted.decision_id != decision_id
            or persisted.audit_channel_id != audit_channel_id
            or persisted.status != status
            or persisted.requirement_hash != requirement_hash
        ):
            raise SecurityPersistenceError(
                "audit requirement identity was reused with different content"
            )
        return persisted

    def read_audit_requirement(
        self,
        *,
        audit_requirement_id: str,
        tenant_id: str,
    ) -> SecurityAuditRequirementReceipt | None:
        row = self.connection.execute(
            text(
                """
                SELECT audit_requirement_id, tenant_id, decision_id, audit_channel_id,
                       requirement_hash, status
                FROM security_audit_requirements
                WHERE audit_requirement_id = :audit_requirement_id
                """
            ),
            {"audit_requirement_id": audit_requirement_id},
        ).mappings().first()
        if row is None:
            return None
        if str(row["tenant_id"]) != tenant_id:
            raise SecurityPersistenceError("audit requirement belongs to another tenant")
        persisted_payload = {
            "audit_requirement_id": str(row["audit_requirement_id"]),
            "tenant_id": str(row["tenant_id"]),
            "decision_id": str(row["decision_id"]),
            "audit_channel_id": str(row["audit_channel_id"]),
            "status": str(row["status"]),
        }
        expected_hash = canonical_sha256(persisted_payload)
        if str(row["requirement_hash"]) != expected_hash:
            raise SecurityPersistenceError(
                "audit requirement hash does not match persisted content"
            )
        return SecurityAuditRequirementReceipt(
            audit_requirement_id=persisted_payload["audit_requirement_id"],
            tenant_id=persisted_payload["tenant_id"],
            decision_id=persisted_payload["decision_id"],
            audit_channel_id=persisted_payload["audit_channel_id"],
            status=persisted_payload["status"],
            requirement_hash=expected_hash,
        )

    def record_secret_ref(
        self,
        *,
        secret_ref: str,
        tenant_id: str,
        credential_version_ref: str,
        audience: str,
        owner_principal_id: str,
        scope: dict[str, Any],
        status: str = "active",
    ) -> SecuritySecretRefReceipt:
        self._reject_secret_material(scope)
        scope_hash = canonical_sha256(scope)
        self.connection.execute(
            text(
                """
                INSERT INTO security_secret_refs(
                    secret_ref, tenant_id, credential_version_ref, audience,
                    owner_principal_id, scope_hash, status
                ) VALUES (
                    :secret_ref, :tenant_id, :credential_version_ref, :audience,
                    :owner_principal_id, :scope_hash, :status
                )
                ON CONFLICT (secret_ref) DO NOTHING
                """
            ),
            {
                "secret_ref": secret_ref,
                "tenant_id": tenant_id,
                "credential_version_ref": credential_version_ref,
                "audience": audience,
                "owner_principal_id": owner_principal_id,
                "scope_hash": scope_hash,
                "status": status,
            },
        )
        return SecuritySecretRefReceipt(secret_ref, tenant_id, audience, scope_hash)

    def issue_secret_lease(
        self,
        *,
        lease_id: str,
        tenant_id: str,
        secret_ref: str,
        workload_identity_ref: str,
        on_behalf_of_binding_ref: str,
        audience: str,
        lease_generation: int,
        expires_at: datetime,
    ) -> SecuritySecretLeaseReceipt:
        if lease_generation <= 0:
            raise SecurityPersistenceError("secret lease_generation must be positive")
        payload = {
            "lease_id": lease_id,
            "tenant_id": tenant_id,
            "secret_ref": secret_ref,
            "workload_identity_ref": workload_identity_ref,
            "on_behalf_of_binding_ref": on_behalf_of_binding_ref,
            "audience": audience,
            "lease_generation": lease_generation,
            "expires_at": expires_at.isoformat(),
        }
        lease_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_secret_leases(
                    lease_id, tenant_id, secret_ref, workload_identity_ref,
                    on_behalf_of_binding_ref, audience, lease_generation, lease_hash, expires_at
                ) VALUES (
                    :lease_id, :tenant_id, :secret_ref, :workload_identity_ref,
                    :on_behalf_of_binding_ref, :audience, :lease_generation, :lease_hash,
                    :expires_at
                )
                """
            ),
            {**payload, "lease_hash": lease_hash},
        )
        return SecuritySecretLeaseReceipt(lease_id, tenant_id, secret_ref, audience, lease_hash)

    def validate_secret_lease(
        self,
        *,
        lease_id: str,
        tenant_id: str,
        audience: str,
        now: datetime | None = None,
    ) -> SecuritySecretLeaseReceipt:
        current_time = now or datetime.now(tz=UTC)
        row = self.connection.execute(
            text(
                """
                SELECT l.lease_id, l.tenant_id, l.secret_ref, l.audience, l.lease_hash,
                       l.expires_at, s.status AS secret_status
                FROM security_secret_leases l
                JOIN security_secret_refs s ON s.secret_ref = l.secret_ref
                WHERE l.lease_id = :lease_id AND l.tenant_id = :tenant_id
                """
            ),
            {"lease_id": lease_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            raise SecurityPersistenceError("secret lease missing")
        if row["secret_status"] != "active":
            raise SecurityPersistenceError("secret lease references a revoked secret")
        if row["audience"] != audience:
            raise SecurityPersistenceError("secret lease audience mismatch")
        expires_at = row["expires_at"]
        if expires_at.tzinfo is None and current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)
        if expires_at <= current_time:
            raise SecurityPersistenceError("secret lease expired")
        return SecuritySecretLeaseReceipt(
            lease_id=row["lease_id"],
            tenant_id=row["tenant_id"],
            secret_ref=row["secret_ref"],
            audience=row["audience"],
            lease_hash=row["lease_hash"],
        )

    def record_redaction_decision(
        self,
        *,
        redaction_id: str,
        tenant_id: str,
        source_ref: str,
        sink_ref: str,
        trust_label: str,
        requested_decision: str,
        redaction_policy_ref: str,
        redacted_payload: dict[str, Any],
        redaction_succeeded: bool,
    ) -> SecurityRedactionDecisionReceipt:
        self._reject_secret_material(redacted_payload)
        decision = requested_decision if redaction_succeeded else "block"
        redacted_payload_hash = canonical_sha256(redacted_payload)
        payload = {
            "redaction_id": redaction_id,
            "tenant_id": tenant_id,
            "source_ref": source_ref,
            "sink_ref": sink_ref,
            "trust_label": trust_label,
            "decision": decision,
            "redaction_policy_ref": redaction_policy_ref,
            "redacted_payload_hash": redacted_payload_hash,
            "redaction_succeeded": redaction_succeeded,
        }
        decision_hash = canonical_sha256(payload)
        self.connection.execute(
            text(
                """
                INSERT INTO security_redaction_decisions(
                    redaction_id, tenant_id, source_ref, sink_ref, trust_label,
                    decision, redaction_policy_ref, redacted_payload_hash, decision_hash
                ) VALUES (
                    :redaction_id, :tenant_id, :source_ref, :sink_ref, :trust_label,
                    :decision, :redaction_policy_ref, :redacted_payload_hash, :decision_hash
                )
                """
            ),
            {**payload, "decision_hash": decision_hash},
        )
        return SecurityRedactionDecisionReceipt(redaction_id, tenant_id, decision, decision_hash)

    def validate_pre_effect_authorization(
        self,
        *,
        decision_id: str,
        tenant_id: str,
        prepared_action_hash: str,
        require_approved_request: bool = True,
        now: datetime | None = None,
    ) -> SecurityAuthorizationReceipt:
        current_time = now or datetime.now(tz=UTC)
        row = self.connection.execute(
            text(
                """
                SELECT d.decision_id, d.tenant_id, d.decision, d.decision_hash,
                       d.prepared_action_hash, e.status AS epoch_status,
                       r.status AS approval_status, r.deadline_at
                FROM security_authorization_decisions d
                JOIN security_effective_epochs e ON e.epoch_ref = d.epoch_ref
                LEFT JOIN security_approval_requests r ON r.decision_id = d.decision_id
                WHERE d.decision_id = :decision_id AND d.tenant_id = :tenant_id
                """
            ),
            {"decision_id": decision_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row is None:
            raise SecurityPersistenceError("authorization decision missing")
        if row["prepared_action_hash"] != prepared_action_hash:
            raise SecurityPersistenceError("prepared action hash changed before effect")
        if row["epoch_status"] != "active":
            raise SecurityPersistenceError("stale security epoch before effect")
        if row["decision"] == "DENY":
            raise SecurityPersistenceError("authorization decision denies effect")
        if require_approved_request and row["decision"] == "REQUIRES_APPROVAL":
            if row["approval_status"] != "approved":
                raise SecurityPersistenceError("approval required before effect")
            deadline_at = row["deadline_at"]
            if deadline_at.tzinfo is None and current_time.tzinfo is not None:
                current_time = current_time.replace(tzinfo=None)
            if deadline_at <= current_time:
                raise SecurityPersistenceError("approval deadline expired before effect")
        return SecurityAuthorizationReceipt(
            decision_id=row["decision_id"],
            tenant_id=row["tenant_id"],
            decision=row["decision"],
            decision_hash=row["decision_hash"],
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
        persisted = self.connection.execute(
            text(
                """
                SELECT event_id, aggregate_id, topic, payload_hash
                FROM security_outbox_events
                WHERE tenant_id = :tenant_id AND idempotency_key = :idempotency_key
                """
            ),
            {"tenant_id": tenant_id, "idempotency_key": idempotency_key},
        ).mappings().one()
        if (
            str(persisted["event_id"]) != event_id
            or str(persisted["aggregate_id"]) != aggregate_id
            or str(persisted["topic"]) != topic
            or str(persisted["payload_hash"]) != payload_hash
        ):
            raise SecurityPersistenceError(
                "security event idempotency key was reused with different content"
            )
        return SecurityOutboxReceipt(
            event_id=str(persisted["event_id"]),
            tenant_id=tenant_id,
            payload_hash=str(persisted["payload_hash"]),
        )

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
    "PostgresSecurityApprovalEventSink",
    "SecurityRedactionDecisionReceipt",
    "SecurityRepository",
    "SecuritySecretLeaseReceipt",
    "SecuritySecretRefReceipt",
    "SecurityUnitOfWork",
]
