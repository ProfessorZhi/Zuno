from __future__ import annotations

"""Formal Security / Budget owner fact resolvers (PHASE22 product wiring).

The workspace product composition root binds these resolvers so Agent Core
never trusts caller-supplied decision envelopes: the Product Adapter carries
only opaque ``security_decision_id`` / ``budget_decision_id``; Agent Core
resolves the formal owner fact through the injected port and re-verifies
tenant / workspace / principal / action / resource / decision / epoch /
expiry / hash before any tool step.

- :class:`PostgresSecurityDecisionResolver` issues and reads the Security-owner
  fact from ``security_authorization_decisions`` (+ effective epoch + principal
  context). Product facts persist workspace scope explicitly; legacy Tool facts
  may still recover it from the historical principal-context identity shape.
- :class:`PostgresBudgetDecisionResolver` performs formal Budget Admission
  from the request context (the runtime contract allows ``decision_id`` to be
  empty when the resolver admits from the request context). Limits must be
  present (request-declared or composition default); a run with no limits is
  not admitted and fails closed.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import Engine

from zuno.agent.contracts import BudgetDecisionRef, SecurityDecisionRef
from zuno.agent.runtime.owner_refs import (
    budget_ref_hash,
    security_ref_hash,
)
from zuno.platform.contracts import canonical_sha256
from zuno.platform.security.governance import SecurityDecision, ToolSecurityGate, ToolSecurityProfile
from zuno.platform.security.persistence import (
    SecurityUnitOfWork,
    authorization_decision_hash,
)

PRINCIPAL_CONTEXT_PREFIX = "principal-context:"
BUDGET_OWNER = "platform.budget.admission"


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


class PostgresBudgetDecisionResolver:
    """Budget-owner resolver: formal Budget Admission from owner-bound fact.

    PHASE22 final engineering closure (P0-6): this resolver MUST NOT
    self-attest. The Product Adapter only carries an opaque
    ``budget_decision_id``; Agent Core must resolve the formal
    ``BudgetDecisionRef`` through a Server-owned budget owner fact store.
    Request-declared ``budget_limits`` / composition ``default_limits``
    are NOT a substitute for the formal owner fact — they are
    application values only and can never directly produce
    ``allowed=True``.

    Fail-closed reasons (return ``None``):

    - No ``budget_decision_id`` (the owner fact id is mandatory).
    - Decision fact not found in the bound owner store.
    - Decision ``allowed`` is ``False`` (denied / expired / forged).
    - Foreign tenant / workspace / run scope.
    - Request limits exceed admitted limits.
    - Decision ``decision_hash`` is missing or malformed (the owner fact
      is not Server-signed).
    - ``expires_at`` missing or expired (no fabricated expiry).
    """

    def __init__(
        self,
        engine: Engine | None = None,
        *,
        default_limits: dict[str, Any] | None = None,
    ) -> None:
        # PHASE22 final engineering closure (P0-6): the composition
        # default is recorded for diagnostics only; it NEVER admits a
        # run. ``allowed=True`` requires a Server-owned budget owner
        # fact resolved through ``resolve_owner_fact``.
        self._engine = engine
        self._default_limits = dict(default_limits or {})

    def resolve(self, decision_id: str, context: dict[str, Any]) -> dict[str, Any] | None:
        # PHASE22 final engineering closure (P0-6): the resolver never
        # self-approves. Without a real Server-owned budget owner fact,
        # the resolver returns ``None`` and the Product Profile fails
        # closed as ``BUDGET_OWNER_NOT_BOUND``. Any caller that previously
        # relied on request-declared ``budget_limits`` or the composition
        # ``default_limits`` to auto-approve is now blocked at the
        # resolver boundary.
        if not decision_id:
            return None
        tenant_id = str(context.get("tenant_id") or "").strip()
        workspace_id = str(context.get("workspace_id") or "").strip()
        run_id = str(context.get("run_id") or "").strip()
        principal_id = str(context.get("principal_id") or "").strip()
        if not (tenant_id and workspace_id and run_id and principal_id):
            return None
        if tenant_id.startswith("user:") or tenant_id == "tenant:default":
            return None
        if self._engine is None:
            return None
        owner_fact = self.resolve_owner_fact(
            decision_id=decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )
        if owner_fact is None:
            return None
        if not bool(owner_fact.get("allowed")):
            return None
        if str(owner_fact.get("tenant_id") or "").strip() != tenant_id:
            return None
        if str(owner_fact.get("workspace_id") or "").strip() != workspace_id:
            return None
        # PHASE22 final engineering closure (P0-6): request limits can
        # only NARROW, never WIDEN, the admitted limits. Any caller
        # requesting more than admitted is rejected.
        admitted_limits = dict(owner_fact.get("limits") or {})
        if not admitted_limits:
            return None
        request_limits = dict(context.get("budget_limits") or {})
        for key, value in request_limits.items():
            admitted_value = admitted_limits.get(key)
            if admitted_value is None:
                return None
            try:
                if float(value) > float(admitted_value):
                    return None
            except (TypeError, ValueError):
                return None
        decision_hash = str(owner_fact.get("decision_hash") or "").strip()
        if not decision_hash:
            return None
        ref = BudgetDecisionRef(
            budget_decision_id=decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            run_id=run_id,
            allowed=True,
            limits=admitted_limits,
            owner=BUDGET_OWNER,
            decision_hash=decision_hash,
        )
        return BudgetDecisionRef(
            **{**ref.model_dump(), "decision_hash": budget_ref_hash(ref=ref)}
        ).to_dict()

    def resolve_owner_fact(
        self,
        *,
        decision_id: str,
        tenant_id: str,
        workspace_id: str,
    ) -> dict[str, Any] | None:
        """Resolve the Server-owned budget owner fact.

        Subclasses / production bindings override this with a PostgreSQL
        lookup against the budget owner store. The default
        ``resolve(...)`` entry point MUST be paired with a real
        ``resolve_owner_fact`` implementation before any run can be
        admitted; without it, the resolver returns ``None`` and the
        Product Profile fails closed as ``BUDGET_OWNER_NOT_BOUND``.
        """
        return None


__all__ = [
    "BUDGET_OWNER",
    "PostgresBudgetDecisionResolver",
    "PostgresSecurityDecisionResolver",
]
