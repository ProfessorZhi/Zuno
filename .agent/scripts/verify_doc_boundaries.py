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
    "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    ".agent/programs/current.md",
    "docs/architecture/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def verify_active_audits_are_not_history_documents() -> list[str]:
    errors: list[str] = []

    for path in sorted((REPO_ROOT / "docs/architecture/audits").glob("*.md")):
        content = path.read_text(encoding="utf-8")
        if "Status: History" in content:
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            errors.append(
                f"{relative_path} active architecture audit is marked History"
            )

    return errors


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_DOCS + REQUIRED_AGENT_PROGRAMS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing boundary path: {relative_path}")

    for relative_path in FORBIDDEN_CURRENT_DIRS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired docs directory still on current path: {relative_path}")

    for relative_path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = relative_path.read_text(encoding="utf-8")
        if "C:\\Users\\Administrator\\Downloads" in content:
            errors.append(f"{relative_path.relative_to(REPO_ROOT)} contains local Downloads path")

    current = _read("docs/architecture/current-architecture.md")
    if "Context Orchestrator and Post-turn Pipeline are Target, not Current" not in current:
        errors.append("current architecture must not promote Context Orchestrator to Current")

    docs_front_path = ["README.md", "docs/README.md", "docs/architecture/README.md"]
    for relative_path in docs_front_path:
        content = _read(relative_path)
        if "zuno-ideal-architecture-and-repo-layout.html" in content:
            errors.append(f"{relative_path} must not place .agent target HTML in docs front path")

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

    forbidden_active_doc_text = [
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
    ]
    for path in sorted(REPO_ROOT.glob("docs/**/*.md")):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path.startswith("docs/architecture/history/"):
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_active_doc_text:
            if phrase in content:
                errors.append(
                    f"{relative_path} links retired architecture current path: {phrase}"
                )

    errors.extend(verify_active_audits_are_not_history_documents())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Doc boundary verification failed.")
        return 1

    print("Doc boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
