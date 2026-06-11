from typing import List, Optional

from pydantic import BaseModel, Field


class AgentCreateReq(BaseModel):
    name: str = Field(..., description="Agent 名称")
    description: str = Field(..., description="Agent 描述")
    tool_ids: List[str] = Field(default=[], description="绑定的工具 ID")
    llm_id: Optional[str] = Field(None, description="绑定的 LLM ID")
    mcp_ids: List[str] = Field(default=[], description="绑定的 MCP Server")
    knowledge_ids: List[str] = Field(default=[], description="绑定的知识库 ID")
    domain_pack_id: Optional[str] = Field(None, description="Agent 默认 Domain Pack")
    agent_skill_ids: List[str] = Field(default=[], description="绑定的技能")
    enable_memory: bool = Field(True, description="是否启用记忆")
    system_prompt: str = Field(..., description="Agent 系统提示词")
    logo_url: str = Field(..., description="Logo URL")


class AgentUpdateReq(BaseModel):
    agent_id: str = Field(..., description="要更新的 Agent ID")
    name: Optional[str] = Field(None, description="Agent 名称")
    description: Optional[str] = Field(None, description="Agent 描述")
    tool_ids: Optional[List[str]] = Field(None, description="绑定的工具 ID")
    knowledge_ids: Optional[List[str]] = Field(None, description="绑定的知识库 ID")
    domain_pack_id: Optional[str] = Field(None, description="Agent 默认 Domain Pack")
    mcp_ids: Optional[List[str]] = Field(None, description="绑定的 MCP Server")
    llm_id: Optional[str] = Field(None, description="绑定的 LLM ID")
    agent_skill_ids: List[str] = Field(default=[], description="绑定的技能")
    enable_memory: Optional[bool] = Field(True, description="是否启用记忆")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    system_prompt: Optional[str] = Field(None, description="Agent 系统提示词")


class AgentDeleteReq(BaseModel):
    agent_id: str


class AgentSearchReq(BaseModel):
    name: str
