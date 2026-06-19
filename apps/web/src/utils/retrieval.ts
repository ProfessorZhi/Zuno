const retrievalModeOptions = [
  {
    value: 'rag',
    label: '标准检索',
    description: '默认融合向量检索与 BM25 关键词检索，适合大多数文档问答与配置查找。',
  },
  {
    value: 'rag_graph',
    label: '增强检索',
    description: '在标准检索上增加 GraphRAG 路径扩展，适合关系追问、依赖链路和结构化问题。',
  },
] as const

export type RetrievalMode = typeof retrievalModeOptions[number]['value']

const legacyModeMap: Record<string, RetrievalMode> = {
  auto: 'rag',
  default: 'rag',
  hybrid: 'rag_graph',
  graphrag: 'rag_graph',
  rag_graph_deep: 'rag_graph',
}

const retrievalModeLabelMap = Object.fromEntries(
  retrievalModeOptions.map((item) => [item.value, item.label]),
) as Record<RetrievalMode, string>

const fallbackReasonLabelMap: Record<string, string> = {
  empty_result: '首轮没有命中有效内容',
  too_few_documents: '首轮命中文档过少',
  low_rerank_score: '首轮结果相关性偏弱',
  graph_result_empty: '图谱路径为空',
}

export const normalizeRetrievalMode = (mode?: string | null): RetrievalMode => {
  const value = String(mode || 'rag').toLowerCase()
  const mapped = legacyModeMap[value] || value
  return mapped in retrievalModeLabelMap ? (mapped as RetrievalMode) : 'rag'
}

export const getRetrievalModeLabel = (mode?: string | null) => (
  retrievalModeLabelMap[normalizeRetrievalMode(mode)]
)

export const getFallbackReasonLabel = (reason?: string | null) => {
  if (!reason) return ''
  return fallbackReasonLabelMap[reason] || reason
}

export { retrievalModeOptions }
