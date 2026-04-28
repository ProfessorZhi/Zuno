import type {
  KnowledgeConfigPayload,
  KnowledgeConfigPatchPayload,
  KnowledgeModelBindingPayload,
} from '../apis/knowledge'
import type { RetrievalMode } from './retrieval'

export type KnowledgeChunkMode = 'general' | 'parent_child' | 'qa'
export type KnowledgeImageStrategy = 'text_only' | 'vl_only' | 'dual'

export interface KnowledgeModelBinding {
  llm_id: string
  model: string
  provider: string
}

export interface KnowledgeConfigSummary {
  chunkModeLabel: string
  retrievalModeLabel: string
  imageStrategyLabel: string
  textEmbeddingLabel: string
  vlEmbeddingLabel: string
  rerankLabel: string
}

const REINDEX_FIELDS = {
  index_settings: [
    'chunk_mode',
    'chunk_size',
    'overlap',
    'separator',
    'replace_consecutive_spaces',
    'remove_urls_emails',
    'image_indexing_mode',
  ] as const,
  model_refs: [
    'text_embedding_model_id',
    'vl_embedding_model_id',
  ] as const,
}

export const chunkModeOptions = [
  {
    value: 'general' as const,
    label: '通用分段',
    description: '适合大多数文档问答，检索块和回答块使用同一批内容。',
  },
  {
    value: 'parent_child' as const,
    label: '父子分段',
    description: '小块负责检索，大块保留上下文，适合长文档和章节型内容。',
  },
  {
    value: 'qa' as const,
    label: 'Q&A 分段',
    description: '更偏向问答对结构，适合 FAQ、手册和标准流程。',
  },
]

export const imageStrategyOptions = [
  {
    value: 'text_only' as const,
    label: '图片转文本',
    description: '先做图片理解，再把描述文本写入普通索引。',
  },
  {
    value: 'vl_only' as const,
    label: '仅 VL 索引',
    description: '图片优先走 VL Embedding，适合图库和视觉检索。',
  },
  {
    value: 'dual' as const,
    label: '图文双通道',
    description: '文本继续走普通向量，图片额外走 VL 向量，适合当前 Zuno。',
  },
]

export const retrievalModeOptions = [
  { value: 'auto' as const, label: '自动补检', description: '先走知识库默认路线，首轮结果偏弱时再自动补检一轮更合适的路线。' },
  { value: 'hybrid' as const, label: '混合检索', description: '结合向量召回与图谱检索，适合作为默认策略。' },
  { value: 'rag' as const, label: '智能补检', description: '先做向量召回，首轮不足时自动补检一轮并重排，适合普通文档型知识库。' },
  { value: 'graphrag' as const, label: '图谱检索', description: '优先走图谱关系检索，适合结构化知识。' },
] as const

const defaultConfig = (): KnowledgeConfigPayload => ({
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
  },
  retrieval_settings: {
    default_mode: 'hybrid',
    top_k: 5,
    rerank_enabled: true,
    rerank_top_k: 4,
    score_threshold: null,
  },
})

export const createDefaultKnowledgeConfig = defaultConfig

export const normalizeKnowledgeConfig = (
  config?: Partial<KnowledgeConfigPayload> | null,
): KnowledgeConfigPayload => {
  const base = defaultConfig()
  return {
    model_refs: {
      ...base.model_refs,
      ...(config?.model_refs || {}),
    },
    index_settings: {
      ...base.index_settings,
      ...(config?.index_settings || {}),
    },
    retrieval_settings: {
      ...base.retrieval_settings,
      ...(config?.retrieval_settings || {}),
    },
  }
}

export const toKnowledgeConfigPatch = (config: KnowledgeConfigPayload): KnowledgeConfigPatchPayload => ({
  model_refs: { ...config.model_refs },
  index_settings: { ...config.index_settings },
  retrieval_settings: { ...config.retrieval_settings },
})

export const mapModelToBinding = (
  model?: { llm_id: string; model: string; provider: string } | null,
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
  options: Array<{ llm_id: string; model: string; provider: string }>,
): KnowledgeModelBinding | null => {
  if (!modelId) return null
  const found = options.find((item) => item.llm_id === modelId)
  return mapModelToBinding(found)
}

export const bindingLabel = (
  binding?: KnowledgeModelBindingPayload | KnowledgeModelBinding | null,
  fallback = '未选择',
) => {
  if (!binding) return fallback
  return binding.model
}

export const getChunkModeLabel = (mode: KnowledgeChunkMode) => (
  chunkModeOptions.find((item) => item.value === mode)?.label || '通用分段'
)

export const getImageStrategyLabel = (strategy: KnowledgeImageStrategy) => (
  imageStrategyOptions.find((item) => item.value === strategy)?.label || '图文双通道'
)

export const getRetrievalModeLabel = (mode: RetrievalMode) => (
  retrievalModeOptions.find((item) => item.value === mode)?.label || '混合检索'
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
    chunkModeLabel: getChunkModeLabel(config.index_settings.chunk_mode),
    retrievalModeLabel: getRetrievalModeLabel(config.retrieval_settings.default_mode as RetrievalMode),
    imageStrategyLabel: getImageStrategyLabel(config.index_settings.image_indexing_mode),
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
  const imageHint = config.index_settings.image_indexing_mode === 'dual'
    ? '图片会同时保留描述文本索引和 VL 图像向量索引。'
    : config.index_settings.image_indexing_mode === 'vl_only'
      ? '图片会优先走 VL 向量索引。'
      : '图片会先转成描述文本，再进入普通文本索引。'
  const retrievalHint = `默认检索模式是 ${getRetrievalModeLabel(config.retrieval_settings.default_mode as RetrievalMode)}，Top K=${config.retrieval_settings.top_k}。`
  const chunkHint = `分段长度 ${config.index_settings.chunk_size}，重叠 ${config.index_settings.overlap}，分段模式 ${getChunkModeLabel(config.index_settings.chunk_mode)}。`

  return [
    `${title}：${description}`,
    chunkHint,
    `${imageHint} ${retrievalHint} 首轮不足时会自动补检一轮。`,
  ]
}

export const detectReindexImpact = (
  previousInput?: Partial<KnowledgeConfigPayload> | null,
  nextInput?: Partial<KnowledgeConfigPayload> | null,
) => {
  const previous = normalizeKnowledgeConfig(previousInput)
  const next = normalizeKnowledgeConfig(nextInput)
  const changedIndexFields: string[] = []
  const changedQueryFields: string[] = []

  REINDEX_FIELDS.index_settings.forEach((key) => {
    if (previous.index_settings[key] !== next.index_settings[key]) {
      changedIndexFields.push(`index_settings.${key}`)
    }
  })

  REINDEX_FIELDS.model_refs.forEach((key) => {
    if (previous.model_refs[key] !== next.model_refs[key]) {
      changedIndexFields.push(`model_refs.${key}`)
    }
  })

  ;(['default_mode', 'top_k', 'rerank_enabled', 'rerank_top_k', 'score_threshold'] as const).forEach((key) => {
    if (previous.retrieval_settings[key] !== next.retrieval_settings[key]) {
      changedQueryFields.push(`retrieval_settings.${key}`)
    }
  })

  if (previous.model_refs.rerank_model_id !== next.model_refs.rerank_model_id) {
    changedQueryFields.push('model_refs.rerank_model_id')
  }

  return {
    requiresReindex: changedIndexFields.length > 0,
    changedIndexFields,
    changedQueryFields,
  }
}
