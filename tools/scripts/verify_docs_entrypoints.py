from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
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
FACTS = ["README.md", "project-background.md", "team-and-ownership.md", "development-evolution.md", "delivery-and-usage.md", "technology-reality.md"]
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def load_links():
    path = REPO_ROOT / "tools/scripts/verify_markdown_internal_links.py"
    spec = importlib.util.spec_from_file_location("verify_markdown_internal_links", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load markdown link verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify() -> list[str]:
    errors = list(load_links().verify())
    required = [
        "README.md", "docs/README.md", "docs/project/README.md", "docs/project/facts/README.md",
        "docs/project/architecture/README.md", "docs/project/architecture/architecture.md",
        "docs/project/architecture/architecture-views.md", "docs/project/architecture/architecture.html",
        "docs/project/modules/README.md", "docs/status/production-readiness.md", "docs/decisions/README.md",
        "docs/governance/repo-ownership-matrix.md", ".agent/references/docs-map.md", ".agent/system.yaml",
        *TAXONOMY,
        *[f"docs/project/facts/{name}" for name in FACTS if name != "README.md"],
    ]
    for path in required:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing documentation entrypoint: {path}")
    root = REPO_ROOT / "docs/project/architecture"
    if {path.name for path in root.iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("docs/project/architecture must contain exactly four files")
    if any(path.is_dir() for path in root.iterdir()):
        errors.append("docs/project/architecture must not contain subdirectories")
    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    index = read("docs/project/README.md")
    docs_readme = read("docs/README.md")
    system = read(".agent/system.yaml")
    for path in TAXONOMY:
        marker = path.split("docs/project/", 1)[-1]
        for label, content in (("docs/project/README.md", index), ("docs/README.md", docs_readme), (".agent/system.yaml", system)):
            if marker not in content and Path(path).name not in content:
                errors.append(f"{label} does not route to {path}")
    legacy_index = read("docs/project/modules/README.md")
    if "Superseded" not in legacy_index:
        errors.append("legacy module index must be marked Superseded")
    for path in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md"):
        if "status: superseded-legacy-reference" not in path.read_text(encoding="utf-8"):
            errors.append(f"legacy module lacks superseded status: {path.relative_to(REPO_ROOT)}")
    for marker in ("Current", "Target", "Hypothesis", "History", "Microservice", "Python-only"):
        if marker not in index:
            errors.append(f"docs/project/README.md missing status/architecture marker: {marker}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
