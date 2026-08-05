from __future__ import annotations

"""Security / Budget owner-decision reference verification (PHASE22 repair).

The Product Adapter may only carry immutable owner decision refs
(:class:`SecurityDecisionRef` / :class:`BudgetDecisionRef`); Agent Core must
verify the owner fact before any tool step. Verification is deterministic and
fail-closed:

- missing ref when a decision is required
- tenant / workspace / principal scope mismatch
- stale security epoch
- decision hash mismatch (forged ref)
- unknown / denied decision
- budget owner missing

A raw caller-provided ``security_summary`` / ``budget_verdict`` dict is never
treated as an owner decision by the runtime.
"""

from dataclasses import dataclass
from typing import Any

from zuno.agent.contracts import BudgetDecisionRef, SecurityDecisionRef
from zuno.platform.contracts import canonical_sha256


@dataclass(frozen=True, slots=True)
class OwnerRefVerification:
    allowed: bool
    reason: str = ""


def security_ref_hash(
    *,
    decision_id: str,
    tenant_id: str,
    workspace_id: str,
    principal_id: str,
    action: str,
    resource: str,
    decision: str,
    security_epoch_ref: str,
) -> str:
    """Deterministic decision hash over the owner-issued fact fields."""
    return canonical_sha256(
        {
            "decision_id": decision_id,
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "principal_id": principal_id,
            "action": action,
            "resource": resource,
            "decision": decision,
            "security_epoch_ref": security_epoch_ref,
        }
    )


def validate_security_decision_ref(
    ref: SecurityDecisionRef | None,
    *,
    tenant_id: str,
    workspace_id: str,
    principal_id: str,
    action: str,
    resource: str,
    bound_security_epoch_ref: str,
    required: bool,
) -> OwnerRefVerification:
    """Verify a Security-owner decision ref; fail closed on every mismatch."""
    if ref is None:
        if required:
            return OwnerRefVerification(False, "missing_security_decision_ref")
        return OwnerRefVerification(True, "no_security_decision_required")

    if ref.tenant_id != tenant_id:
        return OwnerRefVerification(False, "security_ref_tenant_mismatch")
    if ref.workspace_id != workspace_id:
        return OwnerRefVerification(False, "security_ref_workspace_mismatch")
    if ref.principal_id != principal_id:
        return OwnerRefVerification(False, "security_ref_principal_mismatch")
    if ref.action != action:
        return OwnerRefVerification(False, "security_ref_action_mismatch")
    if ref.security_epoch_ref != bound_security_epoch_ref:
        return OwnerRefVerification(False, "stale_security_epoch")
    expected_hash = security_ref_hash(
        decision_id=ref.decision_id,
        tenant_id=ref.tenant_id,
        workspace_id=ref.workspace_id,
        principal_id=ref.principal_id,
        action=ref.action,
        resource=ref.resource,
        decision=ref.decision,
        security_epoch_ref=ref.security_epoch_ref,
    )
    if ref.decision_hash != expected_hash:
        return OwnerRefVerification(False, "security_ref_hash_mismatch")

    normalized = str(ref.decision or "").lower()
    if normalized in {"deny", "denied", "block", "blocked", "refuse", "refused"}:
        return OwnerRefVerification(False, "security_decision_denied")
    if normalized in {"", "unknown", "not_found", "missing"}:
        # A present ref whose decision is absent / not an owner-issued verdict
        # must not be treated as an allow.
        return OwnerRefVerification(False, "security_decision_not_found")
    return OwnerRefVerification(True, "security_decision_allowed")


def budget_ref_hash(*, ref: BudgetDecisionRef) -> str:
    return canonical_sha256(
        {
            "budget_decision_id": ref.budget_decision_id,
            "tenant_id": ref.tenant_id,
            "workspace_id": ref.workspace_id,
            "run_id": ref.run_id,
            "allowed": ref.allowed,
            "limits": ref.limits,
            "owner": ref.owner,
        }
    )


def validate_budget_decision_ref(
    ref: BudgetDecisionRef | None,
    *,
    tenant_id: str,
    workspace_id: str,
    run_id: str,
    required: bool,
) -> OwnerRefVerification:
    """Verify a Budget-owner decision ref; fail closed on every mismatch."""
    if ref is None:
        if required:
            return OwnerRefVerification(False, "missing_budget_decision_ref")
        return OwnerRefVerification(True, "no_budget_decision_required")

    if ref.tenant_id != tenant_id:
        return OwnerRefVerification(False, "budget_ref_tenant_mismatch")
    if ref.workspace_id != workspace_id:
        return OwnerRefVerification(False, "budget_ref_workspace_mismatch")
    if run_id and ref.run_id and ref.run_id != run_id:
        return OwnerRefVerification(False, "budget_ref_run_mismatch")
    if not ref.owner.strip():
        return OwnerRefVerification(False, "budget_owner_not_found")
    if ref.decision_hash != budget_ref_hash(ref=ref):
        return OwnerRefVerification(False, "budget_ref_hash_mismatch")
    if not ref.allowed:
        return OwnerRefVerification(False, "budget_decision_denied")
    return OwnerRefVerification(True, "budget_decision_allowed")


def resolve_security_ref(raw: dict[str, Any] | None) -> SecurityDecisionRef | None:
    if not raw:
        return None
    return SecurityDecisionRef(**raw)


def resolve_budget_ref(raw: dict[str, Any] | None) -> BudgetDecisionRef | None:
    if not raw:
        return None
    return BudgetDecisionRef(**raw)


__all__ = [
    "BudgetDecisionRef",
    "OwnerRefVerification",
    "SecurityDecisionRef",
    "budget_ref_hash",
    "resolve_budget_ref",
    "resolve_security_ref",
    "security_ref_hash",
    "validate_budget_decision_ref",
    "validate_security_decision_ref",
]
