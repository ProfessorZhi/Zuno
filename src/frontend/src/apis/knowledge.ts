import { request } from '../utils/request'

export interface UnifiedResponse<T = any> {
  status_code: number
  status_message: string
  data?: T
}

export interface KnowledgeConfigPayload {
  model_refs: {
    text_embedding_model_id: string | null
    vl_embedding_model_id: string | null
    rerank_model_id: string | null
  }
  index_settings: {
    chunk_mode: 'general' | 'parent_child' | 'qa'
    chunk_size: number
    overlap: number
    separator: string
    replace_consecutive_spaces: boolean
    remove_urls_emails: boolean
    image_indexing_mode: 'text_only' | 'vl_only' | 'dual'
  }
  retrieval_settings: {
    default_mode: 'auto' | 'hybrid' | 'rag' | 'graphrag'
    top_k: number
    rerank_enabled: boolean
    rerank_top_k: number
    score_threshold: number | null
  }
}

export interface KnowledgeConfigPatchPayload {
  model_refs?: Partial<KnowledgeConfigPayload['model_refs']>
  index_settings?: Partial<KnowledgeConfigPayload['index_settings']>
  retrieval_settings?: Partial<KnowledgeConfigPayload['retrieval_settings']>
}

export interface KnowledgeResponse {
  id: string
  name: string
  description: string | null
  user_id: string | null
  create_time: string
  update_time: string
  count: number
  file_size: string
  processing_count?: number
  failed_count?: number
  completed_count?: number
  knowledge_config?: KnowledgeConfigPayload
}

export interface KnowledgeCreateRequest {
  knowledge_name: string
  knowledge_desc?: string
  knowledge_config?: KnowledgeConfigPayload
}

export interface KnowledgeUpdateRequest {
  knowledge_id: string
  knowledge_name?: string
  knowledge_desc?: string
  knowledge_config?: KnowledgeConfigPatchPayload
}

export interface KnowledgeDeleteRequest {
  knowledge_id: string
}

export interface KnowledgeModelBindingPayload {
  llm_id: string
  model: string
  provider: string
}

export interface KnowledgeRetrievalRequest {
  query: string
  knowledge_id: string | string[]
  top_k?: number
  retrieval_mode?: string
}

export interface KnowledgeRetrievalRound {
  round: number
  mode: string
  query: string
  trigger: string
  quality_reason: string | null
  document_count?: number | null
  top_score?: number | null
  score_threshold?: number | null
  path_count?: number | null
  entity_count?: number | null
  content_found: boolean
}

export interface KnowledgeRetrievalResponse {
  content: string
  actual_mode: string
  first_mode: string
  final_mode: string
  second_pass_used: boolean
  fallback_triggered: boolean
  fallback_reason: string | null
  round_count: number
  metadata?: {
    first_mode: string
    final_mode: string
    second_pass_used: boolean
    fallback_triggered: boolean
    fallback_reason: string | null
    final_quality_reason?: string | null
    round_count: number
    rounds: KnowledgeRetrievalRound[]
    query_variants: string[]
    rewritten_query_used: boolean
  }
}

export function getKnowledgeListAPI() {
  return request<UnifiedResponse<KnowledgeResponse[]>>({
    url: '/api/v1/knowledge/select',
    method: 'GET',
  })
}

export function createKnowledgeAPI(data: KnowledgeCreateRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge/create',
    method: 'POST',
    data,
  })
}

export function updateKnowledgeAPI(data: KnowledgeUpdateRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge/update',
    method: 'PUT',
    data,
  })
}

export function deleteKnowledgeAPI(data: KnowledgeDeleteRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge/delete',
    method: 'DELETE',
    data,
  })
}

export function knowledgeRetrievalAPI(data: KnowledgeRetrievalRequest) {
  return request<UnifiedResponse<KnowledgeRetrievalResponse>>({
    url: '/api/v1/knowledge/retrieval',
    method: 'POST',
    data,
  })
}
