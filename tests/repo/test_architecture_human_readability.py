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


def _base_doc(part_a: str, part_b: str) -> str:
    return (
        "## Part A — Architecture Narrative\n"
        f"{part_a}\n"
        "## Part B — Detailed Architecture Specification\n"
        f"{part_b}\n"
    )


def _rich_part_a(prefix: str = "") -> str:
    paragraphs: list[str] = []
    for index in range(1, 26):
        paragraphs.append(f"### Narrative topic {index}\n")
        paragraphs.append(
            (prefix if index == 1 else "")
            + "A human-first architecture narrative explains a concrete system problem, the reason for the boundary, "
            "the normal flow, failure consequences, recovery choices, ownership, and trade-offs in ordinary prose. "
            "It intentionally contains enough context that a senior engineer can understand the causal design before reading the specification.\n\n"
        )
        paragraphs.append(
            "The same topic is then connected to realistic operational behavior, including what changes when inputs become stale, "
            "which facts remain durable, what the system must not infer, and why a simpler alternative may be preferable when the extra mechanism has no measured value.\n\n"
        )
    return "".join(paragraphs)


def test_writing_model_accepts_substantial_narrative_part_a_and_engineering_part_b() -> None:
    document = _base_doc(
        _rich_part_a(),
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


def test_machine_markers_warn_without_blocking_when_narrative_is_substantial() -> None:
    module = _load()
    document = _base_doc(
        _rich_part_a("TARGET_ONLY UNKNOWN requirement_id values remain outside the narrative. "),
        "Contract, State, and Recovery define the engineering reference.",
    )
    assert module.verify_text(document) == []
    assert module.warnings_for_text(document)


def test_project_narrative_meets_current_depth_floor() -> None:
    verifier = _load()
    for filename, (min_chars, min_sections, min_paragraphs) in verifier.PROJECT_NARRATIVE_BASELINES.items():
        text = (REPO_ROOT / "docs/project" / filename).read_text(encoding="utf-8")
        assert verifier._nonspace_chars(text) >= min_chars, filename
        assert len(re.findall(r"(?m)^##+\s+", verifier._strip_non_prose_blocks(text))) >= min_sections, filename
        assert len(verifier._prose_paragraphs(text)) >= min_paragraphs, filename


def test_architecture_part_a_meets_current_depth_floor() -> None:
    verifier = _load()
    text = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    layers = verifier._split_layers(text)
    assert layers is not None
    part_a, _part_b = layers
    assert verifier._nonspace_chars(part_a) >= verifier.ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS
    assert len(verifier._prose_paragraphs(part_a)) >= verifier.ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS
    assert len(re.findall(r"(?m)^###\s+", part_a)) >= verifier.ARCHITECTURE_PART_A_MIN_SUBSECTIONS


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
