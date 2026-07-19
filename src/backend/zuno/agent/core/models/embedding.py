from typing import List, Union

from zuno.platform.model_gateway import OpenAIEmbeddingGatewayAdapter


class EmbeddingModel:
    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.api_key = kwargs.get("api_key")
        self.base_url = kwargs.get("base_url")
        self.client = OpenAIEmbeddingGatewayAdapter(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
        )

    def embed(self, query: str):
        return self.client.embed(query)

    async def embed_async(self, query: Union[str, List[str]]):
        return await self.client.embed_async(query)


__all__ = ["EmbeddingModel"]
