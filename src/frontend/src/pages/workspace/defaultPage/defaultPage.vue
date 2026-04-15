<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowUp, Plus } from '@element-plus/icons-vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import {
  getWorkspaceExecutionModesAPI,
  getWorkspacePluginsByModeAPI,
  getWorkspaceSessionsAPI,
  workspaceSimpleChatStreamAPI,
  type AccessScopeDefinition,
  type ExecutionModeDefinition,
  type WorkspaceAttachment,
  type WorkspaceExecutionConfig,
  type WorkspaceStreamEvent,
  type WorkSpaceSimpleTask,
} from '../../../apis/workspace'
import { uploadFile } from '../../../apis/chat'
import { getVisibleLLMsAPI, type LLMResponse } from '../../../apis/llm'
import { getAgentSkillsAPI, type AgentSkill } from '../../../apis/agent-skill'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../../apis/knowledge'
import { useUserStore } from '../../../store/user'
import { sanitizeWorkspaceContexts } from '../../../utils/workspace-history'
import robotIcon from '../../../assets/robot.svg'
import { isDesktopRuntime } from '../../../utils/api'

const ALWAYS_WEB_SEARCH = true
const MAX_ATTACHMENTS = 5
const MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
const CHAT_IMAGE_EXTENSIONS = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])
const AGENT_DOCUMENT_EXTENSIONS = new Set(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'csv', 'xls', 'xlsx'])
type WorkspaceMode = 'normal' | 'agent'

interface ChatMessage { role: 'user' | 'assistant'; content: string }
interface TraceRecord { id: string; title: string; detail: string; at: string }
interface PendingAttachment extends WorkspaceAttachment { id: string; preview_url?: string }
interface ProgressStep { key: string; label: string; done: boolean; active: boolean }

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const modes = [
  { id: 'normal' as const, label: '聊天模式', description: '适合轻量对话、图片理解与快速问答。' },
  { id: 'agent' as const, label: 'Agent 模式', description: '可调用工具、分析附件，并执行更完整的任务流程。' },
]

const selectedMode = ref<WorkspaceMode>('normal')
const inputMessage = ref('')
const messages = ref<ChatMessage[]>([])
const executionEvents = ref<TraceRecord[]>([])
const executionModes = ref<ExecutionModeDefinition[]>([])
const accessScopes = ref<AccessScopeDefinition[]>([])
const selectedExecutionMode = ref('tool')
const selectedAccessScope = ref('workspace')
const plugins = ref<any[]>([])
const selectedTools = ref<string[]>([])
const mcpServers = ref<any[]>([])
const selectedMcpServers = ref<string[]>([])
const skillOptions = ref<AgentSkill[]>([])
const selectedSkillIds = ref<string[]>([])
const knowledgeOptions = ref<KnowledgeResponse[]>([])
const selectedKnowledgeIds = ref<string[]>([])
const toolsTouched = ref(false)
const mcpTouched = ref(false)
const skillsTouched = ref(false)
const knowledgeTouched = ref(false)
const modelOptions = ref<LLMResponse[]>([])
const selectedModelId = ref('')
const isGenerating = ref(false)
const modelsLoading = ref(false)
const currentSessionId = ref('')
const conversationRef = ref<HTMLElement | null>(null)
const showControlPanel = ref(false)
const showTracePanel = ref(false)
const isPinnedToBottom = ref(true)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const pendingAttachments = ref<PendingAttachment[]>([])
const attachmentsUploading = ref(false)
const isAttachmentDragOver = ref(false)
const activeSuggestionIndex = ref(0)

type SlashSuggestion = {
  key: string
  label: string
  detail: string
  insertValue: string
}

