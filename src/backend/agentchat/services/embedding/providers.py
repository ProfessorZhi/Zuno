from __future__ import annotations


class EmbeddingProvider:
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    async def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class FakeEmbeddingProvider(EmbeddingProvider):
    def _embed(self, text: str) -> list[float]:
        normalized = str(text or "")
        return [
            float(len(normalized)),
            float(sum(ord(ch) for ch in normalized) % 997),
            float(len(set(normalized))),
        ]

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    async def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
