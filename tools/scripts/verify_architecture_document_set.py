from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = REPO_ROOT / "docs/project/architecture"
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}


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

    for path in (
        REPO_ROOT / "docs/project/README.md",
        REPO_ROOT / "docs/project/history/README.md",
        REPO_ROOT / "docs/project/status/README.md",
        REPO_ROOT / "docs/project/status/current-reality.md",
        REPO_ROOT / "docs/project/status/target-status.md",
        REPO_ROOT / "docs/project/status/production-readiness.md",
        REPO_ROOT / "docs/history/superseded-document-taxonomy/README.md",
    ):
        if not path.exists():
            errors.append(f"missing canonical project entrypoint: {path.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    design = read("docs/project/architecture/architecture.md")
    index = read("docs/project/README.md")
    arch_index = read("docs/project/architecture/README.md")
    system = read(".agent/system.yaml")
    if "docs/project/history/" not in index or "docs/project/status/" not in index:
        errors.append("project README must route to history and status")
    if "docs/project/architecture/" not in system:
        errors.append("system.yaml must route to architecture surface")
    for marker in ("architecture.md", "architecture-views.md", "architecture.html", "docs/project/", "status/", "ADR"):
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