const activeMode = computed(() => modes.find((mode) => mode.id === selectedMode.value) || modes[0])
const activeExecutionMode = computed(() => executionModes.value.find((mode) => mode.id === selectedExecutionMode.value) || null)
const activeAccessScope = computed(() => accessScopes.value.find((scope) => scope.id === selectedAccessScope.value) || null)
const isAgentMode = computed(() => selectedMode.value === 'agent')
const attachmentAccept = computed(() => isAgentMode.value ? '.jpg,.jpeg,.png,.gif,.webp,.bmp,.pdf,.doc,.docx,.ppt,.pptx,.txt,.md,.csv,.xls,.xlsx' : 'image/*')
const attachmentHint = computed(() => {
  if (!isAgentMode.value) return '聊天模式仅支持图片，文档请切换到 Agent 模式。'
  if (selectedExecutionMode.value === 'terminal') {
    return '终端模式支持图片、PDF、Word、PPT、TXT、Markdown 和 Excel，可结合本地文件与命令执行。'
  }
  return 'Agent 模式支持图片、PDF、Word、PPT、TXT、Markdown 和 Excel。'
})
const composerPlaceholder = computed(() => {
  if (!isAgentMode.value) return '输入你的问题，直接开始对话。'
  if (selectedExecutionMode.value === 'terminal') return '输入终端任务，或用 /terminal 明确要求访问本地文件与命令行。'
  return '输入你的任务，或用 /mcp、/skill、/kb 明确指定能力。'
})
const modeFooterCopy = computed(() => {
  if (!isAgentMode.value) return '聊天模式 / 支持图片输入'
  const base = `${activeExecutionMode.value?.label || '工具模式'} / ${activeAccessScope.value?.label || '工作区限制'}`
  if (selectedExecutionMode.value === 'terminal') return `${base} · 支持 /terminal`
  return `${base} · 支持 /mcp /skill /kb`
})
const canPickTools = computed(() => isAgentMode.value && selectedExecutionMode.value === 'tool')
const selectedToolCount = computed(() => (
  selectedTools.value.length
  + selectedMcpServers.value.length
  + selectedSkillIds.value.length
  + selectedKnowledgeIds.value.length
))
const compactPanel = computed(() => messages.value.length > 0)
const traceVisible = computed(() => isAgentMode.value && showTracePanel.value)
const slashSuggestions = computed<SlashSuggestion[]>(() => {
  if (!isAgentMode.value || selectedExecutionMode.value === 'terminal') return []
  const text = inputMessage.value || ''
  if (!text.startsWith('/')) return []
  const trimmed = text.trimStart()
  if (!trimmed.startsWith('/')) return []

  const commandMatch = trimmed.match(/^\/([^\s]*)\s*(.*)$/)
  const rawCommand = (commandMatch?.[1] || '').trim().toLowerCase()
  const rawRest = (commandMatch?.[2] || '').trim()

  const commandSuggestions: SlashSuggestion[] = [
    { key: 'mcp', label: '/mcp', detail: '显式指定某个 MCP 能力', insertValue: '/mcp ' },
    { key: 'skill', label: '/skill', detail: '显式调用某个 Skill', insertValue: '/skill ' },
    { key: 'kb', label: '/kb', detail: '优先按知识库检索', insertValue: '/kb ' },
  ]

  if (!rawCommand) return commandSuggestions

  if ('skill'.startsWith(rawCommand) && rawRest.length === 0 && rawCommand !== 'skill') {
    return commandSuggestions.filter((item) => item.label.includes(rawCommand))
  }

  if (rawCommand === 'skill') {
    const keyword = rawRest.toLowerCase()
    return skillOptions.value
      .filter((skill) => {
        const name = (skill.name || '').toLowerCase()
        const desc = (skill.description || '').toLowerCase()
        return !keyword || name.includes(keyword) || desc.includes(keyword)
      })
      .slice(0, 8)
      .map((skill) => ({
        key: `skill-${skill.id}`,
        label: skill.name,
        detail: skill.description || 'Skill',
        insertValue: `/skill ${skill.name} `,
      }))
  }

  return commandSuggestions.filter((item) => item.label.includes(rawCommand))
})
const progressStageIndex = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return -1
  if (!isGenerating.value && executionEvents.value.length > 0) return 2
  if (executionEvents.value.length > 1) return 1
  return 0
})
const progressSteps = computed<ProgressStep[]>(() => {
  const activeIndex = progressStageIndex.value
  return [
    { key: 'thinking', label: '理解任务', done: activeIndex > 0 || (!isGenerating.value && executionEvents.value.length > 0), active: activeIndex === 0 },
    { key: 'tool', label: '调用能力', done: activeIndex > 1, active: activeIndex === 1 },
    { key: 'answer', label: '生成回复', done: !isGenerating.value && executionEvents.value.length > 0, active: activeIndex === 2 },
  ]
})
const progressHeadline = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return executionEvents.value[executionEvents.value.length - 1]?.title || '正在处理中'
})
const progressDetail = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return executionEvents.value[executionEvents.value.length - 1]?.detail || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value}`
})
const liveProgressEvents = computed(() => executionEvents.value.slice(-3))

const generateSessionId = () => crypto.randomUUID().replace(/-/g, '')
const safeQueryValue = (value: unknown, fallback: string) => Array.isArray(value) ? String(value[0] || fallback) : (typeof value === 'string' && value.trim() ? value : fallback)
const getFileExtension = (fileName: string) => fileName.split('.').pop()?.toLowerCase() || ''

const sanitizeAssistantChunk = (chunk: string) => isAgentMode.value ? chunk : chunk.replace(/ReAct\s*Agent[^\n]*\n?/gi, '').replace(/ReAct\s*鎺ㄧ悊[^\n]*\n?/gi, '').replace(/鎬濊€冭繃绋媅^\n]*\n?/gi, '').replace(/^\s+/, '')
const handleAvatarError = (event: Event) => { const target = event.target as HTMLImageElement; if (target) target.src = '/src/assets/user.svg' }
const scrollToBottom = async (force = false) => { await nextTick(); if (conversationRef.value && (force || isPinnedToBottom.value)) conversationRef.value.scrollTop = conversationRef.value.scrollHeight }
const handleConversationScroll = () => { const panel = conversationRef.value; if (!panel) return; isPinnedToBottom.value = panel.scrollHeight - (panel.scrollTop + panel.clientHeight) < 24 }
const emitSessionUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-updated', { detail: { sessionId: currentSessionId.value } }))

const syncRouteState = async () => {
  if (!currentSessionId.value) return
  await router.replace({ name: 'workspaceDefaultPage', query: { session_id: currentSessionId.value, mode: selectedMode.value, execution_mode: selectedExecutionMode.value, access_scope: selectedAccessScope.value } })
}
const buildTraceRecord = (event: WorkspaceStreamEvent): TraceRecord => {
  const data = event.data || {}
  if (event.type === 'tool_call') return { id: event.id || crypto.randomUUID(), title: '正在调用工具', detail: String(data.tool_name || data.message || '正在执行外部能力'), at: new Date().toLocaleTimeString() }
  if (event.type === 'tool_result') return { id: event.id || crypto.randomUUID(), title: '工具已返回结果', detail: String(data.tool_name || data.message || '已收到工具结果'), at: new Date().toLocaleTimeString() }
  if (event.type === 'final') return { id: event.id || crypto.randomUUID(), title: '正在整理最终回复', detail: '正在生成最终答案。', at: new Date().toLocaleTimeString() }
  return { id: event.id || crypto.randomUUID(), title: String(data.message || event.title || '正在处理中'), detail: String(data.result || data.error || data.tool_name || event.detail || ''), at: new Date().toLocaleTimeString() }
}
const pushTraceEvent = (event: WorkspaceStreamEvent) => {
  const nextRecord = buildTraceRecord(event)
  const lastRecord = executionEvents.value[executionEvents.value.length - 1]
  if (lastRecord && lastRecord.title === nextRecord.title && lastRecord.detail === nextRecord.detail) return
  executionEvents.value.push(nextRecord)
  if (executionEvents.value.length > 24) executionEvents.value.splice(0, executionEvents.value.length - 24)
}

const buildLiveAssistantProgress = () => {
  const summary = [
    `**${progressHeadline.value || '正在处理中'}**`,
    progressDetail.value || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value}`,
    '',
    ...progressSteps.value.map((step) => `- ${step.done ? 'x' : step.active ? '>' : '-'} ${step.label}`),
  ]
  if (liveProgressEvents.value.length > 0) {
    summary.push('', '最近进展')
    liveProgressEvents.value.forEach((event) => {
      summary.push(`- ${event.title}${event.detail ? `: ${event.detail}` : ''}`)
    })
  }
  return summary.join('\n')
}

