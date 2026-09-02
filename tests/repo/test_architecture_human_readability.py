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


def _rich_architecture(prefix: str = "") -> str:
    parts = ["# Zuno 目标架构\n\n"]
    for index in range(1, 13):
        parts.append(f"## {index}. Architecture concept {index}\n\n")
        for paragraph in range(3):
            lead = prefix if index == 1 and paragraph == 0 else ""
            parts.append(
                lead
                + "A conceptual target architecture explains a concrete system problem, the durable fact that must be protected, "
                "the owner responsible for that fact, the normal flow, realistic failure consequences, recovery choices and trade-offs. "
                "The prose is intentionally complete enough that an engineer can understand why the boundary exists before reading module contracts. "
                "A simpler design remains valid whenever the stronger mechanism has no demonstrated need, and implementation details stay outside the overall architecture.\n\n"
            )
    return "".join(parts)


def test_writing_model_accepts_substantial_conceptual_architecture() -> None:
    assert _load().verify_text(_rich_architecture()) == []


def test_writing_model_rejects_missing_target_architecture_title() -> None:
    errors = _load().verify_text("## 1. Design\nThe system serves a concrete user need.")
    assert any("missing Zuno target architecture title" in error for error in errors)


def test_writing_model_rejects_embedded_part_b_specification() -> None:
    document = _rich_architecture() + "\n## Part B — Detailed Architecture Specification\nContract\n"
    assert any("must remain conceptual" in error for error in _load().verify_text(document))


def test_writing_model_rejects_thin_architecture() -> None:
    document = "# Zuno 目标架构\n\n## 1. Design\n\nA short explanation of the system.\n"
    errors = _load().verify_text(document)
    assert any(
        "too thin" in error
        or "broader conceptual coverage" in error
        or "explanatory prose" in error
        for error in errors
    )


def test_machine_markers_warn_without_blocking_when_narrative_is_substantial() -> None:
    module = _load()
    document = _rich_architecture(
        "TARGET_ONLY CURRENT_STATE MODULE_STATE NOT_READY UNKNOWN requirement_id canonical_question values remain hidden from the reader. "
    )
    assert module.verify_text(document) == []
    assert module.warnings_for_text(document)


def test_project_narrative_meets_regression_floor() -> None:
    verifier = _load()
    for filename, (min_chars, min_sections, min_paragraphs) in verifier.PROJECT_NARRATIVE_BASELINES.items():
        text = (REPO_ROOT / "docs/project" / filename).read_text(encoding="utf-8")
        assert verifier._nonspace_chars(text) >= min_chars, filename
        assert len(re.findall(r"(?m)^##+\s+", verifier._strip_non_prose_blocks(text))) >= min_sections, filename
        assert len(verifier._prose_paragraphs(text)) >= min_paragraphs, filename


def test_architecture_meets_conceptual_depth_floor() -> None:
    verifier = _load()
    text = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert verifier._nonspace_chars(text) >= verifier.ARCHITECTURE_MIN_NONSPACE_CHARS
    assert len(verifier._prose_paragraphs(text)) >= verifier.ARCHITECTURE_MIN_PROSE_PARAGRAPHS
    assert len(re.findall(r"(?m)^##\s+", verifier._strip_non_prose_blocks(text))) >= verifier.ARCHITECTURE_MIN_SECTIONS


def test_all_nine_module_part_a_sections_meet_current_depth_floor() -> None:
    verifier = _load()
    for filename in verifier.MODULE_FILES:
        text = (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        layers = verifier._split_module_layers(text)
        assert layers is not None, filename
        part_a, _part_b, _part_c = layers
        assert verifier._nonspace_chars(part_a) >= verifier.MODULE_PART_A_MIN_NONSPACE_CHARS, filename
        assert len(verifier._prose_paragraphs(part_a)) >= verifier.MODULE_PART_A_MIN_PROSE_PARAGRAPHS, filename
        assert len(re.findall(r"(?m)^###\s+", part_a)) >= verifier.MODULE_PART_A_MIN_SUBSECTIONS, filename
        assert "### 当前、目标与缺口" in part_a, filename
