from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/05-memory-context.md"
MIRROR = REPO_ROOT / ".agent/modules/05-memory-context.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"

REQUIRED_PARTS = [
    "# Part I：定位、术语与概念架构",
    "# Part II：完整运行流程",
    "# Part III：状态、失败、恢复与一致性",
    "# Part IV：领域对象与 Contract",
    "# Part V：Policy、模型角色与安全",
    "# Part VI：目标实现表面",
    "# Part VII：规范性矩阵",
    "# Part VIII：测试与完成证据",
]

REQUIRED_TERMS = [
    "Working Memory",
    "Session Memory",
    "Long-term Memory",
    "Episodic Memory",
    "Semantic Memory",
    "Procedural Memory",
    "C0 Deterministic Lossless",
    "C1 Deterministic Lossy",
    "C2 Model-assisted Structured Compression",
    "C3 Reasoning Consolidation",
    "F0 FULL",
    "F1 NORMALIZED",
    "F2 EVIDENCE_BOUND_SUMMARY",
    "F3 REFERENCE_ONLY",
    "F4 EXCLUDED",
    "ContextPack read view, not another memory layer",
    "MemoryCaptureIntent",
    "MemoryCandidate",
    "MemoryGovernanceDecision",
    "MemoryRecord",
    "MemoryVersion",
    "SessionSummaryVersion",
    "MemorySnapshot",
    "MemoryManifestSnapshot",
    "ContextCandidateItem",
    "ContextSelectionDecision",
    "ContextPackVersion",
    "MemoryUseTrace",
    "MemoryUtilityProjection",
    "ReflexionCandidate",
    "ConsolidationProposal",
    "MemoryCommitReceipt",
    "Protected Set",
    "Atomic-group-aware Deterministic Greedy",
    "CompactionSnapshot",
    "MemoryCommitIntent",
    "Checkpoint Commit != Domain Memory Commit",
    "MEM_CONTEXT_MANDATORY_BUDGET_UNSATISFIABLE",
    "CrossModuleEnvelopeV1",
    "PostgreSQL",
    ".agent/programs/",
    "唯一的正式 Target 架构主设计",
]

REQUIRED_TABLES = [
    "memory_capture_intents",
    "memory_candidates",
    "memory_candidate_validations",
    "memory_governance_decisions",
    "memory_records",
    "memory_versions",
    "memory_source_bindings",
    "memory_conflicts",
    "memory_revocations",
    "session_summary_versions",
    "memory_snapshots",
    "memory_manifest_snapshots",
    "context_pack_versions",
    "context_selection_decisions",
    "context_compression_traces",
    "memory_use_traces",
    "memory_utility_projections",
    "memory_projection_manifests",
    "memory_commit_receipts",
    "memory_deletion_requests",
    "memory_deletion_receipts",
    "memory_reconciliation_decisions",
]

FORBIDDEN_TERMS = [
    "## 四层 Memory",
    "Entity Memory 是第四",
    "ContextPack 是第五层",
    "模型直接写 Active Memory",
    "# Current Baseline",
    "# 当前与短期目标",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX]:
        if not path.exists():
            errors.append(f"missing Memory & Context target path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)

    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Memory & Context formal document and mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Memory & Context document must declare normative-target-module-architecture")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Memory & Context document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Memory & Context document parts are not in canonical order I through VIII")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Memory & Context document missing required term: {term}")

    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Memory & Context document missing target table: {table}")

    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Memory & Context document contains obsolete or conflicting contract: {term}")

    requirement_ids = [int(value) for value in re.findall(r"ARCH-MEM-(\d{3})", formal)]
    if requirement_ids != list(range(1, 61)):
        errors.append("Memory & Context document must define ARCH-MEM-001 through ARCH-MEM-060 exactly once and in order")

    control_ids = [int(value) for value in re.findall(r"RC-MEM-(\d{3})", formal)]
    if control_ids != list(range(1, 61)):
        errors.append("Memory & Context document must map RC-MEM-001 through RC-MEM-060 exactly once and in order")

    for requirement_id in range(1, 61):
        for token in [
            f"MEM-{requirement_id:03d}-UT",
            f"MEM-{requirement_id:03d}-IT",
            f"EV-MEM-{requirement_id:03d}",
        ]:
            if token not in formal:
                errors.append(f"Memory & Context requirement mapping missing: {token}")

    for transition_group in [
        "# 26. MemoryCandidate 状态机",
        "# 27. MemoryVersion 状态机",
        "# 28. SessionSummaryVersion 状态机",
        "# 29. ContextPackBuild 状态机",
        "# 30. Projection 状态机",
    ]:
        if transition_group not in formal:
            errors.append(f"Memory & Context document missing state machine: {transition_group}")

    for index_name, content in {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
    }.items():
        for term in [
            "05-memory-context.md",
            "verify_memory_context_target_protocols.py",
        ]:
            if term not in content:
                errors.append(f"{index_name} does not route to Memory & Context target artifact: {term}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Memory & Context target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
