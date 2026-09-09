from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH_HUMAN = ROOT / "docs/architecture/README.md"
ARCH_REFERENCE = ROOT / "docs/architecture/reference.md"
PROJECT_ROOT = ROOT / "docs/project"
MODULES_ROOT = ROOT / "docs/modules"
ROUND_01 = ROOT / "docs/red-blue/archive/legacy/manual-round-01-overall-architecture.md"
ROUND_02 = ROOT / "docs/red-blue/archive/legacy/manual-round-02-overall-architecture-freeze-review.md"

MODULE_DIRS = (
    "application",
    "domain",
    "knowledge",
    "runtime",
    "capability",
    "effects",
    "model-gateway",
    "security",
    "evaluation",
)

# Regression floors only. They prevent human-facing documents from collapsing into thin
# index/spec sheets. They intentionally do not reward padding or pretend to score prose quality.
PROJECT_NARRATIVE_BASELINES = {"README.md": (9000, 24)}
ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS = 8000
ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS = 28
MODULE_PART_A_MIN_NONSPACE_CHARS = 5500
MODULE_PART_A_MIN_PROSE_PARAGRAPHS = 18

ARCHITECTURE_PART_A_HEADING = "## Part A — Human Narrative"
ARCHITECTURE_PART_B_HEADING = "## Part B — Engineering / Agent Reference"
MODULE_PART_A_HEADING = "## Part A — Human Narrative"
MODULE_PART_B_HEADING = "## Part B — Engineering / Agent Reference"
MODULE_PART_C_HEADING = "## Part C — Cross-Module Consistency"

_MACHINE_TOKEN_RE = re.compile(
    r"(?:\b(?:TARGET|CURRENT|MODULE|NOT|UNKNOWN)_[A-Z0-9_]+\b|"
    r"\bUNKNOWN\b|"
    r"\b(?:ARCH|RC|FACT)-[A-Z0-9_-]+\b|"
    r"\b(?:requirement_id|source_boundary|canonical_[a-z_]+)\b)",
    re.IGNORECASE,
)


