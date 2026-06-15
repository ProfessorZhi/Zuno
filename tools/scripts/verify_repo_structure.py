from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "apps/desktop",
    "apps/web",
    "docs/architecture",
    "docs/development",
    "domain-packs",
    "infra/db",
    "infra/docker",
    "services",
    "services/api",
    "src/backend",
    "src/backend/zuno",
    "src/backend/zuno/main.py",
    "tests",
    "tests/compat",
    "tools",
    "tools/evals/zuno",
    "tools/launchers/windows",
]

DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "README.md": [
        "## Repository Layout",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "pytest tests/test_phase0_runtime_recovery.py",
        "python tools/scripts/verify_repo_structure.py",
        "pytest tests/test_repo_structure_consistency.py",
        "pytest tests/test_publish_boundary.py",
        "apps/",
        "docs/",
        "domain-packs/",
        "infra/",
        "services/",
        "src/",
        "tests/",
        "tools/",
        "./docs/architecture/README.md",
    ],
    "docs/README.md": [
        "./architecture/README.md",
        "./development/README.md",
        "./development/architecture-doc-maintenance-workflow.md",
    ],
    "docs/architecture/README.md": [
        "./current-architecture.md",
        "./target-architecture.md",
        "./phases/README.md",
        "./plans/stable-baseline-recovery-and-runtime-deepening-plan.md",
        "./history/README.md",
    ],
    "docs/architecture/plans/README.md": [
        "../phases/README.md",
        "history/",
    ],
    "docs/architecture/phases/README.md": [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 5: Docs And Public Explanation Sync",
        "the user has personally tried the recovered runtime",
    ],
    "docs/development/backend-layering-guidelines.md": [
        "src/backend/zuno/api/*",
        "src/backend/zuno/core/*",
        "src/backend/zuno/services/*",
        "src/backend/zuno/database/dao/*",
        "do not treat `services/api/src/zuno/*` as the default placement rule while Phase 0 is still open",
    ],
    "docs/development/README.md": [
        "Architecture Doc Maintenance Workflow",
        "backend layering rules",
        "public-release-checklist.md",
        "history/README.md",
    ],
}

README_FORBIDDEN_PHRASES = [
    "Phase 1-6",
    "Phase 1-7",
    "Phase 7",
    "verify_phase7_readiness.py",
    "migration-facing backend startup root",
]


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

        if relative_path == "README.md":
            for phrase in README_FORBIDDEN_PHRASES:
                if phrase in content:
                    errors.append(f"README.md contains stale phase phrase: {phrase}")
    return errors


def verify_archived_reference_docs() -> list[str]:
    errors: list[str] = []
    if (REPO_ROOT / "docs" / "reference" / "migration.md").exists():
        errors.append("docs/reference/migration.md should be archived out of the front path")
    if not (REPO_ROOT / "docs" / "reference" / "history" / "migration.md").exists():
        errors.append("docs/reference/history/migration.md is missing")
    return errors


def run_verification() -> VerificationResult:
    errors = [
        *verify_required_paths(),
        *verify_doc_phrases(),
        *verify_archived_reference_docs(),
    ]
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
