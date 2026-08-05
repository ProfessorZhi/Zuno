from __future__ import annotations

"""Formal Security / Budget owner fact resolvers (PHASE22 product wiring).

The workspace product composition root binds these resolvers so Agent Core
never trusts caller-supplied decision envelopes: the Product Adapter carries
only opaque ``security_decision_id`` / ``budget_decision_id``; Agent Core
resolves the formal owner fact through the injected port and re-verifies
tenant / workspace / principal / action / resource / decision / epoch /
expiry / hash before any tool step.

- :class:`PostgresSecurityDecisionResolver` reads the Security-owner fact
  from ``security_authorization_decisions`` (+ effective epoch + principal
  context). The workspace dimension comes from the owner-recorded principal
  context id (``principal-context:{workspace_id}:{call_id}``); an owner fact
  whose workspace cannot be recovered is not resolvable and fails closed.
- :class:`PostgresBudgetDecisionResolver` performs formal Budget Admission
  from the request context (the runtime contract allows ``decision_id`` to be
  empty when the resolver admits from the request context). Limits must be
  present (request-declared or composition default); a run with no limits is
  not admitted and fails closed.
"""

from typing import Any

from sqlalchemy import Engine

from zuno.agent.contracts import BudgetDecisionRef, SecurityDecisionRef
from zuno.agent.runtime.owner_refs import (
    budget_ref_hash,
    security_ref_hash,
)
from zuno.platform.security import SecurityUnitOfWork

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
    """Security-owner fact resolver backed by the PostgreSQL security tables.

    ``security_epoch_ref``: the epoch this composition currently certifies.
    Owner facts recorded under a different epoch fail closed as stale at
    Agent Core validation (never downgraded here).
    """

    def __init__(self, engine: Engine, security_epoch_ref: str = "") -> None:
        self._engine = engine
        self._bound_epoch = str(security_epoch_ref or "").strip()

    def resolve(self, decision_id: str, context: dict[str, Any]) -> dict[str, Any] | None:
        if not decision_id:
            return None
        tenant_id = str(context.get("tenant_id") or "").strip()
        if not tenant_id:
            return None
        with SecurityUnitOfWork(self._engine) as repo:
            fact = repo.read_authorization_decision_fact(
                decision_id=decision_id,
                tenant_id=tenant_id,
            )
        if not fact:
            return None
        if str(fact.get("epoch_status") or "").strip() != "active":
            # The owner epoch is not active: there is no current owner fact.
            return None
        workspace_id = _workspace_from_principal_context_id(
            str(fact.get("principal_context_id") or "")
        )
        if not workspace_id:
            return None
        principal_id = str(fact.get("user_principal_id") or "").strip() or str(
            context.get("principal_id") or ""
        ).strip()
        action = str(fact.get("action") or "tool.execute").strip()
        resource = str(fact.get("resource_ref") or "").strip()
        decision = str(fact.get("decision") or "").strip()
        epoch_ref = str(fact.get("epoch_ref") or "").strip()
        if not (principal_id and resource and decision and epoch_ref):
            return None
        decision_hash = security_ref_hash(
            decision_id=decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=principal_id,
            action=action,
            resource=resource,
            decision=decision,
            security_epoch_ref=epoch_ref,
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
            expires_at=None,
        ).to_dict()


class PostgresBudgetDecisionResolver:
    """Budget-owner resolver: formal Budget Admission from request context.

    ``decision_id`` may be empty — the runtime contract allows the resolver
    to admit from the request context. Limits must resolve (request-declared
    ``budget_limits`` first, then the composition default); a run without any
    limits is not admitted (``None``) and fails closed as
    ``missing_budget_decision_ref``. The owner identity is the formal budget
    admission owner — the adapter never self-attests.
    """

    def __init__(self, default_limits: dict[str, Any] | None = None) -> None:
        self._default_limits = dict(default_limits or {})

    def resolve(self, decision_id: str, context: dict[str, Any]) -> dict[str, Any] | None:
        tenant_id = str(context.get("tenant_id") or "").strip()
        workspace_id = str(context.get("workspace_id") or "").strip()
        run_id = str(context.get("run_id") or "").strip()
        if not (tenant_id and workspace_id and run_id):
            return None
        limits = dict(context.get("budget_limits") or {}) or dict(self._default_limits)
        if not limits:
            return None
        admitted_decision_id = str(decision_id or "").strip() or f"budget-admission:{run_id}"
        ref = BudgetDecisionRef(
            budget_decision_id=admitted_decision_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            run_id=run_id,
            allowed=True,
            limits=limits,
            owner=BUDGET_OWNER,
            decision_hash="",
        )
        return BudgetDecisionRef(
            **{**ref.model_dump(), "decision_hash": budget_ref_hash(ref=ref)}
        ).to_dict()


__all__ = [
    "BUDGET_OWNER",
    "PostgresBudgetDecisionResolver",
    "PostgresSecurityDecisionResolver",
]
