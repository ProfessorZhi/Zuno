from __future__ import annotations


class LLMProvider:
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        raise NotImplementedError


class EchoLLMProvider(LLMProvider):
    async def chat(self, messages: list[dict], **kwargs) -> dict:
        last = messages[-1] if messages else {}
        return {
            "provider": "echo",
            "content": str(last.get("content") or ""),
            "messages": messages,
        }
