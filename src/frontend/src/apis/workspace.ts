import { fetchEventSource } from '@microsoft/fetch-event-source'
import { request } from '../utils/request'
import { apiUrl } from '../utils/api'

export const getWorkspacePluginsAPI = async () => {
  return request({
    url: '/api/v1/workspace/plugins',
    method: 'get',
  })
}

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

export const getWorkspaceSessionsAPI = async () => {
  return request({
    url: '/api/v1/workspace/session',
    method: 'get',
  })
}

export const createWorkspaceSessionAPI = async (data: { title?: string; contexts?: any }) => {
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

export interface WorkSpaceSimpleTask {
  query: string
  model_id: string
  workspace_mode?: string
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

export interface WorkspaceAttachment {
  name: string
  url: string
  mime_type?: string
  size?: number
}

export const workspaceSimpleChatAPI = async (data: WorkSpaceSimpleTask) => {
  return request({
    url: '/api/v1/workspace/simple/chat',
    method: 'post',
    data,
    responseType: 'stream',
  })
}

export interface WorkspaceStreamEvent {
  id: string
  type: string
  title: string
  detail: string
  isFinal?: boolean
  data?: Record<string, any>
  raw?: any
}

export const workspaceSimpleChatStreamAPI = async (
  data: WorkSpaceSimpleTask,
  handlers: {
    onMessage?: (chunk: string) => void
    onEvent?: (event: WorkspaceStreamEvent) => void
    onError?: (err: any) => void
    onClose?: () => void
  }
) => {
  const token = localStorage.getItem('token')
  const ctrl = new AbortController()
  const streamUrl = apiUrl('/api/v1/workspace/simple/chat')

  console.log('=== workspaceSimpleChatStreamAPI ===')
  console.log('Request payload:', data)
  console.log('Request URL:', streamUrl)

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
              data: parsed?.data || {},
              raw: parsed,
            }
            handlers.onEvent?.(normalized)
          }

          if (parsed?.event === 'final') {
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
        console.error('Workspace SSE error:', err)
        handlers.onError?.(err)
        ctrl.abort()
      },
      onclose() {
        console.log('Workspace SSE connection closed')
        handlers.onClose?.()
      },
    })
  } catch (error: any) {
    console.error('Workspace SSE exception:', error)
    if (error?.name !== 'AbortError') {
      handlers.onError?.(error)
    }
  }
}
