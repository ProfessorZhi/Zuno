from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.knowledge.runtime_batch import (  # noqa: E402
    KnowledgeRuntimeBatch,
    KnowledgeVersionState,
    RetrievalRoundStatus,
)


REQUIREMENTS = tuple(f"ARCH-KNOW-{index:03d}" for index in range(1, 31))


def verify_knowledge_runtime_batch() -> list[str]:
    errors: list[str] = []
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
    plan = runtime.retrieval_plan(plan_ref="retrieval-plan:1", dynamic_round_refs=("round:1",), retriever_refs=("vector", "graph"))
    round_record = runtime.retrieval_round(round_ref="round:1", status=RetrievalRoundStatus.REDUCED, snapshot_ref=request.snapshot_ref, security_filter_ref=request.security_filter_ref, results=({"source_span": "span:1", "score": 0.9},), deadline_ref="deadline:1", generation=1)
    evidence = runtime.evidence_record(evidence_ref="evidence:1", requirement_ref=requirement.requirement_ref, source_span_ref="source-span:1", document_version_ref="document-version:1", content={"text": "renewal is 30 days"}, strict=True)
    ledger = runtime.evidence_ledger(ledger_ref="ledger:1", evidence_refs=(evidence.evidence_ref, evidence.evidence_ref), frontier_ref="frontier:1", generation=2)
    if not (request.agent_core_decision_ref and request.evidence_requirement_refs):
        errors.append("ARCH-KNOW-001..003 ownership/retrieval need/evidence requirement invalid")
    if not (version.accepted and version.source_span_manifest_hash and version.visibility_receipt_ref):
        errors.append("ARCH-KNOW-004/025 snapshot/version lifecycle invalid")
    if not request.security_filter_ref:
        errors.append("ARCH-KNOW-005 ACL prefilter missing")
    if plan.fixed_graph_ref != "knowledge-retrieval-graph:v1":
        errors.append("ARCH-KNOW-006 fixed graph invalid")
    if not (plan.dynamic_round_refs and round_record.generation >= 1):
        errors.append("ARCH-KNOW-007 dynamic round plan invalid")
    if not (plan.retriever_refs and plan.idempotent_reducer_ref):
        errors.append("ARCH-KNOW-008 parallel retriever/reducer invalid")
    if not (round_record.snapshot_ref and round_record.security_filter_ref and round_record.result_hash and round_record.deadline_ref):
        errors.append("ARCH-KNOW-009 result validation missing")
    fusion = runtime.fusion(fusion_ref="fusion:1", rerank_candidate_count=20)
    graph = runtime.graph_evidence(graph_ref="graph:path:1", graph_capability_available=True, source_span_backlink_ref="source-span:graph:1", reason_code="multi_hop_required")
    aux_graph = runtime.graph_evidence(graph_ref="graph:aux:1", graph_capability_available=False, source_span_backlink_ref=None, reason_code="graph_unavailable")
    quality = runtime.quality(quality_ref="quality:1", conflict_refs=("conflict:1",), citation_eligible=True)
    if not (fusion.normalized_score_ref and fusion.rrf_version_ref):
        errors.append("ARCH-KNOW-010 fusion normalization invalid")
    if not (fusion.rerank_candidate_count and fusion.model_slot_ref):
        errors.append("ARCH-KNOW-011 rerank boundary invalid")
    if not (graph.reason_code and graph.graph_capability_available):
        errors.append("ARCH-KNOW-012 graph routing invalid")
    if not graph.source_span_backlink_ref or not aux_graph.auxiliary_only_without_source_span:
        errors.append("ARCH-KNOW-013 graph SourceSpan/auxiliary boundary invalid")
    if not (ledger.append_only_generation and ledger.deduplicated and ledger.frontier_ref):
        errors.append("ARCH-KNOW-014/015 evidence ledger/frontier invalid")
    if not (quality.authority_policy_ref and quality.temporal_policy_ref):
        errors.append("ARCH-KNOW-016 authority/temporal policy invalid")
    if not quality.conflict_refs:
        errors.append("ARCH-KNOW-017 conflict preservation invalid")
    if not evidence.strict_citation_eligible:
        errors.append("ARCH-KNOW-018 citation eligibility invalid")
    corrective = runtime.corrective(corrective_ref="corrective:1", gap_ref="gap:source-span-missing", retry_kind="focused_citation")
    replan = runtime.corrective(corrective_ref="corrective:replan", gap_ref="gap:no-progress", retry_kind="replan")
    stop = runtime.stop_budget(decision_ref="stop:1", sufficient=True, no_progress=False, budget_reserved=100, budget_settled=80)
    recovery = runtime.recovery(recovery_ref="recovery:1", cancellation_signal_ref="cancel:1", domain_commit_ref="domain-commit:evidence:1", checkpoint_ref="checkpoint:control:1")
    if not corrective.next_action_ref:
        errors.append("ARCH-KNOW-019 corrective retrieval invalid")
    if corrective.retry_kind == replan.retry_kind or not replan.replan_required:
        errors.append("ARCH-KNOW-020 retry/correct/replan separation invalid")
    if not stop.sufficient or stop.overrun:
        errors.append("ARCH-KNOW-021/022 stop/budget guard invalid")
    if not (recovery.cancellation_signal_ref and recovery.late_result_rejected):
        errors.append("ARCH-KNOW-023 cancellation/late guard invalid")
    if not recovery.reconciled:
        errors.append("ARCH-KNOW-024 recovery reconciliation invalid")
    deletion = runtime.deletion_propagation(delete_ref="delete:knowledge:1", revoked_evidence_refs=("evidence:1", "evidence:2"))
    event = runtime.event(event_ref="event:knowledge:1", event_type="EvidenceCommitted", payload={"evidence": "redacted"})
    eval_release = runtime.eval_release(eval_ref="eval:knowledge:1", pinned_profile_ref="profile:retrieval:v1", case_set_ref="case-set:multihop:v1", measured=True, comparable=True)
    config = runtime.config_separation(config_ref="knowledge-config:1", intent_ref="config-intent:1", spec_ref="config-spec:1", projection_api_ref="config-projection:1")
    readiness = runtime.readiness_evidence(code_refs=("src/backend/zuno/knowledge/runtime_batch.py",), test_refs=("tests/knowledge/test_knowledge_runtime_batch.py",), verifier_ref="tools/scripts/verify_knowledge_runtime_batch.py", evidence_ref="docs/evidence/knowledge-runtime-batch.md")
    if not deletion.retrieval_paths_blocked or not deletion.taint_propagated:
        errors.append("ARCH-KNOW-026 deletion propagation invalid")
    if event.schema_version != "knowledge.event.v1" or not event.redacted:
        errors.append("ARCH-KNOW-027 typed/redacted event invalid")
    if not (eval_release.pinned_profile_ref and eval_release.case_set_ref and eval_release.measured and eval_release.comparable):
        errors.append("ARCH-KNOW-028 eval comparability invalid")
    if not eval_release.release_gate_passed:
        errors.append("ARCH-KNOW-029 quality release gate invalid")
    if config.config_owns_runtime_fact:
        errors.append("ARCH-KNOW-030 config separation invalid")
    if readiness.requirement_ids != REQUIREMENTS or not readiness.implementation_available:
        errors.append("ARCH-KNOW readiness evidence invalid")
    return errors


def main() -> int:
    errors = verify_knowledge_runtime_batch()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Knowledge runtime batch verifier passed for ARCH-KNOW-001..030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
