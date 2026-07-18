from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any

from zuno.platform.security.governance import redact_sensitive_payload


def _hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class AuthorizationVerdict(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    QUARANTINE = "QUARANTINE"


class TrustLabel(StrEnum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    WORKSPACE = "WORKSPACE"
    UNTRUSTED = "UNTRUSTED"


class Classification(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    SECRET = "SECRET"


class SandboxTier(StrEnum):
    NONE = "NONE"
    READ_ONLY = "READ_ONLY"
    NETWORK_LIMITED = "NETWORK_LIMITED"
    EXECUTION_RESTRICTED = "EXECUTION_RESTRICTED"
    ISOLATED = "ISOLATED"


@dataclass(frozen=True, slots=True)
class PrincipalContext:
    principal_ref: str
    principal_type: str
    tenant_id: str
    workspace_id: str
    workload_identity_ref: str
    identity_chain: tuple[str, ...]
    trusted: bool


@dataclass(frozen=True, slots=True)
class SecurityContext:
    context_ref: str
    principal_ref: str
    tenant_id: str
    workspace_id: str
    task_ref: str
    session_ref: str
    effective_action_set: tuple[str, ...]
    epoch_ref: str


@dataclass(frozen=True, slots=True)
class OrgUnitRecord:
    org_unit_ref: str
    parent_ref: str | None
    ancestor_refs: tuple[str, ...]
    acyclic: bool


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    membership_ref: str
    principal_ref: str
    org_unit_ref: str
    resource_scope_ref: str
    delegated_admin_scope_ref: str


@dataclass(frozen=True, slots=True)
class UiPermissionMapping:
    ui_level: str
    action_set_ref: str
    actions: tuple[str, ...]
    can_delegate: bool


@dataclass(frozen=True, slots=True)
class GrantLineage:
    grant_ref: str
    parent_grant_ref: str | None
    delegated_actions: tuple[str, ...]
    parent_actions: tuple[str, ...]
    amplification_blocked: bool
    revoked_by_parent: bool


@dataclass(frozen=True, slots=True)
class TaskGrantRecord:
    grant_ref: str
    user_actions: tuple[str, ...]
    agent_actions: tuple[str, ...]
    task_actions: tuple[str, ...]
    session_actions: tuple[str, ...]
    effective_actions: tuple[str, ...]
    expires_at_ref: str


@dataclass(frozen=True, slots=True)
class PolicyVersionRecord:
    policy_ref: str
    version: str
    schema_hash: str
    immutable: bool
    active_generation: int


@dataclass(frozen=True, slots=True)
class PolicyPlaneRecord:
    pap_ref: str
    pdp_ref: str
    pep_ref: str
    pip_ref: str
    validation_report_ref: str
    simulation_report_ref: str
    shadow_evaluation_ref: str


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    decision_ref: str
    verdict: AuthorizationVerdict
    explicit_deny: bool
    default_deny_applied: bool
    explanation_ref: str
    policy_version_ref: str
    epoch_ref: str


@dataclass(frozen=True, slots=True)
class EffectiveSecurityEpoch:
    epoch_ref: str
    policy_generation: int
    grant_generation: int
    revocation_generation: int
    credential_generation: int
    cache_key_hash: str


@dataclass(frozen=True, slots=True)
class DetectionDecision:
    detection_ref: str
    profile_ref: str
    input_hash: str
    findings: tuple[str, ...]
    classification: Classification


@dataclass(frozen=True, slots=True)
class RedactionDecision:
    redaction_ref: str
    profile_ref: str
    input_hash: str
    output_hash: str
    findings: tuple[str, ...]
    reversible: bool
    evidence_ref: str
    export_allowed: bool


@dataclass(frozen=True, slots=True)
class InformationFlowDecision:
    flow_ref: str
    source_label: TrustLabel
    sink_ref: str
    declassification_ref: str | None
    protected_sink_policy_ref: str
    allowed: bool


@dataclass(frozen=True, slots=True)
class ActionIntentBinding:
    binding_ref: str
    user_goal_hash: str
    action_hash: str
    ambiguous: bool
    model_can_self_authorize: bool


@dataclass(frozen=True, slots=True)
class DomainGateDecision:
    gate_ref: str
    domain: str
    authorization_ref: str
    classification: Classification
    allowed: bool


@dataclass(frozen=True, slots=True)
class ModelSecurityDecision:
    decision_ref: str
    provider_ref: str
    residency_ref: str
    redaction_ref: str
    allowed: bool


@dataclass(frozen=True, slots=True)
class ActionAuthorizationDecision:
    decision_ref: str
    prepared_action_hash: str
    principal_ref: str
    task_ref: str
    policy_version_ref: str
    epoch_ref: str
    verdict: AuthorizationVerdict


@dataclass(frozen=True, slots=True)
class SecurityApprovalDecision:
    approval_ref: str
    prepared_action_hash: str
    principal_ref: str
    task_ref: str
    policy_version_ref: str
    epoch_ref: str
    ttl_ref: str
    nonce_ref: str
    accepted: bool
    replayable: bool


@dataclass(frozen=True, slots=True)
class EffectReconciliationRequirement:
    requirement_ref: str
    unknown_effect_ref: str
    retry_allowed_before_reconcile: bool


@dataclass(frozen=True, slots=True)
class CredentialPolicyDecision:
    decision_ref: str
    audience: str
    token_passthrough_allowed: bool
    on_behalf_of_binding_ref: str
    credential_version_ref: str


@dataclass(frozen=True, slots=True)
class SecretLeaseDecision:
    secret_ref: str
    lease_ref: str
    ttl_seconds: int
    prompt_trace_memory_allowed: bool


@dataclass(frozen=True, slots=True)
class SandboxDecision:
    sandbox_ref: str
    tier: SandboxTier
    network_egress_policy_ref: str
    ssrf_blocked: bool
    fail_closed: bool


@dataclass(frozen=True, slots=True)
class SupplyChainDecision:
    artifact_ref: str
    provenance_hash: str
    trust_decision_ref: str
    status: AuthorizationVerdict


@dataclass(frozen=True, slots=True)
class BreakGlassSession:
    session_ref: str
    scope_refs: tuple[str, ...]
    expires_at_ref: str
    audit_required: bool
    limited: bool


@dataclass(frozen=True, slots=True)
class SecurityIncidentRecord:
    incident_ref: str
    severity: str
    finding_refs: tuple[str, ...]
    response_owner: str


@dataclass(frozen=True, slots=True)
class SecurityPersistenceBoundary:
    security_fact_ref: str
    outbox_event_ref: str
    same_transaction: bool
    storage_owner: str
    checkpoint_is_fact_source: bool


@dataclass(frozen=True, slots=True)
class SecurityAuditRequirement:
    requirement_ref: str
    before_effect: bool
    audit_owner: str
    domain_owner_transferred: bool


@dataclass(frozen=True, slots=True)
class SecurityRecoveryContract:
    recovery_ref: str
    idempotency_ref: str
    retry_policy_ref: str
    stale_epoch_rejected: bool


@dataclass(frozen=True, slots=True)
class ProductSecurityProjection:
    projection_ref: str
    backend_decision_ref: str
    frontend_is_fact_source: bool


@dataclass(frozen=True, slots=True)
class SecurityEvalGate:
    eval_ref: str
    adaptive_attack_ref: str
    utility_ref: str
    release_gate_ref: str
    attack_success_rate: float
    utility_preserved: bool
    passed: bool


@dataclass(frozen=True, slots=True)
class SecurityReadinessEvidence:
    requirement_ids: tuple[str, ...]
    code_refs: tuple[str, ...]
    test_refs: tuple[str, ...]
    verifier_ref: str
    evidence_ref: str
    implementation_available: bool


class SecurityRuntimeBatch:
    requirement_ids = tuple(f"ARCH-SEC-{index:03d}" for index in range(1, 61))

    def principal_context(self, *, principal_ref: str, principal_type: str, tenant_id: str, workspace_id: str, workload_identity_ref: str, identity_chain: tuple[str, ...]) -> PrincipalContext:
        return PrincipalContext(principal_ref, principal_type, tenant_id, workspace_id, workload_identity_ref, identity_chain, trusted=bool(identity_chain and tenant_id and workspace_id))

    def security_context(self, *, context_ref: str, principal: PrincipalContext, task_ref: str, session_ref: str, action_sets: tuple[tuple[str, ...], ...], epoch_ref: str) -> SecurityContext:
        effective = set(action_sets[0]) if action_sets else set()
        for action_set in action_sets[1:]:
            effective &= set(action_set)
        return SecurityContext(context_ref, principal.principal_ref, principal.tenant_id, principal.workspace_id, task_ref, session_ref, tuple(sorted(effective)), epoch_ref)

    def org_unit(self, *, org_unit_ref: str, parent_ref: str | None, ancestor_refs: tuple[str, ...]) -> OrgUnitRecord:
        return OrgUnitRecord(org_unit_ref, parent_ref, ancestor_refs, acyclic=org_unit_ref not in ancestor_refs and parent_ref != org_unit_ref)

    def membership(self, *, membership_ref: str, principal_ref: str, org_unit_ref: str, resource_scope_ref: str, delegated_admin_scope_ref: str) -> MembershipRecord:
        return MembershipRecord(membership_ref, principal_ref, org_unit_ref, resource_scope_ref, delegated_admin_scope_ref)

    def ui_permission(self, *, ui_level: str, action_set_ref: str) -> UiPermissionMapping:
        mapping = {
            "DENY": (),
            "USE_ONLY": ("resource.read", "tool.prepare"),
            "USE_AND_DELEGATE": ("resource.read", "tool.prepare", "grant.delegate"),
        }
        actions = mapping.get(ui_level, ())
        return UiPermissionMapping(ui_level, action_set_ref, actions, can_delegate="grant.delegate" in actions)

    def grant_lineage(self, *, grant_ref: str, parent_grant_ref: str | None, delegated_actions: tuple[str, ...], parent_actions: tuple[str, ...], parent_revoked: bool) -> GrantLineage:
        amplification = not set(delegated_actions) <= set(parent_actions)
        return GrantLineage(grant_ref, parent_grant_ref, delegated_actions, parent_actions, amplification_blocked=amplification, revoked_by_parent=parent_revoked)

    def task_grant(self, *, grant_ref: str, user_actions: tuple[str, ...], agent_actions: tuple[str, ...], task_actions: tuple[str, ...], session_actions: tuple[str, ...], expires_at_ref: str) -> TaskGrantRecord:
        effective = set(user_actions) & set(agent_actions) & set(task_actions) & set(session_actions)
        return TaskGrantRecord(grant_ref, user_actions, agent_actions, task_actions, session_actions, tuple(sorted(effective)), expires_at_ref)

    def policy_version(self, *, policy_ref: str, version: str, schema: dict[str, Any], active_generation: int) -> PolicyVersionRecord:
        return PolicyVersionRecord(policy_ref, version, _hash(schema), immutable=True, active_generation=active_generation)

    def policy_plane(self, *, pap_ref: str, pdp_ref: str, pep_ref: str, pip_ref: str, validation_report_ref: str, simulation_report_ref: str, shadow_evaluation_ref: str) -> PolicyPlaneRecord:
        return PolicyPlaneRecord(pap_ref, pdp_ref, pep_ref, pip_ref, validation_report_ref, simulation_report_ref, shadow_evaluation_ref)

    def authorize(self, *, decision_ref: str, requested_actions: tuple[str, ...], effective_actions: tuple[str, ...], explicit_deny: bool, policy_version_ref: str, epoch_ref: str) -> AuthorizationDecision:
        allowed = set(requested_actions) <= set(effective_actions)
        verdict = AuthorizationVerdict.DENY if explicit_deny or not allowed else AuthorizationVerdict.ALLOW
        return AuthorizationDecision(decision_ref, verdict, explicit_deny, default_deny_applied=not explicit_deny and not allowed, explanation_ref=f"explain:{decision_ref}", policy_version_ref=policy_version_ref, epoch_ref=epoch_ref)

    def epoch(self, *, epoch_ref: str, policy_generation: int, grant_generation: int, revocation_generation: int, credential_generation: int) -> EffectiveSecurityEpoch:
        return EffectiveSecurityEpoch(epoch_ref, policy_generation, grant_generation, revocation_generation, credential_generation, _hash([policy_generation, grant_generation, revocation_generation, credential_generation]))

    def detect(self, *, detection_ref: str, profile_ref: str, payload: dict[str, Any], findings: tuple[str, ...], classification: Classification) -> DetectionDecision:
        return DetectionDecision(detection_ref, profile_ref, _hash(payload), findings, classification)

    def redact(self, *, redaction_ref: str, profile_ref: str, payload: dict[str, Any], findings: tuple[str, ...], evidence_ref: str, adapter_failed: bool = False) -> RedactionDecision:
        redacted = redact_sensitive_payload(payload)
        return RedactionDecision(redaction_ref, profile_ref, _hash(payload), _hash(redacted), findings, reversible=False, evidence_ref=evidence_ref, export_allowed=not adapter_failed)

    def information_flow(self, *, flow_ref: str, source_label: TrustLabel, sink_ref: str, protected_sink_policy_ref: str, declassification_ref: str | None = None) -> InformationFlowDecision:
        allowed = source_label is not TrustLabel.UNTRUSTED or bool(declassification_ref)
        return InformationFlowDecision(flow_ref, source_label, sink_ref, declassification_ref, protected_sink_policy_ref, allowed)

    def action_intent(self, *, binding_ref: str, user_goal: str, action_payload: dict[str, Any], ambiguous: bool) -> ActionIntentBinding:
        return ActionIntentBinding(binding_ref, _hash(user_goal), _hash(action_payload), ambiguous, model_can_self_authorize=False)

    def domain_gate(self, *, gate_ref: str, domain: str, authorization_ref: str, classification: Classification, allowed: bool) -> DomainGateDecision:
        return DomainGateDecision(gate_ref, domain, authorization_ref, classification, allowed)

    def model_security(self, *, decision_ref: str, provider_ref: str, residency_ref: str, redaction_ref: str, residency_allowed: bool) -> ModelSecurityDecision:
        return ModelSecurityDecision(decision_ref, provider_ref, residency_ref, redaction_ref, residency_allowed)

    def action_authorization(self, *, decision_ref: str, prepared_action_hash: str, principal_ref: str, task_ref: str, policy_version_ref: str, epoch_ref: str, allowed: bool) -> ActionAuthorizationDecision:
        return ActionAuthorizationDecision(decision_ref, prepared_action_hash, principal_ref, task_ref, policy_version_ref, epoch_ref, AuthorizationVerdict.ALLOW if allowed else AuthorizationVerdict.DENY)

    def approval(self, *, approval_ref: str, prepared_action_hash: str, principal_ref: str, task_ref: str, policy_version_ref: str, epoch_ref: str, ttl_ref: str, nonce_ref: str, accepted: bool) -> SecurityApprovalDecision:
        return SecurityApprovalDecision(approval_ref, prepared_action_hash, principal_ref, task_ref, policy_version_ref, epoch_ref, ttl_ref, nonce_ref, accepted, replayable=False)

    def effect_reconciliation_requirement(self, *, requirement_ref: str, unknown_effect_ref: str) -> EffectReconciliationRequirement:
        return EffectReconciliationRequirement(requirement_ref, unknown_effect_ref, retry_allowed_before_reconcile=False)

    def credential_policy(self, *, decision_ref: str, audience: str, on_behalf_of_binding_ref: str, credential_version_ref: str) -> CredentialPolicyDecision:
        return CredentialPolicyDecision(decision_ref, audience, token_passthrough_allowed=False, on_behalf_of_binding_ref=on_behalf_of_binding_ref, credential_version_ref=credential_version_ref)

    def secret_lease(self, *, secret_ref: str, lease_ref: str, ttl_seconds: int) -> SecretLeaseDecision:
        return SecretLeaseDecision(secret_ref, lease_ref, ttl_seconds, prompt_trace_memory_allowed=False)

    def sandbox(self, *, sandbox_ref: str, tier: SandboxTier, network_egress_policy_ref: str, ssrf_attempt: bool) -> SandboxDecision:
        return SandboxDecision(sandbox_ref, tier, network_egress_policy_ref, ssrf_blocked=ssrf_attempt, fail_closed=tier is SandboxTier.ISOLATED or ssrf_attempt)

    def supply_chain(self, *, artifact_ref: str, provenance: dict[str, Any], trust_decision_ref: str, trusted: bool) -> SupplyChainDecision:
        return SupplyChainDecision(artifact_ref, _hash(provenance), trust_decision_ref, AuthorizationVerdict.ALLOW if trusted else AuthorizationVerdict.QUARANTINE)

    def break_glass(self, *, session_ref: str, scope_refs: tuple[str, ...], expires_at_ref: str) -> BreakGlassSession:
        return BreakGlassSession(session_ref, scope_refs, expires_at_ref, audit_required=True, limited=bool(scope_refs and expires_at_ref))

    def incident(self, *, incident_ref: str, severity: str, finding_refs: tuple[str, ...]) -> SecurityIncidentRecord:
        return SecurityIncidentRecord(incident_ref, severity, finding_refs, response_owner="09 Security")

    def persistence_boundary(self, *, security_fact_ref: str, outbox_event_ref: str) -> SecurityPersistenceBoundary:
        return SecurityPersistenceBoundary(security_fact_ref, outbox_event_ref, same_transaction=bool(security_fact_ref and outbox_event_ref), storage_owner="PostgreSQL security facts", checkpoint_is_fact_source=False)

    def audit_requirement(self, *, requirement_ref: str) -> SecurityAuditRequirement:
        return SecurityAuditRequirement(requirement_ref, before_effect=True, audit_owner="10 Observability / Eval", domain_owner_transferred=False)

    def recovery_contract(self, *, recovery_ref: str, idempotency_ref: str, retry_policy_ref: str) -> SecurityRecoveryContract:
        return SecurityRecoveryContract(recovery_ref, idempotency_ref, retry_policy_ref, stale_epoch_rejected=True)

    def product_projection(self, *, projection_ref: str, backend_decision_ref: str) -> ProductSecurityProjection:
        return ProductSecurityProjection(projection_ref, backend_decision_ref, frontend_is_fact_source=False)

    def eval_gate(self, *, eval_ref: str, adaptive_attack_ref: str, utility_ref: str, release_gate_ref: str, attack_success_rate: float, utility_preserved: bool) -> SecurityEvalGate:
        return SecurityEvalGate(eval_ref, adaptive_attack_ref, utility_ref, release_gate_ref, attack_success_rate, utility_preserved, passed=attack_success_rate == 0 and utility_preserved)

    def readiness_evidence(self, *, code_refs: tuple[str, ...], test_refs: tuple[str, ...], verifier_ref: str, evidence_ref: str) -> SecurityReadinessEvidence:
        return SecurityReadinessEvidence(self.requirement_ids, code_refs, test_refs, verifier_ref, evidence_ref, bool(code_refs and test_refs and verifier_ref and evidence_ref and len(self.requirement_ids) == 60))


__all__ = [
    "ActionAuthorizationDecision",
    "ActionIntentBinding",
    "AuthorizationDecision",
    "AuthorizationVerdict",
    "BreakGlassSession",
    "Classification",
    "CredentialPolicyDecision",
    "DetectionDecision",
    "DomainGateDecision",
    "EffectiveSecurityEpoch",
    "EffectReconciliationRequirement",
    "GrantLineage",
    "InformationFlowDecision",
    "MembershipRecord",
    "ModelSecurityDecision",
    "OrgUnitRecord",
    "PolicyPlaneRecord",
    "PolicyVersionRecord",
    "PrincipalContext",
    "ProductSecurityProjection",
    "RedactionDecision",
    "SandboxDecision",
    "SandboxTier",
    "SecretLeaseDecision",
    "SecurityApprovalDecision",
    "SecurityAuditRequirement",
    "SecurityContext",
    "SecurityEvalGate",
    "SecurityIncidentRecord",
    "SecurityPersistenceBoundary",
    "SecurityReadinessEvidence",
    "SecurityRecoveryContract",
    "SecurityRuntimeBatch",
    "SupplyChainDecision",
    "TaskGrantRecord",
    "TrustLabel",
    "UiPermissionMapping",
]
