from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any

from zuno.platform.security import redact_sensitive_payload


class CapabilityDecisionStatus(StrEnum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    QUARANTINED = "QUARANTINED"
    REQUIRES_REVALIDATION = "REQUIRES_REVALIDATION"


class CapabilityAvailabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    CONFIG_REQUIRED = "CONFIG_REQUIRED"
    UNAVAILABLE = "UNAVAILABLE"
    VERSION_INCOMPATIBLE = "VERSION_INCOMPATIBLE"
    POLICY_CONSTRAINED = "POLICY_CONSTRAINED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class CapabilityResultValidity(StrEnum):
    VALID = "VALID"
    STALE = "STALE"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"
    UNKNOWN_VALIDITY = "UNKNOWN_VALIDITY"


def _hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class CapabilityBoundaryDecision:
    module: str
    executes_tool: bool
    commits_foreign_fact: bool
    allowed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class CapabilityConceptTaxonomy:
    capability_kind: str
    provider_protocol: str
    governance_objects: tuple[str, ...]
    valid: bool


@dataclass(frozen=True, slots=True)
class CapabilityEnvelope:
    envelope_type: str
    major_version: int
    payload_hash: str
    tenant_id: str
    trace_id: str
    security_epoch_ref: str


@dataclass(frozen=True, slots=True)
class CapabilityUnknownContractVerdict:
    status: CapabilityDecisionStatus
    reason: str


@dataclass(frozen=True, slots=True)
class SkillVersionRecord:
    skill_id: str
    version: str
    metadata_ref: str
    instruction_ref: str
    resource_manifest_ref: str
    capability_requirement_refs: tuple[str, ...]
    acceptance_criteria_ref: str
    immutable_hash: str


@dataclass(frozen=True, slots=True)
class SkillDiscoveryResult:
    discovery_id: str
    metadata_only: bool
    candidate_skill_ids: tuple[str, ...]
    rejected: tuple[str, ...]
    immutable_hash: str


@dataclass(frozen=True, slots=True)
class SkillLoadResult:
    skill_id: str
    version: str
    resource_hashes: tuple[str, ...]
    load_policy_ref: str
    budget_ref: str
    validity: CapabilityResultValidity


@dataclass(frozen=True, slots=True)
class SkillResourceClassification:
    resource_ref: str
    resource_type: str
    data_classification: str
    integrity_hash: str
    source_ref: str
    executable: bool
    direct_execution_allowed: bool


@dataclass(frozen=True, slots=True)
class SkillPolicyVerdict:
    non_amplifying: bool
    supply_chain_verified: bool
    security_precedence: bool
    model_visible_fields: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CapabilityDefinitionRecord:
    capability_id: str
    semantic_identity: str
    provider_tool_name: str | None
    stable: bool


@dataclass(frozen=True, slots=True)
class CapabilityVersionRecord:
    capability_id: str
    version: str
    input_schema_hash: str
    output_schema_hash: str
    risk_ref: str
    dependency_refs: tuple[str, ...]
    compatibility_ref: str
    acceptance_ref: str


@dataclass(frozen=True, slots=True)
class CapabilityProviderBindingRecord:
    binding_id: str
    capability_version_ref: str
    tool_definition_ref: str
    binding_version: str
    proposal_source: str
    deterministic_gates_passed: bool
    active: bool


@dataclass(frozen=True, slots=True)
class ProviderConformanceRecord:
    provider_ref: str
    covered_semantics: tuple[str, ...]
    passed: bool


@dataclass(frozen=True, slots=True)
class ProviderFailureDomain:
    provider_family: str
    backend_ref: str
    quota_ref: str
    effect_failure_domain_ref: str
    independent_disaster_recovery: bool


@dataclass(frozen=True, slots=True)
class ConnectorPackSplit:
    connector_pack_ref: str
    provider_definition_ref: str
    tool_manifest_refs: tuple[str, ...]
    capability_mapping_refs: tuple[str, ...]
    scope_mapping_refs: tuple[str, ...]
    contract_test_refs: tuple[str, ...]
    reconciliation_extension_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CapabilityAvailabilitySnapshot:
    snapshot_ref: str
    version: str
    ttl_seconds: int
    source_generation: int
    immutable: bool


@dataclass(frozen=True, slots=True)
class CapabilityAvailabilityEntry:
    capability_ref: str
    status: CapabilityAvailabilityStatus
    candidate_only: bool
    authorization_implied: bool


@dataclass(frozen=True, slots=True)
class CapabilitySelectionRecord:
    selection_id: str
    candidate_refs: tuple[str, ...]
    hard_filtered_refs: tuple[str, ...]
    scoring_hash: str
    selected_binding_ref: str
    provider_instance_ref: str
    fallback_order: tuple[str, ...]
    deterministic_commit: bool


@dataclass(frozen=True, slots=True)
class CapabilityFallbackVerdict:
    output_contract_preserved: bool
    risk_within_limit: bool
    tenant_preserved: bool
    data_residency_preserved: bool
    side_effect_semantics_preserved: bool
    compatible: bool


@dataclass(frozen=True, slots=True)
class CapabilityPinnedVersionSet:
    capability_version_ref: str
    binding_version_ref: str
    tool_definition_ref: str
    schema_hash: str
    exact: bool


@dataclass(frozen=True, slots=True)
class CapabilityInventoryChange:
    inventory_generation: int
    tool_definition_version_ref: str
    revalidation_required: bool
    schema_mutated_in_place: bool


@dataclass(frozen=True, slots=True)
class CapabilityReuseVerdict:
    version_ok: bool
    scope_ok: bool
    security_epoch_ok: bool
    snapshot_ttl_ok: bool
    resource_integrity_ok: bool
    reusable: bool


@dataclass(frozen=True, slots=True)
class CapabilitySecurityBoundary:
    provider_instance_ref: str
    credential_scope_ref: str
    capability_constraint_ref: str
    secret_material_stored: bool
    authorization_overridden_by_skill: bool
    valid: bool


@dataclass(frozen=True, slots=True)
class CapabilityConstraintRecord:
    tenant_id: str
    workspace_id: str
    region: str
    data_residency: str
    identity_mode: str
    resource_scope_ref: str
    provider_trust_ref: str


@dataclass(frozen=True, slots=True)
class CapabilityAuditBoundary:
    audit_requirement_ref: str
    persistence_receipt_owner: str
    audit_event_owner: str
    selection_propagates_requirement: bool


@dataclass(frozen=True, slots=True)
class CapabilityPersistenceBoundary:
    domain_fact_refs: tuple[str, ...]
    object_payload_refs: tuple[str, ...]
    projection_refs: tuple[str, ...]
    source_is_projection: bool


@dataclass(frozen=True, slots=True)
class CapabilityTransactionRecord:
    transaction_id: str
    facts: tuple[str, ...]
    outbox_event_ref: str
    atomic: bool


@dataclass(frozen=True, slots=True)
class CapabilityTransitionRecord:
    transition_id: str
    expected_generation: int
    committed_generation: int
    cas_passed: bool


@dataclass(frozen=True, slots=True)
class CapabilityOutboxRecord:
    event_id: str
    delivery_semantics: str
    consumer_idempotency_key: str


@dataclass(frozen=True, slots=True)
class CapabilityRecoveryPlan:
    resource_commit_ref: str
    version_publish_ref: str
    active_switch_ref: str
    snapshot_build_ref: str
    revocation_propagation_ref: str
    reconciler_ref: str
    claim_ref: str
    fencing_ref: str
    human_escalation_ref: str


@dataclass(frozen=True, slots=True)
class CapabilityConnectorPolicy:
    provider_specific_core_branch: bool
    generic_adapter_families: tuple[str, ...]
    structured_manifest_required: bool
    draft_only_from_discovery: bool
    custom_extension_reason: str | None
    unknown_effect_retry_allowed: bool


@dataclass(frozen=True, slots=True)
class CapabilityTraceEvent:
    event_type: str
    trace_ref: str
    payload_hash: str
    redacted_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CapabilityCurrentEvidenceGate:
    requirement_id: str
    code_ref: str
    migration_ref: str
    unit_ref: str
    integration_ref: str
    fault_ref: str
    e2e_ref: str
    trace_ref: str
    eval_ref: str
    runtime_evidence_ref: str

    @property
    def implementation_available(self) -> bool:
        return all(
            [
                self.code_ref,
                self.migration_ref,
                self.unit_ref,
                self.integration_ref,
                self.fault_ref,
                self.e2e_ref,
                self.trace_ref,
                self.eval_ref,
                self.runtime_evidence_ref,
            ]
        )


class CapabilityRuntimeBatch:
    provider_protocols = {"api", "cli", "sdk", "mcp", "browser", "rpc", "http", "database", "local_function"}
    governance_objects = {"security_gate", "approval", "budget", "trace", "checkpoint", "lease", "idempotency_claim"}
    availability_statuses = tuple(CapabilityAvailabilityStatus)
    generic_adapter_families = ("HTTP", "CLI", "MCP", "SDK", "RPC", "Browser", "Database", "LocalFunction")

    def boundary_decision(self, *, executes_tool: bool, commits_foreign_fact: bool) -> CapabilityBoundaryDecision:
        allowed = not executes_tool and not commits_foreign_fact
        return CapabilityBoundaryDecision(
            module="Capability / Skill",
            executes_tool=executes_tool,
            commits_foreign_fact=commits_foreign_fact,
            allowed=allowed,
            reason="boundary_ok" if allowed else "capability_boundary_violation",
        )

    def concept_taxonomy(self, *, capability_kind: str, provider_protocol: str, governance_objects: tuple[str, ...]) -> CapabilityConceptTaxonomy:
        valid = provider_protocol.lower() in self.provider_protocols and not set(governance_objects) - self.governance_objects
        return CapabilityConceptTaxonomy(
            capability_kind=capability_kind,
            provider_protocol=provider_protocol,
            governance_objects=governance_objects,
            valid=valid,
        )

    def envelope(self, *, envelope_type: str, major_version: int, payload: dict[str, Any], tenant_id: str, trace_id: str, security_epoch_ref: str) -> CapabilityEnvelope:
        if major_version <= 0 or not tenant_id or not trace_id or not security_epoch_ref:
            raise ValueError("capability envelope fail closed")
        return CapabilityEnvelope(
            envelope_type=envelope_type,
            major_version=major_version,
            payload_hash=_hash(payload),
            tenant_id=tenant_id,
            trace_id=trace_id,
            security_epoch_ref=security_epoch_ref,
        )

    def unknown_contract(self, *, known: bool, quarantine: bool = False) -> CapabilityUnknownContractVerdict:
        if known:
            return CapabilityUnknownContractVerdict(status=CapabilityDecisionStatus.ALLOWED, reason="known")
        return CapabilityUnknownContractVerdict(
            status=CapabilityDecisionStatus.QUARANTINED if quarantine else CapabilityDecisionStatus.BLOCKED,
            reason="unknown_contract_fail_closed",
        )

    def skill_version(
        self,
        *,
        skill_id: str,
        version: str,
        metadata_ref: str,
        instruction_ref: str,
        resource_manifest_ref: str,
        capability_requirement_refs: tuple[str, ...],
        acceptance_criteria_ref: str,
    ) -> SkillVersionRecord:
        payload = [skill_id, version, metadata_ref, instruction_ref, resource_manifest_ref, capability_requirement_refs, acceptance_criteria_ref]
        return SkillVersionRecord(
            skill_id=skill_id,
            version=version,
            metadata_ref=metadata_ref,
            instruction_ref=instruction_ref,
            resource_manifest_ref=resource_manifest_ref,
            capability_requirement_refs=capability_requirement_refs,
            acceptance_criteria_ref=acceptance_criteria_ref,
            immutable_hash=_hash(payload),
        )

    def skill_discovery(self, *, discovery_id: str, candidate_skill_ids: tuple[str, ...], rejected: tuple[str, ...]) -> SkillDiscoveryResult:
        return SkillDiscoveryResult(
            discovery_id=discovery_id,
            metadata_only=True,
            candidate_skill_ids=candidate_skill_ids,
            rejected=rejected,
            immutable_hash=_hash([discovery_id, candidate_skill_ids, rejected]),
        )

    def skill_load(self, *, skill_id: str, version: str, resource_hashes: tuple[str, ...], load_policy_ref: str, budget_ref: str) -> SkillLoadResult:
        return SkillLoadResult(
            skill_id=skill_id,
            version=version,
            resource_hashes=resource_hashes,
            load_policy_ref=load_policy_ref,
            budget_ref=budget_ref,
            validity=CapabilityResultValidity.VALID,
        )

    def skill_resource(self, *, resource_ref: str, resource_type: str, data_classification: str, source_ref: str, content_hash: str, executable: bool) -> SkillResourceClassification:
        return SkillResourceClassification(
            resource_ref=resource_ref,
            resource_type=resource_type,
            data_classification=data_classification,
            integrity_hash=content_hash,
            source_ref=source_ref,
            executable=executable,
            direct_execution_allowed=False,
        )

    def skill_policy(
        self,
        *,
        allowed_subset: tuple[str, ...],
        original_candidates: tuple[str, ...],
        signature_verified: bool,
        integrity_verified: bool,
        policy_verified: bool,
        risk_verified: bool,
        model_visible_fields: tuple[str, ...],
    ) -> SkillPolicyVerdict:
        return SkillPolicyVerdict(
            non_amplifying=set(allowed_subset) <= set(original_candidates),
            supply_chain_verified=signature_verified and integrity_verified and policy_verified and risk_verified,
            security_precedence=True,
            model_visible_fields=model_visible_fields,
        )

    def capability_definition(self, *, capability_id: str, semantic_identity: str, provider_tool_name: str | None = None) -> CapabilityDefinitionRecord:
        return CapabilityDefinitionRecord(
            capability_id=capability_id,
            semantic_identity=semantic_identity,
            provider_tool_name=provider_tool_name,
            stable=semantic_identity != provider_tool_name,
        )

    def capability_version(self, *, capability_id: str, version: str, input_schema: dict[str, Any], output_schema: dict[str, Any], risk_ref: str, dependency_refs: tuple[str, ...], compatibility_ref: str, acceptance_ref: str) -> CapabilityVersionRecord:
        return CapabilityVersionRecord(
            capability_id=capability_id,
            version=version,
            input_schema_hash=_hash(input_schema),
            output_schema_hash=_hash(output_schema),
            risk_ref=risk_ref,
            dependency_refs=dependency_refs,
            compatibility_ref=compatibility_ref,
            acceptance_ref=acceptance_ref,
        )

    def provider_binding(self, *, binding_id: str, capability_version_ref: str, tool_definition_ref: str, binding_version: str, proposal_source: str, deterministic_gates_passed: bool) -> CapabilityProviderBindingRecord:
        return CapabilityProviderBindingRecord(
            binding_id=binding_id,
            capability_version_ref=capability_version_ref,
            tool_definition_ref=tool_definition_ref,
            binding_version=binding_version,
            proposal_source=proposal_source,
            deterministic_gates_passed=deterministic_gates_passed,
            active=deterministic_gates_passed and proposal_source != "model_only",
        )

    def conformance_record(self, *, provider_ref: str, covered_semantics: tuple[str, ...]) -> ProviderConformanceRecord:
        required = {"input", "output", "side_effect", "idempotency", "reconciliation", "security", "error"}
        return ProviderConformanceRecord(provider_ref=provider_ref, covered_semantics=covered_semantics, passed=required <= set(covered_semantics))

    def provider_failure_domain(self, *, provider_family: str, backend_ref: str, quota_ref: str, effect_failure_domain_ref: str, independent_disaster_recovery: bool) -> ProviderFailureDomain:
        return ProviderFailureDomain(provider_family, backend_ref, quota_ref, effect_failure_domain_ref, independent_disaster_recovery)

    def connector_pack_split(self, *, connector_pack_ref: str, provider_definition_ref: str, tool_manifest_refs: tuple[str, ...], capability_mapping_refs: tuple[str, ...], scope_mapping_refs: tuple[str, ...], contract_test_refs: tuple[str, ...], reconciliation_extension_refs: tuple[str, ...]) -> ConnectorPackSplit:
        return ConnectorPackSplit(connector_pack_ref, provider_definition_ref, tool_manifest_refs, capability_mapping_refs, scope_mapping_refs, contract_test_refs, reconciliation_extension_refs)

    def availability_snapshot(self, *, snapshot_ref: str, version: str, ttl_seconds: int, source_generation: int) -> CapabilityAvailabilitySnapshot:
        return CapabilityAvailabilitySnapshot(snapshot_ref, version, ttl_seconds, source_generation, immutable=True)

    def availability_entry(self, *, capability_ref: str, status: CapabilityAvailabilityStatus) -> CapabilityAvailabilityEntry:
        return CapabilityAvailabilityEntry(capability_ref, status, candidate_only=status == CapabilityAvailabilityStatus.AVAILABLE, authorization_implied=False)

    def selection_record(self, *, selection_id: str, candidate_refs: tuple[str, ...], hard_filtered_refs: tuple[str, ...], scores: dict[str, float], selected_binding_ref: str, provider_instance_ref: str, fallback_order: tuple[str, ...]) -> CapabilitySelectionRecord:
        return CapabilitySelectionRecord(selection_id, candidate_refs, hard_filtered_refs, _hash(scores), selected_binding_ref, provider_instance_ref, fallback_order, deterministic_commit=True)

    def fallback_verdict(self, *, output_contract_preserved: bool, risk_within_limit: bool, tenant_preserved: bool, data_residency_preserved: bool, side_effect_semantics_preserved: bool) -> CapabilityFallbackVerdict:
        compatible = output_contract_preserved and risk_within_limit and tenant_preserved and data_residency_preserved and side_effect_semantics_preserved
        return CapabilityFallbackVerdict(output_contract_preserved, risk_within_limit, tenant_preserved, data_residency_preserved, side_effect_semantics_preserved, compatible)

    def pinned_versions(self, *, capability_version_ref: str, binding_version_ref: str, tool_definition_ref: str, schema_hash: str) -> CapabilityPinnedVersionSet:
        exact = all(":" in value for value in [capability_version_ref, binding_version_ref, tool_definition_ref, schema_hash])
        return CapabilityPinnedVersionSet(capability_version_ref, binding_version_ref, tool_definition_ref, schema_hash, exact)

    def inventory_change(self, *, inventory_generation: int, tool_definition_version_ref: str, schema_mutated_in_place: bool = False) -> CapabilityInventoryChange:
        return CapabilityInventoryChange(inventory_generation, tool_definition_version_ref, revalidation_required=True, schema_mutated_in_place=schema_mutated_in_place)

    def reuse_verdict(self, *, version_ok: bool, scope_ok: bool, security_epoch_ok: bool, snapshot_ttl_ok: bool, resource_integrity_ok: bool) -> CapabilityReuseVerdict:
        reusable = version_ok and scope_ok and security_epoch_ok and snapshot_ttl_ok and resource_integrity_ok
        return CapabilityReuseVerdict(version_ok, scope_ok, security_epoch_ok, snapshot_ttl_ok, resource_integrity_ok, reusable)

    def security_boundary(self, *, provider_instance_ref: str, credential_scope_ref: str, capability_constraint_ref: str, secret_material_stored: bool, authorization_overridden_by_skill: bool) -> CapabilitySecurityBoundary:
        valid = len({provider_instance_ref, credential_scope_ref, capability_constraint_ref}) == 3 and not secret_material_stored and not authorization_overridden_by_skill
        return CapabilitySecurityBoundary(provider_instance_ref, credential_scope_ref, capability_constraint_ref, secret_material_stored, authorization_overridden_by_skill, valid)

    def constraint_record(self, *, tenant_id: str, workspace_id: str, region: str, data_residency: str, identity_mode: str, resource_scope_ref: str, provider_trust_ref: str) -> CapabilityConstraintRecord:
        return CapabilityConstraintRecord(tenant_id, workspace_id, region, data_residency, identity_mode, resource_scope_ref, provider_trust_ref)

    def audit_boundary(self, *, audit_requirement_ref: str) -> CapabilityAuditBoundary:
        return CapabilityAuditBoundary(audit_requirement_ref, persistence_receipt_owner="11 Infrastructure", audit_event_owner="10 Observability / Eval", selection_propagates_requirement=True)

    def persistence_boundary(self, *, domain_fact_refs: tuple[str, ...], object_payload_refs: tuple[str, ...], projection_refs: tuple[str, ...]) -> CapabilityPersistenceBoundary:
        return CapabilityPersistenceBoundary(domain_fact_refs, object_payload_refs, projection_refs, source_is_projection=False)

    def transaction_record(self, *, transaction_id: str, facts: tuple[str, ...], outbox_event_ref: str) -> CapabilityTransactionRecord:
        return CapabilityTransactionRecord(transaction_id, facts, outbox_event_ref, atomic=bool(facts and outbox_event_ref))

    def transition_record(self, *, transition_id: str, expected_generation: int, committed_generation: int) -> CapabilityTransitionRecord:
        return CapabilityTransitionRecord(transition_id, expected_generation, committed_generation, cas_passed=committed_generation == expected_generation + 1)

    def outbox_record(self, *, event_id: str, consumer_idempotency_key: str) -> CapabilityOutboxRecord:
        return CapabilityOutboxRecord(event_id, delivery_semantics="at_least_once", consumer_idempotency_key=consumer_idempotency_key)

    def recovery_plan(self, **refs: str) -> CapabilityRecoveryPlan:
        return CapabilityRecoveryPlan(**refs)

    def connector_policy(self, *, custom_extension_reason: str | None = None) -> CapabilityConnectorPolicy:
        return CapabilityConnectorPolicy(
            provider_specific_core_branch=False,
            generic_adapter_families=self.generic_adapter_families,
            structured_manifest_required=True,
            draft_only_from_discovery=True,
            custom_extension_reason=custom_extension_reason,
            unknown_effect_retry_allowed=False,
        )

    def trace_event(self, *, event_type: str, trace_ref: str, payload: dict[str, Any]) -> CapabilityTraceEvent:
        redacted = redact_sensitive_payload(payload)
        return CapabilityTraceEvent(event_type, trace_ref, _hash(redacted), redacted)

    def current_evidence_gate(self, **refs: str) -> CapabilityCurrentEvidenceGate:
        return CapabilityCurrentEvidenceGate(**refs)


__all__ = [
    "CapabilityAvailabilityEntry",
    "CapabilityAvailabilitySnapshot",
    "CapabilityAvailabilityStatus",
    "CapabilityAuditBoundary",
    "CapabilityBoundaryDecision",
    "CapabilityConceptTaxonomy",
    "CapabilityConnectorPolicy",
    "CapabilityConstraintRecord",
    "CapabilityCurrentEvidenceGate",
    "CapabilityDecisionStatus",
    "CapabilityDefinitionRecord",
    "CapabilityEnvelope",
    "CapabilityFallbackVerdict",
    "CapabilityInventoryChange",
    "CapabilityOutboxRecord",
    "CapabilityPersistenceBoundary",
    "CapabilityPinnedVersionSet",
    "CapabilityProviderBindingRecord",
    "CapabilityRecoveryPlan",
    "CapabilityResultValidity",
    "CapabilityReuseVerdict",
    "CapabilityRuntimeBatch",
    "CapabilitySecurityBoundary",
    "CapabilitySelectionRecord",
    "CapabilityTraceEvent",
    "CapabilityTransactionRecord",
    "CapabilityTransitionRecord",
    "CapabilityUnknownContractVerdict",
    "CapabilityVersionRecord",
    "ConnectorPackSplit",
    "ProviderConformanceRecord",
    "ProviderFailureDomain",
    "SkillDiscoveryResult",
    "SkillLoadResult",
    "SkillPolicyVerdict",
    "SkillResourceClassification",
    "SkillVersionRecord",
]
