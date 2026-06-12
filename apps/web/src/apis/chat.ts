import { apiUrl } from '../utils/api'
import type { UnifiedResponse } from './knowledge'

export interface UploadResponse {
  code: number
  message: string
  data: string
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(apiUrl('/api/v1/upload'), {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
    },
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`)
  }

  return await response.json()
}
