"""Recompute the Red/Blue V3 scorecard instead of trusting its summary."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-002"
SCORE_RE = re.compile(
    r"^\|\s*(Q\d{3})\s*\|\s*([^|]+?)\s*\|\s*([0-5])\s*\|\s*(P[0-3])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(D\d{3})\s*\|",
    re.MULTILINE,
)
LENS_COUNTS = {
    "00 Overall Architecture": 12, "01 Product Surface": 6, "02 Input / Document Ingestion": 7,
    "03 Knowledge / Agentic GraphRAG": 11, "04 Model Gateway": 6, "05 Memory & Context": 8,
    "06 Agent Core / Planning & Control": 14, "07 Capability / Skill": 6, "08 Tool Runtime": 10,
    "09 Security": 8, "10 Observability & Eval": 6, "11 Infrastructure": 6,
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _summary_yaml(text: str) -> dict:
    match = re.search(r"```yaml\s*(.*?)\s*```", text, re.DOTALL)
    if not match:
        raise ValueError("scorecard is missing its YAML summary")
    value = yaml.safe_load(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("scorecard YAML summary must be a mapping")
    return value


def verify_score(session: Path) -> list[str]:
    errors: list[str] = []
    scores = SCORE_RE.findall(_text(session / "red-scores.md"))
    expected_ids = [f"Q{i:03d}" for i in range(1, 101)]
    if [row[0] for row in scores] != expected_ids:
        return ["red-scores.md must contain ordered Q001..Q100 before score recomputation"]
    raw = sum(int(row[2]) for row in scores)
    normalized = round(raw / 5, 2)
    lens_raw: dict[str, int] = {lens: 0 for lens in LENS_COUNTS}
    lens_seen: dict[str, int] = {lens: 0 for lens in LENS_COUNTS}
    severity_counts = {f"P{i}": 0 for i in range(4)}
    closure_counts = {key: 0 for key in ("A", "I", "E", "X")}
    for _, lens, score, severity, closure, _, _ in scores:
        lens = lens.strip()
        if lens not in lens_raw:
            errors.append(f"unknown lens in scorecard: {lens}")
            continue
        lens_raw[lens] += int(score)
        lens_seen[lens] += 1
        severity_counts[severity] += 1
        closure_key = closure.strip().split("-", 1)[-1]
        if closure_key in closure_counts:
            closure_counts[closure_key] += 1
    if lens_seen != LENS_COUNTS:
        errors.append(f"lens question counts mismatch: {lens_seen}")
    try:
        summary = _summary_yaml(_text(session / "scorecard.md"))
    except (ValueError, yaml.YAMLError) as exc:
        return [str(exc)]
    expected_summary = {
        "question_count": 100, "answer_count": 100, "score_count": 100, "decision_count": 100,
        "novel_question_count": 80, "regression_question_count": 20, "raw_score": raw,
        "normalized_score": normalized, "p0_count": severity_counts["P0"], "p1_count": severity_counts["P1"],
        "p2_count": severity_counts["P2"], "p3_count": severity_counts["P3"],
        "canonical_sync_status": "APPLIED", "round_status": "COMPLETE", "round_003_status": "READY_NOT_STARTED",
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(f"scorecard {key}: expected {expected!r}, got {summary.get(key)!r}")
    declared_closure = summary.get("closure_class_counts")
    if declared_closure != closure_counts:
        errors.append(f"scorecard closure counts: expected {closure_counts}, got {declared_closure}")
    table_rows = re.findall(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d.]+)\s*\|", _text(session / "scorecard.md"), re.MULTILINE)
    if len(table_rows) != 12:
        errors.append("scorecard must have one lens table row for each of 11+1 lenses")
    for lens, questions, table_raw, table_normalized in table_rows:
        lens = lens.strip()
        if lens not in LENS_COUNTS:
            errors.append(f"scorecard table has unknown lens: {lens}")
            continue
        if int(questions) != LENS_COUNTS[lens] or int(table_raw) != lens_raw[lens] or round(float(table_normalized), 2) != round(lens_raw[lens] / LENS_COUNTS[lens] / 5 * 100, 2):
            errors.append(f"scorecard lens row does not match recomputation: {lens}")
    if raw != 371 or normalized != 74.2:
        errors.append(f"Round-002 expected deterministic score 371/500 and 74.20, got {raw}/{normalized}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Red/Blue V3 scorecard")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_score(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue V3 score verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