def _strip_non_prose_blocks(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


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
        if stripped.startswith(("#", "|", "- ", "* ", "> ")) or re.match(r"^\d+\.\s", stripped):
            flush()
            continue
        current.append(line)
    return paragraphs


def _nonspace_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", _strip_non_prose_blocks(text)))


def verify_architecture_human(text: str) -> list[str]:
    errors: list[str] = []
    if "# Zuno 目标架构" not in text:
        return ["missing Zuno target architecture title"]
    if ARCHITECTURE_PART_A_HEADING not in text:
        return ["architecture README must contain Part A Human Narrative"]
    if ARCHITECTURE_PART_B_HEADING in text:
        errors.append("architecture README must not contain Part B Engineering Reference")

    visible = text[text.index(ARCHITECTURE_PART_A_HEADING) + len(ARCHITECTURE_PART_A_HEADING):]
    nonspace_chars = _nonspace_chars(visible)
    prose_paragraph_count = len(_prose_paragraphs(visible))
    if nonspace_chars < ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS:
        errors.append(
            "architecture Part A is too thin for the conceptual design baseline "
            f"({nonspace_chars} non-space chars < {ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS})"
        )
    if prose_paragraph_count < ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS:
        errors.append(
            "architecture Part A must contain substantial explanatory prose "
            f"({prose_paragraph_count} paragraphs < {ARCHITECTURE_PART_A_MIN_PROSE_PARAGRAPHS})"
        )
    return errors


def verify_project_text(text: str, filename: str) -> list[str]:
    errors: list[str] = []
    min_chars, min_paragraphs = PROJECT_NARRATIVE_BASELINES[filename]
    nonspace_chars = _nonspace_chars(text)
    prose_paragraph_count = len(_prose_paragraphs(text))
    if nonspace_chars < min_chars:
        errors.append(f"{filename}: project narrative is too thin ({nonspace_chars} < {min_chars})")
    if prose_paragraph_count < min_paragraphs:
        errors.append(f"{filename}: project narrative needs more explanatory prose ({prose_paragraph_count} < {min_paragraphs})")
    return errors


def verify_module_human(text: str, label: str) -> list[str]:
    errors: list[str] = []
    if MODULE_PART_A_HEADING not in text:
        return [f"{label}: module README must contain Part A Human Narrative"]
    if MODULE_PART_B_HEADING in text or MODULE_PART_C_HEADING in text:
        errors.append(f"{label}: module README must not contain Part B or Part C")
    visible = text[text.index(MODULE_PART_A_HEADING) + len(MODULE_PART_A_HEADING):]
    nonspace_chars = _nonspace_chars(visible)
    prose_paragraph_count = len(_prose_paragraphs(visible))
    if nonspace_chars < MODULE_PART_A_MIN_NONSPACE_CHARS:
        errors.append(f"{label}: Part A is too thin ({nonspace_chars} < {MODULE_PART_A_MIN_NONSPACE_CHARS})")
    if prose_paragraph_count < MODULE_PART_A_MIN_PROSE_PARAGRAPHS:
        errors.append(f"{label}: Part A needs more explanatory prose ({prose_paragraph_count} < {MODULE_PART_A_MIN_PROSE_PARAGRAPHS})")
    if not all(marker in visible for marker in ("Current", "Target", "Gap")):
        errors.append(f"{label}: Part A must preserve explicit Current / Target / Gap semantics")
    return errors


def verify_engineering_reference(text: str, label: str, *, module: bool) -> list[str]:
    errors: list[str] = []
    part_b = text.find(MODULE_PART_B_HEADING if module else ARCHITECTURE_PART_B_HEADING)
    if part_b < 0:
        return [f"{label}: missing Part B Engineering / Agent Reference"]
    if module:
        part_c = text.find(MODULE_PART_C_HEADING)
        if part_c < 0:
            errors.append(f"{label}: missing Part C Cross-Module Consistency")
        elif part_b >= part_c:
            errors.append(f"{label}: Part B must precede Part C")
        elif not text[part_b:part_c].strip() or not text[part_c:].strip():
            errors.append(f"{label}: Part B and Part C must both be non-empty")
    elif not text[part_b:].strip():
        errors.append(f"{label}: Part B must not be empty")
    return errors


def warning_for_human(text: str, label: str) -> list[str]:
    matches = _MACHINE_TOKEN_RE.findall(_strip_non_prose_blocks(text))
    if len(matches) < 6:
        return []
    unique = sorted(set(matches), key=str.casefold)
    preview = ", ".join(unique[:8]) + (", …" if len(unique) > 8 else "")
    return [f"READABILITY_WARNING: {label} contains many machine-oriented markers ({preview}); human review is still required."]


def _verify_archives(errors: list[str]) -> None:
    archive_requirements = {
        ROUND_01: ("STAGE A", "STAGE B", "STAGE C", "STAGE D", "STAGE E"),
        ROUND_02: ("## Q1 —", "## A1 —", "## R1 —", "## Q32 —", "## A32 —", "## R32 —", "## Q33 —", "## Q38 —"),
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
    if not ARCH_HUMAN.exists():
        errors.append("missing canonical architecture README")
    else:
        errors.extend(f"docs/architecture/README.md: {e}" for e in verify_architecture_human(ARCH_HUMAN.read_text(encoding="utf-8")))
    if not ARCH_REFERENCE.exists():
        errors.append("missing canonical architecture reference")
    else:
        errors.extend(verify_engineering_reference(ARCH_REFERENCE.read_text(encoding="utf-8"), "docs/architecture/reference.md", module=False))

    for filename in PROJECT_NARRATIVE_BASELINES:
        path = PROJECT_ROOT / filename
        if not path.exists():
            errors.append(f"missing canonical project narrative: {path.relative_to(ROOT)}")
        else:
            errors.extend(verify_project_text(path.read_text(encoding="utf-8"), filename))

    for directory in MODULE_DIRS:
        human = MODULES_ROOT / directory / "README.md"
        reference = MODULES_ROOT / directory / "reference.md"
        if not human.exists():
            errors.append(f"missing canonical module narrative: {human.relative_to(ROOT)}")
        else:
            errors.extend(verify_module_human(human.read_text(encoding="utf-8"), f"{directory}/README.md"))
        if not reference.exists():
            errors.append(f"missing canonical module reference: {reference.relative_to(ROOT)}")
        else:
            errors.extend(verify_engineering_reference(reference.read_text(encoding="utf-8"), f"{directory}/reference.md", module=True))

    _verify_archives(errors)
    views = ROOT / "docs/architecture/architecture-views.md"
    html = ROOT / "docs/architecture/architecture.html"
    if not views.exists() or not html.exists():
        errors.append("architecture diagram presentation pair must remain present")
    elif 'fetch("./architecture-views.md")' not in html.read_text(encoding="utf-8"):
        errors.append("architecture.html must continue to consume architecture-views.md")
    for pattern in ("docs/**/*-human.md", "docs/**/*-spec.md"):
        for forbidden in ROOT.glob(pattern):
            errors.append(f"human/spec mirror document must not exist: {forbidden.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    warnings: list[str] = []
    if ARCH_HUMAN.exists():
        warnings.extend(warning_for_human(ARCH_HUMAN.read_text(encoding="utf-8"), "architecture README"))
    project = PROJECT_ROOT / "README.md"
    if project.exists():
        warnings.extend(warning_for_human(project.read_text(encoding="utf-8"), "project README"))
    for warning in warnings:
        print(warning, file=sys.stderr)
    print("project, architecture and module human readability structural verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
