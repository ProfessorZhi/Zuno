from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _sentences_to_text(sentences: list[Any]) -> list[str]:
    return [str(sentence or "").strip() for sentence in sentences if str(sentence or "").strip()]


def normalize_documents(context: list[Any]) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    for index, item in enumerate(context or []):
        title = f"doc_{index}"
        sentences: list[str] = []
        if isinstance(item, dict):
            title = str(item.get("title") or item.get("id") or title)
            raw_sentences = item.get("sentences")
            if raw_sentences is None:
                raw_sentences = [item.get("text") or item.get("paragraph_text") or ""]
            sentences = _sentences_to_text(list(raw_sentences or []))
            doc_id = str(item.get("doc_id") or item.get("id") or title)
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            title = str(item[0])
            sentences = _sentences_to_text(list(item[1] or []))
            doc_id = title
        else:
            doc_id = title
            sentences = _sentences_to_text([item])
        documents.append(
            {
                "doc_id": doc_id,
                "title": title,
                "sentences": sentences,
                "text": " ".join(sentences),
            }
        )
    return documents


def build_support(
    supporting_facts: list[Any],
    documents: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_title = {document["title"]: document for document in documents}
    support: list[dict[str, Any]] = []
    for item in supporting_facts or []:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        title = str(item[0])
        sent_id = int(item[1])
        sentences = by_title.get(title, {}).get("sentences") or []
        text = sentences[sent_id] if 0 <= sent_id < len(sentences) else ""
        support.append({"title": title, "sent_id": sent_id, "text": text})
    return support


def normalize_hotpot_style_record(record: dict[str, Any], *, dataset: str) -> dict[str, Any]:
    documents = normalize_documents(list(record.get("context") or []))
    return {
        "dataset": dataset,
        "id": str(record.get("_id") or record.get("id") or ""),
        "question": str(record.get("question") or ""),
        "answer": str(record.get("answer") or ""),
        "documents": documents,
        "gold_support": build_support(list(record.get("supporting_facts") or []), documents),
        "gold_entities": [],
        "gold_evidence_path": [],
        "metadata": {
            key: value
            for key, value in record.items()
            if key not in {"_id", "id", "question", "answer", "context", "supporting_facts"}
        },
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def read_json_or_jsonl(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    return read_json_or_jsonl_text(text=text, source=str(path))


def read_json_or_jsonl_text(*, text: str, source: str = "<memory>") -> list[dict[str, Any]]:
    text = str(text or "").strip()
    if not text:
        return []
    if source.endswith(".jsonl"):
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    payload = json.loads(text)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "examples", "records"):
            if isinstance(payload.get(key), list):
                return payload[key]
    raise ValueError(f"unsupported dataset payload shape: {source}")
