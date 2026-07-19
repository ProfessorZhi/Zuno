from typing import List, Union

from zuno.core.models.manager import ModelManager
from zuno.platform.model_gateway import OpenAIEmbeddingGatewayAdapter


def _normalize_model_config(config_override):
    if not config_override:
        return None
    if hasattr(config_override, "model_name"):
        return config_override
    return type("EmbeddingConfig", (), config_override)()


def _get_embedding_config(config_override=None):
    return _normalize_model_config(config_override) or ModelManager.get_model_config("embedding", "Embedding model")


def _get_embedding_client(config_override=None) -> OpenAIEmbeddingGatewayAdapter:
    config = _get_embedding_config(config_override)
    return OpenAIEmbeddingGatewayAdapter(
        api_key=config.api_key,
        base_url=config.base_url,
        model=config.model_name,
    )


async def get_embedding(query: Union[str, List[str]], config_override=None):
    client = _get_embedding_client(config_override)
    return await client.embed_async(query)
