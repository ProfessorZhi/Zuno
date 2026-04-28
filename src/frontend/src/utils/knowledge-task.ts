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
  rag_indexing: '检索处理中',
  graph_extracting: '图谱抽取中',
  graph_indexing: '图谱索引中',
  completed: '已完成',
  failed: '失败',
}

export interface KnowledgeFileProgressSource {
  status?: string | number | null
  parse_status?: string | number | null
  rag_index_status?: string | number | null
  graph_index_status?: string | number | null
  last_error?: string | null
}

export interface KnowledgeProgressSummary {
  total: number
  completed: number
  processing: number
  pending: number
  failed: number
  completionRate: number
  label: string
}

const normalizeStatus = (status?: string | number | null) => String(status || '').trim().toLowerCase()

export const isSuccessStatus = (status?: string | number | null) => {
  const value = normalizeStatus(status)
  return value.includes('success') || value.includes('completed') || value.includes('done')
}

export const isFailedStatus = (status?: string | number | null) => {
  const value = normalizeStatus(status)
  return value.includes('fail') || value.includes('error') || value.includes('broken')
}

export const isPendingStatus = (status?: string | number | null) => {
  const value = normalizeStatus(status)
  return value.includes('pending') || value.includes('queued')
}

export const isProcessingStatus = (status?: string | number | null) => {
  const value = normalizeStatus(status)
  return ['running', 'process', 'parsing', 'splitting', 'indexing', 'extracting']
    .some((keyword) => value.includes(keyword))
}

export const getStatusLabel = (status?: string | number | null) => {
  if (isSuccessStatus(status)) return '已完成'
  if (isFailedStatus(status)) return '失败'
  if (isPendingStatus(status)) return '待处理'
  if (isProcessingStatus(status)) return '处理中'
  return '待处理'
}

export const getFileProgressSummary = (file: KnowledgeFileProgressSource) => {
  const steps = [
    { key: '解析', status: file.parse_status },
    { key: '检索策略', status: file.rag_index_status },
    { key: '图谱', status: file.graph_index_status },
  ]
  const failedStep = steps.find((step) => isFailedStatus(step.status))
  const processingStep = steps.find((step) => isProcessingStatus(step.status))
  const pendingStep = steps.find((step) => isPendingStatus(step.status))
  const completedCount = steps.filter((step) => isSuccessStatus(step.status)).length

  let label = `${completedCount}/${steps.length} 已完成`
  if (failedStep) {
    label = `${failedStep.key}失败`
  } else if (processingStep) {
    label = `${processingStep.key}处理中`
  } else if (pendingStep) {
    label = `${pendingStep.key}待处理`
  }

  return {
    steps,
    completedCount,
    total: steps.length,
    label,
  }
}

export const summarizeKnowledgeProgress = (files: KnowledgeFileProgressSource[]): KnowledgeProgressSummary => {
  const total = files.length
  const completed = files.filter((file) => {
    const hasFailure = Boolean(file.last_error)
      || isFailedStatus(file.status)
      || isFailedStatus(file.parse_status)
      || isFailedStatus(file.rag_index_status)
      || isFailedStatus(file.graph_index_status)

    if (hasFailure) return false

    const hasProcessing = isProcessingStatus(file.status)
      || isProcessingStatus(file.parse_status)
      || isProcessingStatus(file.rag_index_status)
      || isProcessingStatus(file.graph_index_status)

    const allDone = isSuccessStatus(file.status)
      || (
        isSuccessStatus(file.parse_status)
        && isSuccessStatus(file.rag_index_status)
        && isSuccessStatus(file.graph_index_status)
      )

    return !hasProcessing && allDone
  }).length

  const failed = files.filter((file) => (
    Boolean(file.last_error)
    || isFailedStatus(file.status)
    || isFailedStatus(file.parse_status)
    || isFailedStatus(file.rag_index_status)
    || isFailedStatus(file.graph_index_status)
  )).length

  const processing = files.filter((file) => (
    !Boolean(file.last_error)
    && !isFailedStatus(file.status)
    && (
      isProcessingStatus(file.status)
      || isProcessingStatus(file.parse_status)
      || isProcessingStatus(file.rag_index_status)
      || isProcessingStatus(file.graph_index_status)
    )
  )).length

  const pending = files.filter((file) => (
    !Boolean(file.last_error)
    && !isFailedStatus(file.status)
    && (
      isPendingStatus(file.status)
      || isPendingStatus(file.parse_status)
      || isPendingStatus(file.rag_index_status)
      || isPendingStatus(file.graph_index_status)
    )
  )).length
  const completionRate = total === 0 ? 0 : Math.round((completed / total) * 100)

  let label = '暂无文件'
  if (total > 0) {
    if (completed === 0 && processing === 0 && failed === 0) {
      label = `${pending}/${total} 待处理`
    } else {
      const parts = [`${completed}/${total} 已完成`]
      if (processing > 0) {
        parts.push(`${processing} 个处理中`)
      }
      if (pending > 0) {
        parts.push(`${pending} 个待处理`)
      }
      if (failed > 0) {
        parts.push(`${failed} 个失败`)
      }
      label = parts.join('，')
    }
  }

  return {
    total,
    completed,
    processing,
    pending,
    failed,
    completionRate,
    label,
  }
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
