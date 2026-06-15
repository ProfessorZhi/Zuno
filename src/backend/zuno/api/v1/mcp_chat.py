from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from zuno.api.services.dialog import DialogService
from zuno.api.services.history import HistoryService
from zuno.api.services.mcp_chat import MCPChatAgent

router = APIRouter(tags=["MCP-Chat"])


@router.post("/mcp_chat", description="MCP chat endpoint")
async def chat(
    user_input: str = Body(description="user input"),
    dialog_id: str = Body(description="dialog id"),
):
    agent = await DialogService.get_agent_by_dialog_id(dialog_id)
    mcp_chat_agent = MCPChatAgent(**agent)
    await mcp_chat_agent.init_MCP_Server()

    async def general_generate():
        assistant_result = ""
        async for text in await mcp_chat_agent.ainvoke(user_input, dialog_id, True):
            assistant_result += text
            yield f"{text}\n\n"
        yield "[DONE]"
        await HistoryService.save_chat_history("assistant", assistant_result, dialog_id)

    await HistoryService.save_chat_history("user", user_input, dialog_id)
    DialogService.update_dialog_time(dialog_id)
    return StreamingResponse(general_generate(), media_type="text/event-stream")


__all__ = ["chat", "router"]
