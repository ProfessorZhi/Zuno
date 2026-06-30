import { fetchEventSource } from '@microsoft/fetch-event-source'
import { request } from '../utils/request'
import { apiUrl } from '../utils/api'

export interface ExecutionModeDefinition {
  id: string
  label: string
  summary: string
  capabilities: string[]
  restrictions: string[]
  supports_tools: boolean
  supports_terminal: boolean
}

export interface AccessScopeDefinition {
  id: string
  label: string
  summary: string
  capabilities: string[]
  restrictions: string[]
  risk_level: string
}

export interface WorkspaceExecutionConfig {
  execution_modes: ExecutionModeDefinition[]
  access_scopes: AccessScopeDefinition[]
}

export const getWorkspaceExecutionModesAPI = async () => {
  return request({
    url: '/api/v1/workspace/execution-modes',
    method: 'get',
  })
}

export const getWorkspacePluginsByModeAPI = async (executionMode: string, accessScope: string) => {
  return request({
    url: '/api/v1/workspace/plugins',
    method: 'get',
    params: {
      execution_mode: executionMode,
      access_scope: accessScope,
    },
  })
}

export const getWorkspaceSessionsAPI = async (workspaceMode?: string) => {
  return request({
    url: '/api/v1/workspace/session',
    method: 'get',
    params: workspaceMode
      ? {
          workspace_mode: workspaceMode,
        }
      : undefined,
  })
}

export const createWorkspaceSessionAPI = async (data: {
  title?: string
  contexts?: any[]
  session_id?: string
  agent?: string
  workspace_mode?: 'normal' | 'agent'
}) => {
  return request({
    url: '/api/v1/workspace/session',
    method: 'post',
    data,
  })
}

export const getWorkspaceSessionInfoAPI = async (sessionId: string) => {
  return request({
    url: `/api/v1/workspace/session/${sessionId}`,
    method: 'post',
  })
}

export const deleteWorkspaceSessionAPI = async (sessionId: string) => {
  return request({
    url: '/api/v1/workspace/session',
    method: 'delete',
    params: {
      session_id: sessionId,
    },
  })
}

export type WorkspaceProductMode = 'enterprise_kb' | 'hr_resume' | 'contract_review' | 'general_agent'

export type WorkspaceTaskStatus =
  | 'created'
  | 'context_building'
  | 'planning'
  | 'running'
  | 'approval_waiting'
  | 'resuming'
  | 'finalizing'
  | 'completed'
  | 'failed'
  | 'cancelled'

export interface WorkspaceTaskBudget {
  max_steps?: number
  max_tokens?: number
  timeout_seconds?: number
  cost_ceiling?: number
}

export interface WorkspaceOutputContract {
  artifact_kinds: string[]
  citation_required: boolean
  trace_required: boolean
  format?: string
}

export interface WorkspaceProductObjectBase {
  workspace_id: string
  owner?: string
  status: string
  policy_scope?: string
  trace_id?: string
  created_at?: string
  updated_at?: string
  retention_policy?: string
}

export interface WorkspaceContract extends WorkspaceProductObjectBase {
  members: string[]
}

export interface KnowledgeSpaceContract extends WorkspaceProductObjectBase {
  knowledge_space_id: string
  graph_project_id?: string
  index_version?: string
  acl_policy?: string
}

export interface WorkspaceSessionContract extends WorkspaceProductObjectBase {
  session_id: string
  user_id: string
  thread_id?: string
  active_task_id?: string
}

export interface WorkspaceTaskContract extends WorkspaceProductObjectBase {
  task_id: string
  session_id: string
  goal: string
  product_mode: WorkspaceProductMode
  status: WorkspaceTaskStatus
  budget?: WorkspaceTaskBudget
}

export interface UploadedFileContract extends WorkspaceProductObjectBase {
  file_id: string
  mime_type: string
  hash: string
  security_label?: string
  parse_status: string
}

export interface ArtifactContract extends WorkspaceProductObjectBase {
  artifact_id: string
  task_id: string
  kind: string
  uri: string
  hash?: string
  download_policy?: string
}

export interface TraceEventContract {
  event_id: string
  task_id: string
  trace_id: string
  type: string
  timestamp: number
  payload: Record<string, any>
}

export interface CitationContract {
  citation_id: string
  evidence_id: string
  document_id: string
  block_id: string
  source_span: Record<string, any>
  created_at?: string
}

export interface FeedbackContract {
  feedback_id: string
  task_id: string
  rating?: number
  label?: string
  comment?: string
  dataset_candidate?: boolean
  created_at?: string
}

