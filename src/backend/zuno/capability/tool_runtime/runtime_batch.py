from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any

from zuno.platform.security import redact_sensitive_payload


def _hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class AdapterFamily(StrEnum):
    CLI = "CLI"
    OPENAPI = "OPENAPI"
    SDK = "SDK"
    MCP = "MCP"
    BROWSER = "BROWSER"
    ASYNC_JOB = "ASYNC_JOB"


class EffectLevel(StrEnum):
    READ_ONLY = "READ_ONLY"
    AUDIT_OR_CURSOR = "AUDIT_OR_CURSOR"
    WRITE_INTERNAL = "WRITE_INTERNAL"
    WRITE_EXTERNAL = "WRITE_EXTERNAL"
    DESTRUCTIVE = "DESTRUCTIVE"


class PreparedActionStatus(StrEnum):
    PREPARED = "PREPARED"
    APPROVAL_WAITING = "APPROVAL_WAITING"
    READY = "READY"
    DISPATCHED = "DISPATCHED"
    OBSOLETE = "OBSOLETE"
    CANCEL_REQUESTED = "CANCEL_REQUESTED"
    CANCELLED = "CANCELLED"


class ToolAttemptStatus(StrEnum):
    STARTED = "STARTED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
    RECONCILING = "RECONCILING"


class DispatchCertainty(StrEnum):
    NOT_DISPATCHED = "NOT_DISPATCHED"
    DISPATCHED = "DISPATCHED"
    MAYBE_DISPATCHED = "MAYBE_DISPATCHED"


class EffectCertainty(StrEnum):
    NO_EFFECT = "NO_EFFECT"
    CONFIRMED_EFFECT = "CONFIRMED_EFFECT"
    UNKNOWN_EFFECT = "UNKNOWN_EFFECT"


class ReconciliationConclusion(StrEnum):
    PENDING = "PENDING"
    CONFIRMED_EXECUTED = "CONFIRMED_EXECUTED"
    CONFIRMED_NOT_EXECUTED = "CONFIRMED_NOT_EXECUTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True, slots=True)
class ToolDefinitionRecord:
    tool_id: str
    owner_module: str
    schema_hash: str
    definition_event_ref: str
    canonical_owner: str = "08 Tool Runtime"


@dataclass(frozen=True, slots=True)
class PlannerProjectionRecord:
    projection_ref: str
    source_definition_ref: str
    owner_module: str = "07 Capability / Skill"
    executable: bool = False


@dataclass(frozen=True, slots=True)
class ToolVersionRecord:
    tool_id: str
    version: str
    immutable_hash: str
    mutation_allowed: bool = False


@dataclass(frozen=True, slots=True)
class InstallationRecord:
    installation_ref: str
    tool_definition_ref: str
    workspace_id: str
    credential_scope_ref: str


@dataclass(frozen=True, slots=True)
class ActivationRecord:
    activation_ref: str
    installation_ref: str
    version_ref: str
    generation: int
    active: bool
    cas_passed: bool


@dataclass(frozen=True, slots=True)
class ExposureDecision:
    exposure_ref: str
    can_show_to_model: bool
    can_prepare: bool
    can_execute: bool
    security_decision_ref: str


@dataclass(frozen=True, slots=True)
class ActionProposalRecord:
    proposal_ref: str
    producer_module: str
    tool_ref: str
    input_hash: str
    accepted_by_tool_runtime: bool


@dataclass(frozen=True, slots=True)
class CanonicalizationProfile:
    profile_ref: str
    version: str
    canonical_hash: str


@dataclass(frozen=True, slots=True)
class TargetResourceSet:
    resource_set_ref: str
    resource_refs: tuple[str, ...]
    conflict_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EffectProfile:
    profile_ref: str
    level: EffectLevel
    requires_approval: bool
    requires_effect_receipt: bool
    canary_real_effect_allowed: bool = False


