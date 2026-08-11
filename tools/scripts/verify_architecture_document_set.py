from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = REPO_ROOT / "docs/project/architecture"
TAXONOMY = [
    "docs/project/product/product-architecture.md",
    "docs/project/domain/legal-domain-model.md",
    "docs/project/domain/domain-state-lifecycle.md",
    "docs/project/agents/agent-platform.md",
    "docs/project/agents/multi-agent-runtime.md",
    "docs/project/knowledge/knowledge-evidence-architecture.md",
    "docs/project/services/service-architecture.md",
    "docs/project/data/data-ownership-and-recovery.md",
    "docs/project/security/security-architecture.md",
    "docs/project/eval/legal-eval-and-benchmark.md",
    "docs/project/deployment/microservice-deployment.md",
]
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
LEGACY_MODULES = sorted(path.name for path in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md"))


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    files = {path.name for path in ARCH_ROOT.iterdir() if path.is_file()}
    dirs = [path.name for path in ARCH_ROOT.iterdir() if path.is_dir()]
    if files != ARCHITECTURE_FILES:
        errors.append(f"architecture file set mismatch: {sorted(files)}")
    if dirs:
        errors.append(f"architecture directory must not contain subdirectories: {dirs}")

    for path in TAXONOMY:
        full = REPO_ROOT / path
        if not full.exists():
            errors.append(f"missing canonical taxonomy document: {path}")
        else:
            content = full.read_text(encoding="utf-8")
            for marker in ("status:", "canonical_question:", "owner:", "Current", "Target", "Gap"):
                if marker not in content:
                    errors.append(f"{path} missing taxonomy metadata or boundary: {marker}")

    for path in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md"):
        content = path.read_text(encoding="utf-8")
        if "status: superseded-legacy-reference" not in content:
            errors.append(f"legacy module is not explicitly superseded: {path.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    design = read("docs/project/architecture/architecture.md")
    index = read("docs/project/README.md")
    arch_index = read("docs/project/architecture/README.md")
    legacy_index = read("docs/project/modules/README.md")
    system = read(".agent/system.yaml")
    for path in TAXONOMY:
        marker = path.split("docs/project/", 1)[-1]
        for label, content in (("architecture.md", design), ("docs/project/README.md", index), (".agent/system.yaml", system)):
            if marker not in content and Path(path).name not in content:
                errors.append(f"{label} does not route to {path}")
    if "Superseded" not in legacy_index or "History" not in legacy_index:
        errors.append("legacy module index must explain Superseded and History")
    for marker in ("architecture.md", "architecture-views.md", "architecture.html", "docs/project/", "docs/status/", "ADR"):
        if marker not in arch_index:
            errors.append(f"architecture README missing boundary marker: {marker}")
    if "11 Logical Modules + 1 Architecture" not in design or "History" not in design:
        errors.append("architecture.md must record the former 11+1 arrangement as History")
    if "Current" not in index or "Target" not in index or "Hypothesis" not in index:
        errors.append("project README must explain Current/Target/Hypothesis")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture document set verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
