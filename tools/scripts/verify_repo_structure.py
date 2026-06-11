from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "apps/desktop",
    "docs/architecture",
    "docs/development",
    "infra/docker",
    "launchers",
    "src/backend",
    "src/backend/zuno/api",
    "src/backend/zuno/core",
    "src/backend/zuno/database",
    "src/backend/zuno/database/dao",
    "src/backend/zuno/services",
    "src/frontend",
    "tests",
    "tools",
]

DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "README.md": [
        "## Repository Layout",
        "python tools/scripts/verify_repo_structure.py",
        "pytest tests/test_repo_structure_consistency.py",
        "pytest tests/test_publish_boundary.py",
        "./docs/architecture/README.md",
        "./docs/development/README.md",
        "./docs/development/github-publish-boundary.md",
    ],
    "docs/README.md": [
        "./architecture/README.md",
        "./development/README.md",
    ],
    "docs/architecture/README.md": [
        "./plans/current-phase-audit.md",
        "./specs/layered-backend-and-service-evolution.md",
        "./plans/zuno-refactor-execution-plan.md",
    ],
    "docs/architecture/plans/README.md": [
        "./current-phase-audit.md",
        "./zuno-refactor-execution-plan.md",
    ],
    "docs/architecture/plans/current-phase-audit.md": [
        "`Phase 2`: completed",
        "`Phase 3`: completed",
        "verify_repo_structure.py",
        "tests/test_repo_structure_consistency.py",
        "tests/test_publish_boundary.py",
    ],
    "docs/development/backend-layering-guidelines.md": [
        "src/backend/zuno/api/v1/*",
        "src/backend/zuno/services/*",
        "src/backend/zuno/database/dao/*",
    ],
    "docs/development/README.md": [
        "backend layering rules",
        "publish boundary rules",
        "repository structure verification",
    ],
    "docs/development/github-publish-boundary.md": [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
    ],
}


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")

    for relative_path, phrases in DOC_REQUIRED_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required doc: {relative_path}")
            continue

        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Repository structure verification failed.")
        return 1

    print("Repository structure verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

