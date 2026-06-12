from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "apps/desktop",
    "docs/architecture",
    "docs/development",
    "infra/db",
    "infra/docker",
    "src/backend",
    "src/backend/zuno/api",
    "src/backend/zuno/core",
    "src/backend/zuno/database",
    "src/backend/zuno/database/dao",
    "src/backend/zuno/services",
    "apps/web",
    "tests",
    "tests/compat",
    "tools",
    "tools/evals/zuno",
    "tools/launchers/windows",
]

DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "README.md": [
        "## Repository Layout",
        "python tools/scripts/verify_repo_structure.py",
        "pytest tests/test_repo_structure_consistency.py",
        "pytest tests/test_publish_boundary.py",
        "apps/",
        "docs/",
        "infra/",
        "infra/db/",
        "src/",
        "tests/",
        "tools/",
        "tools/launchers/windows/",
        "./docs/architecture/README.md",
        "./docs/development/github-publish-boundary.md",
    ],
    "docs/README.md": [
        "./architecture/README.md",
        "./development/README.md",
        "./development/github-publish-boundary.md",
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
        "Phase 1",
        "Phase 2",
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
        "repository structure verification",
        "backend layering rules",
        "public release checklist",
    ],
    "docs/development/github-publish-boundary.md": [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
    ],
}


@dataclass
class VerificationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    errors: list[str] = []
    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required path: {relative_path}")
    return errors


def verify_doc_phrases() -> list[str]:
    errors: list[str] = []
    for relative_path, phrases in DOC_REQUIRED_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required doc: {relative_path}")
            continue

        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")
    return errors


def run_verification() -> VerificationResult:
    errors = [*verify_required_paths(), *verify_doc_phrases()]
    return VerificationResult(errors=errors)


def main() -> int:
    result = run_verification()
    if result.ok:
        print("Repository structure verification passed.")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    print("Repository structure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
