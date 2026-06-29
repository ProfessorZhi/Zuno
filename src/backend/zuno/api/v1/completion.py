import json
from typing import Callable

import loguru
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from starlette.types import Receive

from zuno.api.services.completion import CompletionService
from zuno.api.services.dialog import DialogService
from zuno.api.services.history import HistoryService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.schema.completion import CompletionReq
from zuno.utils.contexts import set_agent_name_context, set_user_id_context

router = APIRouter(tags=["Completion"])


class _LazyClassProxy:
    def __init__(self, module_path: str, class_name: str) -> None:
        self._module_path = module_path
        self._class_name = class_name

    def __call__(self, *args, **kwargs):
        from importlib import import_module

        klass = getattr(import_module(self._module_path), self._class_name)
        return klass(*args, **kwargs)


AgentConfig = _LazyClassProxy("zuno.core.agents.general_agent", "AgentConfig")
GeneralAgent = _LazyClassProxy("zuno.core.agents.general_agent", "GeneralAgent")


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


async def _create_chat_agent(req: CompletionReq, login_user_id: str):
    db_config = await DialogService.get_agent_by_dialog_id(dialog_id=req.dialog_id)
    agent_config = AgentConfig(**db_config)
    agent_config.user_id = login_user_id
    agent_config.dialog_id = req.dialog_id
    agent_config.multi_agent_enabled = bool(req.multi_agent_enabled)
    agent_config.product_mode = req.product_mode
    agent_config.query_method = req.query_method

    chat_agent = GeneralAgent(agent_config)
    await chat_agent.init_agent()
    return chat_agent, agent_config


@router.post("/completion", description="Completion chat endpoint")
async def completion(*, req: CompletionReq, login_user: UserPayload = Depends(get_login_user)):
    chat_agent, agent_config = await _create_chat_agent(req, login_user.user_id)

    set_user_id_context(login_user.user_id)
    set_agent_name_context(agent_config.name)

    original_user_input, messages = await CompletionService.prepare_messages(
        req=req,
        agent_config=agent_config,
    )
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
            await CompletionService.save_memory_turn(
                agent_config=agent_config,
                original_user_input=original_user_input,
                response_content=response_content,
                dialog_id=req.dialog_id,
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


__all__ = ["DialogService", "GeneralAgent", "WatchedStreamingResponse", "completion", "router"]
