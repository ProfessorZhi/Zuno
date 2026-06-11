from typing import Literal, Optional

from pydantic import BaseModel, Field


class SimpleApiParamConfig(BaseModel):
    name: str
    location: Literal["path", "query", "header"] = Field(default="query", alias="in")
    required: bool = False
    description: str = ""
    type: Literal["string", "integer", "number", "boolean"] = "string"

    model_config = {"populate_by_name": True}


class SimpleApiConfig(BaseModel):
    base_url: str
    path: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "GET"
    operation_id: str
    summary: str = ""
    description: str = ""
    params: list[SimpleApiParamConfig] = Field(default_factory=list)
    body_schema: Optional[dict] = None
    response_schema: Optional[dict] = None


class ToolCreateReq(BaseModel):
    display_name: str
    description: str
    logo_url: str
    runtime_type: str = Field(default="remote_api")
    auth_config: dict = None
    cli_config: dict = None
    openapi_schema: dict = None
    simple_api_config: Optional[SimpleApiConfig] = None
    source_metadata: Optional[dict] = None

class ToolUpdateReq(BaseModel):
    tool_id: str
    description: str = None
    logo_url: str = None
    runtime_type: str = Field(default="remote_api")
    auth_config: dict = None
    cli_config: dict = None
    display_name: str = None
    openapi_schema: dict = None
    simple_api_config: Optional[SimpleApiConfig] = None
    source_metadata: Optional[dict] = None

class ToolDeleteReq(BaseModel):
    tool_id: str


class ToolConnectivityReq(BaseModel):
    runtime_type: str = Field(default="remote_api")
    auth_config: dict = None
    cli_config: dict = None
    openapi_schema: dict = None
    simple_api_config: Optional[SimpleApiConfig] = None
    probe_operation_id: str = ""
    probe_args: dict = Field(default_factory=dict)


class ToolConnectivityResp(BaseModel):
    ok: bool
    runtime_type: Literal["remote_api", "cli"]
    summary: str
    details: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    executed: bool = False
    operation_id: Optional[str] = None
    tested_url: Optional[str] = None
    command: Optional[str] = None


class RemoteApiAssistReq(BaseModel):
    endpoint_url: str = ""
    docs_url: str = ""
    docs_urls: list[str] = Field(default_factory=list)
    sample_curl: str = ""
    api_key: str = ""
    api_key_name: str = ""
    auth_type: Literal["none", "bearer", "basic", "api_key_query", "api_key_header"] = "none"
    method: Literal["", "GET", "POST", "PUT", "PATCH", "DELETE"] = ""
    display_name: str = ""
    description: str = ""


class RemoteApiAssistResp(BaseModel):
    display_name: str
    description: str
    simple_api_config: SimpleApiConfig
    auth_config: dict = Field(default_factory=dict)
    openapi_schema: dict
    probe_args: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class CLIToolPreviewReq(BaseModel):
    tool_dir: str = ""
    source_type: Literal["local_directory", "executable", "npm_package", "python_package", "github_repo"] = "local_directory"
    install_source: str = ""
    command: str = ""
    doc_url: str = ""
    docs_url: str = ""
    github_url: str = ""
    local_path: str = ""
    notes: str = ""


class CLIToolPreviewCommand(BaseModel):
    command: str
    args_template: list[str] = Field(default_factory=list)
    cwd_mode: Literal["tool_dir", "workspace", "custom"] = "tool_dir"
    cwd: Optional[str] = None
    source: str
    confidence: float = 0.0
    notes: list[str] = Field(default_factory=list)
    label: Optional[str] = None
    reason: Optional[str] = None
    healthcheck_command: Optional[str] = None


class CLIToolCredentialModeSuggestion(BaseModel):
    mode: Literal["none", "env", "profiles", "manual"] = "none"
    confidence: float = 0.0
    reason: str = ""
    env_vars: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class CLIToolStructuredSuggestion(BaseModel):
    id: str
    title: str
    summary: str
    confidence: float = 0.0
    notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    detected_files: list[str] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
    command: Optional[str] = None
    args_template: list[str] = Field(default_factory=list)
    cwd_mode: Optional[Literal["tool_dir", "workspace", "custom"]] = None
    cwd: Optional[str] = None
    display_name: Optional[str] = None
    tool_name: Optional[str] = None
    tool_dir: Optional[str] = None
    install_source: Optional[str] = None
    install_command: Optional[str] = None
    healthcheck_command: Optional[str] = None


class CLIToolPreviewResp(BaseModel):
    tool_dir: str
    source_type: Literal["local_directory", "executable", "npm_package", "python_package", "github_repo"] = "local_directory"
    install_source: str = ""
    doc_url: str = ""
    docs_url: str = ""
    github_url: str = ""
    local_path: str = ""
    resolved_path: str
    exists: bool
    suggested_name: str
    default_description: str
    readme_path: Optional[str] = None
    readme_summary: Optional[str] = None
    command_candidates: list[CLIToolPreviewCommand] = Field(default_factory=list)
    recommended: Optional[CLIToolPreviewCommand] = None
    candidates: list[CLIToolPreviewCommand] = Field(default_factory=list)
    install_suggestions: list[CLIToolPreviewCommand] = Field(default_factory=list)
    run_suggestions: list[CLIToolPreviewCommand] = Field(default_factory=list)
    healthcheck_suggestions: list[CLIToolPreviewCommand] = Field(default_factory=list)
    credential_mode_suggestions: list[CLIToolCredentialModeSuggestion] = Field(default_factory=list)
    display_name: Optional[str] = None
    description: Optional[str] = None
    readme_excerpt: Optional[str] = None
    detected_files: list[str] = Field(default_factory=list)
    suggested_install_command: Optional[str] = None
    suggested_healthcheck_command: Optional[str] = None
    assist_summary: Optional[str] = None
    assist_sources: list[str] = Field(default_factory=list)
    structured_suggestions: list[CLIToolStructuredSuggestion] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
