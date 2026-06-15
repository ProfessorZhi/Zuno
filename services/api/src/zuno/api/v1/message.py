from fastapi import APIRouter, Request

from zuno.api.services.message import MessageDownService, MessageLikeService
from zuno.schema.schemas import resp_200

router = APIRouter(tags=["Message"])


@router.post("/message/like")
async def insert_message_like(request: Request):
    body = await request.json()
    user_input = body.get("user_input")
    agent_output = body.get("agent_output")
    MessageLikeService.create_message_like(
        user_input=user_input,
        agent_output=agent_output,
    )
    return resp_200()


@router.post("/message/down")
async def insert_message_down(request: Request):
    body = await request.json()
    user_input = body.get("user_input")
    agent_output = body.get("agent_output")
    MessageDownService.create_message_down(
        user_input=user_input,
        agent_output=agent_output,
    )
    return resp_200()


__all__ = ["insert_message_down", "insert_message_like", "router"]
