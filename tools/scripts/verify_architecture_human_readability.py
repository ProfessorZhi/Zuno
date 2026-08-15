from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANONICAL = [ROOT / "docs/architecture/architecture.md"]
ARCHITECTURE_README = ROOT / "docs/architecture/README.md"
MODULES_ROOT = ROOT / "docs/modules"
ROUND_01 = ROOT / "docs/history/red-blue/manual-round-01-overall-architecture.md"
ROUND_02 = ROOT / "docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md"

PART_A_HEADING = "## Part A — Architecture Narrative"
PART_B_HEADING = "## Part B — Detailed Architecture Specification"
_MACHINE_TOKEN_RE = re.compile(
    r"(?:\b(?:TARGET|CURRENT|MODULE|NOT|UNKNOWN)_[A-Z0-9_]+\b|"
    r"\bUNKNOWN\b|"
    r"\b(?:ARCH|RC|FACT)-[A-Z0-9_-]+\b|"
    r"\b(?:requirement_id|source_boundary|canonical_[a-z_]+)\b)",
    re.IGNORECASE,
)
_ENGINEERING_ANCHORS = (
    "Contract",
    "State",
    "Recovery",
    "Ownership",
    "Engineering",
    "Evidence",
    "Persistence",
    "Security",
)


def _split_layers(text: str) -> tuple[str, str] | None:
    """Return Part A and Part B bodies when both headings are present and ordered."""
    if PART_A_HEADING not in text or PART_B_HEADING not in text:
        return None
    part_a_start = text.index(PART_A_HEADING) + len(PART_A_HEADING)
    part_b_start = text.index(PART_B_HEADING)
    if part_b_start < part_a_start:
        return None
    return text[part_a_start:part_b_start], text[part_b_start + len(PART_B_HEADING) :]


def _has_narrative_prose(text: str) -> bool:
    """Detect at least one ordinary explanatory paragraph, not only metadata or lists."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    in_fence = False
    paragraph: list[str] = []

    def is_prose(lines: list[str]) -> bool:
        if not lines:
            return False
        value = " ".join(line.strip() for line in lines).strip()
        if not value or value.startswith(("#", "|", "- ", "* ", "> ")):
            return False
        if value.endswith(":") and len(value) < 120:
            return False
        if re.match(r"^[A-Za-z_][A-Za-z0-9_ -]*:\s*\S+$", value):
            return False
        return len(value) >= 25

    for line in text.splitlines() + [""]:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            if paragraph and not in_fence:
                if is_prose(paragraph):
                    return True
                paragraph = []
            continue
        if in_fence or not stripped:
            if paragraph and is_prose(paragraph):
                return True
            paragraph = []
            continue
        if stripped.startswith(("#", "|", "- ", "* ", "> ")):
            if paragraph and is_prose(paragraph):
                return True
            paragraph = []
            continue
        paragraph.append(line)
    return False


def verify_text(text: str) -> list[str]:
    """Check the stable writing-model contract without judging prose quality."""
    errors: list[str] = []
    if PART_A_HEADING not in text:
        errors.append("missing Part A — Architecture Narrative")
    if PART_B_HEADING not in text:
        errors.append("missing Part B — Detailed Architecture Specification")
    if errors:
        return errors

    part_a_position = text.index(PART_A_HEADING)
    part_b_position = text.index(PART_B_HEADING)
    if part_b_position < part_a_position:
        errors.append("Part B must follow Part A")
        return errors

    layers = _split_layers(text)
    if layers is None:
        errors.append("Part A and Part B could not be split in the required order")
        return errors
    part_a, part_b = layers
    if not part_a.strip():
        errors.append("Part A must not be empty")
    elif not _has_narrative_prose(part_a):
        errors.append("Part A must contain at least one explanatory prose paragraph")
    if not part_b.strip():
        errors.append("Part B must not be empty")
    elif not any(anchor in part_b for anchor in _ENGINEERING_ANCHORS):
        errors.append("Part B must contain an engineering reference anchor")
    return errors


def warnings_for_text(text: str) -> list[str]:
    """Report machine-oriented language in Part A without making it a validation failure."""
    layers = _split_layers(text)
    if layers is None:
        return []
    matches = _MACHINE_TOKEN_RE.findall(layers[0])
    if len(matches) < 3:
        return []
    unique = sorted(set(matches), key=str.casefold)
    preview = ", ".join(unique[:8])
    if len(unique) > 8:
        preview += ", …"
    return [
        "READABILITY_WARNING: Part A contains machine-oriented markers "
        f"({preview}); human review is still required."
    ]


def _verify_supporting_boundaries(errors: list[str]) -> None:
    if not ARCHITECTURE_README.exists():
        errors.append("missing docs/architecture/README.md")
    else:
        readme = ARCHITECTURE_README.read_text(encoding="utf-8")
        for filename in ("architecture.md", "architecture-views.md", "architecture.html"):
            if filename not in readme:
                errors.append(f"architecture README missing entry: {filename}")

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
    for warning in warnings:
        print(warning)
    print("architecture human readability structural verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
