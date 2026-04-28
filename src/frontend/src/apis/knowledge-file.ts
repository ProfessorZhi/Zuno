import { request } from '../utils/request'

export interface UnifiedResponse<T = any> {
  status_code: number
  status_message: string
  data?: T
}

export enum KnowledgeFileStatus {
  FAIL = 'FAIL',
  PROCESS = 'PROCESS',
  SUCCESS = 'SUCCESS',
}

export interface KnowledgeFileResponse {
  id: string
  file_name: string
  knowledge_id: string
  status: string
  parse_status?: string
  rag_index_status?: string
  graph_index_status?: string
  last_task_id?: string | null
  last_error?: string | null
  user_id: string
  oss_url: string
  file_size: number
  create_time: string
  update_time: string
}

export interface KnowledgeTaskResponse {
  id: string
  knowledge_id: string
  knowledge_file_id: string
  task_type: string
  status: string
  current_stage: string
  retry_count: number
  error_message?: string | null
  payload?: Record<string, any>
  result_summary?: Record<string, any>
  started_at?: string | null
  finished_at?: string | null
  create_time: string
  update_time: string
}

export interface KnowledgeTaskEventResponse {
  id: string
  task_id: string
  stage: string
  status: string
  message: string
  detail?: Record<string, any>
  create_time: string
}

export interface KnowledgeTaskDetailResponse {
  task: KnowledgeTaskResponse | null
  events: KnowledgeTaskEventResponse[]
}

export interface KnowledgeFileCreateRequest {
  knowledge_id: string
  file_url: string
}

export interface KnowledgeFileDeleteRequest {
  knowledge_file_id: string
}

export interface KnowledgeTaskRetryRequest {
  task_id: string
}

export interface KnowledgeBulkReindexRequest {
  knowledge_id: string
}

export interface KnowledgeBulkReindexResponse {
  knowledge_id: string
  total_files: number
  queued_files: number
  failed_files: number
  tasks: Array<{
    task_id: string
    knowledge_file_id: string
    dispatch_mode: string
    previous_task_id?: string | null
  }>
  failures?: Array<{
    knowledge_file_id: string
    file_name: string
    error: string
  }>
}

export function createKnowledgeFileAPI(data: KnowledgeFileCreateRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge_file/create',
    method: 'POST',
    data,
    timeout: 60000,
  })
}

export function getKnowledgeFileListAPI(knowledge_id: string) {
  return request<UnifiedResponse<KnowledgeFileResponse[]>>({
    url: '/api/v1/knowledge_file/select',
    method: 'GET',
    params: { knowledge_id },
  })
}

export function deleteKnowledgeFileAPI(data: KnowledgeFileDeleteRequest) {
  return request<UnifiedResponse<null>>({
    url: '/api/v1/knowledge_file/delete',
    method: 'DELETE',
    data: {
      knowledge_file_id: data.knowledge_file_id,
    },
  })
}

export function getKnowledgeTaskDetailAPI(task_id: string) {
  return request<UnifiedResponse<KnowledgeTaskDetailResponse>>({
    url: '/api/v1/knowledge_file/task',
    method: 'GET',
    params: { task_id },
  })
}

export function getKnowledgeTaskListAPI(knowledge_id: string) {
  return request<UnifiedResponse<KnowledgeTaskResponse[]>>({
    url: '/api/v1/knowledge_file/tasks',
    method: 'GET',
    params: { knowledge_id },
  })
}

export function retryKnowledgeTaskAPI(data: KnowledgeTaskRetryRequest) {
  return request<UnifiedResponse<Record<string, any>>>({
    url: '/api/v1/knowledge_file/task/retry',
    method: 'POST',
    data,
  })
}

export function reindexKnowledgeFilesAPI(data: KnowledgeBulkReindexRequest) {
  return request<UnifiedResponse<KnowledgeBulkReindexResponse>>({
    url: '/api/v1/knowledge_file/reindex',
    method: 'POST',
    data,
    timeout: 60000,
  })
}

export function formatFileSize(bytes: number): string {
  if (!bytes) return '0 B'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1)
  const value = bytes / Math.pow(1024, index)
  return `${value.toFixed(value >= 10 || index === 0 ? 0 : 2)} ${units[index]}`
}

export function getFileExtension(filename: string): string {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2)
}

export function getFileType(filename: string): string {
  const ext = getFileExtension(filename).toLowerCase()

  const fileTypes: Record<string, string> = {
    pdf: 'PDF',
    doc: 'Word',
    docx: 'Word',
    txt: '文本',
    md: 'Markdown',
    xls: 'Excel',
    xlsx: 'Excel',
    ppt: 'PowerPoint',
    pptx: 'PowerPoint',
    jpg: '图片',
    jpeg: '图片',
    png: '图片',
    gif: '图片',
    bmp: '图片',
    webp: '图片',
  }

  return fileTypes[ext] || '未知类型'
}
