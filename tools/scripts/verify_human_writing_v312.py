"""Deterministic warnings for the V3.1.2 Canonical Part A human-writing gate.

This verifier reports mechanical signals only. It must never claim that a document
has passed human review; the Review Package records that judgement separately.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [
    ROOT / "docs/project/architecture/architecture.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/product/product-architecture.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/domain/legal-domain-model.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/domain/domain-state-lifecycle.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/agents/multi-agent-runtime.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/knowledge/knowledge-evidence-architecture.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/services/service-architecture.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/data/data-ownership-and-recovery.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/security/security-architecture.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/eval/legal-eval-and-benchmark.md",
    ROOT / "docs/history/superseded-document-taxonomy/project-topics/deployment/microservice-deployment.md",
]
PART_A = "## Part A — Architecture Narrative"
PART_B = "## Part B — Detailed Architecture Specification"
PROCESS = re.compile(r"(?im)\b(?:Round-\d+|D\d{3}|Q\d{3})\b")


def _contains_process_trace(text: str) -> bool:
    """Allow a Canonical boundary to say a round is not being started."""
    for line in text.splitlines():
        if "不启动 Red/Blue" in line or "不启动 Round-" in line:
            continue
        if PROCESS.search(line):
            return True
    return False
TEMPLATE_PHRASES = (
    "不是……而是",
    "主要失败是",
    "这套设计的价值是",
    "因此当前 Target",
    "需要注意的是",
    "值得强调的是",
    "如果……则删除",
)
SCENARIO_MARKERS = ("Target Scenario", "场景", "案件", "材料", "任务", "时序")
FAILURE_MARKERS = ("失败", "timeout", "stale", "恢复", "对账", "未知结果")
TRADEOFF_MARKERS = ("取舍", "代价", "成本", "复杂度", "替代", "删除", "缩减")


def _parts(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    if text.count(PART_A) != 1 or text.count(PART_B) != 1:
        return "", ""
    start = text.index(PART_A) + len(PART_A)
    end = text.index(PART_B)
    return text[start:end], text[end:]


def metrics(path: Path) -> dict[str, int | str]:
    part_a, _ = _parts(path)
    lines = [line for line in part_a.splitlines() if line.strip()]
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", part_a)
    headings = [line for line in lines if line.startswith("### ")]
    bullets = [line for line in lines if line.lstrip().startswith(("- ", "* "))]
    tables = [line for line in lines if line.lstrip().startswith("|")]
    return {
        "document": str(path.relative_to(ROOT)),
        "part_a_lines": len(lines),
        "heading_count": len(headings),
        "bullet_count": len(bullets),
        "table_count": len(tables),
        "english_token_count": len(words),
        "template_phrase_count": sum(part_a.count(phrase) for phrase in TEMPLATE_PHRASES),
        "scenario": int(any(marker in part_a for marker in SCENARIO_MARKERS)),
        "failure_story": int(any(marker in part_a for marker in FAILURE_MARKERS)),
        "tradeoff": int(any(marker in part_a for marker in TRADEOFF_MARKERS)),
        "boundary": int(any(marker in part_a for marker in ("Current", "Target", "Gap", "不负责", "不拥有"))),
    }


def verify() -> tuple[list[str], list[str], list[dict[str, int | str]]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, int | str]] = []
    for path in CANONICAL:
        if not path.exists():
            errors.append(f"missing canonical document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        part_a, part_b = _parts(path)
        label = str(path.relative_to(ROOT))
        if not part_a or not part_b:
            errors.append(f"{label}: missing Part A or Part B")
            continue
        if _contains_process_trace(text):
            errors.append(f"{label}: process trace leaked into Canonical document")
        row = metrics(path)
        rows.append(row)
        line_count = int(row["part_a_lines"])
        if int(row["heading_count"]) > max(7, line_count // 3):
            warnings.append(f"{label}: heading density is high")
        if int(row["bullet_count"]) > max(8, line_count * 0.45):
            warnings.append(f"{label}: Part A is list-heavy")
        if int(row["table_count"]) > max(5, line_count * 0.45):
            warnings.append(f"{label}: Part A is table-heavy")
        if int(row["english_token_count"]) > max(180, line_count * 12):
            warnings.append(f"{label}: English technical-token density is high")
        if int(row["template_phrase_count"]) >= 3:
            warnings.append(f"{label}: repeated template phrase signal")
        for key, description in (("scenario", "scenario"), ("failure_story", "failure story"), ("tradeoff", "tradeoff"), ("boundary", "Current/Target boundary")):
            if int(row[key]) == 0:
                warnings.append(f"{label}: weak {description} signal")
    return errors, warnings, rows


def main() -> int:
    errors, warnings, rows = verify()
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"human writing deterministic audit completed: {len(rows)} docs; HUMAN_WRITING_REVIEW requires manual judgement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
