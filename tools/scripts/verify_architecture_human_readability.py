from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [ROOT / "docs/architecture/architecture.md"]
ARCHITECTURE_README = ROOT / "docs/architecture/README.md"
PROJECT_ROOT = ROOT / "docs/project"
MODULES_ROOT = ROOT / "docs/modules"
ROUND_01 = ROOT / "docs/maintenance/history/red-blue/manual-round-01-overall-architecture.md"
ROUND_02 = ROOT / "docs/maintenance/history/red-blue/manual-round-02-overall-architecture-freeze-review.md"

MODULE_FILES = (
    "01-application-integration.md",
    "02-legal-domain-work-product.md",
    "03-knowledge-evidence.md",
    "04-agent-runtime-control.md",
    "05-capability-skill.md",
    "06-tool-runtime-effects.md",
    "07-model-gateway.md",
    "08-security-governance.md",
    "09-observability-evaluation.md",
)

# Regression floors only. They prevent human-facing documents from collapsing into thin
# index/spec sheets. They intentionally do not reward padding or pretend to score prose quality.
PROJECT_NARRATIVE_BASELINES = {
    "project.md": (9000, 10, 24),
}

ARCHITECTURE_PART_A_HEADING = "## Part A — Human Narrative"
ARCHITECTURE_PART_B_HEADING = "## Part B — Engineering / Agent Reference"
ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS = 8000
ARCHITECTURE_PART_A_MIN_SUBSECTIONS = 10
ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS = 28

MODULE_PART_A_HEADING = "## Part A — Human Narrative"
MODULE_PART_B_HEADING = "## Part B — Engineering / Agent Reference"
MODULE_PART_C_HEADING = "## Part C — Cross-Module Consistency"
MODULE_PART_A_MIN_NONSPACE_CHARS = 5500
MODULE_PART_A_MIN_SUBSECTIONS = 14
MODULE_PART_A_MIN_PROSE_PARAGRAPHS = 18

_MACHINE_TOKEN_RE = re.compile(
    r"(?:\b(?:TARGET|CURRENT|MODULE|NOT|UNKNOWN)_[A-Z0-9_]+\b|"
    r"\bUNKNOWN\b|"
    r"\b(?:ARCH|RC|FACT)-[A-Z0-9_-]+\b|"
    r"\b(?:requirement_id|source_boundary|canonical_[a-z_]+)\b)",
    re.IGNORECASE,
)


def _split_architecture_layers(text: str) -> tuple[str, str] | None:
    if ARCHITECTURE_PART_A_HEADING not in text or ARCHITECTURE_PART_B_HEADING not in text:
        return None
    a_start = text.index(ARCHITECTURE_PART_A_HEADING) + len(ARCHITECTURE_PART_A_HEADING)
    b_pos = text.index(ARCHITECTURE_PART_B_HEADING)
    if a_start > b_pos:
        return None
    b_start = b_pos + len(ARCHITECTURE_PART_B_HEADING)
    return text[a_start:b_pos], text[b_start:]


def _split_module_layers(text: str) -> tuple[str, str, str] | None:
    if any(
        heading not in text
        for heading in (MODULE_PART_A_HEADING, MODULE_PART_B_HEADING, MODULE_PART_C_HEADING)
    ):
        return None
    a_start = text.index(MODULE_PART_A_HEADING) + len(MODULE_PART_A_HEADING)
    b_pos = text.index(MODULE_PART_B_HEADING)
    c_pos = text.index(MODULE_PART_C_HEADING)
    if not (a_start <= b_pos < c_pos):
        return None
    b_start = b_pos + len(MODULE_PART_B_HEADING)
    c_start = c_pos + len(MODULE_PART_C_HEADING)
    return text[a_start:b_pos], text[b_start:c_pos], text[c_start:]


