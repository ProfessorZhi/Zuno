from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SharedContractEntry(BaseModel):
    owner: str
    path: str
    fields: list[str]
    serialization: Literal["pydantic", "enum", "dataclass-facade"] = "pydantic"
    consuming_phases: list[str] = Field(default_factory=list)
    notes: str = ""


class RetrievalProfile(StrEnum):
    STANDARD = "standard"
    DEEP = "deep"
    DEEP_WITHOUT_GRAPH = "deep_without_graph"


class FileInputFormat(StrEnum):
    TEXT = "text"
    MARKDOWN = "markdown"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    CODE = "code"
    PDF = "pdf"
    OFFICE = "office"
    IMAGE = "image"
    SCANNED = "scanned"
    BINARY = "binary"
    UNKNOWN = "unknown"


class ParserCapabilityStatus(StrEnum):
    CURRENT = "current"
    FALLBACK_CURRENT = "fallback_current"
    TARGET_BLOCKED = "target_blocked"
    DISABLED = "disabled"
    UNKNOWN_NEEDS_TEST = "unknown_needs_test"


class ParseJobStatus(StrEnum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    DEAD_LETTER = "dead_letter"


class AgentRun(BaseModel):
    run_id: str
    task_id: str
    session_id: str
    workspace_id: str
    user_id: str
    state: str = "created"
    strategy: str | None = None
    selected_skill: str | None = None
    trace_id: str | None = None


class ContextPack(BaseModel):
    context_pack_id: str
    user_goal: str
    task_state: dict[str, Any] = Field(default_factory=dict)
    selected_memory_refs: list[str] = Field(default_factory=list)
    selected_evidence_refs: list[str] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    safety_policy: dict[str, Any] = Field(default_factory=dict)
    output_contract: dict[str, Any] = Field(default_factory=dict)
    budget: dict[str, Any] = Field(default_factory=dict)


class RetrievalDecision(BaseModel):
    requested_profile: RetrievalProfile
    effective_profile: RetrievalProfile
    fallback_reason: str | None = None
    retrievers_used: list[str] = Field(default_factory=list)
    evidence_count: int = 0
    citation_coverage: float = 0.0
    trace_id: str | None = None


class EvidenceBundle(BaseModel):
    evidence_ids: list[str] = Field(default_factory=list)
    citation_ids: list[str] = Field(default_factory=list)
    evidence_count: int = 0
    citation_coverage: float = 0.0
    unsupported_claim_inputs: list[str] = Field(default_factory=list)
    acl_scopes: list[str] = Field(default_factory=list)


class CitationLineage(BaseModel):
    citation_id: str
    source_object_id: str | None = None
    document_version_id: str
    block_id: str
    chunk_id: str | None = None
    parse_job_id: str | None = None
    parse_attempt_id: str | None = None
    source_sha256: str | None = None
    source_span: dict[str, Any] = Field(default_factory=dict)


class ObjectStoreRef(BaseModel):
    storage_uri: str
    source_sha256: str
    content_type: str | None = None
    size_bytes: int = 0


class SourceObject(BaseModel):
    source_id: str
    workspace_id: str
    filename: str
    declared_format: FileInputFormat = FileInputFormat.UNKNOWN
    mime_type: str
    object_ref: ObjectStoreRef
    acl_scope: str = "workspace"
    sensitivity_tags: list[str] = Field(default_factory=list)


class BinarySourceObject(SourceObject):
    declared_format: FileInputFormat = FileInputFormat.BINARY
    bytes_verified: bool = False
    parser_dependency_probe: dict[str, Any] = Field(default_factory=dict)


class ObjectStoreResult(BaseModel):
    ok: bool
    object_ref: ObjectStoreRef | None = None
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)


class ParserDependencyProbe(BaseModel):
    provider_id: str
    capability: str
    status: Literal["present", "missing", "disabled", "unsupported", "target_blocked"]
    blocked_reason: str | None = None
    diagnostics: dict[str, Any] = Field(default_factory=dict)


class ParserWorkerSpec(BaseModel):
    worker_id: str
    parser_id: str
    supported_formats: list[FileInputFormat] = Field(default_factory=list)
    dependency_probe: ParserDependencyProbe | None = None
    max_attempts: int = 3


