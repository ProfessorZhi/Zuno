"""Verify the V3.1.3 Round-005 closure-class and recovery review contract."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SESSION = ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005"
IDS = [f"Q{i:03d}" for i in range(1, 101)]
LENSES = {
    "00 Overall Architecture": (1, 12),
    "01 Product Surface": (13, 18),
    "02 Input / Document Ingestion": (19, 25),
    "03 Knowledge / Agentic GraphRAG": (26, 35),
    "04 Model Gateway": (36, 40),
    "05 Memory & Context": (41, 48),
    "06 Agent Core / Planning & Control": (49, 63),
    "07 Capability / Skill": (64, 69),
    "08 Tool Runtime": (70, 79),
    "09 Security": (80, 87),
    "10 Observability & Eval": (88, 93),
    "11 Infrastructure": (94, 100),
}
CLASSES = {"A", "I", "E", "X"}
SECONDARY = {"NONE", "A", "I", "E", "X"}
IMPACTS = {"PART_A", "PART_B", "BOTH", "NONE"}
SYNC_MODES = {"SECTION_REWRITE", "FULL_PART_REWRITE", "NO_CHANGE", "ESCALATION"}
DECISIONS = {
    "KEEP", "CLARIFY", "REFINE", "SPLIT", "MERGE", "REPLACE", "DELETE", "DEFER",
    "FACT_RECOVERY", "IMPLEMENTATION_GAP", "MEASUREMENT_GAP", "EXTERNAL_GAP",
    "ADR_ESCALATION", "USER_GATE_ESCALATION",
}
TABLE_LINE = re.compile(r"^\|\s*(Q\d{3})\s*\|(.+)\|\s*$")

CANONICAL_OWNER_ALIASES = {
    "docs/project/product/": "docs/history/superseded-document-taxonomy/project-topics/product/",
    "docs/project/domain/": "docs/history/superseded-document-taxonomy/project-topics/domain/",
    "docs/project/agents/": "docs/history/superseded-document-taxonomy/project-topics/agents/",
    "docs/project/knowledge/": "docs/history/superseded-document-taxonomy/project-topics/knowledge/",
    "docs/project/services/": "docs/history/superseded-document-taxonomy/project-topics/services/",
    "docs/project/data/": "docs/history/superseded-document-taxonomy/project-topics/data/",
    "docs/project/security/": "docs/history/superseded-document-taxonomy/project-topics/security/",
    "docs/project/eval/": "docs/history/superseded-document-taxonomy/project-topics/eval/",
    "docs/project/deployment/": "docs/history/superseded-document-taxonomy/project-topics/deployment/",
    "docs/project/modules/": "docs/history/superseded-document-taxonomy/project-modules/",
}


def canonical_owner_exists(owner: str) -> bool:
    path = ROOT / owner
    if path.exists():
        return True
    for old_prefix, new_prefix in CANONICAL_OWNER_ALIASES.items():
        if owner.startswith(old_prefix):
            return (ROOT / (new_prefix + owner[len(old_prefix):])).exists()
    return False


def rows(path: Path) -> list[list[str]]:
    result: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = TABLE_LINE.match(line)
        if not match:
            continue
        result.append([match.group(1), *[value.strip() for value in match.group(2).split("|")]])
    return result


def classify_closure_class(
    architecture_conflict: bool,
    implementation_gap: bool,
    measurement_gap: bool,
    external_gap: bool,
) -> tuple[str, list[str]]:
    """Apply the V3.1.3 ordered gate and retain secondary gaps."""

    if architecture_conflict:
        primary = "A"
    elif implementation_gap:
        primary = "I"
    elif measurement_gap:
        primary = "E"
    elif external_gap:
        primary = "X"
    else:
        primary = "I"
    secondary = [
        gap for gap, present in (("I", implementation_gap), ("E", measurement_gap), ("X", external_gap))
        if present and gap != primary
    ]
    return primary, secondary


def _load_normalizer():
    path = ROOT / "tools/scripts/verify_document_normalization_v311.py"
    spec = importlib.util.spec_from_file_location("verify_document_normalization_v311", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load normalization verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _delta_for_question(qid: str) -> str:
    number = int(qid[1:])
    for index, (_lens, (start, end)) in enumerate(LENSES.items(), start=1):
        if start <= number <= end:
            return f"D{index:03d}"
    raise ValueError(qid)


def verify() -> list[str]:
    errors: list[str] = []
    required = [
        "README.md", "manifest.yaml", "baseline-audit.md", "canonical-snapshot.md",
        "11-plus-1-coverage-map.md", "questions.md", "blue-answers.md", "red-scores.md",
        "blue-decisions.md", "architecture-deltas.md", "canonical-sync-record.md",
        "closure-class-audit.md", "human-writing-audit.md", "scorecard.md", "review-package.md",
        "round-report.md", "gap-register.md", "adr-escalations.md",
    ]
    for name in required:
        if not (SESSION / name).exists():
            errors.append(f"missing Round-005 file: {name}")
    if errors:
        return errors

    manifest = yaml.safe_load((SESSION / "manifest.yaml").read_text(encoding="utf-8"))
    expected = {
        "protocol_version": "ZUNO-RED-BLUE-WORKFLOW-V3.1.3",
        "session_id": "RB-WORKFLOW-V3-ROUND-005",
        "round_id": "RB-WORKFLOW-V3-ROUND-005",
        "question_budget": 100,
        "actual_question_count": 100,
        "answer_count": 100,
        "score_count": 100,
        "decision_count": 100,
        "novel_question_count": 80,
        "regression_question_count": 20,
        "human_writing_review": "WARNING",
        "architecture_integrity": "PASS",
        "part_a_quality_gate": "PASS",
        "part_b_quality_gate": "PASS",
        "closure_class_audit": "PASS",
        "canonical_sync_status": "COMPLETE",
        "round_status": "COMPLETE",
        "new_a_p0": 0,
        "new_e_p0": 0,
        "new_x_p0": 0,
        "round_006_status": "READY_NOT_STARTED",
        "facts_changed": "NONE",
        "runtime_changed": "NONE",
        "schema_or_migration_changed": "NONE",
        "dependencies_changed": "NONE",
        "production_infra_changed": "NONE",
        "adr_escalation_count": 0,
        "user_gate_escalation_count": 0,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"manifest {key} must be {value!r}")
    if manifest.get("round_004_immutable") is not True:
        errors.append("Round-004 immutable marker is required")

    question_rows = rows(SESSION / "questions.md")
    answer_rows = rows(SESSION / "blue-answers.md")
    score_rows = rows(SESSION / "red-scores.md")
    decision_rows = rows(SESSION / "blue-decisions.md")
    for label, table in (("questions", question_rows), ("answers", answer_rows), ("scores", score_rows), ("decisions", decision_rows)):
        if [row[0] for row in table] != IDS:
            errors.append(f"{label} must contain exactly Q001..Q100 in order")

    question_by_id = {row[0]: row for row in question_rows}
    answer_by_id = {row[0]: row for row in answer_rows}
    score_by_id = {row[0]: row for row in score_rows}
    decision_by_id = {row[0]: row for row in decision_rows}
    if len(question_rows) == 100:
        lens_counts = {lens: 0 for lens in LENSES}
        type_counts = {"NOVEL": 0, "REGRESSION": 0}
        for row in question_rows:
            if len(row) != 9:
                errors.append(f"{row[0]} question row has wrong field count")
                continue
            _qid, qtype, lens, owner, scenario, question, intent, evidence, kill = row
            if qtype not in type_counts:
                errors.append(f"{row[0]} has invalid question type")
            else:
                type_counts[qtype] += 1
            if lens not in LENSES:
                errors.append(f"{row[0]} has unknown lens")
            else:
                lens_counts[lens] += 1
            if not (owner.startswith("docs/project/") and canonical_owner_exists(owner)):
                errors.append(f"{row[0]} has invalid canonical owner: {owner}")
            if any(not value for value in (scenario, question, intent, evidence, kill)):
                errors.append(f"{row[0]} must include scenario, question, intent, evidence and kill condition")
        expected_counts = {lens: end - start + 1 for lens, (start, end) in LENSES.items()}
        if lens_counts != expected_counts:
            errors.append(f"lens counts mismatch: {lens_counts}")
        if type_counts != {"NOVEL": 80, "REGRESSION": 20}:
            errors.append(f"novelty counts mismatch: {type_counts}")

    answer_impacts: dict[str, str] = {}
    if len(answer_rows) == 100:
        for row in answer_rows:
            if len(row) != 9:
                errors.append(f"{row[0]} answer row has wrong field count")
                continue
            answer_impacts[row[0]] = row[8]
            if any(not value for value in row[1:]):
                errors.append(f"{row[0]} has an empty answer field")
            if not row[1].startswith(("不能", "可以", "Contract", "Target")):
                errors.append(f"{row[0]} answer must begin with a direct answer")
            if row[8] not in IMPACTS:
                errors.append(f"{row[0]} has invalid answer impact")

    severity_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    class_counts = {key: 0 for key in CLASSES}
    total = 0
    if len(score_rows) == 100:
        for row in score_rows:
            if len(row) != 9:
                errors.append(f"{row[0]} score row has wrong field count")
                continue
            try:
                score = int(row[1])
            except ValueError:
                score = -1
            severity, primary, rationale, quality, impact, _risk, delta = row[2:]
            if score < 0 or score > 5:
                errors.append(f"{row[0]} score must be 0..5")
            total += max(score, 0)
            if severity not in severity_counts:
                errors.append(f"{row[0]} has invalid severity")
            else:
                severity_counts[severity] += 1
            if primary not in CLASSES:
                errors.append(f"{row[0]} has invalid primary closure class")
            else:
                class_counts[primary] += 1
            if not rationale or not quality or impact not in IMPACTS:
                errors.append(f"{row[0]} must include rationale, explanation quality and impact")
            if quality not in {"CLEAR", "DENSE", "AMBIGUOUS", "TEMPLATE_LIKE"}:
                errors.append(f"{row[0]} has invalid explanation quality")
            if impact != answer_impacts.get(row[0]):
                errors.append(f"{row[0]} score impact differs from answer")
            if delta != _delta_for_question(row[0]):
                errors.append(f"{row[0]} has incorrect Delta Ref")
        if total != manifest.get("raw_score"):
            errors.append(f"raw score differs from manifest: {total}")
        if severity_counts != {"P0": 0, "P1": 15, "P2": 85, "P3": 0}:
            errors.append(f"severity distribution mismatch: {severity_counts}")
        if class_counts != {"A": 10, "I": 45, "E": 30, "X": 15}:
            errors.append(f"closure class distribution mismatch: {class_counts}")

    if len(decision_rows) == 100:
        for row in decision_rows:
            if len(row) != 14:
                errors.append(f"{row[0]} decision row has wrong field count")
                continue
            primary, secondary, rationale, decision, _owner, _state, failure, idem, impact, evidence, delta, sync, part_ab = row[1:]
            if primary not in CLASSES:
                errors.append(f"{row[0]} decision has invalid primary closure class")
            secondary_values = secondary.split(",")
            if not secondary_values or any(value not in SECONDARY for value in secondary_values):
                errors.append(f"{row[0]} decision has invalid secondary gap")
            if not rationale:
                errors.append(f"{row[0]} decision lacks closure class rationale")
            if decision not in DECISIONS:
                errors.append(f"{row[0]} has invalid decision")
            if not failure or not idem or not evidence:
                errors.append(f"{row[0]} decision lacks recovery/idempotency/evidence")
            if impact != answer_impacts.get(row[0]):
                errors.append(f"{row[0]} decision impact differs from answer")
            if delta != _delta_for_question(row[0]) or sync not in SYNC_MODES:
                errors.append(f"{row[0]} has invalid delta or sync mode")
            if primary != score_by_id.get(row[0], [None, None, None, None])[3]:
                errors.append(f"{row[0]} primary closure class differs between score and decision")
            if "/" not in part_ab:
                errors.append(f"{row[0]} must record Part A / Part B impact")

    delta_text = (SESSION / "architecture-deltas.md").read_text(encoding="utf-8")
    if re.findall(r"^## (D\d{3})\b", delta_text, re.MULTILINE) != [f"D{i:03d}" for i in range(1, 13)]:
        errors.append("architecture-deltas.md must contain D001..D012 in order")
    sync_text = (SESSION / "canonical-sync-record.md").read_text(encoding="utf-8")
    if len(re.findall(r"^\| D\d{3}\s*\|", sync_text, re.MULTILINE)) != 12:
        errors.append("canonical-sync-record.md must map all 12 Deltas")
    if "APPEND" in sync_text.upper() and "APPEND forbidden" not in sync_text:
        errors.append("canonical sync must not use APPEND")
    if "Status: COMPLETE" not in sync_text:
        errors.append("canonical sync must be COMPLETE")
    for did in [f"D{i:03d}" for i in range(1, 13)]:
        if did not in sync_text or "APPLIED" not in sync_text[sync_text.index(did):]:
            errors.append(f"{did} is not traceably applied")

    audit_text = (SESSION / "closure-class-audit.md").read_text(encoding="utf-8")
    for label in ("A", "I", "E", "X", "Borderline classifications", "Reclassified questions", "Potential default-bias findings"):
        if label not in audit_text:
            errors.append(f"closure-class-audit.md missing {label}")
    manual_ids = re.findall(r"^\| (Q\d{3}) \|", audit_text, re.MULTILINE)
    if len(set(manual_ids)) < 20:
        errors.append("closure-class-audit.md must contain a 20-question manual audit")

    writing_text = (SESSION / "human-writing-audit.md").read_text(encoding="utf-8")
    for marker in ("Human review result", "WARNING", "Part A", "Part B", "读到最后一段"):
        if marker not in writing_text:
            errors.append(f"human-writing-audit.md missing {marker}")
    review_text = (SESSION / "review-package.md").read_text(encoding="utf-8")
    for marker in ("BASE_SHA", "FINAL_SHA", "Closure Class Distribution", "Distribution Audit Result", "New A-P0", "New E-P0", "New X-P0", "Round-006"):
        if marker not in review_text:
            errors.append(f"review-package.md missing {marker}")
    if "Production Ready" in review_text and "不得" not in review_text:
        errors.append("review package must not promote Production Ready")

    try:
        errors.extend(_load_normalizer().verify())
    except Exception as exc:  # pragma: no cover
        errors.append(f"normalization verifier could not run: {exc}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    manifest = yaml.safe_load((SESSION / "manifest.yaml").read_text(encoding="utf-8"))
    print(f"red-blue V3.1.3 Round-005 verification passed: {manifest['raw_score']}/500; Closure Class Audit PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
