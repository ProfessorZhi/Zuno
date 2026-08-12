"""Verify the fixed 100-question Red/Blue V3 Round contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-002"
EXPECTED_PROTOCOL = "ZUNO-RED-BLUE-WORKFLOW-V3"
EXPECTED_LENSES = {
    "00 Overall Architecture": 12,
    "01 Product Surface": 6,
    "02 Input / Document Ingestion": 7,
    "03 Knowledge / Agentic GraphRAG": 11,
    "04 Model Gateway": 6,
    "05 Memory & Context": 8,
    "06 Agent Core / Planning & Control": 14,
    "07 Capability / Skill": 6,
    "08 Tool Runtime": 10,
    "09 Security": 8,
    "10 Observability & Eval": 6,
    "11 Infrastructure": 6,
}
EXPECTED_IDS = [f"Q{i:03d}" for i in range(1, 101)]
EXPECTED_DELTAS = [f"D{i:03d}" for i in range(1, 12)]
SECTION_RE = re.compile(r"(?ms)^## (Q\d{3})\s*\n(.*?)(?=^## Q\d{3}\s*$|\Z)")
DELTA_RE = re.compile(r"(?ms)^## (D\d{3})\s*\n(.*?)(?=^## D\d{3}\s*$|\Z)")
SCORE_RE = re.compile(
    r"^\|\s*(Q\d{3})\s*\|\s*([^|]+?)\s*\|\s*([0-5])\s*\|\s*(P[0-3])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(D\d{3})\s*\|",
    re.MULTILINE,
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sections(text: str, pattern: re.Pattern[str]) -> list[tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in pattern.finditer(text)]


def has_field(body: str, label: str) -> bool:
    return re.search(rf"(?m)^-\s*{re.escape(label)}\s*:\s*\S", body) is not None


def field(body: str, label: str) -> str | None:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}\s*:\s*(.*?)\s*$", body)
    return match.group(1).strip() if match else None


def _check_sections(
    errors: list[str], path: Path, required_labels: tuple[str, ...], expected_ids: list[str]
) -> dict[str, str]:
    rows = sections(_text(path), SECTION_RE)
    ids = [row[0] for row in rows]
    if ids != expected_ids:
        errors.append(f"{path.name} must contain exactly {expected_ids[0]}..{expected_ids[-1]}")
    bodies: dict[str, str] = {}
    for qid, body in rows:
        if qid in bodies:
            errors.append(f"{path.name} duplicate section: {qid}")
        bodies[qid] = body
        if re.search(r"(?im)^-\s*[^:]+:\s*(?:N/A|NA|TBD|TODO)\s*$", body):
            errors.append(f"{path.name} {qid} contains an empty escape value")
        for label in required_labels:
            if not has_field(body, label):
                errors.append(f"{path.name} {qid} missing required field: {label}")
    return bodies


QUESTION_FIELDS = (
    "Question ID", "Round ID", "11+1 Lens", "Canonical Doc", "Target Component", "Question",
    "Attack Intent", "Assumption Being Attacked", "Failure Scenario", "Simpler Alternative",
    "OSS Alternative", "Severity", "Closure Class", "Expected Depth", "Required Evidence",
    "Kill Condition", "Question Type",
)
ANSWER_FIELDS = (
    "Question ID", "Round ID", "Blue Answer", "Current / Target / Future / History", "Problem",
    "Target Decision", "Owner", "State Transition", "Failure", "Failure Propagation", "Retry",
    "Recovery", "Idempotency", "Security", "Observability", "Alternative", "OSS Alternative",
    "Tradeoff", "Test / Benchmark", "Evidence", "Remaining Gap", "Reversal Condition", "Delta Ref",
    "Red Score Context",
)
DECISION_FIELDS = (
    "Question ID", "Red Score", "Red Finding", "Blue Decision", "Decision Rationale", "Architecture Before",
    "Architecture After", "Complexity Added", "Complexity Removed", "Contract Changed", "Owner Changed",
    "State Changed", "Failure Semantics Changed", "Canonical Doc", "ADR Required?", "Fact Gap?",
    "Implementation Gap", "Measurement Gap", "External Gap", "Sync Mode", "Delta Ref", "Reversal Condition",
)


def verify_round(session: Path) -> list[str]:
    errors: list[str] = []
    required_files = (
        "README.md", "manifest.yaml", "canonical-snapshot.md", "11-plus-1-coverage-map.md", "questions.md",
        "blue-answers.md", "red-scores.md", "blue-decisions.md", "architecture-deltas.md",
        "canonical-sync-record.md", "scorecard.md", "gap-register.md", "adr-escalations.md",
        "chatgpt-review-package.md", "round-report.md",
    )
    for name in required_files:
        if not (session / name).exists():
            errors.append(f"missing required V3 file: {name}")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]
    if manifest.get("protocol_version") != EXPECTED_PROTOCOL:
        errors.append(f"manifest protocol_version must be {EXPECTED_PROTOCOL}")
    if manifest.get("question_budget") != 100 or manifest.get("actual_question_count") != 100:
        errors.append("manifest must declare question_budget=100 and actual_question_count=100")
    if manifest.get("category_distribution") != EXPECTED_LENSES:
        errors.append("manifest category_distribution does not match the fixed 11+1 quota")
    for key in ("answer_count", "score_count", "decision_count"):
        if manifest.get(key) != 100:
            errors.append(f"manifest {key} must equal 100")
    if manifest.get("novel_question_count") != 80 or manifest.get("regression_question_count") != 20:
        errors.append("manifest novelty must be 80 and regression must be 20")
    if manifest.get("novelty_threshold_percent", 0) < 70 or manifest.get("regression_max_percent", 100) > 30:
        errors.append("manifest novelty/regression thresholds are not satisfied")
    for key, expected in {
        "canonical_sync_status": "APPLIED", "round_status": "COMPLETE", "new_a_p0": 0,
        "original_p0_closed": 0, "implementation_program": "READY_FOR_TASK_DEFINITION",
        "round_003_status": "READY_NOT_STARTED", "runtime_changed": "NONE",
        "schema_or_migration_changed": "NONE", "facts_changed": "NONE",
        "adr_escalation_count": 0, "user_gate_escalation_count": 0,
    }.items():
        if manifest.get(key) != expected:
            errors.append(f"manifest {key} must be {expected!r}")

    question_bodies = _check_sections(errors, session / "questions.md", QUESTION_FIELDS, EXPECTED_IDS)
    answer_bodies = _check_sections(errors, session / "blue-answers.md", ANSWER_FIELDS, EXPECTED_IDS)
    decision_bodies = _check_sections(errors, session / "blue-decisions.md", DECISION_FIELDS, EXPECTED_IDS)

    lens_counts: dict[str, int] = {lens: 0 for lens in EXPECTED_LENSES}
    novelty_counts = {"NOVEL": 0, "REGRESSION": 0}
    for qid in EXPECTED_IDS:
        body = question_bodies.get(qid, "")
        lens = field(body, "11+1 Lens")
        qtype = field(body, "Question Type")
        if lens not in lens_counts:
            errors.append(f"{qid} has unknown 11+1 Lens: {lens}")
        else:
            lens_counts[lens] += 1
        if qtype not in novelty_counts:
            errors.append(f"{qid} Question Type must be NOVEL or REGRESSION")
        else:
            novelty_counts[qtype] += 1
        for other, label in ((answer_bodies, "Question ID"), (decision_bodies, "Question ID")):
            if field(other.get(qid, ""), label) != qid:
                errors.append(f"{qid} {label} does not self-identify")
    if lens_counts != EXPECTED_LENSES:
        errors.append(f"question lens counts mismatch: {lens_counts}")
    if novelty_counts != {"NOVEL": 80, "REGRESSION": 20}:
        errors.append(f"novelty counts mismatch: {novelty_counts}")

    score_rows = SCORE_RE.findall(_text(session / "red-scores.md"))
    if len(score_rows) != 100 or [row[0] for row in score_rows] != EXPECTED_IDS:
        errors.append("red-scores.md must contain exactly one ordered row for Q001..Q100")
    score_ids = {row[0] for row in score_rows}
    for qid, lens, score, severity, closure, decision, delta in score_rows:
        if qid not in score_ids:
            errors.append(f"score row missing {qid}")
        if question_bodies.get(qid) and lens.strip() != field(question_bodies[qid], "11+1 Lens"):
            errors.append(f"red score lens does not match question for {qid}")
        if field(decision_bodies.get(qid, ""), "Red Score") != f"{score}/5":
            errors.append(f"blue decision score does not match red score for {qid}")
        if field(decision_bodies.get(qid, ""), "Delta Ref") != delta:
            errors.append(f"blue decision delta does not match red score for {qid}")

    delta_sections = sections(_text(session / "architecture-deltas.md"), DELTA_RE)
    if [delta_id for delta_id, _ in delta_sections] != EXPECTED_DELTAS:
        errors.append("architecture-deltas.md must contain exactly D001..D011")
    for delta_id, body in delta_sections:
        if not re.search(r"(?m)^- Source Questions:\s*Q\d{3}", body):
            errors.append(f"{delta_id} has no Question trace")
        if not re.search(r"(?m)^- Affected Canonical Docs:\s*docs/project/", body):
            errors.append(f"{delta_id} has no Canonical Doc trace")
        if field(body, "Apply Mode") not in {"AUTO_APPLY", "ADR_ESCALATION", "USER_GATE_ESCALATION"}:
            errors.append(f"{delta_id} has invalid Apply Mode")

    sync_text = _text(session / "canonical-sync-record.md")
    if "Status: APPLIED" not in sync_text or "Canonical Before SHA:" not in sync_text:
        errors.append("canonical-sync-record.md must record APPLIED status and before SHA")
    if len(re.findall(r"(?m)^\| D\d{3}\s*\|", sync_text)) != 11:
        errors.append("canonical-sync-record.md must map all 11 deltas")
    if "Facts changed: NONE" not in _text(session / "round-report.md") and "facts_changed: NONE" not in _text(session / "manifest.yaml"):
        errors.append("Round must explicitly state that facts were not changed")
    review = _text(session / "chatgpt-review-package.md")
    for marker in ("## Scores", "## Lowest 20 Questions", "## Highest-risk 20 Questions", "## Architecture Deltas", "## Components", "## Changes", "## Contradictions / gaps", "## Proposed Round-003 Focus"):
        if marker not in review:
            errors.append(f"review package missing section: {marker}")
    if "production_proven" in (review + _text(session / "round-report.md")):
        errors.append("Round package must not promote production_proven")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Red/Blue Workflow V3 Round")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_round(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue V3 round verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
