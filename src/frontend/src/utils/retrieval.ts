const retrievalModeOptions = [
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

const retrievalModeLabelMap = Object.fromEntries(
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
