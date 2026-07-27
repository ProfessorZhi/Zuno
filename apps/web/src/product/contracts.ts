export const PRODUCT_CONTRACT_BUNDLE_VERSION = 'product-contract-v1.phase10'

export const PRODUCT_CONTRACT_NAMES = [
  'AgentDefinition',
  'AgentDraft',
  'AgentVersion',
  'AgentPublication',
  'AgentInstallation',
  'AgentCatalogEntry',
  'ProductCommand',
  'RuntimeRequest',
  'CommandReceipt',
  'ProductProjection',
  'AvailableAction',
  'ChannelDelivery',
] as const

export type ProductContractName = (typeof PRODUCT_CONTRACT_NAMES)[number]

export type ProductDisplayStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'WAITING'
  | 'CANCELLING'
  | 'COMPLETED'
  | 'PARTIAL'
  | 'ABSTAINED'
  | 'REFUSED'
  | 'BLOCKED'
  | 'FAILED'
  | 'CANCELLED'
  | 'EXPIRED'
  | 'UNKNOWN'

export type ProjectionFreshness =
  | 'CURRENT'
  | 'STALE'
  | 'GAP'
  | 'RESYNC_REQUIRED'
  | 'REVOKED'

export type ConnectionStatus =
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'RECONNECTING'
  | 'BACKOFF'
  | 'AUTH_REQUIRED'
  | 'CLOSED'

export type AvailableActionKind =
  | 'APPROVE'
  | 'DENY'
  | 'CANCEL'
  | 'INPUT'
  | 'RECONCILE'
  | 'DOWNLOAD'
  | 'RESYNC'

export type ProductProblemType =
  | 'AUTHENTICATION_REQUIRED'
  | 'AUTHORIZATION_DENIED'
  | 'IDEMPOTENCY_CONFLICT'
  | 'ACTION_TOKEN_EXPIRED'
  | 'PROJECTION_GAP'
  | 'CONTRACT_UNSUPPORTED'
  | 'RATE_LIMITED'
  | 'SERVER_ERROR'

export interface ProductProblemDetail {
  type: ProductProblemType
  title: string
  status: number
  detail: string
  instance?: string
  trace_id?: string
  retryable: boolean
}

export interface ProductEnvelope {
  contract_name: ProductContractName
  contract_version: string
  contract_bundle_version: typeof PRODUCT_CONTRACT_BUNDLE_VERSION
  tenant_id: string
  workspace_id: string
  principal_context_ref: string
  effective_security_epoch_ref: string
  payload_hash: string
  payload_schema_hash: string
}

export interface AgentDefinition {
  agent_definition_id: string
  tenant_id: string
  workspace_id: string
  owner_principal_ref: string
  display_name: string
  description?: string
  status: 'DRAFTING' | 'DRAFT' | 'ACTIVE' | 'ARCHIVED' | 'RETIRED' | 'REVOKED'
}

export interface AgentDraft {
  agent_draft_id: string
  agent_definition_id: string
  draft_version: number
  editor_principal_ref: string
  configuration_hash: string
  status: 'OPEN' | 'DRAFT' | 'VALIDATING' | 'READY_TO_PUBLISH' | 'LOCKED' | 'DISCARDED'
}

export interface AgentVersion {
  agent_version_id: string
  agent_definition_id: string
  version_no: number
  configuration_hash: string
  primary_agent_core_profile_ref: string
  published_from_draft_ref: string
}

export interface AgentPublication {
  publication_id: string
  agent_version_id: string
  scope: 'PRIVATE' | 'WORKSPACE' | 'TENANT'
  status: 'PUBLISHED' | 'WITHDRAWN' | 'REVOKED' | 'SUPERSEDED'
  published_at?: string
}

export interface AgentInstallation {
  installation_id: string
  agent_version_id: string
  workspace_id: string
  principal_ref?: string
  status: 'INSTALLED' | 'SUSPENDED' | 'REVOKED'
}

export interface AgentCatalogEntry {
  catalog_entry_id: string
  agent_version_id: string
  publication_ref?: string
  agent_definition_id: string
  display_name: string
  description?: string
  definition_status: AgentDefinition['status']
  authorized: boolean
  visibility_scope: AgentPublication['scope']
  effective_permission_preview_ref: string
}

export interface ProductCommand {
  command_id: string
  conversation_id: string
  command_kind: string
  idempotency_key: string
  raw_intent_ref: string
  status: 'ACCEPTED' | 'REJECTED' | 'DUPLICATE' | 'CONFLICT'
}

export interface RuntimeRequest {
  runtime_request_ref: string
  active_agent_version_id: string
  goal_ref: string
  command_ref: string
}

export interface CommandReceipt {
  receipt_id: string
  command_id: string
  status: ProductCommand['status']
  domain_success_ref?: never
}

export interface ProductProjection {
  projection_event_id: string
  source_module: string
  source_event_id: string
  source_watermark: number
  projection_version: number
  freshness: ProjectionFreshness
  display_status: ProductDisplayStatus
  redaction_decision_ref: string
}

export interface AvailableAction {
  action: AvailableActionKind
  action_token_id: string
  target_ref: string
  effective_security_epoch_ref: string
  projection_version: number
  expires_at: string
  disabled_reason?: string
}

export interface ProductStreamEvent {
  event_id: string
  event_type: 'SNAPSHOT' | 'DELTA' | 'GAP' | 'RESYNC_REQUIRED' | 'HEARTBEAT' | 'REVOKED'
  sequence_no: number
  projection_event_id?: string
  resync_required: boolean
  redaction_decision_ref: string
}

export interface ChannelDelivery {
  delivery_id: string
  publication_ref: string
  channel: 'WEB' | 'DESKTOP' | 'EXTERNAL_API'
  status: 'PENDING' | 'DELIVERED' | 'UNKNOWN' | 'FAILED'
  receipt_ref?: string
}

export interface ProductContractSchemaSentinel {
  bundle_version: typeof PRODUCT_CONTRACT_BUNDLE_VERSION
  contract_names: readonly ProductContractName[]
  unknown_enum_policy: 'fail_closed'
  frontend_fact_source: false
  product_actions_from_server_only: true
}

export const PRODUCT_CONTRACT_SCHEMA_SENTINEL: ProductContractSchemaSentinel = {
  bundle_version: PRODUCT_CONTRACT_BUNDLE_VERSION,
  contract_names: PRODUCT_CONTRACT_NAMES,
  unknown_enum_policy: 'fail_closed',
  frontend_fact_source: false,
  product_actions_from_server_only: true,
}
