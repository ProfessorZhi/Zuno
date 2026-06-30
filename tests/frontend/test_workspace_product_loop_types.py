from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_workspace_api_types_expose_phase03_product_loop_contract() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "export type WorkspaceProductMode = 'enterprise_kb' | 'hr_resume' | 'contract_review' | 'general_agent'",
        "export type WorkspaceTaskStatus =",
        "'approval_waiting'",
        "export interface WorkspaceTaskBudget",
        "export interface WorkspaceOutputContract",
        "export interface WorkspaceProductObjectBase",
        "export interface KnowledgeSpaceContract",
        "export interface WorkspaceTaskContract",
        "export interface UploadedFileContract",
        "export interface ArtifactContract",
        "export interface TraceEventContract",
        "export interface CitationContract",
        "export interface FeedbackContract",
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


def test_workspace_stream_normalizer_preserves_product_trace_ids() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "task_id: parsed?.data?.task_id",
        "trace_id: parsed?.data?.trace_id",
        "artifact_id: parsed?.data?.artifact_id",
        "citation_ids: parsed?.data?.citation_ids",
    ]:
        assert phrase in workspace_api


def test_workspace_api_exposes_phase03_task_runtime_calls() -> None:
    workspace_api = (REPO_ROOT / "apps/web/src/apis/workspace.ts").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "export interface WorkspaceFileCreateRequest",
        "export interface WorkspaceFileCreateResponse",
        "export interface WorkspaceIngestRequest",
        "export interface WorkspaceIngestResponse",
        "export interface WorkspaceApprovalRequest",
        "export const createWorkspaceTaskAPI",
        "url: '/api/v1/workspace/task'",
        "export const createWorkspaceFileAPI",
        "url: '/api/v1/workspace/file'",
        "export const createWorkspaceIngestAPI",
        "url: '/api/v1/workspace/ingest'",
        "export const getWorkspaceTaskAPI",
        "url: `/api/v1/workspace/task/${taskId}`",
        "export const getWorkspaceTaskEventsAPI",
        "url: `/api/v1/workspace/task/${taskId}/events`",
        "export const workspaceTaskEventsStreamAPI",
        "apiUrl(`/api/v1/workspace/task/${taskId}/events/stream`)",
        "export const approveWorkspaceTaskAPI",
        "url: `/api/v1/workspace/task/${taskId}/approve`",
        "export const getWorkspaceArtifactAPI",
        "url: `/api/v1/workspace/artifact/${artifactId}`",
        "export const createWorkspaceFeedbackAPI",
        "url: '/api/v1/workspace/feedback'",
    ]:
        assert phrase in workspace_api