const buildFallbackAssistantMessage = () => [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.detail || [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.title || '这次请求没有返回可见内容，请稍后重试。'
const applySlashSuggestion = (suggestion: SlashSuggestion) => {
  inputMessage.value = suggestion.insertValue
  activeSuggestionIndex.value = 0
}

const fetchModels = async () => {
  modelsLoading.value = true
  try {
    const response = await getVisibleLLMsAPI()
    if (response.data?.status_code !== 200) return
    const grouped = response.data.data || {}
    const list: LLMResponse[] = []
    Object.values(grouped).forEach((items: any) => Array.isArray(items) && list.push(...items))
    modelOptions.value = list.filter((item) => (item.llm_type || '').toUpperCase() === 'LLM')
    if (!selectedModelId.value && modelOptions.value.length > 0) selectedModelId.value = modelOptions.value[0].llm_id
  } catch (error) { console.error('获取模型失败', error) } finally { modelsLoading.value = false }
}

const fetchExecutionConfig = async () => {
  try {
    const response = await getWorkspaceExecutionModesAPI()
    if (response.data.status_code !== 200) return
    const config = (response.data.data || {}) as WorkspaceExecutionConfig
    executionModes.value = config.execution_modes || []
    accessScopes.value = config.access_scopes || []
  } catch (error) { console.error('获取执行配置失败', error) }
}

const fetchPlugins = async () => {
  if (!canPickTools.value) { plugins.value = []; selectedTools.value = []; return }
  try {
    const response = await getWorkspacePluginsByModeAPI(selectedExecutionMode.value, selectedAccessScope.value)
    if (response.data.status_code !== 200) return
    plugins.value = response.data.data || []
    syncDefaultSelections()
  } catch (error) { console.error('获取工具失败', error) }
}

const fetchMcpServers = async () => {
  try {
    const { getMCPServersAPI } = await import('../../../apis/mcp-server')
    const response = await getMCPServersAPI()
    if (response.data?.status_code === 200 && Array.isArray(response.data.data)) {
      mcpServers.value = response.data.data
      syncDefaultSelections()
    }
  } catch (error) { console.error('获取 MCP 失败', error) }
}

const fetchSkills = async () => {
  if (!canPickTools.value) { skillOptions.value = []; selectedSkillIds.value = []; return }
  try {
    const response = await getAgentSkillsAPI()
    if (response.data?.status_code !== 200 || !Array.isArray(response.data.data)) return
    skillOptions.value = response.data.data
    syncDefaultSelections()
  } catch (error) { console.error('获取 Skill 失败', error) }
}

const fetchKnowledges = async () => {
  if (!canPickTools.value) { knowledgeOptions.value = []; selectedKnowledgeIds.value = []; return }
  try {
    const response = await getKnowledgeListAPI()
    if (response.data?.status_code !== 200 || !Array.isArray(response.data.data)) return
    knowledgeOptions.value = response.data.data
    syncDefaultSelections()
  } catch (error) { console.error('获取知识库失败', error) }
}

const loadSessionHistory = async (sessionId: string) => {
  try {
    const response = await getWorkspaceSessionsAPI()
    if (response.data.status_code !== 200) return
    const session = response.data.data.find((item: any) => item.session_id === sessionId)
    if (!session?.contexts || !Array.isArray(session.contexts)) return
    const contexts = sanitizeWorkspaceContexts(session.contexts)
    messages.value = contexts.map((context: any) => [{ role: 'user' as const, content: context.query || '' }, { role: 'assistant' as const, content: context.answer || '' }]).flat().filter((message: ChatMessage) => message.content)
    executionEvents.value = []
    await scrollToBottom(true)
  } catch (error) { console.error('加载会话历史失败', error); ElMessage.error('加载会话历史失败') }
}

const syncDefaultSelections = () => {
  if (!isAgentMode.value || !canPickTools.value) return

  const availableToolIds = plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean)
  const availableMcpIds = mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean)
  const availableSkillIds = skillOptions.value.map((item) => item.id).filter(Boolean)
  const availableKnowledgeIds = knowledgeOptions.value.map((item) => item.id).filter(Boolean)

  if (!toolsTouched.value) {
    selectedTools.value = [...availableToolIds]
  } else {
    selectedTools.value = selectedTools.value.filter((toolId) => availableToolIds.includes(toolId))
  }

  if (!mcpTouched.value) {
    selectedMcpServers.value = [...availableMcpIds]
  } else {
    selectedMcpServers.value = selectedMcpServers.value.filter((serverId) => availableMcpIds.includes(serverId))
  }

  if (!skillsTouched.value) {
    selectedSkillIds.value = []
  } else {
    selectedSkillIds.value = selectedSkillIds.value.filter((skillId) => availableSkillIds.includes(skillId))
  }

  if (!knowledgeTouched.value) {
    selectedKnowledgeIds.value = []
  } else {
    selectedKnowledgeIds.value = selectedKnowledgeIds.value.filter((knowledgeId) => availableKnowledgeIds.includes(knowledgeId))
  }
}

const toggleTool = (toolId: string) => {
  toolsTouched.value = true
  const index = selectedTools.value.indexOf(toolId)
  index >= 0 ? selectedTools.value.splice(index, 1) : selectedTools.value.push(toolId)
}

const toggleMcp = (serverId: string) => {
  mcpTouched.value = true
  const index = selectedMcpServers.value.indexOf(serverId)
  index >= 0 ? selectedMcpServers.value.splice(index, 1) : selectedMcpServers.value.push(serverId)
}

const toggleSkill = (skillId: string) => {
  skillsTouched.value = true
  const index = selectedSkillIds.value.indexOf(skillId)
  index >= 0 ? selectedSkillIds.value.splice(index, 1) : selectedSkillIds.value.push(skillId)
}

const toggleKnowledge = (knowledgeId: string) => {
  knowledgeTouched.value = true
  const index = selectedKnowledgeIds.value.indexOf(knowledgeId)
  index >= 0 ? selectedKnowledgeIds.value.splice(index, 1) : selectedKnowledgeIds.value.push(knowledgeId)
}

const getValidSelectedToolIds = () => {
  const availableToolIds = new Set(plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean))
  return selectedTools.value.filter((toolId) => availableToolIds.has(toolId))
}

const getValidSelectedMcpIds = () => {
  const availableMcpIds = new Set(mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean))
  return selectedMcpServers.value.filter((serverId) => availableMcpIds.has(serverId))
}

const getValidSelectedSkillIds = () => {
  const availableSkillIds = new Set(skillOptions.value.map((item) => item.id).filter(Boolean))
  return selectedSkillIds.value.filter((skillId) => availableSkillIds.has(skillId))
}

const getValidSelectedKnowledgeIds = () => {
  const availableKnowledgeIds = new Set(knowledgeOptions.value.map((item) => item.id).filter(Boolean))
  return selectedKnowledgeIds.value.filter((knowledgeId) => availableKnowledgeIds.has(knowledgeId))
}

const classifySelectedFile = (file: File) => {
  const extension = getFileExtension(file.name)
  if (file.type.startsWith('image/') || CHAT_IMAGE_EXTENSIONS.has(extension)) return 'image'
  if (AGENT_DOCUMENT_EXTENSIONS.has(extension)) return 'document'
  return 'unsupported'
}

const validateSelectedFile = (file: File) => {
  if (file.size > MAX_ATTACHMENT_SIZE) return `文件 ${file.name} 超过 20MB，无法上传。`
  const kind = classifySelectedFile(file)
  if (kind === 'unsupported') return `文件 ${file.name} 暂不支持。支持类型：图片、PDF、Word、PPT、TXT、Markdown、Excel。`
  if (!isAgentMode.value && kind !== 'image') return `聊天模式仅支持图片，请切换到 Agent 模式后再分析 ${file.name}。`
  return ''
}

const resetAttachmentInput = () => { if (attachmentInputRef.value) attachmentInputRef.value.value = '' }
const triggerAttachmentSelect = () => { if (!attachmentsUploading.value && !isGenerating.value) attachmentInputRef.value?.click() }
const revokeAttachmentPreview = (attachment: PendingAttachment) => {
  if (attachment.preview_url && attachment.preview_url.startsWith('blob:')) {
    URL.revokeObjectURL(attachment.preview_url)
  }
}