class ParseAttempt(BaseModel):
    parse_attempt_id: str
    parse_job_id: str
    attempt: int = 1
    status: ParseJobStatus = ParseJobStatus.ACCEPTED
    started_at: str | None = None
    finished_at: str | None = None
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)


class ParserWorkerResult(BaseModel):
    parse_job_id: str
    status: ParseJobStatus
    document_version_id: str | None = None
    parse_attempt: ParseAttempt | None = None
    blocked_reason: str | None = None
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)


class IndexWorkerSpec(BaseModel):
    worker_id: str
    index_targets: list[str] = Field(default_factory=lambda: ["bm25", "vector"])
    max_attempts: int = 3


class IndexWorkerResult(BaseModel):
    index_job_id: str
    status: ParseJobStatus
    index_manifest_id: str | None = None
    chunk_count: int = 0
    blocked_reason: str | None = None
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)


class QueueMessage(BaseModel):
    message_id: str
    topic: str
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    status: Literal["queued", "consumed", "acked", "failed", "dead_letter"] = "queued"
    attempt: int = 0
    trace_id: str | None = None


class QueueBackendResult(BaseModel):
    ok: bool
    message_id: str | None = None
    status: str
    dependency_probe: ParserDependencyProbe | None = None
    error: str | None = None


class OutboxEvent(BaseModel):
    event_id: str
    aggregate_id: str
    topic: str
    payload: dict[str, Any] = Field(default_factory=dict)
    published: bool = False


class DeadLetterRecord(BaseModel):
    dead_letter_id: str
    source_message_id: str
    reason: str
    retryable: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


class ReconcilerFinding(BaseModel):
    finding_id: str
    finding_type: str
    severity: str = "warning"
    entity_id: str
    recommended_action: str
    details: dict[str, Any] = Field(default_factory=dict)


class OCRVLMEnrichmentResult(BaseModel):
    status: Literal["succeeded", "blocked", "target_blocked", "failed"]
    confidence: float | None = None
    model_id: str | None = None
    prompt_version: str | None = None
    derived_from: list[str] = Field(default_factory=list)
    review_required: bool = True
    privacy_gate: dict[str, Any] = Field(default_factory=dict)
    budget_gate: dict[str, Any] = Field(default_factory=dict)
    blocked_reason: str | None = None


class KnowledgeSpaceConfig(BaseModel):
    name: str
    workspace_id: str
    description: str = ""
    acl_scope: str = "workspace"
    default_sensitivity: str = "internal"
    index_capabilities: dict[str, Any] = Field(default_factory=dict)
    parser_config: dict[str, Any] = Field(default_factory=dict)
    chunk_config: dict[str, Any] = Field(default_factory=dict)
    embedding_config: dict[str, Any] = Field(default_factory=dict)
    graph_config: dict[str, Any] = Field(default_factory=dict)
    ocr_vlm_config: dict[str, Any] = Field(default_factory=dict)
    retrieval_defaults: dict[str, str] = Field(default_factory=lambda: {"default_profile": "standard"})
    security_policy: dict[str, Any] = Field(default_factory=dict)


class FileIngestionStatus(BaseModel):
    file_id: str
    parse_status: str
    index_status: str
    status_timeline: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    dependency_probe: ParserDependencyProbe | None = None
    retry_count: int = 0
    last_error: str | None = None


class ChangeImpactPreview(BaseModel):
    change_type: str
    triggered_action: str
    affected_file_count: int = 0
    affected_chunk_count: int = 0
    affects_existing_artifacts: bool = False
    requires_external_provider: bool = False
    may_create_blocked_state: bool = False
    estimated_duration_ms: int | None = None


class CapabilityPolicy(BaseModel):
    capability_id: str
    capability_type: str
    workspace_scope: str
    required_roles: list[str] = Field(default_factory=list)
    approval_required: bool = False
    side_effect_level: str = "read"
    network_policy: str = "deny"
    credential_policy: str = "none"
    data_access_policy: str = "workspace_acl"
    audit_policy: str = "trace"


class CapabilityRiskProfile(BaseModel):
    read_only: bool = True
    write_workspace: bool = False
    external_write: bool = False
    network_access: bool = False
    credential_access: bool = False
    code_execution: bool = False
    browser_control: bool = False


