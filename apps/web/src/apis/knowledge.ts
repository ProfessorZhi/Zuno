import { request } from '../utils/request'

export interface UnifiedResponse<T = any> {
  status_code: number
  status_message: string
  data?: T
}

export interface KnowledgeConfigPayload {
  index_capability: 'rag' | 'rag_graph'
  graphrag_project_id: string | null
  domain_pack_id: string | null
  eval_profile_id: string | null
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
    vector_backend: 'milvus' | 'chroma' | 'milvus_lite'
    index_version: string
    status: 'active' | 'disabled' | 'archived'
    health_status: 'ready' | 'degraded' | 'stale' | 'failed' | 'unavailable'
  }
  graph_index_settings: {
    entity_extraction_mode: 'rule' | 'llm' | 'rule_llm'
    relation_schema: 'open' | 'typed'
    entity_normalization: boolean
    evidence_backlink: boolean
    use_rag_entry_chunk: boolean
    community_report_prompt_id: string | null
    index_version: string
    health_status: 'ready' | 'degraded' | 'stale' | 'failed' | 'unavailable'
    graph_index_status?: 'ready' | 'queued' | 'running' | 'stale' | 'failed' | 'unavailable' | 'not_built'
    community_detection_status?: 'ready' | 'queued' | 'running' | 'stale' | 'failed' | 'unavailable' | 'not_built'
    community_report_status?: 'ready' | 'queued' | 'running' | 'stale' | 'failed' | 'unavailable' | 'not_built'
    community_version?: string
  }
  retrieval_settings: {
    default_mode: 'auto' | 'hybrid' | 'rag' | 'graphrag' | 'rag_graph' | 'rag_graph_deep'
    profile: string
    refill_policy: 'none' | 'auto' | 'smart'
    top_k: number
    rerank_enabled: boolean
    rerank_top_k: number
    score_threshold: number | null
    graph_hop_limit: number
    max_paths_per_entity: number
  }
}

export interface KnowledgeConfigPatchPayload {
  index_capability?: KnowledgeConfigPayload['index_capability']
  graphrag_project_id?: string | null
  domain_pack_id?: string | null
  eval_profile_id?: string | null
  model_refs?: Partial<KnowledgeConfigPayload['model_refs']>
  index_settings?: Partial<KnowledgeConfigPayload['index_settings']>
  graph_index_settings?: Partial<KnowledgeConfigPayload['graph_index_settings']>
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

export type KnowledgeReindexAction =
  | 'text_index'
  | 'image_index'
  | 'bm25_index'
  | 'graph_index'
  | 'community_detection'
  | 'community_report'
  | 'full_rebuild'

export interface KnowledgeConfigImpactResponse {
  changed_fields: string[]
  immediate_effect_fields: string[]
  text_reindex_required: boolean
  image_reindex_required: boolean
  bm25_reindex_required: boolean
  graph_update_required: boolean
  community_detection_required: boolean
  community_report_required: boolean
  full_rebuild_required: boolean
  recommended_action: KnowledgeReindexAction | 'save_only'
}

export interface KnowledgeModelBindingPayload {
  llm_id: string
  model: string
  provider: string
}

interface KnowledgeRetrievalRequest {
  query: string
  knowledge_id: string | string[]
  top_k?: number
  retrieval_mode?: string
}

interface KnowledgeRetrievalRound {
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

interface KnowledgeRetrievalResponse {
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
  return request<UnifiedResponse<KnowledgeResponse>>({
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

export function getKnowledgeConfigAPI(knowledgeId: string) {
  return request<UnifiedResponse<KnowledgeConfigPayload>>({
    url: `/api/v1/knowledge/${knowledgeId}/config`,
    method: 'GET',
  })
}

export function updateKnowledgeConfigAPI(knowledgeId: string, nextConfig: KnowledgeConfigPayload) {
  return request<UnifiedResponse<null>>({
    url: `/api/v1/knowledge/${knowledgeId}/config`,
    method: 'PUT',
    data: {
      next_config: nextConfig,
    },
  })
}

export function analyzeKnowledgeConfigImpactAPI(knowledgeId: string, nextConfig: KnowledgeConfigPayload) {
  return request<UnifiedResponse<KnowledgeConfigImpactResponse>>({
    url: `/api/v1/knowledge/${knowledgeId}/config/impact`,
    method: 'POST',
    data: {
      next_config: nextConfig,
    },
  })
}

export function runKnowledgeReindexActionAPI(knowledgeId: string, action: KnowledgeReindexAction) {
  return request<UnifiedResponse<{ knowledge_id: string; action: KnowledgeReindexAction; status: string }>>({
    url: `/api/v1/knowledge/${knowledgeId}/reindex/${action}`,
    method: 'POST',
  })
}

export function deleteKnowledgeAPI(data: KnowledgeDeleteRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge/delete',
    method: 'DELETE',
    data,
  })
}
