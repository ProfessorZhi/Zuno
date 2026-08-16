from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
MODULE_FILES = [
    "docs/modules/README.md",
    "docs/modules/01-application-integration.md",
    "docs/modules/02-legal-domain-work-product.md",
    "docs/modules/03-knowledge-evidence.md",
    "docs/modules/04-agent-runtime-control.md",
    "docs/modules/05-capability-skill.md",
    "docs/modules/06-tool-runtime-effects.md",
    "docs/modules/07-model-gateway.md",
    "docs/modules/08-security-governance.md",
    "docs/modules/09-observability-evaluation.md",
]


def _load_links():
    path = REPO_ROOT / "tools/scripts/verify_markdown_internal_links.py"
    spec = importlib.util.spec_from_file_location("verify_markdown_internal_links", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load markdown link verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify() -> list[str]:
    errors = list(_load_links().verify())
    required = [
        "README.md", "docs/README.md",
        "docs/project/README.md", "docs/project/project-background.md",
        "docs/project/team-and-contributions.md", "docs/project/development-process.md",
        "docs/governance/project-fact-provenance.md",
        "docs/governance/human-first-documentation-standard.md",
        "docs/evidence/README.md", *MODULE_FILES, "docs/history/README.md",
        "docs/history/red-blue/README.md",
        "docs/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/architecture/README.md", "docs/architecture/architecture.md",
        "docs/architecture/architecture-views.md", "docs/architecture/architecture.html",
        "docs/decisions/README.md", "docs/terminology.md",
        "docs/operations/postgresql-migration-runbook.md",
        "docs/operations/infrastructure-dr-profile.yaml",
        ".agent/references/docs-map.md", ".agent/system.yaml",
    ]
    for path in required:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing documentation entrypoint: {path}")
    root = REPO_ROOT / "docs/architecture"
    if {path.name for path in root.iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("docs/architecture must contain exactly four files")
    if any(path.is_dir() for path in root.iterdir()):
        errors.append("docs/architecture must not contain subdirectories")
    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")
    for forbidden in (REPO_ROOT / "docs/facts", REPO_ROOT / "project-reconstruction-lab"):
        if forbidden.exists():
            errors.append(f"obsolete documentation workspace must be absent: {forbidden.relative_to(REPO_ROOT)}")
    index = (REPO_ROOT / "docs/README.md").read_text(encoding="utf-8")
    for marker in ("Current", "Target", "Unknown", "project/", "architecture/", "modules/", "evidence/", "history/red-blue/"):
        if marker not in index:
            errors.append(f"docs/README.md missing status/architecture marker: {marker}")
    modules = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    for marker in ("01-application-integration.md", "09-observability-evaluation.md", "design skeleton", "implementation_authorization"):
        if marker not in modules:
            errors.append(f"docs/modules/README.md missing module design marker: {marker}")
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