const removeAttachment = (attachmentId: string) => {
  const target = pendingAttachments.value.find((item) => item.id === attachmentId)
  if (target) revokeAttachmentPreview(target)
  pendingAttachments.value = pendingAttachments.value.filter((item) => item.id !== attachmentId)
}
const isImageAttachment = (attachment: PendingAttachment) => attachment.mime_type?.startsWith('image/')
const formatAttachmentSize = (size = 0) => {
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const normalizeClipboardFile = (file: File, index: number) => {
  if (file.name && file.name.trim()) return file
  const extension = file.type.split('/')[1] || 'png'
  return new File([file], `clipboard-image-${Date.now()}-${index}.${extension}`, { type: file.type || 'image/png' })
}

const uploadAttachments = async (rawFiles: File[]) => {
  const files = rawFiles.map((file, index) => normalizeClipboardFile(file, index))
  if (files.length === 0) return
  if (pendingAttachments.value.length + files.length > MAX_ATTACHMENTS) { ElMessage.warning(`最多只能添加 ${MAX_ATTACHMENTS} 个附件。`); resetAttachmentInput(); return }
  for (const file of files) { const err = validateSelectedFile(file); if (err) { ElMessage.warning(err); resetAttachmentInput(); return } }
  attachmentsUploading.value = true
  try {
    for (const file of files) {
      const localPreviewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : ''
      const response = await uploadFile(file)
      pendingAttachments.value.push({
        id: crypto.randomUUID(),
        name: file.name,
        url: response.data,
        preview_url: localPreviewUrl || response.data,
        mime_type: file.type,
        size: file.size,
      })
    }
    ElMessage.success(files.length === 1 ? '附件已添加。' : `已添加 ${files.length} 个附件。`)
  } catch (error) { console.error('附件上传失败', error); ElMessage.error('附件上传失败，请稍后重试') } finally { attachmentsUploading.value = false; resetAttachmentInput() }
}

const handleComposerPaste = async (event: ClipboardEvent) => {
  const files = Array.from(event.clipboardData?.items || [])
    .filter((item) => item.kind === 'file')
    .map((item) => item.getAsFile())
    .filter((file): file is File => !!file)
  if (files.length === 0) return
  event.preventDefault()
  if (attachmentsUploading.value || isGenerating.value) { ElMessage.warning('请等待当前任务结束后再粘贴附件。'); return }
  await uploadAttachments(files)
}

const handleAttachmentChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (files.length === 0) return
  await uploadAttachments(files)
}

const handleAttachmentDragOver = (event: DragEvent) => {
  if (!event.dataTransfer?.types?.includes('Files')) return
  event.preventDefault()
  if (!attachmentsUploading.value && !isGenerating.value) isAttachmentDragOver.value = true
}

const handleAttachmentDragLeave = (event: DragEvent) => {
  const currentTarget = event.currentTarget as HTMLElement | null
  const nextTarget = event.relatedTarget as Node | null
  if (currentTarget && nextTarget && currentTarget.contains(nextTarget)) return
  isAttachmentDragOver.value = false
}

const handleAttachmentDrop = async (event: DragEvent) => {
  if (!event.dataTransfer?.files?.length) return
  event.preventDefault()
  isAttachmentDragOver.value = false
  if (attachmentsUploading.value || isGenerating.value) return
  await uploadAttachments(Array.from(event.dataTransfer.files))
}

const buildPayload = (query: string): WorkSpaceSimpleTask => ({
  query,
  model_id: selectedModelId.value,
  workspace_mode: selectedMode.value,
  web_search: ALWAYS_WEB_SEARCH,
  plugins: canPickTools.value ? getValidSelectedToolIds() : [],
  mcp_servers: canPickTools.value ? getValidSelectedMcpIds() : [],
  knowledge_ids: canPickTools.value ? getValidSelectedKnowledgeIds() : [],
  agent_skill_ids: canPickTools.value ? getValidSelectedSkillIds() : [],
  session_id: currentSessionId.value,
  execution_mode: isAgentMode.value ? selectedExecutionMode.value : 'tool',
  access_scope: isAgentMode.value ? selectedAccessScope.value : 'workspace',
  desktop_bridge_url: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeUrl || '' : '',
  desktop_bridge_token: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeToken || '' : '',
  attachments: pendingAttachments.value.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment),
})

const submitMessage = async () => {
  const query = inputMessage.value.trim() || (pendingAttachments.value.length > 0 ? '请分析我上传的附件。' : '')
  if (!query) return ElMessage.warning('请输入内容。')
  if (isGenerating.value) return ElMessage.warning('请等待当前回复完成。')
  if (!selectedModelId.value) return ElMessage.warning('请先选择模型')
  if (!currentSessionId.value) currentSessionId.value = generateSessionId()
  await syncRouteState()
  inputMessage.value = ''
  isGenerating.value = true
  executionEvents.value = []
  showControlPanel.value = false
  showTracePanel.value = false
  const attachmentsForRequest = [...pendingAttachments.value]
  pendingAttachments.value = []
  const attachmentSummary = attachmentsForRequest.length ? `\n\n已附加 ${attachmentsForRequest.length} 个文件：${attachmentsForRequest.map((item) => item.name).join('，')}` : ''
  messages.value.push({ role: 'user', content: `${query}${attachmentSummary}`.trim() })
  const assistantIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: isAgentMode.value ? buildLiveAssistantProgress() : '' })
  isPinnedToBottom.value = true
  await scrollToBottom(true)
  if (isAgentMode.value) executionEvents.value.push({ id: crypto.randomUUID(), title: '开始执行', detail: `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value}`, at: new Date().toLocaleTimeString() })
  let assistantHasRealContent = false
  const renderAgentProgress = async () => {
    if (!isAgentMode.value || assistantHasRealContent || !messages.value[assistantIndex]) return
    messages.value[assistantIndex].content = buildLiveAssistantProgress()
    await scrollToBottom()
  }
  const applyFallback = () => {
    if (messages.value[assistantIndex] && !assistantHasRealContent) messages.value[assistantIndex].content = buildFallbackAssistantMessage()
  }
  try {
    const payload = buildPayload(query)
    payload.attachments = attachmentsForRequest.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment)
    await workspaceSimpleChatStreamAPI(payload, {
      onMessage: async (chunk) => {
        const safeChunk = sanitizeAssistantChunk(chunk)
        if (!safeChunk) return
        if (!assistantHasRealContent) {
          messages.value[assistantIndex].content = ''
          assistantHasRealContent = true
        }
        messages.value[assistantIndex].content += safeChunk
        await scrollToBottom()
      },
      onEvent: async (event) => {
        if (!isAgentMode.value) return
        pushTraceEvent(event)
        await renderAgentProgress()
      },
      onError: (error) => { console.error('对话失败', error); pendingAttachments.value = attachmentsForRequest; applyFallback(); ElMessage.error('对话失败，请稍后重试'); isGenerating.value = false },
      onClose: () => {
        attachmentsForRequest.forEach(revokeAttachmentPreview)
        applyFallback()
        isGenerating.value = false
        emitSessionUpdated()
      },
    })
  } catch (error) {
    console.error('对话异常', error)
    pendingAttachments.value = attachmentsForRequest
    applyFallback()
    ElMessage.error('对话异常')
    isGenerating.value = false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (slashSuggestions.value.length > 0) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      activeSuggestionIndex.value = (activeSuggestionIndex.value + 1) % slashSuggestions.value.length
      return
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      activeSuggestionIndex.value = (activeSuggestionIndex.value - 1 + slashSuggestions.value.length) % slashSuggestions.value.length
      return
    }
    if (event.key === 'Tab') {
      event.preventDefault()
      applySlashSuggestion(slashSuggestions.value[activeSuggestionIndex.value])
      return
    }
    if (event.key === 'Enter' && !event.shiftKey) {
      const trimmed = (inputMessage.value || '').trim()
      if (trimmed.startsWith('/')) {
        event.preventDefault()
        applySlashSuggestion(slashSuggestions.value[activeSuggestionIndex.value])
        return
      }
    }
  }

  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!isGenerating.value) void submitMessage()
  }
}

