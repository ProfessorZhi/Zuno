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
        if (
            self.payload is not None
            and canonical_sha256(self.payload) != self.payload_hash
        ):
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
            raise ValueError(
                f"failure code {self.code} does not match owner prefix {expected}"
            )
        return self


class DataServiceCapabilityV1(StrictContract):
    service_kind: Literal[
        "RELATIONAL",
        "QUEUE",
        "OBJECT",
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "TRACE_AUDIT",
        "SECRET_KMS",
    ]
    adapter_name: str
    adapter_version: str
    deployment_profile: str
    authoritative: bool
    rebuildable: bool
    consistency_model: str
    tenant_isolation_mode: str
    backup_restore_class: str
    schema_or_contract_version: str
    config_hash: str
    supported_semantics: tuple[str, ...]
    unsupported_semantics: tuple[str, ...]

    @model_validator(mode="after")
    def _capability_boundary(self) -> "DataServiceCapabilityV1":
        if not self.supported_semantics:
            raise ValueError("supported_semantics must be explicit")
        if self.authoritative and self.rebuildable:
            raise ValueError("authoritative services cannot be marked rebuildable")
        if (
            self.service_kind in {"VECTOR", "GRAPH", "LEXICAL", "CACHE"}
            and self.authoritative
        ):
            raise ValueError(f"{self.service_kind} cannot be authoritative by default")
        return self


class TenantIsolationProfileV1(StrictContract):
    profile_id: str
    service_kind: Literal[
        "RELATIONAL",
        "QUEUE",
        "OBJECT",
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "TRACE_AUDIT",
        "SECRET_KMS",
    ]
    isolation_mode: str
    scope_fields: tuple[str, ...]
    strong_isolation_option: str
    mandatory_filter_required: bool
    application_end_filter_only_allowed: bool = False
    cross_tenant_hit_action: Literal["QUARANTINE", "FAIL_CLOSED", "MANDATORY_AUDIT"]
    evidence_ref: str
    current_runtime_status: Literal["PROVEN", "PROFILE_ONLY", "BLOCKED"]

    @model_validator(mode="after")
    def _tenant_isolation_boundary(self) -> "TenantIsolationProfileV1":
        if "tenant_id" not in self.scope_fields:
            raise ValueError("tenant isolation profile must include tenant_id")
        if self.application_end_filter_only_allowed:
            raise ValueError("application-end filtering cannot be the only isolation")
        if self.cross_tenant_hit_action not in {
            "QUARANTINE",
            "FAIL_CLOSED",
            "MANDATORY_AUDIT",
        }:
            raise ValueError("cross tenant hit action must fail closed")
        return self


