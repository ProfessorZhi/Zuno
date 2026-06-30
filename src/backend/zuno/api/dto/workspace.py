from enum import Enum
from typing import Any, List, Literal, TypedDict

from pydantic import BaseModel, Field


WorkspaceProductMode = Literal[
    "enterprise_kb",
    "hr_resume",
    "contract_review",
    "general_agent",
]
WorkspaceTaskStatus = Literal[
    "created",
    "context_building",
    "planning",
    "running",
    "approval_waiting",
    "resuming",
    "finalizing",
    "completed",
    "failed",
    "cancelled",
]
WORKSPACE_TASK_STATUS_FLOW = [
    "created",
    "context_building",
    "planning",
    "running",
    "approval_waiting",
    "resuming",
    "finalizing",
    "completed",
    "failed",
    "cancelled",
]


class WorkSpaceAgents(Enum):
    SimpleAgent: str = "simple"
    WeChatAgent: str = "wechat-agent"


class WorkspaceTaskBudget(BaseModel):
    max_steps: int | None = None
    max_tokens: int | None = None
    timeout_seconds: int | None = None
    cost_ceiling: float | None = None


class WorkspaceOutputContract(BaseModel):
    artifact_kinds: list[str] = Field(default_factory=list)
    citation_required: bool = True
    trace_required: bool = True
    format: str = "markdown"


class WorkSpaceSimpleTask(BaseModel):
    query: str
    model_id: str
    session_id: str
    workspace_id: str | None = None
    user_id: str | None = None
    task_id: str | None = None
    trace_id: str | None = None
    goal: str | None = None
    product_mode: WorkspaceProductMode = "general_agent"
    knowledge_space_ids: List[str] = Field(default_factory=list)
    uploaded_file_ids: List[str] = Field(default_factory=list)
    approval_mode: str = "auto"
    budget: WorkspaceTaskBudget | None = None
    output_contract: WorkspaceOutputContract | None = None
    workspace_mode: str = "normal"
    agent_name: str | None = None
    agent_id: str | None = None
    web_search: bool = True
    plugins: List[str] = Field(default_factory=list)
    mcp_servers: List[str] = Field(default_factory=list)
    knowledge_ids: List[str] = Field(default_factory=list)
    retrieval_mode: str = "auto"
    multi_agent_enabled: bool = False
    agent_skill_ids: List[str] = Field(default_factory=list)
    execution_mode: str = "tool"
    access_scope: str = "workspace"
    desktop_bridge_url: str | None = None
    desktop_bridge_token: str | None = None
    attachments: List["WorkspaceAttachment"] = Field(default_factory=list)


class WorkspaceAttachment(BaseModel):
    name: str
    url: str
    mime_type: str | None = None
    size: int | None = None


class WorkspaceProductObjectBase(BaseModel):
    workspace_id: str
    owner: str | None = None
    status: str = "active"
    policy_scope: str = "workspace"
    trace_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    retention_policy: str | None = None


class WorkspaceContract(WorkspaceProductObjectBase):
    members: list[str] = Field(default_factory=list)


class KnowledgeSpaceContract(WorkspaceProductObjectBase):
    knowledge_space_id: str
    graph_project_id: str | None = None
    index_version: str | None = None
    acl_policy: str = "workspace"


class WorkspaceSessionContract(WorkspaceProductObjectBase):
    session_id: str
    user_id: str
    thread_id: str | None = None
    active_task_id: str | None = None


class WorkspaceTaskContract(WorkspaceProductObjectBase):
    task_id: str
    session_id: str
    goal: str
    product_mode: WorkspaceProductMode = "general_agent"
    status: WorkspaceTaskStatus = "created"
    budget: WorkspaceTaskBudget = Field(default_factory=WorkspaceTaskBudget)


class UploadedFileContract(WorkspaceProductObjectBase):
    file_id: str
    mime_type: str
    hash: str
    security_label: str = "internal"
    parse_status: str = "created"


class ArtifactContract(WorkspaceProductObjectBase):
    artifact_id: str
    task_id: str
    kind: str
    uri: str
    hash: str | None = None
    download_policy: str = "workspace"


class TraceEventContract(BaseModel):
    event_id: str
    task_id: str
    trace_id: str
    type: str
    timestamp: float
    payload: dict[str, Any] = Field(default_factory=dict)


class CitationContract(BaseModel):
    citation_id: str
    evidence_id: str
    document_id: str
    block_id: str
    source_span: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None


class FeedbackContract(BaseModel):
    feedback_id: str
    task_id: str
    rating: int | None = None
    label: str | None = None
    comment: str | None = None
    dataset_candidate: bool = False
    created_at: str | None = None


class WorkspaceProductStreamEvent(BaseModel):
    event_id: str
    task_id: str
    trace_id: str
    type: str
    status: WorkspaceTaskStatus | str
    timestamp: float
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkspaceAgentEventData(TypedDict, total=False):
    event_id: str
    task_id: str
    trace_id: str
    artifact_id: str
    citation_ids: list[str]
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
    retrieval_mode: str
    first_mode: str
    final_mode: str
    fallback_reason: str
    round_count: int
    second_pass_used: bool
    rewritten_query_used: bool
    query_variants: list[str]
    rounds: list[dict[str, Any]]


class WorkspaceAgentStreamEvent(TypedDict):
    event: Literal["status", "tool_call", "tool_result", "final"]
    timestamp: float
    data: WorkspaceAgentEventData


__all__ = [
    "ArtifactContract",
    "CitationContract",
    "FeedbackContract",
    "KnowledgeSpaceContract",
    "TraceEventContract",
    "UploadedFileContract",
    "WORKSPACE_TASK_STATUS_FLOW",
    "WorkSpaceAgents",
    "WorkSpaceSimpleTask",
    "WorkspaceAgentEventData",
    "WorkspaceAgentStreamEvent",
    "WorkspaceAttachment",
    "WorkspaceContract",
    "WorkspaceOutputContract",
    "WorkspaceProductObjectBase",
    "WorkspaceProductStreamEvent",
    "WorkspaceSessionContract",
    "WorkspaceTaskBudget",
    "WorkspaceTaskContract",
]
