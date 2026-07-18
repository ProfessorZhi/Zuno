from __future__ import annotations

from zuno.platform.security.runtime_batch import (
    AuthorizationVerdict,
    Classification,
    SandboxTier,
    SecurityRuntimeBatch,
    TrustLabel,
)


def test_security_runtime_batch_identity_authorization_policy_and_epoch() -> None:
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
        action_sets=(
            ("resource.read", "tool.prepare", "grant.delegate"),
            ("resource.read", "tool.prepare"),
            ("tool.prepare", "resource.read"),
        ),
        epoch_ref="epoch:1",
    )
    org = runtime.org_unit(org_unit_ref="org:legal", parent_ref="org:root", ancestor_refs=("org:root",))
    membership = runtime.membership(
        membership_ref="membership:1",
        principal_ref=principal.principal_ref,
        org_unit_ref=org.org_unit_ref,
        resource_scope_ref="resource-scope:legal",
        delegated_admin_scope_ref="delegated-admin:legal",
    )
    use_only = runtime.ui_permission(ui_level="USE_ONLY", action_set_ref="action-set:use")
    delegate = runtime.ui_permission(ui_level="USE_AND_DELEGATE", action_set_ref="action-set:delegate")
    lineage = runtime.grant_lineage(
        grant_ref="grant:child",
        parent_grant_ref="grant:parent",
        delegated_actions=("resource.read", "grant.delegate"),
        parent_actions=("resource.read",),
        parent_revoked=True,
    )
    grant = runtime.task_grant(
        grant_ref="task-grant:1",
        user_actions=("resource.read", "tool.prepare"),
        agent_actions=("resource.read", "tool.prepare", "tool.execute"),
        task_actions=("resource.read", "tool.prepare"),
        session_actions=("resource.read",),
        expires_at_ref="expires:soon",
    )
    policy = runtime.policy_version(
        policy_ref="policy:workspace",
        version="1.0.0",
        schema={"rules": [{"effect": "allow", "action": "resource.read"}]},
        active_generation=3,
    )
    plane = runtime.policy_plane(
        pap_ref="pap:1",
        pdp_ref="pdp:1",
        pep_ref="pep:1",
        pip_ref="pip:1",
        validation_report_ref="validation:1",
        simulation_report_ref="simulation:1",
        shadow_evaluation_ref="shadow:1",
    )
    denied = runtime.authorize(
        decision_ref="authz:deny",
        requested_actions=("tool.execute",),
        effective_actions=context.effective_action_set,
        explicit_deny=True,
        policy_version_ref=policy.policy_ref,
        epoch_ref=context.epoch_ref,
    )
    default_denied = runtime.authorize(
        decision_ref="authz:default-deny",
        requested_actions=("tool.execute",),
        effective_actions=context.effective_action_set,
        explicit_deny=False,
        policy_version_ref=policy.policy_ref,
        epoch_ref=context.epoch_ref,
    )
    epoch = runtime.epoch(
        epoch_ref="epoch:1",
        policy_generation=3,
        grant_generation=4,
        revocation_generation=5,
        credential_generation=6,
    )

    assert principal.trusted and principal.tenant_id == "tenant-a"
    assert context.effective_action_set == ("resource.read", "tool.prepare")
    assert "tool.execute" not in context.effective_action_set
    assert org.acyclic is True
    assert membership.resource_scope_ref != membership.delegated_admin_scope_ref
    assert use_only.can_delegate is False and delegate.can_delegate is True
    assert lineage.amplification_blocked and lineage.revoked_by_parent
    assert grant.effective_actions == ("resource.read",)
    assert policy.immutable and policy.schema_hash
    assert all([plane.pap_ref, plane.pdp_ref, plane.pep_ref, plane.pip_ref, plane.validation_report_ref, plane.simulation_report_ref, plane.shadow_evaluation_ref])
    assert denied.verdict == AuthorizationVerdict.DENY and denied.explicit_deny
    assert default_denied.default_deny_applied
    assert epoch.cache_key_hash


