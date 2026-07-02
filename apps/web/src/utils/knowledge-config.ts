import type {
  GraphRAGProjectPayload,
  KnowledgeConfigPayload,
  KnowledgeConfigPatchPayload,
  KnowledgeModelBindingPayload,
} from '../apis/knowledge'
import type { RetrievalMode } from './retrieval'
import { getRetrievalModeLabel, retrievalModeOptions } from './retrieval'

export { getRetrievalModeLabel }

export type KnowledgeIndexCapability = 'rag' | 'rag_graph'
export type KnowledgeChunkMode = 'general' | 'parent_child' | 'qa'
export type KnowledgeImageStrategy = 'text_only' | 'vl_only' | 'dual'
export type KnowledgeVectorBackend = 'milvus' | 'chroma' | 'milvus_lite'
export type KnowledgeRefillPolicy = 'none' | 'auto' | 'smart'
export type KnowledgeProductMode = 'standard' | 'deep'
export type LegacyKnowledgeProductMode = KnowledgeProductMode | 'enhanced'
export type WorkspaceRetrievalProductProfile = 'standard' | 'deep'
type LegacyKnowledgeConfigInput = Partial<KnowledgeConfigPayload> & {
  domain_pack_id?: string | null
}

export interface KnowledgeModelBinding {
  llm_id: string
  model: string
  provider: string
}

export interface KnowledgeConfigSummary {
  indexCapabilityLabel: string
  chunkModeLabel: string
  retrievalModeLabel: string
  imageStrategyLabel: string
  vectorBackendLabel: string
  textEmbeddingLabel: string
  vlEmbeddingLabel: string
  rerankLabel: string
}

const defaultGraphRAGProject = (projectId: string): GraphRAGProjectPayload => ({
  graphrag_project_id: projectId,
  settings_path: null,
  prompt_version: 'default',
  index_version: 'v1',
  query_method: 'auto',
  query_prompt_version: 'default',
  community_version: 'v0',
  document_hash: null,
  chunk_hash: null,
  status: 'not_configured',
})

const REINDEX_FIELDS = {
  root: ['index_capability'] as const,
  index_settings: [
    'chunk_mode',
    'chunk_size',
    'overlap',
    'separator',
    'replace_consecutive_spaces',
    'remove_urls_emails',
    'image_indexing_mode',
    'vector_backend',
  ] as const,
  graph_index_settings: [
    'entity_extraction_mode',
    'relation_schema',
    'entity_normalization',
    'evidence_backlink',
    'use_rag_entry_chunk',
  ] as const,
  model_refs: [
    'text_embedding_model_id',
    'vl_embedding_model_id',
  ] as const,
}

export const indexCapabilityOptions = [
  {
    value: 'rag' as const,
    label: 'RAG',
    description: '建立向量与 BM25 所需的文本索引，不建立图谱索引，适合大多数文档问答知识库。',
  },
  {
    value: 'rag_graph' as const,
    label: 'RAG + GraphRAG',
    description: '建立标准 RAG 索引和图谱索引，查询时可在标准检索与图谱增强检索间切换。',
  },
]

export const chunkModeOptions = [
  {
    value: 'general' as const,
    label: '通用分段',
    description: '按标题、段落、长度和重叠规则切块，适合大多数 Markdown、PDF 和说明文档。',
  },
  {
    value: 'parent_child' as const,
    label: '父子分段',
    description: '小块负责召回，大块负责上下文，适合长章节、教程和需要完整语境的材料。',
  },
  {
    value: 'qa' as const,
    label: 'Q&A 分段',
    description: '保留显式问题和答案边界，适合 FAQ、操作手册和标准流程。',
  },
]

export const imageStrategyOptions = [
  {
    value: 'text_only' as const,
    label: '图片转文本',
    description: '先做 OCR/图片理解，再把描述文本写入普通文本索引。',
  },
  {
    value: 'vl_only' as const,
    label: '仅 VL 索引',
    description: '图片优先走视觉向量索引，适合图像检索场景。',
  },
  {
    value: 'dual' as const,
    label: '图文双通道',
    description: '同时保留图片描述文本索引和视觉向量索引，适合图文混合知识库。',
  },
]

export const vectorBackendOptions = [
  { value: 'milvus' as const, label: 'Milvus', description: '适合企业级 RAG，支持独立向量服务和较大规模索引。' },
  { value: 'chroma' as const, label: 'Chroma', description: '适合本地轻量原型和小规模知识库。' },
  { value: 'milvus_lite' as const, label: 'Milvus Lite', description: '适合单机开发验证，部署成本低于独立 Milvus。' },
]

