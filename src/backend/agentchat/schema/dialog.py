from typing import Optional

from pydantic import BaseModel, Field


class DialogCreateRequest(BaseModel):
    name: str = Field(description='对话名称')
    agent_id: str = Field(description='绑定对象 ID')
    agent_type: str = Field(
        "Agent",
        description="绑定对象类型，当前兼容 Agent 与历史 MCP 标记",
    )


class DialogUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, description='对话名称')
    agent_id: Optional[str] = Field(default=None, description='绑定对象 ID')
    dialog_id: str = Field(description='对话 ID')
    agent_type: Optional[str] = Field(
        "Agent",
        description="绑定对象类型，当前兼容 Agent 与历史 MCP 标记",
    )
