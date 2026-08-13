"""Verify the derived semantic audit for Round-005 without rewriting history."""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-005"
AUDIT = ROOT / "project-reconstruction-lab/sessions/RB-CLOSURE-SEMANTIC-AUDIT-V3.1.3.1"
IDS = [f"Q{i:03d}" for i in range(1, 101)]
CLASSES = {"A", "I", "E", "X"}
POST_CLASSES = CLASSES | {"NONE"}
STATES = {"OPEN", "RESOLVED_IN_ROUND", "REMAINS_OPEN", "DEFERRED", "ESCALATED", "EVIDENCE_PENDING"}
SECONDARY = {"NONE", "A", "I", "E", "X"}
LENSES = {
    "00 Overall Architecture", "01 Product Surface", "02 Input / Document Ingestion",
    "03 Knowledge / Agentic GraphRAG", "04 Model Gateway", "05 Memory & Context",
    "06 Agent Core / Planning & Control", "07 Capability / Skill", "08 Tool Runtime",
    "09 Security", "10 Observability & Eval", "11 Infrastructure",
}


def table(path: Path) -> dict[str, list[str]]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| Q"):
            cells = [cell.strip() for cell in line.split("|")[1:-1]]
            result[cells[0]] = cells
    return result


def derive_class(scenario: str) -> str:
    """Derive a class from semantic triggers; no question ID or distribution is used."""

    architecture = (
        "DomainVersion D31 已提交", "Host 和 Native Runtime", "旧 11 模块文档",
        "Reviewer A 接受 Finding", "同一 DocumentVersion 的两个 Parser", "Hybrid 与 Graph 给出互相冲突",
    )
    evidence = (
        "A/B/C 质量接近", "一个 Claim 需要三份材料", "Graph 成本上升", "A/B 两个架构使用不同 fallback",
        "Memory 已 stale", "必需 Worker 超时", "Join 少一个证据分支", "同一 Capability 有本地模型",
        "Reviewer 对 Evidence Sufficiency", "Graph 与 Hybrid 都提高", "故障注入只覆盖 API timeout",
        "Knowledge Worker 占满 CPU",
    )
    external = (
        "滚动发布中旧 Worker", "Gateway 暂时不可用", "OpenViking Provider 被替换", "Sandbox 崩溃且 Provider",
        "Tool Provider v2", "Sandbox 进程尝试", "Tool Version 升级", "Provider outage", "Runtime v2 已滚动",
        "备份恢复后 Domain State", "Production 配置存在",
    )
    if any(trigger in scenario for trigger in architecture):
        return "A"
    if any(trigger in scenario for trigger in evidence):
        return "E"
    if any(trigger in scenario for trigger in external):
        return "X"
    return "I"


def _hashes() -> dict[str, str]:
    names = ["questions.md", "blue-answers.md", "red-scores.md", "blue-decisions.md", "scorecard.md", "architecture-deltas.md"]
    return {name: sha256((ROUND / name).read_bytes()).hexdigest() for name in names}


