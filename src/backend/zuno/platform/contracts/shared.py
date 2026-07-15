from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from zuno.platform.contracts.canonical import canonical_sha256


class StrictContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, use_enum_values=True)


class ContractRef(StrictContract):
    ref: str
    schema_hash: str | None = None


class PrincipalContextRefV1(StrictContract):
    principal_context_ref: str
    tenant_id: str
    principal_id: str
    principal_type: Literal["USER", "SERVICE", "SYSTEM"]
    issued_at: datetime
    expires_at: datetime | None = None


class SecurityContextRefV1(StrictContract):
    security_context_ref: str
    tenant_id: str
    workspace_id: str | None = None
    principal_context_ref: str
    scope_hash: str
    classification: str
    issued_at: datetime


class EffectiveSecurityEpochRefV1(StrictContract):
    effective_security_epoch_ref: str
    tenant_id: str
    workspace_id: str | None = None
    principal_context_ref: str | None = None
    resource_scope_ref: str | None = None
    tenant_epoch: int
    workspace_epoch: int | None = None
    principal_epoch: int | None = None
    resource_epoch: int | None = None
    policy_version_ref: str
    epoch_hash: str
    issued_at: datetime
    expires_at: datetime | None = None


class SecurityApprovalDecisionV1(StrictContract):
    approval_decision_ref: str
    prepared_tool_action_id: str
    prepared_action_hash: str
    principal_id: str
    tenant_id: str
    workspace_id: str | None = None
    tool_definition_ref: str
    operation: str
    canonical_args_hash: str
    policy_snapshot_ref: str
    effective_security_epoch_hash: str
    approval_policy_id: str
    approver_principal_ids: tuple[str, ...]
    expires_at: datetime
    nonce: str
    consumption_mode: Literal["SINGLE_USE", "MULTI_USE_UNTIL_EXPIRY"] = "SINGLE_USE"
    decision: Literal["APPROVED", "DENIED", "EXPIRED", "REVOKED"]


class AuditPersistenceReceiptV1(StrictContract):
    audit_persistence_receipt_id: str
    source_event_ref: str
    audit_requirement_ref: str
    local_commit_ref: str
    outbox_ref: str | None = None
    integrity_chain_ref: str
    persisted_at: datetime
    status: Literal["COMMITTED", "DUPLICATE", "FAILED"]


class CrossModuleEnvelopeV1(StrictContract):
    contract_name: str
    contract_version: str
    contract_bundle_version: str
    message_id: str
    producer_module: str
    consumer_module: str
    tenant_id: str
    workspace_id: str | None = None
    run_id: str | None = None
    step_run_id: str | None = None
    correlation_id: str
    causation_id: str | None = None
    idempotency_key: str | None = None
    aggregate_type: str | None = None
    aggregate_id: str | None = None
    aggregate_version: int | None = None
    expected_generation: int | None = None
    effective_security_epoch_ref: str | None = None
    effective_security_epoch_hash: str | None = None
    principal_context_ref: str | None = None
    security_context_ref: str | None = None
    authorization_decision_ref: str | None = None
    deadline_at: datetime | None = None
    trace_id: str
    data_classification: str
    redaction_decision_ref: str | None = None
    audit_requirement_ref: str | None = None
    occurred_at: datetime
    created_at: datetime
    payload: dict[str, Any] | None = None
    payload_ref: str | None = None
    payload_hash: str
    payload_schema_hash: str

    @model_validator(mode="after")
    def _payload_boundary(self) -> "CrossModuleEnvelopeV1":
        if (self.payload is None) == (self.payload_ref is None):
            raise ValueError("exactly one of payload or payload_ref must be present")
        if self.payload is not None and canonical_sha256(self.payload) != self.payload_hash:
            raise ValueError("payload_hash does not match canonical payload")
        return self


class FailureOwner(StrEnum):
    SECURITY = "SECURITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MODEL_GATEWAY = "MODEL_GATEWAY"
    OBSERVABILITY = "OBSERVABILITY"
    TOOL_RUNTIME = "TOOL_RUNTIME"
    KNOWLEDGE = "KNOWLEDGE"
    MEMORY = "MEMORY"
    AGENT_CORE = "AGENT_CORE"


_PREFIX_BY_OWNER = {
    FailureOwner.SECURITY: "SEC_",
    FailureOwner.INFRASTRUCTURE: "INFRA_",
    FailureOwner.MODEL_GATEWAY: "MODEL_",
    FailureOwner.OBSERVABILITY: "OBS_",
    FailureOwner.TOOL_RUNTIME: "TOOL_",
    FailureOwner.KNOWLEDGE: "KNOW_",
    FailureOwner.MEMORY: "MEM_",
    FailureOwner.AGENT_CORE: "AGENT_",
}


class FailureCodeV1(StrictContract):
    code: str
    owner: FailureOwner
    retryable: bool = False
    recovery_owner: FailureOwner
    requires_reconcile: bool = False
    user_visible: bool = False

    @model_validator(mode="after")
    def _owner_prefix(self) -> "FailureCodeV1":
        expected = _PREFIX_BY_OWNER[self.owner]
        if not self.code.startswith(expected):
            raise ValueError(f"failure code {self.code} does not match owner prefix {expected}")
        return self


class ModelUsageReceiptV1(StrictContract):
    usage_receipt_id: str
    receipt_version: int = Field(ge=1)
    model_call_id: str
    attempt_id: str
    provider_request_ref: str | None = None
    usage_kind: Literal["ESTIMATED", "OBSERVED", "SETTLED", "CORRECTION"]
    input_units: float = Field(ge=0)
    output_units: float = Field(ge=0)
    cost_amount: float | None = Field(default=None, ge=0)
    currency: str | None = None
    pricing_version_ref: str | None = None
    supersedes_receipt_ref: str | None = None
    observed_at: datetime
    idempotency_key: str


