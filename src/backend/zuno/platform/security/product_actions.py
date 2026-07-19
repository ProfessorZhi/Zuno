from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import Engine

from zuno.platform.contracts import canonical_sha256
from zuno.platform.security.persistence import SecurityUnitOfWork


class SecurityProductActionDenied(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SecurityProductActionRequest:
    tenant_id: str
    workspace_id: str
    principal_id: str
    action: str
    resource_ref: str
    decision_id: str
    prepared_action_hash: str


class SecurityProductActionGuard(Protocol):
    def require_authorized_action(self, request: SecurityProductActionRequest) -> None:
        ...


class PostgresSecurityProductActionGuard:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def require_authorized_action(self, request: SecurityProductActionRequest) -> None:
        with SecurityUnitOfWork(self.engine) as repo:
            try:
                repo.validate_pre_effect_authorization(
                    decision_id=request.decision_id,
                    tenant_id=request.tenant_id,
                    prepared_action_hash=request.prepared_action_hash,
                )
            except Exception as exc:
                raise SecurityProductActionDenied(str(exc)) from exc


def build_product_action_hash(
    *,
    tenant_id: str,
    workspace_id: str,
    principal_id: str,
    action: str,
    resource_ref: str,
) -> str:
    return canonical_sha256(
        {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "principal_id": principal_id,
            "action": action,
            "resource_ref": resource_ref,
        }
    )


__all__ = [
    "PostgresSecurityProductActionGuard",
    "SecurityProductActionDenied",
    "SecurityProductActionGuard",
    "SecurityProductActionRequest",
    "build_product_action_hash",
]
