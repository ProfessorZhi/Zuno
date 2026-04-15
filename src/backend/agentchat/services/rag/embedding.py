import asyncio
from typing import List, Union

from openai import AsyncOpenAI

from agentchat.settings import app_settings, initialize_app_settings


def _get_embedding_config():
    config = app_settings.multi_models.embedding
    if not config.is_configured():
        raise ValueError("Embedding 模型未配置，请先在系统中新增模型配置")
    return config


def _get_embedding_client() -> tuple[AsyncOpenAI, str]:
    config = _get_embedding_config()
    client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
    return client, config.model_name


async def get_embedding(query: Union[str, List[str]]):
    client, embedding_model = _get_embedding_client()

    if isinstance(query, str) or (isinstance(query, list) and len(query) <= 10):
        responses = await client.embeddings.create(
            model=embedding_model,
            input=query,
            encoding_format="float",
        )

        if isinstance(query, str):
            return responses.data[0].embedding
        return [response.embedding for response in responses.data]

    semaphore = asyncio.Semaphore(5)

    async def process_batch(batch):
        async with semaphore:
            responses = await client.embeddings.create(
                model=embedding_model,
                input=batch,
                encoding_format="float",
            )
            return [response.embedding for response in responses.data]

    batches = [query[i : i + 10] for i in range(0, len(query), 10)]
    tasks = [process_batch(batch) for batch in batches]
    results = await asyncio.gather(*tasks)

    return [embedding for batch_result in results for embedding in batch_result]


if __name__ == "__main__":
    asyncio.run(initialize_app_settings("../../config.yaml"))
    asyncio.run(get_embedding(["测试模型"]))