export interface WorkSpaceSimpleTask {
  query: string
  model_id: string
  workspace_id?: string
  user_id?: string
  task_id?: string
  trace_id?: string
  goal?: string
  product_mode?: WorkspaceProductMode
  knowledge_space_ids?: string[]
  uploaded_file_ids?: string[]
  approval_mode?: string
  budget?: WorkspaceTaskBudget
  output_contract?: WorkspaceOutputContract
  workspace_mode?: string
  agent_name?: string
  agent_id?: string
  web_search?: boolean
  plugins: string[]
  mcp_servers: string[]
  knowledge_ids?: string[]
  retrieval_mode?: string
  agent_skill_ids?: string[]
  session_id?: string
  execution_mode: string
  access_scope: string
  desktop_bridge_url?: string
  desktop_bridge_token?: string
  attachments?: WorkspaceAttachment[]
}

export interface WorkspaceTaskCreateResponse {
  task: WorkspaceTaskContract
  artifact_ids: string[]
  artifacts: ArtifactContract[]
  runtime?: WorkspaceRuntimeSnapshot
}

export interface WorkspaceArtifactResponse {
  artifact: ArtifactContract
  content: string
}

export interface WorkspaceFeedbackRequest {
  task_id: string
  rating?: number
  label?: string
  comment?: string
  dataset_candidate?: boolean
}

export interface WorkspaceFileCreateRequest {
  workspace_id: string
  file_id?: string
  name?: string
  mime_type: string
  hash?: string
  uri?: string
  trace_id?: string
  security_label?: string
}

export interface WorkspaceFileCreateResponse {
  file: UploadedFileContract
  name?: string
  uri?: string
}

export interface WorkspaceIngestRequest {
  workspace_id: string
  file_id: string
  knowledge_space_id: string
  session_id?: string
  trace_id?: string
}

export interface WorkspaceIngestResponse {
  ingest_task_id: string
  workspace_id: string
  file_id: string
  knowledge_space_id: string
  session_id?: string
  trace_id: string
  status: string
  file: UploadedFileContract
}

export interface WorkspaceApprovalRequest {
  decision: 'approved' | 'rejected'
  comment?: string
  approval_id?: string
  tool_call_id?: string
  required_approval?: string
}

export interface WorkspaceApprovalResponse extends WorkspaceTaskCreateResponse {}

export interface WorkspaceCancelRequest {
  reason?: string
}

export interface WorkspaceRuntimeSnapshot {
  task_id: string
  trace_id: string
  thread_id: string
  workspace_id: string
  status: WorkspaceTaskStatus | string
  state: Record<string, any>
  checkpoint_ids: string[]
  latest_checkpoint?: Record<string, any> | null
  pending_interrupt?: Record<string, any> | null
  failure?: Record<string, any> | null
  events: Array<Record<string, any>>
}

export interface WorkspaceAttachment {
  name: string
  url: string
  mime_type?: string
  size?: number
}

export interface WorkspaceStreamEvent {
  id: string
  type: string
  title: string
  detail: string
  isFinal?: boolean
  task_id?: string
  trace_id?: string
  artifact_id?: string
  citation_ids?: string[]
  tool_id?: string
  tool_call_id?: string
  approval_id?: string
  required_approval?: string
  audit_ref?: string
  data?: Record<string, any>
  raw?: any
}

export const workspaceSimpleChatStreamAPI = async (
  data: WorkSpaceSimpleTask,
  handlers: {
    onMessage?: (chunk: string) => void
    onFinalMessage?: (message: string) => void
    onEvent?: (event: WorkspaceStreamEvent) => void
    onError?: (err: any) => void
    onClose?: () => void
  }
) => {
  const token = localStorage.getItem('token')
  const ctrl = new AbortController()
  const streamUrl = apiUrl('/api/v1/workspace/simple/chat')

  try {
    await fetchEventSource(streamUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify(data),
      signal: ctrl.signal,
      openWhenHidden: true,
      onmessage(event) {
        if (!event.data) return

        try {
          const parsed = JSON.parse(event.data)
          if (parsed?.event !== undefined) {
            const normalized: WorkspaceStreamEvent = {
              id: crypto.randomUUID(),
              type: String(parsed.event || 'event'),
              title: String(
                parsed?.data?.message ||
                  parsed?.data?.summary ||
                  parsed?.data?.phase ||
                  parsed.event ||
                  'event'
              ),
              detail: String(
                parsed?.data?.result ||
                  parsed?.data?.error ||
                  parsed?.data?.chunk ||
                  parsed?.data?.accumulated ||
                  ''
              ),
              isFinal: parsed?.event === 'final',
              task_id: parsed?.data?.task_id,
              trace_id: parsed?.data?.trace_id,
              artifact_id: parsed?.data?.artifact_id,
              citation_ids: parsed?.data?.citation_ids,
              tool_id: parsed?.data?.tool_id,
              tool_call_id: parsed?.data?.tool_call_id,
              approval_id: parsed?.data?.approval_id,
              required_approval: parsed?.data?.required_approval,
              audit_ref: parsed?.data?.audit_ref,
              data: parsed?.data || {},
              raw: parsed,
            }
            handlers.onEvent?.(normalized)
          }

          if (parsed?.event === 'final') {
            if (parsed?.data?.done === true && typeof parsed?.data?.accumulated === 'string' && parsed.data.accumulated !== '') {
              handlers.onFinalMessage?.(parsed.data.accumulated)
              return
            }
            if (parsed?.data?.chunk !== undefined && parsed.data.chunk !== '') {
              handlers.onMessage?.(parsed.data.chunk)
              return
            }
            if (parsed?.data?.message !== undefined && parsed.data.message !== '') {
              handlers.onMessage?.(parsed.data.message)
              return
            }
          } else if (typeof parsed?.data?.accumulated === 'string' && parsed.data.accumulated !== '') {
            return
          } else if (typeof parsed?.data?.message === 'string' && parsed.data.message !== '') {
            return
          }
        } catch {
          const rawText = event.data.trim()
          if (rawText && !rawText.startsWith('{') && !rawText.startsWith('[')) {
            handlers.onMessage?.(rawText)
          }
        }
      },
      onerror(err) {
        handlers.onError?.(err)
        ctrl.abort()
      },
      onclose() {
        handlers.onClose?.()
      },
    })
  } catch (error: any) {
    if (error?.name !== 'AbortError') {
      handlers.onError?.(error)
    }
  }
}

