from __future__ import annotations

"""Formal Security owner fact resolver for Product wiring.

The Product Adapter carries only an opaque ``security_decision_id``; Agent
Core resolves the formal owner fact through this port and re-verifies tenant /
workspace / principal / action / resource / decision / epoch / expiry / hash.

Formal Budget Admission is deliberately not implemented here. PSC-C deferred
that owner surface because Current has caller-declared runtime limits but no
durable Budget owner store or issuer. Product Budget admission therefore stays
fail-closed through the generic ``BudgetDecisionResolver`` port until a real
business owner contract is justified.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Engine

from zuno.agent.contracts import SecurityDecisionRef
from zuno.agent.runtime.owner_refs import security_ref_hash
from zuno.platform.contracts import canonical_sha256
from zuno.platform.security.governance import SecurityDecision, ToolSecurityGate, ToolSecurityProfile
from zuno.platform.security.persistence import (
    SecurityUnitOfWork,
    authorization_decision_hash,
)

PRINCIPAL_CONTEXT_PREFIX = "principal-context:"


def _workspace_from_principal_context_id(principal_context_id: str) -> str:
    """Recover the owner-recorded workspace from the principal context id.

    The Tool Control Plane records principal contexts as
    ``principal-context:{workspace_id}:{call_id}``; the workspace is the
    owner-encoded scope of the authorization fact. An id outside that shape
    has no recoverable workspace dimension and must not be mapped.
    """
    if not principal_context_id or not principal_context_id.startswith(PRINCIPAL_CONTEXT_PREFIX):
        return ""
    remainder = principal_context_id[len(PRINCIPAL_CONTEXT_PREFIX):]
    workspace_id, _, _ = remainder.partition(":")
    return workspace_id.strip()


class PostgresSecurityDecisionResolver:
    """Security owner port for Product admission.

    ``issue()`` evaluates one Product tool action through the existing
    Security-owned ToolSecurityGate and persists an immutable owner fact.
    ``resolve()`` reads that fact back and verifies durable hash, scope, epoch
    and expiry before mapping it to ``SecurityDecisionRef``. No caller payload
    can mint an allow decision.

    A positive ``decision_ttl_seconds`` is required for issuance. When it is
    absent the resolver remains read-only/fail-closed, which keeps policy TTL
    outside code defaults.
    """

    def __init__(
        self,
        engine: Engine,
        security_epoch_ref: str = "",
        *,
        decision_ttl_seconds: int | None = None,
    ) -> None:
        self._engine = engine
        self._bound_epoch = str(security_epoch_ref or "").strip()
        ttl = int(decision_ttl_seconds or 0)
        self._decision_ttl_seconds = ttl if ttl > 0 else 0

    def issue(self, context: dict[str, Any]) -> dict[str, str] | None:
        if self._decision_ttl_seconds <= 0:
            return None
        tenant_id = str(context.get("tenant_id") or "").strip()
        workspace_id = str(context.get("workspace_id") or "").strip()
        principal_id = str(context.get("principal_id") or "").strip()
        action = str(context.get("action") or "").strip()
        resource = str(context.get("resource") or "").strip()
        task_id = str(context.get("task_id") or "").strip()
        trace_id = str(context.get("trace_id") or "").strip()
        run_id = str(context.get("run_id") or "").strip()
        if not all((tenant_id, workspace_id, principal_id, action, resource, task_id)):
            return None
        if tenant_id.startswith("user:") or tenant_id == "tenant:default":
            return None

        side_effect_level = str(context.get("side_effect_level") or "unknown").strip()
        execution_mode = str(context.get("execution_mode") or "").strip()
        profile = ToolSecurityProfile.from_tool_card(
            tool_id=resource,
            side_effect_level=side_effect_level,
            execution_mode=execution_mode,
        )
        gate = ToolSecurityGate().evaluate(
            profile=profile,
            model_intent=str(context.get("model_intent") or ""),
            proposed_args=dict(context.get("proposed_args") or {}),
            workspace_id=workspace_id,
            trace_id=trace_id or f"security-product:{task_id}",
            task_id=task_id,
        )
        if gate.decision is SecurityDecision.ALLOW:
            decision = "USE_ONLY"
        elif gate.decision is SecurityDecision.REQUIRE_APPROVAL:
            decision = "REQUIRES_APPROVAL"
        else:
            decision = "DENY"
        reason_code = gate.findings[0].code if gate.findings else "product_security_policy"

        scope_payload = {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "principal_id": principal_id,
            "task_id": task_id,
            "action": action,
            "resource": resource,
        }
        scope_hash = canonical_sha256(scope_payload)
        epoch_ref = f"security-epoch:product:{scope_hash[:32]}"
        principal_context_id = f"principal-context:product:{scope_hash[:32]}"
        decision_id = f"authorization-decision:product:{scope_hash[:32]}"
        policy_bundle = {
            "policy": "workspace-product-tool-admission",
            "side_effect_level": side_effect_level,
            "execution_mode": execution_mode,
            "gate_decision": gate.decision.value,
        }
        principal_context_hash = canonical_sha256(scope_payload)

        with SecurityUnitOfWork(self._engine) as repo:
            repo.ensure_effective_epoch(
                epoch_ref=epoch_ref,
                tenant_id=tenant_id,
                policy_bundle_ref="security-policy-bundle:workspace-product:v1",
                policy_bundle=policy_bundle,
                action_set_version="workspace-product-actions:v1",
                principal_context_hash=principal_context_hash,
                generation=1,
            )
            repo.ensure_principal_context(
                principal_context_id=principal_context_id,
                tenant_id=tenant_id,
                user_principal_id=principal_id,
                workspace_id=workspace_id,
                agent_principal_id="agent:zuno-workspace-runtime",
                task_principal_id=f"task:{task_id}",
                session_principal_id=f"trace:{trace_id or task_id}",
                run_id=run_id or f"run:{task_id}",
                epoch_ref=epoch_ref,
            )
            existing = repo.read_authorization_decision_fact(
                decision_id=decision_id,
                tenant_id=tenant_id,
            )
            if existing is None:
                expires_at = datetime.now(tz=UTC) + timedelta(seconds=self._decision_ttl_seconds)
                repo.ensure_authorization_decision(
                    decision_id=decision_id,
                    tenant_id=tenant_id,
                    principal_context_id=principal_context_id,
                    epoch_ref=epoch_ref,
                    resource_ref=resource,
                    action=action,
                    decision=decision,
                    reason_code=reason_code,
                    prepared_action_hash=None,
                    expires_at=expires_at,
                )
        return {"decision_id": decision_id, "security_epoch_ref": epoch_ref}

    def resolve(self, decision_id: str, context: dict[str, Any]) -> dict[str, Any] | None:
        if not decision_id:
            return None
        tenant_id = str(context.get("tenant_id") or "").strip()
        expected_epoch = str(context.get("security_epoch_ref") or self._bound_epoch or "").strip()
        if not tenant_id or tenant_id.startswith("user:") or tenant_id == "tenant:default":
            return None
        if not expected_epoch:
            return None
        with SecurityUnitOfWork(self._engine) as repo:
            fact = repo.read_authorization_decision_fact(
                decision_id=decision_id,
                tenant_id=tenant_id,
            )
        if not fact or str(fact.get("epoch_status") or "").strip() != "active":
            return None
        epoch_ref = str(fact.get("epoch_ref") or "").strip()
        if not epoch_ref or epoch_ref != expected_epoch:
            return None

        workspace_id = str(fact.get("workspace_id") or "").strip() or _workspace_from_principal_context_id(
            str(fact.get("principal_context_id") or "")
        )
        fact_tenant_id = str(fact.get("tenant_id") or "").strip()
        principal_id = str(fact.get("user_principal_id") or "").strip()
        action = str(fact.get("action") or "").strip()
        resource = str(fact.get("resource_ref") or "").strip()
        decision = str(fact.get("decision") or "").strip()
        if not all((workspace_id, fact_tenant_id, principal_id, action, resource, decision)):
            return None
        if fact_tenant_id != tenant_id:
            return None
        if str(context.get("workspace_id") or "").strip() != workspace_id:
            return None
        if str(context.get("principal_id") or "").strip() != principal_id:
            return None
        if str(context.get("action") or "").strip() != action:
            return None
        if str(context.get("resource") or "").strip() != resource:
            return None

        expires_raw = fact.get("expires_at")
        issued_raw = fact.get("issued_at")
        if expires_raw is None or issued_raw is None:
            return None
        try:
            expires_dt = (
                expires_raw
                if isinstance(expires_raw, datetime)
                else datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
            )
            issued_dt = (
                issued_raw
                if isinstance(issued_raw, datetime)
                else datetime.fromisoformat(str(issued_raw).replace("Z", "+00:00"))
            )
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=UTC)
            if issued_dt.tzinfo is None:
                issued_dt = issued_dt.replace(tzinfo=UTC)
        except (TypeError, ValueError):
            return None
        if expires_dt <= datetime.now(tz=UTC) or expires_dt <= issued_dt:
            return None

        persisted_hash = authorization_decision_hash(
            decision_id=decision_id,
            tenant_id=fact_tenant_id,
            principal_context_id=str(fact.get("principal_context_id") or ""),
            epoch_ref=epoch_ref,
            resource_ref=resource,
            action=action,
            decision=decision,
            reason_code=str(fact.get("reason_code") or ""),
            prepared_action_hash=(
                None
                if fact.get("prepared_action_hash") is None
                else str(fact.get("prepared_action_hash"))
            ),
            expires_at=expires_dt,
        )
        if str(fact.get("decision_hash") or "") != persisted_hash:
            return None

        issued_at = issued_dt.isoformat()
        expires_at = expires_dt.isoformat()
        decision_hash = security_ref_hash(
            decision_id=decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=principal_id,
            action=action,
            resource=resource,
            decision=decision,
            security_epoch_ref=epoch_ref,
            issued_at=issued_at,
            expires_at=expires_at,
        )
        return SecurityDecisionRef(
            decision_id=decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=principal_id,
            action=action,
            resource=resource,
            decision=decision,
            security_epoch_ref=epoch_ref,
            decision_hash=decision_hash,
            issued_at=issued_at,
            expires_at=expires_at,
        ).to_dict()


__all__ = [
    "PostgresSecurityDecisionResolver",
]
