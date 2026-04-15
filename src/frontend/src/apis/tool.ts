import { request } from "../utils/request"

export type RuntimeType = 'remote_api' | 'cli'

export interface CliConfig {
  tool_dir: string
  command: string
  args_template?: string
  cwd_mode?: 'tool_dir' | 'workspace' | 'custom'
  cwd?: string
  timeout_ms?: number
}

export interface CliPreviewCandidate {
  command: string
  args_template: string[]
  cwd_mode: 'tool_dir' | 'workspace' | 'custom'
  cwd?: string | null
  source?: string
  confidence?: number
  notes?: string[]
  label?: string
  reason?: string
  tool_name?: string
  description?: string
  readme_summary?: string
  readme_path?: string
  entry_path?: string
  timeout_ms?: number
}

export interface CliPreviewResult {
  tool_dir: string
  resolved_path?: string
  exists?: boolean
  suggested_name?: string
  default_description?: string
  readme_path?: string | null
  readme_summary?: string | null
  command_candidates?: CliPreviewCandidate[]
  warnings?: string[]
  candidates?: CliPreviewCandidate[]
  recommended?: CliPreviewCandidate
  display_name?: string
  description?: string
  readme_excerpt?: string
  detected_files?: string[]
}

export interface ToolResponse {
  tool_id: string
  name: string
  display_name: string
  user_id: string
  description: string
  logo_url: string
  openapi_schema?: any
  auth_config?: any
  runtime_type?: RuntimeType
}

export interface ApiResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export function getAllToolsAPI() {
  return request<ApiResponse<ToolResponse[]>>({
    url: '/api/v1/tool/all',
    method: 'POST'
  })
}

export function getOwnToolsAPI() {
  return request<ApiResponse<ToolResponse[]>>({
    url: '/api/v1/tool/user_defined',
    method: 'POST'
  })
}

export function getVisibleToolsAPI() {
  return request<ApiResponse<ToolResponse[]>>({
    url: '/api/v1/tool/all',
    method: 'POST'
  })
}

export function createToolAPI(data: {
  display_name: string
  description: string
  logo_url: string
  runtime_type?: RuntimeType
  auth_config?: any
  cli_config?: CliConfig
  openapi_schema?: any
}) {
  return request<ApiResponse<{ tool_id: string }>>({
    url: '/api/v1/tool/create',
    method: 'POST',
    data
  })
}

export function previewCliToolAPI(data: { tool_dir: string }) {
  return request<ApiResponse<CliPreviewResult>>({
    url: '/api/v1/tool/cli/preview',
    method: 'POST',
    data
  })
}

export function updateToolAPI(data: {
  tool_id: string
  display_name?: string
  description?: string
  logo_url?: string
  runtime_type?: RuntimeType
  auth_config?: any
  cli_config?: CliConfig
  openapi_schema?: any
}) {
  return request<ApiResponse<null>>({
    url: '/api/v1/tool/update',
    method: 'POST',
    data
  })
}

export function deleteToolAPI(data: { tool_id: string }) {
  return request<ApiResponse<null>>({
    url: '/api/v1/tool/delete',
    method: 'POST',
    data
  })
}

export function getDefaultToolLogoAPI() {
  return request<ApiResponse<{ logo_url: string }>>({
    url: '/api/v1/tool/default_logo',
    method: 'GET'
  })
}

export function uploadFileAPI(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return request<ApiResponse<string>>({
    url: '/api/v1/upload/upload',
    method: 'POST',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