class UpgradeCompatibilityProfileV1(StrictContract):
    profile_id: str
    service_kind: Literal[
        "RELATIONAL",
        "QUEUE",
        "OBJECT",
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "TRACE_AUDIT",
        "SECRET_KMS",
    ]
    profile_version: str
    current_adapter_version: str
    current_schema_or_contract_version: str
    read_compatible_adapter_versions: tuple[str, ...]
    write_compatible_adapter_versions: tuple[str, ...]
    rollback_compatible_adapter_versions: tuple[str, ...]
    read_compatible_schema_or_contract_versions: tuple[str, ...]
    write_compatible_schema_or_contract_versions: tuple[str, ...]
    rollback_compatible_schema_or_contract_versions: tuple[str, ...]
    unsupported_adapter_versions: tuple[str, ...] = ()
    unsupported_schema_or_contract_versions: tuple[str, ...] = ()
    unknown_adapter_version_action: Literal["FAIL_CLOSED"]
    unknown_schema_or_contract_version_action: Literal["FAIL_CLOSED"]
    evidence_ref: str
    current_runtime_status: Literal["PROVEN", "PROFILE_ONLY", "BLOCKED"]
    content_hash: str

    def hash_inputs(self) -> dict[str, Any]:
        data = self.model_dump(mode="json", exclude_none=False)
        data.pop("content_hash", None)
        return data

    @model_validator(mode="after")
    def _compatibility_window_is_explicit(self) -> "UpgradeCompatibilityProfileV1":
        adapter_windows = {
            "read": self.read_compatible_adapter_versions,
            "write": self.write_compatible_adapter_versions,
            "rollback": self.rollback_compatible_adapter_versions,
        }
        schema_windows = {
            "read": self.read_compatible_schema_or_contract_versions,
            "write": self.write_compatible_schema_or_contract_versions,
            "rollback": self.rollback_compatible_schema_or_contract_versions,
        }
        for name, versions in adapter_windows.items():
            if not versions:
                raise ValueError(f"{name} adapter compatibility window is empty")
        for name, versions in schema_windows.items():
            if not versions:
                raise ValueError(f"{name} schema compatibility window is empty")
        if self.current_adapter_version not in self.read_compatible_adapter_versions:
            raise ValueError("current adapter version must be read compatible")
        if self.current_adapter_version not in self.write_compatible_adapter_versions:
            raise ValueError("current adapter version must be write compatible")
        if (
            self.current_schema_or_contract_version
            not in self.read_compatible_schema_or_contract_versions
        ):
            raise ValueError("current schema version must be read compatible")
        if (
            self.current_schema_or_contract_version
            not in self.write_compatible_schema_or_contract_versions
        ):
            raise ValueError("current schema version must be write compatible")
        if set(self.unsupported_adapter_versions).intersection(
            self.read_compatible_adapter_versions
            + self.write_compatible_adapter_versions
            + self.rollback_compatible_adapter_versions
        ):
            raise ValueError("unsupported adapter versions cannot be compatible")
        if set(self.unsupported_schema_or_contract_versions).intersection(
            self.read_compatible_schema_or_contract_versions
            + self.write_compatible_schema_or_contract_versions
            + self.rollback_compatible_schema_or_contract_versions
        ):
            raise ValueError("unsupported schema versions cannot be compatible")
        if canonical_sha256(self.hash_inputs()) != self.content_hash:
            raise ValueError(
                "content_hash does not match upgrade compatibility profile"
            )
        return self


class AdapterConformanceProfileV1(StrictContract):
    profile_id: str
    adapter_name: str
    service_kind: Literal[
        "RELATIONAL",
        "QUEUE",
        "OBJECT",
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "TRACE_AUDIT",
        "SECRET_KMS",
    ]
    deployment_class: Literal["DEVELOPER_CI", "SERVER_PRODUCT"]
    supported_semantics: tuple[str, ...]
    unsupported_semantics: tuple[str, ...] = ()
    fail_fast_on_unsupported: bool
    conformance_suite_version: str
    required_test_refs: tuple[str, ...]
    evidence_ref: str
    current_runtime_status: Literal["PROVEN", "PROFILE_ONLY", "BLOCKED"]
    content_hash: str

    def hash_inputs(self) -> dict[str, Any]:
        data = self.model_dump(mode="json", exclude_none=False)
        data.pop("content_hash", None)
        return data

    @model_validator(mode="after")
    def _conformance_boundary_is_explicit(self) -> "AdapterConformanceProfileV1":
        if not self.supported_semantics:
            raise ValueError("supported_semantics must be explicit")
        if not self.fail_fast_on_unsupported:
            raise ValueError("unsupported semantics must fail fast")
        if not self.conformance_suite_version:
            raise ValueError("conformance_suite_version must be explicit")
        if not self.required_test_refs:
            raise ValueError("required_test_refs must be explicit")
        if set(self.supported_semantics).intersection(self.unsupported_semantics):
            raise ValueError("a semantic cannot be both supported and unsupported")
        if canonical_sha256(self.hash_inputs()) != self.content_hash:
            raise ValueError("content_hash does not match conformance profile")
        return self


