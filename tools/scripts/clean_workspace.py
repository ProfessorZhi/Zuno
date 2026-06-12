from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ROOT_TARGETS = [
    ".pytest_cache",
    ".test-tmp",
    ".playwright-mcp",
]

RECURSIVE_PATTERNS = [
    "__pycache__",
]

SAFE_RECURSIVE_ROOTS = [
    "src",
    "tests",
    "tools",
    "infra",
    "apps",
]


def _iter_targets() -> list[Path]:
    targets: list[Path] = []

    for relative_path in ROOT_TARGETS:
        candidate = REPO_ROOT / relative_path
        if candidate.exists():
            targets.append(candidate)

    for root_name in SAFE_RECURSIVE_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for pattern in RECURSIVE_PATTERNS:
            for candidate in root.rglob(pattern):
                if candidate.exists():
                    targets.append(candidate)

    # Keep order stable and avoid duplicate removals.
    unique_targets: list[Path] = []
    seen: set[Path] = set()
    for candidate in sorted(targets):
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_targets.append(candidate)
    return unique_targets


def clean_workspace(*, dry_run: bool) -> dict[str, object]:
    removed: list[str] = []
    for target in _iter_targets():
        removed.append(str(target.relative_to(REPO_ROOT)))
        if dry_run:
            continue
        shutil.rmtree(target, ignore_errors=False)

    return {
        "dry_run": dry_run,
        "removed_count": len(removed),
        "removed": removed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove safe local cache and temporary directories from the workspace root."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without deleting anything.",
    )
    args = parser.parse_args()

    result = clean_workspace(dry_run=args.dry_run)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