export const refillPolicyOptions = [
  { value: 'none' as const, label: '不补检', description: '只使用首轮召回结果。' },
  { value: 'auto' as const, label: '自动补检', description: '首轮结果过少或低于阈值时补检一轮。' },
  { value: 'smart' as const, label: '智能补检', description: '结合命中数量、分数和图谱路径质量决定是否补检。' },
]

const defaultConfig = (): KnowledgeConfigPayload => ({
  index_capability: 'rag',
  graphrag_project_id: null,
  graphrag_project: null,
  eval_profile_id: null,
  model_refs: {
    text_embedding_model_id: null,
    vl_embedding_model_id: null,
    rerank_model_id: null,
  },
  index_settings: {
    chunk_mode: 'general',
    chunk_size: 1024,
    overlap: 120,
    separator: '\n\n',
    replace_consecutive_spaces: true,
    remove_urls_emails: false,
    image_indexing_mode: 'dual',
    vector_backend: 'milvus',
    index_version: 'v1',
    status: 'active',
    health_status: 'ready',
  },
  graph_index_settings: {
    entity_extraction_mode: 'rule_llm',
    relation_schema: 'open',
    entity_normalization: true,
    evidence_backlink: true,
    use_rag_entry_chunk: true,
    community_report_prompt_id: null,
    index_version: 'v1',
    health_status: 'ready',
    graph_index_status: 'ready',
    community_detection_status: 'not_built',
    community_report_status: 'not_built',
    community_version: 'v0',
  },
  retrieval_settings: {
    default_mode: 'rag',
    profile: 'auto',
    refill_policy: 'smart',
    top_k: 5,
    rerank_enabled: true,
    rerank_top_k: 4,
    score_threshold: null,
    graph_hop_limit: 2,
    max_paths_per_entity: 5,
  },
})

const normalizeRetrievalModeForCapability = (
  mode: string | null | undefined,
  capability: KnowledgeIndexCapability,
): KnowledgeConfigPayload['retrieval_settings']['default_mode'] => {
  const legacyMap: Record<string, KnowledgeConfigPayload['retrieval_settings']['default_mode']> = {
    auto: 'rag',
    default: 'rag',
    hybrid: 'rag_graph',
    graphrag: 'rag_graph',
  }
  const raw = String(mode || 'rag').toLowerCase()
  const normalized = (legacyMap[raw] || raw) as KnowledgeConfigPayload['retrieval_settings']['default_mode']
  if (capability === 'rag') return 'rag'
  return normalized === 'rag_graph' ? normalized : 'rag'
}

const normalizeIndexCapability = (
  capability: string | null | undefined,
  defaultMode?: string | null,
): KnowledgeIndexCapability => {
  if (capability === 'rag_graph' || capability === 'rag') return capability
  return ['hybrid', 'graphrag', 'rag_graph'].includes(String(defaultMode || '').toLowerCase())
    ? 'rag_graph'
    : 'rag'
}

export const createDefaultKnowledgeConfig = defaultConfig

export const normalizeKnowledgeConfig = (
  config?: LegacyKnowledgeConfigInput | null,
): KnowledgeConfigPayload => {
  const base = defaultConfig()
  const graphragProjectId = config?.graphrag_project_id ?? config?.domain_pack_id ?? base.graphrag_project_id
  const graphragProject = graphragProjectId
    ? {
        ...defaultGraphRAGProject(graphragProjectId),
        ...(config?.graphrag_project || {}),
        graphrag_project_id: graphragProjectId,
      }
    : null
  const merged = {
    index_capability: normalizeIndexCapability(
      config?.index_capability,
      config?.retrieval_settings?.default_mode,
    ),
    graphrag_project_id: graphragProjectId,
    graphrag_project: graphragProject,
    eval_profile_id: config?.eval_profile_id ?? base.eval_profile_id,
    model_refs: {
      ...base.model_refs,
      ...(config?.model_refs || {}),
    },
    index_settings: {
      ...base.index_settings,
      ...(config?.index_settings || {}),
    },
    graph_index_settings: {
      ...base.graph_index_settings,
      ...(config?.graph_index_settings || {}),
    },
    retrieval_settings: {
      ...base.retrieval_settings,
      ...(config?.retrieval_settings || {}),
    },
  } as KnowledgeConfigPayload
  merged.retrieval_settings.default_mode = normalizeRetrievalModeForCapability(
    merged.retrieval_settings.default_mode,
    merged.index_capability,
  )
  return merged
}