class InfrastructureCapabilityProfileV1(StrictContract):
    profile_id: str
    profile_version: str
    deployment_class: Literal["DEVELOPER_CI", "SERVER_PRODUCT"]
    database: DataServiceCapabilityV1
    object_store: DataServiceCapabilityV1
    checkpoint_store: DataServiceCapabilityV1
    queue: DataServiceCapabilityV1
    vector_index: DataServiceCapabilityV1 | None = None
    graph_index: DataServiceCapabilityV1 | None = None
    lexical_index: DataServiceCapabilityV1 | None = None
    cache: DataServiceCapabilityV1 | None = None
    secret_delivery: DataServiceCapabilityV1
    telemetry: DataServiceCapabilityV1
    limits: dict[str, int | str | bool]
    content_hash: str

    def hash_inputs(self) -> dict[str, Any]:
        data = self.model_dump(mode="json", exclude_none=False)
        data.pop("content_hash", None)
        return data

    @model_validator(mode="after")
    def _profile_hash_matches(self) -> "InfrastructureCapabilityProfileV1":
        if canonical_sha256(self.hash_inputs()) != self.content_hash:
            raise ValueError("content_hash does not match capability profile")
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


class ProductCommandV1(StrictContract):
    command_id: str
    command_kind: str
    tenant_id: str
    workspace_id: str
    principal_context_ref: str
    idempotency_key: str
    payload_schema_hash: str
    payload_hash: str
    submitted_at: datetime


class SourceObjectRefV1(StrictContract):
    source_object_ref: str
    tenant_id: str
    workspace_id: str
    object_uri: str
    content_hash: str
    parser_policy_ref: str
    lineage_ref: str


class KnowledgeVersionRefV1(StrictContract):
    knowledge_version_ref: str
    knowledge_space_id: str
    source_snapshot_ref: str
    index_manifest_hash: str
    visibility_receipt_ref: str


class MemoryContextRefV1(StrictContract):
    memory_context_ref: str
    tenant_id: str
    workspace_id: str
    policy_snapshot_ref: str
    activation_snapshot_hash: str
    expires_at: datetime | None = None


class CapabilityInvocationRefV1(StrictContract):
    capability_invocation_ref: str
    capability_ref: str
    version: str
    caller_module: str
    input_contract_ref: str
    output_contract_ref: str
    security_context_ref: str


class ObservabilityEventRefV1(StrictContract):
    observability_event_ref: str
    trace_id: str
    producer_module: str
    event_kind: str
    payload_hash: str
    redaction_decision_ref: str | None = None


class InfrastructureLeaseRefV1(StrictContract):
    infrastructure_lease_ref: str
    resource_ref: str
    holder_ref: str
    fencing_token: str
    acquired_at: datetime
    expires_at: datetime


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
    consistency_class: Literal[
        "IMMEDIATE", "READ_YOUR_WRITE", "BOUNDED_EVENTUAL", "EVENTUAL"
    ]
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
    status: Literal[
        "PREPARED",
        "WAITING_APPROVAL",
        "AUTHORIZED",
        "EXECUTING",
        "TERMINAL",
        "OBSOLETE",
    ]

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
            raise ValueError(
                "prepared_action_hash does not match canonical hash inputs"
            )
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
    effect_state: Literal[
        "CONFIRMED", "CONFIRMED_NOT_EXECUTED", "DUPLICATE_BLOCKED", "FAILED"
    ]
    provider_receipt_ref: str | None = None
    observed_at: datetime
    idempotency_key: str


class EffectReconciliationV1(StrictContract):
    effect_reconciliation_id: str
    prepared_tool_action_ref: str
    attempt_ref: str
    state: Literal[
        "PENDING",
        "CHECKING_EXTERNAL_FACT",
        "CONFIRMED",
        "CONFIRMED_NOT_EXECUTED",
        "COMPENSATED",
        "ESCALATED",
        "FAILED",
    ]
    reason: str
    next_check_at: datetime | None = None
    concluded_receipt_ref: str | None = None
