from __future__ import annotations

import importlib.util
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools/scripts/verify_architecture_human_readability.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_architecture_human_readability", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_project_architecture_and_modules_meet_human_readability_contracts() -> None:
    assert _load().verify() == []


def test_presentation_pair_remains_intact() -> None:
    assert (REPO_ROOT / "docs/architecture/architecture-views.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def _rich_human(prefix: str = "") -> str:
    parts = [
        "# Zuno 目标架构\n\n",
        "## Part A — Human Narrative（人类技术叙事）\n\n",
    ]
    for index in range(1, 13):
        parts.append(f"### A{index}. Architecture concept {index}\n\n")
        for paragraph in range(3):
            lead = prefix if index == 1 and paragraph == 0 else ""
            parts.append(
                lead
                + "A conceptual target architecture explains a concrete system problem, the durable fact that must be protected, "
                "the owner responsible for that fact, the normal flow, realistic failure consequences, recovery choices and trade-offs. "
                "The prose is intentionally complete enough that an engineer can understand why the boundary exists before reading module contracts. "
                "A simpler design remains valid whenever the stronger mechanism has no demonstrated need, and implementation detail stays outside Part A.\n\n"
            )
    parts.append("---\n\nEngineering reference: [`reference.md`](reference.md).\n")
    return "".join(parts)


def _rich_reference(body: str | None = None) -> str:
    return (
        "# Overall Architecture Engineering Reference\n\n"
        "## Part B — Engineering / Agent Reference（工程 / Agent 参考）\n\n"
        + (
            body
            or (
                "### B1. Scope / Global Invariants\n\n"
                "Owner, Authority, Completion Proof, Recovery and Current/Target are indexed here for machine consumption.\n"
            )
        )
    )


def test_writing_model_accepts_substantial_split_architecture() -> None:
    verifier = _load()
    assert verifier.verify_architecture_human(_rich_human()) == []
    assert verifier.verify_engineering_reference(_rich_reference(), "architecture/reference.md", module=False) == []


def test_writing_model_rejects_missing_target_architecture_title() -> None:
    errors = _load().verify_architecture_human(
        "## Part A — Human Narrative\nA concrete user need.\n"
    )
    assert any("missing Zuno target architecture title" in error for error in errors)


def test_writing_model_rejects_part_b_inside_human_readme() -> None:
    document = _rich_human() + "\n## Part B — Engineering / Agent Reference\nOwner.\n"
    errors = _load().verify_architecture_human(document)
    assert any("must not contain Part B" in error for error in errors)


def test_engineering_reference_requires_part_b() -> None:
    errors = _load().verify_engineering_reference(
        "# Engineering reference without the required section\n",
        "architecture/reference.md",
        module=False,
    )
    assert any("missing Part B Engineering / Agent Reference" in error for error in errors)


def test_machine_dense_reference_does_not_reduce_part_a_readability() -> None:
    verifier = _load()
    human = _rich_human()
    reference = _rich_reference(
        "### B1. Scope / Global Invariants\n\n"
        "TARGET_ONLY CURRENT_STATE MODULE_STATE NOT_READY UNKNOWN requirement_id canonical_question.\n"
        "### B2. Authority / Ownership Matrix\n\nOwner -> Authority -> Receipt -> Recovery.\n"
    )
    assert verifier.verify_architecture_human(human) == []
    assert verifier.verify_engineering_reference(reference, "architecture/reference.md", module=False) == []
    assert verifier.warning_for_human(human, "architecture README") == []


def test_writing_model_rejects_thin_architecture_part_a() -> None:
    document = (
        "# Zuno 目标架构\n\n"
        "## Part A — Human Narrative（人类技术叙事）\n\n"
        "### A1. Design\n\nA short explanation of the system.\n"
    )
    errors = _load().verify_architecture_human(document)
    assert any(
        "too thin" in error
        or "broader conceptual coverage" in error
        or "explanatory prose" in error
        for error in errors
    )


def test_machine_markers_warn_without_blocking_when_part_a_is_substantial() -> None:
    verifier = _load()
    document = _rich_human(
        "TARGET_ONLY CURRENT_STATE MODULE_STATE NOT_READY UNKNOWN requirement_id canonical_question values remain hidden from the reader. "
    )
    assert verifier.verify_architecture_human(document) == []
    assert verifier.warning_for_human(document, "architecture README")


def test_project_narrative_meets_regression_floor() -> None:
    verifier = _load()
    for filename, (min_chars, min_sections, min_paragraphs) in verifier.PROJECT_NARRATIVE_BASELINES.items():
        text = (REPO_ROOT / "docs/project" / filename).read_text(encoding="utf-8")
        assert verifier._nonspace_chars(text) >= min_chars, filename
        assert len(re.findall(r"(?m)^##+\s+", verifier._strip_non_prose_blocks(text))) >= min_sections, filename
        assert len(verifier._prose_paragraphs(text)) >= min_paragraphs, filename


def test_architecture_part_a_meets_conceptual_depth_floor() -> None:
    verifier = _load()
    text = (REPO_ROOT / "docs/architecture/README.md").read_text(encoding="utf-8")
    assert verifier.verify_architecture_human(text) == []
    part_a = text[text.index(verifier.ARCHITECTURE_PART_A_HEADING) + len(verifier.ARCHITECTURE_PART_A_HEADING):]
    assert verifier._nonspace_chars(part_a) >= verifier.ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS
    assert len(verifier._prose_paragraphs(part_a)) >= verifier.ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS
    assert len(re.findall(r"(?m)^###\s+", part_a)) >= verifier.ARCHITECTURE_PART_A_MIN_SUBSECTIONS

    reference = (REPO_ROOT / "docs/architecture/reference.md").read_text(encoding="utf-8")
    assert verifier.verify_engineering_reference(reference, "docs/architecture/reference.md", module=False) == []


def test_all_nine_module_part_a_sections_meet_current_depth_floor() -> None:
    verifier = _load()
    for directory in verifier.MODULE_DIRS:
        human = (REPO_ROOT / "docs/modules" / directory / "README.md").read_text(encoding="utf-8")
        reference = (REPO_ROOT / "docs/modules" / directory / "reference.md").read_text(encoding="utf-8")
        assert verifier.verify_module_human(human, f"{directory}/README.md") == []
        assert verifier.verify_engineering_reference(reference, f"{directory}/reference.md", module=True) == []

        part_a = human[human.index(verifier.MODULE_PART_A_HEADING) + len(verifier.MODULE_PART_A_HEADING):]
        assert verifier._nonspace_chars(part_a) >= verifier.MODULE_PART_A_MIN_NONSPACE_CHARS, directory
        assert len(verifier._prose_paragraphs(part_a)) >= verifier.MODULE_PART_A_MIN_PROSE_PARAGRAPHS, directory
        assert len(re.findall(r"(?m)^###\s+", part_a)) >= verifier.MODULE_PART_A_MIN_SUBSECTIONS, directory
        assert "### 当前、目标与缺口" in part_a, directory
