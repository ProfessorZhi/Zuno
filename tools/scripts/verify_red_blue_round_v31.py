"""Verify the fixed 100-question Red/Blue V3.1 Round-003 contract."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SESSION = ROOT / "project-reconstruction-lab" / "sessions" / "RB-WORKFLOW-V3-ROUND-003"
EXPECTED_PROTOCOL = "ZUNO-RED-BLUE-WORKFLOW-V3.1"
EXPECTED_IDS = [f"Q{i:03d}" for i in range(1, 101)]
EXPECTED_DELTAS = [f"D{i:03d}" for i in range(1, 13)]
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
SECTION_RE = re.compile(r"(?ms)^## (Q\d{3})\s*\n(.*?)(?=^## Q\d{3}\s*$|\Z)")
DELTA_RE = re.compile(r"(?ms)^## (D\d{3})\s*\n(.*?)(?=^## D\d{3}\s*$|\Z)")
SCORE_RE = re.compile(
    r"^\|\s*(Q\d{3})\s*\|\s*([^|]+?)\s*\|\s*([0-5])\s*\|\s*(P[0-3])\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(BOTH|PART_A|PART_B|NONE)\s*\|\s*(YES|NO)\s*\|\s*(YES|NO)\s*\|\s*(D\d{3})\s*\|",
    re.MULTILINE,
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sections(content: str, pattern: re.Pattern[str]) -> list[tuple[str, str]]:
    return [(match.group(1), match.group(2)) for match in pattern.finditer(content)]


def field(body: str, label: str) -> str | None:
    match = re.search(rf"(?m)^-\s*{re.escape(label)}\s*:\s*(.*?)\s*$", body)
    return match.group(1).strip() if match else None


def check_sections(
    errors: list[str], path: Path, labels: tuple[str, ...]
) -> dict[str, str]:
    rows = sections(text(path), SECTION_RE)
    ids = [row[0] for row in rows]
    if ids != EXPECTED_IDS:
        errors.append(f"{path.name} must contain exactly Q001..Q100 in order")
    bodies: dict[str, str] = {}
    for qid, body in rows:
        if qid in bodies:
            errors.append(f"{path.name} has duplicate section {qid}")
        bodies[qid] = body
        if re.search(r"(?im)^-\s*[^:]+:\s*(?:N/A|NA|TBD|TODO|undefined)\s*$", body):
            errors.append(f"{path.name} {qid} contains an empty escape value")
        for label in labels:
            value = field(body, label)
            if value is None or not value.strip():
                errors.append(f"{path.name} {qid} missing required field: {label}")
    return bodies


QUESTION_FIELDS = (
    "Question ID", "Round ID", "11+1 Lens", "Canonical Owner Doc", "Target Component",
    "Question", "Attack Intent", "Assumption Being Attacked", "Failure Scenario",
    "Simpler Alternative", "OSS Alternative", "Severity", "Closure Class", "Expected Depth",
    "Required Evidence", "Part A Concern", "Part B Concern", "Kill Condition", "Question Type",
)
ANSWER_FIELDS = (
    "Question ID", "Round ID", "Blue Answer", "Current / Target / Future / History", "Problem",
    "Target Decision", "Owner", "State Transition", "Failure", "Failure Propagation", "Retry",
    "Recovery", "Idempotency", "Security", "Observability", "Alternative", "OSS Alternative",
    "Tradeoff", "Test / Benchmark", "Evidence", "Remaining Gap", "Reversal Condition", "Delta Ref",
    "Red Score Context", "Document Impact", "Part A Change Required?", "Part B Change Required?",
    "Canonical Owner Doc",
)
DECISION_FIELDS = (
    "Question ID", "Red Score", "Red Finding", "Blue Decision", "Decision Rationale", "Architecture Before",
    "Architecture After", "Complexity Added", "Complexity Removed", "Contract Changed", "Owner Changed",
    "State Changed", "Failure Semantics Changed", "Canonical Doc", "ADR Required?", "Fact Gap?",
    "Implementation Gap", "Measurement Gap", "External Gap", "Sync Mode", "Delta Ref", "Reversal Condition",
    "document_impact", "Part A Change Required?", "Part B Change Required?", "Canonical Owner Doc",
)


def verify_round(session: Path) -> list[str]:
    errors: list[str] = []
    required = (
        "README.md", "manifest.yaml", "baseline-audit.md", "document-quality-scorecard.md",
        "canonical-snapshot.md", "11-plus-1-coverage-map.md", "questions.md", "blue-answers.md",
        "red-scores.md", "blue-decisions.md", "architecture-deltas.md", "canonical-sync-record.md",
        "scorecard.md", "gap-register.md", "adr-escalations.md", "chatgpt-review-package.md", "round-report.md",
    )
    for name in required:
        if not (session / name).exists():
            errors.append(f"missing required V3.1 file: {name}")
    if errors:
        return errors

    try:
        manifest = yaml.safe_load(text(session / "manifest.yaml"))
    except yaml.YAMLError as exc:
        return [f"manifest.yaml invalid YAML: {exc}"]
    if not isinstance(manifest, dict):
        return ["manifest.yaml must contain a mapping"]

    for key, expected in {
        "protocol_version": EXPECTED_PROTOCOL,
        "session_id": "RB-WORKFLOW-V3-ROUND-003",
        "round_id": "RB-WORKFLOW-V3-ROUND-003",
        "question_budget": 100,
        "actual_question_count": 100,
        "answer_count": 100,
        "score_count": 100,
        "decision_count": 100,
        "novel_question_count": 85,
        "regression_question_count": 15,
        "canonical_sync_status": "APPLIED",
        "round_status": "COMPLETE",
        "new_a_p0": 0,
        "original_p0_closed": 0,
        "implementation_program": "READY_FOR_TASK_DEFINITION",
        "round_004_status": "READY_NOT_STARTED",
        "runtime_changed": "NONE",
        "schema_or_migration_changed": "NONE",
        "facts_changed": "NONE",
        "adr_escalation_count": 0,
        "user_gate_escalation_count": 0,
        "part_a_quality_gate": "PASS",
        "part_b_quality_gate": "PASS",
        "document_quality_status": "DOC_QUALITY_COMPLETE",
    }.items():
        if manifest.get(key) != expected:
            errors.append(f"manifest {key} must be {expected!r}")
    if manifest.get("novelty_threshold_percent", 0) < 70:
        errors.append("novelty threshold must be at least 70 percent")
    if manifest.get("regression_max_percent", 100) > 30:
        errors.append("regression maximum must be at most 30 percent")
    if manifest.get("category_distribution") != EXPECTED_LENSES:
        errors.append("manifest category_distribution does not match the fixed 11+1 quota")

    question_bodies = check_sections(errors, session / "questions.md", QUESTION_FIELDS)
    answer_bodies = check_sections(errors, session / "blue-answers.md", ANSWER_FIELDS)
    decision_bodies = check_sections(errors, session / "blue-decisions.md", DECISION_FIELDS)
    lens_counts = {lens: 0 for lens in EXPECTED_LENSES}
    type_counts = {"NOVEL": 0, "REGRESSION": 0}
    lens_number = {lens: index + 1 for index, lens in enumerate(EXPECTED_LENSES)}

    for qid in EXPECTED_IDS:
        qbody = question_bodies.get(qid, "")
        abody = answer_bodies.get(qid, "")
        dbody = decision_bodies.get(qid, "")
        lens = field(qbody, "11+1 Lens")
        qtype = field(qbody, "Question Type")
        impact = field(abody, "Document Impact")
        if lens not in lens_counts:
            errors.append(f"{qid} has unknown 11+1 Lens: {lens}")
        else:
            lens_counts[lens] += 1
        if qtype not in type_counts:
            errors.append(f"{qid} Question Type must be NOVEL or REGRESSION")
        else:
            type_counts[qtype] += 1
        if field(abody, "Question ID") != qid or field(dbody, "Question ID") != qid:
            errors.append(f"{qid} does not self-identify in answers and decisions")
        if field(abody, "Canonical Owner Doc") != field(qbody, "Canonical Owner Doc"):
            errors.append(f"{qid} answer owner does not match question owner")
        if field(dbody, "Canonical Owner Doc") != field(qbody, "Canonical Owner Doc"):
            errors.append(f"{qid} decision owner does not match question owner")
        answer_impact = field(abody, "Document Impact")
        decision_impact = field(dbody, "document_impact")
        if impact not in {"PART_A", "PART_B", "BOTH", "NONE"}:
            errors.append(f"{qid} answer has invalid Document Impact: {impact}")
        if answer_impact != impact or decision_impact != impact:
            errors.append(f"{qid} document impact does not match across artifacts")
        expected_a = "YES" if impact in {"PART_A", "BOTH"} else "NO"
        expected_b = "YES" if impact in {"PART_B", "BOTH"} else "NO"
        for body, label, expected in (
            (abody, "Part A Change Required?", expected_a),
            (abody, "Part B Change Required?", expected_b),
            (dbody, "Part A Change Required?", expected_a),
            (dbody, "Part B Change Required?", expected_b),
        ):
            if field(body, label) != expected:
                errors.append(f"{qid} {label} must be {expected}")
        delta = f"D{lens_number.get(lens, 0):03d}"
        if field(abody, "Delta Ref") != delta or field(dbody, "Delta Ref") != delta:
            errors.append(f"{qid} Delta Ref must be {delta}")
    if lens_counts != EXPECTED_LENSES:
        errors.append(f"question lens counts mismatch: {lens_counts}")
    if type_counts != {"NOVEL": 85, "REGRESSION": 15}:
        errors.append(f"novelty counts mismatch: {type_counts}")

    score_rows = SCORE_RE.findall(text(session / "red-scores.md"))
    if len(score_rows) != 100 or [row[0] for row in score_rows] != EXPECTED_IDS:
        errors.append("red-scores.md must contain exactly one ordered row for Q001..Q100")
    raw_score = 0
    p0 = p1 = p2 = p3 = 0
    for qid, lens, score_text, severity, closure, decision, impact, part_a, part_b, delta in score_rows:
        score = int(score_text)
        raw_score += score
        if severity == "P0":
            p0 += 1
        elif severity == "P1":
            p1 += 1
        elif severity == "P2":
            p2 += 1
        else:
            p3 += 1
        qbody = question_bodies.get(qid, "")
        dbody = decision_bodies.get(qid, "")
        if lens.strip() != field(qbody, "11+1 Lens"):
            errors.append(f"red score lens does not match question for {qid}")
        if impact != field(answer_bodies.get(qid, ""), "Document Impact"):
            errors.append(f"red score impact does not match answer for {qid}")
        if field(dbody, "Red Score") != f"{score}/5":
            errors.append(f"blue decision score does not match red score for {qid}")
        if field(dbody, "Blue Decision") != decision.strip():
            errors.append(f"blue decision does not match red score for {qid}")
        if field(dbody, "Delta Ref") != delta:
            errors.append(f"blue decision delta does not match red score for {qid}")
        if part_a != ("YES" if impact in {"PART_A", "BOTH"} else "NO"):
            errors.append(f"red score Part A impact mismatch for {qid}")
        if part_b != ("YES" if impact in {"PART_B", "BOTH"} else "NO"):
            errors.append(f"red score Part B impact mismatch for {qid}")
    if raw_score != 392:
        errors.append(f"raw score must be 392, got {raw_score}")
    if (p0, p1, p2, p3) != (0, 15, 85, 0):
        errors.append(f"severity distribution must be 0/15/85/0, got {p0}/{p1}/{p2}/{p3}")

    delta_sections = sections(text(session / "architecture-deltas.md"), DELTA_RE)
    if [delta_id for delta_id, _ in delta_sections] != EXPECTED_DELTAS:
        errors.append("architecture-deltas.md must contain exactly D001..D012")
    for delta_id, body in delta_sections:
        for label in ("Source Questions", "Affected Canonical Docs", "Part A Impact", "Part B Impact", "Document Impact", "Apply Mode"):
            if not re.search(rf"(?m)^-\s*{re.escape(label)}:\s*\S", body):
                errors.append(f"{delta_id} missing {label}")
        if field(body, "Apply Mode") != "AUTO_APPLY":
            errors.append(f"{delta_id} must be AUTO_APPLY because no ADR or User Gate was escalated")
        if not re.search(r"(?m)^-\s*Trace:\s*Q\d{3}", body):
            errors.append(f"{delta_id} has no Question trace")

    sync = text(session / "canonical-sync-record.md")
    if "Status: APPLIED" not in sync or "Canonical Before SHA:" not in sync:
        errors.append("canonical-sync-record.md must record APPLIED status and before SHA")
    if len(re.findall(r"(?m)^\| D\d{3}\s*\|", sync)) != 12:
        errors.append("canonical-sync-record.md must map all 12 deltas")

    review = text(session / "chatgpt-review-package.md")
    for marker in (
        "## Part A before score", "## Part A after score", "## Part B before score", "## Part B after score",
        "## Worst Part A docs", "## Worst Part B docs", "## Narrative regressions", "## Contract regressions",
        "## Canonical docs with BOTH changes", "## Round-specific text removed from Canonical",
        "## Remaining documentation debt",
    ):
        if marker not in review:
            errors.append(f"review package missing section: {marker}")

    for canonical in (
        ROOT / "docs/project/architecture/architecture.md",
        ROOT / "docs/project/product/product-architecture.md",
        ROOT / "docs/project/domain/legal-domain-model.md",
        ROOT / "docs/project/domain/domain-state-lifecycle.md",
        ROOT / "docs/project/agents/agent-platform.md",
        ROOT / "docs/project/agents/multi-agent-runtime.md",
        ROOT / "docs/project/knowledge/knowledge-evidence-architecture.md",
        ROOT / "docs/project/services/service-architecture.md",
        ROOT / "docs/project/data/data-ownership-and-recovery.md",
        ROOT / "docs/project/security/security-architecture.md",
        ROOT / "docs/project/eval/legal-eval-and-benchmark.md",
        ROOT / "docs/project/deployment/microservice-deployment.md",
    ):
        canonical_text = text(canonical)
        if "## Part A — Architecture Narrative" not in canonical_text or "## Part B — Detailed Architecture Specification" not in canonical_text:
            errors.append(f"{canonical.relative_to(ROOT)} lacks Part A/Part B")
        if re.search(r"(?im)Round-\d+|\bD\d{3}\b|\bQ\d{3}\b", canonical_text):
            errors.append(f"{canonical.relative_to(ROOT)} contains Round/D/Q process trace")
        if re.search(r"(?im)production_proven|quality is higher than WorkBuddy|GraphRAG is superior to RAG", canonical_text):
            errors.append(f"{canonical.relative_to(ROOT)} contains an unsupported promotion claim")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Red/Blue Workflow V3.1 Round-003")
    parser.add_argument("session", nargs="?", type=Path, default=DEFAULT_SESSION)
    args = parser.parse_args(argv)
    session = args.session if args.session.is_absolute() else ROOT / args.session
    errors = verify_round(session)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue V3.1 round verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
