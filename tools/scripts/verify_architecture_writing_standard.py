from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs/governance/architecture-document-writing-standard.md"
ARCH = ROOT / "docs/project/architecture/architecture.md"
VIEWS = ROOT / "docs/project/architecture/architecture-views.md"
HTML = ROOT / "docs/project/architecture/architecture.html"
MODULES = ROOT / "docs/project/modules"

MODULE_DOCS = [
    "01-product-surface.md",
    "02-input-document-ingestion.md",
    "03-knowledge-agentic-graphrag.md",
    "04-model-gateway.md",
    "05-memory-context.md",
    "06-agent-core-planning-control.md",
    "07-capability-skill.md",
    "08-tool-runtime.md",
    "09-security.md",
    "10-observability-eval.md",
    "11-infrastructure.md",
]


def verify() -> list[str]:
    errors: list[str] = []
    if not STANDARD.exists():
        return ["missing architecture writing standard"]

    standard = STANDARD.read_text(encoding="utf-8")
    for marker in [
        "问题\n→ 场景\n→ 边界与 Owner",
        "## 2. 总架构的阅读协议",
        "## 3. 模块文档的七 Part 协议",
        "## 4. 写作规则",
        "## 5. 图源、入口和引用规则",
        "## 6. 评审与验证规则",
        "Current",
        "Target",
        "Interview QA",
    ]:
        if marker not in standard:
            errors.append(f"writing standard missing marker: {marker}")

    architecture = ARCH.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    for marker in [
        "writing_standard: `docs/governance/architecture-document-writing-standard.md`",
        "# Part I — 为什么需要 Zuno",
        "# Part II — 平台宏观架构",
        "# Part III — 一次企业 Agent 任务如何运行",
        "# Part IV — 分布式系统如何保持正确",
        "# Part V — 部署、扩容与生产演练",
        "# Part VI — 架构边界、演进与验证",
        "审查合同 A",
        "Logical Module 不等于 Deployable Service",
    ]:
        if marker not in architecture:
            errors.append(f"architecture writing structure missing: {marker}")

    views = VIEWS.read_text(encoding="utf-8")
    if "writing_standard: `docs/governance/architecture-document-writing-standard.md`" not in views:
        errors.append("architecture views do not route to writing standard")
    if "Canonical View Model" not in views:
        errors.append("architecture views do not declare the canonical view reading layer")

    if "architecture-document-writing-standard.md" not in html:
        errors.append("architecture HTML does not route to writing standard")

    for filename in MODULE_DOCS:
        path = MODULES / filename
        if not path.exists():
            errors.append(f"missing module document: {filename}")
            continue
        content = path.read_text(encoding="utf-8")
        if "writing_standard: `docs/governance/architecture-document-writing-standard.md`" not in content:
            errors.append(f"module does not declare writing standard: {filename}")
        if "reading_order: Problem → Case → Ownership → Runtime → State/Failure → Contract/Implementation → Verification" not in content:
            errors.append(f"module does not declare stable reading order: {filename}")
        for semantic, alternatives in {
            "problem": ("为什么", "问题"),
            "ownership": ("Ownership", "所有权"),
            "runtime": ("流程", "Runtime"),
            "failure": ("Failure", "失败"),
            "security": ("Security", "安全"),
            "observability": ("Observability", "可观测"),
            "status": ("Current", "Target"),
        }.items():
            if not any(value in content for value in alternatives):
                errors.append(f"module {filename} lacks {semantic} writing concern")

    for forbidden in [ROOT / ".agent/architecture", ROOT / ".agent/modules"]:
        if forbidden.exists():
            errors.append(f"forbidden architecture mirror exists: {forbidden.relative_to(ROOT)}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture writing standard verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
