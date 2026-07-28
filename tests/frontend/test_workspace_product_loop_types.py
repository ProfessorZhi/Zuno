from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_workspace_api_types_expose_product_runtime_payload_contract() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "export type WorkspaceProductMode = 'enterprise_kb' | 'hr_resume' | 'contract_review' | 'general_agent'",
        "export interface WorkspaceTaskBudget",
        "export interface WorkspaceOutputContract",
        "export interface WorkspaceProductObjectBase",
        "export interface KnowledgeSpaceContract",
        "export interface UploadedFileContract",
        "export interface ArtifactContract",
        "export interface WorkspaceProductRuntimePayload",
        "workspace_id?: string",
        "goal?: string",
        "product_mode?: WorkspaceProductMode",
        "knowledge_space_ids?: string[]",
        "uploaded_file_ids?: string[]",
        "approval_mode?: string",
        "budget?: WorkspaceTaskBudget",
        "output_contract?: WorkspaceOutputContract",
        "task_id?: string",
        "trace_id?: string",
    ]:
        assert phrase in workspace_api


def test_workspace_api_removes_legacy_task_status_lifecycle_and_stream_dtos() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "export type WorkspaceTaskStatus =",
        "export type WorkspaceTaskLifecycleState =",
        "export interface WorkspaceTaskContract",
        "export interface WorkspaceTaskLifecycleSnapshot",
        "export interface WorkspaceTaskCreateResponse",
        "export interface WorkspaceApprovalRequest",
        "export interface WorkspaceApprovalResponse",
        "export interface WorkspaceCancelRequest",
        "export interface WorkspaceTaskLifecycleResponse",
        "export interface WorkspaceRuntimeSnapshot",
        "export interface WorkspaceStreamEvent",
        "export const getWorkspaceTaskLifecycleAPI",
        "WorkSpaceSimpleTask",
        "approval_required",
        "recoverable_failed",
        "lifecycle_state?:",
        "required_approval?:",
    ]:
        assert phrase not in workspace_api


def test_workspace_api_removes_legacy_stream_normalizer_trace_mapping() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "task_id: parsed?.data?.task_id",
        "trace_id: parsed?.data?.trace_id",
        "artifact_id: parsed?.data?.artifact_id",
        "citation_ids: parsed?.data?.citation_ids",
    ]:
        assert phrase not in workspace_api


def test_workspace_api_exposes_phase03_task_runtime_calls() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "export interface WorkspaceFileCreateRequest",
        "content?: string",
        "export interface WorkspaceFileCreateResponse",
        "export interface WorkspaceIngestRequest",
        "export interface WorkspaceIngestResponse",
        "export interface WorkspaceObservabilitySnapshot",
        "release_eval?: Record<string, any> | null",
        "source_refs: string[]",
        "export const createWorkspaceFileAPI",
        "url: '/api/v1/workspace/file'",
        "export const createWorkspaceIngestAPI",
        "url: '/api/v1/workspace/ingest'",
    ]:
        assert phrase in workspace_api


def test_workspace_api_no_longer_exposes_legacy_task_chat_artifact_or_feedback_calls() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "workspaceSimpleChatStreamAPI",
        "createWorkspaceTaskAPI",
        "workspaceTaskEventsStreamAPI",
        "approveWorkspaceTaskAPI",
        "cancelWorkspaceTaskAPI",
        "getWorkspaceTaskAPI",
        "getWorkspaceTaskEventsAPI",
        "getWorkspaceArtifactAPI",
        "downloadWorkspaceArtifactAPI",
        "createWorkspaceFeedbackAPI",
        "/api/v1/workspace/simple/chat",
        "apiUrl(`/api/v1/workspace/task/${taskId}/events/stream`)",
        "url: `/api/v1/workspace/task/${taskId}`",
        "url: `/api/v1/workspace/artifact/${artifactId}`",
        "url: '/api/v1/workspace/feedback'",
    ]:
        assert phrase not in workspace_api
