from fastapi import APIRouter, Body, HTTPException

from zuno.api.services.mcp_chat import MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND

router = APIRouter(tags=["MCP-Chat"])


@router.post("/mcp_chat", description="MCP chat endpoint")
async def chat(
    user_input: str = Body(description="user input"),
    dialog_id: str = Body(description="dialog id"),
):
    del user_input, dialog_id
    # PHASE22: this legacy endpoint has no canonical tenant / workspace /
    # principal / security / budget binding. It must fail closed before
    # resolving a dialog, constructing a legacy agent, or touching a model /
    # MCP provider. Product execution belongs to the canonical workspace
    # runtime and ToolInvocationGateway surface.
    raise HTTPException(
        status_code=503,
        detail=MCP_CHAT_CANONICAL_RUNTIME_NOT_BOUND,
    )


__all__ = ["chat", "router"]
