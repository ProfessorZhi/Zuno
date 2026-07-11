from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "zuno-real-unified-runtime-cutover-v1"
ACTIVE_PHASES = [
    "PHASE01_real-runtime-baseline",
    "PHASE02_langgraph-execution-cutover",
    "PHASE03_runtime-dependency-factory",
    "PHASE04_real-agent-execution",
    "PHASE05_knowledge-tool-memory-integration",
    "PHASE06_product-cutover",
    "PHASE07_benchmark-and-closure",
]
CURRENT_PHASE = "PHASE04_real-agent-execution"
LATEST_COMPLETED = "zuno-unified-agent-runtime-closure-v1"

CURRENT_PATH = REPO_ROOT / ".agent/programs/current.md"
ROADMAP_PATH = REPO_ROOT / ".agent/programs/implementation-roadmap.md"
CLOSURE_PATH = REPO_ROOT / ".agent/programs/closure-checklist.md"
REFERENCE_PATH = REPO_ROOT / ".agent/references/current-program.md"
QUEUED_SOURCE = REPO_ROOT / ".agent/programs/queued-programs/PROGRAM01_real-unified-runtime-cutover.md"

PHASE_FILES = [
    "PHASE01_real-runtime-baseline.md",
    "PHASE02_langgraph-execution-cutover.md",
    "PHASE03_runtime-dependency-factory.md",
    "PHASE04_real-agent-execution.md",
    "PHASE05_knowledge-tool-memory-integration.md",
    "PHASE06_product-cutover.md",
    "PHASE07_benchmark-and-closure.md",
]


def load_manifest() -> dict:
    return {
        "program": PROGRAM,
        "phase": "PHASE01_real-runtime-baseline",
        "phase_status": "active",
        "runtime_modification_scope": "none",
        "measurement_status": "baseline_frozen_not_measured",
        "phase01_closure": {
            "runtime_code_modified": False,
            "benchmark_measured": False,
            "quality_gate_changed": False,
        },
        "benchmark_truth_source": {
            "status": "truth_source_identified_measurement_not_run_in_PHASE01",
            "enterprise_rag_runner": "tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py",
        },
        "sample_case_sets": {
            "sample_8": {
                "dataset_path": "tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl",
                "case_ids": [
                    "mrv1_keyword_trace_header",
                    "mrv1_keyword_response_trace_header",
                    "mrv1_keyword_graph_queue",
                    "mrv1_keyword_default_mode_labels",
                    "mrv1_semantic_runtime_split",
                    "mrv1_semantic_standard_default",
                    "mrv1_semantic_bm25_strength",
                    "mrv1_semantic_graph_entry_policy",
                ],
                "coverage": [
                    "exact_lookup",
                    "semantic_fact",
                    "cross_doc_summary",
                    "graph_relation",
                    "citation_required",
                    "negative_or_missing_policy",
                    "structured_table",
                ],
            },
            "sample_80": {
                "status": "blocked",
                "case_ids": [],
                "blocked_reason": "no_tracked_fixed_80_case_enterprise_rag_set_available_in_repo",
            },
        },
    }


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_current_program() -> list[str]:
    errors: list[str] = []
    for path in [CURRENT_PATH, ROADMAP_PATH, CLOSURE_PATH, REFERENCE_PATH, QUEUED_SOURCE]:
        if not path.exists():
            errors.append(f"missing current program path: {path.relative_to(REPO_ROOT).as_posix()}")
    for phase_name in PHASE_FILES:
        phase_path = REPO_ROOT / ".agent/programs" / phase_name
        if not phase_path.exists():
            errors.append(f"missing active phase file: {phase_name}")

    if errors:
        return errors

    current = _read(CURRENT_PATH)
    reference = _read(REFERENCE_PATH)
    queued = _read(QUEUED_SOURCE)
    roadmap = _read(ROADMAP_PATH)
    closure = _read(CLOSURE_PATH)

    for phrase in [
        "state: active",
        f"active_program: {PROGRAM}",
        f"current_phase: {CURRENT_PHASE}",
        f"latest_completed_program: {LATEST_COMPLETED}",
        "implementation in progress",
        "measurement blocked",
        "quality not yet proven",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing active program phrase: {phrase}")
    for phrase in [
        f"active_program: {PROGRAM}",
        f"current_phase: {CURRENT_PHASE}",
        "PHASE04 目标是把 ModelStep",
    ]:
        if phrase not in reference:
            errors.append(f"current-program reference missing phrase: {phrase}")
    if "created_from:" in queued or "C:\\Users\\" in queued:
        errors.append("activated queued source must not contain local absolute created_from path")
    for phrase in [
        "state: activated_from_queue",
        f"active_program: {PROGRAM}",
        "不再作为执行状态事实源",
    ]:
        if phrase not in queued:
            errors.append(f"queued source missing activation phrase: {phrase}")
    for phase_name in PHASE_FILES:
        phase_text = _read(REPO_ROOT / ".agent/programs" / phase_name)
        if f"program: {PROGRAM}" not in phase_text:
            errors.append(f"phase missing program name: {phase_name}")
        if "## 目标" not in phase_text or "## 验证命令" not in phase_text:
            errors.append(f"phase missing required sections: {phase_name}")
    for phrase in [
        "PHASE01_real-runtime-baseline",
        "PHASE07_benchmark-and-closure",
        "不得把 PHASE02-PHASE07 目标写成 Current",
    ]:
        if phrase not in roadmap + closure + current:
            errors.append(f"program roadmap/closure missing phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_current_program()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Current program verification failed.")
        return 1
    print("Current program verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
