from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_IGNORES = [
    ".local/",
    ".codex/",
    "node_modules/",
    "apps/web/node_modules/",
    "apps/web/dist/",
    "data/evals/multihop/raw/",
    "reports/evals/multihop/real_runtime/",
    ".agent/local/*",
]

FORBIDDEN_IGNORE_LINES = [
    "apps/web/AGENTS.md",
    "src/frontend/node_modules",
    "src/frontend/dist",
    "$null",
    "&1",
]

BLOCKED_LEGACY_PATHS = [
    "domain-packs",
    "tests/compat",
    "src/backend/zuno/services/domain_pack",
    "src/backend/zuno/core/graphs/domain_qa_graph.py",
]

FORBIDDEN_CURRENT_PATHS = [
    "src/frontend",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return proc.stdout.splitlines()


def main() -> int:
    errors: list[str] = []
    gitignore = _read(".gitignore")
    dockerignore = _read(".dockerignore")

    for entry in REQUIRED_IGNORES:
        if entry not in gitignore:
            errors.append(f".gitignore missing required ignore: {entry}")

    for line in FORBIDDEN_IGNORE_LINES:
        if line in gitignore or line in dockerignore:
            errors.append(f"ignore files contain retired or wrong entry: {line}")

    for path in BLOCKED_LEGACY_PATHS:
        if not (REPO_ROOT / path).exists():
            errors.append(f"Blocked Legacy path missing without Phase 11 proof: {path}")

    for path in FORBIDDEN_CURRENT_PATHS:
        if (REPO_ROOT / path).exists():
            errors.append(f"retired current path exists: {path}")

    tracked = set(_tracked_files())
    forbidden_tracked_prefixes = [
        "node_modules/",
        "apps/web/node_modules/",
        "apps/web/dist/",
        ".local/",
        ".codex/",
        "data/evals/multihop/raw/",
        "reports/evals/multihop/real_runtime/",
    ]
    for tracked_path in tracked:
        normalized = tracked_path.replace("\\", "/")
        for prefix in forbidden_tracked_prefixes:
            if normalized.startswith(prefix):
                errors.append(f"generated/local path is tracked: {normalized}")
                break

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Repo hygiene verification failed.")
        return 1

    print("Repo hygiene verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