class CapabilityAuditEvent(BaseModel):
    capability_id: str
    task_id: str
    decision: str
    reason: str
    latency_ms: float | None = None
    error: str | None = None
    approval_id: str | None = None


class CapabilityCard(BaseModel):
    capability_id: str
    capability_type: str
    description: str
    policy: CapabilityPolicy
    risk_profile: CapabilityRiskProfile = Field(default_factory=CapabilityRiskProfile)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillCard(BaseModel):
    skill_id: str
    skill_version: str
    when_to_use: str
    task_type: str
    recommended_retrieval_profile: RetrievalProfile = RetrievalProfile.STANDARD
    required_evidence: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    memory_scopes: list[str] = Field(default_factory=list)
    output_contract: dict[str, Any] = Field(default_factory=dict)
    safety_policy: str = "default"
    eval_rubric: dict[str, Any] = Field(default_factory=dict)
    max_steps: int = 3
    reflection_policy: str = "optional"


class ToolCard(BaseModel):
    tool_id: str
    capability_id: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    permission: CapabilityPolicy
    trace_fields: list[str] = Field(default_factory=list)


class PlanStep(BaseModel):
    step_id: str
    goal: str
    action_type: str
    dependencies: list[str] = Field(default_factory=list)
    input_refs: list[str] = Field(default_factory=list)
    expected_output: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    allowed_capabilities: list[str] = Field(default_factory=list)
    retrieval_policy_ref: str | None = None
    tool_policy_ref: str | None = None
    model_role: str | None = None
    failure_conditions: list[str] = Field(default_factory=list)
    budget: dict[str, Any] = Field(default_factory=dict)
    timeout_ms: int | None = None
    attempt: int = 0


class PlanState(BaseModel):
    plan_id: str
    status: str = "created"
    steps: list[PlanStep] = Field(default_factory=list)
    current_step_id: str | None = None


class StrategySelectorOutput(BaseModel):
    strategy: Literal[
        "direct_answer",
        "react",
        "plan_execute",
        "plan_execute_with_replan",
        "reflection_enabled",
        "reflexion_enabled",
    ]
    reason: str
    selected_skill: str | None = None
    retrieval_profile: RetrievalProfile | None = None


class SelectedSkill(BaseModel):
    skill_id: str
    skill_version: str | None = None
    selection_mode: Literal["automatic", "pinned"] = "automatic"
    reason: str = ""
    allowed_tools: list[str] = Field(default_factory=list)
    required_evidence: list[str] = Field(default_factory=list)
    retrieval_profile: RetrievalProfile = RetrievalProfile.STANDARD


class CapabilityPlan(BaseModel):
    allowed_capabilities: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    blocked_capability_reasons: dict[str, str] = Field(default_factory=dict)
    approval_required_tools: list[str] = Field(default_factory=list)
    executed_tools: list[str] = Field(default_factory=list)
    risk_summary: dict[str, Any] = Field(default_factory=dict)


class RetrievalPlan(BaseModel):
    requested_profile: RetrievalProfile
    effective_profile: RetrievalProfile
    retrievers_used: list[str] = Field(default_factory=list)
    fallback_reason: str | None = None
    evidence_requirements: list[str] = Field(default_factory=list)


class ReflectionVerdict(BaseModel):
    decision: Literal["continue", "finish", "retrieve_more", "replan", "ask_user", "refuse"]
    evidence_enough: bool = False
    citation_coverage: float = 0.0
    unsupported_claims: list[str] = Field(default_factory=list)
    security_blocked: bool = False
    reason: str = ""


class ReplanDecision(BaseModel):
    trigger: str
    replaced_step_ids: list[str] = Field(default_factory=list)
    new_steps: list[PlanStep] = Field(default_factory=list)
    reason: str = ""


class ReflexionLesson(BaseModel):
    lesson_id: str
    task_type: str
    failure_type: str
    root_cause: str
    lesson: str
    recommended_fix: str
    trigger_condition: str
    evidence_refs: list[str] = Field(default_factory=list)
    scope: str = "workspace"
    safety_label: str = "internal"
    review_status: str = "candidate"
    expiry: str | None = None


