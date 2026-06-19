from __future__ import annotations

import re
from typing import Any

from .common import read_json_or_jsonl


def _split_sentences(text: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?。！？])\s+", str(text or "").strip()) if part.strip()]
    return parts or ([str(text).strip()] if str(text or "").strip() else [])


def normalize_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        documents: list[dict[str, Any]] = []
        support: list[dict[str, Any]] = []
        for index, paragraph in enumerate(record.get("paragraphs") or []):
            title = str(paragraph.get("title") or paragraph.get("idx") or f"paragraph_{index}")
            text = str(paragraph.get("paragraph_text") or paragraph.get("text") or "")
            sentences = _split_sentences(text)
            documents.append(
                {
                    "doc_id": str(paragraph.get("idx") or title),
                    "title": title,
                    "sentences": sentences,
                    "text": " ".join(sentences),
                }
            )
            if paragraph.get("is_supporting"):
                support.append({"title": title, "sent_id": 0, "text": sentences[0] if sentences else ""})

        normalized.append(
            {
                "dataset": "musique",
                "id": str(record.get("id") or record.get("_id") or ""),
                "question": str(record.get("question") or ""),
                "answer": str(record.get("answer") or record.get("answer_aliases", [""])[0] or ""),
                "documents": documents,
                "gold_support": support,
                "gold_entities": [],
                "gold_evidence_path": [],
                "metadata": {
                    key: value
                    for key, value in record.items()
                    if key not in {"id", "_id", "question", "answer", "answer_aliases", "paragraphs"}
                },
            }
        )
    return normalized


def load_normalized(path) -> list[dict[str, Any]]:
    return normalize_records(read_json_or_jsonl(path))


__all__ = ["load_normalized", "normalize_records"]

