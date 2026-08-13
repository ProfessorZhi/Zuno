from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from zuno.platform.contracts import canonical_sha256


class MutationResultStatus(StrEnum):
    COMMITTED = "COMMITTED"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    REJECTED = "REJECTED"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class DomainMutationCommand(BaseModel):
    """A version-guarded proposal admission command.

    This is deliberately a proposal contract.  It does not expose a generic
    ``write_fact`` operation; only the Domain Owner's admission service can
    turn it into a canonical version.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mutation_id: str = Field(min_length=1, max_length=220)
    matter_id: str = Field(min_length=1, max_length=220)
    tenant_id: str = Field(min_length=1, max_length=180)
    scope_ref: str = Field(min_length=1, max_length=240)
    expected_domain_version: int = Field(ge=0)
    proposal: dict[str, Any] = Field(default_factory=dict)
    proposal_reference: str | None = Field(default=None, max_length=512)
    mutation_type: str = Field(min_length=1, max_length=160)
    principal_ref: str = Field(min_length=1, max_length=220)
    idempotency_key: str = Field(min_length=1, max_length=240)
    correlation_id: str = Field(min_length=1, max_length=240)
    causation_ref: str | None = Field(default=None, max_length=512)
    security_context_ref: str = Field(min_length=1, max_length=512)

    @field_validator(
        "mutation_id",
        "matter_id",
        "tenant_id",
        "scope_ref",
        "proposal_reference",
        "mutation_type",
        "principal_ref",
        "idempotency_key",
        "correlation_id",
        "causation_ref",
        "security_context_ref",
        mode="before",
    )
    @classmethod
    def _strip_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    def semantic_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        for field_name in ("mutation_id", "idempotency_key", "correlation_id", "causation_ref"):
            payload.pop(field_name, None)
        return payload

    def request_hash(self) -> str:
        return canonical_sha256(self.semantic_payload())


class AuthorizationDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    allowed: bool
    reason_code: str = "allowed"
    authorization_ref: str | None = None


class DomainMutationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    mutation_id: str
    matter_id: str
    tenant_id: str
    status: MutationResultStatus
    result_ref: str
    reason_code: str
    domain_version_before: int
    domain_version_after: int
    committed_version_ref: str | None = None
    trace_ref: str
    audit_ref: str
    replayed: bool = False


class CanonicalDomainMutationStore(Protocol):
    def commit_mutation(
        self,
        command: DomainMutationCommand,
        *,
        request_hash: str,
        before_commit: Callable[[], None] | None = None,
    ) -> DomainMutationResult: ...


MutationAuthorizer = Callable[[DomainMutationCommand], AuthorizationDecision | bool]
MutationAuditSink = Callable[[Mapping[str, Any]], None]


class AllowAllMutationAuthorizer:
    """Explicit test/dev authorizer; production callers must inject policy."""

    def __call__(self, command: DomainMutationCommand) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            authorization_ref=command.security_context_ref,
        )


class CanonicalDomainMutationService:
    """The only application boundary allowed to admit canonical domain state."""

    def __init__(
        self,
        store: CanonicalDomainMutationStore,
        *,
        authorizer: MutationAuthorizer | None,
        audit_sink: MutationAuditSink | None = None,
    ) -> None:
        self.store = store
        self.authorizer = authorizer
        self.audit_sink = audit_sink

    def submit(
        self,
        command: DomainMutationCommand,
        *,
        before_commit: Callable[[], None] | None = None,
    ) -> DomainMutationResult:
        if not command.proposal and not command.proposal_reference:
            return self._finish(
                self._non_committing_result(
                    command,
                    MutationResultStatus.VALIDATION_FAILED,
                    "proposal_missing",
                )
            )

        if self.authorizer is None:
            return self._finish(
                self._non_committing_result(
                    command,
                    MutationResultStatus.AUTHORIZATION_FAILED,
                    "mutation_authorizer_missing",
                )
            )

        decision = self.authorizer(command)
        if isinstance(decision, bool):
            decision = AuthorizationDecision(
                allowed=decision,
                reason_code="allowed" if decision else "authorization_denied",
                authorization_ref=command.security_context_ref,
            )
        if not decision.allowed:
            return self._finish(
                self._non_committing_result(
                    command,
                    MutationResultStatus.AUTHORIZATION_FAILED,
                    decision.reason_code or "authorization_denied",
                )
            )

        result = self.store.commit_mutation(
            command,
            request_hash=command.request_hash(),
            before_commit=before_commit,
        )
        return self._finish(result)

    def _finish(self, result: DomainMutationResult) -> DomainMutationResult:
        if self.audit_sink is not None:
            self.audit_sink(
                {
                    "mutation_id": result.mutation_id,
                    "matter_id": result.matter_id,
                    "tenant_id": result.tenant_id,
                    "status": result.status.value,
                    "reason_code": result.reason_code,
                    "domain_version_before": result.domain_version_before,
                    "domain_version_after": result.domain_version_after,
                    "trace_ref": result.trace_ref,
                    "audit_ref": result.audit_ref,
                    "replayed": result.replayed,
                }
            )
        return result

    @staticmethod
    def _non_committing_result(
        command: DomainMutationCommand,
        status: MutationResultStatus,
        reason_code: str,
    ) -> DomainMutationResult:
        result_ref = f"domain-mutation-result:{command.mutation_id}:{status.value}"
        return DomainMutationResult(
            mutation_id=command.mutation_id,
            matter_id=command.matter_id,
            tenant_id=command.tenant_id,
            status=status,
            result_ref=result_ref,
            reason_code=reason_code,
            domain_version_before=command.expected_domain_version,
            domain_version_after=command.expected_domain_version,
            trace_ref=f"trace:domain-mutation:{command.correlation_id}",
            audit_ref=f"audit:domain-mutation:{command.mutation_id}",
        )


__all__ = [
    "AllowAllMutationAuthorizer",
    "AuthorizationDecision",
    "CanonicalDomainMutationService",
    "CanonicalDomainMutationStore",
    "DomainMutationCommand",
    "DomainMutationResult",
    "MutationAuditSink",
    "MutationAuthorizer",
    "MutationResultStatus",
]
