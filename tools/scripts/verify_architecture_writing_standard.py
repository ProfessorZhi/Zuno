from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
STANDARD = ROOT / "docs/governance/human-first-documentation-standard.md"
MODULES = ROOT / "docs/modules"

MODULE_FILES = (
    "01-application-integration.md",
    "02-legal-domain-work-product.md",
    "03-knowledge-evidence.md",
    "04-agent-runtime-control.md",
    "05-capability-skill.md",
    "06-tool-runtime-effects.md",
    "07-model-gateway.md",
    "08-security-governance.md",
    "09-observability-evaluation.md",
)


def verify() -> list[str]:
    errors: list[str] = []
    if not STANDARD.exists():
        errors.append("missing human-first documentation standard")
    else:
        standard = STANDARD.read_text(encoding="utf-8")
        for marker in (
            "ONE DESIGN",
            "THREE COORDINATED VIEWS",
            "Part A — Human Narrative（人类技术叙事）",
            "Part B — Engineering / Agent Reference（工程 / Agent 参考）",
            "Part C — Cross-Module Consistency（跨模块一致性）",
            "A → B → C Semantic Mapping",
            "模块文档模板",
            "B5 Cross-boundary Contract Format",
            "Human Review Checklist",
            "Part B Review Checklist",
            "Part C Review Checklist",
            "中文优先规则",
            "Cancellation 不是全局回滚",
            "Late result 必须重新验收",
            "Idempotency namespace 分离",
            "恢复先找 Authoritative Owner Fact",
            "Correlation 不成为安全或业务权威",
        ):
            if marker not in standard:
                errors.append(f"human-first standard missing model marker: {marker}")

    for path in (ARCH, VIEWS, HTML):
        if not path.exists():
            errors.append(f"missing canonical architecture document: {path.relative_to(ROOT)}")
    if not ARCH.exists():
        return errors

    design = ARCH.read_text(encoding="utf-8")
    for marker in (
        "模块化 Python 后端",
        "独立网络服务",
        "Current",
        "Target",
        "History",
        "为什么必须独立服务",
        "Reconciliation",
    ):
        if marker not in design:
            errors.append(f"architecture.md missing writing marker: {marker}")

    for filename in MODULE_FILES:
        path = MODULES / filename
        if not path.exists():
            errors.append(f"missing canonical module document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in (
            "## Part A — Human Narrative",
            "## Part B — Engineering / Agent Reference",
            "## Part C — Cross-Module Consistency（跨模块一致性）",
            "### C1 Completion Proof / Non-proof（完成证明与非证明）",
            "### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）",
            "### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）",
            "### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）",
        ):
            if marker not in text:
                errors.append(f"{filename} missing writing-model marker: {marker}")

    if VIEWS.exists() and "```mermaid" not in VIEWS.read_text(encoding="utf-8"):
        errors.append("architecture-views.md must remain a Mermaid source")
    if HTML.exists() and 'fetch("./architecture-views.md")' not in HTML.read_text(encoding="utf-8"):
        errors.append("architecture.html must consume architecture-views.md")
    for mirror in (ROOT / ".agent/architecture", ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"forbidden architecture mirror exists: {mirror.relative_to(ROOT)}")
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
