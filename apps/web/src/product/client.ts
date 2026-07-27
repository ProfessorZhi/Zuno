import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { AxiosError } from 'axios'
import { apiUrl } from '../utils/api'
import { request } from '../utils/request'
import type {
  AvailableAction,
  ProductProblemDetail,
  ProductProblemType,
  ProductStreamEvent,
  ProjectionFreshness,
} from './contracts'

export interface ProductRuntimeRequestCommand {
  tenant_id: string
  workspace_id: string
  conversation_id: string
  client_request_id?: string
  runtime_request_ref: string
  raw_intent_ref: string
  command_kind: string
  active_agent_version_id: string
  payload: Record<string, unknown>
}

export interface ProductActionConsumeCommand {
  tenant_id: string
  action_token_id: string
  client_request_id?: string
  raw_intent_ref: string
  payload: Record<string, unknown>
}

export interface ProductRuntimeRequestReceipt {
  command_id: string
  receipt_id: string
  status: string
  projection: {
    projection_event_id: string
    stream_cursor_id: string
    stream_sequence_no: number
    freshness: Lowercase<ProjectionFreshness> | string
  }
  available_actions: AvailableAction[]
}

export interface ProductActionConsumeReceipt {
  action_token_id: string
  command_id: string
  receipt_id: string
  status: string
  target_ref: string
  used_at: string
}

export interface ProductStreamEventList {
  events: ProductStreamEvent[]
}

interface UnifiedResponse<T> {
  status_code?: number
  status?: number
  message?: string
  msg?: string
  data?: T
}

const COMMAND_RETRY_BLOCKED = new Set(['post:/api/v1/product/runtime-requests', 'post:/api/v1/product/actions/consume'])

export const createProductClientRequestId = (prefix = 'product-command') => {
  const uuid = typeof crypto !== 'undefined' && 'randomUUID' in crypto ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`
  return `${prefix}:${uuid}`
}

export const shouldRetryProductTransportFailure = (method: string, path: string, problem: ProductProblemDetail) => {
  const key = `${method.toLowerCase()}:${path}`
  if (COMMAND_RETRY_BLOCKED.has(key)) {
    return false
  }
  return problem.retryable && problem.status >= 500
}

export const normalizeProductProblem = (error: unknown): ProductProblemDetail => {
  const axiosError = error as AxiosError<any>
  const status = axiosError.response?.status ?? 0
  const payload = axiosError.response?.data
  const rawType = payload?.type || payload?.data?.type
  const message = payload?.message || payload?.msg || payload?.detail || axiosError.message || 'Product request failed'

  return {
    type: mapProblemType(status, rawType),
    title: String(payload?.title || message),
    status,
    detail: String(message),
    instance: payload?.instance,
    trace_id: payload?.trace_id || payload?.data?.trace_id,
    retryable: status === 429 || status >= 500 || status === 0,
  }
}

export const submitProductRuntimeRequest = async (
  command: ProductRuntimeRequestCommand
): Promise<ProductRuntimeRequestReceipt> => {
  const body = {
    ...command,
    client_request_id: command.client_request_id || createProductClientRequestId('runtime-request'),
  }
  const response = await request.post<UnifiedResponse<ProductRuntimeRequestReceipt>>('/api/v1/product/runtime-requests', body)
  return unwrapProductResponse(response.data)
}

export const consumeProductAction = async (
  command: ProductActionConsumeCommand
): Promise<ProductActionConsumeReceipt> => {
  const body = {
    ...command,
    client_request_id: command.client_request_id || createProductClientRequestId('action-consume'),
  }
  const response = await request.post<UnifiedResponse<ProductActionConsumeReceipt>>('/api/v1/product/actions/consume', body)
  return unwrapProductResponse(response.data)
}

export const listProductStreamEvents = async (params: {
  tenant_id: string
  workspace_id: string
  last_event_id?: string
}): Promise<ProductStreamEventList> => {
  const response = await request.get<UnifiedResponse<ProductStreamEventList>>('/api/v1/product/stream-events', {
    params: {
      tenant_id: params.tenant_id,
      workspace_id: params.workspace_id,
    },
    headers: params.last_event_id ? { 'Last-Event-ID': params.last_event_id } : undefined,
  })
  return unwrapProductResponse(response.data)
}

export const openProductProjectionStream = async (
  params: {
    tenant_id: string
    workspace_id: string
    last_event_id?: string
    signal?: AbortSignal
  },
  handlers: {
    onEvent?: (event: ProductStreamEvent) => void
    onProblem?: (problem: ProductProblemDetail) => void
    onClose?: () => void
  }
) => {
  const token = localStorage.getItem('token')
  await fetchEventSource(
    apiUrl(`/api/v1/product/stream?tenant_id=${encodeURIComponent(params.tenant_id)}&workspace_id=${encodeURIComponent(params.workspace_id)}`),
    {
      method: 'GET',
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
        ...(params.last_event_id ? { 'Last-Event-ID': params.last_event_id } : {}),
      },
      signal: params.signal,
      openWhenHidden: true,
      onmessage(message) {
        if (!message.data) return
        try {
          handlers.onEvent?.(JSON.parse(message.data) as ProductStreamEvent)
        } catch (error) {
          handlers.onProblem?.(normalizeProductProblem(error))
        }
      },
      onerror(error) {
        handlers.onProblem?.(normalizeProductProblem(error))
        throw error
      },
      onclose() {
        handlers.onClose?.()
      },
    }
  )
}

const unwrapProductResponse = <T>(payload: UnifiedResponse<T>): T => {
  if (payload?.data !== undefined) {
    return payload.data
  }
  throw normalizeProductProblem({ response: { status: payload?.status_code || payload?.status || 500, data: payload } })
}

const mapProblemType = (status: number, type?: string): ProductProblemType => {
  if (type) {
    return String(type).toUpperCase() as ProductProblemType
  }
  if (status === 401) return 'AUTHENTICATION_REQUIRED'
  if (status === 403) return 'AUTHORIZATION_DENIED'
  if (status === 409) return 'IDEMPOTENCY_CONFLICT'
  if (status === 410) return 'ACTION_TOKEN_EXPIRED'
  if (status === 429) return 'RATE_LIMITED'
  return status >= 500 || status === 0 ? 'SERVER_ERROR' : 'CONTRACT_UNSUPPORTED'
}
