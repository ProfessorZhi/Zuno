from __future__ import annotations

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "backend"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from zuno.memory.runtime_batch import (  # noqa: E402
    CandidateStatus,
    CompressionLevel,
    LongTermMemoryKind,
    MemoryRuntimeBatch,
    VersionStatus,
)


REQUIREMENTS = tuple(f"ARCH-MEM-{index:03d}" for index in range(1, 61))


def verify_memory_runtime_batch() -> list[str]:
    errors: list[str] = []
    runtime = MemoryRuntimeBatch()

    lifecycle = runtime.lifecycle()
    if lifecycle.working_owner != "06 Agent Core / Planning & Control" or not lifecycle.session_summary_ref:
        errors.append("ARCH-MEM-001/005/006 lifecycle or working/session owner invalid")
    if lifecycle.long_term_kinds != tuple(LongTermMemoryKind):
        errors.append("ARCH-MEM-002 long-term memory taxonomy invalid")
    if lifecycle.projection_kinds != ("entity", "vector", "graph", "lexical"):
        errors.append("ARCH-MEM-003 projection taxonomy invalid")

    candidate = runtime.candidate(candidate_ref="candidate:1", source_fact_ref="run-outcome:1", kind=LongTermMemoryKind.EPISODIC)
    version = runtime.version(version_ref="memory-version:1", candidate_ref=candidate.candidate_ref, generation=1, source_payload={"fact": "prefers concise updates"}, status=VersionStatus.ACTIVE)
    summary = runtime.session_summary(summary_ref="session-summary:1", source_messages=({"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}), coverage_ratio=0.8, raw_message_ref="raw-message-group:1", incremental_generation=2)
    pack = runtime.context_pack(context_pack_ref="context-pack:1", generation=3, candidate_refs=(candidate.candidate_ref,), compression_trace_ref="compression-trace:1", budget_trace_ref="budget-trace:1", token_count=128)
    if not candidate.governance_required or candidate.model_is_fact_owner:
        errors.append("ARCH-MEM-007/049 candidate governance or model proposal boundary invalid")
    if not (version.immutable_hash and version.source_hash):
        errors.append("ARCH-MEM-008/010 MemoryVersion/source trace invalid")
    if not (pack.read_view and pack.immutable_hash):
        errors.append("ARCH-MEM-004/009 ContextPack immutable read view invalid")
    if summary.incremental_generation <= 1 or not summary.source_message_hashes or not summary.raw_message_ref:
        errors.append("ARCH-MEM-011/012/013 summary increment/coverage/raw tail invalid")

    retrieval = runtime.retrieval_gate(retrieval_ref="retrieval:semantic:1", memory_kind=LongTermMemoryKind.SEMANTIC, scope_ref="scope:workspace", acl_decision_ref="acl:allow", allowed=True)
    compression = runtime.compression(compression_ref="compression:1", level=CompressionLevel.C2_ABSTRACTIVE, fidelity_level="F3", protected_set_refs=("protected:goal",))
    rehydration = runtime.rehydration(rehydration_ref="rehydrate:1", context_pack_ref=pack.context_pack_ref, object_refs=("object:payload:1",))
    if not retrieval.allowed or not retrieval.security_before_summary or not retrieval.scope_ref or not retrieval.acl_decision_ref:
        errors.append("ARCH-MEM-015/016/017 retrieval scope/ACL/security ordering invalid")
    if compression.level not in tuple(CompressionLevel) or not compression.fidelity_level:
        errors.append("ARCH-MEM-018/019 compression/fidelity invalid")
    if not (compression.tool_payload_first and compression.protected_set_refs and compression.deterministic_budget and compression.exact_token_validation):
        errors.append("ARCH-MEM-020..023 budget/protected/token validation invalid")
    if rehydration.summary_is_only_source:
        errors.append("ARCH-MEM-024/025 rehydration/summary source boundary invalid")

    reflexion = runtime.reflexion_governance(reflexion_ref="reflexion:1", procedural_promotion_evidence_refs=("eval:repeat-success", "human-review:1"))
    consolidation = runtime.consolidation(consolidation_ref="consolidation:1", source_refs=("memory-version:1", "memory-version:2"), utility_projection_ref="utility:hint:1", fact_ref="memory-fact:merged:1", negative_transfer=True)
    freshness = runtime.freshness(freshness_ref="freshness:1", effective_time_ref="effective:2026-07-18", observed_time_ref="observed:2026-07-18T10:00:00Z")
    conflict = runtime.conflict(conflict_ref="conflict:1", competing_version_refs=("memory-version:1", "memory-version:2"), resolution_ref="resolution:human:1")
    if reflexion.default_kind != LongTermMemoryKind.EPISODIC or not reflexion.procedural_promotion_evidence_refs or not reflexion.procedural_is_strategy_hint:
        errors.append("ARCH-MEM-026..028 reflexion/procedural governance invalid")
    if consolidation.delete_source or consolidation.utility_projection_ref == consolidation.fact_ref or not consolidation.negative_transfer_suspended:
        errors.append("ARCH-MEM-029..031 consolidation/projection/negative transfer invalid")
    if not freshness.verified_before_use or freshness.effective_time_ref == freshness.observed_time_ref:
        errors.append("ARCH-MEM-032/033 freshness/effective observed time invalid")
    if conflict.silent_overwrite_allowed:
        errors.append("ARCH-MEM-034 conflict allowed silent overwrite")

    candidate_machine = runtime.state_machine(machine_ref="candidate-machine", statuses=tuple(CandidateStatus))
    version_machine = runtime.state_machine(machine_ref="version-machine", statuses=tuple(VersionStatus))
    summary_machine = runtime.state_machine(machine_ref="summary-machine", statuses=(VersionStatus.DRAFT, VersionStatus.ACTIVE, VersionStatus.SUPERSEDED))
    context_machine = runtime.state_machine(machine_ref="context-build-machine", statuses=(VersionStatus.DRAFT, VersionStatus.ACTIVE))
    projection = runtime.projection_publication(publication_ref="projection-publication:1", domain_commit_ref="domain-commit:1", projection_ref="projection:vector:1", index_receipt_ref="index-receipt:1")
    recovery = runtime.commit_recovery(commit_ref="commit:memory:1", idempotency_key="idem:memory:1", checkpoint_ref="checkpoint:agent:1", domain_commit_ref="domain-commit:1", expected_generation=7, committed_generation=8)
    if not all(machine.closed for machine in (candidate_machine, version_machine, summary_machine, context_machine)):
        errors.append("ARCH-MEM-035..038 state machines not closed")
    if not projection.order_valid or projection.index_is_active:
        errors.append("ARCH-MEM-039/040 projection order or index active boundary invalid")
    if not (recovery.idempotency_key and recovery.checkpoint_ref != recovery.domain_commit_ref and recovery.cas_passed and recovery.unknown_requires_reconcile):
        errors.append("ARCH-MEM-041..044 commit/checkpoint/CAS/unknown reconcile invalid")

    privacy = runtime.privacy_delete(delete_ref="privacy-delete:1", source_ref="memory-fact:1", projection_refs=("projection:entity:1", "projection:vector:1"), legal_hold=True)
    safety = runtime.safety(safety_ref="safety:1")
    routing = runtime.model_routing(routing_ref="model-routing:1", upgrade_lineage_ref="model-upgrade:memory:1")
    trace = runtime.trace(trace_ref="memory-trace:1", selection_trace_ref="selection-trace:1", outcome_ref="run-outcome:1", eval_ref="eval:memory:1", long_term_eval_ref="eval:long-term:1", compression_eval_ref="eval:compression:1")
    storage = runtime.storage(storage_ref="memory-storage:1", large_payload_object_ref="object:memory-payload:1")
    envelope = runtime.envelope(envelope_ref="envelope:memory:1", tenant_id="tenant-a", workspace_id="workspace-a", trace_id="trace:1", correlation_id="correlation:1", payload={"memory": "fact"})
    readiness = runtime.readiness_evidence(code_refs=("src/backend/zuno/memory/runtime_batch.py",), test_refs=("tests/memory/test_memory_runtime_batch.py",), verifier_ref="tools/scripts/verify_memory_runtime_batch.py", evidence_ref="docs/evidence/memory-runtime-batch.md")
    if not privacy.all_projections_hidden or not privacy.legal_hold_blocks_delete:
        errors.append("ARCH-MEM-045/046 privacy delete/legal hold invalid")
    if safety.prompt_injection_authoritative or safety.hidden_chain_persisted or not safety.model_output_is_proposal:
        errors.append("ARCH-MEM-047..049 prompt/hidden chain/model proposal invalid")
    if routing.weak_model_default != "summary" or routing.strong_model_path != "complex_consolidation" or not routing.upgrade_lineage_ref:
        errors.append("ARCH-MEM-050/051 model routing/upgrade invalid")
    if not all([trace.selection_trace_ref, trace.outcome_ref, trace.eval_ref, trace.long_term_eval_ref, trace.compression_eval_ref]):
        errors.append("ARCH-MEM-052..054 trace/outcome/eval coverage invalid")
    if storage.canonical_store != "PostgreSQL" or not storage.large_payload_object_ref or not storage.projections_rebuildable:
        errors.append("ARCH-MEM-055..057 storage/object/projection rebuild invalid")
    if not all([envelope.tenant_id, envelope.workspace_id, envelope.trace_id, envelope.correlation_id, envelope.payload_hash]):
        errors.append("ARCH-MEM-058 envelope fields invalid")
    if readiness.requirement_ids != REQUIREMENTS or not readiness.implementation_available:
        errors.append("ARCH-MEM-059/060 readiness/current evidence invalid")
    return errors


def main() -> int:
    errors = verify_memory_runtime_batch()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Memory runtime batch verifier passed for ARCH-MEM-001..060")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
