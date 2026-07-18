from __future__ import annotations

from zuno.knowledge.runtime_batch import (
    KnowledgeRuntimeBatch,
    KnowledgeVersionState,
    RetrievalRoundStatus,
)


def test_knowledge_runtime_batch_request_version_plan_round_and_evidence() -> None:
    runtime = KnowledgeRuntimeBatch()

    requirement = runtime.evidence_requirement(
        requirement_ref="evidence-req:1",
        evidence_goal="prove renewal date",
        unresolved_hops=("contract", "renewal"),
    )
    request = runtime.query_request(
        request_ref="knowledge-query:1",
        agent_core_decision_ref="agent-core-decision:retrieve:1",
        evidence_requirement_refs=(requirement.requirement_ref,),
        snapshot_ref="knowledge-snapshot:1",
        security_filter_ref="security-filter:acl:1",
        budget_ref="budget:knowledge:1",
    )
    version = runtime.knowledge_version(
        version_ref="knowledge-version:1",
        state=KnowledgeVersionState.ACCEPTED,
        source_span_manifest={"spans": ["span:1"]},
        document_version_ref="document-version:1",
        security_metadata_ref="security-metadata:1",
        index_manifest={"vector": "v1", "graph": "v1"},
        visibility_receipt_ref="visibility:1",
    )
    plan = runtime.retrieval_plan(
        plan_ref="retrieval-plan:1",
        dynamic_round_refs=("round:1",),
        retriever_refs=("vector", "graph"),
    )
    round_record = runtime.retrieval_round(
        round_ref="round:1",
        status=RetrievalRoundStatus.REDUCED,
        snapshot_ref=request.snapshot_ref,
        security_filter_ref=request.security_filter_ref,
        results=({"source_span": "span:1", "score": 0.9},),
        deadline_ref="deadline:1",
        generation=1,
    )
    evidence = runtime.evidence_record(
        evidence_ref="evidence:1",
        requirement_ref=requirement.requirement_ref,
        source_span_ref="source-span:1",
        document_version_ref="document-version:1",
        content={"text": "renewal is 30 days"},
        strict=True,
    )
    ledger = runtime.evidence_ledger(
        ledger_ref="ledger:1",
        evidence_refs=(evidence.evidence_ref, evidence.evidence_ref),
        frontier_ref="frontier:1",
        generation=2,
    )

    assert request.agent_core_decision_ref
    assert request.evidence_requirement_refs == (requirement.requirement_ref,)
    assert version.accepted and version.source_span_manifest_hash and version.visibility_receipt_ref
    assert plan.fixed_graph_ref == "knowledge-retrieval-graph:v1"
    assert plan.dynamic_round_refs and plan.idempotent_reducer_ref
    assert round_record.snapshot_ref == request.snapshot_ref
    assert round_record.security_filter_ref == request.security_filter_ref
    assert round_record.result_hash and round_record.deadline_ref
    assert evidence.strict_citation_eligible and not evidence.tainted
    assert ledger.evidence_refs == (evidence.evidence_ref,)
    assert ledger.deduplicated


def test_knowledge_runtime_batch_fusion_graph_quality_correction_budget_and_recovery() -> None:
    runtime = KnowledgeRuntimeBatch()

    fusion = runtime.fusion(fusion_ref="fusion:1", rerank_candidate_count=20)
    graph = runtime.graph_evidence(
        graph_ref="graph:path:1",
        graph_capability_available=True,
        source_span_backlink_ref="source-span:graph:1",
        reason_code="multi_hop_required",
    )
    aux_graph = runtime.graph_evidence(
        graph_ref="graph:aux:1",
        graph_capability_available=False,
        source_span_backlink_ref=None,
        reason_code="graph_unavailable",
    )
    quality = runtime.quality(
        quality_ref="quality:1",
        conflict_refs=("conflict:1",),
        citation_eligible=True,
    )
    corrective = runtime.corrective(
        corrective_ref="corrective:1",
        gap_ref="gap:source-span-missing",
        retry_kind="focused_citation",
    )
    replan = runtime.corrective(
        corrective_ref="corrective:replan",
        gap_ref="gap:no-progress",
        retry_kind="replan",
    )
    stop = runtime.stop_budget(
        decision_ref="stop:1",
        sufficient=True,
        no_progress=False,
        budget_reserved=100,
        budget_settled=80,
    )
    recovery = runtime.recovery(
        recovery_ref="recovery:1",
        cancellation_signal_ref="cancel:1",
        domain_commit_ref="domain-commit:evidence:1",
        checkpoint_ref="checkpoint:control:1",
    )

    assert fusion.normalized_score_ref and fusion.rrf_version_ref
    assert fusion.rerank_candidate_count == 20 and fusion.model_slot_ref
    assert graph.graph_capability_available and not graph.auxiliary_only_without_source_span
    assert aux_graph.auxiliary_only_without_source_span
    assert quality.authority_policy_ref and quality.temporal_policy_ref
    assert quality.conflict_refs and quality.citation_eligible
    assert corrective.next_action_ref.startswith("next-action:")
    assert corrective.replan_required is False
    assert replan.replan_required is True
    assert stop.sufficient and not stop.no_progress and not stop.overrun
    assert recovery.late_result_rejected
    assert recovery.reconciled and recovery.domain_commit_ref != recovery.checkpoint_ref


def test_knowledge_runtime_batch_delete_events_eval_config_and_readiness() -> None:
    runtime = KnowledgeRuntimeBatch()

    deletion = runtime.deletion_propagation(
        delete_ref="delete:knowledge:1",
        revoked_evidence_refs=("evidence:1", "evidence:2"),
    )
    event = runtime.event(
        event_ref="event:knowledge:1",
        event_type="EvidenceCommitted",
        payload={"evidence": "redacted"},
    )
    eval_release = runtime.eval_release(
        eval_ref="eval:knowledge:1",
        pinned_profile_ref="profile:retrieval:v1",
        case_set_ref="case-set:multihop:v1",
        measured=True,
        comparable=True,
    )
    config = runtime.config_separation(
        config_ref="knowledge-config:1",
        intent_ref="config-intent:1",
        spec_ref="config-spec:1",
        projection_api_ref="config-projection:1",
    )
    readiness = runtime.readiness_evidence(
        code_refs=("src/backend/zuno/knowledge/runtime_batch.py",),
        test_refs=("tests/knowledge/test_knowledge_runtime_batch.py",),
        verifier_ref="tools/scripts/verify_knowledge_runtime_batch.py",
        evidence_ref="docs/evidence/knowledge-runtime-batch.md",
    )

    assert deletion.retrieval_paths_blocked and deletion.taint_propagated
    assert event.schema_version == "knowledge.event.v1"
    assert event.payload_hash and event.redacted
    assert eval_release.release_gate_passed
    assert eval_release.pinned_profile_ref and eval_release.case_set_ref
    assert config.intent_ref and config.spec_ref and config.projection_api_ref
    assert config.config_owns_runtime_fact is False
    assert readiness.implementation_available
    assert readiness.requirement_ids == tuple(f"ARCH-KNOW-{index:03d}" for index in range(1, 31))
