import json
from typing import Callable

import loguru
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from starlette.types import Receive

from zuno.api.services.completion import CompletionService
from zuno.api.services.user import UserPayload, get_login_user
from zuno.api.dto.completion import CompletionReq

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
    cutover_mode = CompletionService.resolve_cutover_mode()
    # PHASE22 final engineering closure (P0-1): the Server-owned
    # tenant_id comes from the validated authentication context, never
    # from the request body. The product surface fails closed when no
    # trusted tenant is present in the auth context.
    trusted_tenant = (getattr(login_user, "tenant_id", "") or "").strip()
    async def unified_generate():
        async for event in CompletionService.stream_unified_runtime(
            req=req,
            login_user_id=login_user.user_id,
            cutover_mode=cutover_mode,
            tenant_id=trusted_tenant,
        ):
            yield f"data: {json.dumps(event)}\n\n"

    return WatchedStreamingResponse(
        content=unified_generate(),
        media_type="text/event-stream",
    )


__all__ = ["WatchedStreamingResponse", "completion", "router"]
