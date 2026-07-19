from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk

from zuno.platform.model_gateway import ModelGateway, build_default_model_gateway
from zuno.platform.model_roles import ModelRole


BACKTICK_PATTERN = r"(?:^|\n)```(.*?)(?:```(?:\n|$))"


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def build_weather_agent(
    *,
    gateway: ModelGateway | None = None,
    binding: Mapping[str, Any] | None = None,
):
    model_gateway = gateway or build_default_model_gateway()
    chat_model = model_gateway.get_chat_model(
        binding=dict(binding or {}),
        role=ModelRole.EXECUTOR,
    )
    return create_agent(
        model=chat_model,
        tools=[get_weather],
    )


async def run_weather_agent_demo(
    city: str = "SF",
    *,
    gateway: ModelGateway | None = None,
    binding: Mapping[str, Any] | None = None,
) -> list[Any]:
    agent = build_weather_agent(gateway=gateway, binding=binding)
    messages: list[Any] = []
    async for token, metadata in agent.astream(
        {"messages": [{"role": "user", "content": f"What is the weather in {city}?"}]},
        stream_mode=["messages", "updates", "values"],
    ):
        if token == "values":
            messages = metadata.get("messages", [])
        if token == "messages":
            if isinstance(metadata[0], AIMessageChunk) and metadata[0].content:
                break
    return messages


def extract_and_combine_codeblocks(text: str) -> str:
    """
    Extracts all codeblocks from a text string and combines them into a single code string.

    Args:
        text: A string containing zero or more codeblocks, where each codeblock is
            surrounded by triple backticks (```).

    Returns:
        A string containing the combined code from all codeblocks, with each codeblock
        separated by a newline.

    Example:
        text = '''Here's some code:

        ```python
        print('hello')
        ```
        And more:

        ```
        print('world')
        ```'''

        result = extract_and_combine_codeblocks(text)

        Result:

        print('hello')

        print('world')
    """
    code_blocks = re.findall(BACKTICK_PATTERN, text, re.DOTALL)

    if not code_blocks:
        return ""

    processed_blocks = []
    for block in code_blocks:
        block = block.strip()
        lines = block.split("\n")
        if lines and (not lines[0].strip() or " " not in lines[0].strip()):
            block = "\n".join(lines[1:])

        processed_blocks.append(block)

    return "\n\n".join(processed_blocks)


if __name__ == "__main__":
    asyncio.run(run_weather_agent_demo())
