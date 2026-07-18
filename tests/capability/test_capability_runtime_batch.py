from __future__ import annotations

from zuno.capability.runtime_batch import (
    CapabilityAvailabilityStatus,
    CapabilityDecisionStatus,
    CapabilityResultValidity,
    CapabilityRuntimeBatch,
)


def test_capability_runtime_batch_foundation_skill_binding_and_availability() -> None:
    runtime = CapabilityRuntimeBatch()

    boundary = runtime.boundary_decision(executes_tool=False, commits_foreign_fact=False)
    blocked_boundary = runtime.boundary_decision(executes_tool=True, commits_foreign_fact=False)
    assert boundary.allowed is True
    assert blocked_boundary.allowed is False

    taxonomy = runtime.concept_taxonomy(
        capability_kind="document_research",
        provider_protocol="mcp",
        governance_objects=("security_gate", "approval", "budget"),
    )
    assert taxonomy.valid is True
    assert "mcp" in runtime.provider_protocols
    assert "security_gate" in runtime.governance_objects

    envelope = runtime.envelope(
        envelope_type="CrossModuleEnvelopeV1",
        major_version=1,
        payload={"capability": "document_research"},
        tenant_id="tenant-a",
        trace_id="trace-a",
        security_epoch_ref="security-epoch:1",
    )
    assert envelope.payload_hash and envelope.tenant_id == "tenant-a"
    assert runtime.unknown_contract(known=False).status == CapabilityDecisionStatus.BLOCKED
    assert runtime.unknown_contract(known=False, quarantine=True).status == CapabilityDecisionStatus.QUARANTINED

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
    script = runtime.skill_resource(
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
    assert skill.immutable_hash
    assert discovery.metadata_only is True and discovery.immutable_hash
    assert load.validity == CapabilityResultValidity.VALID
    assert script.direct_execution_allowed is False
    assert policy.non_amplifying and policy.supply_chain_verified and policy.security_precedence
    assert policy.model_visible_fields == ("metadata",)

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
    assert definition.stable is True
    assert version.input_schema_hash and version.output_schema_hash
    assert active_binding.active is True
    assert model_only_binding.active is False
    assert conformance.passed is True
    assert failure_domain.effect_failure_domain_ref
    assert connector_split.tool_manifest_refs and connector_split.capability_mapping_refs

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
    assert snapshot.immutable and snapshot.ttl_seconds == 300
    assert {entry.status for entry in entries} == set(CapabilityAvailabilityStatus)
    assert all(entry.authorization_implied is False for entry in entries)
    assert selection.deterministic_commit is True and selection.fallback_order
    assert fallback.compatible is True


def test_capability_runtime_batch_version_security_persistence_connector_and_current_gate() -> None:
    runtime = CapabilityRuntimeBatch()

    pinned = runtime.pinned_versions(
        capability_version_ref="capability:research:1",
        binding_version_ref="binding:research:1",
        tool_definition_ref="tool:web_search:1",
        schema_hash="schema:abc",
    )
    inventory = runtime.inventory_change(
        inventory_generation=8,
        tool_definition_version_ref="tool:web_search:2",
    )
    reuse = runtime.reuse_verdict(
        version_ok=True,
        scope_ok=True,
        security_epoch_ok=True,
        snapshot_ttl_ok=True,
        resource_integrity_ok=True,
    )
    assert pinned.exact is True
    assert inventory.revalidation_required is True and inventory.schema_mutated_in_place is False
    assert reuse.reusable is True

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
    assert security.valid is True
    assert constraint.provider_trust_ref == "trust:signed"
    assert audit.persistence_receipt_owner == "11 Infrastructure"
    assert audit.audit_event_owner == "10 Observability / Eval"

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
    transition = runtime.transition_record(
        transition_id="transition:1",
        expected_generation=7,
        committed_generation=8,
    )
    outbox = runtime.outbox_record(
        event_id="event:capability:1",
        consumer_idempotency_key="consumer:agent-core:event:capability:1",
    )
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
    assert persistence.source_is_projection is False
    assert publication.atomic is True and selection_tx.atomic is True
    assert transition.cas_passed is True
    assert outbox.delivery_semantics == "at_least_once" and outbox.consumer_idempotency_key
    assert recovery.reconciler_ref and recovery.fencing_ref and recovery.human_escalation_ref

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
    assert connector.provider_specific_core_branch is False
    assert connector.generic_adapter_families == ("HTTP", "CLI", "MCP", "SDK", "RPC", "Browser", "Database", "LocalFunction")
    assert connector.structured_manifest_required is True
    assert connector.draft_only_from_discovery is True
    assert connector.custom_extension_reason == "interactive_cli_reconciliation"
    assert connector.unknown_effect_retry_allowed is False
    assert "sk-secret" not in repr(trace.redacted_payload)
    assert trace.payload_hash
    assert current.implementation_available is True
