from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STANDARD = ROOT / "docs/governance/architecture-document-writing-standard.md"
ARCH = ROOT / "docs/project/architecture/architecture.md"
VIEWS = ROOT / "docs/project/architecture/architecture-views.md"
HTML = ROOT / "docs/project/architecture/architecture.html"
TAXONOMY = [
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
]


def verify() -> list[str]:
    errors: list[str] = []
    if not STANDARD.exists():
        return ["missing architecture writing standard"]
    standard = STANDARD.read_text(encoding="utf-8")
    for marker in ("Canonical taxonomy", "Logical 与 Physical", "Current", "Target", "Hypothesis", "History", "Why service?", "Red Attack"):
        if marker not in standard:
            errors.append(f"writing standard missing marker: {marker}")
    for path in [ARCH, VIEWS, HTML, *TAXONOMY]:
        if not path.exists():
            errors.append(f"missing canonical architecture document: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if path in TAXONOMY:
            for marker in ("status:", "canonical_question:", "owner:", "Current", "Target", "Gap"):
                if marker not in text:
                    errors.append(f"{path.relative_to(ROOT)} missing metadata/boundary: {marker}")
            if not any(marker in text for marker in ("为什么", "Why", "问题", "Boundary", "Definition", "canonical_question")):
                errors.append(f"{path.relative_to(ROOT)} lacks a problem explanation")
            if not any(marker in text for marker in ("Ownership", "Owner", "owner:", "拥有")):
                errors.append(f"{path.relative_to(ROOT)} lacks ownership explanation")
            if not any(marker in text for marker in ("Failure", "失败", "Recovery", "recovery", "stale", "Gap")):
                errors.append(f"{path.relative_to(ROOT)} lacks failure explanation")
            if not any(marker in text for marker in ("Evidence", "证据", "Benchmark", "Metrics", "Current")):
                errors.append(f"{path.relative_to(ROOT)} lacks evidence boundary")
    for marker in ("Python-only", "Microservice", "Current", "Target", "History", "Why service?", "Reconciliation"):
        if marker not in ARCH.read_text(encoding="utf-8"):
            errors.append(f"architecture.md missing writing marker: {marker}")
    if 'fetch("./architecture-views.md")' not in HTML.read_text(encoding="utf-8"):
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