watch(slashSuggestions, (nextSuggestions) => {
  if (!nextSuggestions.length) {
    activeSuggestionIndex.value = 0
    return
  }
  if (activeSuggestionIndex.value >= nextSuggestions.length) activeSuggestionIndex.value = 0
})

watch(() => route.query.session_id, async (newSessionId, oldSessionId) => {
  if (newSessionId && newSessionId !== oldSessionId) {
    currentSessionId.value = String(newSessionId)
    toolsTouched.value = false
    mcpTouched.value = false
    skillsTouched.value = false
    knowledgeTouched.value = false
    selectedTools.value = []
    selectedMcpServers.value = []
    selectedSkillIds.value = []
    selectedKnowledgeIds.value = []
    await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
    syncDefaultSelections()
    await loadSessionHistory(String(newSessionId))
    showControlPanel.value = false
    return
  }
  if (!newSessionId && oldSessionId) {
    currentSessionId.value = generateSessionId()
    messages.value = []
    executionEvents.value = []
    showControlPanel.value = false
    showTracePanel.value = false
    pendingAttachments.value = []
    toolsTouched.value = false
    mcpTouched.value = false
    skillsTouched.value = false
    knowledgeTouched.value = false
    selectedTools.value = []
    selectedMcpServers.value = []
    selectedSkillIds.value = []
    selectedKnowledgeIds.value = []
    await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
    syncDefaultSelections()
  }
})

watch([selectedExecutionMode, selectedAccessScope, selectedMode], async () => {
  if (!isAgentMode.value) {
    plugins.value = []
    selectedTools.value = []
    selectedMcpServers.value = []
    skillOptions.value = []
    selectedSkillIds.value = []
    knowledgeOptions.value = []
    selectedKnowledgeIds.value = []
    toolsTouched.value = false
    mcpTouched.value = false
    skillsTouched.value = false
    knowledgeTouched.value = false
    showTracePanel.value = false
  }
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  syncDefaultSelections()
})

watch(selectedMode, async () => { if (currentSessionId.value) await syncRouteState() })

onMounted(async () => {
  await Promise.all([fetchExecutionConfig(), fetchModels(), fetchMcpServers()])
  selectedMode.value = safeQueryValue(route.query.mode, 'normal') === 'agent' ? 'agent' : 'normal'
  selectedExecutionMode.value = safeQueryValue(route.query.execution_mode, 'tool')
  selectedAccessScope.value = safeQueryValue(route.query.access_scope, 'workspace')
  selectedExecutionMode.value = executionModes.value.some((item) => item.id === selectedExecutionMode.value) ? selectedExecutionMode.value : 'tool'
  selectedAccessScope.value = accessScopes.value.some((item) => item.id === selectedAccessScope.value) ? selectedAccessScope.value : 'workspace'
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  const sessionId = safeQueryValue(route.query.session_id, '')
  if (sessionId) { currentSessionId.value = sessionId; await loadSessionHistory(sessionId) } else currentSessionId.value = generateSessionId()
})
</script>

