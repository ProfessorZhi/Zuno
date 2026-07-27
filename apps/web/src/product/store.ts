import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type {
  AgentCatalogEntry,
  AgentDefinition,
  AgentDraft,
  AgentInstallation,
  AgentPublication,
  AgentVersion,
  AvailableAction,
  ChannelDelivery,
  ConnectionStatus,
  ProductProjection,
  ProductStreamEvent,
  ProjectionFreshness,
} from './contracts'

export interface ProductProjectionRecord {
  projection: ProductProjection
  received_at: string
}

export interface ProductInterruptProjection {
  interrupt_ref: string
  run_ref: string
  kind:
    | 'USER_INPUT'
    | 'APPROVAL'
    | 'EXTERNAL_JOB'
    | 'SECURITY_REVIEW'
    | 'MANUAL_RECONCILIATION'
    | 'RESOURCE_AVAILABLE'
    | 'INGESTION_COMPLETION'
  projection_version: number
  available_action_refs: string[]
}

export interface ProductArtifactProjection {
  artifact_ref: string
  publication_ref: string
  projection_version: number
  downloadable: boolean
  citation_refs: string[]
  citation_count?: number
  citation_authorized?: boolean
  download_policy?: string
}

export interface ProductQualityProjection {
  quality_ref: string
  projection_version: number
  status: 'UNMEASURED' | 'RUNTIME_OBSERVED' | 'MEASURED' | 'BLOCKED' | 'INCOMPARABLE'
  blocked_reason?: string
  metrics?: Record<string, number | string | boolean | null>
  disclosure?: string
}

