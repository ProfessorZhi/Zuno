import {
  consumeProductAction,
  createProductClientRequestId,
  normalizeProductProblem,
  openProductProjectionStream,
  submitProductRuntimeRequest,
  type ProductActionConsumeReceipt,
  type ProductRuntimeRequestCommand,
  type ProductRuntimeRequestReceipt,
} from './client'
import type {
  AvailableAction,
  ProductDisplayStatus,
  ProductProjection,
  ProductStreamEvent,
  ProjectionFreshness,
} from './contracts'
import type { useProductProjectionStore } from './store'

export const PRODUCT_WEB_TENANT_ID = 'tenant:web'
export const PRODUCT_WEB_AGENT_VERSION_ID = 'agent-version:web-default'

type ProductProjectionStore = ReturnType<typeof useProductProjectionStore>

export interface ProductRuntimeSubmissionContext {
  workspace_id: string
  conversation_id: string
  query: string
  active_agent_version_id?: string
}

export interface ProductRuntimeSubmissionResult {
  receipt: ProductRuntimeRequestReceipt
  projection: ProductProjection
  accepted_actions: AvailableAction[]
}

export const submitWorkspacePayloadToProductRuntime = async (
  payload: Record<string, unknown>,
  context: ProductRuntimeSubmissionContext,
  store: ProductProjectionStore
): Promise<ProductRuntimeSubmissionResult> => {
  const command = buildProductRuntimeRequestCommand(payload, context)
  const receipt = await submitProductRuntimeRequest(command)
  const projection = productProjectionFromRuntimeReceipt(receipt)
  const acceptedActions = normalizeAvailableActionsFailClosed(receipt.available_actions, projection.projection_version)
  store.applyProjection(projection, acceptedActions)
  return { receipt, projection, accepted_actions: acceptedActions }
}

export const connectProductRuntimeProjectionStream = async (
  context: Pick<ProductRuntimeSubmissionContext, 'workspace_id'>,
  store: ProductProjectionStore,
  handlers: {
    onEvent?: (event: ProductStreamEvent) => void
    onProblem?: (problem: ReturnType<typeof normalizeProductProblem>) => void
    onClose?: () => void
  } = {}
) => {
  store.setConnectionStatus(store.lastEventId ? 'RECONNECTING' : 'CONNECTING')
  await openProductProjectionStream(
    {
      tenant_id: PRODUCT_WEB_TENANT_ID,
      workspace_id: context.workspace_id,
      last_event_id: store.lastEventId || undefined,
    },
    {
      onEvent: (event) => {
        store.applyStreamEvent(event)
        handlers.onEvent?.(event)
      },
      onProblem: (problem) => {
        if (problem.type === 'AUTHENTICATION_REQUIRED' || problem.type === 'AUTHORIZATION_DENIED') {
          store.setConnectionStatus('AUTH_REQUIRED')
          store.purgeAuthorizedView()
        } else if (problem.type === 'PROJECTION_GAP') {
          store.markResyncRequired()
        } else {
          store.setConnectionStatus('BACKOFF')
        }
        handlers.onProblem?.(problem)
      },
      onClose: () => {
        store.setConnectionStatus('CLOSED')
        handlers.onClose?.()
      },
    }
  )
}

export const consumeProductStoreAction = async (
  action: AvailableAction,
  context: ProductRuntimeSubmissionContext,
  payload: Record<string, unknown>,
  store: ProductProjectionStore
): Promise<ProductActionConsumeReceipt> => {
  const receipt = await consumeProductAction({
    tenant_id: PRODUCT_WEB_TENANT_ID,
    action_token_id: action.action_token_id,
    raw_intent_ref: `intent:${context.conversation_id}:${createProductClientRequestId('action-intent')}`,
    payload,
  })
  store.replaceAvailableActions(Object.values(store.availableActions).filter((item) => item.action_token_id !== action.action_token_id))
  return receipt
}

export const buildProductRuntimeRequestCommand = (
  payload: Record<string, unknown>,
  context: ProductRuntimeSubmissionContext
): ProductRuntimeRequestCommand => {
  const requestId = createProductClientRequestId('runtime-request')
  return {
    tenant_id: PRODUCT_WEB_TENANT_ID,
    workspace_id: context.workspace_id,
    conversation_id: context.conversation_id,
    client_request_id: requestId,
    runtime_request_ref: `runtime:${requestId}`,
    raw_intent_ref: `intent:${context.conversation_id}:${requestId}`,
    command_kind: 'SUBMIT_USER_GOAL',
    active_agent_version_id: context.active_agent_version_id || PRODUCT_WEB_AGENT_VERSION_ID,
    payload: {
      ...payload,
      goal: context.query,
    },
  }
}

export const productProjectionFromRuntimeReceipt = (receipt: ProductRuntimeRequestReceipt): ProductProjection => ({
  projection_event_id: receipt.projection.projection_event_id,
  source_module: 'product.runtime_request',
  source_event_id: receipt.command_id,
  source_watermark: receipt.projection.stream_sequence_no,
  projection_version: receipt.projection.stream_sequence_no,
  freshness: normalizeProjectionFreshness(receipt.projection.freshness),
  display_status: mapRuntimeReceiptStatus(receipt.status),
  redaction_decision_ref: receipt.projection.redaction_decision_ref,
})

export const normalizeAvailableActionsFailClosed = (
  actions: AvailableAction[],
  projectionVersion: number
): AvailableAction[] => actions.filter((action) => (
  Boolean(action.action)
  && Boolean(action.action_token_id)
  && Boolean(action.target_ref)
  && Boolean(action.effective_security_epoch_ref)
  && Number(action.projection_version) === projectionVersion
  && Boolean(action.expires_at)
))

const normalizeProjectionFreshness = (value: string): ProjectionFreshness => {
  const normalized = value.toUpperCase()
  if (['CURRENT', 'STALE', 'GAP', 'RESYNC_REQUIRED', 'REVOKED'].includes(normalized)) {
    return normalized as ProjectionFreshness
  }
  return 'RESYNC_REQUIRED'
}

const mapRuntimeReceiptStatus = (status: string): ProductDisplayStatus => {
  switch (status.toUpperCase()) {
    case 'ACCEPTED':
      return 'RUNNING'
    case 'DUPLICATE':
      return 'WAITING'
    case 'CONFLICT':
      return 'BLOCKED'
    case 'REJECTED':
      return 'REFUSED'
    default:
      return 'UNKNOWN'
  }
}
