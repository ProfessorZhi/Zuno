from typing import Dict, List, Optional

from pydantic import BaseModel


class MCPUserConfigCreateRequest(BaseModel):
    mcp_server_id: str
    config: Optional[Dict] = None


class MCPUserConfigUpdateRequest(BaseModel):
    server_id: str
    config: Optional[List[dict]] = None


class MCPUserConfigTestRequest(BaseModel):
    server_id: str


__all__ = [
    "MCPUserConfigCreateRequest",
    "MCPUserConfigTestRequest",
    "MCPUserConfigUpdateRequest",
]