@dataclass(frozen=True, slots=True)
class PreparedToolAction:
    prepared_ref: str
    proposal_ref: str
    owner_module: str
    status: PreparedActionStatus
    canonical_input_hash: str
    approval_binding_hash: str
    resource_set_ref: str
    effect_profile_ref: str
    security_epoch_ref: str
    audit_requirement_ref: str
    idempotency_key: str
    deadline_ref: str
    contains_secret_material: bool


@dataclass(frozen=True, slots=True)
class ExecutionGateRecord:
    gate_ref: str
    security_epoch_ref: str
    audit_receipt_ref: str
    claim_ref: str
    dispatch_allowed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ToolAttemptRecord:
    attempt_ref: str
    prepared_ref: str
    status: ToolAttemptStatus
    dispatch_certainty: DispatchCertainty
    state_history: tuple[str, ...]
    adapter_family: AdapterFamily
    hidden_retry_count: int


@dataclass(frozen=True, slots=True)
class ToolExecutionReceipt:
    receipt_ref: str
    prepared_ref: str
    attempt_ref: str
    status: ToolAttemptStatus
    dispatch_certainty: DispatchCertainty
    effect_certainty: EffectCertainty
    append_only_generation: int


@dataclass(frozen=True, slots=True)
class EffectItemReceipt:
    item_ref: str
    resource_ref: str
    effect_hash: str


@dataclass(frozen=True, slots=True)
class EffectReceipt:
    effect_ref: str
    attempt_ref: str
    items: tuple[EffectItemReceipt, ...]
    provider_receipt_ref: str
    confirmed: bool


@dataclass(frozen=True, slots=True)
class ReconciliationRecord:
    reconciliation_ref: str
    attempt_ref: str
    conclusion: ReconciliationConclusion
    durable_after_run: bool
    retry_same_effect_allowed: bool


@dataclass(frozen=True, slots=True)
class CompensationPlan:
    compensation_ref: str
    source_effect_ref: str
    new_action_proposal_ref: str
    hidden_rollback: bool


@dataclass(frozen=True, slots=True)
class CancellationRecord:
    cancellation_ref: str
    prepared_ref: str
    requested: bool
    provider_stop_confirmed: bool
    final_certainty: DispatchCertainty


@dataclass(frozen=True, slots=True)
class ToolObservationRecord:
    observation_ref: str
    owner_module: str
    normalized_projection_owner: str
    output_trusted: bool
    schema_valid: bool
    memory_write_allowed: bool
    evidence_write_allowed: bool
    redacted_payload_hash: str


@dataclass(frozen=True, slots=True)
class CliSandboxPolicy:
    allowed_env_keys: tuple[str, ...]
    process_tree_kill: bool
    cpu_seconds: int
    memory_mb: int


@dataclass(frozen=True, slots=True)
class OpenApiPolicy:
    endpoint_allowed: bool
    redirects_rechecked: bool
    probe_has_effect: bool


@dataclass(frozen=True, slots=True)
class AdapterConformanceProfile:
    adapter_ref: str
    family: AdapterFamily
    version: str
    pinned: bool
    invalidated: bool
    hidden_retry_controlled: bool


@dataclass(frozen=True, slots=True)
class McpSessionRecord:
    session_ref: str
    negotiated_capability_refs: tuple[str, ...]
    schema_snapshot_hash: str
    old_actions_obsolete_on_list_changed: bool
    annotations_trusted: bool
    multimodal_content_refs: tuple[str, ...]
    task_binding_ref: str
    redelivery_receipt_ref: str
    idempotency_claim_ref: str
    sampling_route_owner: str
    elicitation_is_security_approval: bool


@dataclass(frozen=True, slots=True)
class AsyncCallbackRecord:
    job_ref: str
    accepted_is_completion: bool
    callback_signature_verified: bool
    callback_nonce_ref: str


@dataclass(frozen=True, slots=True)
class ConcurrencyRecord:
    resource_conflict_keys: tuple[str, ...]
    replan_epoch_ref: str
    stale_dispatch_rejected: bool
    timeout_stages: tuple[str, ...]
    deadline_ref: str


