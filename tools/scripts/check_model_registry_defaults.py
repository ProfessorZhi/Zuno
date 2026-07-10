from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


MODEL_TYPES = ("LLM", "Embedding", "Rerank")
MODEL_SLOTS = (
    "conversation_model",
    "tool_call_model",
    "reasoning_model",
    "embedding",
    "vl_embedding",
    "rerank",
)
REQUIRED_NON_EMPTY_SLOTS = {"conversation_model", "tool_call_model", "reasoning_model", "embedding", "rerank"}


def normalize_llm_type(value: str | None) -> str:
    if value == "Reranker":
        return "Rerank"
    return str(value or "LLM")


def _model_label(row: dict[str, Any]) -> str:
    return str(row.get("model") or row.get("llm_id") or "unknown")


def summarize_registry(rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_rows = []
    for row in rows:
        normalized = dict(row)
        normalized["llm_type"] = normalize_llm_type(row.get("llm_type"))
        normalized_rows.append(normalized)

    type_counts = {model_type: 0 for model_type in MODEL_TYPES}
    for row in normalized_rows:
        llm_type = row.get("llm_type")
        if llm_type in type_counts:
            type_counts[llm_type] += 1

    slot_summaries: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []

    for slot in MODEL_SLOTS:
        slot_rows = [row for row in normalized_rows if row.get("model_slot") == slot]
        models = [_model_label(row) for row in slot_rows]
        status = "ok"

        if slot in REQUIRED_NON_EMPTY_SLOTS and len(slot_rows) > 1:
            status = "ambiguous"
            failures.append(
                f"multiple models are bound to {slot}; default model resolution is ambiguous"
            )
        elif slot in REQUIRED_NON_EMPTY_SLOTS and not slot_rows:
            status = "missing"
            failures.append(f"required slot `{slot}` has no registered model")
        elif not slot_rows:
            status = "missing"
            warnings.append(f"slot `{slot}` has no registered model")

        slot_summaries.append(
            {
                "slot": slot,
                "models": models,
                "count": len(models),
                "status": status,
            }
        )

    return {
        "ok": not failures,
        "model_type_counts": type_counts,
        "slots": slot_summaries,
        "failures": failures,
        "warnings": warnings,
    }


def load_rows_from_database() -> list[dict[str, Any]]:
    from zuno.database.dao.llm import LLMDao

    import asyncio

    async def _load() -> list[dict[str, Any]]:
        rows = await LLMDao.get_all_llm()
        result: list[dict[str, Any]] = []
        for row in rows:
            payload = row.to_dict()
            payload.pop("api_key", None)
            result.append(payload)
        return result

    return asyncio.run(_load())


def main() -> int:
    try:
        rows = load_rows_from_database()
        summary = summarize_registry(rows)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": "database_unavailable",
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
