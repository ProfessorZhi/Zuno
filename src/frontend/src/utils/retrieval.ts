const retrievalModeOptions = [
  {
    value: 'rag',
    label: '纯 RAG',
    description: '只使用文本/多模态向量召回、重排和阈值过滤，适合普通文档问答。',
  },
  {
    value: 'rag_graph',
    label: 'RAG + GraphRAG',
    description: '先用 RAG 找入口证据，再沿知识图谱扩展实体和关系路径，适合关系追问。',
  },
] as const

export type RetrievalMode = typeof retrievalModeOptions[number]['value']

const legacyModeMap: Record<string, RetrievalMode> = {
  auto: 'rag',
  default: 'rag',
  hybrid: 'rag_graph',
  graphrag: 'rag_graph',
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