@dataclass(frozen=True, slots=True)
class FailureCodeRecord:
    code: str
    namespace: str


@dataclass(frozen=True, slots=True)
class ToolInfrastructureBoundary:
    outbox_event_ref: str
    domain_fact_ref: str
    same_transaction: bool
    secret_lease_ref: str
    sandbox_isolation_sufficient: bool
    capacity_gate_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LifecycleRecord:
    canary_real_effect_allowed: bool
    drain_watermark_ref: str
    retired_history_readable: bool
    large_payload_object_ref: str
    legal_hold_blocks_delete: bool
    confirmed_effect_sli_ref: str


@dataclass(frozen=True, slots=True)
class BypassAllowlistRecord:
    current_allowlist_refs: tuple[str, ...]
    zero_gate_ref: str
    monotonic_decrease: bool


@dataclass(frozen=True, slots=True)
class ToolReadinessEvidence:
    requirement_ids: tuple[str, ...]
    code_refs: tuple[str, ...]
    test_refs: tuple[str, ...]
    verifier_ref: str
    evidence_ref: str
    implementation_available: bool


class ToolRuntimeBatch:
    requirement_ids = tuple(f"ARCH-TOOL-{index:03d}" for index in range(1, 81))
    valid_attempt_transitions = {
        ToolAttemptStatus.STARTED: {ToolAttemptStatus.SUCCEEDED, ToolAttemptStatus.FAILED, ToolAttemptStatus.UNKNOWN},
        ToolAttemptStatus.UNKNOWN: {ToolAttemptStatus.RECONCILING},
        ToolAttemptStatus.RECONCILING: {ToolAttemptStatus.SUCCEEDED, ToolAttemptStatus.FAILED},
    }
    gate_order = ("exposure", "prepare", "security_epoch", "audit", "claim", "dispatch", "receipt", "effect")

    def tool_definition(self, *, tool_id: str, schema: dict[str, Any], definition_event_ref: str) -> ToolDefinitionRecord:
        return ToolDefinitionRecord(tool_id, "08 Tool Runtime", _hash(schema), definition_event_ref)

    def planner_projection(self, *, projection_ref: str, source_definition_ref: str) -> PlannerProjectionRecord:
        return PlannerProjectionRecord(projection_ref, source_definition_ref)

    def tool_version(self, *, tool_id: str, version: str, schema: dict[str, Any]) -> ToolVersionRecord:
        return ToolVersionRecord(tool_id, version, _hash([tool_id, version, schema]))

    def installation(self, *, installation_ref: str, tool_definition_ref: str, workspace_id: str, credential_scope_ref: str) -> InstallationRecord:
        return InstallationRecord(installation_ref, tool_definition_ref, workspace_id, credential_scope_ref)

    def activation(self, *, activation_ref: str, installation_ref: str, version_ref: str, expected_generation: int, committed_generation: int) -> ActivationRecord:
        return ActivationRecord(activation_ref, installation_ref, version_ref, committed_generation, True, committed_generation == expected_generation + 1)

    def exposure_decision(self, *, exposure_ref: str, can_show_to_model: bool, can_prepare: bool, security_decision_ref: str) -> ExposureDecision:
        return ExposureDecision(exposure_ref, can_show_to_model, can_prepare, False, security_decision_ref)

    def action_proposal(self, *, proposal_ref: str, producer_module: str, tool_ref: str, input_payload: dict[str, Any]) -> ActionProposalRecord:
        return ActionProposalRecord(proposal_ref, producer_module, tool_ref, _hash(input_payload), producer_module == "06 Agent Core / Planning & Control")

    def canonicalization(self, *, profile_ref: str, version: str, payload: dict[str, Any]) -> CanonicalizationProfile:
        return CanonicalizationProfile(profile_ref, version, _hash({"profile": version, "payload": payload}))

    def target_resources(self, *, resource_set_ref: str, resource_refs: tuple[str, ...], conflict_keys: tuple[str, ...]) -> TargetResourceSet:
        return TargetResourceSet(resource_set_ref, resource_refs, conflict_keys)

    def effect_profile(self, *, profile_ref: str, level: EffectLevel) -> EffectProfile:
        effectful = level != EffectLevel.READ_ONLY
        return EffectProfile(profile_ref, level, level in {EffectLevel.WRITE_EXTERNAL, EffectLevel.DESTRUCTIVE}, effectful)

    def prepare_action(
        self,
        *,
        prepared_ref: str,
        proposal: ActionProposalRecord,
        canonical: CanonicalizationProfile,
        resource_set: TargetResourceSet,
        effect_profile: EffectProfile,
        security_epoch_ref: str,
        audit_requirement_ref: str,
        idempotency_key: str,
        deadline_ref: str,
        input_payload: dict[str, Any],
    ) -> PreparedToolAction:
        redacted = redact_sensitive_payload(input_payload)
        return PreparedToolAction(
            prepared_ref=prepared_ref,
            proposal_ref=proposal.proposal_ref,
            owner_module="08 Tool Runtime",
            status=PreparedActionStatus.APPROVAL_WAITING if effect_profile.requires_approval else PreparedActionStatus.READY,
            canonical_input_hash=_hash(redacted),
            approval_binding_hash=_hash([proposal.proposal_ref, canonical.canonical_hash, resource_set.resource_set_ref, effect_profile.profile_ref, security_epoch_ref, audit_requirement_ref, deadline_ref]),
            resource_set_ref=resource_set.resource_set_ref,
            effect_profile_ref=effect_profile.profile_ref,
            security_epoch_ref=security_epoch_ref,
            audit_requirement_ref=audit_requirement_ref,
            idempotency_key=idempotency_key,
            deadline_ref=deadline_ref,
            contains_secret_material=False,
        )

    def execution_gate(self, *, gate_ref: str, security_epoch_ref: str, audit_receipt_ref: str | None, claim_ref: str | None, sandbox_isolation_sufficient: bool = True) -> ExecutionGateRecord:
        allowed = bool(security_epoch_ref and audit_receipt_ref and claim_ref and sandbox_isolation_sufficient)
        if not sandbox_isolation_sufficient:
            reason = "sandbox_isolation_fail_closed"
        elif not audit_receipt_ref:
            reason = "audit_required_before_effect"
        elif not claim_ref:
            reason = "claim_required_before_dispatch"
        else:
            reason = "dispatch_allowed"
        return ExecutionGateRecord(gate_ref, security_epoch_ref, audit_receipt_ref or "", claim_ref or "", allowed, reason)

    def attempt(self, *, attempt_ref: str, prepared_ref: str, status: ToolAttemptStatus, dispatch_certainty: DispatchCertainty, adapter_family: AdapterFamily, hidden_retry_count: int = 0) -> ToolAttemptRecord:
        history = (ToolAttemptStatus.STARTED.value,) if status == ToolAttemptStatus.STARTED else (ToolAttemptStatus.STARTED.value, status.value)
        return ToolAttemptRecord(attempt_ref, prepared_ref, status, dispatch_certainty, history, adapter_family, hidden_retry_count)

    def transition_allowed(self, *, current: ToolAttemptStatus, next_status: ToolAttemptStatus) -> bool:
        return next_status in self.valid_attempt_transitions.get(current, set())

    def execution_receipt(self, *, receipt_ref: str, attempt: ToolAttemptRecord, generation: int) -> ToolExecutionReceipt:
        if attempt.status == ToolAttemptStatus.SUCCEEDED:
            effect = EffectCertainty.CONFIRMED_EFFECT
        elif attempt.status == ToolAttemptStatus.UNKNOWN:
            effect = EffectCertainty.UNKNOWN_EFFECT
        else:
            effect = EffectCertainty.NO_EFFECT
        return ToolExecutionReceipt(receipt_ref, attempt.prepared_ref, attempt.attempt_ref, attempt.status, attempt.dispatch_certainty, effect, generation)

    def effect_receipt(self, *, effect_ref: str, attempt_ref: str, provider_receipt_ref: str, effects: tuple[tuple[str, dict[str, Any]], ...]) -> EffectReceipt:
        items = tuple(EffectItemReceipt(f"{effect_ref}:item:{index}", resource_ref, _hash(payload)) for index, (resource_ref, payload) in enumerate(effects, start=1))
        return EffectReceipt(effect_ref, attempt_ref, items, provider_receipt_ref, confirmed=bool(provider_receipt_ref and items))

    def reconciliation(self, *, reconciliation_ref: str, attempt_ref: str, conclusion: ReconciliationConclusion) -> ReconciliationRecord:
        return ReconciliationRecord(reconciliation_ref, attempt_ref, conclusion, durable_after_run=True, retry_same_effect_allowed=conclusion == ReconciliationConclusion.CONFIRMED_NOT_EXECUTED)

    def compensation(self, *, compensation_ref: str, source_effect_ref: str, new_action_proposal_ref: str) -> CompensationPlan:
        return CompensationPlan(compensation_ref, source_effect_ref, new_action_proposal_ref, hidden_rollback=False)

    def cancellation(self, *, cancellation_ref: str, prepared_ref: str, provider_stop_confirmed: bool) -> CancellationRecord:
        certainty = DispatchCertainty.NOT_DISPATCHED if provider_stop_confirmed else DispatchCertainty.MAYBE_DISPATCHED
        return CancellationRecord(cancellation_ref, prepared_ref, True, provider_stop_confirmed, certainty)

    def observation(self, *, observation_ref: str, output_payload: dict[str, Any], schema_valid: bool, memory_decision_ref: str | None = None, evidence_decision_ref: str | None = None) -> ToolObservationRecord:
        redacted = redact_sensitive_payload(output_payload)
        return ToolObservationRecord(
            observation_ref=observation_ref,
            owner_module="08 Tool Runtime",
            normalized_projection_owner="06 Agent Core / Planning & Control",
            output_trusted=False,
            schema_valid=schema_valid,
            memory_write_allowed=bool(memory_decision_ref),
            evidence_write_allowed=bool(evidence_decision_ref),
            redacted_payload_hash=_hash(redacted),
        )

    def cli_policy(self, *, allowed_env_keys: tuple[str, ...], cpu_seconds: int, memory_mb: int) -> CliSandboxPolicy:
        return CliSandboxPolicy(allowed_env_keys, process_tree_kill=True, cpu_seconds=cpu_seconds, memory_mb=memory_mb)

    def openapi_policy(self, *, endpoint_allowed: bool, redirects_rechecked: bool) -> OpenApiPolicy:
        return OpenApiPolicy(endpoint_allowed, redirects_rechecked, probe_has_effect=False)

    def adapter_conformance(self, *, adapter_ref: str, family: AdapterFamily, version: str, hidden_retry_controlled: bool, invalidated: bool = False) -> AdapterConformanceProfile:
        return AdapterConformanceProfile(adapter_ref, family, version, pinned=":" in version, invalidated=invalidated, hidden_retry_controlled=hidden_retry_controlled)

    def mcp_session(self, *, session_ref: str, negotiated_capability_refs: tuple[str, ...], schema_snapshot: dict[str, Any], multimodal_content_refs: tuple[str, ...], task_binding_ref: str, redelivery_receipt_ref: str, idempotency_claim_ref: str) -> McpSessionRecord:
        return McpSessionRecord(
            session_ref=session_ref,
            negotiated_capability_refs=negotiated_capability_refs,
            schema_snapshot_hash=_hash(schema_snapshot),
            old_actions_obsolete_on_list_changed=True,
            annotations_trusted=False,
            multimodal_content_refs=multimodal_content_refs,
            task_binding_ref=task_binding_ref,
            redelivery_receipt_ref=redelivery_receipt_ref,
            idempotency_claim_ref=idempotency_claim_ref,
            sampling_route_owner="04 Model Gateway",
            elicitation_is_security_approval=False,
        )

    def async_callback(self, *, job_ref: str, callback_signature_verified: bool, callback_nonce_ref: str) -> AsyncCallbackRecord:
        return AsyncCallbackRecord(job_ref, accepted_is_completion=False, callback_signature_verified=callback_signature_verified, callback_nonce_ref=callback_nonce_ref)

    def concurrency(self, *, resource_conflict_keys: tuple[str, ...], replan_epoch_ref: str, timeout_stages: tuple[str, ...], deadline_ref: str, stale_epoch: bool) -> ConcurrencyRecord:
        return ConcurrencyRecord(resource_conflict_keys, replan_epoch_ref, stale_dispatch_rejected=stale_epoch, timeout_stages=timeout_stages, deadline_ref=deadline_ref)

    def failure_code(self, *, code: str) -> FailureCodeRecord:
        namespace = code.split("_", 1)[0] if "_" in code else "TOOL"
        return FailureCodeRecord(code, namespace)

    def infrastructure_boundary(self, *, outbox_event_ref: str, domain_fact_ref: str, secret_lease_ref: str, sandbox_isolation_sufficient: bool) -> ToolInfrastructureBoundary:
        return ToolInfrastructureBoundary(
            outbox_event_ref=outbox_event_ref,
            domain_fact_ref=domain_fact_ref,
            same_transaction=bool(outbox_event_ref and domain_fact_ref),
            secret_lease_ref=secret_lease_ref,
            sandbox_isolation_sufficient=sandbox_isolation_sufficient,
            capacity_gate_order=self.gate_order,
        )

    def lifecycle(self, *, drain_watermark_ref: str, large_payload_object_ref: str, legal_hold: bool) -> LifecycleRecord:
        return LifecycleRecord(False, drain_watermark_ref, True, large_payload_object_ref, legal_hold_blocks_delete=legal_hold, confirmed_effect_sli_ref="sli:tool.confirmed_effect")

    def allowlist(self, *, current_allowlist_refs: tuple[str, ...], zero_gate_ref: str, previous_count: int) -> BypassAllowlistRecord:
        return BypassAllowlistRecord(current_allowlist_refs, zero_gate_ref, monotonic_decrease=len(current_allowlist_refs) <= previous_count)

    def readiness_evidence(self, *, code_refs: tuple[str, ...], test_refs: tuple[str, ...], verifier_ref: str, evidence_ref: str) -> ToolReadinessEvidence:
        return ToolReadinessEvidence(
            requirement_ids=self.requirement_ids,
            code_refs=code_refs,
            test_refs=test_refs,
            verifier_ref=verifier_ref,
            evidence_ref=evidence_ref,
            implementation_available=bool(code_refs and test_refs and verifier_ref and evidence_ref and len(self.requirement_ids) == 80),
        )


__all__ = [
    "AdapterConformanceProfile",
    "AdapterFamily",
    "AsyncCallbackRecord",
    "BypassAllowlistRecord",
    "CanonicalizationProfile",
    "CancellationRecord",
    "CliSandboxPolicy",
    "CompensationPlan",
    "ConcurrencyRecord",
    "DispatchCertainty",
    "EffectCertainty",
    "EffectItemReceipt",
    "EffectLevel",
    "EffectProfile",
    "EffectReceipt",
    "ExecutionGateRecord",
    "ExposureDecision",
    "FailureCodeRecord",
    "InstallationRecord",
    "LifecycleRecord",
    "McpSessionRecord",
    "OpenApiPolicy",
    "PlannerProjectionRecord",
    "PreparedActionStatus",
    "PreparedToolAction",
    "ReconciliationConclusion",
    "ReconciliationRecord",
    "TargetResourceSet",
    "ToolAttemptRecord",
    "ToolAttemptStatus",
    "ToolDefinitionRecord",
    "ToolExecutionReceipt",
    "ToolInfrastructureBoundary",
    "ToolObservationRecord",
    "ToolReadinessEvidence",
    "ToolRuntimeBatch",
    "ToolVersionRecord",
]