<template>
  <div class="workspace-chat" :class="{ active: messages.length > 0 }">
    <div class="workspace-shell">
      <div v-if="messages.length === 0" class="hero-card"><img :src="robotIcon" alt="Zuno" class="hero-avatar" /><h1>{{ activeMode.label }}</h1><p>{{ activeMode.description }}</p></div>
      <div v-if="messages.length === 0" class="mode-switcher"><button v-for="mode in modes" :key="mode.id" :class="['mode-pill', { active: selectedMode === mode.id }]" @click="selectedMode = mode.id">{{ mode.label }}</button></div>
      <div v-if="messages.length > 0" ref="conversationRef" class="conversation-panel" @scroll="handleConversationScroll">
        <div v-for="(message, index) in messages" :key="index" class="message-row" :class="message.role">
          <img v-if="message.role === 'assistant'" :src="robotIcon" alt="Zuno" class="avatar" />
          <div class="message-bubble" :class="{ assistant: message.role === 'assistant', loading: message.role === 'assistant' && !message.content && isGenerating && index === messages.length - 1 }">
            <div v-if="message.role === 'assistant' && !message.content && isGenerating && index === messages.length - 1" class="loading-row" :class="{ agent: isAgentMode }">
              <template v-if="isAgentMode">
                <div class="loading-head">
                  <span class="spinner"></span>
                  <div class="loading-copy">
                    <strong>{{ progressHeadline }}</strong>
                    <span>{{ progressDetail }}</span>
                  </div>
                </div>
                <div class="loading-steps">
                  <div v-for="step in progressSteps" :key="step.key" class="loading-step" :class="{ active: step.active, done: step.done }">
                    <span class="progress-dot"></span>
                    <span>{{ step.label }}</span>
                  </div>
                </div>
                <div v-if="liveProgressEvents.length > 0" class="loading-events">
                  <div v-for="event in liveProgressEvents" :key="event.id" class="loading-event">
                    <strong>{{ event.title }}</strong>
                    <span v-if="event.detail">{{ event.detail }}</span>
                  </div>
                </div>
              </template>
              <template v-else>
                <span class="spinner"></span>
                <span>Zuno 正在回复...</span>
              </template>
            </div>
            <MdPreview v-else-if="message.content" :editorId="`workspace-message-${index}`" :modelValue="message.content" />
          </div>
          <img v-if="message.role === 'user'" :src="userStore.userInfo?.avatar || '/src/assets/user.svg'" alt="User" class="avatar" @error="handleAvatarError" />
        </div>
      </div>
      <div class="composer-dock" :class="{ fixed: messages.length > 0 }">
        <div class="composer-shell" :class="{ 'drag-active': isAttachmentDragOver }" @dragover.prevent="handleAttachmentDragOver" @dragleave="handleAttachmentDragLeave" @drop.prevent="handleAttachmentDrop">
          <div class="composer-top" :class="{ compact: compactPanel }">
            <div v-if="!compactPanel" class="mode-badge"><span class="label">当前模式</span><strong>{{ activeMode.label }}</strong></div>
            <div class="composer-actions">
              <button v-if="isAgentMode && compactPanel" class="ghost-pill subtle" type="button" @click="showTracePanel = !showTracePanel"><el-icon><ArrowDown v-if="showTracePanel" /><ArrowUp v-else /></el-icon>{{ showTracePanel ? '收起进展' : '查看进展' }}</button>
              <button class="ghost-pill subtle" type="button" @click="showControlPanel = !showControlPanel"><el-icon><ArrowDown v-if="showControlPanel" /><ArrowUp v-else /></el-icon>{{ showControlPanel ? '收起设置' : '更多设置' }}</button>
            </div>
          </div>

          <div v-if="showControlPanel" class="settings-panel">
            <div class="selector-grid">
              <label class="field"><span>模式</span><select v-model="selectedMode"><option v-for="mode in modes" :key="mode.id" :value="mode.id">{{ mode.label }}</option></select></label>
              <label class="field"><span>模型</span><select v-model="selectedModelId"><option v-if="modelsLoading" value="">加载中...</option><option v-for="model in modelOptions" :key="model.llm_id" :value="model.llm_id">{{ model.model }}</option></select></label>
            </div>
            <div v-if="isAgentMode" class="selector-grid agent-grid">
              <label class="field"><span>执行方式</span><select v-model="selectedExecutionMode"><option v-for="mode in executionModes" :key="mode.id" :value="mode.id">{{ mode.label }}</option></select></label>
              <label class="field"><span>访问范围</span><select v-model="selectedAccessScope"><option v-for="scope in accessScopes" :key="scope.id" :value="scope.id">{{ scope.label }}</option></select></label>
            </div>
            <div v-if="isAgentMode && canPickTools" class="tool-columns">
              <div class="picker-card">
                <div class="picker-head"><strong>工具</strong><small>已选 {{ selectedTools.length }}</small></div>
                <div v-if="plugins.length === 0" class="empty-copy">暂无可用工具</div>
                <label v-for="tool in plugins" :key="tool.id || tool.tool_id" class="picker-item"><input type="checkbox" :checked="selectedTools.includes(tool.id || tool.tool_id)" @change="toggleTool(tool.id || tool.tool_id)" /><span>{{ tool.display_name || tool.name }}<small>{{ tool.description || '暂无描述' }}</small></span></label>
              </div>
              <div class="picker-card">
                <div class="picker-head"><strong>MCP</strong><small>已选 {{ selectedMcpServers.length }}</small></div>
                <div v-if="mcpServers.length === 0" class="empty-copy">暂无可用 MCP 服务</div>
                <label v-for="server in mcpServers" :key="server.mcp_server_id" class="picker-item"><input type="checkbox" :checked="selectedMcpServers.includes(server.mcp_server_id)" @change="toggleMcp(server.mcp_server_id)" /><span>{{ server.name || server.server_name }}<small>{{ server.description || '暂无描述' }}</small></span></label>
              </div>
              <div class="picker-card">
                <div class="picker-head"><strong>知识库</strong><small>已选 {{ selectedKnowledgeIds.length }}</small></div>
                <div v-if="knowledgeOptions.length === 0" class="empty-copy">暂无可用知识库</div>
                <label v-for="knowledge in knowledgeOptions" :key="knowledge.id" class="picker-item"><input type="checkbox" :checked="selectedKnowledgeIds.includes(knowledge.id)" @change="toggleKnowledge(knowledge.id)" /><span>{{ knowledge.name }}<small>{{ knowledge.description || `共 ${knowledge.count} 个文件` }}</small></span></label>
              </div>
              <div class="picker-card">
                <div class="picker-head"><strong>Skill</strong><small>已选 {{ selectedSkillIds.length }}</small></div>
                <div v-if="skillOptions.length === 0" class="empty-copy">暂无可用 Skill</div>
                <label v-for="skill in skillOptions" :key="skill.id" class="picker-item"><input type="checkbox" :checked="selectedSkillIds.includes(skill.id)" @change="toggleSkill(skill.id)" /><span>{{ skill.name }}<small>{{ skill.description || '暂无描述' }}</small></span></label>
              </div>
            </div>
          </div>

          <div v-if="traceVisible" class="trace-card" :class="{ generating: isGenerating }">
            <div v-if="isGenerating" class="progress-inline">
              <div class="progress-head">
                <div class="trace-head-copy">
                  <strong>{{ progressHeadline }}</strong>
                  <small>{{ progressDetail }}</small>
                </div>
                <span class="progress-badge">处理中</span>
              </div>
              <div class="progress-steps">
                <div v-for="step in progressSteps" :key="step.key" class="progress-step" :class="{ active: step.active, done: step.done }">
                  <span class="progress-dot"></span>
                  <span>{{ step.label }}</span>
                </div>
              </div>
            </div>
            <div class="picker-head"><div class="trace-head-copy"><strong>执行进展</strong><small>{{ selectedToolCount > 0 ? `已启用 ${selectedToolCount} 项能力` : '未启用额外工具' }}</small></div></div>
            <div v-if="executionEvents.length === 0" class="empty-copy">正在等待新的执行事件...</div>
            <div v-else class="trace-list"><div v-for="event in executionEvents" :key="event.id" class="trace-item"><div class="trace-head"><strong>{{ event.title }}</strong><span>{{ event.at }}</span></div><div v-if="event.detail" class="trace-detail">{{ event.detail }}</div></div></div>
          </div>

          <div v-if="pendingAttachments.length > 0" class="attachment-strip">
            <div v-for="attachment in pendingAttachments" :key="attachment.id" class="attachment-chip" :class="{ image: isImageAttachment(attachment) }">
              <img v-if="isImageAttachment(attachment)" :src="attachment.preview_url || attachment.url" :alt="attachment.name" class="attachment-thumb" />
              <div class="attachment-copy">
                <span class="attachment-name">{{ attachment.name }}</span>
                <span class="attachment-size">{{ formatAttachmentSize(attachment.size) }}</span>
              </div>
              <button type="button" class="attachment-remove" @click="removeAttachment(attachment.id)">×</button>
            </div>
          </div>
          <div v-if="isAttachmentDragOver" class="drop-hint">松开即可添加附件</div>
          <input ref="attachmentInputRef" class="attachment-input" type="file" multiple :accept="attachmentAccept" @change="handleAttachmentChange" />
          <textarea v-model="inputMessage" class="composer" :rows="compactPanel ? 1 : 2" :placeholder="composerPlaceholder" @keydown="handleKeydown" @paste="handleComposerPaste" />
          <div v-if="slashSuggestions.length > 0" class="slash-suggestions">
            <button
              v-for="(suggestion, index) in slashSuggestions"
              :key="suggestion.key"
              type="button"
              class="slash-suggestion"
              :class="{ active: index === activeSuggestionIndex }"
              @click="applySlashSuggestion(suggestion)"
            >
              <span class="slash-label">{{ suggestion.label }}</span>
              <span class="slash-detail">{{ suggestion.detail }}</span>
            </button>
          </div>
          <div class="composer-footer">
            <div class="composer-footer-left">
              <button class="attach-btn" type="button" :disabled="attachmentsUploading || isGenerating" @click="triggerAttachmentSelect"><el-icon><Plus /></el-icon><span>{{ attachmentsUploading ? '上传中...' : '添加附件' }}</span></button>
              <div class="composer-meta"><span class="composer-hint">{{ modeFooterCopy }}</span><span class="attachment-hint">{{ attachmentHint }}</span></div>
            </div>
            <button class="send-btn" :disabled="isGenerating || attachmentsUploading" @click="submitMessage">{{ isGenerating ? '处理中...' : '发送' }}</button>
          </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.workspace-chat {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at top center, rgba(224, 177, 134, 0.08), transparent 34%),
    linear-gradient(180deg, #f8f3eb 0%, #faf7f2 100%);
}

