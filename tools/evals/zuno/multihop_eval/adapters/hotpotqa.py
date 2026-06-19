from __future__ import annotations

from typing import Any

from .common import normalize_hotpot_style_record, read_json_or_jsonl


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_hotpot_style_record(record, dataset="hotpotqa") for record in records]


def load_normalized(path) -> list[dict[str, Any]]:
    return normalize_records(read_json_or_jsonl(path))


__all__ = ["load_normalized", "normalize_records"]

