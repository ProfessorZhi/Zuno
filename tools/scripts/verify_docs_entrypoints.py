from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require_phrases(name: str, content: str, phrases: list[str]) -> list[str]:
    return [f"{name} missing phrase: {phrase}" for phrase in phrases if phrase not in content]


def verify_active_spec_domain_pack_boundaries() -> list[str]:
    allowed_migration_specs = {
        REPO_ROOT / "docs/architecture/specs/README.md",
        REPO_ROOT / "docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md",
    }
    forbidden_phrases = [
        "Domain Pack\n  ->",
        "Domain Pack ->",
        "Domain Pack retrieval policy inputs",
        "Domain-specific graph cues belong in `Domain Pack retrieval_policy`",
        "GraphRAG 不是孤立能力，而是受 Domain Pack 驱动",
        "Domain Pack 成为领域扩展机制",
        "GraphRAG 受 `Domain Pack` 控制",
        "LangGraph runtime 必须能感知 Domain Pack",
        "它验证 Domain Pack 是否有价值",
        "Domain Pack schema",
        "Phase 3: Domain Pack Formalization",
        "deeper LangGraph, GraphRAG, Domain Pack",
        "business orchestration, retrieval, GraphRAG, Domain Pack, provider adapters",
    ]

    errors: list[str] = []
    for path in sorted((REPO_ROOT / "docs/architecture/specs").glob("*.md")):
        if path in allowed_migration_specs:
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in content:
                relative_path = path.relative_to(REPO_ROOT).as_posix()
                errors.append(
                    f"{relative_path} promotes Domain Pack as current/target driver: {phrase}"
                )
    return errors


def main() -> int:
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    roadmap = _read("docs/architecture/roadmap.md")
    evidence = _read("docs/evidence/public-demo.md")

    errors: list[str] = []
    errors.extend(
        _require_phrases(
            "README.md",
            readme,
            [
                "First-time readers start here:",
                "./docs/architecture/current-architecture.md",
                "./docs/architecture/target-architecture.md",
                "./docs/architecture/roadmap.md",
                "./docs/evidence/public-demo.md",
                "Blocked Legacy",
                "Phase 11A",
                "Phase 11B",
                "Phase 11C",
                "Phase 12",
                "src/backend/zuno",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/README.md",
            docs_index,
            [
                "./architecture/current-architecture.md",
                "./architecture/target-architecture.md",
                "./architecture/roadmap.md",
                "./evidence/public-demo.md",
                "docs/architecture/history/",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/architecture/README.md",
            architecture_index,
            [
                "current-architecture.md",
                "target-architecture.md",
                "roadmap.md",
                "../evidence/public-demo.md",
                ".agent/programs/official-graphrag-cleanup-v1/",
                ".agent/programs/zuno-target-architecture-migration-v1/",
                "history/phases/",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/architecture/roadmap.md",
            roadmap,
            [
                "Phase 11A: complete",
                "Phase 11B: complete",
                "Phase 11C: blocked",
                "Phase 12: partial / not closed",
                "Blocked Legacy",
                ".agent/programs/zuno-target-architecture-migration-v1/",
                ".agent/programs/official-graphrag-cleanup-v1/",
            ],
        )
    )
    errors.extend(
        _require_phrases(
            "docs/evidence/public-demo.md",
            evidence,
            [
                "../development/public-demo-evidence.md",
                "../development/public-demo-runbook.md",
                "../development/public-demo-acceptance.md",
            ],
        )
    )
    errors.extend(verify_active_spec_domain_pack_boundaries())

    forbidden_front_path = [
        "docs/architecture/plans/stable-baseline-recovery-and-runtime-deepening-plan.md",
        "./docs/architecture/phases/README.md",
        "./phases/README.md",
        "./plans/",
        "05_TopDown_题库学习/项目/02_项目映射/Zuno/",
    ]
    for name, content in {
        "README.md": readme,
        "docs/README.md": docs_index,
        "docs/architecture/README.md": architecture_index,
    }.items():
        for forbidden in forbidden_front_path:
            if forbidden in content:
                errors.append(f"{name} contains retired front-path text: {forbidden}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("documentation entrypoint verification failed.")
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
