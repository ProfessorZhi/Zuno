from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [
    ROOT / "docs/project/architecture/architecture.md",
]

PART_A_HEADING = "## Part A — Architecture Narrative"
PART_B_HEADING = "## Part B — Detailed Architecture Specification"
ROUND_CHANGELOG_RE = re.compile(r"(?im)^#{1,6}.*Round-\d+|\bD\d{3}\b|\bQ\d{3}\b")


def verify() -> list[str]:
    errors: list[str] = []
    for path in CANONICAL:
        if not path.exists():
            errors.append(f"missing canonical Markdown: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        label = str(path.relative_to(ROOT))
        metadata_markers = ("status:", "Current", "Target", "Gap")
        if path != ROOT / "docs/project/architecture/architecture.md":
            metadata_markers += ("canonical_question:", "owner:")
        for marker in metadata_markers:
            if marker not in text:
                errors.append(f"{label} missing human-readable metadata: {marker}")
        if PART_A_HEADING not in text or PART_B_HEADING not in text:
            errors.append(f"{label} must contain both Part A narrative and Part B specification")
            continue
        part_a_start = text.index(PART_A_HEADING) + len(PART_A_HEADING)
        part_b_start = text.index(PART_B_HEADING)
        part_a = text[part_a_start:part_b_start]
        part_b = text[part_b_start:]
        if ROUND_CHANGELOG_RE.search(text):
            errors.append(f"{label} contains Round-specific changelog or trace identifiers")
        if len([line for line in part_a.splitlines() if line.strip()]) < 6:
            errors.append(f"{label} Part A is too short to be an architecture narrative")
        narrative_lines = [line for line in part_a.splitlines() if line.strip()]
        bullet_lines = [line for line in narrative_lines if line.lstrip().startswith(("- ", "* "))]
        table_lines = [line for line in narrative_lines if line.lstrip().startswith("|")]
        if len(bullet_lines) > max(8, len(narrative_lines) * 0.55):
            errors.append(f"{label} Part A is dominated by bullet lists")
        if len(table_lines) > max(5, len(narrative_lines) * 0.55):
            errors.append(f"{label} Part A is dominated by tables")
        part_a_concerns = {
            "problem/why": ("问题", "Why", "Problem", "动机", "解决", "价值", "目标", "工作", "评测"),
            "concrete scenario": ("例如", "场景", "Target Scenario", "典型", "案件", "材料", "任务"),
            "responsibilities": ("负责", "职责", "Owner", "Ownership", "共享", "Domain Service", "Security", "需要"),
            "non-responsibilities": ("不负责", "不拥有", "不能", "不应", "不复制", "不自动", "不可"),
            "flow/boundary": ("→", "输入", "输出", "上游", "下游", "协作", "边界", "提交", "比较", "DocumentVersion", "服务", "恢复"),
            "happy path": ("流程", "路径", "典型", "例如", "→", "先", "再", "提交", "比较", "然后"),
            "failure story": ("失败", "Failure", "timeout", "stale", "恢复", "异常"),
            "tradeoff": ("取舍", "代价", "成本", "收益", "复杂度", "替代", "保留", "缩减", "不增加", "分开"),
            "reversal": ("替代", "降级", "删除", "缩减", "如果", "若", "不保留", "应", "失效"),
        }
        for concern, markers in part_a_concerns.items():
            if not any(marker in part_a for marker in markers):
                errors.append(f"{label} Part A lacks {concern} explanation")
        for concern, markers in {
            "contract": ("Contract", "契约", "Schema", "Input", "Output", "Boundary", "Gate", "Storage", "Action", "策略"),
            "state": ("State", "状态", "Version", "版本", "checkpoint", "兼容"),
            "failure": ("Failure", "失败", "异常", "Gap"),
            "retry/recovery": ("Retry", "Recovery", "重试", "恢复", "reconciliation", "对账", "队列", "rollback"),
            "idempotency": ("Idempot", "幂等", "去重", "重复", "同一"),
            "security": ("Security", "权限", "授权", "Secret", "Policy", "隔离"),
            "observability/evidence": ("Observability", "Audit", "Trace", "Evidence", "验证", "SLO", "health"),
            "ownership": ("Owner", "owner", "Ownership", "所有权", "保存", "负责", "Domain", "service"),
        }.items():
            if not any(marker in part_b for marker in markers):
                errors.append(f"{label} Part B lacks {concern} contract detail")
        for concern, markers in {
            "problem": ("为什么", "Why", "问题", "Boundary", "Definition", "canonical_question"),
            "case-or-flow": ("流程", "Case", "Flow", "→", "Worker", "Variant", "Scope", "Service", "Runtime"),
            "ownership": ("Owner", "owner:", "Ownership", "所有权", "Platform Domain", "Agent Runtime"),
            "failure": ("Failure", "失败", "异常", "Recovery", "recovery", "stale", "Gap"),
            "verification": ("Evidence", "证据", "验证", "Benchmark", "Metrics", "Current"),
        }.items():
            if not any(marker in text for marker in markers):
                errors.append(f"{label} lacks {concern} explanation")
    views = ROOT / "docs/project/architecture/architecture-views.md"
    html = ROOT / "docs/project/architecture/architecture.html"
    if not views.exists() or not html.exists():
        errors.append("architecture diagram presentation pair must remain present")
    elif 'fetch("./architecture-views.md")' not in html.read_text(encoding="utf-8"):
        errors.append("architecture.html must continue to consume architecture-views.md")
    for forbidden in ROOT.glob("docs/**/*-human.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    for forbidden in ROOT.glob("docs/**/*-spec.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture human readability verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
