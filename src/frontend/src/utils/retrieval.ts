export const retrievalModeOptions = [
  {
    value: 'auto',
    label: '自动补检',
    description: '先走知识库默认路线，首轮结果偏弱时最多自动补检一轮更合适的路线。',
  },
  {
    value: 'hybrid',
    label: '混合检索',
    description: '并行融合向量召回与图谱检索结果，适合信息分散或既要文档也要关系线索的场景。',
  },
  {
    value: 'rag',
    label: '智能补检',
    description: '先做向量召回，首轮不足时最多自动补检一轮并重排，适合普通文档型知识库。',
  },
  {
    value: 'graphrag',
    label: '图谱检索',
    description: '优先走图谱关系链路，适合结构化知识、关系追问和多跳查询。',
  },
] as const

export type RetrievalMode = typeof retrievalModeOptions[number]['value']

export interface RetrievalTraceMetadata {
  requestedMode?: string | null
  actualMode?: string | null
  firstMode?: string | null
  finalMode?: string | null
  secondPassUsed?: boolean | null
  fallbackTriggered?: boolean | null
  fallbackReason?: string | null
}

export const retrievalModeLabelMap = Object.fromEntries(
  retrievalModeOptions.map((item) => [item.value, item.label]),
) as Record<RetrievalMode, string>

const fallbackReasonLabelMap: Record<string, string> = {
  empty_result: '首轮没有命中有效内容',
  too_few_documents: '首轮命中文档过少',
  low_rerank_score: '首轮结果强度偏弱',
}

export const normalizeRetrievalMode = (mode?: string | null): RetrievalMode => {
  const value = String(mode || 'auto').toLowerCase()
  return value in retrievalModeLabelMap ? (value as RetrievalMode) : 'auto'
}

export const getRetrievalModeLabel = (mode?: string | null) => (
  retrievalModeLabelMap[normalizeRetrievalMode(mode)]
)

export const getFallbackReasonLabel = (reason?: string | null) => {
  const normalized = String(reason || '').trim().toLowerCase()
  if (!normalized) return '首轮结果偏弱'
  return fallbackReasonLabelMap[normalized] || normalized.replace(/_/g, ' ')
}

export const buildBoundedRetrievalCopy = (mode?: string | null) => (
  `${getRetrievalModeLabel(mode)} / 首轮不足时最多自动补检一轮`
)

export const buildRetrievalTraceSummary = (metadata?: RetrievalTraceMetadata | null) => {
  const requestedMode = metadata?.requestedMode || metadata?.actualMode || metadata?.finalMode || metadata?.firstMode
  const firstMode = metadata?.firstMode || metadata?.actualMode || requestedMode
  const finalMode = metadata?.finalMode || metadata?.actualMode || firstMode
  const secondPassUsed = Boolean(metadata?.secondPassUsed || metadata?.fallbackTriggered)

  if (!firstMode && !finalMode && !requestedMode) {
    return '检索策略：按知识库默认路线执行，首轮不足时最多自动补检一轮。'
  }

  if (!secondPassUsed) {
    return `检索策略：${getRetrievalModeLabel(finalMode || requestedMode)}，本次首轮已足够，无需补检。`
  }

  return `检索策略：先走 ${getRetrievalModeLabel(firstMode)}，因“${getFallbackReasonLabel(metadata?.fallbackReason)}”自动补检一轮，最终采用 ${getRetrievalModeLabel(finalMode)}。`
}
