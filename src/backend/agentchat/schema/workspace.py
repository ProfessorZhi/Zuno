from enum import Enum
from typing import Any, List, Literal, NotRequired, TypedDict
from pydantic import BaseModel

class WorkSpaceAgents(Enum):
    SimpleAgent: str = "simple"

    WeChatAgent: str = "wechat-agent"


class WorkSpaceSimpleTask(BaseModel):
    query: str
    model_id: str
    session_id: str
    workspace_mode: str = "normal"
    web_search: bool = True
    plugins: List[str] = []
    mcp_servers: List[str] = []
    knowledge_ids: List[str] = []
    agent_skill_ids: List[str] = []
    execution_mode: str = "tool"
    access_scope: str = "workspace"
    desktop_bridge_url: str | None = None
    desktop_bridge_token: str | None = None
    attachments: List["WorkspaceAttachment"] = []


class WorkspaceAttachment(BaseModel):
    name: str
    url: str
    mime_type: str | None = None
    size: int | None = None


class WorkspaceAgentEventData(TypedDict, total=False):
    phase: str
    status: str
    message: str
    tool_name: str
    tool_type: str
    tool_call_id: str
    arguments: dict[str, Any]
    result: str
    chunk: str
    accumulated: str
    error: str
    done: bool


class WorkspaceAgentStreamEvent(TypedDict):
    event: Literal["status", "tool_call", "tool_result", "final"]
    timestamp: float
    data: WorkspaceAgentEventData
