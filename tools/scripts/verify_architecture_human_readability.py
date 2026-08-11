from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [
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
    for path in CANONICAL:
        if not path.exists():
            errors.append(f"missing canonical Markdown: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        label = str(path.relative_to(ROOT))
        for marker in ("status:", "canonical_question:", "owner:", "Current", "Target", "Gap"):
            if marker not in text:
                errors.append(f"{label} missing human-readable metadata: {marker}")
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
