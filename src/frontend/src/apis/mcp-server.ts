import { request } from '../utils/request'

export interface CreateMCPServerRequest {
  server_name?: string
  logo_url?: string
  imported_config: Record<string, any>
}

export interface UpdateMCPServerRequest {
  server_id: string
  name?: string
  logo_url?: string
  imported_config?: Record<string, any>
}

export interface MCPServerToolSchemaProperty {
  description?: string
  type?: string
}

export interface MCPServerTool {
  name: string
  description: string
  input_schema: {
    type: string
    title?: string
    description?: string
    required?: string[]
    properties?: Record<string, MCPServerToolSchemaProperty>
  }
}

export interface MCPUserConfig {
  config_id: string
  mcp_server_id: string
  user_id: string
  config: unknown
  test_status?: {
    code: 'success' | 'failed' | 'untested'
    label: string
    detail: string
    tools: string[]
    tested_at?: string | null
  }
  create_time: string
  update_time: string
}

export interface MCPServer {
  mcp_server_id: string
  server_name: string
  url: string
  type: string
  config?: Record<string, any>
  config_enabled: boolean
  tools: string[]
  params: MCPServerTool[]
  logo_url: string
  user_id: string
  user_name: string
  create_time: string
  update_time: string
  imported_config?: Record<string, any>
  test_status?: {
    code: 'success' | 'failed' | 'untested'
    label: string
    detail: string
    tools: string[]
    tested_at?: string | null
  }
}

export interface MCPResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export interface MCPUserConfigUpdateRequest {
  server_id: string
  config: Array<Record<string, any>>
}

export interface MCPUserConfigTestRequest {
  server_id: string
}

export interface MCPUserConfigCreateRequest {
  mcp_server_id: string
  config: Array<Record<string, any>>
}

export const createMCPServerAPI = (data: CreateMCPServerRequest) =>
  request<MCPResponse<null>>({
    url: '/api/v1/mcp_server',
    method: 'POST',
    data,
  })

export const getMCPServersAPI = () =>
  request<MCPResponse<MCPServer[]>>({
    url: '/api/v1/mcp_server',
    method: 'GET',
  })

export const updateMCPServerAPI = (data: UpdateMCPServerRequest) =>
  request<MCPResponse<null>>({
    url: '/api/v1/mcp_server',
    method: 'PUT',
    data,
  })

export const deleteMCPServerAPI = (server_id: string) =>
  request<MCPResponse<null>>({
    url: '/api/v1/mcp_server',
    method: 'DELETE',
    data: { server_id },
  })

export const getMCPToolsAPI = (server_id: string) =>
  request<MCPResponse<any>>({
    url: '/api/v1/mcp_tools',
    method: 'GET',
    params: { server_id },
  })

export const getMCPUserConfigAPI = (server_id: string) =>
  request<MCPResponse<MCPUserConfig | null>>({
    url: '/api/v1/mcp_user_config',
    method: 'GET',
    params: { server_id },
  })

export const createMCPUserConfigAPI = (data: MCPUserConfigCreateRequest) =>
  request<MCPResponse<MCPUserConfig | null>>({
    url: '/api/v1/mcp_user_config/create',
    method: 'POST',
    data,
  })

export const updateMCPUserConfigAPI = (data: MCPUserConfigUpdateRequest) =>
  request<MCPResponse<null>>({
    url: '/api/v1/mcp_user_config/update',
    method: 'PUT',
    data,
  })

export const testMCPUserConfigAPI = (data: MCPUserConfigTestRequest) =>
  request<MCPResponse<{
    success: boolean
    message: string
    tools: string[]
  }>>({
    url: '/api/v1/mcp_user_config/test',
    method: 'POST',
    data,
    timeout: 45000,
  })

export const deleteMCPUserConfigAPI = (config_id: string) =>
  request<MCPResponse<null>>({
    url: '/api/v1/mcp_user_config/delete',
    method: 'DELETE',
    data: { config_id },
  })

export const getDefaultMCPLogoAPI = () =>
  request<
    MCPResponse<{
      logo_url: string
    }>
  >({
    url: '/api/v1/mcp_server/logo',
    method: 'GET',
  })
