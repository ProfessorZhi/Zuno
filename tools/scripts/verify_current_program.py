from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / ".agent/programs/baseline-manifest.md"
CURRENT_PATH = REPO_ROOT / ".agent/programs/current.md"
ROADMAP_PATH = REPO_ROOT / ".agent/programs/implementation-roadmap.md"
PHASE01_PATH = REPO_ROOT / ".agent/programs/PHASE01_truth-source-baseline-and-program-activation.md"

PROGRAM = "zuno-unified-agent-runtime-closure-v1"
NEXT_PHASE = "PHASE02_unified-runtime-contracts-and-state"
CURRENT_PHASE = "PHASE13_paired-benchmark-release-gate-and-program-closure"


def _extract_json_block(text: str) -> dict[str, Any]:
    marker = "```json"
    if marker not in text:
        raise ValueError("baseline manifest must contain a json fenced block")
    body = text.split(marker, 1)[1].split("```", 1)[0].strip()
    return json.loads(body)


def load_manifest() -> dict[str, Any]:
    return _extract_json_block(MANIFEST_PATH.read_text(encoding="utf-8"))


def _load_jsonl_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ids.add(str(row["id"]))
    return ids


def verify_current_program() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.exists():
        return [f"missing baseline manifest: {MANIFEST_PATH.relative_to(REPO_ROOT).as_posix()}"]

    manifest = load_manifest()
    current = CURRENT_PATH.read_text(encoding="utf-8")
    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    phase01 = PHASE01_PATH.read_text(encoding="utf-8")

    expected_pairs = {
        "program": PROGRAM,
        "phase": "PHASE01_truth-source-baseline-and-program-activation",
        "phase_status": "completed",
        "phase_start_branch": "codex/zuno-truth-source-production-readiness-baseline",
        "runtime_modification_scope": "none",
        "measurement_status": "baseline_frozen_not_measured",
        "next_phase": NEXT_PHASE,
    }
    for key, expected in expected_pairs.items():
        if manifest.get(key) != expected:
            errors.append(f"baseline manifest {key} expected {expected!r}, got {manifest.get(key)!r}")

    closure = manifest.get("phase01_closure") or {}
    if closure.get("runtime_code_modified") is not False:
        errors.append("PHASE01 manifest must state runtime_code_modified=false")
    if closure.get("benchmark_measured") is not False:
        errors.append("PHASE01 manifest must state benchmark_measured=false")
    if closure.get("quality_gate_changed") is not False:
        errors.append("PHASE01 manifest must state quality_gate_changed=false")

    for phrase in [
        "state: active",
        f"active_program: {PROGRAM}",
        f"current_phase: {CURRENT_PHASE}",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing phrase for active program state: {phrase}")
    if "PHASE01 | `truth-source-baseline-and-program-activation` | completed" not in roadmap:
        errors.append("roadmap must mark PHASE01 completed")
    if "state: completed" not in phase01:
        errors.append("PHASE01 file must be marked completed")

    path_sections = [
        "product_entrypoints",
        "agent_runtimes",
        "subsystem_baselines",
        "model_call_inventory",
        "fixed_dataset_candidates",
    ]
    for section in path_sections:
        for item in manifest.get(section) or []:
            path_value = item.get("path")
            if path_value and not (REPO_ROOT / path_value).exists():
                errors.append(f"manifest path does not exist: {section}: {path_value}")

    benchmark = manifest.get("benchmark_truth_source") or {}
    for key in [
        "enterprise_rag_runner",
        "enterprise_rag_dataset_adapter",
        "enterprise_rag_readme",
    ]:
        path_value = benchmark.get(key)
        if not path_value or not (REPO_ROOT / path_value).exists():
            errors.append(f"benchmark truth source path missing: {key}: {path_value}")
    if benchmark.get("status") != "truth_source_identified_measurement_not_run_in_PHASE01":
        errors.append("benchmark status must remain not measured in PHASE01")

    sample_sets = manifest.get("sample_case_sets") or {}
    sample_8 = sample_sets.get("sample_8") or {}
    sample_8_path = REPO_ROOT / str(sample_8.get("dataset_path") or "")
    if not sample_8_path.exists():
        errors.append(f"sample_8 dataset path missing: {sample_8.get('dataset_path')}")
    else:
        ids = _load_jsonl_ids(sample_8_path)
        missing = [case_id for case_id in sample_8.get("case_ids") or [] if case_id not in ids]
        if missing:
            errors.append("sample_8 ids missing from dataset: " + ", ".join(missing))
        if len(sample_8.get("case_ids") or []) != 8:
            errors.append("sample_8 must contain exactly 8 ids")

    sample_80 = sample_sets.get("sample_80") or {}
    if sample_80.get("status") != "blocked":
        errors.append("sample_80 must remain blocked until a tracked fixed 80-case set exists")
    if sample_80.get("case_ids"):
        errors.append("sample_80 must not list untracked local case ids")
    if "blocked_reason" not in sample_80:
        errors.append("sample_80 blocked state must include blocked_reason")

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
