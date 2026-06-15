import asyncio
from typing import List, Union

from openai import OpenAI


class EmbeddingModel:
    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.api_key = kwargs.get("api_key")
        self.base_url = kwargs.get("base_url")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def embed(self, query: str):
        responses = self.client.embeddings.create(
            model=self.model,
            input=query,
            encoding_format="float",
        )
        return responses.data[0].embedding

    async def embed_async(self, query: Union[str, List[str]]):
        if isinstance(query, str) or (isinstance(query, list) and len(query) <= 10):
            responses = await self.client.embeddings.create(
                model=self.model,
                input=query,
                encoding_format="float",
            )
            if isinstance(query, str):
                return responses.data[0].embedding
            return [response.embedding for response in responses.data]

        semaphore = asyncio.Semaphore(5)

        async def process_batch(batch):
            async with semaphore:
                responses = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float",
                )
                return [response.embedding for response in responses.data]

        batches = [query[index : index + 10] for index in range(0, len(query), 10)]
        results = await asyncio.gather(*(process_batch(batch) for batch in batches))
        return [embedding for batch_result in results for embedding in batch_result]


__all__ = ["EmbeddingModel"]