export const toWorkspaceRetrievalProfile = (
  configInput?: LegacyKnowledgeConfigInput | null,
): WorkspaceRetrievalProductProfile => {
  const rawDefaultMode = String(configInput?.retrieval_settings?.default_mode || '').trim().toLowerCase()
  if (['deep', 'rag_graph', 'graphrag', 'hybrid'].includes(rawDefaultMode)) return 'deep'
  if (['standard', 'rag', 'auto', 'default'].includes(rawDefaultMode)) return 'standard'

  const config = normalizeKnowledgeConfig(configInput)
  return config.index_capability === 'rag_graph' ? 'deep' : 'standard'
}

export const toKnowledgeConfigPatch = (config: KnowledgeConfigPayload): KnowledgeConfigPatchPayload => ({
  index_capability: config.index_capability,
  graphrag_project_id: config.graphrag_project_id,
  graphrag_project: config.graphrag_project ? { ...config.graphrag_project } : null,
  eval_profile_id: config.eval_profile_id,
  model_refs: { ...config.model_refs },
  index_settings: { ...config.index_settings },
  graph_index_settings: { ...config.graph_index_settings },
  retrieval_settings: { ...config.retrieval_settings },
})

export const toProductKnowledgeConfig = (
  mode: LegacyKnowledgeProductMode,
  overrides: Partial<KnowledgeConfigPayload> = {},
): KnowledgeConfigPayload => {
  const config = normalizeKnowledgeConfig(overrides)
  if (mode === 'deep' || mode === 'enhanced') {
    config.index_capability = 'rag_graph'
    config.retrieval_settings.default_mode = 'rag_graph'
    if (config.graphrag_project) {
      config.graphrag_project.query_method = config.graphrag_project.query_method || 'auto'
    }
    return config
  }
  config.index_capability = 'rag'
  config.retrieval_settings.default_mode = 'rag'
  config.graphrag_project_id = null
  config.graphrag_project = null
  config.graph_index_settings.graph_index_status = 'not_built'
  config.graph_index_settings.community_detection_status = 'not_built'
  config.graph_index_settings.community_report_status = 'not_built'
  return config
}

const mapModelToBinding = (
  model?: KnowledgeModelBindingPayload | null,
): KnowledgeModelBinding | null => {
  if (!model) return null
  return {
    llm_id: model.llm_id,
    model: model.model,
    provider: model.provider,
  }
}

export const findBindingById = (
  modelId: string | null | undefined,
  options: KnowledgeModelBindingPayload[],
): KnowledgeModelBinding | null => {
  if (!modelId) return null
  const found = options.find((item) => item.llm_id === modelId)
  return mapModelToBinding(found)
}

export const getIndexCapabilityLabel = (mode: KnowledgeIndexCapability) => (
  indexCapabilityOptions.find((item) => item.value === mode)?.label || 'RAG'
)

export const getChunkModeLabel = (mode: KnowledgeChunkMode) => (
  chunkModeOptions.find((item) => item.value === mode)?.label || '通用分段'
)

export const getImageStrategyLabel = (strategy: KnowledgeImageStrategy) => (
  imageStrategyOptions.find((item) => item.value === strategy)?.label || '图文双通道'
)

export const getVectorBackendLabel = (backend: KnowledgeVectorBackend) => (
  vectorBackendOptions.find((item) => item.value === backend)?.label || 'Milvus'
)

export const describeKnowledgeConfig = (
  configInput?: Partial<KnowledgeConfigPayload> | null,
  bindings?: {
    textEmbedding?: KnowledgeModelBinding | null
    vlEmbedding?: KnowledgeModelBinding | null
    rerank?: KnowledgeModelBinding | null
  },
): KnowledgeConfigSummary => {
  const config = normalizeKnowledgeConfig(configInput)
  return {
    indexCapabilityLabel: getIndexCapabilityLabel(config.index_capability),
    chunkModeLabel: getChunkModeLabel(config.index_settings.chunk_mode),
    retrievalModeLabel: getRetrievalModeLabel(config.retrieval_settings.default_mode),
    imageStrategyLabel: getImageStrategyLabel(config.index_settings.image_indexing_mode),
    vectorBackendLabel: getVectorBackendLabel(config.index_settings.vector_backend),
    textEmbeddingLabel: bindings?.textEmbedding?.model || '未选择文本 Embedding',
    vlEmbeddingLabel: bindings?.vlEmbedding?.model || '未选择 VL Embedding',
    rerankLabel: config.retrieval_settings.rerank_enabled
      ? (bindings?.rerank?.model || '已启用但未选择 Rerank')
      : '未启用 Rerank',
  }
}

