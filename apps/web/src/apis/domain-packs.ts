import { request } from '../utils/request'
import type { UnifiedResponse } from './knowledge'

export interface DomainPackSummary {
  pack_id: string
  name: string
  version?: string
  description?: string
  status: 'draft' | 'published'
}

export interface DomainPackDetail extends DomainPackSummary {
  id?: string
  schema_data?: Record<string, any>
  extraction_prompt_text?: string
  retrieval_policy_data?: Record<string, any>
  answer_template_text?: string
  report_template_text?: string
  eval_dataset_text?: string
  source_knowledge_id?: string
  representative_file_ids?: string[]
}

export interface DomainPackDraftPayload {
  pack_id: string
  name: string
  version?: string
  description?: string
  schema_data?: Record<string, any>
  extraction_prompt_text?: string
  retrieval_policy_data?: Record<string, any>
  answer_template_text?: string
  report_template_text?: string
  eval_dataset_text?: string
  default_retrieval_profile?: string | null
  default_eval_profile_id?: string | null
}

export interface DomainPackDraftFromKnowledgePayload extends DomainPackDraftPayload {
  knowledge_id: string
  file_ids?: string[]
}

export function getDomainPacksAPI() {
  return request<UnifiedResponse<DomainPackSummary[]>>({
    url: '/api/v1/domain-packs',
    method: 'GET',
  })
}

export function getDomainPackDetailAPI(packId: string) {
  return request<UnifiedResponse<DomainPackDetail>>({
    url: `/api/v1/domain-packs/${packId}`,
    method: 'GET',
  })
}

export function createDomainPackDraftAPI(data: DomainPackDraftPayload) {
  return request<UnifiedResponse<DomainPackSummary>>({
    url: '/api/v1/domain-packs/draft',
    method: 'POST',
    data,
  })
}

export function createDomainPackDraftFromKnowledgeAPI(data: DomainPackDraftFromKnowledgePayload) {
  return request<UnifiedResponse<DomainPackSummary>>({
    url: '/api/v1/domain-packs/draft/from-knowledge',
    method: 'POST',
    data,
  })
}

export function updateDomainPackAPI(packId: string, data: Partial<DomainPackDraftPayload>) {
  return request<UnifiedResponse<DomainPackSummary>>({
    url: `/api/v1/domain-packs/${packId}`,
    method: 'PUT',
    data,
  })
}

export function publishDomainPackAPI(packId: string) {
  return request<UnifiedResponse<DomainPackSummary>>({
    url: `/api/v1/domain-packs/${packId}/publish`,
    method: 'POST',
  })
}
