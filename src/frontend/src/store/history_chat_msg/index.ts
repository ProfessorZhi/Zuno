import { defineStore } from 'pinia';
import { ref } from 'vue'
import { ChatMessage } from '../../type';
import { getHistoryMsgAPI } from '../../apis/history';
import { ElMessage } from 'element-plus';
import { zunoAgentAvatar } from '../../utils/brand'

// 定义事件数据接口
interface EventData {
  data?: {
    title?: string;
    message?: string;
    status?: string;
  };
  type?: string;
  timestamp?: number;
}

const buildEventInfo = (events: EventData[] = []) => {
  const eventMap = new Map<string, EventData>()

  events.forEach((event) => {
    if (event.type === 'heartbeat') return

    const eventTitle = event.data?.title || event.type || '事件'
    const currentStatus = event.data?.status || 'END'

    if (
      !eventMap.has(eventTitle) ||
      currentStatus === 'END' ||
      currentStatus === 'ERROR'
    ) {
      eventMap.set(eventTitle, event)
    }
  })

  return Array.from(eventMap.values()).map((event) => ({
    event_type: event.data?.title || event.type || '事件',
    message: event.data?.message || JSON.stringify(event.data),
    status: event.data?.status || 'END',
    show: false
  }))
}

const looksLikeSystemPrompt = (content: string) => {
  if (!content) return false
  const normalized = content
    .replace(/\s+/g, '')
    .replace(/\\n/g, '')
    .replace(/\\r/g, '')
    .toLowerCase()
  const hasCore =
    normalized.includes('你是一个专业的ai智能助手') ||
    normalized.includes('请遵循以下准则为用户提供优质服务')
  const hasHistory = normalized.includes('对话历史') || normalized.includes('<chat_history>')
  const hasTools =
    normalized.includes('web_search') ||
    normalized.includes('read_webpage') ||
    normalized.includes('tool_code')
  return (hasCore && (hasHistory || hasTools)) || normalized.includes('<chat_history>')
}

const stripSystemPromptWrapper = (content: string) => {
  if (!looksLikeSystemPrompt(content)) return content
  const cleaned = content.replace(/\r/g, '')
  const tokens = ['用户输入：', '用户输入:', 'user input:', 'user input：']
  const lowered = cleaned.toLowerCase()
  for (const token of tokens) {
    if (cleaned.includes(token)) {
      return cleaned.split(token).pop()?.trim() || ''
    }
    if (lowered.includes(token)) {
      const idx = lowered.lastIndexOf(token)
      return cleaned.slice(idx + token.length).trim()
    }
  }
  return ''
}

export const useHistoryChatStore = defineStore('history_chat_msg', () => {
  const chatArr = ref<ChatMessage[]>([])
  const dialogId = ref('')
  const name = ref('')
  const logo = ref('')
  const loading = ref(false)
  const error = ref('')

  /**
   * 获取历史聊天记录
   * @param id 对话ID
   */
  async function HistoryChat(id: string) {
    console.log('【HistoryChat】开始获取历史消息，dialog_id:', id)
    chatArr.value = [] // 清空现有消息
    loading.value = true
    error.value = ''
    
    try {
      const response = await getHistoryMsgAPI(id)
      console.log('【HistoryChat】历史消息API返回:', response.data)
      
      if (response.data.status_code === 200 && Array.isArray(response.data.data)) {
        const messages = response.data.data
        const visibleMessages = messages
          .filter((message: any) => message.role === 'user' || message.role === 'assistant')
          .map((message: any) => {
            if (message.role !== 'user') return message
            const content = String(message.content || '')
            if (!looksLikeSystemPrompt(content)) return message
            return { ...message, content: stripSystemPromptWrapper(content) }
          })
          .filter((message: any) => {
            const content = String(message.content || '').trim()
            return content && !looksLikeSystemPrompt(content)
          })
        
        // 设置会话信息
        const dialogMeta = messages.find((message: any) => message.dialog_name)
        if (dialogMeta) {
          name.value = dialogMeta.dialog_name || '新对话'
          logo.value = dialogMeta.logo_url || zunoAgentAvatar
        }
        
        let currentChat: ChatMessage | null = null

        visibleMessages.forEach((message: any) => {
          if (message.role === 'user') {
            if (currentChat) {
              chatArr.value.push(currentChat)
            }

            currentChat = {
              personMessage: { content: message.content || '' },
              aiMessage: { content: '' },
              eventInfo: []
            }
            return
          }

          if (message.role === 'assistant') {
            const eventInfo = Array.isArray(message.events) ? buildEventInfo(message.events) : []
            const content = String(message.content || '').trim()

            if (!currentChat) {
              currentChat = {
                personMessage: { content: '' },
                aiMessage: { content },
                eventInfo
              }
              chatArr.value.push(currentChat)
              currentChat = null
              return
            }

            currentChat.aiMessage.content = content
            currentChat.eventInfo = eventInfo
            chatArr.value.push(currentChat)
            currentChat = null
          }
        })

        if (currentChat) {
          chatArr.value.push(currentChat)
        }
        
        console.log('【HistoryChat】处理后的消息数组:', chatArr.value)
      } else {
        console.error('【HistoryChat】API返回错误:', response.data)
        error.value = '获取历史消息失败'
        ElMessage.error('获取历史消息失败')
      }
    } catch (err) {
      console.error('【HistoryChat】获取历史消息出错:', err)
      error.value = '获取历史消息出错'
      ElMessage.error('获取历史消息出错，请重试')
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 清空聊天记录
   */
  function clear() {
    chatArr.value = []
    error.value = ''
  }
  
  return { 
    chatArr, 
    HistoryChat,
    clear,
    dialogId,
    name,
    logo,
    loading,
    error
  }
},
{
  persist: {
    paths: ['dialogId', 'name', 'logo']
  }
})