.workspace-shell {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 8px 14px 6px;
  overflow: hidden;
}

.hero-card {
  border: 1px solid rgba(225, 207, 189, 0.7);
  border-radius: 24px;
  background: rgba(255, 252, 248, 0.84);
  box-shadow: 0 20px 40px rgba(90, 58, 29, 0.06);
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 30px 20px 24px;
  text-align: center;
}

.hero-avatar {
  width: 66px;
  height: 66px;
}

.hero-card h1 {
  margin: 0;
  color: #2f241b;
  font-size: 26px;
}

.hero-card p {
  margin: 0;
  color: #7f6a55;
}

.mode-switcher {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.mode-pill {
  border: 1px solid rgba(220, 198, 176, 0.8);
  background: rgba(255, 251, 246, 0.85);
  color: #7f654d;
  border-radius: 999px;
  padding: 8px 16px;
  cursor: pointer;
}

.mode-pill.active {
  background: linear-gradient(135deg, #d58a4d 0%, #bc6733 100%);
  border-color: transparent;
  color: #fff;
}

.conversation-panel {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 0 62px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message-row.user {
  justify-content: flex-end;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.message-bubble {
  max-width: min(820px, 76vw);
  padding: 8px 10px;
  border-radius: 14px;
  background: linear-gradient(135deg, #d48a4f 0%, #bb6631 100%);
  color: #fff;
}

.message-bubble.assistant {
  background: rgba(255, 252, 248, 0.9);
  color: #2f241b;
  border: 1px solid rgba(229, 211, 194, 0.7);
}

.message-bubble.assistant.loading {
  min-width: 320px;
}

.loading-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7b654f;
  font-size: 13px;
  min-height: 44px;
  width: 100%;
}

.loading-row.agent {
  display: grid;
  gap: 10px;
  align-items: stretch;
  min-height: 0;
}

.loading-head {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.loading-copy {
  display: grid;
  gap: 3px;
}

.loading-copy strong {
  color: #5b3920;
  font-size: 13px;
}

.loading-copy span {
  color: #7b654f;
  font-size: 12px;
  line-height: 1.45;
}

.loading-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.loading-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.95);
  border: 1px solid rgba(226, 206, 187, 0.9);
  color: #8b6d53;
  font-size: 11px;
}

.loading-step.active {
  color: #6d431d;
  border-color: rgba(201, 108, 45, 0.4);
  background: rgba(255, 242, 228, 0.98);
}

.loading-step.done {
  color: #6a543f;
}

.loading-events {
  display: grid;
  gap: 6px;
}

.loading-event {
  display: grid;
  gap: 2px;
  padding: 7px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(235, 220, 204, 0.9);
}

.loading-event strong {
  color: #5b3920;
  font-size: 12px;
}

.loading-event span {
  color: #7b654f;
  font-size: 11px;
  line-height: 1.4;
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(212, 138, 79, 0.22);
  border-top-color: #d48a4f;
  animation: spin 0.9s linear infinite;
}

.composer-dock {
  position: sticky;
  bottom: 0;
  flex-shrink: 0;
  z-index: 6;
  margin-top: auto;
  padding-top: 4px;
  background: linear-gradient(180deg, rgba(248, 243, 235, 0) 0%, rgba(248, 243, 235, 0.92) 24%, rgba(248, 243, 235, 0.98) 100%);
}

.composer-dock.fixed {
  padding-top: 4px;
}

.composer-shell {
  width: min(880px, calc(100% - 24px));
  margin: 0 auto;
  padding: 6px 8px 7px;
  border-radius: 16px;
  border: 1px solid rgba(225, 207, 189, 0.78);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 8px 14px rgba(90, 58, 29, 0.06);
  backdrop-filter: blur(10px);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.composer-shell.drag-active {
  border-color: rgba(201, 108, 45, 0.68);
  box-shadow: 0 0 0 3px rgba(201, 108, 45, 0.14), 0 18px 32px rgba(90, 58, 29, 0.12);
  background: rgba(255, 248, 239, 0.98);
}

.drop-hint {
  margin-bottom: 6px;
  border: 1px dashed rgba(201, 108, 45, 0.48);
  border-radius: 14px;
  padding: 8px 10px;
  background: rgba(255, 244, 232, 0.82);
  color: #8a552e;
  font-size: 12px;
  text-align: center;
}

.slash-suggestions {
  display: grid;
  gap: 6px;
  margin-top: 8px;
  margin-bottom: 6px;
}

.slash-suggestion {
  width: 100%;
  border: 1px solid rgba(225, 207, 189, 0.82);
  background: rgba(255, 252, 248, 0.95);
  border-radius: 12px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.16s ease, background 0.16s ease, box-shadow 0.16s ease;
}

.slash-suggestion.active,
.slash-suggestion:hover {
  border-color: rgba(201, 108, 45, 0.45);
  background: rgba(255, 245, 235, 0.98);
  box-shadow: 0 6px 14px rgba(90, 58, 29, 0.06);
}

.slash-label {
  color: #5b3920;
  font-size: 13px;
  font-weight: 600;
}

.slash-detail {
  color: #8c735d;
  font-size: 11px;
  line-height: 1.4;
}

.composer-top,
.picker-head,
.trace-head,
.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.composer-top {
  margin-bottom: 2px;
}

.composer-top.compact {
  justify-content: flex-end;
  margin-bottom: 2px;
}

.mode-badge {
  display: grid;
  gap: 2px;
}

.label {
  font-size: 11px;
  color: #8d7054;
}

.mode-badge strong {
  color: #2f241b;
  font-size: 14px;
}

.composer-actions,
.composer-footer-left {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.ghost-pill,
.attach-btn {
  border: 1px solid rgba(218, 192, 168, 0.78);
  background: rgba(255, 251, 246, 0.84);
  color: #7b644d;
  border-radius: 999px;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 11px;
}

.ghost-pill.subtle {
  padding: 4px 9px;
  background: rgba(255, 251, 246, 0.65);
  border-color: rgba(223, 203, 182, 0.68);
}

.settings-panel,
.trace-card {
  margin-bottom: 4px;
  padding: 6px;
  border-radius: 12px;
  border: 1px solid rgba(232, 216, 198, 0.86);
  background: rgba(255, 255, 255, 0.72);
  max-height: 176px;
  overflow-y: auto;
}

.trace-card.generating {
  max-height: none;
  overflow: visible;
}

.selector-grid,
.tool-columns {
  display: grid;
  gap: 10px;
}

.selector-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.agent-grid,
.tool-columns {
  margin-top: 10px;
}

.tool-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field {
  display: grid;
  gap: 4px;
}

.field span,
.composer-hint,
.attachment-hint,
.attachment-size {
  font-size: 11px;
  color: #866a51;
}

.field select,
.composer {
  border: 1px solid rgba(225, 207, 189, 0.95);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
}

.field select {
  height: 32px;
  padding: 0 10px;
  font-size: 12px;
}

.picker-card {
  display: grid;
  gap: 7px;
  padding: 9px;
  border-radius: 14px;
  border: 1px solid rgba(236, 222, 207, 0.9);
  background: rgba(255, 252, 248, 0.72);
}

.picker-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  color: #4f3c2b;
}

.picker-item span,
.trace-head-copy,
.composer-meta,
.attachment-copy {
  display: grid;
  gap: 3px;
}

.picker-item small,
.trace-head-copy small,
.empty-copy {
  color: #8a745f;
}

.progress-inline {
  display: grid;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(225, 207, 189, 0.92);
  background: rgba(255, 248, 240, 0.9);
}

.progress-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.progress-badge {
  flex: 0 0 auto;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(201, 108, 45, 0.12);
  color: #b96534;
  font-size: 11px;
  font-weight: 600;
}

.progress-steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.progress-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  padding: 6px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  color: #8b6d53;
  font-size: 11px;
  border: 1px solid rgba(230, 214, 198, 0.9);
}

.progress-step.active {
  color: #6d431d;
  border-color: rgba(201, 108, 45, 0.45);
  background: rgba(255, 244, 232, 0.98);
}

.progress-step.done {
  color: #6a543f;
}

.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(190, 158, 129, 0.55);
}

.progress-step.active .progress-dot {
  background: #cb7a3f;
  box-shadow: 0 0 0 4px rgba(203, 122, 63, 0.14);
}

.progress-step.done .progress-dot {
  background: #b56b36;
}

.trace-list {
  max-height: 140px;
  overflow-y: auto;
  display: grid;
  gap: 7px;
  margin-top: 6px;
}

.trace-card.generating .trace-list {
  max-height: 220px;
}

.trace-item {
  border: 1px solid rgba(239, 225, 209, 0.9);
  border-radius: 12px;
  background: rgba(251, 245, 238, 0.82);
  padding: 7px 9px;
  display: grid;
  gap: 3px;
}

.trace-detail {
  white-space: pre-wrap;
  word-break: break-word;
  color: #584434;
  line-height: 1.45;
  font-size: 12px;
}

.attachment-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 5px;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.98);
  border: 1px solid rgba(222, 195, 169, 0.88);
  color: #6f543d;
}

