from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest


def test_completion_route_no_longer_exports_general_agent_rollback() -> None:
    import zuno.api.v1.completion as completion_module

    assert "GeneralAgent" not in completion_module.__all__
    assert "AgentConfig" not in completion_module.__dict__
    assert "GeneralAgent" not in completion_module.__dict__
    assert "_create_chat_agent" not in completion_module.__dict__


def test_completion_rejects_retired_rollback_mode_before_agent_config(monkeypatch) -> None:
    from zuno.api.dto.completion import CompletionReq
    from zuno.api.v1.completion import completion

    async def fail_stream_unified_runtime(**kwargs):
        raise AssertionError(f"retired rollback reached unified runtime: {kwargs!r}")
        yield {}

    monkeypatch.setenv("ZUNO_COMPLETION_CUTOVER_MODE", "rollback")
    monkeypatch.setattr(
        "zuno.api.v1.completion.CompletionService.stream_unified_runtime",
        fail_stream_unified_runtime,
    )

    with pytest.raises(ValueError, match="rollback mode is retired"):
        asyncio.run(
            completion(
                req=CompletionReq(user_input="审查合同", dialog_id="dialog_42", file_url=None),
                login_user=SimpleNamespace(user_id="u_login"),
            )
        )


def test_completion_new_default_returns_unified_stream_without_agent_config(monkeypatch) -> None:
    from zuno.api.dto.completion import CompletionReq
    from zuno.api.v1.completion import completion

    captured = {}

    async def fake_stream_unified_runtime(**kwargs):
        captured.update(kwargs)
        yield {
            "type": "response_chunk",
            "data": {"chunk": "ok", "runtime_topology": "unified_agent_runtime"},
        }

    monkeypatch.delenv("ZUNO_COMPLETION_CUTOVER_MODE", raising=False)
    monkeypatch.setattr(
        "zuno.api.v1.completion.CompletionService.stream_unified_runtime",
        fake_stream_unified_runtime,
    )

    async def call_and_drain_response():
        response = await completion(
            req=CompletionReq(
                user_input="用目标 runtime 审查合同",
                dialog_id="dialog_multi",
                file_url=None,
                multi_agent_enabled=True,
                product_mode="enhanced",
                query_method="local",
            ),
            login_user=SimpleNamespace(user_id="u_login"),
        )
        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
        return response, chunks

    response, chunks = asyncio.run(call_and_drain_response())

    assert captured["login_user_id"] == "u_login"
    assert captured["cutover_mode"] == "new_default"
    assert captured["req"].dialog_id == "dialog_multi"
    assert chunks
    assert response.media_type == "text/event-stream"