export const useProductProjectionStore = defineStore(
  'product_projection',
  () => {
    const connectionStatus = ref<ConnectionStatus>('DISCONNECTED')
    const freshness = ref<ProjectionFreshness>('CURRENT')
    const lastEventId = ref<string>('')
    const lastSequenceNo = ref(0)
    const sourceWatermark = ref(0)
    const projectionVersion = ref(0)
    const gapDetected = ref(false)
    const resyncRequired = ref(false)

    const projections = ref<Record<string, ProductProjectionRecord>>({})
    const availableActions = ref<Record<string, AvailableAction>>({})
    const agentDefinitions = ref<Record<string, AgentDefinition>>({})
    const catalogEntries = ref<Record<string, AgentCatalogEntry>>({})
    const agentVersions = ref<Record<string, AgentVersion>>({})
    const agentDrafts = ref<Record<string, AgentDraft>>({})
    const publications = ref<Record<string, AgentPublication>>({})
    const installations = ref<Record<string, AgentInstallation>>({})
    const interrupts = ref<Record<string, ProductInterruptProjection>>({})
    const artifacts = ref<Record<string, ProductArtifactProjection>>({})
    const deliveries = ref<Record<string, ChannelDelivery>>({})
    const quality = ref<Record<string, ProductQualityProjection>>({})

    const sortedAvailableActions = computed(() =>
      Object.values(availableActions.value).sort((left, right) => left.expires_at.localeCompare(right.expires_at))
    )
    const pendingInterrupts = computed(() => Object.values(interrupts.value))
    const needsResync = computed(() => gapDetected.value || resyncRequired.value || freshness.value === 'GAP' || freshness.value === 'RESYNC_REQUIRED')

    const applyProjection = (projection: ProductProjection, actions: AvailableAction[] = []) => {
      if (projection.projection_version < projectionVersion.value) {
        return false
      }
      projectionVersion.value = projection.projection_version
      sourceWatermark.value = Math.max(sourceWatermark.value, projection.source_watermark)
      freshness.value = projection.freshness
      gapDetected.value = projection.freshness === 'GAP'
      resyncRequired.value = projection.freshness === 'RESYNC_REQUIRED'
      projections.value[projection.projection_event_id] = {
        projection,
        received_at: new Date().toISOString(),
      }
      replaceAvailableActions(actions)
      return true
    }

    const applyStreamEvent = (event: ProductStreamEvent) => {
      if (event.sequence_no <= lastSequenceNo.value && event.event_id === lastEventId.value) {
        return false
      }
      lastEventId.value = event.event_id
      lastSequenceNo.value = Math.max(lastSequenceNo.value, event.sequence_no)
      if (event.resync_required || event.event_type === 'GAP' || event.event_type === 'RESYNC_REQUIRED') {
        freshness.value = 'RESYNC_REQUIRED'
        gapDetected.value = true
        resyncRequired.value = true
      }
      if (event.event_type === 'REVOKED') {
        purgeAuthorizedView()
        freshness.value = 'REVOKED'
      }
      return true
    }

    const replaceAvailableActions = (actions: AvailableAction[]) => {
      availableActions.value = Object.fromEntries(actions.map((action) => [action.action_token_id, action]))
    }

    const upsertAgentDefinition = (definition: AgentDefinition) => {
      agentDefinitions.value[definition.agent_definition_id] = definition
    }

    const upsertCatalogEntry = (entry: AgentCatalogEntry) => {
      catalogEntries.value[entry.catalog_entry_id] = entry
    }

    const upsertAgentDraft = (draft: AgentDraft) => {
      agentDrafts.value[draft.agent_draft_id] = draft
    }

    const upsertAgentVersion = (version: AgentVersion) => {
      agentVersions.value[version.agent_version_id] = version
    }

    const upsertPublication = (publication: AgentPublication) => {
      publications.value[publication.publication_id] = publication
    }

    const upsertInstallation = (installation: AgentInstallation) => {
      installations.value[installation.installation_id] = installation
    }

    const upsertInterrupt = (interrupt: ProductInterruptProjection) => {
      interrupts.value[interrupt.interrupt_ref] = interrupt
    }

    const upsertArtifact = (artifact: ProductArtifactProjection) => {
      artifacts.value[artifact.artifact_ref] = artifact
    }

    const upsertDelivery = (delivery: ChannelDelivery) => {
      deliveries.value[delivery.delivery_id] = delivery
    }

    const upsertQuality = (item: ProductQualityProjection) => {
      quality.value[item.quality_ref] = item
    }

    const markResyncRequired = () => {
      freshness.value = 'RESYNC_REQUIRED'
      resyncRequired.value = true
    }

    const completeResync = (nextWatermark: number, nextProjectionVersion: number) => {
      sourceWatermark.value = nextWatermark
      projectionVersion.value = nextProjectionVersion
      freshness.value = 'CURRENT'
      gapDetected.value = false
      resyncRequired.value = false
    }

    const setConnectionStatus = (status: ConnectionStatus) => {
      connectionStatus.value = status
    }

    const purgeAuthorizedView = () => {
      availableActions.value = {}
      agentDefinitions.value = {}
      catalogEntries.value = {}
      interrupts.value = {}
      artifacts.value = {}
      deliveries.value = {}
      quality.value = {}
    }

    return {
      connectionStatus,
      freshness,
      lastEventId,
      lastSequenceNo,
      sourceWatermark,
      projectionVersion,
      gapDetected,
      resyncRequired,
      projections,
      availableActions,
      agentDefinitions,
      catalogEntries,
      agentVersions,
      agentDrafts,
      publications,
      installations,
      interrupts,
      artifacts,
      deliveries,
      quality,
      sortedAvailableActions,
      pendingInterrupts,
      needsResync,
      applyProjection,
      applyStreamEvent,
      replaceAvailableActions,
      upsertAgentDefinition,
      upsertCatalogEntry,
      upsertAgentDraft,
      upsertAgentVersion,
      upsertPublication,
      upsertInstallation,
      upsertInterrupt,
      upsertArtifact,
      upsertDelivery,
      upsertQuality,
      markResyncRequired,
      completeResync,
      setConnectionStatus,
      purgeAuthorizedView,
    }
  },
  {
    persist: {
      paths: ['lastEventId', 'lastSequenceNo', 'sourceWatermark', 'projectionVersion'],
    },
  }
)
