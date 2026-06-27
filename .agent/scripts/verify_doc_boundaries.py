from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_CURRENT_DIRS = [
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    "docs/superpowers",
]

REQUIRED_DOCS = [
    "docs/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/history/README.md",
    "docs/evidence/public-demo.md",
]

REQUIRED_AGENT_PROGRAMS = [
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/closure-checklist.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
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

    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = path.read_text(encoding="utf-8")
        if "C:\\Users\\Administrator\\Downloads" in content:
            errors.append(f"{path.relative_to(REPO_ROOT)} contains local Downloads path")

    current = _read("docs/architecture/current-architecture.md")
    if "以下仍是 Target，不是当前成熟事实" not in current:
        errors.append("current architecture must not promote Target behavior to Current")

    target = _read("docs/architecture/target-architecture.md")
    for phrase in [
        "Summary Compression",
        "Structured Extraction",
        "Native BM25",
        "ToolCard",
        "RRF",
        "`auto` 是 router",
        "GraphRAG 实体抽取默认主路径是 LLM 抽取",
    ]:
        if phrase not in target:
            errors.append(f"target architecture missing canonical phrase: {phrase}")

    docs_front_path = ["README.md", "docs/README.md", "docs/architecture/README.md"]
    for relative_path in docs_front_path:
        content = _read(relative_path)
        if "zuno-ideal-architecture-and-repo-layout.html" in content:
            errors.append(f"{relative_path} must not place .agent target HTML in docs front path")

    forbidden_front_path_text = [
        "docs/architecture/phases/README.md",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
        "docs/superpowers/",
    ]
    for relative_path in docs_front_path:
        content = _read(relative_path)
        for phrase in forbidden_front_path_text:
            if phrase in content:
                errors.append(f"{relative_path} contains retired front-path text: {phrase}")

    forbidden_active_doc_text = [
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
    ]
    for path in sorted(REPO_ROOT.glob("docs/**/*.md")):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path.startswith("docs/history/"):
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_active_doc_text:
            if phrase in content:
                errors.append(
                    f"{relative_path} links retired architecture current path: {phrase}"
                )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Doc boundary verification failed.")
        return 1

    print("Doc boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
