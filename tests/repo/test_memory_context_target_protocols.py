from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_memory_context_target_protocols.py"
FORMAL = REPO_ROOT / "docs/modules/05-memory-context.md"
MIRROR = REPO_ROOT / ".agent/modules/05-memory-context.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_memory_context_target_protocols",
        VERIFIER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Memory & Context target verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _content() -> str:
    return FORMAL.read_text(encoding="utf-8")


def test_memory_context_target_contract() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_memory_context_mirror_is_byte_identical() -> None:
    assert MIRROR.read_bytes() == FORMAL.read_bytes()


def test_three_temporal_layers_and_three_long_term_kinds() -> None:
    content = _content()
    for term in [
        "Working Memory",
        "Session Memory",
        "Long-term Memory",
        "Episodic Memory",
        "Semantic Memory",
        "Procedural Memory",
    ]:
        assert term in content
    assert "## 四层 Memory" not in content
    assert "Entity 不是第四种长期 Memory" in content


def test_compression_ladder_is_complete() -> None:
    content = _content()
    for term in [
        "C0 Deterministic Lossless",
        "C1 Deterministic Lossy",
        "C2 Model-assisted Structured Compression",
        "C3 Reasoning Consolidation",
        "F0 FULL",
        "F1 NORMALIZED",
        "F2 EVIDENCE_BOUND_SUMMARY",
        "F3 REFERENCE_ONLY",
        "F4 EXCLUDED",
    ]:
        assert term in content


def test_context_and_memory_boundaries_are_explicit() -> None:
    content = _content()
    for term in [
        "ContextPack read view, not another memory layer",
        "Checkpoint Commit != Domain Memory Commit",
        "Protected Set",
        "Summary 不是唯一恢复来源",
        "模型都只产生 Proposal",
        "Procedural Memory 只能作为 Strategy Hint",
    ]:
        assert term in content


def test_domain_objects_have_storage_decisions() -> None:
    content = _content()
    for object_name, table_name in {
        "MemoryCaptureIntent": "memory_capture_intents",
        "MemoryCandidate": "memory_candidates",
        "MemoryGovernanceDecision": "memory_governance_decisions",
        "MemoryRecord": "memory_records",
        "MemoryVersion": "memory_versions",
        "SessionSummaryVersion": "session_summary_versions",
        "MemorySnapshot": "memory_snapshots",
        "MemoryManifestSnapshot": "memory_manifest_snapshots",
        "ContextPackVersion": "context_pack_versions",
        "ContextSelectionDecision": "context_selection_decisions",
        "MemoryUseTrace": "memory_use_traces",
        "MemoryUtilityProjection": "memory_utility_projections",
        "MemoryCommitReceipt": "memory_commit_receipts",
    }.items():
        assert object_name in content
        assert table_name in content


def test_all_state_machines_and_failure_namespace_are_present() -> None:
    content = _content()
    for heading in [
        "# 26. MemoryCandidate 状态机",
        "# 27. MemoryVersion 状态机",
        "# 28. SessionSummaryVersion 状态机",
        "# 29. ContextPackBuild 状态机",
        "# 30. Projection 状态机",
        "# 31. Failure Namespace",
        "# 32. Failure Decision Matrix",
    ]:
        assert heading in content
    assert "MEM_CONTEXT_MANDATORY_BUDGET_UNSATISFIABLE" in content
    assert "MEM_RECONCILIATION_REQUIRED" in content


def test_requirements_controls_tests_and_evidence_are_closed() -> None:
    content = _content()
    requirements = [int(value) for value in re.findall(r"ARCH-MEM-(\d{3})", content)]
    controls = [int(value) for value in re.findall(r"RC-MEM-(\d{3})", content)]
    assert requirements == list(range(1, 61))
    assert controls == list(range(1, 61))
    for requirement_id in range(1, 61):
        assert f"MEM-{requirement_id:03d}-UT" in content
        assert f"MEM-{requirement_id:03d}-IT" in content
        assert f"EV-MEM-{requirement_id:03d}" in content


def test_target_and_current_are_separated() -> None:
    content = _content()
    assert "唯一的正式 Target 架构主设计" in content
    assert "docs/status/production-readiness.md" in content
    assert ".agent/programs/" in content
    assert "# Current Baseline" not in content
    assert "# 当前与短期目标" not in content
