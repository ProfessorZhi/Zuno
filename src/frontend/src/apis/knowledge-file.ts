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
  user_id: string
  oss_url: string
  file_size: number
  create_time: string
  update_time: string
}

export interface KnowledgeFileCreateRequest {
  knowledge_id: string
  file_url: string
}

export interface KnowledgeFileDeleteRequest {
  knowledge_file_id: string
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
