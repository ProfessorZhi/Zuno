from __future__ import annotations

from zuno.platform.security import (
    SecurityProductActionDenied,
    SecurityProductActionGuard,
    SecurityProductActionRequest,
    build_product_action_hash,
)


_security_product_action_guard: SecurityProductActionGuard | None = None


def configure_security_admin_action_guard(
    guard: SecurityProductActionGuard | None,
) -> None:
    global _security_product_action_guard
    _security_product_action_guard = guard


def require_admin_action_authorized(
    *,
    principal_id: str,
    action: str,
    resource_ref: str,
) -> None:
    if _security_product_action_guard is None:
        return
    tenant_id = "system"
    workspace_id = "system"
    request = SecurityProductActionRequest(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        principal_id=principal_id,
        action=action,
        resource_ref=resource_ref,
        decision_id=f"authorization-decision:{action}:{principal_id}:{resource_ref}",
        prepared_action_hash=build_product_action_hash(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            principal_id=principal_id,
            action=action,
            resource_ref=resource_ref,
        ),
    )
    try:
        _security_product_action_guard.require_authorized_action(request)
    except SecurityProductActionDenied as exc:
        raise ValueError(str(exc) or "Security authorization denied") from exc


__all__ = [
    "configure_security_admin_action_guard",
    "require_admin_action_authorized",
]
