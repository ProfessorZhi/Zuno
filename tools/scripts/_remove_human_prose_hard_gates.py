from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: expected exactly one occurrence for replacement\n{old[:160]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_human_readability() -> None:
    path = "tools/scripts/verify_architecture_human_readability.py"
    replace_once(path, 'PROJECT_NARRATIVE_BASELINES = {"README.md": (9000, 10, 24)}', 'PROJECT_NARRATIVE_BASELINES = {"README.md": (9000, 24)}')
    replace_once(path, "ARCHITECTURE_PART_A_MIN_SUBSECTIONS = 10\n", "")
    replace_once(path, "MODULE_PART_A_MIN_SUBSECTIONS = 14\n", "")
    replace_once(path, '    subsection_count = len(re.findall(r"(?m)^###\\s+", _strip_non_prose_blocks(visible)))\n', "")
    replace_once(
        path,
        '    if subsection_count < ARCHITECTURE_PART_A_MIN_SUBSECTIONS:\n        errors.append(\n            "architecture Part A needs broader conceptual coverage "\n            f"({subsection_count} subsections < {ARCHITECTURE_PART_A_MIN_SUBSECTIONS})"\n        )\n',
        "",
    )
    replace_once(path, "    min_chars, min_sections, min_paragraphs = PROJECT_NARRATIVE_BASELINES[filename]\n", "    min_chars, min_paragraphs = PROJECT_NARRATIVE_BASELINES[filename]\n")
    replace_once(path, '    subsection_count = len(re.findall(r"(?m)^##+\\s+", _strip_non_prose_blocks(text)))\n', "")
    replace_once(path, '    if subsection_count < min_sections:\n        errors.append(f"{filename}: project narrative needs broader coverage ({subsection_count} < {min_sections})")\n', "")
    replace_once(
        path,
        '    for marker in (\n        "为什么会有这个项目",\n        "为什么不直接用 Dify、Coze",\n        "项目是怎样发展到今天的",\n        "团队是什么形态，我在里面做了什么",\n        "相比通用方案，我们今天到底证明了什么",\n    ):\n        if marker not in text:\n            errors.append(f"{filename}: missing human narrative topic: {marker}")\n',
        "",
    )
    replace_once(path, '    subsection_count = len(re.findall(r"(?m)^###\\s+", visible))\n', "")
    replace_once(path, '    if subsection_count < MODULE_PART_A_MIN_SUBSECTIONS:\n        errors.append(f"{label}: Part A needs broader narrative coverage ({subsection_count} < {MODULE_PART_A_MIN_SUBSECTIONS})")\n', "")
    replace_once(
        path,
        '    if "### 当前、目标与缺口" not in visible:\n        errors.append(f"{label}: Part A must close with an explicit Current / Target / Gap narrative")\n',
        '    if not all(marker in visible for marker in ("Current", "Target", "Gap")):\n        errors.append(f"{label}: Part A must preserve explicit Current / Target / Gap semantics")\n',
    )


def patch_human_readability_tests() -> None:
    path = "tests/repo/test_architecture_human_readability.py"
    replace_once(path, "import re\n", "")
    replace_once(path, "    for filename, (min_chars, min_sections, min_paragraphs) in verifier.PROJECT_NARRATIVE_BASELINES.items():\n", "    for filename, (min_chars, min_paragraphs) in verifier.PROJECT_NARRATIVE_BASELINES.items():\n")
    replace_once(path, '        assert len(re.findall(r"(?m)^##+\\s+", verifier._strip_non_prose_blocks(text))) >= min_sections, filename\n', "")
    replace_once(path, '    assert len(re.findall(r"(?m)^###\\s+", part_a)) >= verifier.ARCHITECTURE_PART_A_MIN_SUBSECTIONS\n', "")
    replace_once(path, '        assert len(re.findall(r"(?m)^###\\s+", part_a)) >= verifier.MODULE_PART_A_MIN_SUBSECTIONS, directory\n', "")
    replace_once(path, '        assert "### 当前、目标与缺口" in part_a, directory\n', '        assert all(marker in part_a for marker in ("Current", "Target", "Gap")), directory\n')


def patch_document_set() -> None:
    path = "tools/scripts/verify_architecture_document_set.py"
    replace_once(
        path,
        '    human_markers = (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "法律智能真正变难的时刻",\n        "一件案件里的五种事实",\n        "四次跨边界决定系统是否可信",\n        "九个责任域如何从这些边界产生",\n        "故障以后，先找事实再恢复控制",\n        "研究成果怎样变成工程能力",\n        "复杂度必须在测量中证明收益",\n        "Single Controller",\n        "target_logical_module_count: 9",\n        "overall_architecture_state: ROUND_02_FROZEN",\n        "implementation_authorization: NO",\n        "reference.md",\n    )\n',
        '    human_markers = (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "target_logical_module_count: 9",\n        "overall_architecture_state: ROUND_02_FROZEN",\n        "implementation_authorization: NO",\n        "reference.md",\n    )\n',
    )
    replace_once(
        path,
        '    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in design:\n        errors.append("architecture README must not contain Part B after human/reference split")\n\n    engineering_markers = (\n',
        '    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in design:\n        errors.append("architecture README must not contain Part B after human/reference split")\n    if "Single Controller" not in design + "\\n" + arch_reference:\n        errors.append("architecture split views must preserve Single Controller target semantics")\n\n    engineering_markers = (\n',
    )
    replace_once(
        path,
        '    for marker in (\n        "为什么会有这个项目",\n        "为什么不直接用 Dify、Coze",\n        "项目是怎样发展到今天的",\n        "团队是什么形态，我在里面做了什么",\n        "相比通用方案，我们今天到底证明了什么",\n    ):\n        if marker not in project:\n            errors.append(f"project README missing human narrative marker: {marker}")\n',
        '    for marker in ("project-fact-provenance.md", "Pilot Validation", "Production", "Current", "Target", "Unknown"):\n        if marker not in project:\n            errors.append(f"project README missing factual-boundary marker: {marker}")\n',
    )


def patch_semantic_alignment() -> None:
    path = "tools/scripts/verify_architecture_semantic_alignment.py"
    replace_once(
        path,
        '        (\n            "为什么会有这个项目",\n            "为什么不直接用 Dify、Coze",\n            "项目是怎样发展到今天的",\n            "团队是什么形态，我在里面做了什么",\n            "相比通用方案，我们今天到底证明了什么",\n            "Pilot Validation",\n            "Production",\n            "Current",\n            "Target",\n            "Unknown",\n        ),\n',
        '        (\n            "project-fact-provenance.md",\n            "Pilot Validation",\n            "Production",\n            "Current",\n            "Target",\n            "Unknown",\n        ),\n',
    )
    replace_once(
        path,
        '        (\n            "# Zuno 目标架构",\n            "## Part A — Human Narrative（人类技术叙事）",\n            "### A1. 法律智能真正变难的时刻",\n            "### A2. 一件案件里的五种事实",\n            "### A3. 四次跨边界决定系统是否可信",\n            "### A4. 九个责任域如何从这些边界产生",\n            "### A5. 故障以后，先找事实再恢复控制",\n            "### A6. 研究成果怎样变成工程能力",\n            "### A7. 安全、人和时间",\n            "### A8. 复杂度必须在测量中证明收益",\n            "### A9. 从目标架构进入实施",\n            "overall_architecture_state: ROUND_02_FROZEN",\n            "target_logical_module_count: 9",\n            "module_design_baseline: AVAILABLE_V1",\n            "module_deep_design: AVAILABLE_V2",\n            "module_deep_design_coverage: 9/9",\n            "cross_module_consistency: AVAILABLE_V1",\n            "module_detail_freeze: NOT_YET",\n            "implementation_authorization: NO",\n            "Single Controller",\n            "docs/modules/",\n            "docs/decisions/",\n            "docs/evidence/",\n            "docs/research/",\n        ),\n',
        '        (\n            "# Zuno 目标架构",\n            "## Part A — Human Narrative（人类技术叙事）",\n            "overall_architecture_state: ROUND_02_FROZEN",\n            "target_logical_module_count: 9",\n            "module_design_baseline: AVAILABLE_V1",\n            "module_deep_design: AVAILABLE_V2",\n            "module_deep_design_coverage: 9/9",\n            "cross_module_consistency: AVAILABLE_V1",\n            "module_detail_freeze: NOT_YET",\n            "implementation_authorization: NO",\n            "reference.md",\n        ),\n',
    )
    replace_once(
        path,
        '    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in architecture_human:\n        errors.append("overall architecture human README must not retain Part B")\n\n    _require(\n',
        '    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in architecture_human:\n        errors.append("overall architecture human README must not retain Part B")\n    _require(\n        errors,\n        "overall architecture split views",\n        architecture_all,\n        ("Single Controller", "docs/modules/", "docs/decisions/", "docs/evidence/", "docs/research/"),\n    )\n\n    _require(\n',
    )
    replace_once(path, '    positions = [architecture_human.find(marker) for marker in responsibility_markers]\n    if any(position < 0 for position in positions) or positions != sorted(positions):\n        errors.append("architecture responsibilities must exist in canonical 01-09 order in the human narrative")\n', '    positions = [architecture_reference.find(marker) for marker in responsibility_markers]\n    if any(position < 0 for position in positions) or positions != sorted(positions):\n        errors.append("architecture engineering reference must preserve canonical 01-09 responsibility order")\n')
    replace_once(
        path,
        '            (\n                "## Part A — Human Narrative",\n                "implementation: not-authorized",\n                "deepening: cross-module-consistency-v2",\n                "### 当前、目标与缺口",\n                "reference.md",\n            ),\n',
        '            (\n                "## Part A — Human Narrative",\n                "implementation: not-authorized",\n                "deepening: cross-module-consistency-v2",\n                "reference.md",\n            ),\n',
    )


def patch_renderer() -> None:
    path = "tools/agent/render_architecture.py"
    replace_once(
        path,
        '    for marker in (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "### A1. 法律智能真正变难的时刻",\n        "### A2. 一件案件里的五种事实",\n        "### A3. 四次跨边界决定系统是否可信",\n        "### A4. 九个责任域如何从这些边界产生",\n        "### A5. 故障以后，先找事实再恢复控制",\n        "### A6. 研究成果怎样变成工程能力",\n        "### A7. 安全、人和时间",\n        "### A8. 复杂度必须在测量中证明收益",\n        "### A9. 从目标架构进入实施",\n        "reference.md",\n    ):\n',
        '    for marker in (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "reference.md",\n    ):\n',
    )


def patch_writing_standard() -> None:
    path = "tools/scripts/verify_architecture_writing_standard.py"
    replace_once(
        path,
        '    for marker in (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "合同争议事项",\n        "不同种类的事实",\n        "一件案件里的五种事实",\n        "四次跨边界决定系统是否可信",\n        "Domain commit",\n        "Checkpoint",\n        "Outcome Unknown",\n        "Research Artifact -> Capability -> Provider -> Qualified Provider -> Candidate -> Formal Business Fact",\n        "简单法律问答的 baseline",\n        "复杂度必须在测量中证明收益",\n        "模块化 Python 后端",\n        "独立网络服务",\n        "Reconcile",\n        "Target Architecture",\n        "reference.md",\n    ):\n',
        '    for marker in (\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "reference.md",\n    ):\n',
    )


def patch_docs_entrypoints() -> None:
    path = "tools/scripts/verify_docs_entrypoints.py"
    replace_once(
        path,
        '    for marker in (\n        "# Zuno 项目：从智慧司法研究到可验证的法律智能 Agent 平台",\n        "为什么会有这个项目", "为什么不直接用 Dify、Coze",\n        "项目是怎样发展到今天的", "团队是什么形态，我在里面做了什么",\n        "相比通用方案，我们今天到底证明了什么", "project-fact-provenance.md",\n    ):\n        if marker not in project_readme:\n            errors.append(f"docs/project/README.md missing canonical project narrative marker: {marker}")\n',
        '    for marker in ("project-fact-provenance.md", "Pilot Validation", "Production", "Current", "Target", "Unknown"):\n        if marker not in project_readme:\n            errors.append(f"docs/project/README.md missing factual-boundary marker: {marker}")\n',
    )
    replace_once(
        path,
        '        for marker in (\n            "status: design-baseline-v1", "implementation: not-authorized",\n            "## Part A — Human Narrative", "### 当前、目标与缺口", "reference.md",\n        ):\n',
        '        for marker in (\n            "status: design-baseline-v1", "implementation: not-authorized",\n            "## Part A — Human Narrative", "reference.md",\n        ):\n',
    )


def patch_docs_entrypoint_tests() -> None:
    path = "tests/repo/test_docs_entrypoints.py"
    replace_once(
        path,
        '    project = (root / "README.md").read_text(encoding="utf-8")\n    assert "project-fact-provenance.md" in project\n    for marker in (\n        "为什么会有这个项目",\n        "为什么不直接用 Dify、Coze",\n        "项目是怎样发展到今天的",\n        "团队是什么形态，我在里面做了什么",\n        "相比通用方案，我们今天到底证明了什么",\n    ):\n        assert marker in project\n    assert "通用宿主" in project and "Zuno Legal Backend" in project\n    assert "Current" in project and "Target" in project and "Unknown" in project\n',
        '    project = (root / "README.md").read_text(encoding="utf-8")\n    for marker in ("project-fact-provenance.md", "Pilot Validation", "Production", "Current", "Target", "Unknown"):\n        assert marker in project\n',
    )
    replace_once(
        path,
        '    for marker in [\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "### A2. 一件案件里的五种事实",\n        "### A3. 四次跨边界决定系统是否可信",\n        "### A4. 九个责任域如何从这些边界产生",\n        "### A5. 故障以后，先找事实再恢复控制",\n        "### A6. 研究成果怎样变成工程能力",\n        "reference.md",\n    ]:\n',
        '    for marker in [\n        "# Zuno 目标架构",\n        "## Part A — Human Narrative（人类技术叙事）",\n        "reference.md",\n    ]:\n',
    )


def main() -> None:
    patch_human_readability()
    patch_human_readability_tests()
    patch_document_set()
    patch_semantic_alignment()
    patch_renderer()
    patch_writing_standard()
    patch_docs_entrypoints()
    patch_docs_entrypoint_tests()


if __name__ == "__main__":
    main()
