"""Validate the V4.1 conceptual architecture review artifact contract.

V4.1 extends the V4 state machine with no-code conceptual review, Part-A
cold-start evidence, Candidate Branch ownership, and Main Thread merge gates.
It is intentionally non-operational: it never creates threads, reads business
implementation to fill a documentation gap, changes Canonical, or signs ChatGPT.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
V4_PATH = Path(__file__).with_name("verify_red_blue_workflow_v4.py")
V4_SPEC = importlib.util.spec_from_file_location("zuno_v4_workflow_verifier", V4_PATH)
if V4_SPEC is None or V4_SPEC.loader is None:  # pragma: no cover - repository invariant
    raise RuntimeError("cannot load V4 workflow verifier")
V4 = importlib.util.module_from_spec(V4_SPEC)
V4_SPEC.loader.exec_module(V4)

V41_WORKFLOW = "ZUNO-RED-BLUE-WORKFLOW-V4.1"
POST_JUDGE_STATES = {
    "RED_COUNTER_REVIEW",
    "WAITING_FOR_CHATGPT_REVIEW",
    "CHATGPT_REPAIR_REQUIRED",
    "CLOSED",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
CALIBRATION_SOURCES = {
    "REAL_SELF_INTERVIEW",
    "HIGH_SIGNAL_PUBLIC_INTERVIEW",
    "GENERAL_PUBLIC_INTERVIEW",
    "GENERAL_ARCHITECTURE",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _yaml(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing {path.name}")
        return {}
    try:
        value = yaml.safe_load(_read(path))
    except yaml.YAMLError as exc:
        errors.append(f"{path.name} is invalid YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a mapping")
        return {}
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required artifact: {path.name}")


def _marker(path: Path, marker: str, errors: list[str]) -> None:
    if path.exists() and marker.lower() not in _read(path).lower():
        errors.append(f"{path.name} must contain marker: {marker}")


def verify_bootstrap(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    required = {
        "workflow_id",
        "bootstrap_id",
        "base_sha",
        "final_sha",
        "historical_rounds_immutable",
        "round_006_status",
        "round_006_started",
        "chatgpt_review_status",
        "round_status",
        "architecture_track",
        "implementation_track",
        "facts_changed",
        "runtime_changed",
        "schema_changed",
        "migration_changed",
        "adr_changed",
        "canonical_content_changed",
        "red_reads_business_code",
        "blue_reads_business_code",
        "blue_uses_code_as_architecture_reason",
        "blue_push_main",
        "main_integrator",
        "main_merge_requires_chatgpt_verdict",
        "red_judge_part_a_first_pass",
        "human_writing_verifier_mode",
        "session_creation",
        "interview_calibration_packet_template",
        "interview_calibration_source_policy",
        "blue_reads_interview_calibration",
    }
    for key in sorted(required - manifest.keys()):
        errors.append(f"bootstrap manifest missing required field: {key}")
    if manifest.get("workflow_id") != V41_WORKFLOW:
        errors.append("bootstrap workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4.1")
    if not SHA40.fullmatch(str(manifest.get("base_sha", ""))):
        errors.append("bootstrap base_sha must be a 40-character SHA")
    if manifest.get("historical_rounds_immutable") is not True:
        errors.append("historical_rounds_immutable must be true")
    if manifest.get("round_006_status") != "READY_FOR_FRESH_RED_THREAD":
        errors.append("round_006_status must be READY_FOR_FRESH_RED_THREAD")
    if manifest.get("round_006_started") is not False:
        errors.append("round_006_started must be false")
    if manifest.get("chatgpt_review_status") != "WAITING_FOR_CHATGPT_REVIEW":
        errors.append("bootstrap must wait for ChatGPT review")
    for key in ("facts_changed", "runtime_changed", "schema_changed", "migration_changed", "adr_changed", "canonical_content_changed"):
        if manifest.get(key) != "NONE":
            errors.append(f"bootstrap must keep {key} as NONE")
    if manifest.get("red_reads_business_code") is not False or manifest.get("blue_reads_business_code") is not False:
        errors.append("V4.1 Bootstrap must declare no business-code reading")
    if manifest.get("blue_uses_code_as_architecture_reason") is not False:
        errors.append("Blue must not use code as an architecture reason")
    if manifest.get("blue_push_main") is not False:
        errors.append("Blue must not push main")
    if manifest.get("main_integrator") != "MAIN_THREAD":
        errors.append("main_integrator must be MAIN_THREAD")
    if manifest.get("main_merge_requires_chatgpt_verdict") is not True:
        errors.append("Main merge must require ChatGPT verdict")
    if manifest.get("red_judge_part_a_first_pass") is not True:
        errors.append("Red Judge must perform Part-A first pass")
    if manifest.get("human_writing_verifier_mode") != "WARNING_ONLY":
        errors.append("human_writing_verifier_mode must be WARNING_ONLY")
    if manifest.get("session_creation") != "MANUAL_ARTIFACT_ONLY":
        errors.append("session_creation must be MANUAL_ARTIFACT_ONLY")
    template = str(manifest.get("interview_calibration_packet_template", ""))
    template_path = ROOT / template if template else ROOT / "__missing__"
    if not template_path.exists():
        errors.append("interview_calibration_packet_template must exist")
    else:
        _marker(template_path, "RED_THREAD_ONLY", errors)
        _marker(template_path, "answer_content_included: `NO`", errors)
    if manifest.get("interview_calibration_source_policy") != "RED_ONLY_SYNTHESIS":
        errors.append("interview_calibration_source_policy must be RED_ONLY_SYNTHESIS")
    if manifest.get("blue_reads_interview_calibration") is not False:
        errors.append("Blue must not read interview calibration")
    for name in ("README.md", "review-package.md", "manual-launch-instructions.md", "chatgpt-verdict.md"):
        _require(directory / name, errors)
    package = directory / "review-package.md"
    for marker in ("BASE_SHA:", "FINAL_SHA:", "CANONICAL_PART_A_GAP", "WAITING_FOR_CHATGPT_REVIEW", "NOT_STARTED"):
        _marker(package, marker, errors)
    verdict = directory / "chatgpt-verdict.md"
    if verdict.exists() and "NOT_PROVIDED" not in _read(verdict):
        errors.append("Bootstrap ChatGPT verdict must remain NOT_PROVIDED")
    return errors


def _verify_no_code_context(directory: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    paths = [
        directory / "context-packets" / "red-context.md",
        directory / "context-packets" / "blue-context.md",
    ]
    for path in paths:
        _require(path, errors)
        if not path.exists():
            continue
        content = _read(path)
        _marker(path, "business_implementation_code: PROHIBITED", errors)
        _marker(path, "part_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE", errors)
        if re.search(r"(?im)(?:^|\s)(?:src/backend/|apps/|infra/)", content):
            errors.append(f"{path.name} contains a business implementation path")
    blue = directory / "context-packets" / "blue-context.md"
    if blue.exists():
        _marker(blue, "code_is_not_architecture_reason", errors)
        _marker(blue, "red-questions", errors)
        _marker(blue, "interview_calibration: PROHIBITED", errors)
    red = directory / "context-packets" / "red-context.md"
    if red.exists():
        _marker(red, "interview_calibration: RED_ONLY", errors)
    if manifest.get("red_reads_business_code") is not False:
        errors.append("red_reads_business_code must be false")
    if manifest.get("blue_reads_business_code") is not False:
        errors.append("blue_reads_business_code must be false")
    if manifest.get("blue_uses_code_as_architecture_reason") is not False:
        errors.append("blue_uses_code_as_architecture_reason must be false")
    if manifest.get("interview_calibration_read_by_red") is not True:
        errors.append("interview_calibration_read_by_red must be true")
    if manifest.get("interview_calibration_read_by_blue") is not False:
        errors.append("interview_calibration_read_by_blue must be false")


def _verify_part_a(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    if state not in POST_JUDGE_STATES:
        return
    raw_path = str(manifest.get("part_a_explainability_artifact", ""))
    if not raw_path:
        errors.append("part_a_explainability_artifact is required after Red Judge")
        return
    path = directory / raw_path
    _require(path, errors)
    if not path.exists():
        return
    _marker(path, "PART_A_EXPLAINABILITY", errors)
    for marker in ("CLEAR", "PARTIAL", "MISSING"):
        _marker(path, marker, errors)
    for marker in ("INTERVIEW_EXPLAINABILITY", "DENSE", "TERM_DEPENDENT"):
        _marker(path, marker, errors)
    counts: list[int] = []
    for field in ("part_a_clear_count", "part_a_partial_count", "part_a_missing_count"):
        value = manifest.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{field} must be a non-negative integer")
        else:
            counts.append(value)
    if len(counts) == 3 and sum(counts) != 100:
        errors.append("Part-A Explainability counts must sum to 100")
    if manifest.get("red_judge_part_a_first_pass") is not True:
        errors.append("red_judge_part_a_first_pass must be true")


def _verify_candidate_and_merge(manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    required = {
        "candidate_branch",
        "integration_branch",
        "main_branch",
        "blue_push_main",
        "main_integrator",
        "main_merge_requires_chatgpt_verdict",
        "merge_status",
        "main_final_sha",
        "blue_candidate_ready",
    }
    for key in sorted(required - manifest.keys()):
        errors.append(f"round manifest missing V4.1 field: {key}")
    candidate = str(manifest.get("candidate_branch", ""))
    main = str(manifest.get("main_branch", ""))
    if not candidate or not main or candidate == main:
        errors.append("candidate_branch must be non-empty and different from main_branch")
    if main != "main":
        errors.append("main_branch must be main")
    if manifest.get("integration_branch") != main:
        errors.append("integration_branch must equal main_branch")
    if manifest.get("blue_push_main") is not False:
        errors.append("blue_push_main must be false")
    if manifest.get("main_integrator") != "MAIN_THREAD":
        errors.append("main_integrator must be MAIN_THREAD")
    if manifest.get("main_merge_requires_chatgpt_verdict") is not True:
        errors.append("main_merge_requires_chatgpt_verdict must be true")
    if state != "CLOSED":
        if manifest.get("merge_status") == "MERGED":
            errors.append("Candidate cannot be merged before accepted ChatGPT verdict")
        if manifest.get("main_final_sha") not in (None, "NOT_MERGED"):
            errors.append("main_final_sha must be empty before Main merge")
    else:
        if manifest.get("merge_status") != "MERGED":
            errors.append("CLOSED round requires Main Thread merge")
        if not SHA40.fullmatch(str(manifest.get("main_final_sha", ""))):
            errors.append("CLOSED round requires a main_final_sha")


def _verify_interview_calibration(directory: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    raw_path = str(manifest.get("interview_calibration_packet", ""))
    if not raw_path:
        errors.append("interview_calibration_packet is required")
        return
    path = directory / raw_path
    _require(path, errors)
    if not path.exists():
        return
    _marker(path, "RED_THREAD_ONLY", errors)
    _marker(path, "answer_content_included: `NO`", errors)
    if re.search(r"(?im)(candidate answer|标准答案|更稳回答|包装话术|answer key)", _read(path)):
        errors.append("interview calibration must not contain answer or candidate-script content")
    declared = str(manifest.get("interview_calibration_packet_sha", ""))
    if not SHA64.fullmatch(declared) or declared != _sha256(path):
        errors.append("interview_calibration_packet_sha must match the round packet")


def _verify_deep_dive_chains(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    chains = manifest.get("deep_dive_chains")
    if not isinstance(chains, list) or not 12 <= len(chains) <= 18:
        errors.append("deep_dive_chains must contain 12 to 18 chains")
        return
    expected_ids = {f"Q{index:03d}" for index in range(1, 101)}
    seen: list[str] = []
    chain_ids: list[str] = []
    for index, chain in enumerate(chains, start=1):
        if not isinstance(chain, dict):
            errors.append(f"deep_dive_chains[{index}] must be a mapping")
            continue
        for key in ("chain_id", "root_claim", "question_ids", "primary_concept", "questioning_pattern_source"):
            if not chain.get(key):
                errors.append(f"deep_dive_chains[{index}] missing {key}")
        question_ids = chain.get("question_ids")
        if not isinstance(question_ids, list) or not 5 <= len(question_ids) <= 10:
            errors.append(f"deep_dive_chains[{index}] must contain 5 to 10 question IDs")
        else:
            seen.extend(str(value) for value in question_ids)
        chain_ids.append(str(chain.get("chain_id", "")))
        if chain.get("questioning_pattern_source") not in CALIBRATION_SOURCES:
            errors.append(f"deep_dive_chains[{index}] has invalid questioning_pattern_source")
        flags = ("counterfactual_used", "alternative_used", "failure_used", "reversal_used")
        if not any(chain.get(flag) is True for flag in flags):
            errors.append(f"deep_dive_chains[{index}] needs a counterfactual, alternative, failure, or reversal")
        if chain.get("constraint_injected") is not True:
            errors.append(f"deep_dive_chains[{index}] must inject at least one constraint")
        depth = chain.get("interview_depth")
        if not isinstance(depth, int) or isinstance(depth, bool) or not 0 <= depth <= 5:
            errors.append(f"deep_dive_chains[{index}] interview_depth must be an integer from 0 to 5")
    if len(chain_ids) != len(set(chain_ids)) or "" in chain_ids:
        errors.append("deep_dive_chains must have unique non-empty chain_id values")
    if len(seen) != 100 or set(seen) != expected_ids or len(set(seen)) != 100:
        errors.append("deep_dive_chains must cover Q001..Q100 exactly once")
    quality_status = manifest.get("question_quality_status")
    novel = manifest.get("novel_question_count")
    regression = manifest.get("regression_question_count")
    if quality_status not in {"READY", "QUESTION_QUALITY_BLOCKED"}:
        errors.append("question_quality_status must be READY or QUESTION_QUALITY_BLOCKED")
    if not all(isinstance(value, int) and not isinstance(value, bool) and value >= 0 for value in (novel, regression)):
        errors.append("novel_question_count and regression_question_count must be non-negative integers")
    elif novel + regression != 100:
        errors.append("novel_question_count plus regression_question_count must equal 100")
    elif quality_status == "READY" and (novel < 75 or regression > 25):
        errors.append("READY question quality requires at least 75 Novel and at most 25 Regression")
    elif quality_status == "QUESTION_QUALITY_BLOCKED" and novel >= 75 and regression <= 25:
        errors.append("QUESTION_QUALITY_BLOCKED cannot be used when the Novel/Regression gate is met")
    if state in POST_JUDGE_STATES:
        raw_path = str(manifest.get("interview_depth_artifact", ""))
        if not raw_path:
            errors.append("interview_depth_artifact is required after Red Judge")
        else:
            path = directory / raw_path
            _require(path, errors)
            if path.exists():
                _marker(path, "INTERVIEW_DEPTH", errors)
                _marker(path, "0–5", errors)


def _human_writing_warnings(directory: Path, manifest: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if manifest.get("human_writing_verifier_mode") != "WARNING_ONLY":
        return warnings
    for raw_path in manifest.get("canonical_part_a_files", []) or []:
        path = directory.parent.parent.parent / str(raw_path)
        if not path.exists():
            warnings.append(f"Part-A file not available for human-writing signal: {raw_path}")
            continue
        content = _read(path)
        heading_count = len(re.findall(r"(?m)^#{1,6}\s", content))
        list_lines = len(re.findall(r"(?m)^\s*[-*]\s", content))
        table_lines = len(re.findall(r"(?m)^\s*\|", content))
        english_tokens = len(re.findall(r"\b[A-Za-z][A-Za-z0-9_-]{3,}\b", content))
        if heading_count > 35:
            warnings.append(f"{raw_path}: high heading density ({heading_count})")
        if list_lines > 90:
            warnings.append(f"{raw_path}: high bullet density ({list_lines})")
        if table_lines > 120:
            warnings.append(f"{raw_path}: high table density ({table_lines})")
        if english_tokens > 600:
            warnings.append(f"{raw_path}: high English-token signal ({english_tokens})")
    return warnings


def verify_round(directory: Path) -> tuple[list[str], list[str]]:
    errors = V4.verify_round(directory)
    manifest_errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", manifest_errors)
    errors.extend(manifest_errors)
    if manifest.get("workflow_id") != V41_WORKFLOW:
        errors.append("round workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4.1")
    for key in (
        "conceptual_architecture_review",
        "red_reads_business_code",
        "blue_reads_business_code",
        "blue_uses_code_as_architecture_reason",
        "red_judge_part_a_first_pass",
        "main_merge_requires_chatgpt_verdict",
    ):
        if manifest.get(key) not in (True, False):
            errors.append(f"round manifest missing boolean V4.1 field: {key}")
    if manifest.get("conceptual_architecture_review") is not True:
        errors.append("conceptual_architecture_review must be true")
    snapshot = _yaml(directory / "canonical-snapshot.yaml", errors)
    for key in ("canonical_part_a_files", "canonical_part_b_files"):
        if not isinstance(snapshot.get(key), list) or not snapshot.get(key):
            errors.append(f"snapshot {key} must be a non-empty list")
    state = str(manifest.get("round_status", ""))
    _verify_interview_calibration(directory, manifest, errors)
    _verify_deep_dive_chains(directory, manifest, state, errors)
    _verify_no_code_context(directory, manifest, errors)
    _verify_part_a(directory, manifest, state, errors)
    _verify_candidate_and_merge(manifest, state, errors)
    if manifest.get("human_writing_verifier_mode") != "WARNING_ONLY":
        errors.append("human_writing_verifier_mode must be WARNING_ONLY")
    return errors, _human_writing_warnings(directory, manifest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bootstrap", type=Path)
    group.add_argument("--round", type=Path)
    args = parser.parse_args()
    if args.bootstrap:
        errors = verify_bootstrap(args.bootstrap)
        warnings: list[str] = []
    else:
        errors, warnings = verify_round(args.round)
    if errors:
        print("RED_BLUE_WORKFLOW_V4_1_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RED_BLUE_WORKFLOW_V4_1_VALID")
    for warning in warnings:
        print(f"WARNING: {warning}")
    print("HUMAN_WRITING_REVIEW: WARNING_ONLY; manual Red/ChatGPT review required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