class IndexWriteBatchV1(StrictContract):
    batch_id: str
    build_run_id: str
    owner_module: Literal["KNOWLEDGE", "MEMORY"]
    tenant_id: str
    workspace_id: str
    index_kind: Literal["VECTOR", "GRAPH", "LEXICAL"]
    target_version: str
    source_snapshot_ref: str
    item_identity_scheme: str
    item_count: int = Field(ge=0)
    payload_ref: str
    payload_hash: str
    schema_spec_ref: str
    idempotency_key: str
    expected_generation: int
    effective_security_epoch_ref: str
    deadline_at: datetime


class IndexWriteReceiptV1(StrictContract):
    receipt_id: str
    batch_id: str
    physical_target_ref: str
    attempt_no: int = Field(ge=1)
    accepted_count: int = Field(ge=0)
    rejected_count: int = Field(ge=0)
    observed_generation: int
    service_commit_ref: str | None = None
    checksum_or_digest: str | None = None
    status: Literal["COMMITTED", "PARTIAL", "DUPLICATE", "FAILED", "UNKNOWN"]


class WriteVisibilityReceiptV1(StrictContract):
    receipt_id: str
    write_receipt_ref: str
    consistency_class: Literal["IMMEDIATE", "READ_YOUR_WRITE", "BOUNDED_EVENTUAL", "EVENTUAL"]
    visible_at: datetime | None = None
    visibility_deadline_at: datetime
    serving_watermark_ref: str | None = None
    status: Literal["PENDING", "VISIBLE", "DEADLINE_EXCEEDED", "FAILED"]


class ActionProposalV1(StrictContract):
    action_proposal_id: str
    run_id: str
    step_run_id: str
    proposed_capability_ref: str
    proposed_operation: str
    proposed_args_ref: str
    proposed_args_hash: str
    expected_result_contract_ref: str
    side_effect_class: str
    proposal_source_ref: str
    status: Literal["PROPOSED", "REJECTED", "BOUND", "OBSOLETE"]


class ActionExecutionBindingV1(StrictContract):
    action_execution_binding_id: str
    action_proposal_ref: str
    prepared_tool_action_ref: str
    run_id: str
    plan_version_ref: str
    step_run_id: str
    control_state: Literal["BOUND", "WAITING", "COMPLETED", "OBSOLETE"]


class PreparedToolActionV1(StrictContract):
    prepared_tool_action_id: str
    action_proposal_ref: str
    tenant_id: str
    workspace_id: str
    principal_context_ref: str
    tool_definition_ref: str
    tool_definition_version: str
    operation: str
    canonical_args_ref: str
    canonical_args_hash: str
    target_resource_refs_hash: str
    side_effect_class: str
    credential_scope_ref: str | None = None
    idempotency_scope: str
    policy_snapshot_ref: str
    effective_security_epoch_ref: str
    effective_security_epoch_hash: str
    deadline_at: datetime
    canonical_hash_version: str
    prepared_action_hash: str
    status: Literal["PREPARED", "WAITING_APPROVAL", "AUTHORIZED", "EXECUTING", "TERMINAL", "OBSOLETE"]

    def hash_inputs(self) -> dict[str, Any]:
        return {
            "canonical_hash_version": self.canonical_hash_version,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "principal_context_ref": self.principal_context_ref,
            "tool_definition_ref": self.tool_definition_ref,
            "tool_definition_version": self.tool_definition_version,
            "operation": self.operation,
            "canonical_args_hash": self.canonical_args_hash,
            "target_resource_refs_hash": self.target_resource_refs_hash,
            "side_effect_class": self.side_effect_class,
            "credential_scope_ref": self.credential_scope_ref,
            "idempotency_scope": self.idempotency_scope,
            "policy_snapshot_ref": self.policy_snapshot_ref,
            "effective_security_epoch_hash": self.effective_security_epoch_hash,
            "deadline_at": self.deadline_at.isoformat().replace("+00:00", "Z"),
        }

    @model_validator(mode="after")
    def _hash_matches(self) -> "PreparedToolActionV1":
        if canonical_sha256(self.hash_inputs()) != self.prepared_action_hash:
            raise ValueError("prepared_action_hash does not match canonical hash inputs")
        return self


class ToolObservationV1(StrictContract):
    tool_observation_id: str
    prepared_tool_action_ref: str
    attempt_ref: str | None = None
    status: Literal["OBSERVED", "FAILED", "BLOCKED", "UNKNOWN"]
    summary: str
    payload_ref: str | None = None
    payload_hash: str | None = None


class EffectReceiptV1(StrictContract):
    effect_receipt_id: str
    prepared_tool_action_ref: str
    attempt_ref: str
    effect_state: Literal["CONFIRMED", "CONFIRMED_NOT_EXECUTED", "DUPLICATE_BLOCKED", "FAILED"]
    provider_receipt_ref: str | None = None
    observed_at: datetime
    idempotency_key: str


class EffectReconciliationV1(StrictContract):
    effect_reconciliation_id: str
    prepared_tool_action_ref: str
    attempt_ref: str
    state: Literal["PENDING", "CHECKING_EXTERNAL_FACT", "CONFIRMED", "CONFIRMED_NOT_EXECUTED", "COMPENSATED", "ESCALATED", "FAILED"]
    reason: str
    next_check_at: datetime | None = None
    concluded_receipt_ref: str | None = None