def test_security_runtime_batch_detection_flow_approval_secret_and_tool_boundaries() -> None:
    runtime = SecurityRuntimeBatch()

    detection = runtime.detect(
        detection_ref="detect:input:1",
        profile_ref="detect-profile:pii",
        payload={"text": "token sk-secret"},
        findings=("secret_detected",),
        classification=Classification.SECRET,
    )
    redaction_failed = runtime.redact(
        redaction_ref="redact:failed",
        profile_ref="redact-profile:default",
        payload={"api_key": "sk-secret"},
        findings=("secret_detected",),
        evidence_ref="evidence:redaction",
        adapter_failed=True,
    )
    untrusted_flow = runtime.information_flow(
        flow_ref="flow:untrusted",
        source_label=TrustLabel.UNTRUSTED,
        sink_ref="sink:tool",
        protected_sink_policy_ref="sink-policy:tool",
    )
    declassified_flow = runtime.information_flow(
        flow_ref="flow:declassified",
        source_label=TrustLabel.UNTRUSTED,
        sink_ref="sink:answer",
        protected_sink_policy_ref="sink-policy:answer",
        declassification_ref="declassify:1",
    )
    intent = runtime.action_intent(
        binding_ref="intent:tool:1",
        user_goal="Send the approved summary.",
        action_payload={"tool": "mail.send", "to": "reviewer@example.com"},
        ambiguous=True,
    )
    retrieval_gate = runtime.domain_gate(
        gate_ref="retrieval-gate:1",
        domain="knowledge",
        authorization_ref="authz:retrieval",
        classification=Classification.CONFIDENTIAL,
        allowed=True,
    )
    model_gate = runtime.model_security(
        decision_ref="model-security:1",
        provider_ref="model:provider",
        residency_ref="residency:us",
        redaction_ref=redaction_failed.redaction_ref,
        residency_allowed=True,
    )
    action_auth = runtime.action_authorization(
        decision_ref="action-auth:1",
        prepared_action_hash="hash:prepared:1",
        principal_ref="principal:user:1",
        task_ref="task:1",
        policy_version_ref="policy:1",
        epoch_ref="epoch:1",
        allowed=True,
    )
    approval = runtime.approval(
        approval_ref="approval:1",
        prepared_action_hash=action_auth.prepared_action_hash,
        principal_ref=action_auth.principal_ref,
        task_ref=action_auth.task_ref,
        policy_version_ref=action_auth.policy_version_ref,
        epoch_ref=action_auth.epoch_ref,
        ttl_ref="ttl:short",
        nonce_ref="nonce:1",
        accepted=True,
    )
    reconcile = runtime.effect_reconciliation_requirement(
        requirement_ref="reconcile:unknown-effect",
        unknown_effect_ref="effect:unknown:1",
    )
    credential = runtime.credential_policy(
        decision_ref="credential:1",
        audience="mcp:lark",
        on_behalf_of_binding_ref="obo:user:agent:1",
        credential_version_ref="credential-version:1",
    )
    secret = runtime.secret_lease(secret_ref="secret:mail", lease_ref="lease:mail:1", ttl_seconds=60)

    assert detection.input_hash and detection.classification == Classification.SECRET
    assert redaction_failed.export_allowed is False
    assert redaction_failed.output_hash != redaction_failed.input_hash
    assert untrusted_flow.allowed is False
    assert declassified_flow.allowed is True
    assert intent.ambiguous and intent.model_can_self_authorize is False
    assert retrieval_gate.allowed and retrieval_gate.authorization_ref
    assert model_gate.allowed and model_gate.redaction_ref
    assert action_auth.verdict == AuthorizationVerdict.ALLOW
    assert approval.accepted and approval.replayable is False
    assert approval.prepared_action_hash == action_auth.prepared_action_hash
    assert reconcile.retry_allowed_before_reconcile is False
    assert credential.token_passthrough_allowed is False and credential.audience == "mcp:lark"
    assert secret.lease_ref and secret.ttl_seconds == 60 and secret.prompt_trace_memory_allowed is False


def test_security_runtime_batch_infra_eval_projection_and_readiness() -> None:
    runtime = SecurityRuntimeBatch()

    sandbox = runtime.sandbox(
        sandbox_ref="sandbox:tool:1",
        tier=SandboxTier.ISOLATED,
        network_egress_policy_ref="egress:deny",
        ssrf_attempt=True,
    )
    supply_chain = runtime.supply_chain(
        artifact_ref="artifact:skill:1",
        provenance={"builder": "ci", "sha": "abc"},
        trust_decision_ref="trust:artifact:1",
        trusted=False,
    )
    break_glass = runtime.break_glass(
        session_ref="break-glass:1",
        scope_refs=("workspace:a",),
        expires_at_ref="expires:short",
    )
    incident = runtime.incident(
        incident_ref="incident:1",
        severity="high",
        finding_refs=("finding:secret",),
    )
    persistence = runtime.persistence_boundary(
        security_fact_ref="security-fact:approval:1",
        outbox_event_ref="outbox:security:1",
    )
    audit = runtime.audit_requirement(requirement_ref="audit:before-effect")
    recovery = runtime.recovery_contract(
        recovery_ref="recovery:security:1",
        idempotency_ref="idempotency:approval:1",
        retry_policy_ref="retry:security:1",
    )
    projection = runtime.product_projection(
        projection_ref="product-security-view:1",
        backend_decision_ref="authz:1",
    )
    eval_gate = runtime.eval_gate(
        eval_ref="security-eval:1",
        adaptive_attack_ref="attack:adaptive:1",
        utility_ref="utility:benign:1",
        release_gate_ref="release-gate:security:1",
        attack_success_rate=0,
        utility_preserved=True,
    )
    readiness = runtime.readiness_evidence(
        code_refs=("src/backend/zuno/platform/security/runtime_batch.py",),
        test_refs=("tests/security/test_security_runtime_batch.py",),
        verifier_ref="tools/scripts/verify_security_runtime_batch.py",
        evidence_ref="docs/evidence/security-runtime-batch.md",
    )

    assert sandbox.ssrf_blocked and sandbox.fail_closed and sandbox.tier == SandboxTier.ISOLATED
    assert supply_chain.status == AuthorizationVerdict.QUARANTINE and supply_chain.provenance_hash
    assert break_glass.audit_required and break_glass.limited
    assert incident.response_owner == "09 Security"
    assert persistence.same_transaction
    assert persistence.storage_owner == "PostgreSQL security facts"
    assert persistence.checkpoint_is_fact_source is False
    assert audit.before_effect and audit.audit_owner == "10 Observability / Eval"
    assert audit.domain_owner_transferred is False
    assert recovery.stale_epoch_rejected
    assert projection.frontend_is_fact_source is False
    assert eval_gate.passed
    assert readiness.implementation_available
    assert readiness.requirement_ids == tuple(f"ARCH-SEC-{index:03d}" for index in range(1, 61))
