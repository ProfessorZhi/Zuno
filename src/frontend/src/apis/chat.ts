import { fetchEventSource } from '@microsoft/fetch-event-source'
import { apiUrl } from '../utils/api'
import type { KnowledgeRetrievalResponse, UnifiedResponse } from './knowledge'

export interface Chat {
  dialogId: string
  userInput: string
  fileUrl?: string
}

export interface UploadResponse {
  code: number
  message: string
  data: string
}

export function sendMessage(data: Chat, onmessage: any, onclose: any) {
  const ctrl = new AbortController()

  fetchEventSource(apiUrl('/api/v1/completion'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
    },
    body: JSON.stringify(
      data.fileUrl
        ? {
            dialog_id: data.dialogId,
            user_input: data.userInput,
            file_url: data.fileUrl,
          }
        : {
            dialog_id: data.dialogId,
            user_input: data.userInput,
          }
    ),
    signal: ctrl.signal,
    openWhenHidden: true,
    async onopen(response: any) {
      if (response.status !== 200) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
    },
    onmessage(msg: any) {
      try {
        onmessage(msg)
      } catch (error) {
        console.error('Failed to handle message chunk:', error)
      }
    },
    onclose() {
      onclose()
    },
    onerror(err: any) {
      console.error('Chat stream error:', err)
      ctrl.abort()
      throw err
    },
  })

  return ctrl
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

export async function retrieveKnowledge(query: string, knowledgeIds: string | string[]) {
  const response = await fetch(apiUrl('/api/v1/knowledge/retrieval'), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
    },
    body: JSON.stringify({
      query,
      knowledge_id: knowledgeIds,
    }),
  })

  if (!response.ok) {
    throw new Error(`Knowledge retrieval failed: ${response.statusText}`)
  }

  return await response.json() as UnifiedResponse<KnowledgeRetrievalResponse>
}
