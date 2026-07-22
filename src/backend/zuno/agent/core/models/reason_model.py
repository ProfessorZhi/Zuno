import json
from typing import Any, Dict, List, Union

from langchain_core.messages import AIMessage, BaseMessage, ChatMessage, FunctionMessage, HumanMessage, SystemMessage, ToolCall, ToolMessage
from openai.types.chat import ChatCompletionMessageToolCall
from openai.types.chat.chat_completion_message_tool_call import Function

from zuno.platform.model_gateway import OpenAIChatCompletionsGatewayAdapter


class ReasoningModel:
    def __init__(self, base_url: str, api_key: str, model_name: str):
        self.model_name = model_name
        self.client = OpenAIChatCompletionsGatewayAdapter(base_url=base_url, api_key=api_key)

    async def astream(self, messages: List[BaseMessage]):
        user_messages = [self.convert_message_to_dict(message) for message in messages]
        return await self.client.create(
            model=self.model_name,
            messages=user_messages,
            stream=True,
        )

    def convert_message_to_dict(self, message: BaseMessage) -> dict:
        if isinstance(message, ChatMessage):
            return {"role": message.role, "content": message.content}
        if isinstance(message, HumanMessage):
            return {"role": "user", "content": message.content}
        if isinstance(message, SystemMessage):
            return {"role": "user", "content": message.content}
        if isinstance(message, AIMessage):
            payload = {"role": "assistant", "content": message.content}
            if message.tool_calls:
                payload["function_call"] = None
                payload["tool_calls"] = self.convert_openai_tool_calls(message.tool_calls)
            return payload
        if isinstance(message, (FunctionMessage, ToolMessage)):
            return {
                "role": "tool",
                "content": self._create_tool_content(message.content),
                "name": message.name or message.additional_kwargs.get("name"),
                "tool_call_id": message.tool_call_id,
            }
        raise TypeError(f"Got unknown type {message}")

    def convert_openai_tool_calls(self, tool_calls: List[ToolCall]):
        openai_tool_calls: List[ChatCompletionMessageToolCall] = []
        for tool_call in tool_calls:
            openai_tool_calls.append(
                ChatCompletionMessageToolCall(
                    id=tool_call["id"],
                    type="function",
                    function=Function(
                        arguments=json.dumps(tool_call["args"]),
                        name=tool_call["name"],
                    ),
                )
            )
        return openai_tool_calls

    def _create_tool_content(self, content: Union[str, List[Union[str, Dict[Any, Any]]]]) -> str:
        if isinstance(content, str):
            try:
                if isinstance(json.loads(content), dict):
                    return content
                return json.dumps({"tool_result": content})
            except json.JSONDecodeError:
                return json.dumps({"tool_result": content})
        return json.dumps({"tool_result": content})


__all__ = ["ReasoningModel"]
