import asyncio

from zuno.services.embedding.providers import FakeEmbeddingProvider


def test_fake_embedding_provider_is_deterministic():
    provider = FakeEmbeddingProvider()
    first = asyncio.run(provider.embed_query("contract review"))
    second = asyncio.run(provider.embed_query("contract review"))
    assert first == second
    assert len(first) == 3
