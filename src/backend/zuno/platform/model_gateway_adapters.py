from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.language_models import BaseChatModel


class OpenAIEmbeddingGatewayAdapter:
    """Provider SDK adapter for OpenAI-compatible embeddings inside the Gateway boundary."""

    def __init__(self, *, api_key: str | None, base_url: str | None, model: str):
        from openai import AsyncOpenAI, OpenAI

        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def embed(self, query: str) -> list[float]:
        responses = self._client.embeddings.create(
            model=self.model,
            input=query,
            encoding_format="float",
        )
        return responses.data[0].embedding

    async def embed_async(self, query: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(query, str) or len(query) <= 10:
            return await self._embed_batch(query)

        semaphore = asyncio.Semaphore(5)

        async def process_batch(batch: list[str]) -> list[list[float]]:
            async with semaphore:
                batch_result = await self._embed_batch(batch)
                return batch_result if isinstance(batch_result[0], list) else [batch_result]

        batches = [query[index : index + 10] for index in range(0, len(query), 10)]
        results = await asyncio.gather(*(process_batch(batch) for batch in batches))
        return [embedding for batch_result in results for embedding in batch_result]

    async def _embed_batch(self, query: str | list[str]) -> list[float] | list[list[float]]:
        responses = await self._async_client.embeddings.create(
            model=self.model,
            input=query,
            encoding_format="float",
        )
        if isinstance(query, str):
            return responses.data[0].embedding
        return [response.embedding for response in responses.data]


def build_openai_embedding_gateway_adapter(config_override: Any = None) -> OpenAIEmbeddingGatewayAdapter:
    from zuno.core.models.manager import ModelManager

    config = _normalize_embedding_config_override(config_override) or ModelManager.get_model_config(
        "embedding",
        "Embedding model",
    )
    return OpenAIEmbeddingGatewayAdapter(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model_name,
    )


def _normalize_embedding_config_override(config_override: Any) -> Any:
    if not config_override:
        return None
    if hasattr(config_override, "model_name"):
        return config_override
    return type("EmbeddingConfig", (), config_override)()


class OpenAIChatCompletionsGatewayAdapter:
    """Provider SDK adapter for OpenAI-compatible chat completions inside the Gateway boundary."""

    def __init__(self, *, api_key: str | None, base_url: str | None):
        from openai import AsyncOpenAI

        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        tools: list[dict[str, Any]] | dict[str, Any] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools is not None:
            payload["tools"] = tools
        return await self._async_client.chat.completions.create(**payload)


class OpenAIUsageChatGatewayAdapter:
    """Provider SDK adapter for chat completions used by token-usage chat models."""

    def __init__(self, *, api_key: str | None, base_url: str | None):
        from openai import AsyncOpenAI, OpenAI

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def create(self, **kwargs: Any) -> Any:
        return self._client.chat.completions.create(**kwargs)

    async def acreate(self, **kwargs: Any) -> Any:
        return await self._async_client.chat.completions.create(**kwargs)


class AnthropicMessagesGatewayAdapter:
    """Provider SDK adapter for Anthropic messages inside the Gateway boundary."""

    def __init__(self, *, api_key: str | None, base_url: str | None):
        from anthropic import Anthropic

        self._client = Anthropic(base_url=base_url, api_key=api_key)

    def create(self, **kwargs: Any) -> Any:
        return self._client.messages.create(**kwargs)

    def stream(self, **kwargs: Any) -> Any:
        return self._client.messages.stream(**kwargs)


class AsyncAnthropicMessagesGatewayAdapter:
    """Provider SDK adapter for async Anthropic messages inside the Gateway boundary."""

    def __init__(self, *, api_key: str | None, base_url: str | None):
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(base_url=base_url, api_key=api_key)

    async def create(self, **kwargs: Any) -> Any:
        return await self._client.messages.create(**kwargs)

    def stream(self, **kwargs: Any) -> Any:
        return self._client.messages.stream(**kwargs)


def is_openai_well_known_tool(tool_choice: str) -> bool:
    from langchain_openai.chat_models.base import WellKnownTools

    return tool_choice in WellKnownTools


def build_openai_chat_gateway_model(
    *,
    model: str | None,
    api_key: str | None,
    base_url: str | None,
    stream_usage: bool = True,
) -> BaseChatModel:
    """Build an OpenAI-compatible LangChain chat model inside the Gateway boundary."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        stream_usage=stream_usage,
        model=model,
        api_key=api_key,
        base_url=base_url,
        **_standard_openai_chat_kwargs(model, base_url),
    )


def _standard_openai_chat_kwargs(model_name: str | None, base_url: str | None) -> dict[str, Any]:
    base_url_lower = str(base_url or "").lower()
    model_lower = str(model_name or "").lower()
    if "deepseek.com" in base_url_lower and model_lower.startswith("deepseek-v4"):
        return {"extra_body": {"thinking": {"type": "disabled"}}}
    return {}


__all__ = [
    "AnthropicMessagesGatewayAdapter",
    "AsyncAnthropicMessagesGatewayAdapter",
    "OpenAIChatCompletionsGatewayAdapter",
    "OpenAIEmbeddingGatewayAdapter",
    "OpenAIUsageChatGatewayAdapter",
    "build_openai_chat_gateway_model",
    "build_openai_embedding_gateway_adapter",
    "is_openai_well_known_tool",
]
