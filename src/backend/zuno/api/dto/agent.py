from typing import List, Optional

from pydantic import BaseModel, Field


class AgentCreateReq(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    tool_ids: List[str] = Field(default=[], description="Bound tool IDs")
    llm_id: Optional[str] = Field(None, description="Bound LLM ID")
    mcp_ids: List[str] = Field(default=[], description="Bound MCP servers")
    knowledge_ids: List[str] = Field(default=[], description="Bound knowledge IDs")
    graphrag_project_id: Optional[str] = Field(None, description="Default GraphRAG Project")
    agent_skill_ids: List[str] = Field(default=[], description="Bound skill IDs")
    enable_memory: bool = Field(True, description="Whether memory is enabled")
    system_prompt: str = Field(..., description="Agent system prompt")
    logo_url: str = Field(..., description="Logo URL")

class AgentUpdateReq(BaseModel):
    agent_id: str = Field(..., description="Agent ID to update")
    name: Optional[str] = Field(None, description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    tool_ids: Optional[List[str]] = Field(None, description="Bound tool IDs")
    knowledge_ids: Optional[List[str]] = Field(None, description="Bound knowledge IDs")
    graphrag_project_id: Optional[str] = Field(None, description="Default GraphRAG Project")
    mcp_ids: Optional[List[str]] = Field(None, description="Bound MCP servers")
    llm_id: Optional[str] = Field(None, description="Bound LLM ID")
    agent_skill_ids: List[str] = Field(default=[], description="Bound skill IDs")
    enable_memory: Optional[bool] = Field(True, description="Whether memory is enabled")
    logo_url: Optional[str] = Field(None, description="Logo URL")
    system_prompt: Optional[str] = Field(None, description="Agent system prompt")

class AgentDeleteReq(BaseModel):
    agent_id: str


class AgentSearchReq(BaseModel):
    name: str


__all__ = [
    "AgentCreateReq",
    "AgentDeleteReq",
    "AgentSearchReq",
    "AgentUpdateReq",
]
