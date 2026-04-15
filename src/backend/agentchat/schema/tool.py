from typing import Literal, Optional

from pydantic import BaseModel, Field


class ToolCreateReq(BaseModel):
    display_name: str
    description: str
    logo_url: str
    runtime_type: str = Field(default="remote_api")
    auth_config: dict = None
    cli_config: dict = None
    openapi_schema: dict = None

class ToolUpdateReq(BaseModel):
    tool_id: str
    description: str = None
    logo_url: str = None
    runtime_type: str = Field(default="remote_api")
    auth_config: dict = None
    cli_config: dict = None
    display_name: str = None
    openapi_schema: dict = None

class ToolDeleteReq(BaseModel):
    tool_id: str


class CLIToolPreviewReq(BaseModel):
    tool_dir: str = Field(min_length=1)


class CLIToolPreviewCommand(BaseModel):
    command: str
    args_template: list[str] = Field(default_factory=list)
    cwd_mode: Literal["tool_dir", "workspace", "custom"] = "tool_dir"
    cwd: Optional[str] = None
    source: str
    confidence: float = 0.0
    notes: list[str] = Field(default_factory=list)


class CLIToolPreviewResp(BaseModel):
    tool_dir: str
    resolved_path: str
    exists: bool
    suggested_name: str
    default_description: str
    readme_path: Optional[str] = None
    readme_summary: Optional[str] = None
    command_candidates: list[CLIToolPreviewCommand] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
