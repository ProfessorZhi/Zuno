from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
STANDARD = ROOT / "docs/governance/human-first-documentation-standard.md"


def verify() -> list[str]:
    errors: list[str] = []
    if not STANDARD.exists():
        errors.append("missing human-first documentation standard")
    else:
        standard = STANDARD.read_text(encoding="utf-8")
        for marker in (
            "Part A / Part B Model",
            "Part A — Human Narrative",
            "Part B — Engineering / Agent Reference",
            "A → B Semantic Mapping",
            "Architecture Document Template",
            "Module Document Template",
            "B3 Cross-boundary Contract Format",
            "Human Review Checklist",
            "Part B Review Checklist",
        ):
            if marker not in standard:
                errors.append(f"human-first standard missing model marker: {marker}")
    for path in (ARCH, VIEWS, HTML):
        if not path.exists():
            errors.append(f"missing canonical architecture document: {path.relative_to(ROOT)}")
    if not ARCH.exists():
        return errors
    design = ARCH.read_text(encoding="utf-8")
    for marker in ("模块化 Python 后端", "独立网络服务", "Current", "Target", "History", "为什么必须独立服务", "Reconciliation"):
        if marker not in design:
            errors.append(f"architecture.md missing writing marker: {marker}")
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
