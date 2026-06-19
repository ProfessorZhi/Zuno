import { request } from '../utils/request'
import type { UnifiedResponse } from './knowledge'

export interface DomainPackSummary {
  pack_id: string
  name: string
  version?: string
  description?: string
  status: 'draft' | 'published'
}

export function getDomainPacksAPI() {
  return request<UnifiedResponse<DomainPackSummary[]>>({
    url: '/api/v1/domain-packs',
    method: 'GET',
  })
}

export function publishDomainPackAPI(packId: string) {
  return request<UnifiedResponse<DomainPackSummary>>({
    url: `/api/v1/domain-packs/${packId}/publish`,
    method: 'POST',
  })
}
