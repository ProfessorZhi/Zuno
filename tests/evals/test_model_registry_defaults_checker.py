from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "tools" / "scripts" / "check_model_registry_defaults.py"

spec = importlib.util.spec_from_file_location("check_model_registry_defaults", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def _row(*, model: str, llm_type: str, model_slot: str | None) -> dict[str, str | None]:
    return {
        "model": model,
        "llm_type": llm_type,
        "model_slot": model_slot,
    }


def _slot(summary: dict, slot_name: str) -> dict:
    return next(slot for slot in summary["slots"] if slot["slot"] == slot_name)


def test_single_conversation_default_passes() -> None:
    summary = module.summarize_registry(
        [
            _row(model="qwen-plus", llm_type="LLM", model_slot="conversation_model"),
            _row(model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
            _row(model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
        ]
    )

    assert summary["ok"] is True
    assert _slot(summary, "conversation_model")["status"] == "ok"


def test_duplicate_conversation_default_fails() -> None:
    summary = module.summarize_registry(
        [
            _row(model="MiniMax-M2.5", llm_type="LLM", model_slot="conversation_model"),
            _row(model="qwen-plus", llm_type="LLM", model_slot="conversation_model"),
            _row(model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
            _row(model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
        ]
    )

    assert summary["ok"] is False
    assert _slot(summary, "conversation_model")["status"] == "ambiguous"
    assert summary["failures"]


def test_missing_embedding_fails() -> None:
    summary = module.summarize_registry(
        [
            _row(model="qwen-plus", llm_type="LLM", model_slot="conversation_model"),
            _row(model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
        ]
    )

    assert summary["ok"] is False
    assert _slot(summary, "embedding")["status"] == "missing"


def test_missing_rerank_fails() -> None:
    summary = module.summarize_registry(
        [
            _row(model="qwen-plus", llm_type="LLM", model_slot="conversation_model"),
            _row(model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        ]
    )

    assert summary["ok"] is False
    assert _slot(summary, "rerank")["status"] == "missing"
