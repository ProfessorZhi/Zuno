import { request } from "../utils/request"

export interface ConfigResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export interface RuntimeConfigPayload {
  content: string
  system_tools: Array<{
    tool_name: string
    display_name: string
    description: string
    has_fields: boolean
    status: {
      code: 'ready' | 'needs_config' | 'runtime_input' | 'missing_dependency'
      label: string
      detail: string
      configurable: boolean
    }
  }>
}

export interface SystemToolField {
  key: string
  label: string
  placeholder?: string
  required?: boolean
  secret?: boolean
}

export interface SystemToolConfigPayload {
  tool_name: string
  display_name: string
  description: string
  root?: string | null
  section?: string | null
  config_type?: 'fields' | 'email_accounts'
  fields: SystemToolField[]
  values: Record<string, string>
  note?: string
  accounts?: Array<{
    slot_name: string
    provider: string
    sender_email: string
    auth_code: string
    smtp_host: string
    smtp_port: number
    use_ssl: boolean
    display_name?: string
  }>
}

export function getConfigAPI() {
  return request<ConfigResponse<RuntimeConfigPayload>>({
    url: "/api/v1/config",
    method: "GET",
  })
}

export function updateConfigAPI(data: FormData) {
  return request<ConfigResponse<string>>({
    url: "/api/v1/config",
    method: "POST",
    data,
  })
}

export function getSystemToolConfigAPI(toolName: string) {
  return request<ConfigResponse<SystemToolConfigPayload>>({
    url: `/api/v1/config/system-tool/${toolName}`,
    method: "GET",
  })
}

export function updateSystemToolConfigAPI(
  toolName: string,
  payload: {
    values?: Record<string, string>
    accounts?: Array<{
      slot_name: string
      provider: string
      sender_email: string
      auth_code: string
      smtp_host: string
      smtp_port: number
      use_ssl: boolean
      display_name?: string
    }>
  }
) {
  return request<ConfigResponse<{ message: string; config_path: string }>>({
    url: `/api/v1/config/system-tool/${toolName}`,
    method: "POST",
    data: payload,
  })
}
