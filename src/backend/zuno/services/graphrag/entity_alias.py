from __future__ import annotations

import re

LEADING_ARTICLE_PATTERN = re.compile(r"^(the|a|an)\s+", re.IGNORECASE)
PARENTHETICAL_PATTERN = re.compile(r"\s*\([^)]*\)")
PUNCTUATION_PATTERN = re.compile(r"[_/:,.;]+")
HYPHEN_PATTERN = re.compile(r"[-–—]+")
WHITESPACE_PATTERN = re.compile(r"\s+")
GENERIC_ENTITIES = {
    "Introduction",
    "Overview",
    "Objectives",
    "Objective",
    "History",
    "Roadmap",
    "Examples",
    "Example",
    "High",
    "Low",
    "Medium",
}


def normalize_entity_name(value: str) -> str:
    text = str(value or "").strip().lower()
    text = PARENTHETICAL_PATTERN.sub("", text)
    text = LEADING_ARTICLE_PATTERN.sub("", text)
    text = HYPHEN_PATTERN.sub(" ", text)
    text = PUNCTUATION_PATTERN.sub(" ", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def resolve_alias(candidate: str, known_entities: list[str], *, allow_fuzzy: bool = False) -> dict[str, object]:
    display = str(candidate or "").strip()
    if not display or display in GENERIC_ENTITIES:
        return {"matched": False, "resolved_from": display, "resolved_to": display}

    known = [str(item or "").strip() for item in known_entities if str(item or "").strip()]
    if display in known:
        return {"matched": True, "resolved_from": display, "resolved_to": display}

    normalized_candidate = normalize_entity_name(display)
    if not normalized_candidate or normalized_candidate.title() in GENERIC_ENTITIES:
        return {"matched": False, "resolved_from": display, "resolved_to": display}

    normalized_map = {normalize_entity_name(item): item for item in known}
    if normalized_candidate in normalized_map:
        return {
            "matched": True,
            "resolved_from": display,
            "resolved_to": normalized_map[normalized_candidate],
        }

    if allow_fuzzy:
        for normalized_known, original in normalized_map.items():
            if normalized_candidate == normalized_known:
                return {"matched": True, "resolved_from": display, "resolved_to": original}

    return {"matched": False, "resolved_from": display, "resolved_to": display}


__all__ = ["normalize_entity_name", "resolve_alias"]