def _strip_non_prose_blocks(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return text


def _prose_paragraphs(text: str) -> list[str]:
    text = _strip_non_prose_blocks(text)
    paragraphs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if not current:
            return
        value = " ".join(line.strip() for line in current).strip()
        current.clear()
        if len(value) >= 40:
            paragraphs.append(value)

    for line in text.splitlines() + [""]:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if stripped.startswith(("#", "|", "- ", "* ", "> ")):
            flush()
            continue
        if re.match(r"^\d+\.\s", stripped):
            flush()
            continue
        current.append(line)
    return paragraphs


def _has_narrative_prose(text: str) -> bool:
    return bool(_prose_paragraphs(text))


def _nonspace_chars(text: str) -> int:
    visible = _strip_non_prose_blocks(text)
    return len(re.sub(r"\s+", "", visible))


def verify_text(text: str) -> list[str]:
    errors: list[str] = []
    if "# Zuno 目标架构" not in text:
        errors.append("missing Zuno target architecture title")
        return errors

    layers = _split_architecture_layers(text)
    if layers is None:
        return [
            "overall architecture must contain ordered Part A Human Narrative and "
            "Part B Engineering / Agent Reference"
        ]
    part_a, part_b = layers
    if not part_b.strip():
        errors.append("overall architecture Part B must not be empty")

    # Human readability is deliberately measured on Part A only. Part B is expected to
    # be dense and machine-oriented; semantic validators check its engineering coverage.
    if not _has_narrative_prose(part_a):
        errors.append("architecture Part A must contain explanatory prose")
        return errors

    nonspace_chars = _nonspace_chars(part_a)
    subsection_count = len(re.findall(r"(?m)^###\s+", _strip_non_prose_blocks(part_a)))
    prose_paragraph_count = len(_prose_paragraphs(part_a))
    if nonspace_chars < ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS:
        errors.append(
            "architecture Part A is too thin for the conceptual design baseline "
            f"({nonspace_chars} non-space chars < {ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS})"
        )
    if subsection_count < ARCHITECTURE_PART_A_MIN_SUBSECTIONS:
        errors.append(
            "architecture Part A needs broader conceptual coverage "
            f"({subsection_count} subsections < {ARCHITECTURE_PART_A_MIN_SUBSECTIONS})"
        )
    if prose_paragraph_count < ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS:
        errors.append(
            "architecture Part A must contain substantial explanatory prose "
            f"({prose_paragraph_count} paragraphs < {ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS})"
        )
    return errors


def verify_project_text(text: str, filename: str) -> list[str]:
    errors: list[str] = []
    baseline = PROJECT_NARRATIVE_BASELINES.get(filename)
    if baseline is None:
        return errors

    min_chars, min_sections, min_paragraphs = baseline
    nonspace_chars = _nonspace_chars(text)
    subsection_count = len(re.findall(r"(?m)^##+\s+", _strip_non_prose_blocks(text)))
    prose_paragraph_count = len(_prose_paragraphs(text))

    if nonspace_chars < min_chars:
        errors.append(
            f"{filename}: project narrative is too thin for its regression baseline "
            f"({nonspace_chars} non-space chars < {min_chars})"
        )
    if subsection_count < min_sections:
        errors.append(
            f"{filename}: project narrative needs broader coverage "
            f"({subsection_count} sections < {min_sections})"
        )
    if prose_paragraph_count < min_paragraphs:
        errors.append(
            f"{filename}: project narrative must contain explanatory prose, not mainly tables/lists "
            f"({prose_paragraph_count} prose paragraphs < {min_paragraphs})"
        )
    for marker in (
        "为什么会有这个项目",
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
    ):
        if marker not in text:
            errors.append(f"{filename}: missing human narrative topic: {marker}")
    return errors


def verify_module_text(text: str, filename: str) -> list[str]:
    errors: list[str] = []
    layers = _split_module_layers(text)
    if layers is None:
        return [
            f"{filename}: module must contain ordered Part A Human Narrative, "
            "Part B Engineering Reference and Part C Cross-Module Consistency"
        ]

    part_a, part_b, part_c = layers
    nonspace_chars = _nonspace_chars(part_a)
    subsection_count = len(re.findall(r"(?m)^###\s+", part_a))
    prose_paragraph_count = len(_prose_paragraphs(part_a))

    if nonspace_chars < MODULE_PART_A_MIN_NONSPACE_CHARS:
        errors.append(
            f"{filename}: Part A is too thin for the current human-first baseline "
            f"({nonspace_chars} non-space chars < {MODULE_PART_A_MIN_NONSPACE_CHARS})"
        )
    if subsection_count < MODULE_PART_A_MIN_SUBSECTIONS:
        errors.append(
            f"{filename}: Part A needs broader narrative coverage "
            f"({subsection_count} subsections < {MODULE_PART_A_MIN_SUBSECTIONS})"
        )
    if prose_paragraph_count < MODULE_PART_A_MIN_PROSE_PARAGRAPHS:
        errors.append(
            f"{filename}: Part A must contain substantial explanatory prose, not mainly tables/lists "
            f"({prose_paragraph_count} paragraphs < {MODULE_PART_A_MIN_PROSE_PARAGRAPHS})"
        )
    if "### 当前、目标与缺口" not in part_a:
        errors.append(f"{filename}: Part A must close with an explicit Current / Target / Gap narrative")
    if not part_b.strip():
        errors.append(f"{filename}: Part B must not be empty")
    if not part_c.strip():
        errors.append(f"{filename}: Part C must not be empty")
    return errors


def warnings_for_text(text: str) -> list[str]:
    layers = _split_architecture_layers(text)
    visible = _strip_non_prose_blocks(layers[0] if layers is not None else text)
    matches = _MACHINE_TOKEN_RE.findall(visible)
    if len(matches) < 6:
        return []
    unique = sorted(set(matches), key=str.casefold)
    preview = ", ".join(unique[:8])
    if len(unique) > 8:
        preview += ", …"
    return [
        "READABILITY_WARNING: architecture Part A contains many machine-oriented markers "
        f"({preview}); human review is still required."
    ]


def warnings_for_project_text(text: str) -> list[str]:
    visible = _strip_non_prose_blocks(text)
    matches = _MACHINE_TOKEN_RE.findall(visible)
    if len(matches) < 6:
        return []
    unique = sorted(set(matches), key=str.casefold)
    preview = ", ".join(unique[:8])
    if len(unique) > 8:
        preview += ", …"
    return [
        "READABILITY_WARNING: project narrative contains many machine-oriented markers "
        f"({preview}); human review is still required."
    ]


def _verify_supporting_boundaries(errors: list[str]) -> None:
    if not ARCHITECTURE_README.exists():
        errors.append("missing docs/architecture/README.md")
    else:
        readme = ARCHITECTURE_README.read_text(encoding="utf-8")
        for marker in (
            "architecture.md",
            "architecture-views.md",
            "architecture.html",
            "Part A — Human Narrative",
            "Part B — Engineering / Agent Reference",
        ):
            if marker not in readme:
                errors.append(f"architecture README missing entry or layer marker: {marker}")

    architecture = CANONICAL[0]
    if architecture.exists():
        text = architecture.read_text(encoding="utf-8")
        gate_open = bool(
            re.search(
                r"(?im)^(?:module_decomposition_gate|MODULE_DECOMPOSITION_GATE)\s*[:=]\s*OPEN\b",
                text,
            )
        )
        module_docs = [path for path in MODULES_ROOT.glob("*.md") if path.name.lower() != "readme.md"]
        if not gate_open and module_docs:
            errors.append("module decomposition gate is closed but module documents exist")

    archive_requirements = {
        ROUND_01: ("STAGE A", "STAGE B", "STAGE C", "STAGE D", "STAGE E"),
        ROUND_02: (
            "## Q1 —",
            "## A1 —",
            "## R1 —",
            "## Q32 —",
            "## A32 —",
            "## R32 —",
            "## Q33 —",
            "## Q38 —",
        ),
    }
    for path, markers in archive_requirements.items():
        if not path.exists():
            errors.append(f"missing required history archive: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(ROOT)} missing archive marker: {marker}")


def verify() -> list[str]:
    errors: list[str] = []
    for path in CANONICAL:
        if not path.exists():
            errors.append(f"missing canonical Markdown: {path.relative_to(ROOT)}")
            continue
        errors.extend(
            f"{path.relative_to(ROOT)}: {error}"
            for error in verify_text(path.read_text(encoding="utf-8"))
        )

    for filename in PROJECT_NARRATIVE_BASELINES:
        path = PROJECT_ROOT / filename
        if not path.exists():
            errors.append(f"missing canonical project narrative: {path.relative_to(ROOT)}")
            continue
        errors.extend(verify_project_text(path.read_text(encoding="utf-8"), filename))

    for filename in MODULE_FILES:
        path = MODULES_ROOT / filename
        if not path.exists():
            errors.append(f"missing canonical module narrative: {path.relative_to(ROOT)}")
            continue
        errors.extend(verify_module_text(path.read_text(encoding="utf-8"), filename))

    _verify_supporting_boundaries(errors)
    views = ROOT / "docs/architecture/architecture-views.md"
    html = ROOT / "docs/architecture/architecture.html"
    if not views.exists() or not html.exists():
        errors.append("architecture diagram presentation pair must remain present")
    elif 'fetch("./architecture-views.md")' not in html.read_text(encoding="utf-8"):
        errors.append("architecture.html must continue to consume architecture-views.md")
    for forbidden in ROOT.glob("docs/**/*-human.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    for forbidden in ROOT.glob("docs/**/*-spec.md"):
        errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    warnings: list[str] = []
    for path in CANONICAL:
        if path.exists():
            warnings.extend(warnings_for_text(path.read_text(encoding="utf-8")))
    for filename in PROJECT_NARRATIVE_BASELINES:
        path = PROJECT_ROOT / filename
        if path.exists():
            warnings.extend(
                f"{filename}: {warning}"
                for warning in warnings_for_project_text(path.read_text(encoding="utf-8"))
            )
    for warning in warnings:
        print(warning, file=sys.stderr)
    print("project, architecture and module human readability structural verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
