from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.capability.runtime_batch import (  # noqa: E402
    CapabilityAvailabilityStatus,
    CapabilityDecisionStatus,
    CapabilityResultValidity,
    CapabilityRuntimeBatch,
)


REQUIREMENTS = tuple(f"ARCH-CAP-{index:03d}" for index in range(1, 81))


def verify_capability_runtime_batch() -> list[str]:
    errors: list[str] = []
    runtime = CapabilityRuntimeBatch()

    if not runtime.boundary_decision(executes_tool=False, commits_foreign_fact=False).allowed:
        errors.append("capability boundary rejected valid semantic/governance-only decision")
    if runtime.boundary_decision(executes_tool=True, commits_foreign_fact=False).allowed:
        errors.append("capability boundary allowed direct tool execution")

    taxonomy = runtime.concept_taxonomy(
        capability_kind="document_research",
        provider_protocol="mcp",
        governance_objects=("security_gate", "approval", "budget", "trace", "checkpoint", "lease", "idempotency_claim"),
    )
    if not taxonomy.valid or "mcp" not in runtime.provider_protocols:
        errors.append("capability taxonomy did not separate capability/provider/governance objects")

    envelope = runtime.envelope(
        envelope_type="CrossModuleEnvelopeV1",
        major_version=1,
        payload={"capability": "document_research"},
        tenant_id="tenant-a",
        trace_id="trace-a",
        security_epoch_ref="security-epoch:1",
    )
    if not all([envelope.payload_hash, envelope.tenant_id, envelope.trace_id, envelope.security_epoch_ref]):
        errors.append("cross-module envelope lacks version/hash/tenant/trace/security epoch")

    if runtime.unknown_contract(known=False).status != CapabilityDecisionStatus.BLOCKED:
        errors.append("unknown contract did not fail closed")
    if runtime.unknown_contract(known=False, quarantine=True).status != CapabilityDecisionStatus.QUARANTINED:
        errors.append("unknown contract did not quarantine when requested")

    skill = runtime.skill_version(
        skill_id="skill:research",
        version="1.0.0",
        metadata_ref="metadata:skill:research",
        instruction_ref="instruction:skill:research",
        resource_manifest_ref="manifest:skill:research",
        capability_requirement_refs=("capability:req:research",),
        acceptance_criteria_ref="acceptance:research",
    )
    discovery = runtime.skill_discovery(
        discovery_id="discovery:1",
        candidate_skill_ids=("skill:research",),
        rejected=("skill:unknown",),
    )
    load = runtime.skill_load(
        skill_id=skill.skill_id,
        version=skill.version,
        resource_hashes=("hash:resource:1",),
        load_policy_ref="load-policy:1",
        budget_ref="budget:skill:1",
    )
    resource = runtime.skill_resource(
        resource_ref="resource:script",
        resource_type="script",
        data_classification="internal",
        source_ref="object:skill:script",
        content_hash="hash:script",
        executable=True,
    )
    policy = runtime.skill_policy(
        allowed_subset=("tool:read",),
        original_candidates=("tool:read", "tool:write"),
        signature_verified=True,
        integrity_verified=True,
        policy_verified=True,
        risk_verified=True,
        model_visible_fields=("metadata",),
    )
    if not skill.immutable_hash:
        errors.append("skill version lacks immutable hash")
    if not discovery.metadata_only or not discovery.immutable_hash:
        errors.append("skill discovery did not enforce metadata-only immutable result")
    if load.validity != CapabilityResultValidity.VALID or not (load.resource_hashes and load.load_policy_ref and load.budget_ref):
        errors.append("skill load did not pin version/resource/load policy/budget")
    if resource.direct_execution_allowed or not resource.integrity_hash:
        errors.append("skill resource allowed direct execution or lacked integrity/source classification")
    if not (policy.non_amplifying and policy.supply_chain_verified and policy.security_precedence):
        errors.append("skill policy did not enforce non-amplification/supply-chain/security precedence")
    if policy.model_visible_fields != ("metadata",):
        errors.append("model visibility was not minimized")

    definition = runtime.capability_definition(
        capability_id="capability:document_research",
        semantic_identity="document_research",
        provider_tool_name="web_search",
    )
    version = runtime.capability_version(
        capability_id=definition.capability_id,
        version="1.0.0",
        input_schema={"query": "string"},
        output_schema={"answer": "string"},
        risk_ref="risk:read-only",
        dependency_refs=("knowledge",),
        compatibility_ref="compatibility:v1",
        acceptance_ref="acceptance:document_research",
    )
    active_binding = runtime.provider_binding(
        binding_id="binding:1",
        capability_version_ref="capability:document_research:1",
        tool_definition_ref="tool:web_search:1",
        binding_version="binding:1",
        proposal_source="human",
        deterministic_gates_passed=True,
    )
    model_only_binding = runtime.provider_binding(
        binding_id="binding:model",
        capability_version_ref="capability:document_research:1",
        tool_definition_ref="tool:web_search:1",
        binding_version="binding:2",
        proposal_source="model_only",
        deterministic_gates_passed=True,
    )
    conformance = runtime.conformance_record(
        provider_ref="provider:web",
        covered_semantics=("input", "output", "side_effect", "idempotency", "reconciliation", "security", "error"),
    )
    failure_domain = runtime.provider_failure_domain(
        provider_family="search",
        backend_ref="backend:tavily",
        quota_ref="quota:search",
        effect_failure_domain_ref="effect:read-only",
        independent_disaster_recovery=False,
    )
    connector_split = runtime.connector_pack_split(
        connector_pack_ref="connector:web",
        provider_definition_ref="provider:web",
        tool_manifest_refs=("tool:web_search",),
        capability_mapping_refs=("mapping:web_search",),
        scope_mapping_refs=("scope:web_search",),
        contract_test_refs=("contract:web_search",),
        reconciliation_extension_refs=("reconcile:web_search",),
    )
    if not definition.stable:
        errors.append("capability definition used provider tool name as semantic identity")
    if not (version.input_schema_hash and version.output_schema_hash and version.risk_ref and version.compatibility_ref):
        errors.append("capability version lacks canonical schema/risk/dependency/compatibility/acceptance")
    if not active_binding.active or model_only_binding.active:
        errors.append("binding activation did not require deterministic governance or blocked model-only activation")
    if not conformance.passed:
        errors.append("provider conformance did not cover input/output/side-effect/idempotency/reconciliation/security/error")
    if not all([failure_domain.provider_family, failure_domain.backend_ref, failure_domain.quota_ref, failure_domain.effect_failure_domain_ref]):
        errors.append("provider failure domain lacks family/backend/quota/effect refs")
    if not (connector_split.provider_definition_ref and connector_split.tool_manifest_refs and connector_split.capability_mapping_refs and connector_split.contract_test_refs):
        errors.append("connector pack was not split into versioned module facts")

    snapshot = runtime.availability_snapshot(
        snapshot_ref="snapshot:1",
        version="snapshot:v1",
        ttl_seconds=300,
        source_generation=7,
    )
    entries = tuple(runtime.availability_entry(capability_ref=f"capability:{status.value}", status=status) for status in CapabilityAvailabilityStatus)
    selection = runtime.selection_record(
        selection_id="selection:1",
        candidate_refs=("binding:1", "binding:2"),
        hard_filtered_refs=("binding:2",),
        scores={"binding:1": 0.9},
        selected_binding_ref="binding:1",
        provider_instance_ref="provider-instance:1",
        fallback_order=("binding:1", "binding:3"),
    )
    fallback = runtime.fallback_verdict(
        output_contract_preserved=True,
        risk_within_limit=True,
        tenant_preserved=True,
        data_residency_preserved=True,
        side_effect_semantics_preserved=True,
    )
    if not (snapshot.immutable and snapshot.ttl_seconds > 0 and snapshot.source_generation == 7):
        errors.append("availability snapshot lacks immutable version/TTL/source generation")
    if {entry.status for entry in entries} != set(CapabilityAvailabilityStatus):
        errors.append("availability entries do not cover all required statuses")
    if any(entry.authorization_implied for entry in entries):
        errors.append("availability implied authorization")
    if not (selection.candidate_refs and selection.hard_filtered_refs and selection.scoring_hash and selection.selected_binding_ref and selection.provider_instance_ref and selection.fallback_order):
        errors.append("selection result lacks candidates/filter/scoring/binding/instance/fallback")
    if not selection.deterministic_commit:
        errors.append("selection did not deterministically commit after hard filters")
    if not fallback.compatible:
        errors.append("fallback candidate failed output/risk/tenant/residency/side-effect compatibility")

    pinned = runtime.pinned_versions(
        capability_version_ref="capability:research:1",
        binding_version_ref="binding:research:1",
        tool_definition_ref="tool:web_search:1",
        schema_hash="schema:abc",
    )
    inventory = runtime.inventory_change(inventory_generation=8, tool_definition_version_ref="tool:web_search:2")
    reuse = runtime.reuse_verdict(
        version_ok=True,
        scope_ok=True,
        security_epoch_ok=True,
        snapshot_ttl_ok=True,
        resource_integrity_ok=True,
    )
    if not pinned.exact:
        errors.append("plan/prepared action did not pin exact versions/schema hash")
    if not inventory.revalidation_required or inventory.schema_mutated_in_place:
        errors.append("inventory generation did not force revalidation or mutated schema in place")
    if not reuse.reusable:
        errors.append("reuse did not require version/scope/security epoch/TTL/resource integrity")

    security = runtime.security_boundary(
        provider_instance_ref="provider-instance:tenant-a",
        credential_scope_ref="credential-scope:tenant-a",
        capability_constraint_ref="constraint:tenant-a",
        secret_material_stored=False,
        authorization_overridden_by_skill=False,
    )
    constraint = runtime.constraint_record(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        region="us-east-1",
        data_residency="us",
        identity_mode="delegated",
        resource_scope_ref="scope:docs",
        provider_trust_ref="trust:signed",
    )
    audit = runtime.audit_boundary(audit_requirement_ref="audit:required")
    if not security.valid:
        errors.append("security boundary conflated instance/credential/constraint or stored secret/overrode authorization")
    if not all([constraint.tenant_id, constraint.workspace_id, constraint.region, constraint.data_residency, constraint.identity_mode, constraint.resource_scope_ref, constraint.provider_trust_ref]):
        errors.append("capability constraint lacks tenant/workspace/region/residency/identity/scope/trust")
    if audit.persistence_receipt_owner != "11 Infrastructure" or audit.audit_event_owner != "10 Observability / Eval" or not audit.selection_propagates_requirement:
        errors.append("audit ownership boundary invalid")

    persistence = runtime.persistence_boundary(
        domain_fact_refs=("capability_definition:1", "selection:1"),
        object_payload_refs=("object:skill-package:1",),
        projection_refs=("search-index:capability", "runtime-health:provider"),
    )
    publication = runtime.transaction_record(
        transaction_id="tx:publish",
        facts=("definition:1", "active_pointer:1", "transition:1"),
        outbox_event_ref="outbox:capability:1",
    )
    selection_tx = runtime.transaction_record(
        transaction_id="tx:selection",
        facts=("selection:1", "snapshot:1", "policy:1"),
        outbox_event_ref="outbox:selection:1",
    )
    transition = runtime.transition_record(transition_id="transition:1", expected_generation=7, committed_generation=8)
    outbox = runtime.outbox_record(event_id="event:capability:1", consumer_idempotency_key="consumer:agent-core:event:capability:1")
    recovery = runtime.recovery_plan(
        resource_commit_ref="recovery:resource",
        version_publish_ref="recovery:version",
        active_switch_ref="recovery:active",
        snapshot_build_ref="recovery:snapshot",
        revocation_propagation_ref="recovery:revocation",
        reconciler_ref="reconciler:capability",
        claim_ref="claim:capability",
        fencing_ref="fence:capability",
        human_escalation_ref="escalation:capability",
    )
    if persistence.source_is_projection:
        errors.append("projection/cache/runtime health became capability fact source")
    if not (publication.atomic and selection_tx.atomic):
        errors.append("publish or selection transaction did not atomically include facts/outbox")
    if not transition.cas_passed:
        errors.append("transition did not use expected generation/CAS")
    if outbox.delivery_semantics != "at_least_once" or not outbox.consumer_idempotency_key:
        errors.append("outbox lacks at-least-once/idempotent consumer semantics")
    if not all(
        [
            recovery.resource_commit_ref,
            recovery.version_publish_ref,
            recovery.active_switch_ref,
            recovery.snapshot_build_ref,
            recovery.revocation_propagation_ref,
            recovery.reconciler_ref,
            recovery.claim_ref,
            recovery.fencing_ref,
            recovery.human_escalation_ref,
        ]
    ):
        errors.append("recovery plan lacks crash/reconciler/claim/fencing/escalation refs")

    connector = runtime.connector_policy(custom_extension_reason="interactive_cli_reconciliation")
    trace = runtime.trace_event(
        event_type="capability.selection",
        trace_ref="trace:capability",
        payload={"selected": "binding:1", "api_key": "sk-secret"},
    )
    current = runtime.current_evidence_gate(
        requirement_id="ARCH-CAP-080",
        code_ref="src/backend/zuno/capability/runtime_batch.py",
        migration_ref="migration:not-required-runtime-contract",
        unit_ref="tests/capability/test_capability_runtime_batch.py",
        integration_ref="tests/agent/test_capability_layer_surfaces.py",
        fault_ref="tools/scripts/verify_capability_runtime_batch.py",
        e2e_ref="docs/evidence/capability-runtime-batch.md",
        trace_ref="docs/evidence/capability-runtime-batch.md#trace",
        eval_ref="tools/scripts/verify_capability_runtime_batch.py",
        runtime_evidence_ref="docs/evidence/capability-runtime-batch.md",
    )
    if connector.provider_specific_core_branch:
        errors.append("core capability code contains provider-specific branch")
    if connector.generic_adapter_families != ("HTTP", "CLI", "MCP", "SDK", "RPC", "Browser", "Database", "LocalFunction"):
        errors.append("generic adapter families incomplete")
    if not connector.structured_manifest_required or not connector.draft_only_from_discovery:
        errors.append("connector policy lacks structured manifest or draft-only discovery rule")
    if connector.custom_extension_reason != "interactive_cli_reconciliation":
        errors.append("custom extension reason not constrained to exceptional cases")
    if connector.unknown_effect_retry_allowed:
        errors.append("unknown side-effect retry was allowed before reconciliation")
    if "sk-secret" in repr(trace.redacted_payload) or not trace.payload_hash:
        errors.append("capability trace event did not redact or hash payload")
    if not current.implementation_available:
        errors.append("target-to-current gate lacks code/migration/unit/integration/fault/e2e/trace/eval/runtime evidence")

    return errors


def main() -> int:
    errors = verify_capability_runtime_batch()
    if errors:
        print("Capability runtime batch verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Capability runtime batch verification passed for {', '.join(REQUIREMENTS)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
