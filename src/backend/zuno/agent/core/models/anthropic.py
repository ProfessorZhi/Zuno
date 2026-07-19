from zuno.platform.model_gateway import (
    AnthropicMessagesGatewayAdapter,
    AsyncAnthropicMessagesGatewayAdapter,
)


class DeepAnthropic:
    def __init__(self, api_key, model, base_url, max_tokens=None):
        self.max_tokens = max_tokens or 1024
        self.model = model
        self.client = AnthropicMessagesGatewayAdapter(base_url=base_url, api_key=api_key)

    def invoke(self, messages, available_tools=None, max_tokens=None):
        return self.client.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            messages=messages,
            tools=available_tools,
        )

    async def invoke_stream(self, messages, available_tools=None, max_tokens=None):
        with self.client.stream(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            messages=messages,
            tools=available_tools,
        ) as stream:
            for text in stream.text_stream:
                yield text


class DeepAsyncAnthropic:
    def __init__(self, api_key, model, base_url, max_tokens=None):
        self.max_tokens = max_tokens or 1024
        self.model = model
        self.client = AsyncAnthropicMessagesGatewayAdapter(base_url=base_url, api_key=api_key)

    async def ainvoke(self, messages, available_tools=None, max_tokens=None):
        return await self.client.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            messages=messages,
            tools=available_tools,
        )

    async def ainvoke_stream(self, messages, available_tools=None, max_tokens=None):
        async with self.client.stream(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            messages=messages,
            tools=available_tools,
        ) as stream:
            async for text in stream.text_stream:
                yield text
