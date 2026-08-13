from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
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
        "README.md", "docs/README.md", "docs/project/README.md", "docs/project/history/README.md",
        "docs/project/status/README.md", "docs/project/status/current-reality.md", "docs/project/status/target-status.md",
        "docs/project/status/production-readiness.md", "docs/history/superseded-document-taxonomy/README.md",
        "docs/project/architecture/README.md", "docs/project/architecture/architecture.md",
        "docs/project/architecture/architecture-views.md", "docs/project/architecture/architecture.html", "docs/decisions/README.md",
        "docs/governance/repo-ownership-matrix.md", ".agent/references/docs-map.md", ".agent/system.yaml",
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
    for marker in ("Current", "Target", "Hypothesis", "History", "Microservice", "Python-only", "docs/project/history/", "docs/project/status/"):
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
