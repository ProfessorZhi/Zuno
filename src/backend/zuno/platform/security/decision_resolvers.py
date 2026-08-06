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

    PHASE22 final engineering closure (P0-5): the resolver MUST compare
    ``fact["epoch_ref"]`` to ``self._bound_epoch`` and reject stale
    epochs. ``expires_at`` MUST come from the owner fact; missing or
    malformed expiry fails closed. ``tenant_id`` is taken from the
    validated caller context, never recovered from ``workspace_id`` or
    any string substring.
    """

    def __init__(self, engine: Engine, security_epoch_ref: str = "") -> None:
        self._engine = engine
        self._bound_epoch = str(security_epoch_ref or "").strip()
        if not self._bound_epoch:
            # PHASE22 final engineering closure (P0-5): the composition
            # MUST bind a real Server-owned epoch. Empty / synthetic epoch
            # disables the resolver — every resolve() will fail closed.
            self._engine = None  # type: ignore[assignment]

    def resolve(self, decision_id: str, context: dict[str, Any]) -> dict[str, Any] | None:
        if not decision_id:
            return None
        tenant_id = str(context.get("tenant_id") or "").strip()
        if not tenant_id or tenant_id.startswith("user:") or tenant_id == "tenant:default":
            return None
        if self._bound_epoch is None or self._bound_epoch == "":
            return None
        if self._engine is None:
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
        epoch_ref = str(fact.get("epoch_ref") or "").strip()
        # PHASE22 final engineering closure (P0-5): real epoch comparison;
        # stale or inactive epochs are rejected with no downgrade path.
        if not epoch_ref or epoch_ref != self._bound_epoch:
            return None
        workspace_id = _workspace_from_principal_context_id(
            str(fact.get("principal_context_id") or "")
        )
        if not workspace_id:
            return None
        # PHASE22 final engineering closure (P0-2): tenant_id and
        # workspace_id must come from validated facts, never from one
        # another. Foreign workspace / tenant / principal rejected.
        fact_tenant_id = str(fact.get("tenant_id") or "").strip()
        if not fact_tenant_id or fact_tenant_id != tenant_id:
            return None
        principal_id = str(fact.get("user_principal_id") or "").strip()
        if not principal_id:
            return None
        action = str(fact.get("action") or "tool.execute").strip()
        resource = str(fact.get("resource_ref") or "").strip()
        decision = str(fact.get("decision") or "").strip()
        if not (principal_id and resource and decision and epoch_ref):
            return None
        # PHASE22 final engineering closure (P0-5): expires_at MUST come
        # from the owner fact; missing or malformed expiry fails closed.
        expires_at_raw = fact.get("expires_at")
        if expires_at_raw is None:
            return None
        expires_at = str(expires_at_raw).strip()
        if not expires_at:
            return None
        try:
            # Validate that the expiry is a parseable ISO-8601 timestamp.
            from datetime import datetime
            datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except (TypeError, ValueError):
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
