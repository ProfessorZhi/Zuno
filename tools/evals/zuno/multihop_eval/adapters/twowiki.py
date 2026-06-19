from __future__ import annotations

from typing import Any

from .common import normalize_hotpot_style_record, read_json_or_jsonl


def _evidence_entities(evidences: list[Any]) -> list[str]:
    entities: list[str] = []
    for evidence in evidences or []:
        if not isinstance(evidence, (list, tuple)):
            continue
        for value in (evidence[0:1] + evidence[2:3]):
            text = str(value or "").strip()
            if text and text not in entities:
                entities.append(text)
    return entities


def _evidence_path(evidences: list[Any]) -> list[dict[str, str]]:
    path: list[dict[str, str]] = []
    for evidence in evidences or []:
        if isinstance(evidence, (list, tuple)) and len(evidence) >= 3:
            path.append(
                {
                    "subject": str(evidence[0]),
                    "relation": str(evidence[1]),
                    "object": str(evidence[2]),
                }
            )
    return path


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        item = normalize_hotpot_style_record(record, dataset="2wikimultihopqa")
        evidences = list(record.get("evidences") or [])
        item["gold_entities"] = _evidence_entities(evidences)
        item["gold_evidence_path"] = _evidence_path(evidences)
        normalized.append(item)
    return normalized


def load_normalized(path) -> list[dict[str, Any]]:
    return normalize_records(read_json_or_jsonl(path))


__all__ = ["load_normalized", "normalize_records"]

