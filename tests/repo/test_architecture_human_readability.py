from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools/scripts/verify_architecture_human_readability.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_architecture_human_readability", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_canonical_markdown_and_modules_have_human_and_normative_layers() -> None:
    assert _load().verify() == []


def test_presentation_pair_remains_intact() -> None:
    assert (REPO_ROOT / "docs/architecture/architecture-views.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def _base_doc(part_a: str, part_b: str) -> str:
    return (
        "## Part A — Architecture Narrative\n"
        f"{part_a}\n"
        "## Part B — Detailed Architecture Specification\n"
        f"{part_b}\n"
    )


def test_writing_model_accepts_narrative_part_a_and_engineering_part_b() -> None:
    document = _base_doc(
        "Users need a clear path through the system, so the design explains the normal task flow and its boundaries.",
        "Contract, State, Ownership, and Recovery define the engineering reference.",
    )
    assert _load().verify_text(document) == []


def test_writing_model_rejects_missing_part_a() -> None:
    errors = _load().verify_text("## Part B — Detailed Architecture Specification\nContract")
    assert any("missing Part A" in error for error in errors)


def test_writing_model_rejects_missing_part_b() -> None:
    errors = _load().verify_text("## Part A — Architecture Narrative\nThe system serves a concrete user need.")
    assert any("missing Part B" in error for error in errors)


def test_writing_model_rejects_part_b_before_part_a() -> None:
    document = (
        "## Part B — Detailed Architecture Specification\nContract\n"
        "## Part A — Architecture Narrative\nThe system serves a concrete user need."
    )
    assert any("Part B must follow Part A" in error for error in _load().verify_text(document))


def test_writing_model_rejects_empty_part_a() -> None:
    document = _base_doc("", "Contract and Recovery")
    assert any("Part A must not be empty" in error for error in _load().verify_text(document))


def test_machine_markers_warn_without_blocking() -> None:
    module = _load()
    document = _base_doc(
        "TARGET_ONLY UNKNOWN requirement_id values remain outside the narrative.",
        "Contract, State, and Recovery define the engineering reference.",
    )
    assert module.verify_text(document) == []
    assert module.warnings_for_text(document)


def test_all_nine_module_part_a_sections_meet_current_depth_floor() -> None:
    verifier = _load()
    for filename in verifier.MODULE_FILES:
        text = (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        layers = verifier._split_module_layers(text)
        assert layers is not None, filename
        part_a, _part_b, _part_c = layers
        assert verifier._nonspace_chars(part_a) >= verifier.MODULE_PART_A_MIN_NONSPACE_CHARS, filename
        assert len(verifier._prose_paragraphs(part_a)) >= verifier.MODULE_PART_A_MIN_PROSE_PARAGRAPHS, filename
        assert len(__import__("re").findall(r"(?m)^###\s+", part_a)) >= verifier.MODULE_PART_A_MIN_SUBSECTIONS, filename
        assert "### 当前、目标与缺口" in part_a, filename
