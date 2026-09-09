from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected migration marker not found in {relative}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    replace(
        "docs/modules/evaluation/README.md",
        "](../../src/backend/zuno/platform/observability/README.md)",
        "](../../../src/backend/zuno/platform/observability/README.md)",
    )
    replace(
        "docs/red-blue/archive/legacy/README.md",
        "../../../architecture/architecture.md",
        "../../../architecture/README.md",
    )
    replace(
        "tools/scripts/verify_docs_entrypoints.py",
        'PROJECT_FILES = [\n    "docs/project/README.md",\n    "docs/project/README.md",\n    "docs/project/reference.md",\n]',
        'PROJECT_FILES = [\n    "docs/project/README.md",\n    "docs/project/reference.md",\n]',
    )
    replace(
        "tools/scripts/verify_docs_entrypoints.py",
        '        "docs/architecture/README.md",\n        "docs/architecture/README.md",',
        '        "docs/architecture/README.md",',
    )
    replace(
        "tools/scripts/verify_docs_entrypoints.py",
        '''    project_readme = (REPO_ROOT / "docs/project/README.md").read_text(encoding="utf-8")\n    for marker in (\n        "Project — Zuno 为什么会出现",\n        "Human View",\n        "Machine View",\n        "project.md",\n        "reference.md",\n        "project-fact-provenance.md",\n    ):\n        if marker not in project_readme:\n            errors.append(f"docs/project/README.md missing project navigation marker: {marker}")''',
        '''    project_readme = (REPO_ROOT / "docs/project/README.md").read_text(encoding="utf-8")\n    for marker in (\n        "# Zuno 项目：从智慧司法研究到可验证的法律智能 Agent 平台",\n        "为什么会有这个项目",\n        "为什么不直接用 Dify、Coze",\n        "项目是怎样发展到今天的",\n        "团队是什么形态，我在里面做了什么",\n        "相比通用方案，我们今天到底证明了什么",\n        "project-fact-provenance.md",\n    ):\n        if marker not in project_readme:\n            errors.append(f"docs/project/README.md missing canonical project narrative marker: {marker}")''',
    )


if __name__ == "__main__":
    main()