class TraceRecord(BaseModel):
    event_id: str
    task_id: str
    trace_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class PlannerOutput(BaseModel):
    task_id: str
    trace_id: str
    strategy: StrategySelectorOutput
    selected_skill: SelectedSkill | None = None
    capability_plan: CapabilityPlan = Field(default_factory=CapabilityPlan)
    retrieval_plan: RetrievalPlan
    plan_state: PlanState
    reflection_verdict: ReflectionVerdict = Field(default_factory=lambda: ReflectionVerdict(decision="continue"))
    replan_decision: ReplanDecision | None = None
    reflexion_lesson: ReflexionLesson | None = None
    trace_events: list[TraceRecord] = Field(default_factory=list)


class TraceMetric(BaseModel):
    name: str
    value: float | int | str
    unit: str | None = None
    trace_event_ids: list[str] = Field(default_factory=list)


class CostMetric(BaseModel):
    model_id: str | None = None
    token_count: int = 0
    cost_estimate: float = 0.0
    latency_ms: float = 0.0
    retry_count: int = 0
    timeout_count: int = 0


class ConversationRunMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str
    session_id: str
    workspace_id: str
    user_id: str
    selected_knowledge_spaces: list[str] = Field(default_factory=list)
    retrieval_profiles: dict[str, str] = Field(default_factory=dict)
    selected_skill: str | None = None
    strategy: str | None = None
    model_settings: dict[str, Any] = Field(default_factory=dict, alias="model_config")
    started_at: str | None = None
    ended_at: str | None = None


class StageMetrics(BaseModel):
    stage_name: str
    latency_ms: float = 0.0
    token_count: int = 0
    cost_estimate: float = 0.0
    model_id: str | None = None
    error_count: int = 0
    retry_count: int = 0
    security_block_count: int = 0
    trace_event_ids: list[str] = Field(default_factory=list)


class IngestionMetrics(BaseModel):
    files_uploaded: int = 0
    files_indexed: int = 0
    files_failed: int = 0
    files_blocked: int = 0
    parse_duration_ms: float = 0.0
    index_duration_ms: float = 0.0
    parser_id: str | None = None
    parser_format: str | None = None
    dependency_status: str | None = None
    blocked_reason: str | None = None
    retry_count: int = 0
    dead_letter_count: int = 0
    reconciler_findings: list[str] = Field(default_factory=list)
    ocr_vlm_pages: int = 0
    ocr_vlm_cost_estimate: float = 0.0
    binary_bytes_processed: int = 0


class RetrievalMetrics(BaseModel):
    retrieval_rounds: int = 0
    retrievers_used: list[str] = Field(default_factory=list)
    candidate_count: int = 0
    reranked_count: int = 0
    evidence_count: int = 0
    citation_count: int = 0
    citation_coverage: float = 0.0
    source_span_accuracy: float = 0.0


class PlanningMetrics(BaseModel):
    plan_step_count: int = 0
    strategy: str | None = None
    skill_selected: str | None = None
    replan_count: int = 0
    reflection_count: int = 0
    reflexion_count: int = 0
    replan_reason: str | None = None


class SecurityMetrics(BaseModel):
    input_blocks: int = 0
    retrieval_acl_denied: int = 0
    tool_approval_required: int = 0
    output_dlp_blocks: int = 0
    prompt_injection_flags: int = 0


class EvalComparisonReport(BaseModel):
    baseline_label: Literal["basic_rag", "static_graphrag", "agentic_graphrag"]
    quality_delta: float
    latency_delta: float
    cost_delta: float
    citation_delta: float
    security_delta: float


class TraceSummary(BaseModel):
    trace_id: str
    events: list[TraceRecord] = Field(default_factory=list)
    metrics: list[TraceMetric] = Field(default_factory=list)
    cost_summary: CostMetric = Field(default_factory=CostMetric)


class ScenarioSummary(BaseModel):
    user_question: str
    selected_knowledge_spaces: list[str]
    retrieval_profiles: dict[str, str]
    selected_skill: str | None
    plan_summary: str
    retrieval_decision: RetrievalDecision
    reflection_verdict: dict[str, Any]
    replan_event: dict[str, Any]
    artifact_content_excerpt: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    metrics_summary: dict[str, Any] = Field(default_factory=dict)
    feedback_result: dict[str, Any] = Field(default_factory=dict)
    restart_rehydrate_result: dict[str, Any] = Field(default_factory=dict)
    file_status_timeline: list[str] = Field(default_factory=list)
    parser_dependency_probe: ParserDependencyProbe | None = None
    blocked_reason: str | None = None
    worker_event: dict[str, Any] = Field(default_factory=dict)
    index_status: str
    citation_lineage: list[dict[str, Any]] = Field(default_factory=list)


