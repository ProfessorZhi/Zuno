import json
from typing import Callable, List

import loguru
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from starlette.types import Receive

from agentchat.api.services.dialog import DialogService
from agentchat.api.services.history import HistoryService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.core.agents.general_agent import AgentConfig, GeneralAgent
from agentchat.prompts.completion import SYSTEM_PROMPT
from agentchat.schema.completion import CompletionReq
from agentchat.services.memory.client import memory_client
from agentchat.utils.contexts import set_agent_name_context, set_user_id_context
from agentchat.utils.helpers import (
    build_completion_history_messages,
    build_completion_system_prompt,
    build_completion_user_input,
)

router = APIRouter(tags=["Completion"])


class WatchedStreamingResponse(StreamingResponse):
    def __init__(
        self,
        content,
        callback: Callable = None,
        status_code: int = 200,
        headers=None,
        media_type: str | None = None,
        background=None,
    ):
        super().__init__(content, status_code, headers, media_type, background)
        self.callback = callback

    async def listen_for_disconnect(self, receive: Receive) -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                loguru.logger.info("http.disconnect. stop task and streaming")
                if self.callback:
                    self.callback()
                break


@router.post("/completion", description="Completion chat endpoint")
async def completion(*, req: CompletionReq, login_user: UserPayload = Depends(get_login_user)):
    db_config = await DialogService.get_agent_by_dialog_id(dialog_id=req.dialog_id)
    agent_config = AgentConfig(**db_config)

    set_user_id_context(login_user.user_id)
    set_agent_name_context(agent_config.name)

    agent_config.user_id = login_user.user_id
    agent_config.dialog_id = req.dialog_id
    agent_config.multi_agent_enabled = bool(req.multi_agent_enabled)

    chat_agent = GeneralAgent(agent_config)
    await chat_agent.init_agent()

    original_user_input = req.user_input
    req.user_input = build_completion_user_input(file_url=req.file_url, user_input=req.user_input)

    system_prompt = agent_config.system_prompt if agent_config.system_prompt.strip() else SYSTEM_PROMPT

    if agent_config.enable_memory:
        history = await memory_client.search(query=original_user_input, run_id=req.dialog_id)
        history_text = "\n".join(msg.get("memory", "") for msg in history.get("results", []))
    else:
        history_records = await HistoryService.select_history(dialog_id=req.dialog_id)
        history_text = build_completion_history_messages(history_records)

    system_prompt = build_completion_system_prompt(system_prompt, history_text)

    messages: List[BaseMessage] = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=req.user_input),
    ]
    events = []

    async def general_generate():
        response_content = " "
        try:
            async for event in chat_agent.astream(messages):
                if event.get("type") == "response_chunk":
                    yield f"data: {json.dumps(event)}\n\n"
                    response_content += event["data"].get("chunk")
                else:
                    events.append(event)
                    yield f"data: {json.dumps(event)}\n\n"
        finally:
            if agent_config.enable_memory:
                await memory_client.add(
                    messages=[
                        {"role": "user", "content": original_user_input},
                        {"role": "assistant", "content": response_content},
                    ],
                    run_id=req.dialog_id,
                )

            await HistoryService.save_chat_history(
                role="assistant",
                content=response_content,
                events=events,
                dialog_id=req.dialog_id,
                memory_enable=agent_config.enable_memory,
            )

    await HistoryService.save_chat_history(
        role="user",
        content=original_user_input,
        events=events,
        dialog_id=req.dialog_id,
        memory_enable=agent_config.enable_memory,
    )

    return WatchedStreamingResponse(
        content=general_generate(),
        callback=chat_agent.stop_streaming_callback,
        media_type="text/event-stream",
    )


__all__ = ["WatchedStreamingResponse", "completion", "router"]
