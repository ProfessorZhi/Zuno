import { request } from '../utils/request'

export interface AgentCreateRequest {
  name: string
  description: string
  logo_url: string
  tool_ids: string[]
  llm_id: string
  mcp_ids: string[]
  system_prompt: string
  knowledge_ids: string[]
  agent_skill_ids?: string[]
  enable_memory: boolean
}

export interface AgentUpdateRequest {
  agent_id: string
  name?: string
  description?: string
  logo_url?: string
  tool_ids?: string[]
  llm_id?: string
  mcp_ids?: string[]
  system_prompt?: string
  knowledge_ids?: string[]
  agent_skill_ids?: string[]
  enable_memory?: boolean
}

export interface AgentResponse {
  agent_id?: string
  id?: string
  name: string
  description: string
  logo_url: string
  tool_ids: string[]
  llm_id: string
  mcp_ids: string[]
  system_prompt: string
  knowledge_ids: string[]
  agent_skill_ids?: string[]
  enable_memory: boolean
  create_time?: string
  created_time?: string
  is_custom?: boolean
}

export interface AgentSearchItem {
  agent_id?: string
  id?: string
  name: string
  description: string
  logo_url: string
  is_custom?: boolean
}

export interface ApiResponse<T> {
  status_code: number
  status_message: string
  data: T
}

export function createAgentAPI(data: AgentCreateRequest) {
  return request<ApiResponse<null>>({
    url: '/api/v1/agent',
    method: 'POST',
    data,
  })
}

export function getAgentsAPI() {
  return request<ApiResponse<AgentResponse[]>>({
    url: '/api/v1/agent',
    method: 'GET',
  })
}

export function getAgentByIdAPI(agentId: string) {
  return getAgentsAPI().then((response) => {
    if (response.data.status_code !== 200) {
      return {
        data: {
          status_code: response.data.status_code,
          status_message: response.data.status_message,
          data: null,
        },
      } as { data: ApiResponse<AgentResponse | null> }
    }

    const agent =
      response.data.data.find(
        (item) =>
          item.agent_id === agentId ||
          item.id === agentId ||
          String(item.agent_id) === String(agentId) ||
          String(item.id) === String(agentId),
      ) ?? null

    return {
      data: {
        status_code: agent ? 200 : 404,
        status_message: agent ? 'SUCCESS' : '智能体不存在',
        data: agent,
      },
    } as { data: ApiResponse<AgentResponse | null> }
  })
}

export function deleteAgentAPI(data: { agent_id: string }) {
  return request<ApiResponse<null>>({
    url: '/api/v1/agent',
    method: 'DELETE',
    data,
  })
}

export function updateAgentAPI(data: AgentUpdateRequest) {
  return request<ApiResponse<null>>({
    url: '/api/v1/agent',
    method: 'PUT',
    data,
  })
}

export function searchAgentsAPI(data: { name: string }) {
  return request<ApiResponse<AgentSearchItem[]>>({
    url: '/api/v1/agent/search',
    method: 'POST',
    data,
  })
}
