from __future__ import annotations

"""In-memory fakes of the Tool / Security / Infrastructure UoW repositories
used by ``ToolInvocationGateway`` (PHASE22 workspace cutover tests).

These are test doubles ONLY — the product path requires the real PostgreSQL
UoWs from the server composition root; SQLite / in-memory persistence is
limited to the explicit developer test profile. They implement just the
repository surface the gateway touches, so fail-closed semantics
(SIDE_EFFECT_GATEWAY_NOT_BOUND, approval gating, idempotency replay,
effect receipts, reconciliation) can be verified without a live Postgres.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from zuno.platform.database.foundation import FencingToken, IdempotencyClaimReceipt
from zuno.platform.security import SecurityPersistenceError


@dataclass(frozen=True, slots=True)
class _FakeIdempotencyRecord:
    status: str  # in_progress | completed
    generation: int
    owner: str
    result_ref: str = ""


@dataclass(slots=True)
class FakeInfrastructureRepository:
    _claims: dict[tuple[str, str], _FakeIdempotencyRecord] = field(default_factory=dict)

    def claim_idempotency_receipt(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        request: dict[str, Any],
        ttl_seconds: int = 60,
    ) -> IdempotencyClaimReceipt:
        existing = self._claims.get((scope, key))
        if existing is not None:
            return IdempotencyClaimReceipt(
                status=existing.status,
                generation=existing.generation,
                result_ref=existing.result_ref,
                owner=existing.owner,
                acquired=False,
            )
        self._claims[(scope, key)] = _FakeIdempotencyRecord(
            status="in_progress",
            generation=1,
            owner=owner,
        )
        return IdempotencyClaimReceipt(
            status="in_progress",
            generation=1,
            result_ref="",
            owner=owner,
            acquired=True,
        )

    def complete_idempotency(
        self,
        *,
        scope: str,
        key: str,
        owner: str,
        generation: int,
        result_ref: str,
    ) -> None:
        record = self._claims.get((scope, key))
        if record is None or record.owner != owner or record.generation != generation:
            return
        self._claims[(scope, key)] = _FakeIdempotencyRecord(
            status="completed",
            generation=generation,
            owner=owner,
            result_ref=result_ref,
        )

    def acquire_lease(self, *, resource_id: str, owner_id: str, ttl_seconds: int = 30) -> FencingToken:
        return FencingToken(
            resource_id=resource_id,
            owner_id=owner_id,
            lease_id=f"fake-lease:{resource_id}:{owner_id}",
            epoch=1,
            expires_at=None,
        )

    def assert_fence(self, token: FencingToken, *, clock_tolerance_seconds: float = 0) -> None:
        return None

    def completed_result_ref(self, *, scope: str, key: str) -> str:
        record = self._claims.get((scope, key))
        if record is not None and record.status == "completed":
            return record.result_ref
        return ""


@dataclass(slots=True)
class FakeInfrastructureUnitOfWork:
    _repo: FakeInfrastructureRepository = field(default_factory=FakeInfrastructureRepository)

    def __enter__(self) -> FakeInfrastructureRepository:
        return self._repo

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


@dataclass(slots=True)
class FakeSecurityRepository:
    _approved_calls: set[str] = field(default_factory=set)
    _epochs: dict[str, str] = field(default_factory=dict)
    _secret_leases: set[str] = field(default_factory=set)

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
    ) -> None:
        self._epochs[epoch_ref] = tenant_id

    def ensure_principal_context(self, **_: Any) -> None:
        return None

    def ensure_authorization_decision(self, **_: Any) -> None:
        return None

    def ensure_approval_request(self, **_: Any) -> None:
        return None

    def ensure_approval_decision(self, *, approval_decision_id: str, **_: Any) -> None:
        self._approved_calls.add(approval_decision_id)

    def ensure_audit_requirement(self, **_: Any) -> None:
        return None

    def validate_pre_effect_authorization(
        self,
        *,
        decision_id: str,
        tenant_id: str,
        prepared_action_hash: str,
        require_approved_request: bool,
    ) -> None:
        # Deterministic fake: an approval-required action needs its approval
        # decision (keyed by the gateway's per-call approval decision id)
        # recorded; otherwise the pre-effect authorization fails closed.
        if require_approved_request:
            call_id = str(decision_id or "").removeprefix("authorization-decision:")
            if not call_id or f"approval-decision:{call_id}" not in self._approved_calls:
                raise SecurityPersistenceError("authorization decision not approved")

    def record_secret_ref(self, **_: Any) -> None:
        return None

    def issue_secret_lease(self, *, lease_id: str, **_: Any) -> None:
        self._secret_leases.add(lease_id)

    def validate_secret_lease(self, *, lease_id: str, audience: str, **_: Any) -> None:
        if lease_id not in self._secret_leases:
            raise SecurityPersistenceError(f"secret lease not issued: {lease_id}")


@dataclass(slots=True)
class FakeSecurityUnitOfWork:
    _repo: FakeSecurityRepository = field(default_factory=FakeSecurityRepository)

    def __enter__(self) -> FakeSecurityRepository:
        return self._repo

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


@dataclass(slots=True)
class FakeToolRepository:
    _prepared_actions: dict[str, dict[str, Any]] = field(default_factory=dict)
    _effect_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    _execution_receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    _reconciliations: list[str] = field(default_factory=list)
    _sandbox_sessions: dict[str, dict[str, Any]] = field(default_factory=dict)

    def publish_tool_version(self, *args: Any, **_: Any) -> None:
        return None

    def record_adapter_binding(self, *args: Any, **_: Any) -> None:
        return None

    def install_tool(self, *args: Any, **_: Any) -> None:
        return None

    def activate_tool(self, *args: Any, **_: Any) -> None:
        return None

    def prepare_action(self, prepared: Any) -> str:
        self._prepared_actions[prepared.prepared_tool_action_id] = (
            prepared.model_dump(mode="json")
            if hasattr(prepared, "model_dump")
            else asdict(prepared)
        )
        return prepared.prepared_tool_action_id

    def record_attempt(self, *args: Any, **_: Any) -> None:
        return None

    def record_observation(self, *args: Any, **_: Any) -> None:
        return None

    def record_execution_receipt(self, receipt: Any) -> None:
        self._execution_receipts[receipt.receipt_id] = (
            receipt.model_dump(mode="json") if hasattr(receipt, "model_dump") else asdict(receipt)
        )

    def update_execution_receipt(self, receipt: Any) -> None:
        self._execution_receipts[receipt.receipt_id] = (
            receipt.model_dump(mode="json") if hasattr(receipt, "model_dump") else asdict(receipt)
        )

    def record_effect_receipt(self, receipt: Any) -> None:
        self._effect_receipts[receipt.effect_receipt_id] = (
            receipt.model_dump(mode="json") if hasattr(receipt, "model_dump") else asdict(receipt)
        )

    def record_effect_reconciliation(self, reconciliation: Any) -> None:
        self._reconciliations.append(
            reconciliation.reconciliation_id
            if hasattr(reconciliation, "reconciliation_id")
            else str(reconciliation)
        )

    def record_async_job(self, *args: Any, **_: Any) -> None:
        return None

    def record_sandbox_session(self, session: Any) -> None:
        self._sandbox_sessions[session.session_ref] = asdict(session)

    def get_sandbox_session(self, session_ref: str) -> dict[str, Any] | None:
        return self._sandbox_sessions.get(session_ref)

    def record_sandbox_receipt(self, *args: Any, **_: Any) -> None:
        return None

    def record_bypass_guard(self, *args: Any, **_: Any) -> None:
        return None

    def existing_side_effect_result_ref(self, *, tenant_id: str, call_id: str) -> str:
        return self._execution_receipts.get(f"tool-execution-receipt:{call_id}", {}).get("result_ref", "")


@dataclass(slots=True)
class FakeToolUnitOfWork:
    _repo: FakeToolRepository = field(default_factory=FakeToolRepository)

    def __enter__(self) -> FakeToolRepository:
        return self._repo

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


@dataclass(frozen=True, slots=True)
class FakeGatewayBinding:
    """The three UoW factories the gateway requires, backed by in-memory fakes."""

    tool_unit_of_work: FakeToolUnitOfWork = field(default_factory=FakeToolUnitOfWork, kw_only=True)
    security_unit_of_work: FakeSecurityUnitOfWork = field(default_factory=FakeSecurityUnitOfWork, kw_only=True)
    infrastructure_unit_of_work: FakeInfrastructureUnitOfWork = field(
        default_factory=FakeInfrastructureUnitOfWork, kw_only=True
    )

    def tool_factory(self) -> FakeToolUnitOfWork:
        return self.tool_unit_of_work

    def security_factory(self) -> FakeSecurityUnitOfWork:
        return self.security_unit_of_work

    def infrastructure_factory(self, tenant_id: str) -> FakeInfrastructureUnitOfWork:
        return self.infrastructure_unit_of_work

    def approve(self, *, call_id: str) -> None:
        """Record the approval decision the gateway requires pre-effect."""
        self.security_unit_of_work._repo._approved_calls.add(f"approval-decision:{call_id}")
