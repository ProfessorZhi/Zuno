export const retrievalModeOptions = [
  { value: 'default', label: '跟随知识库默认', description: '优先沿用知识库配置的默认检索策略。' },
  { value: 'rag', label: 'RAG', description: '标准向量或混合检索，适合文档片段问答。' },
  { value: 'graphrag', label: 'GraphRAG', description: '优先走图谱关系检索，适合关系推理问题。' },
  { value: 'hybrid', label: 'Hybrid', description: '并行融合 RAG 与 GraphRAG 的检索结果。' },
  { value: 'auto', label: 'Auto', description: '根据问题类型自动选择更合适的检索策略。' },
] as const

export const retrievalModeLabelMap = Object.fromEntries(
  retrievalModeOptions.map((item) => [item.value, item.label]),
) as Record<string, string>

export const normalizeRetrievalMode = (mode?: string | null) => {
  const value = String(mode || 'rag').toLowerCase()
  return retrievalModeLabelMap[value] ? value : 'rag'
}

export const getRetrievalModeLabel = (mode?: string | null) => (
  retrievalModeLabelMap[normalizeRetrievalMode(mode)]
)