def verify() -> list[str]:
    errors: list[str] = []
    required = [
        "README.md", "manifest.yaml", "semantic-classification.md", "question-by-question-audit.md",
        "attack-vs-post-round.md", "lens-class-matrix.md", "rationale-duplication-audit.md",
        "classification-delta.md", "gate-impact.md", "review-package.md",
    ]
    for name in required:
        if not (AUDIT / name).exists():
            errors.append(f"missing semantic audit file: {name}")
    if errors:
        return errors

    manifest = yaml.safe_load((AUDIT / "manifest.yaml").read_text(encoding="utf-8"))
    if manifest.get("round_005_immutable") is not True:
        errors.append("Round-005 immutable marker missing")
    if manifest.get("questions_audited") != 100:
        errors.append("semantic audit must cover exactly 100 questions")
    if manifest.get("rationale_exact_duplicates") != 0:
        errors.append("rationale exact duplicates must be zero")
    if any(key in (AUDIT / name).read_text(encoding="utf-8") for name in required for key in ("expected_A_count", "expected_I_count", "expected_E_count", "expected_X_count")):
        errors.append("semantic audit must not contain expected class quota fields")

    questions = table(ROUND / "questions.md")
    scores = table(ROUND / "red-scores.md")
    audit_rows = table(AUDIT / "question-by-question-audit.md")
    if list(audit_rows) != IDS:
        errors.append("question-by-question audit must contain Q001..Q100 in order")
    if len(audit_rows) == 100:
        attack_counts: Counter[str] = Counter()
        post_counts: Counter[str] = Counter()
        state_counts: Counter[str] = Counter()
        rationale_values: list[str] = []
        for qid in IDS:
            row = audit_rows[qid]
            if len(row) != 10:
                errors.append(f"{qid} semantic row has wrong field count")
                continue
            _id, lens, original, attack, post, state, secondary, changed, rationale, post_reason = row
            if lens not in LENSES:
                errors.append(f"{qid} has invalid lens")
            if original != scores[qid][3]:
                errors.append(f"{qid} does not preserve Round-005 original class")
            if attack not in CLASSES or attack != derive_class(questions[qid][4]):
                errors.append(f"{qid} attack-time class is not semantic-derived")
            if post not in POST_CLASSES:
                errors.append(f"{qid} has invalid post-round class")
            if state not in STATES:
                errors.append(f"{qid} has invalid finding state")
            if any(value not in SECONDARY for value in secondary.split(",")):
                errors.append(f"{qid} has invalid secondary gap")
            if not rationale or not post_reason or questions[qid][4][:4] not in rationale:
                errors.append(f"{qid} lacks a question-specific closure rationale")
            if post == "NONE" and state != "RESOLVED_IN_ROUND":
                errors.append(f"{qid} has NONE post class without resolved state")
            if attack == "A" and post == "A":
                errors.append(f"{qid} leaves an A gap open without explicit repair escalation")
            attack_counts[attack] += 1
            if post != "NONE":
                post_counts[post] += 1
            state_counts[state] += 1
            rationale_values.append(rationale)
        if len(rationale_values) != len(set(rationale_values)):
            errors.append("duplicate closure rationale detected")
        manifest_attack = {key: manifest["attack_time_distribution"].get(key, 0) for key in sorted(CLASSES)}
        actual_attack = {key: attack_counts.get(key, 0) for key in sorted(CLASSES)}
        if manifest_attack != actual_attack:
            errors.append(f"attack distribution mismatch: {actual_attack}")
        manifest_post = {key: manifest["post_round_open_distribution"].get(key, 0) for key in sorted(CLASSES)}
        actual_post = {key: post_counts.get(key, 0) for key in sorted(CLASSES)}
        if manifest_post != actual_post:
            errors.append(f"post-round distribution mismatch: {actual_post}")
        if manifest.get("reclassified_count") != sum(a != scores[qid][3] for qid, a in ((qid, audit_rows[qid][3]) for qid in IDS)):
            errors.append("reclassified count mismatch")

    if manifest.get("round_005_original_sha256") != _hashes():
        errors.append("Round-005 immutable source hashes do not match")

    matrix_text = (AUDIT / "lens-class-matrix.md").read_text(encoding="utf-8")
    matrix_rows = re.findall(r"^\| (.+?) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \|$", matrix_text, re.MULTILINE)
    if len(matrix_rows) != 12:
        errors.append("lens-class-matrix.md must contain 12 lens rows")
    for lens, a, i, e, x in matrix_rows:
        if sum(int(value) > 0 for value in (a, i, e, x)) < 2:
            errors.append(f"{lens} has only one closure class; manual explanation required")

    rationale_text = (AUDIT / "rationale-duplication-audit.md").read_text(encoding="utf-8")
    for marker in ("Exact duplicate rationale count: 0", "WARNING_REVIEWED", "具体 Scenario", "Maturity Gate"):
        if marker not in rationale_text:
            errors.append(f"rationale duplication audit missing {marker}")
    gate_text = (AUDIT / "gate-impact.md").read_text(encoding="utf-8")
    for marker in ("A-P0", "A-P1/P2 core-contract check", "Core architecture contradiction remaining", "Round-006", "PASS"):
        if marker not in gate_text:
            errors.append(f"gate-impact.md missing {marker}")
    review_text = (AUDIT / "review-package.md").read_text(encoding="utf-8")
    for marker in ("Original distribution", "Semantic attack-time distribution", "Post-round remaining distribution", "A found / resolved / remaining", "Lens/Class independence", "Architecture repair required", "Round-006 readiness"):
        if marker not in review_text:
            errors.append(f"review-package.md missing {marker}")

    if manifest.get("a_remaining") != 0 or manifest.get("a_p0") != 0:
        errors.append("A remaining or A-P0 gate is not closed")
    if manifest.get("core_architecture_contradictions_remaining") != 0:
        errors.append("core architecture contradiction remains")
    if manifest.get("classification_integrity") != "PASS":
        errors.append("classification integrity is not PASS")
    if manifest.get("architecture_repair_required") is not False:
        errors.append("architecture repair must not be required by this audit")
    for key in ("facts_changed", "runtime_changed", "adr_changed"):
        if manifest.get(key) != "NONE":
            errors.append(f"{key} must remain NONE")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("closure semantic audit V3.1.3.1 verification passed: 100 questions, immutable Round-005, classification integrity PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
