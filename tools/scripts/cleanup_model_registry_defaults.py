from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


SLOT_TO_TYPE = {
    "conversation_model": "LLM",
    "embedding": "Embedding",
    "vl_embedding": "Embedding",
    "rerank": "Rerank",
}


def normalize_llm_type(value: str | None) -> str:
    if value == "Reranker":
        return "Rerank"
    return str(value or "LLM")


def summarize_slots(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    summary: dict[str, list[dict[str, Any]]] = {slot: [] for slot in SLOT_TO_TYPE}
    for row in rows:
        slot = row.get("model_slot")
        if slot in summary:
            summary[slot].append(
                {
                    "llm_id": row.get("llm_id"),
                    "model": row.get("model"),
                    "llm_type": normalize_llm_type(row.get("llm_type")),
                    "provider": row.get("provider"),
                    "user_id": row.get("user_id"),
                }
            )
    return summary


def resolve_unique_model(rows: list[dict[str, Any]], *, model_name: str, expected_type: str) -> dict[str, Any]:
    matches = [
        row
        for row in rows
        if str(row.get("model") or "") == model_name
        and normalize_llm_type(row.get("llm_type")) == expected_type
    ]
    if not matches:
        raise ValueError(f"model not found: {model_name} ({expected_type})")
    if len(matches) > 1:
        raise ValueError(f"multiple models matched: {model_name} ({expected_type})")
    return matches[0]


def build_target_plan(
    rows: list[dict[str, Any]],
    *,
    conversation_model: str,
    embedding_model: str,
    vl_embedding_model: str,
    rerank_model: str,
) -> list[dict[str, Any]]:
    requested = {
        "conversation_model": conversation_model,
        "embedding": embedding_model,
        "vl_embedding": vl_embedding_model,
        "rerank": rerank_model,
    }
    plan: list[dict[str, Any]] = []
    for slot, model_name in requested.items():
        target = resolve_unique_model(rows, model_name=model_name, expected_type=SLOT_TO_TYPE[slot])
        plan.append(
            {
                "slot": slot,
                "target_model": model_name,
                "llm_id": target.get("llm_id"),
                "current_slot": target.get("model_slot"),
                "already_bound": target.get("model_slot") == slot,
            }
        )
    return plan


async def load_rows_from_database() -> list[dict[str, Any]]:
    from zuno.database.dao.llm import LLMDao

    rows = await LLMDao.get_all_llm()
    payloads: list[dict[str, Any]] = []
    for row in rows:
        payload = row.to_dict()
        payload.pop("api_key", None)
        payloads.append(payload)
    return payloads


async def apply_plan(plan: list[dict[str, Any]]) -> None:
    from zuno.api.services.llm import LLMService

    for item in plan:
        await LLMService.activate_model_slot(str(item["llm_id"]), str(item["slot"]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean up local model registry default slots safely.")
    parser.add_argument("--conversation-model", required=True)
    parser.add_argument("--embedding-model", required=True)
    parser.add_argument("--vl-embedding-model", required=True)
    parser.add_argument("--rerank-model", required=True)
    parser.add_argument("--apply", action="store_true", help="Apply the cleanup. Without this flag, run as dry-run.")
    return parser.parse_args()


async def run_cleanup(args: argparse.Namespace) -> int:
    try:
        before_rows = await load_rows_from_database()
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

    try:
        plan = build_target_plan(
            before_rows,
            conversation_model=args.conversation_model,
            embedding_model=args.embedding_model,
            vl_embedding_model=args.vl_embedding_model,
            rerank_model=args.rerank_model,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "status": "plan_error",
                    "error": str(exc),
                    "before_slots": summarize_slots(before_rows),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    payload: dict[str, Any] = {
        "ok": True,
        "mode": "apply" if args.apply else "dry-run",
        "plan": plan,
        "before_slots": summarize_slots(before_rows),
    }

    if args.apply:
        try:
            await apply_plan(plan)
            after_rows = await load_rows_from_database()
            payload["after_slots"] = summarize_slots(after_rows)
        except Exception as exc:
            payload = {
                "ok": False,
                "status": "apply_error",
                "error": str(exc),
                "plan": plan,
                "before_slots": summarize_slots(before_rows),
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 2

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    return asyncio.run(run_cleanup(args))


if __name__ == "__main__":
    raise SystemExit(main())
