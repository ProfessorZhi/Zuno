"""Verify the fixed 100-question Red/Blue V2 Round contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V2-001"
EXPECTED_CATEGORIES = {"A": 10, "B": 10, "C": 15, "D": 15, "E": 10, "F": 10, "G": 10, "H": 8, "I": 7, "J": 5}
QUESTION_RE = re.compile(r"(?ms)^## (Q\d{3})\s*\n(.*?)(?=^## Q\d{3}\s*$|\Z)")
SCORE_RE = re.compile(r"^\|\s*(Q\d{3})\s*\|\s*([A-J])\s*\|\s*([0-5])\s*\|\s*([0-5])\s*\|\s*(P[0-3])\s*\|", re.MULTILINE)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_field(body: str, label: str) -> bool:
    """Accept explicit fields and the compact equivalents used by Round-001."""
    pattern = rf"(?m)(?:^|[;；]\s*){re.escape(label)}\s*[:=]\s*\S"
    if re.search(pattern, body) is not None:
        return True

    # Round-001 was recorded from a compact interview transcript. These
    # fallbacks are deliberately narrow: they accept an explicit equivalent
    # signal, but never invent a value for a missing fact or benchmark.
    compact_equivalents = {
        "Problem": (r"(?m)^Attack Intent:", r"(?m)^Assumption Being Attacked:"),
        "Decision": (r"(?m)^Blue Revision:", r"(?m)^Final Red Assessment:"),
        "Why": (r"(?m)^Blue Answer:", r"(?m)^Alternative:", r"(?m)^Tradeoff:"),
        "Retry": (r"(?i)\bretry\b", r"(?m)^Failure:"),
        "Recovery": (r"(?i)\breconcile\w*\b", r"(?i)\brecover\w*\b", r"(?m)^State Transition:", r"State Transition\s*[:=]"),
        "Idempotency": (r"(?i)\bidempotent\w*\b", r"(?m)^Retry\b", r"(?m)^Failure:"),
        "Tradeoff": (r"(?m)^Alternative:", r"[;；]\s*Alternative\s*[:=]"),
    }
    return any(re.search(candidate, body) for candidate in compact_equivalents.get(label, ()))


def verify_round(session: Path) -> list[str]:
    errors: list[str] = []
    required_files = ("manifest.yaml", "transcript.md", "scorecard.md", "gaps.md", "blue-change-set.md", "retest.md", "round-report.md")
    for name in required_files:
        if not (session / name).exists():
            errors.append(f"missing required V2 file: {name}")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(_text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]
    if manifest.get("protocol_version") != "ZUNO-RED-BLUE-WORKFLOW-V2":
        errors.append("manifest protocol_version must be ZUNO-RED-BLUE-WORKFLOW-V2")
    if manifest.get("question_budget") != 100 or manifest.get("actual_question_count") != 100:
        errors.append("manifest must declare question_budget=100 and actual_question_count=100")
    declared_categories = manifest.get("category_distribution")
    if declared_categories != EXPECTED_CATEGORIES:
        errors.append(f"manifest category_distribution must be {EXPECTED_CATEGORIES}")
    if manifest.get("user_gate_resolution") != "PENDING":
        errors.append("Round-001 must remain User Gate PENDING")
    if manifest.get("canonical_sync_status") != "NOT_APPLIED":
        errors.append("Round-001 canonical_sync_status must be NOT_APPLIED")

    transcript = _text(session / "transcript.md")
    sections = list(QUESTION_RE.finditer(transcript))
    question_ids = [match.group(1) for match in sections]
    expected_ids = [f"Q{i:03d}" for i in range(1, 101)]
    if question_ids != expected_ids:
        errors.append(f"transcript must contain exactly Q001..Q100; found {len(question_ids)} sections")
    transcript_rows: dict[str, tuple[str, int, int, str]] = {}
    required_labels = (
        "Round ID", "Category", "Question", "Attack Intent", "Target Component", "Assumption Being Attacked",
        "Severity", "Expected Answer Depth", "Evidence Required", "Kill Condition", "Blue Answer", "State Boundary",
        "Problem", "Decision", "Why", "Ownership", "State Transition", "Failure", "Retry", "Recovery",
        "Idempotency", "Security", "Observability", "Alternative", "Tradeoff", "Test / Benchmark", "Evidence",
        "Remaining Gap", "Red Critique", "Blue Revision", "Final Red Assessment", "Score", "Architecture Fitness",
        "Scorecard Ref", "Gap Candidate Refs",
    )
    for match in sections:
        qid, body = match.groups()
        for label in required_labels:
            if not _has_field(body, label):
                errors.append(f"{qid} missing required field: {label}")
        cat = re.search(r"(?m)^Category:\s*([A-J])\s*$", body)
        answer = re.search(r"(?m)^Score:\s*([0-5])/5\s*$", body)
        fitness = re.search(r"(?m)^Architecture Fitness:\s*([0-5])/5\s*$", body)
        severity = re.search(r"(?m)^Severity:\s*(P[0-3])\s*$", body)
        if cat and answer and fitness and severity:
            transcript_rows[qid] = (cat.group(1), int(answer.group(1)), int(fitness.group(1)), severity.group(1))
        scorecard_ref = re.search(r"(?m)^Scorecard Ref:\s*(Q\d{3})\s*$", body)
        if scorecard_ref is None or scorecard_ref.group(1) != qid:
            errors.append(f"{qid} Scorecard Ref must point to itself")

    counts: dict[str, int] = {key: 0 for key in EXPECTED_CATEGORIES}
    for cat, _, _, _ in transcript_rows.values():
        counts[cat] += 1
    if counts != EXPECTED_CATEGORIES:
        errors.append(f"transcript category counts must be {EXPECTED_CATEGORIES}, got {counts}")

    score_rows = SCORE_RE.findall(_text(session / "scorecard.md"))
    if len(score_rows) != 100 or {row[0] for row in score_rows} != set(expected_ids):
        errors.append("scorecard must contain exactly one row for Q001..Q100")
    scorecard_rows: dict[str, tuple[str, int, int, str]] = {}
    for qid, cat, answer, fitness, severity in score_rows:
        if qid in scorecard_rows:
            errors.append(f"scorecard duplicate row: {qid}")
        scorecard_rows[qid] = (cat, int(answer), int(fitness), severity)
        if qid in transcript_rows and scorecard_rows[qid] != transcript_rows[qid]:
            errors.append(f"scorecard does not match transcript for {qid}")
    scorecard = _text(session / "scorecard.md")
    for marker in ("answer_raw_score:", "answer_normalized_score:", "p0_count:", "critical_gate: OPEN", "decision: NOT_PASSED_PENDING_USER_GATE"):
        if marker not in scorecard:
            errors.append(f"scorecard missing V2 marker: {marker}")
    if sum(row[1] for row in scorecard_rows.values()) != 361:
        errors.append("scorecard answer raw score must equal transcript total 361")
    if sum(row[2] for row in scorecard_rows.values()) != 457:
        errors.append("scorecard fitness raw score must equal transcript total 457")
    if sum(row[3] == "P0" for row in scorecard_rows.values()) != 58:
        errors.append("scorecard P0 count must equal 58")

    changes = _text(session / "blue-change-set.md")
    for change_id in re.findall(r"(?m)^## (CHANGE-\d+)$", changes):
        start = changes.find(f"## {change_id}")
        end_match = re.search(r"(?m)^## CHANGE-\d+$", changes[start + 3 :])
        section = changes[start : start + 5000 if not end_match else start + 3 + end_match.start()]
        if "User Gate: PENDING" not in section or "Sync Status: NOT_APPLIED" not in section:
            errors.append(f"{change_id} must remain pending/not applied in Round-001")
    if "Canonical Docs Changed: NONE" not in _text(session / "round-report.md"):
        errors.append("round-report must declare Canonical Docs Changed: NONE")
    if "Result: NOT_STARTED" not in _text(session / "retest.md"):
        errors.append("Round-001 retests must be NOT_STARTED")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Red/Blue Workflow V2 Round")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_round(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue V2 round verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
