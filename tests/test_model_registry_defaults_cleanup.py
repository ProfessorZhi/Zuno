from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "tools" / "scripts" / "cleanup_model_registry_defaults.py"

spec = importlib.util.spec_from_file_location("cleanup_model_registry_defaults", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def _row(*, llm_id: str, model: str, llm_type: str, model_slot: str | None) -> dict[str, str | None]:
    return {
        "llm_id": llm_id,
        "model": model,
        "llm_type": llm_type,
        "model_slot": model_slot,
        "provider": "test",
        "user_id": "0",
    }


def _args(*, apply: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        conversation_model="deepseek-v4-flash",
        embedding_model="text-embedding-v4",
        vl_embedding_model="qwen3-vl-embedding",
        rerank_model="gte-rerank-v2",
        apply=apply,
    )


def test_build_target_plan_resolves_unique_models() -> None:
    rows = [
        _row(llm_id="a", model="deepseek-v4-flash", llm_type="LLM", model_slot=None),
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        _row(llm_id="c", model="qwen3-vl-embedding", llm_type="Embedding", model_slot="vl_embedding"),
        _row(llm_id="d", model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
    ]

    plan = module.build_target_plan(
        rows,
        conversation_model="deepseek-v4-flash",
        embedding_model="text-embedding-v4",
        vl_embedding_model="qwen3-vl-embedding",
        rerank_model="gte-rerank-v2",
    )

    assert [item["slot"] for item in plan] == ["conversation_model", "embedding", "vl_embedding", "rerank"]
    assert plan[0]["llm_id"] == "a"
    assert plan[1]["already_bound"] is True


def test_build_target_plan_fails_when_model_missing() -> None:
    rows = [
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
    ]

    try:
        module.build_target_plan(
            rows,
            conversation_model="deepseek-v4-flash",
            embedding_model="text-embedding-v4",
            vl_embedding_model="qwen3-vl-embedding",
            rerank_model="gte-rerank-v2",
        )
    except ValueError as exc:
        assert "model not found" in str(exc)
    else:
        raise AssertionError("expected missing model error")


def test_build_target_plan_fails_when_model_is_duplicated() -> None:
    rows = [
        _row(llm_id="a1", model="deepseek-v4-flash", llm_type="LLM", model_slot=None),
        _row(llm_id="a2", model="deepseek-v4-flash", llm_type="LLM", model_slot=None),
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        _row(llm_id="c", model="qwen3-vl-embedding", llm_type="Embedding", model_slot="vl_embedding"),
        _row(llm_id="d", model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
    ]

    try:
        module.build_target_plan(
            rows,
            conversation_model="deepseek-v4-flash",
            embedding_model="text-embedding-v4",
            vl_embedding_model="qwen3-vl-embedding",
            rerank_model="gte-rerank-v2",
        )
    except ValueError as exc:
        assert "multiple models matched" in str(exc)
    else:
        raise AssertionError("expected duplicate model error")


def test_run_cleanup_dry_run_does_not_apply(monkeypatch, capsys) -> None:
    rows = [
        _row(llm_id="a", model="deepseek-v4-flash", llm_type="LLM", model_slot=None),
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        _row(llm_id="c", model="qwen3-vl-embedding", llm_type="Embedding", model_slot="vl_embedding"),
        _row(llm_id="d", model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
    ]
    applied: list[list[dict[str, object]]] = []

    async def fake_load_rows():
        return rows

    async def fake_apply(plan):
        applied.append(plan)

    monkeypatch.setattr(module, "load_rows_from_database", fake_load_rows)
    monkeypatch.setattr(module, "apply_plan", fake_apply)

    exit_code = module.main if False else None
    result = __import__("asyncio").run(module.run_cleanup(_args(apply=False)))
    captured = capsys.readouterr().out

    assert result == 0
    assert applied == []
    assert '"mode": "dry-run"' in captured


def test_run_cleanup_apply_executes_plan(monkeypatch, capsys) -> None:
    before_rows = [
        _row(llm_id="old1", model="MiniMax-M2.5", llm_type="LLM", model_slot="conversation_model"),
        _row(llm_id="old2", model="qwen-plus", llm_type="LLM", model_slot="conversation_model"),
        _row(llm_id="a", model="deepseek-v4-flash", llm_type="LLM", model_slot=None),
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        _row(llm_id="c", model="qwen3-vl-embedding", llm_type="Embedding", model_slot="vl_embedding"),
        _row(llm_id="d", model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
    ]
    after_rows = [
        _row(llm_id="old1", model="MiniMax-M2.5", llm_type="LLM", model_slot=None),
        _row(llm_id="old2", model="qwen-plus", llm_type="LLM", model_slot=None),
        _row(llm_id="a", model="deepseek-v4-flash", llm_type="LLM", model_slot="conversation_model"),
        _row(llm_id="b", model="text-embedding-v4", llm_type="Embedding", model_slot="embedding"),
        _row(llm_id="c", model="qwen3-vl-embedding", llm_type="Embedding", model_slot="vl_embedding"),
        _row(llm_id="d", model="gte-rerank-v2", llm_type="Rerank", model_slot="rerank"),
    ]
    load_calls = {"count": 0}
    applied: list[dict[str, str]] = []

    async def fake_load_rows():
        load_calls["count"] += 1
        return before_rows if load_calls["count"] == 1 else after_rows

    async def fake_apply(plan):
        applied.extend(plan)

    monkeypatch.setattr(module, "load_rows_from_database", fake_load_rows)
    monkeypatch.setattr(module, "apply_plan", fake_apply)

    result = __import__("asyncio").run(module.run_cleanup(_args(apply=True)))
    captured = capsys.readouterr().out

    assert result == 0
    assert [item["slot"] for item in applied] == ["conversation_model", "embedding", "vl_embedding", "rerank"]
    assert '"after_slots"' in captured
