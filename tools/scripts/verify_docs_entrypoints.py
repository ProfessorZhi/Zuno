from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require_phrases(name: str, content: str, phrases: list[str]) -> list[str]:
    errors: list[str] = []
    for phrase in phrases:
        if phrase not in content:
            errors.append(f"{name} missing phrase: {phrase}")
    return errors


def main() -> int:
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    development_index = _read("docs/development/README.md")

    errors: list[str] = []
    errors.extend(
        _require_phrases(
            "README.md",
            readme,
            [
                "./docs/architecture/README.md",
                "./docs/architecture/current-architecture.md",
                "./docs/architecture/target-architecture.md",
                "./docs/development/public-demo-evidence.md",
                "./docs/development/public-demo-runbook.md",
                "./docs/development/public-demo-acceptance.md",
                "First-time readers start here:",
                "Maintainer-only release workflow:",
                "First-time readers should stop at the public path below and skip release staging, checklist, and publish-boundary docs on the first pass.",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/README.md",
            docs_index,
            [
                "./architecture/README.md",
                "./development/architecture-doc-maintenance-workflow.md",
                "./development/public-demo-evidence.md",
                "./development/public-demo-runbook.md",
                "./development/public-demo-acceptance.md",
                "./development/README.md",
                "./development/github-publish-boundary.md",
                "## Maintainer Path",
                "## First-Read Path",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/architecture/README.md",
            architecture_index,
            [
                "./current-architecture.md",
                "./target-architecture.md",
                "./phases/README.md",
                "./specs/enterprise-retrieval-governance.md",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/development/README.md",
            development_index,
            [
                "It is not the first-read public explanation path.",
                "## Current Maintainer Path",
                "## Current Sync Rule",
                "../../README.md",
                "../architecture/README.md",
            ],
        )
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("documentation entrypoint verification failed.")
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
