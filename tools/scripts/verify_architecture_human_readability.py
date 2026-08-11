from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [
    ROOT / "docs/architecture/architecture.md",
    *sorted((ROOT / "docs/modules").glob("[0-9][0-9]-*.md")),
]
PART_A = "# Part A — 面向人的设计说明"
PART_B = "# Part B — 规范性架构与实施约束"


def _has_any(content: str, markers: tuple[str, ...]) -> bool:
    return any(marker in content for marker in markers)


def verify() -> list[str]:
    errors: list[str] = []
    if len(CANONICAL) != 12:
        errors.append(f"canonical Markdown set must contain 12 files, got {len(CANONICAL)}")

    for path in CANONICAL:
        if not path.exists():
            errors.append(f"missing canonical Markdown: {path.relative_to(ROOT)}")
            continue
        content = path.read_text(encoding="utf-8")
        label = str(path.relative_to(ROOT))
        a_pos = content.find(PART_A)
        b_pos = content.find(PART_B)
        if a_pos < 0:
            errors.append(f"{label} missing human-readable Part A marker")
            continue
        if b_pos < 0:
            errors.append(f"{label} missing normative Part B marker")
            continue
        if a_pos >= b_pos:
            errors.append(f"{label} Part A must precede Part B")

        part_a = content[a_pos:b_pos]
        part_b = content[b_pos:]
        for concern, markers in {
            "problem": ("问题", "Problem"),
            "case": ("案例", "Case", "合同审查"),
            "flow": ("流程", "运行", "Flow"),
            "failure-or-exception": ("失败", "异常", "Failure"),
            "trade-off": ("取舍", "替代", "Trade-off", "为什么"),
        }.items():
            if not _has_any(part_a, markers):
                errors.append(f"{label} Part A lacks {concern} explanation")

        for concern, markers in {
            "invariant": ("不变量", "Invariant"),
            "ownership": ("Ownership", "事实负责方", "所有权"),
            "contract": ("Contract", "契约"),
            "state-or-failure": ("状态", "State", "Failure"),
            "recovery-or-idempotency": ("Recovery", "恢复", "幂等", "Idempotency"),
            "security": ("Security", "安全"),
            "test-or-evidence": ("Test", "测试", "Evidence", "证据"),
        }.items():
            if not _has_any(part_b, markers):
                errors.append(f"{label} Part B lacks {concern} specification")

        for metadata in ("human_readable_part:", "normative_specification_part:"):
            if metadata not in content:
                errors.append(f"{label} missing metadata: {metadata}")

    for forbidden in (ROOT / "docs").glob("**/*-human.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    for forbidden in (ROOT / "docs").glob("**/*-spec.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")

    views = ROOT / "docs/architecture/architecture-views.md"
    html = ROOT / "docs/architecture/architecture.html"
    if not views.exists() or not html.exists():
        errors.append("architecture diagram presentation pair must remain present")
    elif 'fetch("./architecture-views.md")' not in html.read_text(encoding="utf-8"):
        errors.append("architecture.html must continue to consume architecture-views.md")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture human/normative readability verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
