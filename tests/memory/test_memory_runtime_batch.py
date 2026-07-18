from __future__ import annotations

from zuno.memory.runtime_batch import (
    CandidateStatus,
    CompressionLevel,
    LongTermMemoryKind,
    MemoryRuntimeBatch,
    VersionStatus,
)


def test_memory_runtime_batch_lifecycle_candidates_versions_and_context_pack() -> None:
    runtime = MemoryRuntimeBatch()

    lifecycle = runtime.lifecycle()
    candidate = runtime.candidate(
        candidate_ref="candidate:1",
        source_fact_ref="run-outcome:1",
        kind=LongTermMemoryKind.EPISODIC,
    )
    version = runtime.version(
        version_ref="memory-version:1",
        candidate_ref=candidate.candidate_ref,
        generation=1,
        source_payload={"fact": "prefers concise updates"},
        status=VersionStatus.ACTIVE,
    )
    summary = runtime.session_summary(
        summary_ref="session-summary:1",
        source_messages=({"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}),
        coverage_ratio=0.8,
        raw_message_ref="raw-message-group:1",
        incremental_generation=2,
    )
    pack = runtime.context_pack(
        context_pack_ref="context-pack:1",
        generation=3,
        candidate_refs=(candidate.candidate_ref,),
        compression_trace_ref="compression-trace:1",
        budget_trace_ref="budget-trace:1",
        token_count=128,
    )
    retrieval = runtime.retrieval_gate(
        retrieval_ref="retrieval:semantic:1",
        memory_kind=LongTermMemoryKind.SEMANTIC,
        scope_ref="scope:workspace",
        acl_decision_ref="acl:allow",
        allowed=True,
    )
    compression = runtime.compression(
        compression_ref="compression:1",
        level=CompressionLevel.C2_ABSTRACTIVE,
        fidelity_level="F3",
        protected_set_refs=("protected:goal",),
    )
    rehydration = runtime.rehydration(
        rehydration_ref="rehydrate:1",
        context_pack_ref=pack.context_pack_ref,
        object_refs=("object:payload:1",),
    )

    assert lifecycle.working_owner == "06 Agent Core / Planning & Control"
    assert lifecycle.long_term_kinds == tuple(LongTermMemoryKind)
    assert lifecycle.projection_kinds == ("entity", "vector", "graph", "lexical")
    assert candidate.governance_required and candidate.model_is_fact_owner is False
    assert version.immutable_hash and version.source_hash
    assert summary.source_message_hashes and summary.raw_message_ref
    assert summary.incremental_generation == 2
    assert pack.read_view and pack.immutable_hash and pack.token_count == 128
    assert retrieval.security_before_summary and retrieval.allowed
    assert compression.tool_payload_first
    assert compression.protected_set_refs and compression.deterministic_budget
    assert compression.exact_token_validation
    assert rehydration.summary_is_only_source is False


def test_memory_runtime_batch_governance_recovery_privacy_and_safety() -> None:
    runtime = MemoryRuntimeBatch()

    reflexion = runtime.reflexion_governance(
        reflexion_ref="reflexion:1",
        procedural_promotion_evidence_refs=("eval:repeat-success", "human-review:1"),
    )
    consolidation = runtime.consolidation(
        consolidation_ref="consolidation:1",
        source_refs=("memory-version:1", "memory-version:2"),
        utility_projection_ref="utility:hint:1",
        fact_ref="memory-fact:merged:1",
        negative_transfer=True,
    )
    freshness = runtime.freshness(
        freshness_ref="freshness:1",
        effective_time_ref="effective:2026-07-18",
        observed_time_ref="observed:2026-07-18T10:00:00Z",
    )
    conflict = runtime.conflict(
        conflict_ref="conflict:1",
        competing_version_refs=("memory-version:1", "memory-version:2"),
        resolution_ref="resolution:human:1",
    )
    candidate_machine = runtime.state_machine(
        machine_ref="candidate-machine",
        statuses=tuple(CandidateStatus),
    )
    version_machine = runtime.state_machine(
        machine_ref="version-machine",
        statuses=tuple(VersionStatus),
    )
    projection = runtime.projection_publication(
        publication_ref="projection-publication:1",
        domain_commit_ref="domain-commit:1",
        projection_ref="projection:vector:1",
        index_receipt_ref="index-receipt:1",
    )
    recovery = runtime.commit_recovery(
        commit_ref="commit:memory:1",
        idempotency_key="idem:memory:1",
        checkpoint_ref="checkpoint:agent:1",
        domain_commit_ref="domain-commit:1",
        expected_generation=7,
        committed_generation=8,
    )
    privacy = runtime.privacy_delete(
        delete_ref="privacy-delete:1",
        source_ref="memory-fact:1",
        projection_refs=("projection:entity:1", "projection:vector:1"),
        legal_hold=True,
    )
    safety = runtime.safety(safety_ref="safety:1")

    assert reflexion.default_kind == LongTermMemoryKind.EPISODIC
    assert reflexion.procedural_promotion_evidence_refs
    assert reflexion.procedural_is_strategy_hint
    assert consolidation.delete_source is False
    assert consolidation.utility_projection_ref != consolidation.fact_ref
    assert consolidation.negative_transfer_suspended
    assert freshness.effective_time_ref != freshness.observed_time_ref
    assert freshness.verified_before_use
    assert conflict.silent_overwrite_allowed is False
    assert candidate_machine.closed and version_machine.closed
    assert projection.order_valid and projection.index_is_active is False
    assert recovery.cas_passed and recovery.unknown_requires_reconcile
    assert recovery.checkpoint_ref != recovery.domain_commit_ref
    assert privacy.all_projections_hidden and privacy.legal_hold_blocks_delete
    assert safety.prompt_injection_authoritative is False
    assert safety.hidden_chain_persisted is False
    assert safety.model_output_is_proposal


def test_memory_runtime_batch_model_trace_storage_envelope_and_readiness() -> None:
    runtime = MemoryRuntimeBatch()

    routing = runtime.model_routing(
        routing_ref="model-routing:1",
        upgrade_lineage_ref="model-upgrade:memory:1",
    )
    trace = runtime.trace(
        trace_ref="memory-trace:1",
        selection_trace_ref="selection-trace:1",
        outcome_ref="run-outcome:1",
        eval_ref="eval:memory:1",
        long_term_eval_ref="eval:long-term:1",
        compression_eval_ref="eval:compression:1",
    )
    storage = runtime.storage(
        storage_ref="memory-storage:1",
        large_payload_object_ref="object:memory-payload:1",
    )
    envelope = runtime.envelope(
        envelope_ref="envelope:memory:1",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        trace_id="trace:1",
        correlation_id="correlation:1",
        payload={"memory": "fact"},
    )
    readiness = runtime.readiness_evidence(
        code_refs=("src/backend/zuno/memory/runtime_batch.py",),
        test_refs=("tests/memory/test_memory_runtime_batch.py",),
        verifier_ref="tools/scripts/verify_memory_runtime_batch.py",
        evidence_ref="docs/evidence/memory-runtime-batch.md",
    )

    assert routing.weak_model_default == "summary"
    assert routing.strong_model_path == "complex_consolidation"
    assert routing.upgrade_lineage_ref
    assert all([trace.selection_trace_ref, trace.outcome_ref, trace.eval_ref, trace.long_term_eval_ref, trace.compression_eval_ref])
    assert storage.canonical_store == "PostgreSQL"
    assert storage.large_payload_object_ref
    assert storage.projections_rebuildable
    assert envelope.tenant_id and envelope.workspace_id and envelope.trace_id and envelope.correlation_id
    assert envelope.payload_hash
    assert readiness.implementation_available
    assert readiness.requirement_ids == tuple(f"ARCH-MEM-{index:03d}" for index in range(1, 61))