def _fields(model: type[BaseModel]) -> list[str]:
    fields = getattr(model, "model_fields", None)
    if fields is None:
        fields = getattr(model, "__fields__", {})
    return list(fields)


def _entry(
    owner: str,
    path: str,
    fields: list[str],
    phases: list[str],
    *,
    serialization: Literal["pydantic", "enum", "dataclass-facade"] = "pydantic",
    notes: str = "",
) -> SharedContractEntry:
    target_note = f"Target owner path: {path}." if path != _AGENT_PATH else ""
    combined_notes = " ".join(part for part in [target_note, notes] if part).strip()
    return SharedContractEntry(
        owner=owner,
        path=_AGENT_PATH,
        fields=fields,
        serialization=serialization,
        consuming_phases=phases,
        notes=combined_notes,
    )


_AGENT_PATH = "src/backend/zuno/agent/contracts.py"
_INGEST_PATH = "src/backend/zuno/knowledge/ingestion/contracts.py"
_STORAGE_PATH = "src/backend/zuno/knowledge/storage/contracts.py"
_INDEX_PATH = "src/backend/zuno/knowledge/indexing/contracts.py"
_CAP_PATH = "src/backend/zuno/capability/contracts.py"
_OBS_PATH = "src/backend/zuno/platform/observability/contracts.py"
_API_PATH = "src/backend/zuno/api/dto/workspace.py"


