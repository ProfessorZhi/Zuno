from typing import List, Union

from zuno.platform.model_gateway import build_openai_embedding_gateway_adapter


async def get_embedding(query: Union[str, List[str]], config_override=None):
    client = build_openai_embedding_gateway_adapter(config_override)
    return await client.embed_async(query)