export const createWorkspaceTaskAPI = async (data: WorkSpaceSimpleTask) => {
  return request({
    url: '/api/v1/workspace/task',
    method: 'post',
    data,
  })
}

export const createWorkspaceFileAPI = async (data: WorkspaceFileCreateRequest) => {
  return request({
    url: '/api/v1/workspace/file',
    method: 'post',
    data,
  })
}

export const createWorkspaceIngestAPI = async (data: WorkspaceIngestRequest) => {
  return request({
    url: '/api/v1/workspace/ingest',
    method: 'post',
    data,
  })
}

export const getWorkspaceTaskAPI = async (taskId: string) => {
  return request({
    url: `/api/v1/workspace/task/${taskId}`,
    method: 'get',
  })
}

export const getWorkspaceTaskEventsAPI = async (taskId: string) => {
  return request({
    url: `/api/v1/workspace/task/${taskId}/events`,
    method: 'get',
  })
}

export const workspaceTaskEventsStreamAPI = async (
  taskId: string,
  handlers: {
    onEvent?: (event: WorkspaceStreamEvent) => void
    onError?: (err: any) => void
    onClose?: () => void
  }
) => {
  const token = localStorage.getItem('token')
  const ctrl = new AbortController()
  const streamUrl = apiUrl(`/api/v1/workspace/task/${taskId}/events/stream`)

  try {
    await fetchEventSource(streamUrl, {
      method: 'GET',
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
      signal: ctrl.signal,
      openWhenHidden: true,
      onmessage(event) {
        if (!event.data) return
        try {
          const parsed = JSON.parse(event.data)
          const normalized: WorkspaceStreamEvent = {
            id: String(parsed?.data?.event_id || crypto.randomUUID()),
            type: String(parsed?.event || parsed?.data?.phase || 'event'),
            title: String(parsed?.data?.message || parsed?.event || 'event'),
            detail: String(parsed?.data?.result || parsed?.data?.error || parsed?.data?.chunk || ''),
            isFinal: parsed?.event === 'task_completed' || parsed?.data?.status === 'completed',
            task_id: parsed?.data?.task_id,
            trace_id: parsed?.data?.trace_id,
            artifact_id: parsed?.data?.artifact_id,
            citation_ids: parsed?.data?.citation_ids,
            tool_id: parsed?.data?.tool_id,
            tool_call_id: parsed?.data?.tool_call_id,
            approval_id: parsed?.data?.approval_id,
            required_approval: parsed?.data?.required_approval,
            audit_ref: parsed?.data?.audit_ref,
            data: parsed?.data || {},
            raw: parsed,
          }
          handlers.onEvent?.(normalized)
        } catch (err) {
          handlers.onError?.(err)
        }
      },
      onerror(err) {
        handlers.onError?.(err)
        ctrl.abort()
      },
      onclose() {
        handlers.onClose?.()
      },
    })
  } catch (error: any) {
    if (error?.name !== 'AbortError') {
      handlers.onError?.(error)
    }
  }
}

export const approveWorkspaceTaskAPI = async (taskId: string, data: WorkspaceApprovalRequest) => {
  return request({
    url: `/api/v1/workspace/task/${taskId}/approve`,
    method: 'post',
    data,
  })
}

export const cancelWorkspaceTaskAPI = async (taskId: string, data: WorkspaceCancelRequest) => {
  return request({
    url: `/api/v1/workspace/task/${taskId}/cancel`,
    method: 'post',
    data,
  })
}

export const getWorkspaceArtifactAPI = async (artifactId: string) => {
  return request({
    url: `/api/v1/workspace/artifact/${artifactId}`,
    method: 'get',
  })
}

export const createWorkspaceFeedbackAPI = async (data: WorkspaceFeedbackRequest) => {
  return request({
    url: '/api/v1/workspace/feedback',
    method: 'post',
    data,
  })
}