PHASE02_SHARED_CONTRACTS: dict[str, SharedContractEntry] = {
    "AgentRun": _entry("Workstream F", _AGENT_PATH, _fields(AgentRun), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "ContextPack": _entry("Workstream C", _AGENT_PATH, _fields(ContextPack), ["PHASE05", "PHASE09", "PHASE10", "PHASE12"]),
    "RetrievalProfile": _entry("Workstream B", _AGENT_PATH, ["standard", "deep", "deep_without_graph"], ["PHASE04", "PHASE09", "PHASE11", "PHASE12"], serialization="enum"),
    "RetrievalDecision": _entry("Workstream B", _AGENT_PATH, _fields(RetrievalDecision), ["PHASE04", "PHASE09", "PHASE12", "PHASE13"]),
    "EvidenceBundle": _entry("Workstream B", _AGENT_PATH, _fields(EvidenceBundle), ["PHASE04", "PHASE10", "PHASE12", "PHASE13"]),
    "CitationLineage": _entry("Workstream B", _AGENT_PATH, _fields(CitationLineage), ["PHASE04", "PHASE11", "PHASE12"]),
    "FileInputFormat": _entry("Workstream A", _AGENT_PATH, [item.value for item in FileInputFormat], ["PHASE03", "PHASE11", "PHASE12"], serialization="enum"),
    "SourceObject": _entry("Workstream A", _STORAGE_PATH, _fields(SourceObject), ["PHASE03", "PHASE11", "PHASE12"]),
    "BinarySourceObject": _entry("Workstream A", _STORAGE_PATH, _fields(BinarySourceObject), ["PHASE03", "PHASE12", "PHASE13"]),
    "ObjectStoreRef": _entry("Workstream A", _STORAGE_PATH, _fields(ObjectStoreRef), ["PHASE03", "PHASE12"]),
    "ObjectStoreResult": _entry("Workstream A", _STORAGE_PATH, _fields(ObjectStoreResult), ["PHASE03", "PHASE12"]),
    "ParserCapabilityStatus": _entry("Workstream A", _INGEST_PATH, [item.value for item in ParserCapabilityStatus], ["PHASE03", "PHASE11"], serialization="enum"),
    "ParserDependencyProbe": _entry("Workstream A", _INGEST_PATH, _fields(ParserDependencyProbe), ["PHASE03", "PHASE11", "PHASE12", "PHASE13"]),
    "ParserWorkerSpec": _entry("Workstream A", _INGEST_PATH, _fields(ParserWorkerSpec), ["PHASE03"]),
    "ParserWorkerResult": _entry("Workstream A", _INGEST_PATH, _fields(ParserWorkerResult), ["PHASE03", "PHASE12", "PHASE13"]),
    "ParseJobStatus": _entry("Workstream A", _INGEST_PATH, [item.value for item in ParseJobStatus], ["PHASE03", "PHASE11", "PHASE12"], serialization="enum"),
    "ParseAttempt": _entry("Workstream A", _INGEST_PATH, _fields(ParseAttempt), ["PHASE03", "PHASE12"]),
    "IndexWorkerSpec": _entry("Workstream A", _INDEX_PATH, _fields(IndexWorkerSpec), ["PHASE03"]),
    "IndexWorkerResult": _entry("Workstream A", _INDEX_PATH, _fields(IndexWorkerResult), ["PHASE03", "PHASE12", "PHASE13"]),
    "QueueMessage": _entry("Workstream A", _INGEST_PATH, _fields(QueueMessage), ["PHASE03", "PHASE12", "PHASE13"]),
    "QueueBackendResult": _entry("Workstream A", _INGEST_PATH, _fields(QueueBackendResult), ["PHASE03", "PHASE12"]),
    "OutboxEvent": _entry("Workstream A", _INGEST_PATH, _fields(OutboxEvent), ["PHASE03", "PHASE12"]),
    "DeadLetterRecord": _entry("Workstream A", _INGEST_PATH, _fields(DeadLetterRecord), ["PHASE03", "PHASE12", "PHASE13"]),
    "ReconcilerFinding": _entry("Workstream A", _INGEST_PATH, _fields(ReconcilerFinding), ["PHASE03", "PHASE12", "PHASE13"]),
    "OCRVLMEnrichmentResult": _entry("Workstream A", _INGEST_PATH, _fields(OCRVLMEnrichmentResult), ["PHASE03", "PHASE12", "PHASE13"]),
    "KnowledgeSpaceConfig": _entry("Coordinator", _API_PATH, _fields(KnowledgeSpaceConfig), ["PHASE11", "PHASE12", "PHASE14"]),
    "FileIngestionStatus": _entry("Coordinator", _API_PATH, _fields(FileIngestionStatus), ["PHASE11", "PHASE12", "PHASE13"]),
    "ChangeImpactPreview": _entry("Coordinator", _API_PATH, _fields(ChangeImpactPreview), ["PHASE11", "PHASE14"]),
    "CapabilityCard": _entry("Workstream D", _CAP_PATH, _fields(CapabilityCard), ["PHASE06", "PHASE09", "PHASE10"]),
    "CapabilityPolicy": _entry("Workstream D", _CAP_PATH, _fields(CapabilityPolicy), ["PHASE06", "PHASE07", "PHASE10"]),
    "CapabilityRiskProfile": _entry("Workstream D", _CAP_PATH, _fields(CapabilityRiskProfile), ["PHASE06", "PHASE07"]),
    "CapabilityAuditEvent": _entry("Workstream D", _CAP_PATH, _fields(CapabilityAuditEvent), ["PHASE06", "PHASE07", "PHASE13"]),
    "SkillCard": _entry("Workstream D", _CAP_PATH, _fields(SkillCard), ["PHASE06", "PHASE09", "PHASE10", "PHASE12"]),
    "ToolCard": _entry("Workstream D", _CAP_PATH, _fields(ToolCard), ["PHASE06", "PHASE07", "PHASE10"]),
    "PlanStep": _entry("Workstream F", _AGENT_PATH, _fields(PlanStep), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "PlanState": _entry("Workstream F", _AGENT_PATH, _fields(PlanState), ["PHASE09", "PHASE10", "PHASE12"]),
    "StrategySelectorOutput": _entry("Workstream F", _AGENT_PATH, _fields(StrategySelectorOutput), ["PHASE09", "PHASE10", "PHASE13"]),
    "SelectedSkill": _entry("Workstream F", _AGENT_PATH, _fields(SelectedSkill), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "CapabilityPlan": _entry("Workstream F", _AGENT_PATH, _fields(CapabilityPlan), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "RetrievalPlan": _entry("Workstream F", _AGENT_PATH, _fields(RetrievalPlan), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "ReflectionVerdict": _entry("Workstream F", _AGENT_PATH, _fields(ReflectionVerdict), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "ReplanDecision": _entry("Workstream F", _AGENT_PATH, _fields(ReplanDecision), ["PHASE09", "PHASE10", "PHASE12"]),
    "ReflexionLesson": _entry("Workstream C", _AGENT_PATH, _fields(ReflexionLesson), ["PHASE05", "PHASE10", "PHASE13"]),
    "TraceRecord": _entry("Workstream G", _OBS_PATH, _fields(TraceRecord), ["PHASE08", "PHASE10", "PHASE12", "PHASE13"]),
    "PlannerOutput": _entry("Workstream F", _AGENT_PATH, _fields(PlannerOutput), ["PHASE09", "PHASE10", "PHASE12", "PHASE13"]),
    "TraceMetric": _entry("Workstream G", _OBS_PATH, _fields(TraceMetric), ["PHASE08", "PHASE13"]),
    "CostMetric": _entry("Workstream G", _OBS_PATH, _fields(CostMetric), ["PHASE08", "PHASE13"]),
    "ConversationRunMetrics": _entry("Workstream G", _OBS_PATH, _fields(ConversationRunMetrics), ["PHASE13", "PHASE15"]),
    "StageMetrics": _entry("Workstream G", _OBS_PATH, _fields(StageMetrics), ["PHASE08", "PHASE13"]),
    "IngestionMetrics": _entry("Workstream G", _OBS_PATH, _fields(IngestionMetrics), ["PHASE03", "PHASE13"]),
    "RetrievalMetrics": _entry("Workstream G", _OBS_PATH, _fields(RetrievalMetrics), ["PHASE04", "PHASE13"]),
    "PlanningMetrics": _entry("Workstream G", _OBS_PATH, _fields(PlanningMetrics), ["PHASE09", "PHASE10", "PHASE13"]),
    "SecurityMetrics": _entry("Workstream G", _OBS_PATH, _fields(SecurityMetrics), ["PHASE07", "PHASE13"]),
    "EvalComparisonReport": _entry("Workstream G", _OBS_PATH, _fields(EvalComparisonReport), ["PHASE13", "PHASE15"]),
    "ScenarioSummary": _entry("Coordinator", _AGENT_PATH, _fields(ScenarioSummary), ["PHASE12", "PHASE13", "PHASE15"]),
    "TraceSummary": _entry("Workstream G", _OBS_PATH, _fields(TraceSummary), ["PHASE12", "PHASE13", "PHASE15"]),
}


__all__ = [
    "AgentRun",
    "BinarySourceObject",
    "CapabilityAuditEvent",
    "CapabilityCard",
    "CapabilityPlan",
    "CapabilityPolicy",
    "CapabilityRiskProfile",
    "ChangeImpactPreview",
    "CitationLineage",
    "ContextPack",
    "ConversationRunMetrics",
    "CostMetric",
    "DeadLetterRecord",
    "EvalComparisonReport",
    "EvidenceBundle",
    "FileIngestionStatus",
    "FileInputFormat",
    "IndexWorkerResult",
    "IndexWorkerSpec",
    "IngestionMetrics",
    "KnowledgeSpaceConfig",
    "OCRVLMEnrichmentResult",
    "ObjectStoreRef",
    "ObjectStoreResult",
    "OutboxEvent",
    "PHASE02_SHARED_CONTRACTS",
    "ParserCapabilityStatus",
    "ParserDependencyProbe",
    "ParserWorkerResult",
    "ParserWorkerSpec",
    "ParseAttempt",
    "ParseJobStatus",
    "PlannerOutput",
    "PlanState",
    "PlanStep",
    "PlanningMetrics",
    "QueueBackendResult",
    "QueueMessage",
    "ReconcilerFinding",
    "ReflectionVerdict",
    "ReflexionLesson",
    "ReplanDecision",
    "RetrievalDecision",
    "RetrievalMetrics",
    "RetrievalProfile",
    "ScenarioSummary",
    "SecurityMetrics",
    "SelectedSkill",
    "SharedContractEntry",
    "SkillCard",
    "SourceObject",
    "StageMetrics",
    "StrategySelectorOutput",
    "ToolCard",
    "TraceMetric",
    "TraceRecord",
    "TraceSummary",
    "RetrievalPlan",
]
