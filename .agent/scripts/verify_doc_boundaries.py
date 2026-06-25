from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_CURRENT_DIRS = [
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/superpowers",
    "docs/prototypes/superpowers-legacy",
    "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
]

REQUIRED_DOCS = [
    "docs/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/history/README.md",
    "docs/evidence/public-demo.md",
]

REQUIRED_AGENT_PROGRAMS = [
    ".agent/programs/current.md",
    ".agent/programs/official-graphrag-cleanup-v1/implementation-roadmap.md",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_DOCS + REQUIRED_AGENT_PROGRAMS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing boundary path: {relative_path}")

    for relative_path in FORBIDDEN_CURRENT_DIRS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired docs directory still on current path: {relative_path}")

    front_path_files = ["README.md", "docs/README.md", "docs/architecture/README.md"]
    forbidden_front_path_text = [
        "docs/architecture/phases/README.md",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/superpowers/",
        "docs/prototypes/superpowers-legacy/",
    ]
    for relative_path in front_path_files:
        content = _read(relative_path)
        for phrase in forbidden_front_path_text:
            if phrase in content:
                errors.append(f"{relative_path} contains retired front-path text: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Doc boundary verification failed.")
        return 1

    print("Doc boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
