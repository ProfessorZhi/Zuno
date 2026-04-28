import { request } from "../utils/request"

export type RuntimeType = 'remote_api' | 'cli'
export type CliSourceType = 'local_directory' | 'executable' | 'npm_package' | 'python_package' | 'github_repo'
export type CliCwdMode = 'tool_dir' | 'workspace' | 'custom'
export type RemoteApiMode = 'simple' | 'openapi'
export type RemoteApiAuthType = '' | 'bearer' | 'basic' | 'api_key_query' | 'api_key_header'

export interface SimpleApiParamConfig {
  name: string
  in: 'path' | 'query' | 'header'
  required?: boolean
  description?: string
  type?: 'string' | 'integer' | 'number' | 'boolean'
}

export interface SimpleApiConfig {
  base_url: string
  path: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  operation_id: string
  summary?: string
  description?: string
  params?: SimpleApiParamConfig[]
  body_schema?: Record<string, any> | null
  response_schema?: Record<string, any> | null
}

export interface RemoteApiAssistRequest {
  endpoint_url?: string
  docs_url?: string
  docs_urls?: string[]
  sample_curl?: string
  api_key?: string
  api_key_name?: string
  auth_type?: Exclude<RemoteApiAuthType, ''> | 'none'
  method?: '' | 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  display_name?: string
  description?: string
}

export interface RemoteApiAssistResponse {
  display_name: string
  description: string
  simple_api_config: SimpleApiConfig
  auth_config?: Record<string, any>
  openapi_schema: Record<string, any>
  probe_args?: Record<string, any>
  warnings?: string[]
}

export interface ToolConnectivityRequest {
  runtime_type?: RuntimeType
  auth_config?: Record<string, any>
  cli_config?: CliConfig
  openapi_schema?: Record<string, any>
  simple_api_config?: SimpleApiConfig
  probe_operation_id?: string
  probe_args?: Record<string, any>
}

export interface ToolConnectivityResponse {
  ok: boolean
  runtime_type: RuntimeType
  summary: string
  details?: string[]
  warnings?: string[]
  executed?: boolean
  operation_id?: string | null
  tested_url?: string | null
  command?: string | null
  status?: {
    code: 'ready' | 'needs_config' | 'runtime_input' | 'missing_dependency'
    label: string
    detail: string
    configurable: boolean
  }
}

export interface CliAssistRequest {
  tool_dir: string
  source_type?: CliSourceType
  install_source?: string
  command?: string
  doc_url?: string
  github_url?: string
  docs_url?: string
  local_path?: string
  notes?: string
}

export interface CliConfig {
  source_type?: CliSourceType
  tool_dir: string
  command: string
  args_template?: string
  cwd_mode?: CliCwdMode
  cwd?: string
  timeout_ms?: number
  install_command?: string
  install_source?: string
  install_notes?: string
  healthcheck_command?: string
  credential_mode?: 'none' | 'single' | 'profiles'
}

export interface CliPreviewCandidate {
  command: string
  args_template: string[]
  cwd_mode: CliCwdMode
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
  healthcheck_command?: string
}

export interface CliStructuredSuggestion {
  id?: string
  title?: string
  label?: string
  summary?: string
  description?: string
  reason?: string
  confidence?: number
  notes?: string[]
  warnings?: string[]
  detected_files?: string[]
  references?: string[]
  command?: string
  args_template?: string[] | string
  cwd_mode?: CliCwdMode
  cwd?: string | null
  display_name?: string
  tool_name?: string
  tool_dir?: string
  install_source?: string
  install_command?: string
  healthcheck_command?: string
}

export interface CliPreviewResult {
  tool_dir: string
  source_type?: CliSourceType
  install_source?: string
  doc_url?: string
  docs_url?: string
  github_url?: string
  local_path?: string
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
  suggested_install_command?: string
  suggested_healthcheck_command?: string
  assist_summary?: string
  assist_sources?: string[]
  install_suggestions?: CliPreviewCandidate[]
  run_suggestions?: CliPreviewCandidate[]
  healthcheck_suggestions?: CliPreviewCandidate[]
  credential_mode_suggestions?: Array<{
    mode?: 'none' | 'env' | 'profiles' | 'manual'
    confidence?: number
    reason?: string
    env_vars?: string[]
    notes?: string[]
  }>
  structured_suggestions?: CliStructuredSuggestion[]
  suggestions?: CliStructuredSuggestion[]
  assist_suggestions?: CliStructuredSuggestion[]
  plans?: CliStructuredSuggestion[]
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
  simple_api_config?: SimpleApiConfig
  source_metadata?: Record<string, any>
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
  simple_api_config?: SimpleApiConfig
  source_metadata?: Record<string, any>
}) {
  return request<ApiResponse<{ tool_id: string }>>({
    url: '/api/v1/tool/create',
    method: 'POST',
    data
  })
}

export function previewCliToolAPI(data: CliAssistRequest) {
  return request<ApiResponse<CliPreviewResult>>({
    url: '/api/v1/tool/cli/preview',
    method: 'POST',
    data,
    timeout: 60000
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
  simple_api_config?: SimpleApiConfig
  source_metadata?: Record<string, any>
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

export function assistRemoteApiToolAPI(data: RemoteApiAssistRequest) {
  return request<ApiResponse<RemoteApiAssistResponse>>({
    url: '/api/v1/tool/remote_api/assist',
    method: 'POST',
    data,
    timeout: 240000
  })
}

export function testToolConnectivityAPI(data: ToolConnectivityRequest) {
  return request<ApiResponse<ToolConnectivityResponse>>({
    url: '/api/v1/tool/test_connectivity',
    method: 'POST',
    data,
    timeout: 30000
  })
}

export function testSavedToolConnectivityAPI(toolId: string) {
  return request<ApiResponse<ToolConnectivityResponse>>({
    url: `/api/v1/tool/${toolId}/test_connectivity`,
    method: 'POST',
    timeout: 30000,
  })
}

export function testSystemToolConnectivityAPI(toolName: string) {
  return request<ApiResponse<ToolConnectivityResponse>>({
    url: `/api/v1/tool/system/${toolName}/test_connectivity`,
    method: 'POST',
    timeout: 30000,
  })
}