.attachment-chip.image {
  border-radius: 16px;
  align-items: center;
}

.attachment-thumb {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  object-fit: cover;
  border: 1px solid rgba(222, 195, 169, 0.72);
}

.attachment-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
}

.attachment-remove {
  border: none;
  background: transparent;
  color: #9f6b43;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.attachment-input {
  display: none;
}

.composer {
  width: 100%;
  min-height: 32px;
  max-height: 72px;
  padding: 6px 9px;
  resize: none;
  outline: none;
  color: #2f241b;
  line-height: 1.32;
  font-size: 12px;
}

.composer-footer {
  margin-top: 4px;
}

.send-btn {
  min-width: 74px;
  height: 30px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #d58a4d 0%, #bc6733 100%);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.message-bubble :deep(.md-editor-preview) {
  font-size: 12px;
  line-height: 1.42;
}

.message-bubble :deep(.md-editor-preview-wrapper) {
  padding: 0;
}

.message-bubble :deep(p) {
  margin: 0 0 0.42em;
}

.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3),
.message-bubble :deep(h4) {
  margin: 0.12em 0 0.32em;
  line-height: 1.28;
}

.message-bubble :deep(h1) { font-size: 1.22em; }
.message-bubble :deep(h2) { font-size: 1.12em; }
.message-bubble :deep(h3) { font-size: 1.04em; }
.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 0.25em 0 0.42em 1em;
  padding: 0;
}

.message-bubble :deep(li) {
  margin: 0.12em 0;
}

.message-bubble :deep(pre) {
  margin: 0.35em 0;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 11px;
}

.message-bubble :deep(code) {
  font-size: 0.88em;
}

.message-bubble.assistant :deep(table) {
  font-size: 11.5px;
}

.message-bubble.assistant :deep(blockquote) {
  margin: 0.32em 0;
  padding: 0.2em 0 0.2em 0.7em;
}

.composer-meta {
  gap: 1px;
}

.send-btn:disabled,
.attach-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1100px) {
  .message-bubble {
    max-width: min(100%, 74vw);
  }

  .selector-grid,
  .tool-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .workspace-shell {
    padding: 8px 6px 6px;
  }

  .composer-shell {
    width: 100%;
    padding: 6px 7px;
    border-radius: 14px;
  }

  .message-bubble {
    max-width: calc(100vw - 120px);
  }

  .composer-top,
  .composer-footer,
  .composer-footer-left {
    align-items: flex-start;
    flex-direction: column;
  }

  .composer-actions {
    flex-wrap: wrap;
  }

  .attachment-name {
    max-width: 160px;
  }

  .progress-steps {
    grid-template-columns: 1fr;
  }

  .message-bubble.assistant.loading {
    min-width: min(260px, calc(100vw - 120px));
  }
}
</style>