export const buildKnowledgePreviewChunks = (
  knowledgeName: string,
  knowledgeDescription: string,
  configInput?: Partial<KnowledgeConfigPayload> | null,
) => {
  const config = normalizeKnowledgeConfig(configInput)
  const title = knowledgeName || '当前知识库'
  const description = knowledgeDescription || '这里会收录项目资料、文档、PDF、图片和说明信息。'
  const graphHint = config.index_capability === 'rag_graph'
    ? `查询可走标准检索或图谱增强检索，图谱扩展默认 ${config.retrieval_settings.graph_hop_limit}-hop。`
    : '当前不建立图谱索引，查询模式锁定为标准检索。'
  const graphragProjectHint = config.graphrag_project_id
    ? `当前绑定 GraphRAG Project：${config.graphrag_project_id}。`
    : '当前未绑定 GraphRAG Project。'
  const imageHint = config.index_settings.image_indexing_mode === 'dual'
    ? '图片会同时保留描述文本索引和 VL 图像向量索引。'
    : config.index_settings.image_indexing_mode === 'vl_only'
      ? '图片会优先走 VL 向量索引。'
      : '图片会先转成描述文本，再进入普通文本索引。'
  const retrievalHint = `默认检索模式是 ${getRetrievalModeLabel(config.retrieval_settings.default_mode)}，Top K=${config.retrieval_settings.top_k}。`
  const chunkHint = `分段长度 ${config.index_settings.chunk_size}，重叠 ${config.index_settings.overlap}，分段模式 ${getChunkModeLabel(config.index_settings.chunk_mode)}。`

  return [
    `${title}：${description}`,
    chunkHint,
    `${imageHint} ${retrievalHint} ${graphHint} ${graphragProjectHint}`,
  ]
}

export const getAllowedRetrievalModeOptions = (capability: KnowledgeIndexCapability) => (
  capability === 'rag'
    ? retrievalModeOptions.filter((item) => item.value === 'rag')
    : retrievalModeOptions
)

export const detectReindexImpact = (
  previousInput?: Partial<KnowledgeConfigPayload> | null,
  nextInput?: Partial<KnowledgeConfigPayload> | null,
) => {
  const previous = normalizeKnowledgeConfig(previousInput)
  const next = normalizeKnowledgeConfig(nextInput)
  const changedIndexFields: string[] = []
  const changedQueryFields: string[] = []

  REINDEX_FIELDS.root.forEach((key) => {
    if (previous[key] !== next[key]) {
      changedIndexFields.push(key)
    }
  })

  REINDEX_FIELDS.index_settings.forEach((key) => {
    if (previous.index_settings[key] !== next.index_settings[key]) {
      changedIndexFields.push(`index_settings.${key}`)
    }
  })

  REINDEX_FIELDS.graph_index_settings.forEach((key) => {
    if (previous.graph_index_settings[key] !== next.graph_index_settings[key]) {
      changedIndexFields.push(`graph_index_settings.${key}`)
    }
  })

  REINDEX_FIELDS.model_refs.forEach((key) => {
    if (previous.model_refs[key] !== next.model_refs[key]) {
      changedIndexFields.push(`model_refs.${key}`)
    }
  })

  ;([
    'default_mode',
    'profile',
    'refill_policy',
    'top_k',
    'rerank_enabled',
    'rerank_top_k',
    'score_threshold',
    'graph_hop_limit',
    'max_paths_per_entity',
  ] as const).forEach((key) => {
    if (previous.retrieval_settings[key] !== next.retrieval_settings[key]) {
      changedQueryFields.push(`retrieval_settings.${key}`)
    }
  })

  if (previous.model_refs.rerank_model_id !== next.model_refs.rerank_model_id) {
    changedQueryFields.push('model_refs.rerank_model_id')
  }
  if (previous.graphrag_project_id !== next.graphrag_project_id) {
    changedQueryFields.push('graphrag_project_id')
  }
  if (previous.eval_profile_id !== next.eval_profile_id) {
    changedQueryFields.push('eval_profile_id')
  }

  return {
    requiresReindex: changedIndexFields.length > 0,
    changedIndexFields,
    changedQueryFields,
  }
}
