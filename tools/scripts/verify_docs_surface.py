from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "README.md": [
        "## First-Read Path",
        "./docs/README.md",
        "./docs/architecture/README.md",
        "./docs/architecture/specs/README.md",
        "./docs/architecture/plans/README.md",
        "./docs/architecture/plans/current-phase-audit.md",
        "python tools/scripts/verify_docs_surface.py",
        "pytest tests/test_docs_surface_consistency.py",
        "pytest tests/test_publish_boundary.py",
    ],
    "docs/README.md": [
        "## First-Read Path",
        "./architecture/README.md",
        "./architecture/specs/README.md",
        "./architecture/plans/README.md",
        "./development/README.md",
    ],
    "docs/architecture/README.md": [
        "`Phase 5`: completed",
        "`Phase 6`: completed",
        "`Phase 7`: completed",
        "./specs/README.md",
        "./plans/README.md",
        "./plans/current-phase-audit.md",
    ],
    "docs/architecture/zuno_refactor_plan.md": [
        "`Phase 5`：已完成",
        "`Phase 6`：已完成",
        "`Phase 7`：已完成",
        "每完成一个大阶段，都必须回看这些入口是否仍然对齐",
        "已经解决的问题，不再继续挂在主阅读路径里；",
    ],
    "docs/architecture/plans/README.md": [
        "./zuno-refactor-execution-plan.md",
        "./current-phase-audit.md",
        "不属于当前主阅读路径",
    ],
    "docs/architecture/plans/current-phase-audit.md": [
        "`Phase 4`: completed",
        "`Phase 5`: completed",
        "`Phase 6`: completed",
        "`Phase 7`: completed",
        "No further serial phase remains.",
    ],
    "docs/architecture/plans/zuno-refactor-execution-plan.md": [
        "## Phase 3：文档与展示面硬收口",
        "## Phase 5：LangGraph + GraphRAG 主线深化",
        "python tools/scripts/verify_docs_surface.py",
        "pytest tests/test_docs_surface_consistency.py",
        "pytest tests/test_publish_boundary.py",
        "`Phase 5` is completed and already merged to `main`.",
    ],
    "docs/architecture/specs/README.md": [
        "Platform Evolution And Future Direction",
        "Domain Pack + LangGraph + GraphRAG Architecture",
        "Layered Backend And Service Evolution",
    ],
    "docs/development/README.md": [
        "It is not part of the first-read public project path.",
        "It should explain maintenance rules, not replace the public architecture path.",
    ],
}

DISALLOWED_PHRASES: dict[str, list[str]] = {
    "docs/architecture/README.md": [
        "docs/development/public-demo-evidence.md",
        "docs/development/public-demo-runbook.md",
        "docs/development/public-demo-acceptance.md",
    ],
    "docs/architecture/zuno_refactor_plan.md": [
        "### Phase 3：GraphRAG 重构",
        "### Phase 7：包名收口 `agentchat -> zuno`",
    ],
    "docs/architecture/plans/zuno-refactor-execution-plan.md": [
        "`Phase 1-4` 已完成并已有最小验收证据",
        "当前仓库口径已经同步记录了 `Phase 1-4` 的关闭判断",
        "继续线性推进 `Phase 5`",
    ],
}


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def main() -> int:
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

    for relative_path, phrases in DISALLOWED_PHRASES.items():
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase in content:
                errors.append(f"{relative_path} still contains stale phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Docs surface verification failed.")
        return 1

    print("Docs surface verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
