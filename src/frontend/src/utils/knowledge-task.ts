export const pipelineStageOrder = [
  'uploaded',
  'queued',
  'parsing',
  'splitting',
  'rag_indexing',
  'graph_extracting',
  'graph_indexing',
  'completed',
] as const

const stageLabelMap: Record<string, string> = {
  uploaded: '已上传',
  queued: '已排队',
  parsing: '解析中',
  splitting: '切块中',
  rag_indexing: 'RAG 索引中',
  graph_extracting: '图谱抽取中',
  graph_indexing: 'GraphRAG 索引中',
  completed: '已完成',
  failed: '失败',
}

export const getPipelineStageLabel = (stage?: string | null) => {
  const value = String(stage || '').toLowerCase()
  return stageLabelMap[value] || (stage || '未知阶段')
}

export const getPipelineStatusTagType = (status?: string | null) => {
  const value = String(status || '').toLowerCase()
  if (value.includes('success') || value.includes('completed')) return 'success'
  if (value.includes('fail')) return 'danger'
  if (value.includes('running') || value.includes('process') || value.includes('pending') || value.includes('queued')) return 'warning'
  return 'info'
}

export const buildStageTimeline = (currentStage?: string | null, failed = false) => {
  const normalized = String(currentStage || '').toLowerCase()
  const currentIndex = pipelineStageOrder.indexOf(normalized as (typeof pipelineStageOrder)[number])
  return pipelineStageOrder.map((stage, index) => ({
    key: stage,
    label: getPipelineStageLabel(stage),
    done: currentIndex >= 0 && index < currentIndex && !failed,
    active: !failed && stage === normalized,
    failed: failed && stage === normalized,
  }))
}
