from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.platform.security.runtime_batch import (  # noqa: E402
    AuthorizationVerdict,
    Classification,
    SandboxTier,
    SecurityRuntimeBatch,
    TrustLabel,
)


REQUIREMENTS = tuple(f"ARCH-SEC-{index:03d}" for index in range(1, 61))


def verify_security_runtime_batch() -> list[str]:
    errors: list[str] = []
    runtime = SecurityRuntimeBatch()

    principal = runtime.principal_context(
        principal_ref="principal:user:1",
        principal_type="user",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        workload_identity_ref="workload:web:1",
        identity_chain=("idp:okta:user:1", "session:1"),
    )
    context = runtime.security_context(
        context_ref="security-context:1",
        principal=principal,
        task_ref="task:1",
        session_ref="session:1",
        action_sets=(("resource.read", "tool.prepare", "grant.delegate"), ("resource.read", "tool.prepare"), ("resource.read",)),
        epoch_ref="epoch:1",
    )
    org = runtime.org_unit(org_unit_ref="org:legal", parent_ref="org:root", ancestor_refs=("org:root",))
    membership = runtime.membership(membership_ref="membership:1", principal_ref=principal.principal_ref, org_unit_ref=org.org_unit_ref, resource_scope_ref="resource-scope:legal", delegated_admin_scope_ref="delegated-admin:legal")
    use_only = runtime.ui_permission(ui_level="USE_ONLY", action_set_ref="action-set:use")
    delegate = runtime.ui_permission(ui_level="USE_AND_DELEGATE", action_set_ref="action-set:delegate")
    lineage = runtime.grant_lineage(grant_ref="grant:child", parent_grant_ref="grant:parent", delegated_actions=("resource.read", "grant.delegate"), parent_actions=("resource.read",), parent_revoked=True)
    grant = runtime.task_grant(grant_ref="task-grant:1", user_actions=("resource.read", "tool.prepare"), agent_actions=("resource.read", "tool.prepare"), task_actions=("resource.read",), session_actions=("resource.read",), expires_at_ref="expires:soon")
    policy = runtime.policy_version(policy_ref="policy:workspace", version="1.0.0", schema={"rules": [{"effect": "allow"}]}, active_generation=3)
    plane = runtime.policy_plane(pap_ref="pap:1", pdp_ref="pdp:1", pep_ref="pep:1", pip_ref="pip:1", validation_report_ref="validation:1", simulation_report_ref="simulation:1", shadow_evaluation_ref="shadow:1")
    denied = runtime.authorize(decision_ref="authz:deny", requested_actions=("tool.execute",), effective_actions=context.effective_action_set, explicit_deny=True, policy_version_ref=policy.policy_ref, epoch_ref=context.epoch_ref)
    default_denied = runtime.authorize(decision_ref="authz:default", requested_actions=("tool.execute",), effective_actions=context.effective_action_set, explicit_deny=False, policy_version_ref=policy.policy_ref, epoch_ref=context.epoch_ref)
    epoch = runtime.epoch(epoch_ref="epoch:1", policy_generation=3, grant_generation=4, revocation_generation=5, credential_generation=6)
    if not principal.trusted:
        errors.append("ARCH-SEC-001 trusted principal/workload identity chain missing")
    if principal.tenant_id != context.tenant_id or principal.workspace_id != context.workspace_id:
        errors.append("ARCH-SEC-002 tenant/workspace isolation missing")
    if not org.acyclic:
        errors.append("ARCH-SEC-003 org unit cycle accepted")
    if membership.resource_scope_ref == membership.delegated_admin_scope_ref:
        errors.append("ARCH-SEC-004/005 membership/resource/delegated admin scopes conflated")
    if use_only.can_delegate or not delegate.can_delegate:
        errors.append("ARCH-SEC-006 UI permission mapping invalid")
    if "tool.execute" in context.effective_action_set:
        errors.append("ARCH-SEC-007/014 effective action set did not intersect")
    if denied.verdict != AuthorizationVerdict.DENY or not denied.explicit_deny:
        errors.append("ARCH-SEC-008 explicit deny not first")
    if not default_denied.default_deny_applied:
        errors.append("ARCH-SEC-009 default deny missing")
    if not (lineage.amplification_blocked and lineage.revoked_by_parent):
        errors.append("ARCH-SEC-010/011 grant amplification/revocation cascade missing")
    if not grant.expires_at_ref or grant.effective_actions != ("resource.read",):
        errors.append("ARCH-SEC-012/013 task/session grant not temporary/intersection based")
    if not policy.schema_hash or not policy.immutable:
        errors.append("ARCH-SEC-015/017 policy schema/immutability missing")
    if not (plane.pap_ref and plane.pdp_ref and plane.pep_ref and plane.pip_ref and plane.simulation_report_ref and plane.shadow_evaluation_ref):
        errors.append("ARCH-SEC-016/018 policy plane/simulation/shadow missing")
    if not denied.explanation_ref:
        errors.append("ARCH-SEC-019 decision explanation missing")
    if not epoch.cache_key_hash:
        errors.append("ARCH-SEC-020 epoch/cache consistency hash missing")

    detection = runtime.detect(detection_ref="detect:input:1", profile_ref="detect-profile:pii", payload={"text": "token sk-secret"}, findings=("secret_detected",), classification=Classification.SECRET)
    output_detection = runtime.detect(detection_ref="detect:output:1", profile_ref="detect-profile:output", payload={"text": "answer"}, findings=(), classification=Classification.INTERNAL)
    redaction_failed = runtime.redact(redaction_ref="redact:failed", profile_ref="redact-profile:default", payload={"api_key": "sk-secret"}, findings=("secret_detected",), evidence_ref="evidence:redaction", adapter_failed=True)
    untrusted_flow = runtime.information_flow(flow_ref="flow:untrusted", source_label=TrustLabel.UNTRUSTED, sink_ref="sink:tool", protected_sink_policy_ref="sink-policy:tool")
    declassified_flow = runtime.information_flow(flow_ref="flow:declassified", source_label=TrustLabel.UNTRUSTED, sink_ref="sink:answer", protected_sink_policy_ref="sink-policy:answer", declassification_ref="declassify:1")
    intent = runtime.action_intent(binding_ref="intent:tool:1", user_goal="Send approved summary", action_payload={"tool": "mail.send"}, ambiguous=True)
    if not detection.findings or not output_detection.input_hash:
        errors.append("ARCH-SEC-021/022 input/output detection missing")
    if detection.classification != Classification.SECRET:
        errors.append("ARCH-SEC-023 data classification not propagated")
    if redaction_failed.export_allowed:
        errors.append("ARCH-SEC-024 redaction failure exported")
    if untrusted_flow.source_label != TrustLabel.UNTRUSTED:
        errors.append("ARCH-SEC-025 instruction trust label missing")
    if untrusted_flow.allowed:
        errors.append("ARCH-SEC-026/028 untrusted data controlled protected sink")
    if not declassified_flow.allowed or not declassified_flow.declassification_ref:
        errors.append("ARCH-SEC-027/029 information flow/declassification invalid")
    if intent.model_can_self_authorize or not intent.ambiguous:
        errors.append("ARCH-SEC-030 ambiguous action intent self-authorized")

    memory_gate = runtime.domain_gate(gate_ref="memory-gate:1", domain="memory", authorization_ref="authz:memory", classification=Classification.CONFIDENTIAL, allowed=False)
    multimodal_gate = runtime.domain_gate(gate_ref="multimodal-gate:1", domain="multimodal", authorization_ref="authz:image", classification=Classification.INTERNAL, allowed=True)
    retrieval_gate = runtime.domain_gate(gate_ref="retrieval-gate:1", domain="knowledge", authorization_ref="authz:retrieval", classification=Classification.CONFIDENTIAL, allowed=True)
    citation_gate = runtime.domain_gate(gate_ref="citation-gate:1", domain="citation", authorization_ref="authz:citation", classification=Classification.CONFIDENTIAL, allowed=True)
    model_gate = runtime.model_security(decision_ref="model-security:1", provider_ref="model:provider", residency_ref="residency:us", redaction_ref=redaction_failed.redaction_ref, residency_allowed=True)
    action_auth = runtime.action_authorization(decision_ref="action-auth:1", prepared_action_hash="hash:prepared:1", principal_ref=principal.principal_ref, task_ref="task:1", policy_version_ref=policy.policy_ref, epoch_ref=epoch.epoch_ref, allowed=True)
    approval = runtime.approval(approval_ref="approval:1", prepared_action_hash=action_auth.prepared_action_hash, principal_ref=action_auth.principal_ref, task_ref=action_auth.task_ref, policy_version_ref=action_auth.policy_version_ref, epoch_ref=action_auth.epoch_ref, ttl_ref="ttl:short", nonce_ref="nonce:1", accepted=True)
    reconcile = runtime.effect_reconciliation_requirement(requirement_ref="reconcile:unknown-effect", unknown_effect_ref="effect:unknown:1")
    if memory_gate.allowed:
        errors.append("ARCH-SEC-031 memory poisoning quarantine missing")
    if not multimodal_gate.allowed:
        errors.append("ARCH-SEC-032 multimodal isolation gate missing")
    if not (retrieval_gate.allowed and citation_gate.allowed):
        errors.append("ARCH-SEC-033/034 retrieval/citation authorization missing")
    if not model_gate.allowed or not model_gate.redaction_ref:
        errors.append("ARCH-SEC-035 model provider/residency/redaction gate invalid")
    if not action_auth.prepared_action_hash:
        errors.append("ARCH-SEC-036 prepared action hash missing")
    if approval.replayable or not (approval.ttl_ref and approval.nonce_ref):
        errors.append("ARCH-SEC-037 approval replay protection missing")
    if approval.epoch_ref != epoch.epoch_ref:
        errors.append("ARCH-SEC-038 execute-time epoch review missing")
    if reconcile.retry_allowed_before_reconcile:
        errors.append("ARCH-SEC-039 unknown tool effect retry allowed before reconcile")

    credential = runtime.credential_policy(decision_ref="credential:1", audience="mcp:lark", on_behalf_of_binding_ref="obo:user:agent:1", credential_version_ref="credential-version:1")
    secret = runtime.secret_lease(secret_ref="secret:mail", lease_ref="lease:mail:1", ttl_seconds=60)
    sandbox = runtime.sandbox(sandbox_ref="sandbox:tool:1", tier=SandboxTier.ISOLATED, network_egress_policy_ref="egress:deny", ssrf_attempt=True)
    supply_chain = runtime.supply_chain(artifact_ref="artifact:skill:1", provenance={"builder": "ci", "sha": "abc"}, trust_decision_ref="trust:artifact:1", trusted=False)
    break_glass = runtime.break_glass(session_ref="break-glass:1", scope_refs=("workspace:a",), expires_at_ref="expires:short")
    incident = runtime.incident(incident_ref="incident:1", severity="high", finding_refs=("finding:secret",))
    persistence = runtime.persistence_boundary(security_fact_ref="security-fact:approval:1", outbox_event_ref="outbox:security:1")
    audit = runtime.audit_requirement(requirement_ref="audit:before-effect")
    recovery = runtime.recovery_contract(recovery_ref="recovery:security:1", idempotency_ref="idempotency:approval:1", retry_policy_ref="retry:security:1")
    projection = runtime.product_projection(projection_ref="product-security-view:1", backend_decision_ref="authz:1")
    eval_gate = runtime.eval_gate(eval_ref="security-eval:1", adaptive_attack_ref="attack:adaptive:1", utility_ref="utility:benign:1", release_gate_ref="release-gate:security:1", attack_success_rate=0, utility_preserved=True)
    readiness = runtime.readiness_evidence(code_refs=("src/backend/zuno/platform/security/runtime_batch.py",), test_refs=("tests/security/test_security_runtime_batch.py",), verifier_ref="tools/scripts/verify_security_runtime_batch.py", evidence_ref="docs/evidence/security-runtime-batch.md")
    if not credential.audience or credential.token_passthrough_allowed:
        errors.append("ARCH-SEC-040/041 MCP audience/token passthrough invalid")
    if not credential.on_behalf_of_binding_ref:
        errors.append("ARCH-SEC-042 on-behalf-of binding missing")
    if not secret.lease_ref or secret.ttl_seconds <= 0:
        errors.append("ARCH-SEC-043 secret short lease missing")
    if secret.prompt_trace_memory_allowed:
        errors.append("ARCH-SEC-044 secret can enter prompt/trace/memory")
    if sandbox.tier != SandboxTier.ISOLATED or not sandbox.ssrf_blocked or not sandbox.fail_closed:
        errors.append("ARCH-SEC-045/046 sandbox/network/SSRF fail-closed invalid")
    if not supply_chain.provenance_hash or supply_chain.status != AuthorizationVerdict.QUARANTINE:
        errors.append("ARCH-SEC-047/048 supply-chain provenance/trust lifecycle invalid")
    if not break_glass.limited or not break_glass.audit_required:
        errors.append("ARCH-SEC-049 break-glass not limited/audited")
    if incident.response_owner != "09 Security":
        errors.append("ARCH-SEC-050 incident owner invalid")
    if not persistence.same_transaction:
        errors.append("ARCH-SEC-051 security fact/outbox transaction missing")
    if not audit.before_effect:
        errors.append("ARCH-SEC-052 mandatory audit before effect missing")
    if audit.domain_owner_transferred:
        errors.append("ARCH-SEC-053 audit transferred domain ownership")
    if not recovery.stale_epoch_rejected or not (recovery.idempotency_ref and recovery.retry_policy_ref):
        errors.append("ARCH-SEC-054 retry/idempotency/recovery invalid")
    if persistence.storage_owner != "PostgreSQL security facts":
        errors.append("ARCH-SEC-055 PostgreSQL security fact source missing")
    if persistence.checkpoint_is_fact_source:
        errors.append("ARCH-SEC-056 checkpointer became security fact source")
    if projection.frontend_is_fact_source:
        errors.append("ARCH-SEC-057 frontend became security fact source")
    if not eval_gate.passed or not (eval_gate.adaptive_attack_ref and eval_gate.utility_ref and eval_gate.release_gate_ref):
        errors.append("ARCH-SEC-058/059 adaptive security eval/release gate invalid")
    if readiness.requirement_ids != REQUIREMENTS or not readiness.implementation_available:
        errors.append("ARCH-SEC-060 readiness evidence does not cover ARCH-SEC-001..060")
    return errors


def main() -> int:
    errors = verify_security_runtime_batch()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Security runtime batch verifier passed for ARCH-SEC-001..060")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
