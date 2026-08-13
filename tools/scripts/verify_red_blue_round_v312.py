"""Verify the V3.1.2 Human Writing / Round-004 session contract."""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SESSION = ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004"
IDS = [f"Q{i:03d}" for i in range(1, 101)]
LENSES = {
    "00 Overall Architecture": (1, 12),
    "01 Product Surface": (13, 18),
    "02 Input / Document Ingestion": (19, 25),
    "03 Knowledge / Agentic GraphRAG": (26, 36),
    "04 Model Gateway": (37, 42),
    "05 Memory & Context": (43, 50),
    "06 Agent Core / Planning & Control": (51, 64),
    "07 Capability / Skill": (65, 70),
    "08 Tool Runtime": (71, 80),
    "09 Security": (81, 88),
    "10 Observability & Eval": (89, 94),
    "11 Infrastructure": (95, 100),
}
TABLE_LINE = re.compile(r"^\|\s*(Q\d{3})\s*\|(.+)\|\s*$")

CANONICAL_OWNER_ALIASES = {
    "docs/project/architecture/": "docs/architecture/",
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
        values = [value.strip() for value in match.group(2).split("|")]
        result.append([match.group(1), *values])
    return result


def load_normalizer():
    path = ROOT / "tools/scripts/verify_document_normalization_v311.py"
    spec = importlib.util.spec_from_file_location("verify_document_normalization_v311", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load normalization verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify() -> list[str]:
    errors: list[str] = []
    required = (
        "README.md", "manifest.yaml", "baseline-audit.md", "canonical-snapshot.md",
        "11-plus-1-coverage-map.md", "questions.md", "blue-answers.md", "red-scores.md",
        "blue-decisions.md", "architecture-deltas.md", "canonical-sync-record.md",
        "human-writing-audit.md", "scorecard.md", "review-package.md", "round-report.md",
        "gap-register.md", "adr-escalations.md",
    )
    for name in required:
        if not (SESSION / name).exists():
            errors.append(f"missing Round-004 file: {name}")
    if errors:
        return errors

    manifest = yaml.safe_load((SESSION / "manifest.yaml").read_text(encoding="utf-8"))
    expected = {
        "protocol_version": "ZUNO-RED-BLUE-WORKFLOW-V3.1.2",
        "session_id": "RB-WORKFLOW-V3-ROUND-004",
        "round_id": "RB-WORKFLOW-V3-ROUND-004",
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
        "canonical_sync_status": "APPLIED",
        "round_status": "COMPLETE",
        "new_a_p0": 0,
        "round_005_status": "READY_NOT_STARTED",
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

    question_rows = rows(SESSION / "questions.md")
    answer_rows = rows(SESSION / "blue-answers.md")
    score_rows = rows(SESSION / "red-scores.md")
    decision_rows = rows(SESSION / "blue-decisions.md")
    for label, table in (("questions", question_rows), ("answers", answer_rows), ("scores", score_rows), ("decisions", decision_rows)):
        if [row[0] for row in table] != IDS:
            errors.append(f"{label} must contain exactly Q001..Q100 in order")

    if len(question_rows) == 100:
        lens_counts = {lens: 0 for lens in LENSES}
        type_counts = {"NOVEL": 0, "REGRESSION": 0}
        for qid, row in enumerate(question_rows, start=1):
            if len(row) != 9:
                errors.append(f"{IDS[qid - 1]} question row has wrong field count")
                continue
            question_type, lens, owner = row[1], row[2], row[3]
            if question_type not in type_counts:
                errors.append(f"{row[0]} has invalid question type")
            else:
                type_counts[question_type] += 1
            if lens not in LENSES:
                errors.append(f"{row[0]} has unknown lens")
            else:
                lens_counts[lens] += 1
            if not (owner.startswith("docs/project/") and canonical_owner_exists(owner)):
                errors.append(f"{row[0]} has invalid canonical owner: {owner}")
            if not row[4] or not row[5] or not row[6] or not row[7] or not row[8]:
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
            impact = row[8]
            answer_impacts[row[0]] = impact
            if impact not in {"PART_A", "PART_B", "BOTH", "NONE"}:
                errors.append(f"{row[0]} has invalid document impact")
            if any(not value for value in row[1:]):
                errors.append(f"{row[0]} has an empty answer field")

    total = 0
    severity_counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    if len(score_rows) == 100:
        for row in score_rows:
            if len(row) != 10:
                errors.append(f"{row[0]} score row has wrong field count")
                continue
            total += int(row[2]) if row[2].isdigit() else 0
            severity_counts[row[3]] = severity_counts.get(row[3], 0) + 1
            if row[6] != answer_impacts.get(row[0]):
                errors.append(f"{row[0]} score impact differs from answer")
            if row[9] != f"D{next(index for index, (start, end) in enumerate(LENSES.values(), start=1) if start <= int(row[0][1:]) <= end):03d}":
                errors.append(f"{row[0]} has incorrect Delta Ref")
        if total != 385:
            errors.append(f"raw score must be 385, got {total}")
        if severity_counts != {"P0": 0, "P1": 15, "P2": 85, "P3": 0}:
            errors.append(f"severity distribution mismatch: {severity_counts}")

    if len(decision_rows) == 100:
        for row in decision_rows:
            if len(row) != 13:
                errors.append(f"{row[0]} decision row has wrong field count")
                continue
            if row[8] != answer_impacts.get(row[0]):
                errors.append(f"{row[0]} decision impact differs from answer")
            if row[10] not in {f"D{i:03d}" for i in range(1, 13)}:
                errors.append(f"{row[0]} has invalid Delta Ref")
            if row[11] not in {"SECTION_REWRITE", "FULL_PART_REWRITE", "NO_CHANGE"}:
                errors.append(f"{row[0]} has invalid sync mode")
            if row[4] not in {"KEEP", "CLARIFY", "REFINE", "SPLIT", "MERGE", "REPLACE", "DELETE", "DEFER"}:
                errors.append(f"{row[0]} has invalid Blue Decision")

    delta_text = (SESSION / "architecture-deltas.md").read_text(encoding="utf-8")
    if [f"D{i:03d}" for i in range(1, 13)] != re.findall(r"^## (D\d{3})\b", delta_text, re.MULTILINE):
        errors.append("architecture-deltas.md must contain D001..D012 in order")
    sync_text = (SESSION / "canonical-sync-record.md").read_text(encoding="utf-8")
    if len(re.findall(r"^\| D\d{3}\s*\|", sync_text, re.MULTILINE)) != 12 or "Status: APPLIED" not in sync_text or "APPEND forbidden" not in sync_text:
        errors.append("canonical-sync-record.md must map all 12 applied/recorded Deltas")

    human_text = (SESSION / "human-writing-audit.md").read_text(encoding="utf-8")
    for marker in ("Deterministic signal boundary", "Human review result", "Overall: `WARNING`", "Rewrite"):
        if marker not in human_text:
            errors.append(f"human-writing-audit.md missing {marker}")
    review_text = (SESSION / "review-package.md").read_text(encoding="utf-8")
    for marker in ("Most natural documents", "Remaining human-writing concerns", "Canonical sections rewritten", "New A-P0: 0", "Round-005"):
        if marker not in review_text:
            errors.append(f"review-package.md missing {marker}")

    try:
        errors.extend(load_normalizer().verify())
    except Exception as exc:  # pragma: no cover - verifier bootstrap failure
        errors.append(f"normalization verifier could not run: {exc}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("red-blue V3.1.2 Round-004 verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
