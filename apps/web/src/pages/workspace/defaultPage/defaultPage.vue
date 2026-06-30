<script setup lang="ts">
import { computed, markRaw, nextTick, onBeforeUnmount, onMounted, onUpdated, ref, watch, type Component } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowLeft, ArrowUp, CopyDocument, Plus } from '@element-plus/icons-vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import {
  approveWorkspaceTaskAPI,
  createWorkspaceFeedbackAPI,
  createWorkspaceFileAPI,
  createWorkspaceIngestAPI,
  createWorkspaceTaskAPI,
  createWorkspaceSessionAPI,
  deleteWorkspaceSessionAPI,
  getWorkspaceArtifactAPI,
  getWorkspaceExecutionModesAPI,
  getWorkspacePluginsByModeAPI,
  getWorkspaceSessionInfoAPI,
  getWorkspaceTaskAPI,
  workspaceSimpleChatStreamAPI,
  workspaceTaskEventsStreamAPI,
  type AccessScopeDefinition,
  type ExecutionModeDefinition,
  type WorkspaceArtifactResponse,
  type WorkspaceExecutionConfig,
  type WorkspaceObservabilitySnapshot,
  type WorkspaceStreamEvent,
  type WorkspaceTaskCreateResponse,
  type WorkSpaceSimpleTask,
} from '../../../apis/workspace'
import { uploadFile } from '../../../apis/chat'
import { getVisibleLLMsAPI, type LLMResponse } from '../../../apis/llm'
import { getAgentsAPI, type AgentResponse } from '../../../apis/agent'
import { getAgentSkillsAPI, type AgentSkill } from '../../../apis/agent-skill'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../../apis/knowledge'
import { useUserStore } from '../../../store/user'
import { getRetrievalModeLabel, normalizeRetrievalMode } from '../../../utils/retrieval'
import { describeKnowledgeConfig, normalizeKnowledgeConfig } from '../../../utils/knowledge-config'
import { safeDisplayText } from '../../../utils/display-text'
import { sanitizeWorkspaceContexts } from '../../../utils/workspace-history'
import { zunoAgentAvatar } from '../../../utils/brand'
import { isDesktopRuntime } from '../../../utils/api'
import { getSettingsIcon } from '../../../utils/settings-icons'
import MascotPresence from '../../../components/MascotPresence.vue'
import type { ZunoPetMood } from '../../../components/zuno-pet'
import messageIcon from '../../../assets/message.svg'
import { DEFAULT_USER_AVATAR, isLegacyRemoteUserAvatar, withUserAvatarVersion } from '../../../utils/user-avatars'
import Agent from '../../agent'
import AgentEditor from '../../agent/agent-editor.vue'
import AgentSkillPage from '../../agent-skill'
import Dashboard from '../../dashboard'
import Knowledge from '../../knowledge'
import KnowledgeConfig from '../../knowledge/knowledge-config.vue'
import KnowledgeFile from '../../knowledge/knowledge-file.vue'
import McpServer from '../../mcp-server'
import Model from '../../model'
import Profile from '../../profile'
import Tool from '../../tool'
import { ConversationArchive } from '../../account'
import SettingsUiModeSwitch from '../components/SettingsUiModeSwitch.vue'
import {
  loadWorkspaceDefaults,
  saveWorkspaceSessionMode,
  type WorkspaceMode,
} from '../../../utils/workspace-defaults'
import {
  loadSettingsUiMode,
  type SettingsUiMode,
} from '../../../utils/settings-preferences'
import {
  AGENT_DOCUMENT_EXTENSIONS,
  ALWAYS_WEB_SEARCH,
  CHAT_IMAGE_EXTENSIONS,
  MAX_ATTACHMENTS,
  MAX_ATTACHMENT_SIZE,
  fallbackDescription,
  fallbackKnowledgeDescription,
  modes,
  settingsCommandSections,
  settingsLabels,
  settingsRouteBySection,
} from './defaultPage.constants'
import type {
  AgentOption,
  ChatMessage,
  ConversationBlock,
  MascotPresenceState,
  MessageMotion,
  NewConversationDetail,
  PendingAttachment,
  ProgressStep,
  RetrievalTraceSummary,
  SettingsRouteSnapshot,
  SettingsThreadItem,
  SlashSuggestion,
  ToolCreationKind,
  TraceRecord,
} from './defaultPage.types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const selectedMode = ref<WorkspaceMode>('normal')
const activeAgentName = ref('')
const activeAgentId = ref('')
const inputMessage = ref('')
const consumedInitialMessageKey = ref('')
const initialRouteMessageInFlightKey = ref('')
const messages = ref<ChatMessage[]>([])
const executionEvents = ref<TraceRecord[]>([])
const pendingToolApproval = ref<{
  taskId: string
  toolId: string
  requiredApproval: string
  approvalId: string
  toolCallId: string
  auditRef: string
} | null>(null)
const activeRuntimeTaskId = ref('')
const activeRuntimeArtifact = ref<{
  artifactId: string
  content: string
  citations: string[]
  uri: string
} | null>(null)
const activeRuntimeCitationIds = ref<string[]>([])
const activeRuntimeObservability = ref<WorkspaceObservabilitySnapshot | null>(null)
const runtimeFailure = ref<{ title: string; detail: string } | null>(null)
const feedbackSubmitting = ref(false)
const feedbackSent = ref(false)
const runtimeFeedbackLabel = ref('')
const toolApprovalSubmitting = ref(false)
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
const sessionHistoryLoading = ref(false)
const sessionHistoryLabel = ref('正在打开对话')
const conversationRef = ref<HTMLElement | null>(null)
const showTracePanel = ref(false)
const isPinnedToBottom = ref(true)
const workspaceHydrated = ref(false)
const preserveConversationOnRouteSync = ref(false)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const composerInputRef = ref<HTMLTextAreaElement | null>(null)
const pendingAttachments = ref<PendingAttachment[]>([])
const attachmentsUploading = ref(false)
const isAttachmentDragOver = ref(false)
const activeSuggestionIndex = ref(0)
const settingsThreads = ref<SettingsThreadItem[]>([])
const composerExpanded = ref(false)
const composerFocused = ref(false)
const transientPetMood = ref<ZunoPetMood | ''>('')
const agentPickerOpen = ref(false)
const agentPickerLoading = ref(false)
const agentOptions = ref<AgentOption[]>([])
const activeAssistantMessageIndex = ref(-1)
const assistantTextStreaming = ref(false)
let conversationOrder = 0
let settingsMutationObserver: MutationObserver | null = null
let settingsBubbleAnchorCleanup: (() => void) | null = null
let settingsAnchorProgrammaticScroll = false
let settingsAnchorProgrammaticTimer = 0
let autosizeFrame = 0
let viewportResizeFrame = 0
let viewportResizeTimer = 0
let transientPetMoodTimer = 0
const messageMotionTimers = new Map<ChatMessage, number>()
let restoringSettingsRoute = false
let pendingSettingsNavigationThreadId = ''
let sessionHistoryLoadToken = ''
const activeSettingsRouteSnapshot = ref<SettingsRouteSnapshot | null>(null)
const settingsUiMode = ref<SettingsUiMode>(loadSettingsUiMode())

const settingsComponentByRouteName: Record<string, Component> = {
  workspaceSettingsAgent: markRaw(Agent),
  workspaceSettingsAgentEditor: markRaw(AgentEditor),
  workspaceSettingsModel: markRaw(Model),
  workspaceSettingsKnowledge: markRaw(Knowledge),
  workspaceSettingsKnowledgeFile: markRaw(KnowledgeFile),
  workspaceSettingsKnowledgeConfig: markRaw(KnowledgeConfig),
  workspaceSettingsMcp: markRaw(McpServer),
  workspaceSettingsTool: markRaw(Tool),
  workspaceSettingsSkill: markRaw(AgentSkillPage),
  workspaceSettingsDashboard: markRaw(Dashboard),
  workspaceAccountProfile: markRaw(Profile),
  workspaceAccountConversations: markRaw(ConversationArchive),
}

const activeMode = computed(() => modes.find((mode) => mode.id === selectedMode.value) || modes[0])
const settingsRouteActive = computed(() => Boolean(route.meta.settingsSection || route.meta.accountSection))
const useTraditionalSettingsShell = computed(() => settingsRouteActive.value && settingsUiMode.value === 'traditional')
const conversationBlocks = computed<ConversationBlock[]>(() => {
  const messageBlocks = messages.value.map((message, index) => ({
    type: 'message' as const,
    order: message.uiOrder || index + 1,
    message,
    index,
  }))
  const settingsBlocks = settingsThreads.value.map((thread) => ({
    type: 'settings' as const,
    order: thread.order,
    thread,
  }))
  return [...messageBlocks, ...settingsBlocks].sort((a, b) => a.order - b.order)
})
const hasConversationBlocks = computed(() => conversationBlocks.value.length > 0)
const conversationSurfaceActive = computed(() => hasConversationBlocks.value || sessionHistoryLoading.value)
const latestAssistantMessageIndex = computed(() => {
  for (let index = messages.value.length - 1; index >= 0; index -= 1) {
    if (messages.value[index]?.role === 'assistant') return index
  }
  return -1
})
const normalizePetMood = (mood: ZunoPetMood | ''): MascotPresenceState | '' => {
  if (!mood) return ''
  if (mood === 'wake') return 'click'
  return mood
}
const getAssistantMascotState = (messageIndex: number): MascotPresenceState => {
  if (messageIndex !== latestAssistantMessageIndex.value) return 'idle'

  const transientState = normalizePetMood(transientPetMood.value)
  if (transientState) return transientState

  const message = messages.value[messageIndex]
  if (message?.motion === 'error') return 'error'
  if (message?.motion === 'complete') return 'success'
  if (message?.motion === 'streaming') return 'typing'
  if (message?.motion === 'thinking') return 'thinking'

  if (isGenerating.value && messageIndex === activeAssistantMessageIndex.value) {
    return assistantTextStreaming.value ? 'typing' : 'thinking'
  }

  if (composerFocused.value || inputMessage.value.trim()) return 'listening'
  return 'idle'
}
const getAssistantStatusLabel = (message: ChatMessage, messageIndex: number) => {
  if (message.motion === 'error') return '需要调整'
  if (message.motion === 'thinking') return '正在思考'
  if (message.motion === 'streaming') return '正在输出'
  if (message.motion === 'complete') return '已完成'
  if (!message.content && isGenerating.value && messageIndex === messages.value.length - 1) return '正在思考'
  return '已回复'
}
const shouldShowAssistantStatus = (message: ChatMessage, messageIndex: number) => (
  !!message.motion || (!message.content && isGenerating.value && messageIndex === messages.value.length - 1)
)
const getSettingsMascotState = (thread: SettingsThreadItem): MascotPresenceState => (
  thread.ready ? 'idle' : 'thinking'
)
const isAccountThread = (thread: SettingsThreadItem) => ['profile', 'conversations'].includes(thread.section)
const getThreadLoadingVerb = (thread: SettingsThreadItem) => isAccountThread(thread) ? '正在整理' : '正在整理'
const getThreadLoadingText = (thread: SettingsThreadItem) => isAccountThread(thread) ? 'Zuno 正在整理账号内容' : 'Zuno 正在拉取配置'
const normalizeAvatarUrl = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/') || isLegacyRemoteUserAvatar(raw)) return DEFAULT_USER_AVATAR
  return withUserAvatarVersion(raw)
}
const userAvatarSrc = computed(() => normalizeAvatarUrl(userStore.userInfo?.avatar))
const activeExecutionMode = computed(() => executionModes.value.find((mode) => mode.id === selectedExecutionMode.value) || null)
const activeAccessScope = computed(() => accessScopes.value.find((scope) => scope.id === selectedAccessScope.value) || null)
const isAgentMode = computed(() => selectedMode.value === 'agent')
const selectedModel = computed(() => modelOptions.value.find((model) => model.llm_id === selectedModelId.value) || null)
const modelStatusLabel = computed(() => {
  if (modelsLoading.value) return '正在读取模型'
  if (selectedModel.value) return `模型：${selectedModel.value.model || selectedModel.value.provider || '已就绪'}`
  return '还没有可用模型'
})
const modelStatusTone = computed(() => selectedModel.value ? 'ready' : (modelsLoading.value ? 'loading' : 'empty'))
const heroTitle = computed(() => isAgentMode.value && activeAgentName.value ? `和 ${activeAgentName.value} 开聊` : '今天想让 Zuno 做什么？')
const heroSubtitle = computed(() => isAgentMode.value && activeAgentName.value ? '这个对话会跟随选中的 Agent，工具和知识库也会一起工作。' : '直接输入问题，或切到 Agent 处理带工具的任务。')
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
  return '输入你的任务，或输入 / 直接选择 Skill。'
})
const modeFooterCopy = computed(() => {
  if (!isAgentMode.value) return '聊天模式 / 支持图片输入'
  const base = `${activeExecutionMode.value?.label || '工具模式'} / ${activeAccessScope.value?.label || '工作区限制'}`
  if (selectedExecutionMode.value === 'terminal') return `${base} · 支持 /terminal`
  return `${base} · MCP 默认启用，输入 / 可快速选择 Skill`
})
const canPickTools = computed(() => isAgentMode.value && selectedExecutionMode.value === 'tool')
const autoAvailableMcpIds = computed(() => (
  mcpServers.value
    .filter((server: any) => !server?.config_enabled && (!Array.isArray(server?.config) || server.config.length === 0))
    .map((server: any) => server.mcp_server_id)
    .filter(Boolean)
))
const selectedToolCount = computed(() => (
  selectedTools.value.length
  + selectedMcpServers.value.length
  + selectedSkillIds.value.length
  + selectedKnowledgeIds.value.length
))
const selectedKnowledge = computed(() => {
  const currentId = selectedKnowledgeIds.value[0]
  return knowledgeOptions.value.find((item) => item.id === currentId) || null
})
const selectedKnowledgeConfig = computed(() => normalizeKnowledgeConfig(selectedKnowledge.value?.knowledge_config))
const effectiveRetrievalMode = computed(() => normalizeRetrievalMode(selectedKnowledgeConfig.value.retrieval_settings.default_mode))
const effectiveRetrievalModeLabel = computed(() => getRetrievalModeLabel(effectiveRetrievalMode.value))
const selectedKnowledgeSummary = computed(() => describeKnowledgeConfig(selectedKnowledgeConfig.value))
const buildToolCreationPrompt = (kind: ToolCreationKind = 'general') => {
  if (kind === 'api') {
    return [
      '请帮我新增一个 API 工具。',
      '你先判断我提供的信息是否足够；如果不够，请继续追问。',
      '我会继续给你：接口文档或文档地址、Base URL、路径、认证方式、API Key、图标。',
      '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
    ].join('\n')
  }
  if (kind === 'cli') {
    return [
      '请帮我新增一个 CLI 工具。',
      '你先判断我提供的信息是否足够；如果不够，请继续追问。',
      '我会继续给你：本地目录、可执行命令、GitHub 地址、README、安装方法、所需凭证、图标。',
      '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
    ].join('\n')
  }
  return [
    '请帮我新增一个工具。',
    '你先判断它应该接成 API 还是 CLI；如果信息不够，请继续追问。',
    '我会继续给你：文档地址、URL、API Key、本地目录、安装方法、图标等。',
    '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
  ].join('\n')
}

const openToolCreationPrompt = (kind: ToolCreationKind = 'general') => {
  inputMessage.value = buildToolCreationPrompt(kind)
  activeSuggestionIndex.value = 0
}

const retrievalModeHint = computed(() => {
  if (!isAgentMode.value || !canPickTools.value || selectedKnowledgeIds.value.length === 0) {
    return '选中知识库后，会自动使用这个知识库自己的默认检索策略。首轮不足时会自动补检一轮。'
  }
  return `当前跟随知识库：${effectiveRetrievalModeLabel.value}`
})
const traceVisible = computed(() => isAgentMode.value && showTracePanel.value)
const compactPanel = computed(() => conversationSurfaceActive.value)
const canCollapseComposer = computed(() => (
  conversationSurfaceActive.value
  && !sessionHistoryLoading.value
  && !inputMessage.value.trim()
  && pendingAttachments.value.length === 0
  && slashSuggestions.value.length === 0
  && !traceVisible.value
  && !isAttachmentDragOver.value
  && !attachmentsUploading.value
))
const compactComposerVisible = computed(() => canCollapseComposer.value && !composerExpanded.value)
const toolCreationSuggestions: SlashSuggestion[] = [
  {
    key: 'create-tool-general',
    label: '/新增工具',
    detail: '让 Agent 判断是 API 还是 CLI，并继续追问缺失信息。',
    insertValue: buildToolCreationPrompt('general'),
  },
  {
    key: 'create-tool-api',
    label: '/新增API工具',
    detail: '适合你已经有文档、URL、认证方式或 API Key 的接口能力。',
    insertValue: buildToolCreationPrompt('api'),
  },
  {
    key: 'create-tool-cli',
    label: '/新增CLI工具',
    detail: '适合本地目录、可执行命令、README、GitHub 仓库一类能力。',
    insertValue: buildToolCreationPrompt('cli'),
  },
]

const slashSuggestions = computed<SlashSuggestion[]>(() => {
  if (!isAgentMode.value || selectedExecutionMode.value === 'terminal') return []
  const text = inputMessage.value || ''
  if (!text.startsWith('/')) return []
  const trimmed = text.trimStart()
  if (!trimmed.startsWith('/')) return []

  const keyword = trimmed.slice(1).trim().toLowerCase()
  const builtIns = toolCreationSuggestions.filter((item) => {
    const haystack = `${item.label} ${item.detail}`.toLowerCase()
    return !keyword || haystack.includes(keyword)
  })
  const skillSuggestions = skillOptions.value
    .filter((skill) => {
      const name = (skill.name || '').toLowerCase()
      const desc = (skill.description || '').toLowerCase()
      return !keyword || name.includes(keyword) || desc.includes(keyword)
    })
    .slice(0, 8)
    .map((skill) => ({
      key: `skill-${skill.id}`,
      label: `/${skill.name}`,
      detail: skill.description || 'Skill',
      insertValue: `/${skill.name} `,
    }))
  return [...builtIns, ...skillSuggestions].slice(0, 8)
})
const latestTraceRecord = computed(() => executionEvents.value[executionEvents.value.length - 1] || null)
const progressStageIndex = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return -1
  if (!isGenerating.value && executionEvents.value.length > 0) return 4
  const last = latestTraceRecord.value
  if (!last) return 0
  if (last.phase === 'complete' || last.status === 'END') return 4
  if (last.phase === 'model_call' || last.phase === 'answer') return 3
  if (last.accent === 'tool') return 2
  if (last.accent === 'graph') return 1
  if (last.accent === 'retrieval') return 1
  return 0
})
const progressSteps = computed<ProgressStep[]>(() => {
  const activeIndex = progressStageIndex.value
  return [
    { key: 'prepare', label: '准备请求', done: activeIndex > 0, active: activeIndex === 0, accent: 'default' },
    { key: 'retrieve', label: '检索知识', done: activeIndex > 1, active: activeIndex === 1, accent: effectiveRetrievalMode.value === 'rag_graph' ? 'graph' : 'retrieval' },
    { key: 'tool', label: '调用能力', done: activeIndex > 2, active: activeIndex === 2, accent: 'tool' },
    { key: 'answer', label: '整理答案', done: activeIndex > 3, active: activeIndex === 3, accent: 'answer' },
    { key: 'done', label: '完成输出', done: !isGenerating.value && executionEvents.value.length > 0, active: activeIndex === 4, accent: 'default' },
  ]
})
const progressHeadline = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return latestTraceRecord.value?.title || '正在处理中'
})
const progressDetail = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return latestTraceRecord.value?.detail || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value}`
})
const liveProgressEvents = computed(() => executionEvents.value.slice(-3))
const runtimeSpanCount = computed(() => activeRuntimeObservability.value?.spans?.length || 0)
const runtimeTraceSourceRefs = computed(() => activeRuntimeObservability.value?.trace_replay?.source_refs || [])
const runtimeReleaseEvalStatus = computed(() => String(
  activeRuntimeObservability.value?.release_eval?.status
  || activeRuntimeObservability.value?.release_eval?.overall_status
  || activeRuntimeObservability.value?.release_eval?.verdict
  || 'pending'
))
const runtimeFeedbackCopy = computed(() => {
  if (!feedbackSent.value) return '等待反馈。'
  return runtimeFeedbackLabel.value === 'helpful' ? '已记录为可用结果。' : '已记录为需要调整。'
})

const safeQueryValue = (value: unknown, fallback: string) => Array.isArray(value) ? String(value[0] || fallback) : (typeof value === 'string' && value.trim() ? value : fallback)
const getFileExtension = (fileName: string) => fileName.split('.').pop()?.toLowerCase() || ''
const normalizeSessionMode = (session: any): WorkspaceMode => {
  if (normalizeSessionAgentName(session)) return 'agent'
  const explicitMode = String(session?.workspace_mode || '').trim().toLowerCase()
  if (explicitMode === 'normal') return 'normal'
  return 'normal'
}
const normalizeSessionAgentName = (session: any) => {
  const raw = String(session?.agent || '').trim()
  if (!raw || ['normal', 'simple', 'agent'].includes(raw.toLowerCase())) return ''
  return raw
}

const sanitizeAssistantChunk = (chunk: string) => isAgentMode.value ? chunk : chunk.replace(/ReAct\s*Agent[^\n]*\n?/gi, '').replace(/^\s+/, '')
const normalizeMessageMarkdown = (content: string) => {
  const lines = content.replace(/\r\n/g, '\n').split('\n')
  let insideFence = false

  const normalizedLines = lines.map((line) => {
    if (/^\s*```/.test(line)) {
      insideFence = !insideFence
      return line
    }
    if (insideFence) return line

    return line
      .replace(/^(\s{0,3})(#{1,6})(?=[^\s#])/g, '$1$2 ')
      .replace(/([。！？!?；;：:])\s*(#{1,6})(?=\s?\S)/g, '$1\n\n$2 ')
      .replace(/(\S)\s*(#{2,6})(?=[^\s#])/g, '$1\n\n$2 ')
      .replace(/^(\s{0,3})(#{1,6})\s{2,}/g, '$1$2 ')
      .replace(/^(\s*[-*+])(?=\S)/g, '$1 ')
      .replace(/^(\s*\d+\.)(?=\S)/g, '$1 ')
  })

  return normalizedLines
    .join('\n')
    .replace(/([^\n])\n(\|[^\n]+\|\n\|[-:\s|]+\|)/g, '$1\n\n$2')
    .replace(/(^|\n)(\s{0,3})(#{1,6})\s{2,}/g, '$1$2$3 ')
    .replace(/\n{4,}/g, '\n\n\n')
}
const handleAvatarError = (event: Event) => { const target = event.target as HTMLImageElement; if (target) target.src = DEFAULT_USER_AVATAR }
const copyMessageContent = async (message: ChatMessage) => {
  const content = message.content.trim()
  if (!content) return
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制')
  } catch (error) {
    console.error('复制消息失败', error)
    ElMessage.error('复制失败')
  }
}
const wait = (ms: number) => new Promise<void>((resolve) => window.setTimeout(resolve, ms))
const shouldReduceMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
const clearTransientPetMood = () => {
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  transientPetMoodTimer = 0
  transientPetMood.value = ''
}
const pulsePetMood = (mood: ZunoPetMood, duration = 1200) => {
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  transientPetMood.value = mood
  transientPetMoodTimer = window.setTimeout(() => {
    transientPetMood.value = ''
    transientPetMoodTimer = 0
  }, shouldReduceMotion() ? Math.min(duration, 240) : duration)
}
const clearMessageMotionTimers = () => {
  messageMotionTimers.forEach((timer) => window.clearTimeout(timer))
  messageMotionTimers.clear()
}
const setMessageMotion = (message: ChatMessage | undefined, motion: MessageMotion, duration = 0) => {
  if (!message) return
  const existingTimer = messageMotionTimers.get(message)
  if (existingTimer) window.clearTimeout(existingTimer)
  message.motion = motion
  if (!duration) {
    messageMotionTimers.delete(message)
    return
  }
  const timer = window.setTimeout(() => {
    if (message.motion === motion) message.motion = undefined
    messageMotionTimers.delete(message)
  }, shouldReduceMotion() ? Math.min(duration, 240) : duration)
  messageMotionTimers.set(message, timer)
}
const scrollToBottom = async (force = false, behavior: ScrollBehavior = 'auto') => {
  await nextTick()
  const panel = conversationRef.value
  if (!panel || (!force && !isPinnedToBottom.value)) return
  panel.scrollTo({
    top: panel.scrollHeight,
    behavior: shouldReduceMotion() ? 'auto' : behavior,
  })
}
const markSettingsAnchorProgrammaticScroll = () => {
  settingsAnchorProgrammaticScroll = true
  if (settingsAnchorProgrammaticTimer) window.clearTimeout(settingsAnchorProgrammaticTimer)
  settingsAnchorProgrammaticTimer = window.setTimeout(() => {
    settingsAnchorProgrammaticScroll = false
    settingsAnchorProgrammaticTimer = 0
  }, 120)
}
const cancelSettingsBubbleAnchor = () => {
  settingsBubbleAnchorCleanup?.()
}
const handleConversationScroll = () => {
  const panel = conversationRef.value
  if (!panel) return
  isPinnedToBottom.value = panel.scrollHeight - (panel.scrollTop + panel.clientHeight) < 24
  if (settingsBubbleAnchorCleanup && !settingsAnchorProgrammaticScroll) {
    cancelSettingsBubbleAnchor()
  }
}
const restoreSettingsBubbleTop = (bubble: HTMLElement, targetTop: number) => {
  const panel = conversationRef.value
  if (!panel || !panel.contains(bubble)) return false
  const nextTop = bubble.getBoundingClientRect().top
  const delta = nextTop - targetTop
  if (Math.abs(delta) < 0.5) return false
  markSettingsAnchorProgrammaticScroll()
  panel.scrollTop += delta
  return true
}
const lockSettingsBubbleTop = (bubble: HTMLElement, duration = 760) => {
  const panel = conversationRef.value
  if (!panel || !panel.contains(bubble)) return
  settingsBubbleAnchorCleanup?.()
  const targetTop = bubble.getBoundingClientRect().top
  let disposed = false
  const frameIds: number[] = []
  const timerIds: number[] = []
  let lastDelta = 0
  let expectedScrollTop = panel.scrollTop
  const runStable = () => {
    if (disposed) return
    if (!settingsAnchorProgrammaticScroll && Math.abs(panel.scrollTop - expectedScrollTop) > 3) {
      cancelSettingsBubbleAnchor()
      return
    }
    const nextTop = bubble.getBoundingClientRect().top
    const delta = nextTop - targetTop
    if (Math.abs(delta) < 1 || Math.abs(delta - lastDelta) < 0.5) return
    lastDelta = delta
    if (restoreSettingsBubbleTop(bubble, targetTop)) {
      expectedScrollTop = panel.scrollTop
    }
  }
  const queueFrame = () => {
    frameIds.push(window.requestAnimationFrame(() => {
      runStable()
      frameIds.push(window.requestAnimationFrame(runStable))
    }))
  }
  const resizeObserver = new ResizeObserver(runStable)
  resizeObserver.observe(bubble)
  queueFrame()
  ;[80, 180, 360, duration].forEach((delay) => {
    timerIds.push(window.setTimeout(runStable, delay))
  })
  const cleanupTimer = window.setTimeout(() => {
    settingsBubbleAnchorCleanup?.()
  }, duration + 80)
  settingsBubbleAnchorCleanup = () => {
    if (disposed) return
    disposed = true
    resizeObserver.disconnect()
    frameIds.forEach((id) => window.cancelAnimationFrame(id))
    timerIds.forEach((id) => window.clearTimeout(id))
    window.clearTimeout(cleanupTimer)
    settingsBubbleAnchorCleanup = null
  }
}
const lockSettingsBubbleFromEvent = (event: Event) => {
  const target = event.target as Element | null
  const bubble = target?.closest<HTMLElement>('.settings-bubble')
  if (!bubble) return
  const shouldLock = Boolean(target?.closest([
    'button',
    'a',
    'input',
    'textarea',
    'select',
    '[role="button"]',
    '[role="tab"]',
    '[role="menuitem"]',
    '.el-button',
    '.el-dropdown',
    '.el-tabs',
    '.el-collapse',
    '.el-switch',
    '.el-radio',
    '.el-checkbox',
    '.el-select',
    '.el-input',
  ].join(',')))
  if (!shouldLock) return
  lockSettingsBubbleTop(bubble)
}
const waitForSettingsBubbleLayout = (threadId: string) => new Promise<void>((resolve) => {
  const startedAt = Date.now()
  const maxWait = 1600
  const stableDelay = 180
  let lastHeight = -1
  let stableSince = Date.now()
  let frameId = 0
  let observer: MutationObserver | null = null
  let finished = false

  const finish = () => {
    if (finished) return
    finished = true
    if (frameId) window.cancelAnimationFrame(frameId)
    observer?.disconnect()
    resolve()
  }

  const measure = () => {
    const bubble = conversationRef.value?.querySelector<HTMLElement>(`.settings-bubble[data-settings-thread-id="${threadId}"]`)
    if (!bubble) {
      frameId = window.requestAnimationFrame(measure)
      return
    }

    const height = Math.ceil(bubble.scrollHeight)
    const imagesReady = Array.from(bubble.querySelectorAll<HTMLImageElement>('img')).every((image) => image.complete)
    const loadingSettled = !Array
      .from(bubble.querySelectorAll<HTMLElement>('.el-loading-mask'))
      .some((mask) => getComputedStyle(mask).display !== 'none' && getComputedStyle(mask).visibility !== 'hidden')
    const heightChanged = Math.abs(height - lastHeight) > 1
    if (heightChanged) {
      lastHeight = height
      stableSince = Date.now()
    }

    const waited = Date.now() - startedAt
    const stableFor = Date.now() - stableSince
    if ((imagesReady && loadingSettled && stableFor >= stableDelay) || waited >= maxWait) {
      finish()
      return
    }
    frameId = window.requestAnimationFrame(measure)
  }

  window.requestAnimationFrame(() => {
    const bubble = conversationRef.value?.querySelector<HTMLElement>(`.settings-bubble[data-settings-thread-id="${threadId}"]`)
    if (bubble) {
      observer = new MutationObserver(() => {
        stableSince = Date.now()
      })
      observer.observe(bubble, { childList: true, subtree: true, attributes: true, characterData: true })
    }
    measure()
  })
})
const autosizeTextarea = (textarea: HTMLTextAreaElement) => {
  textarea.rows = 1
  textarea.style.height = 'auto'
  textarea.style.overflowY = 'hidden'
  textarea.style.height = `${Math.max(30, textarea.scrollHeight)}px`
}
const autosizeComposerTextarea = async () => {
  await nextTick()
  const textarea = composerInputRef.value
  if (!textarea) return
  const minHeight = hasConversationBlocks.value ? 34 : 44
  const maxHeight = hasConversationBlocks.value ? 104 : 68
  textarea.style.height = 'auto'
  const height = Math.min(Math.max(minHeight, textarea.scrollHeight), maxHeight)
  textarea.style.height = `${height}px`
  textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden'
}
const autosizeSettingsTextareas = async () => {
  await nextTick()
  const panel = conversationRef.value
  if (!panel) return
  panel.querySelectorAll<HTMLTextAreaElement>('.settings-bubble textarea').forEach((textarea) => {
    autosizeTextarea(textarea)
    if (textarea.dataset.zunoAutosize === 'true') return
    textarea.dataset.zunoAutosize = 'true'
    textarea.addEventListener('input', () => autosizeTextarea(textarea))
  })
}
const scheduleSettingsTextareaAutosize = () => {
  if (autosizeFrame) window.cancelAnimationFrame(autosizeFrame)
  autosizeFrame = window.requestAnimationFrame(() => {
    autosizeFrame = 0
    void autosizeSettingsTextareas()
  })
}
const stabilizeConversationViewport = async (forceBottom = false) => {
  await autosizeComposerTextarea()
  await autosizeSettingsTextareas()
  if (hasConversationBlocks.value && (forceBottom || isPinnedToBottom.value)) {
    await scrollToBottom(true, 'auto')
  }
}
const handleViewportResize = () => {
  const shouldKeepLatestTurnVisible = hasConversationBlocks.value && (isPinnedToBottom.value || settingsThreads.value.length > 0)
  if (viewportResizeFrame) window.cancelAnimationFrame(viewportResizeFrame)
  viewportResizeFrame = window.requestAnimationFrame(() => {
    viewportResizeFrame = 0
    void stabilizeConversationViewport(shouldKeepLatestTurnVisible)
  })
  if (viewportResizeTimer) window.clearTimeout(viewportResizeTimer)
  viewportResizeTimer = window.setTimeout(() => {
    viewportResizeTimer = 0
    void stabilizeConversationViewport(shouldKeepLatestTurnVisible)
  }, 160)
}
const ensureSettingsMutationObserver = () => {
  const panel = conversationRef.value
  if (!panel || settingsMutationObserver) return
  settingsMutationObserver = new MutationObserver(() => scheduleSettingsTextareaAutosize())
  settingsMutationObserver.observe(panel, { childList: true, subtree: true })
}
const emitSessionUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-updated', { detail: { sessionId: currentSessionId.value } }))
const emitSessionModeUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-mode-updated', { detail: { sessionId: currentSessionId.value, mode: selectedMode.value } }))
const nextConversationOrder = () => {
  conversationOrder += 1
  return conversationOrder
}
const getSettingsCommand = (label: string, routeName: string, detail = false) => {
  if (routeName === 'workspaceSettingsAgentEditor') return route.query.id ? '编辑智能体' : '创建智能体'
  if (routeName === 'workspaceSettingsKnowledgeFile') return '打开知识库文件'
  if (routeName === 'workspaceSettingsKnowledgeConfig') return '打开知识库参数'
  return detail ? `打开${label}详情` : `打开${label}`
}
const getSettingsSectionCommand = (label: string) => `打开${label}`
const getSettingsPanelTitle = (label: string, routeName: string) => {
  if (routeName === 'workspaceSettingsAgentEditor') return route.query.id ? '编辑智能体' : '创建智能体'
  if (routeName === 'workspaceSettingsKnowledgeFile') return `${route.query.name || '知识库'} · 文件`
  if (routeName === 'workspaceSettingsKnowledgeConfig') return `${route.query.name || '知识库'} · 参数`
  return label
}
const getThreadIcon = (section: string, routeName = '') => {
  if (section === 'conversations' || routeName === 'workspaceAccountConversations') return messageIcon
  if (section === 'profile' || routeName === 'workspaceAccountProfile') return DEFAULT_USER_AVATAR
  return getSettingsIcon(section)
}
const normalizeSettingsCommandText = (value: string) => value
  .trim()
  .replace(/\s+/g, '')
  .replace(/[。.!！?？,，;；:：]/g, '')
  .toLowerCase()
const getSettingsSectionFromLocalCommand = (value: string) => {
  const normalized = normalizeSettingsCommandText(value)
  if (!normalized) return ''
  const commandBody = normalized
    .replace(/^(请|帮我|麻烦|帮忙|给我|我要|我想|想)?(打开|进入|去|切到|切换到|查看|调出|唤起)/, '')
    .replace(/(页面|页|面板|设置|配置|中心)$/, '')
  if (!commandBody) return ''

  const matched = settingsCommandSections.find((item) => item.names.some((name) => {
    const alias = normalizeSettingsCommandText(name)
    return commandBody === alias || commandBody === `${alias}管理`
  }))
  return matched?.section || ''
}
const snapshotSettingsRoute = (): SettingsRouteSnapshot | null => {
  const routeName = String(route.name || '')
  if (!routeName || (!route.meta.settingsSection && !route.meta.accountSection)) return null
  return {
    name: routeName,
    fullPath: route.fullPath,
    params: { ...route.params },
    query: { ...route.query },
  }
}
const appendSettingsThreadFromRoute = async () => {
  if (useTraditionalSettingsShell.value) return
  const section = String(route.meta.settingsSection || route.meta.accountSection || '')
  if (!section) return

  const routeName = String(route.name || '')
  const component = settingsComponentByRouteName[routeName]
  if (!component) return

  const label = settingsLabels[section] || '设置'
  const detail = Boolean(route.meta.settingsDetail)
  const snapshot = snapshotSettingsRoute()
  const requestedThread = pendingSettingsNavigationThreadId
    ? settingsThreads.value.find((thread) => thread.id === pendingSettingsNavigationThreadId)
    : null
  const latestThread = requestedThread || settingsThreads.value[settingsThreads.value.length - 1]
  const previousSnapshot = requestedThread?.routeSnapshot || activeSettingsRouteSnapshot.value
  const canReuseLatestThread = Boolean(
    latestThread
    && previousSnapshot
    && latestThread.section === section
    && (requestedThread || latestThread.routeKey === previousSnapshot.fullPath)
    && (detail || restoringSettingsRoute || requestedThread)
  )
  if (canReuseLatestThread && latestThread) {
    const nextLabel = getSettingsPanelTitle(label, routeName)
    const nextCommand = getSettingsCommand(label, routeName, detail)
    const sectionCommand = getSettingsSectionCommand(label)
    if (
      snapshot
      && previousSnapshot
      && previousSnapshot.fullPath !== snapshot.fullPath
      && !restoringSettingsRoute
      && detail
      && latestThread.history[latestThread.history.length - 1]?.fullPath !== previousSnapshot.fullPath
    ) {
      latestThread.history.push(previousSnapshot)
    }
    latestThread.command = nextCommand
    if (!restoringSettingsRoute && !detail && latestThread.commandTurns.length === 0) {
      latestThread.commandTurns.push({
        id: `${Date.now()}-${latestThread.commandTurns.length}`,
        command: sectionCommand,
      })
    }
    latestThread.label = nextLabel
    latestThread.switching = true
    await nextTick()
    await scrollToBottom(false, 'smooth')
    await wait(shouldReduceMotion() ? 0 : 320)
    if (route.fullPath !== snapshot?.fullPath) return
    latestThread.section = section
    latestThread.icon = getThreadIcon(section, routeName)
    latestThread.component = component
    latestThread.routeName = routeName
    latestThread.routeKey = route.fullPath
    latestThread.routeSnapshot = snapshot
    latestThread.detail = detail
    latestThread.ready = true
    activeSettingsRouteSnapshot.value = snapshot
    pendingSettingsNavigationThreadId = ''
    ensureSettingsMutationObserver()
    await nextTick()
    await autosizeSettingsTextareas()
    await scrollToBottom(false, 'smooth')
    window.setTimeout(() => {
      if (latestThread.routeKey === route.fullPath) {
        latestThread.switching = false
      }
    }, shouldReduceMotion() ? 0 : 260)
    return
  }
  const thread: SettingsThreadItem = {
    id: `${Date.now()}-${settingsThreads.value.length}`,
    order: nextConversationOrder(),
    section,
    label: getSettingsPanelTitle(label, routeName),
    command: getSettingsCommand(label, routeName, detail),
    commandTurns: [{
      id: `${Date.now()}-0`,
      command: getSettingsSectionCommand(label),
    }],
    icon: getThreadIcon(section, routeName),
    component,
    routeName,
    routeKey: route.fullPath,
    routeSnapshot: snapshot,
    detail,
    history: [],
    commandVisible: false,
    assistantVisible: false,
    ready: false,
    switching: false,
  }
  const threadIndex = settingsThreads.value.push(thread) - 1
  activeSettingsRouteSnapshot.value = snapshot
  isPinnedToBottom.value = true
  ensureSettingsMutationObserver()
  try {
    await wait(120)
    const commandThread = settingsThreads.value[threadIndex]
    if (commandThread) commandThread.commandVisible = true
    await scrollToBottom(true, 'smooth')
    await wait(280)
    const assistantThread = settingsThreads.value[threadIndex]
    if (assistantThread) assistantThread.assistantVisible = true
    await scrollToBottom(true, 'smooth')
    await wait(120)
    await nextTick()
    await waitForSettingsBubbleLayout(thread.id)
    await autosizeSettingsTextareas()
  } finally {
    const currentThread = settingsThreads.value[threadIndex]
    if (currentThread) currentThread.ready = true
    pendingSettingsNavigationThreadId = ''
    await nextTick()
    await scrollToBottom(true, 'smooth')
  }
}
const expandComposer = async () => {
  composerExpanded.value = true
  composerFocused.value = true
  await nextTick()
  await autosizeComposerTextarea()
  composerInputRef.value?.focus()
}
const handleComposerFocus = () => {
  composerExpanded.value = true
  composerFocused.value = true
}
const handleComposerFocusOut = (event: FocusEvent) => {
  const currentTarget = event.currentTarget as HTMLElement | null
  const nextTarget = event.relatedTarget as Node | null
  if (currentTarget && nextTarget && currentTarget.contains(nextTarget)) return
  composerFocused.value = false
  window.setTimeout(() => {
    if (canCollapseComposer.value) composerExpanded.value = false
  }, 80)
}
const handleIntroPetClick = async () => {
  pulsePetMood('wake', 900)
  await nextTick()
  composerExpanded.value = true
  composerFocused.value = true
  composerInputRef.value?.focus()
}
const handleSettingsNavigateRequest = async (event: Event) => {
  const detail = (event as CustomEvent<{ location?: RouteLocationRaw; threadId?: string }>).detail
  if (!detail?.location) return
  pendingSettingsNavigationThreadId = detail.threadId || ''
  try {
    await router.push(detail.location)
  } catch (error) {
    pendingSettingsNavigationThreadId = ''
    throw error
  }
}
const canNavigateSettingsThreadBack = (thread: SettingsThreadItem) => thread.detail
const handleSettingsThreadBack = async (thread: SettingsThreadItem) => {
  const fallbackRouteName = settingsRouteBySection[thread.section] || 'workspaceSettingsAgent'
  thread.history = []
  pendingSettingsNavigationThreadId = thread.id
  try {
    await router.push({
      name: fallbackRouteName,
      query: { ...route.query, settings_turn: String(Date.now()) },
    })
  } catch (error) {
    pendingSettingsNavigationThreadId = ''
    throw error
  }
}
const resetRuntimeSurface = () => {
  activeRuntimeTaskId.value = ''
  activeRuntimeArtifact.value = null
  activeRuntimeCitationIds.value = []
  activeRuntimeObservability.value = null
  runtimeFailure.value = null
  feedbackSubmitting.value = false
  feedbackSent.value = false
  runtimeFeedbackLabel.value = ''
}
const clearConversationState = (options?: { keepSessionHistoryLoading?: boolean }) => {
  inputMessage.value = ''
  clearMessageMotionTimers()
  messages.value = []
  settingsThreads.value = []
  activeAssistantMessageIndex.value = -1
  assistantTextStreaming.value = false
  activeSettingsRouteSnapshot.value = null
  conversationOrder = 0
  composerExpanded.value = false
  composerFocused.value = false
  clearTransientPetMood()
  executionEvents.value = []
  pendingToolApproval.value = null
  toolApprovalSubmitting.value = false
  resetRuntimeSurface()
  pendingAttachments.value = []
  attachmentsUploading.value = false
  isGenerating.value = false
  showTracePanel.value = false
  isPinnedToBottom.value = true
  consumedInitialMessageKey.value = ''
  initialRouteMessageInFlightKey.value = ''
  if (!options?.keepSessionHistoryLoading) {
    sessionHistoryLoading.value = false
    sessionHistoryLoadToken = ''
  }
}
const isCurrentSessionDisposable = () => (
  Boolean(currentSessionId.value)
  && messages.value.length === 0
  && executionEvents.value.length === 0
  && !pendingToolApproval.value
  && pendingAttachments.value.length === 0
)

const buildWorkspaceQuery = () => ({
  ...(currentSessionId.value ? { session_id: currentSessionId.value } : {}),
  mode: selectedMode.value,
  execution_mode: selectedExecutionMode.value,
  access_scope: selectedAccessScope.value,
  ...(activeAgentName.value ? { agent_name: activeAgentName.value } : {}),
  ...(activeAgentId.value ? { agent_id: activeAgentId.value } : {}),
})

const syncRouteState = async (options?: { preserveConversation?: boolean }) => {
  if (options?.preserveConversation) preserveConversationOnRouteSync.value = true
  try {
    await router.replace({ name: 'workspaceDefaultPage', query: buildWorkspaceQuery() })
    await nextTick()
  } finally {
    if (options?.preserveConversation) preserveConversationOnRouteSync.value = false
  }
}

const resetToDraftSession = async (mode: WorkspaceMode, options?: { pruneCurrent?: boolean; agentName?: string; agentId?: string }) => {
  const pruneCurrent = options?.pruneCurrent !== false
  const disposableSessionId = pruneCurrent && isCurrentSessionDisposable() ? currentSessionId.value : ''
  clearConversationState()
  selectedMode.value = mode
  activeAgentName.value = mode === 'agent' ? String(options?.agentName || activeAgentName.value || '').trim() : ''
  activeAgentId.value = mode === 'agent' ? String(options?.agentId || activeAgentId.value || '').trim() : ''
  currentSessionId.value = ''
  try {
    if (disposableSessionId) {
      await deleteWorkspaceSessionAPI(disposableSessionId)
    }
  } catch (error) {
    console.warn('清理空会话失败', error)
  }
  await syncRouteState()
  emitSessionUpdated()
}

const createPersistedSession = async (mode: WorkspaceMode) => {
  selectedMode.value = mode
  const agentName = mode === 'agent' ? activeAgentName.value.trim() : ''
  const response = await createWorkspaceSessionAPI({
    title: '新对话',
    workspace_mode: mode,
    agent: agentName || mode,
    contexts: [],
  })
  if (response.data?.status_code !== 200 || !response.data?.data?.session_id) {
    throw new Error('create_session_failed')
  }
  currentSessionId.value = String(response.data.data.session_id)
  saveWorkspaceSessionMode(currentSessionId.value, mode)
  emitSessionUpdated()
  emitSessionModeUpdated()
}

const startFreshConversation = async (detail?: NewConversationDetail) => {
  const defaults = loadWorkspaceDefaults()
  const nextMode = detail?.mode === 'agent' ? 'agent' : 'normal'
  selectedExecutionMode.value = defaults.executionMode || selectedExecutionMode.value
  selectedAccessScope.value = defaults.accessScope || selectedAccessScope.value
  if (defaults.modelId && modelOptions.value.some((model) => model.llm_id === defaults.modelId)) selectedModelId.value = defaults.modelId
  await resetToDraftSession(nextMode || defaults.mode || selectedMode.value, {
    agentName: detail?.agentName,
    agentId: detail?.agentId,
  })
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
}
const handleNewConversationRequest = async (event?: Event) => {
  if (isGenerating.value) {
    ElMessage.warning('请等待当前回复完成后再新建会话。')
    return
  }
  try {
    const detail = (event as CustomEvent<NewConversationDetail> | undefined)?.detail
    await startFreshConversation(detail)
  } catch (error) {
    console.error('新建会话失败', error)
    ElMessage.error('新建会话失败')
  }
}

const normalizeAgentAvatar = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/')) return zunoAgentAvatar
  return withUserAvatarVersion(raw)
}

const normalizeAgentOption = (agent: AgentResponse): AgentOption => ({
  id: String(agent.agent_id || agent.id || agent.name || '').trim(),
  name: String(agent.name || '未命名智能体').trim(),
  description: String(agent.description || '暂无描述').trim(),
  avatar: normalizeAgentAvatar(agent.logo_url),
})

const fetchAgentOptions = async () => {
  try {
    agentPickerLoading.value = true
    const response = await getAgentsAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '获取 Agent 失败')
    }
    agentOptions.value = (response.data.data || [])
      .map(normalizeAgentOption)
      .filter((agent) => Boolean(agent.id))
  } catch (error) {
    console.error('获取 Agent 失败', error)
    agentOptions.value = []
  } finally {
    agentPickerLoading.value = false
  }
}

const openAgentPicker = async () => {
  if (isGenerating.value) return
  agentPickerOpen.value = !agentPickerOpen.value
  if (!agentPickerOpen.value) return
  pulsePetMood('listening', 900)
  await fetchAgentOptions()
}

const handleAgentPickerPointerDown = (event: PointerEvent) => {
  if (!agentPickerOpen.value) return
  const target = event.target as Element | null
  if (target?.closest('.mode-switcher')) return
  agentPickerOpen.value = false
}

const selectAgentOption = async (agent: AgentOption) => {
  if (isGenerating.value) return
  agentPickerOpen.value = false
  await resetToDraftSession('agent', {
    pruneCurrent: false,
    agentName: agent.name,
    agentId: agent.id,
  })
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
  pulsePetMood('success', 1100)
}
const handleAgentOptionAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement | null
  if (target) target.src = zunoAgentAvatar
}
const getRetrievalTriggerLabel = (trigger: string) => {
  if (trigger === 'route_broadening') return '自动扩路补检'
  if (trigger === 'query_rewrite_retry') return '改写后重试'
  if (trigger === 'initial') return '首轮检索'
  return trigger || '检索'
}
const getQualityReasonLabel = (reason: string) => {
  if (reason === 'empty_result') return '结果为空'
  if (reason === 'graph_result_empty') return '图谱结果为空'
  if (reason === 'too_few_documents') return '召回片段过少'
  if (reason === 'low_rerank_score') return '重排分数过低'
  if (reason === 'no_relevant_documents') return '没有相关文档'
  return reason || ''
}
const buildRetrievalTrace = (data: Record<string, any>, retrievalMode: string): RetrievalTraceSummary | null => {
  const rounds = Array.isArray(data.rounds) ? data.rounds : []
  const firstMode = String(data.first_mode || retrievalMode || '').trim()
  const finalMode = String(data.final_mode || retrievalMode || '').trim()
  const fallbackReason = String(data.fallback_reason || '').trim()
  const roundCount = Number(data.round_count || rounds.length || 0)
  const rewrittenQueryUsed = Boolean(data.rewritten_query_used)
  if (!firstMode && !finalMode && !roundCount && !fallbackReason && rounds.length === 0)
    return null
  return {
    firstMode: firstMode || finalMode || retrievalMode || 'rag',
    finalMode: finalMode || firstMode || retrievalMode || 'rag',
    roundCount: roundCount || Math.max(rounds.length, 1),
    fallbackReason,
    rewrittenQueryUsed,
    rounds: rounds.map((item: any, index: number) => ({
      round: Number(item?.round || index + 1),
      mode: String(item?.mode || finalMode || retrievalMode || 'rag'),
      trigger: String(item?.trigger || ''),
      qualityReason: String(item?.quality_reason || ''),
      query: String(item?.query || ''),
    })),
  }
}
const buildRetrievalTraceDetail = (data: Record<string, any>, retrievalMode: string) => {
  const retrieval = buildRetrievalTrace(data, retrievalMode)
  if (!retrieval) return ''
  const routeSummary = retrieval.firstMode && retrieval.finalMode && retrieval.firstMode !== retrieval.finalMode
    ? `首轮 ${getRetrievalModeLabel(retrieval.firstMode)}，最终切到 ${getRetrievalModeLabel(retrieval.finalMode)}`
    : `检索策略：${getRetrievalModeLabel(retrieval.finalMode || retrievalMode)}`
  const parts = [`${routeSummary}，共 ${retrieval.roundCount} 轮。`]
  if (retrieval.fallbackReason) parts.push(`补检原因：${retrieval.fallbackReason}。`)
  if (retrieval.rewrittenQueryUsed) parts.push('已启用改写后的问题再次检索。')
  const lastRound = retrieval.rounds[retrieval.rounds.length - 1]
  if (lastRound?.trigger === 'query_rewrite_retry') {
    parts.push('最后一轮来自改写后重试。')
  } else if (lastRound?.trigger === 'route_broadening') {
    parts.push('最后一轮来自自动扩路补检。')
  }
  return parts.join('')
}
const normalizeStringList = (value: unknown): string[] => {
  if (Array.isArray(value)) return value.map((item) => String(item || '').trim()).filter(Boolean)
  if (typeof value === 'string' && value.trim()) return [value.trim()]
  return []
}
const mergeRuntimeCitationIds = (ids: string[]) => {
  const merged = Array.from(new Set([...activeRuntimeCitationIds.value, ...ids].filter(Boolean)))
  activeRuntimeCitationIds.value = merged
  if (activeRuntimeArtifact.value) {
    activeRuntimeArtifact.value = {
      ...activeRuntimeArtifact.value,
      citations: Array.from(new Set([...activeRuntimeArtifact.value.citations, ...merged])),
    }
  }
}
const buildEvalDiagnosticDetail = (data: Record<string, any>) => {
  const releaseEval = data.release_eval || data.eval || data
  const status = String(releaseEval.status || releaseEval.overall_status || releaseEval.verdict || data.status || 'unknown')
  const metrics = Array.isArray(releaseEval.metrics)
    ? releaseEval.metrics
    : Object.entries(releaseEval.metrics || {}).map(([name, value]) => ({ name, value }))
  const metricCopy = metrics
    .slice(0, 3)
    .map((metric: any) => `${metric.name || metric.metric || 'metric'}=${metric.value ?? metric.score ?? metric.status ?? ''}`.replace(/=$/, ''))
    .filter(Boolean)
    .join('，')
  return metricCopy ? `release_eval=${status}；${metricCopy}` : `release_eval=${status}`
}
const captureRuntimeEventSurface = (event: WorkspaceStreamEvent) => {
  const data = event.data || {}
  const citationIds = normalizeStringList(event.citation_ids || data.citation_ids)
  if (citationIds.length > 0) mergeRuntimeCitationIds(citationIds)
  const artifactId = String(event.artifact_id || data.artifact_id || '')
  if (artifactId && !activeRuntimeArtifact.value) {
    activeRuntimeArtifact.value = {
      artifactId,
      content: '',
      citations: citationIds,
      uri: '',
    }
  }
  const failed = event.type === 'task_failed'
    || String(data.status || '').toLowerCase() === 'failed'
    || String(data.phase || '').toLowerCase().includes('failed')
  if (failed) {
    runtimeFailure.value = {
      title: '任务失败',
      detail: String(data.error || data.message || event.detail || '任务未能完成。'),
    }
  }
}

const buildTraceRecord = (event: WorkspaceStreamEvent): TraceRecord => {
  const data = event.data || {}
  const phase = String(data.phase || '')
  const status = String(data.status || '')
  const retrievalMode = String(data.retrieval_mode || effectiveRetrievalMode.value || '')
  const retrieval = buildRetrievalTrace(data, retrievalMode)
  const toolName = String(data.tool_name || '')
  const toolResult = String(data.result || data.message || '')
  const artifactId = String(event.artifact_id || data.artifact_id || '')
  const citationIds = normalizeStringList(event.citation_ids || data.citation_ids)
  const sourceRefs = normalizeStringList(data.source_refs || data.source_event_ids)
  const isToolCreation = event.type === 'tool_result' && ['create_remote_api_tool', 'create_cli_tool'].includes(toolName)
  if (event.type === 'approval_required') {
    return {
      id: event.id || crypto.randomUUID(),
      title: '等待工具审批',
      detail: String(data.tool_id || event.tool_id || data.required_approval || event.required_approval || '需要确认后继续执行'),
      at: new Date().toLocaleTimeString(),
      phase: phase || 'approval',
      status: status || 'approval_waiting',
      accent: 'tool',
      retrieval,
    }
  }
  if (event.type === 'security_gate') {
    const decision = String(data.action || data.decision?.action || status || 'review')
    const blocked = ['block', 'blocked', 'failed', 'deny'].some((token) => decision.toLowerCase().includes(token))
    return {
      id: event.id || crypto.randomUUID(),
      title: blocked ? '安全策略已阻断' : '安全检查通过',
      detail: String(data.message || data.reason || event.detail || decision),
      at: new Date().toLocaleTimeString(),
      phase: phase || 'security_gate',
      status: status || decision,
      accent: blocked ? 'error' : 'tool',
      retrieval,
      sourceRefs,
    }
  }
  if (event.type === 'eval_diagnostic') {
    return {
      id: event.id || crypto.randomUUID(),
      title: '评测诊断',
      detail: buildEvalDiagnosticDetail(data),
      at: new Date().toLocaleTimeString(),
      phase: phase || 'eval_diagnostic',
      status,
      accent: String(data.status || '').toLowerCase().includes('fail') ? 'error' : 'answer',
      retrieval,
      sourceRefs,
    }
  }
  if (event.type === 'artifact_created') {
    return {
      id: event.id || crypto.randomUUID(),
      title: 'Artifact 已创建',
      detail: artifactId ? `artifact_id=${artifactId}` : '任务产物已生成。',
      at: new Date().toLocaleTimeString(),
      phase: phase || 'artifact',
      status: status || 'created',
      accent: 'answer',
      retrieval,
      artifactId,
      citationIds,
      sourceRefs,
    }
  }
  if (event.type === 'task_failed') {
    return {
      id: event.id || crypto.randomUUID(),
      title: '任务失败',
      detail: String(data.error || data.message || event.detail || '任务未能完成。'),
      at: new Date().toLocaleTimeString(),
      phase: phase || 'failed',
      status: status || 'failed',
      accent: 'error',
      retrieval,
      sourceRefs,
    }
  }
  if (event.type === 'task_completed') {
    return {
      id: event.id || crypto.randomUUID(),
      title: '任务完成',
      detail: artifactId ? `已生成 artifact：${artifactId}` : String(data.message || '完整 task runtime 已完成。'),
      at: new Date().toLocaleTimeString(),
      phase: phase || 'complete',
      status: status || 'completed',
      accent: 'answer',
      retrieval,
      artifactId,
      citationIds,
      sourceRefs,
    }
  }
  if (event.type === 'tool_call') {
    return { id: event.id || crypto.randomUUID(), title: '正在调用工具', detail: String(data.tool_id || data.tool_name || data.message || '正在执行外部能力'), at: new Date().toLocaleTimeString(), phase, status, accent: 'tool', retrieval }
  }
  if (event.type === 'tool_result') {
    const failed = data.ok === false
    return {
      id: event.id || crypto.randomUUID(),
      title: isToolCreation
        ? (
            failed
              ? (toolName === 'create_remote_api_tool' ? '创建 API 工具失败' : '创建 CLI 工具失败')
              : (toolName === 'create_remote_api_tool' ? '已创建 API 工具' : '已创建 CLI 工具')
          )
        : '工具已返回结果',
      detail: isToolCreation
        ? toolResult
        : String(data.tool_name || data.message || '已收到工具结果'),
      at: new Date().toLocaleTimeString(),
      phase,
      status,
      accent: data.ok === false ? 'error' : 'tool',
      retrieval,
    }
  }
  if (event.type === 'final') {
    return { id: event.id || crypto.randomUUID(), title: '正在整理最终回复', detail: `${buildRetrievalTraceDetail(data, retrievalMode)} 正在生成最终答案。`, at: new Date().toLocaleTimeString(), phase: phase || 'answer', status, accent: 'answer', retrieval }
  }
  const accent = phase.includes('error')
    ? 'error'
    : retrievalMode === 'graphrag'
      ? 'graph'
      : retrievalMode === 'hybrid' || retrievalMode === 'auto' || retrievalMode === 'rag'
        ? 'retrieval'
        : 'default'
  return {
    id: event.id || crypto.randomUUID(),
    title: String(data.message || event.title || '正在处理中'),
    detail: String(
      data.result
      || data.error
      || data.tool_name
      || event.detail
      || (
        retrievalMode
          ? buildRetrievalTraceDetail(data, retrievalMode)
          : ''
      )
    ),
    at: new Date().toLocaleTimeString(),
    phase,
    status,
    accent,
    retrieval,
    artifactId,
    citationIds,
    sourceRefs,
  }
}
const pushTraceEvent = (event: WorkspaceStreamEvent) => {
  captureRuntimeEventSurface(event)
  const nextRecord = buildTraceRecord(event)
  const lastRecord = executionEvents.value[executionEvents.value.length - 1]
  if (lastRecord && lastRecord.title === nextRecord.title && lastRecord.detail === nextRecord.detail) return
  executionEvents.value.push(nextRecord)
  if (executionEvents.value.length > 24) executionEvents.value.splice(0, executionEvents.value.length - 24)
}

const capturePendingToolApproval = (event: WorkspaceStreamEvent) => {
  if (event.type !== 'approval_required') return
  const data = event.data || {}
  const taskId = String(event.task_id || data.task_id || '')
  const requiredApproval = String(event.required_approval || data.required_approval || '')
  const toolId = String(event.tool_id || data.tool_id || requiredApproval.replace(/^tool:/, ''))
  if (!taskId || !requiredApproval.startsWith('tool:')) return
  pendingToolApproval.value = {
    taskId,
    toolId,
    requiredApproval,
    approvalId: String(event.approval_id || data.approval_id || requiredApproval),
    toolCallId: String(event.tool_call_id || data.tool_call_id || toolId),
    auditRef: String(event.audit_ref || data.audit_ref || ''),
  }
  isGenerating.value = false
  assistantTextStreaming.value = false
}

const unwrapWorkspaceTaskResponse = (response: any): WorkspaceTaskCreateResponse | null => (
  response?.data?.data || response?.data || response || null
)
const unwrapWorkspaceArtifactResponse = (response: any): WorkspaceArtifactResponse | null => (
  response?.data?.data || response?.data || response || null
)
const normalizeRuntimeSlug = (value: string, prefix: string) => {
  const slug = value
    .trim()
    .replace(/[^a-zA-Z0-9_-]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .replace(/_+/g, '_')
    .slice(0, 72)
  return `${prefix}_${slug || crypto.randomUUID()}`
}
const buildRuntimeAttachmentContent = (attachment: PendingAttachment, query: string) => [
  `# ${attachment.name}`,
  '',
  `用户任务：${query}`,
  `文件名：${attachment.name}`,
  `MIME：${attachment.mime_type || 'application/octet-stream'}`,
  `大小：${formatAttachmentSize(attachment.size || 0)}`,
  `来源：${attachment.url}`,
  '',
  '该内容由 Web workspace 注册给 Parse Gateway。后端 ingestion runtime 会继续保留 file uri、provenance、index handoff 和 citation 证据链。',
].join('\n')
const registerRuntimeAttachments = async (workspaceId: string, query: string, attachmentsForRequest: PendingAttachment[]) => {
  const registered: Array<{ fileId: string; knowledgeSpaceId: string }> = []
  for (const attachment of attachmentsForRequest) {
    const fileId = normalizeRuntimeSlug(attachment.id || attachment.name || Date.now().toString(), 'web_file')
    const knowledgeSpaceId = normalizeRuntimeSlug(`${fileId}_ks`, 'ks')
    await createWorkspaceFileAPI({
      workspace_id: workspaceId,
      file_id: fileId,
      name: attachment.name,
      mime_type: attachment.mime_type || 'application/octet-stream',
      uri: attachment.url,
      content: buildRuntimeAttachmentContent(attachment, query),
      security_label: 'workspace-upload',
    })
    await createWorkspaceIngestAPI({
      workspace_id: workspaceId,
      file_id: fileId,
      knowledge_space_id: knowledgeSpaceId,
      session_id: currentSessionId.value,
    })
    registered.push({ fileId, knowledgeSpaceId })
  }
  return registered
}
const buildRuntimeAssistantMessage = () => {
  if (runtimeFailure.value) return `**${runtimeFailure.value.title}**\n\n${runtimeFailure.value.detail}`
  if (activeRuntimeArtifact.value?.content) return activeRuntimeArtifact.value.content
  return buildLiveAssistantProgress()
}
const loadWorkspaceArtifact = async (artifactId: string, assistantIndex = -1) => {
  if (!artifactId) return
  const response = await getWorkspaceArtifactAPI(artifactId)
  const data = unwrapWorkspaceArtifactResponse(response)
  const artifact = data?.artifact
  const content = String(data?.content || '')
  activeRuntimeArtifact.value = {
    artifactId,
    content,
    citations: activeRuntimeCitationIds.value,
    uri: String(artifact?.uri || ''),
  }
  if (content && assistantIndex >= 0 && messages.value[assistantIndex]) {
    messages.value[assistantIndex].content = content
    assistantTextStreaming.value = false
    setMessageMotion(messages.value[assistantIndex], 'complete', 1100)
    await scrollToBottom()
  }
}
const applyWorkspaceTaskSnapshot = async (snapshot: WorkspaceTaskCreateResponse | null, assistantIndex = -1) => {
  if (!snapshot?.task) return
  activeRuntimeTaskId.value = snapshot.task.task_id
  if (snapshot.observability) activeRuntimeObservability.value = snapshot.observability
  const runtimeEvents = Array.isArray(snapshot.runtime?.events) ? snapshot.runtime?.events || [] : []
  const runtimeCitationIds = runtimeEvents.flatMap((event: any) => normalizeStringList(event?.citation_ids || event?.payload?.citation_ids))
  if (runtimeCitationIds.length > 0) mergeRuntimeCitationIds(runtimeCitationIds)
  const artifactIds = [
    ...normalizeStringList(snapshot.artifact_ids),
    ...(snapshot.artifacts || []).map((artifact) => artifact.artifact_id).filter(Boolean),
  ]
  if (artifactIds[0]) await loadWorkspaceArtifact(artifactIds[0], assistantIndex)
  const status = String(snapshot.task.status || snapshot.runtime?.status || '').toLowerCase()
  const failure = snapshot.runtime?.failure || snapshot.runtime?.state?.failure
  if (status === 'failed' || status === 'cancelled' || failure) {
    runtimeFailure.value = {
      title: status === 'cancelled' ? '任务已取消' : '任务失败',
      detail: String(failure?.message || failure?.reason || failure?.error || '任务未能完成。'),
    }
    if (assistantIndex >= 0 && messages.value[assistantIndex] && !activeRuntimeArtifact.value?.content) {
      messages.value[assistantIndex].content = buildRuntimeAssistantMessage()
      setMessageMotion(messages.value[assistantIndex], 'error', 1800)
      await scrollToBottom()
    }
  }
}
const streamWorkspaceTaskEvents = async (taskId: string, assistantIndex: number, renderAgentProgress: () => Promise<void>) => {
  let streamError: any = null
  await workspaceTaskEventsStreamAPI(taskId, {
    onEvent: (event) => {
      pushTraceEvent(event)
      capturePendingToolApproval(event)
      void refreshToolSelectionsAfterCreation(event)
      void renderAgentProgress()
    },
    onError: (error) => {
      streamError = error
    },
  })
  if (streamError) throw streamError
  const response = await getWorkspaceTaskAPI(taskId)
  await applyWorkspaceTaskSnapshot(unwrapWorkspaceTaskResponse(response), assistantIndex)
}
const submitWorkspaceFeedback = async (label: 'helpful' | 'needs_revision') => {
  if (!activeRuntimeTaskId.value || feedbackSubmitting.value) return
  feedbackSubmitting.value = true
  try {
    await createWorkspaceFeedbackAPI({
      task_id: activeRuntimeTaskId.value,
      rating: label === 'helpful' ? 5 : 2,
      label,
      comment: label === 'helpful' ? 'Workspace user marked the artifact as useful.' : 'Workspace user requested revision.',
      dataset_candidate: label !== 'helpful',
    })
    feedbackSent.value = true
    runtimeFeedbackLabel.value = label
    executionEvents.value.push({
      id: crypto.randomUUID(),
      title: '反馈已记录',
      detail: label === 'helpful' ? '这次 artifact 已记录为可用样本。' : '这次 artifact 已记录为需要调整。',
      at: new Date().toLocaleTimeString(),
      phase: 'feedback',
      status: 'submitted',
      accent: 'answer',
    })
    ElMessage.success('反馈已提交。')
  } catch (error) {
    console.error('反馈提交失败', error)
    ElMessage.error('反馈提交失败，请稍后重试')
  } finally {
    feedbackSubmitting.value = false
  }
}

const submitToolApproval = async (decision: 'approved' | 'rejected') => {
  const pending = pendingToolApproval.value
  if (!pending || toolApprovalSubmitting.value) return
  toolApprovalSubmitting.value = true
  try {
    const response = await approveWorkspaceTaskAPI(pending.taskId, {
      decision,
      comment: decision === 'approved' ? 'Approved from workspace approval panel.' : 'Rejected from workspace approval panel.',
      approval_id: pending.approvalId,
      tool_call_id: pending.toolCallId,
      required_approval: pending.requiredApproval,
    })
    pendingToolApproval.value = null
    ElMessage.success(decision === 'approved' ? '工具调用已批准。' : '工具调用已拒绝。')
    const taskSnapshot = unwrapWorkspaceTaskResponse(response)
    await applyWorkspaceTaskSnapshot(taskSnapshot, activeAssistantMessageIndex.value)
    const task = taskSnapshot?.task
    if (task?.status === 'completed') {
      executionEvents.value.push({
        id: crypto.randomUUID(),
        title: '工具审批已处理',
        detail: `${pending.toolId} 已继续执行。`,
        at: new Date().toLocaleTimeString(),
        phase: 'approval',
        status: 'completed',
        accent: 'tool',
      })
    }
  } catch (error) {
    console.error('工具审批失败', error)
    ElMessage.error('工具审批失败，请稍后重试')
  } finally {
    toolApprovalSubmitting.value = false
  }
}

const parseCreatedToolId = (text: string) => {
  const matched = text.match(/\(tool_id=([^)]+)\)/)
  return matched?.[1] || ''
}

const refreshToolSelectionsAfterCreation = async (event: WorkspaceStreamEvent) => {
  const data = event.data || {}
  const toolName = String(data.tool_name || '')
  if (event.type !== 'tool_result' || data.ok === false) return
  if (!['create_remote_api_tool', 'create_cli_tool'].includes(toolName)) return
  if (!canPickTools.value) return
  await fetchPlugins()
  const createdToolId = parseCreatedToolId(String(data.result || data.message || ''))
  if (createdToolId && !selectedTools.value.includes(createdToolId)) selectedTools.value.push(createdToolId)
  ElMessage.success(toolName === 'create_remote_api_tool' ? 'API 工具已创建并刷新到当前工具列表。' : 'CLI 工具已创建并刷新到当前工具列表。')
}

const buildLiveAssistantProgress = () => {
  const summary = [
    `**${progressHeadline.value || '正在处理中'}**`,
    progressDetail.value || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value} / ${effectiveRetrievalModeLabel.value}`,
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

const buildChatErrorMessage = (raw: string) => {
  const text = String(raw || '').trim()
  if (!text) return '这次请求没有成功完成，请稍后再试。'

  const unsupportedModel = text.match(/Not supported model\s+([^'",}]+)/i)
  if (unsupportedModel?.[1]) {
    return `模型接口不支持当前模型 ID「${unsupportedModel[1].trim()}」。请在模型设置里填写接口实际使用的 model id，例如小米 Token Plan 通常使用 mimo-v2.5 或 mimo-v2.5-pro。`
  }

  return `这次请求没有成功完成。后端返回的错误是：${text}`
}

const buildMissingModelMessage = () => [
  '我现在还没找到可用的聊天模型。',
  '',
  '先在 Settings 里添加一个 LLM，再回来继续这句就行。也可以直接输入「打开模型管理」。',
].join('\n')
const buildFallbackAssistantMessage = () => [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.detail || [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.title || '这次请求没有返回可见内容，请稍后重试。'
const applySlashSuggestion = (suggestion: SlashSuggestion) => {
  inputMessage.value = suggestion.insertValue
  activeSuggestionIndex.value = 0
}

const waitForRetry = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms))

const ensureInitialRouteDependencies = async () => {
  const initialMessage = safeQueryValue(route.query.message, '').trim()
  if (!initialMessage)
    return true

  let attempt = 0
  while (attempt < 4) {
    attempt += 1

    if (!selectedModelId.value) {
      await fetchModels()
    }
    if (executionModes.value.length === 0 || accessScopes.value.length === 0) {
      await fetchExecutionConfig()
    }
    if (mcpServers.value.length === 0) {
      await fetchMcpServers()
    }

    const ready = Boolean(selectedModelId.value)
      && executionModes.value.length > 0
      && accessScopes.value.length > 0
      && mcpServers.value.length > 0
    if (ready)
      return true

    await waitForRetry(300 * attempt)
  }

  return false
}

const consumeInitialRouteMessage = async () => {
  const initialMessage = safeQueryValue(route.query.message, '').trim()
  if (!initialMessage || isGenerating.value)
    return

  const dependenciesReady = await ensureInitialRouteDependencies()
  if (!dependenciesReady || !selectedModelId.value)
    return

  const routeSessionId = safeQueryValue(route.query.session_id, 'new')
  const messageKey = `${routeSessionId}|${selectedMode.value}|${initialMessage}`
  if (consumedInitialMessageKey.value === messageKey)
    return
  if (initialRouteMessageInFlightKey.value === messageKey)
    return

  initialRouteMessageInFlightKey.value = messageKey
  try {
    inputMessage.value = initialMessage
    const submitted = await submitMessage()
    if (!submitted) return
    consumedInitialMessageKey.value = messageKey
    inputMessage.value = ''
  } finally {
    if (initialRouteMessageInFlightKey.value === messageKey) {
      initialRouteMessageInFlightKey.value = ''
    }
  }
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
    if (selectedModelId.value && !modelOptions.value.some((model) => model.llm_id === selectedModelId.value)) selectedModelId.value = ''
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
  const loadToken = `${sessionId}-${Date.now()}-${Math.random()}`
  sessionHistoryLoadToken = loadToken
  sessionHistoryLabel.value = '正在打开对话'
  sessionHistoryLoading.value = true
  try {
    clearConversationState({ keepSessionHistoryLoading: true })
    const response = await getWorkspaceSessionInfoAPI(sessionId)
    if (sessionHistoryLoadToken !== loadToken) return
    if (response.data.status_code !== 200) return
    const session = response.data.data
    const sessionMode = normalizeSessionMode(session)
    selectedMode.value = sessionMode
    activeAgentName.value = sessionMode === 'agent' ? normalizeSessionAgentName(session) : ''
    if (!session?.contexts || !Array.isArray(session.contexts)) return
    const contexts = sanitizeWorkspaceContexts(session.contexts)
    messages.value = contexts
      .map((context: any) => [{ role: 'user' as const, content: context.query || '' }, { role: 'assistant' as const, content: context.answer || '' }])
      .flat()
      .filter((message: ChatMessage) => message.content)
      .map((message: ChatMessage) => ({ ...message, uiOrder: nextConversationOrder() }))
    executionEvents.value = []
    await scrollToBottom(true)
  } catch (error) {
    if (sessionHistoryLoadToken === loadToken) {
      console.error('加载会话历史失败', error)
      ElMessage.error('加载会话历史失败')
    }
  } finally {
    if (sessionHistoryLoadToken === loadToken) {
      sessionHistoryLoading.value = false
    }
  }
}

const syncDefaultSelections = () => {
  if (!isAgentMode.value || !canPickTools.value) return

  const defaults = loadWorkspaceDefaults()
  const hasSavedDefaults = Boolean(defaults.updatedAt)
  const availableToolIds = plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean)
  const availableMcpIds = mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean)
  const availableSkillIds = skillOptions.value.map((item) => item.id).filter(Boolean)
  const availableKnowledgeIds = knowledgeOptions.value.map((item) => item.id).filter(Boolean)

  if (hasSavedDefaults) {
    selectedTools.value = defaults.toolIds.filter((toolId) => availableToolIds.includes(toolId))
    selectedMcpServers.value = defaults.mcpServerIds.filter((serverId) => availableMcpIds.includes(serverId))
    selectedSkillIds.value = defaults.skillIds.filter((skillId) => availableSkillIds.includes(skillId))
    selectedKnowledgeIds.value = defaults.knowledgeIds
      .filter((knowledgeId) => availableKnowledgeIds.includes(knowledgeId))
      .slice(0, 1)
    toolsTouched.value = true
    mcpTouched.value = true
    skillsTouched.value = true
    knowledgeTouched.value = true
    return
  }

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
    selectedKnowledgeIds.value = selectedKnowledgeIds.value
      .filter((knowledgeId) => availableKnowledgeIds.includes(knowledgeId))
      .slice(0, 1)
  }
}

const applySavedWorkspaceDefaults = () => {
  const defaults = loadWorkspaceDefaults()
  if (!defaults.updatedAt) return

  if (!route.query.mode) {
    selectedMode.value = defaults.mode
  }

  if (defaults.modelId && modelOptions.value.some((model) => model.llm_id === defaults.modelId)) {
    selectedModelId.value = defaults.modelId
  }
  if (defaults.executionMode && executionModes.value.some((mode) => mode.id === defaults.executionMode)) {
    selectedExecutionMode.value = defaults.executionMode
  }
  if (defaults.accessScope && accessScopes.value.some((scope) => scope.id === defaults.accessScope)) {
    selectedAccessScope.value = defaults.accessScope
  }

  syncDefaultSelections()
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
  selectedKnowledgeIds.value = selectedKnowledgeIds.value[0] === knowledgeId ? [] : [knowledgeId]
}

const getValidSelectedToolIds = () => {
  const availableToolIds = new Set(plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean))
  return selectedTools.value.filter((toolId) => availableToolIds.has(toolId))
}

const getValidSelectedMcpIds = () => {
  const availableMcpIds = new Set(mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean))
  return selectedMcpServers.value.filter((serverId) => availableMcpIds.has(serverId))
}

const getValidAutoMcpIds = () => {
  const availableMcpIds = new Set(mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean))
  return autoAvailableMcpIds.value.filter((serverId) => availableMcpIds.has(serverId))
}

const getValidSelectedSkillIds = () => {
  const availableSkillIds = new Set(skillOptions.value.map((item) => item.id).filter(Boolean))
  return selectedSkillIds.value.filter((skillId) => availableSkillIds.has(skillId))
}

const getValidSelectedKnowledgeIds = () => {
  const availableKnowledgeIds = new Set(knowledgeOptions.value.map((item) => item.id).filter(Boolean))
  return selectedKnowledgeIds.value.filter((knowledgeId) => availableKnowledgeIds.has(knowledgeId)).slice(0, 1)
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
const isImageAttachment = (attachment: ChatAttachment) => attachment.mime_type?.startsWith('image/')
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
  agent_name: isAgentMode.value ? activeAgentName.value : '',
  agent_id: isAgentMode.value ? activeAgentId.value : '',
  web_search: ALWAYS_WEB_SEARCH,
  plugins: canPickTools.value ? getValidSelectedToolIds() : [],
  mcp_servers: canPickTools.value ? getValidSelectedMcpIds() : getValidAutoMcpIds(),
  knowledge_ids: canPickTools.value ? getValidSelectedKnowledgeIds() : [],
  retrieval_mode: canPickTools.value ? effectiveRetrievalMode.value : 'rag',
  agent_skill_ids: canPickTools.value ? getValidSelectedSkillIds() : [],
  session_id: currentSessionId.value,
  execution_mode: isAgentMode.value ? selectedExecutionMode.value : 'tool',
  access_scope: isAgentMode.value ? selectedAccessScope.value : 'workspace',
  desktop_bridge_url: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeUrl || '' : '',
  desktop_bridge_token: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeToken || '' : '',
  attachments: pendingAttachments.value.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment),
})

const submitAgentRuntimeTask = async (query: string, attachmentsForRequest: PendingAttachment[], assistantIndex: number) => {
  let generationFailed = false
  let shouldRestoreAttachments = false
  const renderAgentProgress = async () => {
    if (!messages.value[assistantIndex] || activeRuntimeArtifact.value?.content) return
    messages.value[assistantIndex].content = buildRuntimeAssistantMessage()
    await scrollToBottom()
  }
  try {
    const workspaceId = currentSessionId.value || normalizeRuntimeSlug('workspace', 'workspace')
    const registered = await registerRuntimeAttachments(workspaceId, query, attachmentsForRequest)
    const payload = buildPayload(query)
    payload.workspace_id = workspaceId
    payload.goal = query
    payload.product_mode = registered.length > 0 ? 'enterprise_kb' : 'general_agent'
    payload.uploaded_file_ids = registered.map((item) => item.fileId)
    payload.knowledge_space_ids = registered.map((item) => item.knowledgeSpaceId)
    payload.approval_mode = 'runtime'
    payload.output_contract = {
      artifact_kinds: ['markdown'],
      citation_required: registered.length > 0,
      trace_required: true,
      format: 'markdown',
    }
    payload.budget = {
      max_steps: 10,
      timeout_seconds: 180,
    }
    payload.attachments = attachmentsForRequest.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment)
    if (registered.length > 0) {
      executionEvents.value.push({
        id: crypto.randomUUID(),
        title: '文档已进入解析与索引',
        detail: registered.map((item) => `${item.fileId} -> ${item.knowledgeSpaceId}`).join('\n'),
        at: new Date().toLocaleTimeString(),
        phase: 'ingest',
        status: 'indexed',
        accent: 'retrieval',
      })
      await renderAgentProgress()
    }
    const response = await createWorkspaceTaskAPI(payload)
    const taskSnapshot = unwrapWorkspaceTaskResponse(response)
    await applyWorkspaceTaskSnapshot(taskSnapshot, assistantIndex)
    const taskId = taskSnapshot?.task?.task_id || ''
    const traceId = taskSnapshot?.task?.trace_id || taskSnapshot?.runtime?.trace_id || ''
    if (!taskId) throw new Error('Workspace task runtime did not return task_id.')
    executionEvents.value.push({
      id: crypto.randomUUID(),
      title: 'Task 已创建',
      detail: `task_id=${taskId}${traceId ? ` / trace_id=${traceId}` : ''}`,
      at: new Date().toLocaleTimeString(),
      phase: 'task',
      status: taskSnapshot?.task?.status || 'created',
      accent: 'default',
    })
    await renderAgentProgress()
    await streamWorkspaceTaskEvents(taskId, assistantIndex, renderAgentProgress)
    const hasPendingApproval = Boolean(pendingToolApproval.value)
    if (runtimeFailure.value) {
      generationFailed = true
      if (messages.value[assistantIndex]) {
        messages.value[assistantIndex].content = buildRuntimeAssistantMessage()
        setMessageMotion(messages.value[assistantIndex], 'error', 1800)
      }
      pulsePetMood('error', 1800)
    } else if (hasPendingApproval) {
      if (messages.value[assistantIndex]) {
        messages.value[assistantIndex].content = buildRuntimeAssistantMessage()
        setMessageMotion(messages.value[assistantIndex], 'thinking')
      }
      pulsePetMood('thinking', 1200)
    } else {
      if (messages.value[assistantIndex] && !activeRuntimeArtifact.value?.content) {
        messages.value[assistantIndex].content = buildRuntimeAssistantMessage() || buildFallbackAssistantMessage()
      }
      setMessageMotion(messages.value[assistantIndex], 'complete', 1100)
      pulsePetMood('success', 1300)
    }
    isGenerating.value = false
    assistantTextStreaming.value = false
    emitSessionUpdated()
    return !generationFailed
  } catch (error) {
    console.error('Workspace runtime task failed', error)
    runtimeFailure.value = {
      title: '任务异常',
      detail: buildChatErrorMessage(error instanceof Error ? error.message : String(error || 'unknown error')),
    }
    shouldRestoreAttachments = true
    pendingAttachments.value = attachmentsForRequest
    if (messages.value[assistantIndex]) {
      messages.value[assistantIndex].content = buildRuntimeAssistantMessage()
      setMessageMotion(messages.value[assistantIndex], 'error', 1800)
    }
    assistantTextStreaming.value = false
    pulsePetMood('error', 1800)
    ElMessage.error('任务运行失败，请稍后重试')
    isGenerating.value = false
    return false
  } finally {
    if (!shouldRestoreAttachments) attachmentsForRequest.forEach(revokeAttachmentPreview)
  }
}

const submitMessage = async () => {
  const query = inputMessage.value.trim() || (pendingAttachments.value.length > 0 ? '请分析我上传的附件。' : '')
  if (!query) { ElMessage.warning('请输入内容。'); return false }
  if (isGenerating.value) { ElMessage.warning('请等待当前回复完成。'); return false }
  const localSettingsSection = pendingAttachments.value.length ? '' : getSettingsSectionFromLocalCommand(query)
  if (localSettingsSection) {
    inputMessage.value = ''
    composerExpanded.value = false
    composerFocused.value = false
    pulsePetMood('wake', 900)
    window.dispatchEvent(new CustomEvent('workspace-open-settings', { detail: { section: localSettingsSection } }))
    return true
  }
  if (!selectedModelId.value || !selectedModel.value) {
    await fetchModels()
  }
  if (!selectedModelId.value || !selectedModel.value) {
    inputMessage.value = ''
    composerExpanded.value = false
    const userMessage: ChatMessage = { role: 'user', content: query, uiOrder: nextConversationOrder() }
    const assistantMessage: ChatMessage = { role: 'assistant', content: buildMissingModelMessage(), uiOrder: nextConversationOrder() }
    messages.value.push(userMessage)
    messages.value.push(assistantMessage)
    setMessageMotion(userMessage, 'sending', 520)
    setMessageMotion(assistantMessage, 'error', 1800)
    activeAssistantMessageIndex.value = messages.value.length - 1
    assistantTextStreaming.value = false
    pulsePetMood('confused', 1800)
    isPinnedToBottom.value = true
    await scrollToBottom(true, 'smooth')
    return false
  }
  if (!currentSessionId.value) {
    try {
      await createPersistedSession(selectedMode.value)
    } catch (error) {
      console.error('补建会话失败', error)
      pulsePetMood('error', 1600)
      ElMessage.error('新建会话失败')
      return false
    }
  }
  clearTransientPetMood()
  inputMessage.value = ''
  composerExpanded.value = false
  composerFocused.value = false
  isGenerating.value = true
  executionEvents.value = []
  resetRuntimeSurface()
  showTracePanel.value = isAgentMode.value
  const attachmentsForRequest = [...pendingAttachments.value]
  pendingAttachments.value = []
  const attachmentsForMessage = attachmentsForRequest.map((attachment) => ({
    ...attachment,
    preview_url: attachment.url,
  }))
  const userMessage: ChatMessage = { role: 'user', content: query, attachments: attachmentsForMessage, uiOrder: nextConversationOrder() }
  messages.value.push(userMessage)
  setMessageMotion(userMessage, 'sending', 520)
  const assistantIndex = messages.value.length
  const assistantMessage: ChatMessage = { role: 'assistant', content: isAgentMode.value ? buildLiveAssistantProgress() : '', uiOrder: nextConversationOrder() }
  messages.value.push(assistantMessage)
  setMessageMotion(assistantMessage, 'thinking')
  activeAssistantMessageIndex.value = assistantIndex
  assistantTextStreaming.value = false
  isPinnedToBottom.value = true
  await scrollToBottom(true)
  await syncRouteState({ preserveConversation: true })
  if (isAgentMode.value) executionEvents.value.push({ id: crypto.randomUUID(), title: '开始执行', detail: `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value} / ${effectiveRetrievalModeLabel.value}`, at: new Date().toLocaleTimeString(), phase: 'start', status: 'START', accent: 'default' })
  if (isAgentMode.value) return await submitAgentRuntimeTask(query, attachmentsForRequest, assistantIndex)
  let assistantHasRealContent = false
  let generationFailed = false
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
        assistantTextStreaming.value = true
        setMessageMotion(messages.value[assistantIndex], 'streaming')
        messages.value[assistantIndex].content += safeChunk
        await scrollToBottom()
      },
      onFinalMessage: async (message) => {
        const safeMessage = sanitizeAssistantChunk(message)
        if (!safeMessage || !messages.value[assistantIndex]) return
        messages.value[assistantIndex].content = safeMessage
        assistantHasRealContent = true
        assistantTextStreaming.value = true
        setMessageMotion(messages.value[assistantIndex], 'streaming')
        await scrollToBottom()
      },
      onEvent: async (event) => {
        if (String(event.data?.status || '').toUpperCase() === 'ERROR') {
          if (messages.value[assistantIndex]) {
            messages.value[assistantIndex].content = buildChatErrorMessage(event.detail || event.title)
            assistantHasRealContent = true
            assistantTextStreaming.value = false
            generationFailed = true
            setMessageMotion(messages.value[assistantIndex], 'error', 1800)
            pulsePetMood('error', 1600)
            await scrollToBottom()
          }
          return
        }
        if (!isAgentMode.value) return
        pushTraceEvent(event)
        capturePendingToolApproval(event)
        await refreshToolSelectionsAfterCreation(event)
        await renderAgentProgress()
      },
      onError: (error) => {
        console.error('对话失败', error)
        generationFailed = true
        pendingAttachments.value = attachmentsForRequest
        applyFallback()
        assistantTextStreaming.value = false
        setMessageMotion(messages.value[assistantIndex], 'error', 1800)
        pulsePetMood('error', 1800)
        ElMessage.error('对话失败，请稍后重试')
        isGenerating.value = false
      },
      onClose: () => {
        attachmentsForRequest.forEach(revokeAttachmentPreview)
        applyFallback()
        isGenerating.value = false
        assistantTextStreaming.value = false
        setMessageMotion(messages.value[assistantIndex], generationFailed ? 'error' : 'complete', generationFailed ? 1800 : 1100)
        pulsePetMood(generationFailed ? 'error' : 'success', generationFailed ? 1800 : 1300)
        emitSessionUpdated()
      },
    })
    return true
  } catch (error) {
    console.error('对话异常', error)
    pendingAttachments.value = attachmentsForRequest
    applyFallback()
    assistantTextStreaming.value = false
    setMessageMotion(messages.value[assistantIndex], 'error', 1800)
    pulsePetMood('error', 1800)
    ElMessage.error('对话异常')
    isGenerating.value = false
    return false
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

watch(selectedModelId, async (newModelId, oldModelId) => {
  if (!newModelId || newModelId === oldModelId) return
  await consumeInitialRouteMessage()
})

watch(() => route.query.session_id, async (newSessionId, oldSessionId) => {
  if (newSessionId && newSessionId !== oldSessionId) {
    if (preserveConversationOnRouteSync.value && String(newSessionId) === currentSessionId.value) {
      selectedMode.value = safeQueryValue(route.query.mode, selectedMode.value) === 'agent' ? 'agent' : 'normal'
      return
    }
    currentSessionId.value = String(newSessionId)
    selectedMode.value = safeQueryValue(route.query.mode, selectedMode.value) === 'agent' ? 'agent' : 'normal'
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
    await nextTick()
    await consumeInitialRouteMessage()
    return
  }
  if (!newSessionId && oldSessionId) {
    try {
      await resetToDraftSession(selectedMode.value, { pruneCurrent: false })
    } catch (error) {
      console.error('补建会话失败', error)
      ElMessage.error('新建会话失败')
    }
  }
})

watch(() => route.query.message, async (newMessage, oldMessage) => {
  if (!newMessage || newMessage === oldMessage)
    return

  await nextTick()
  await consumeInitialRouteMessage()
})

watch(() => route.fullPath, async (newPath, oldPath) => {
  if (newPath === oldPath) return
  await appendSettingsThreadFromRoute()
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

watch(selectedMode, async (newMode, oldMode) => {
  if (!workspaceHydrated.value || newMode === oldMode) return
  try {
    if (currentSessionId.value) {
      saveWorkspaceSessionMode(currentSessionId.value, newMode)
      emitSessionModeUpdated()
    }
    await syncRouteState()
  } catch (error) {
    console.error('切换模式失败', error)
    ElMessage.error('切换模式失败')
  }
})

onMounted(async () => {
  window.addEventListener('workspace-new-conversation', handleNewConversationRequest)
  window.addEventListener('resize', handleViewportResize)
  window.addEventListener('pointerdown', handleAgentPickerPointerDown)
  window.addEventListener('workspace-settings-navigate', handleSettingsNavigateRequest as EventListener)
  await Promise.all([fetchExecutionConfig(), fetchModels(), fetchMcpServers()])
  const savedDefaults = loadWorkspaceDefaults()
  selectedMode.value = safeQueryValue(route.query.mode, savedDefaults.mode || 'normal') === 'agent' ? 'agent' : 'normal'
  activeAgentName.value = selectedMode.value === 'agent' ? safeQueryValue(route.query.agent_name, '') : ''
  activeAgentId.value = selectedMode.value === 'agent' ? safeQueryValue(route.query.agent_id, '') : ''
  selectedExecutionMode.value = safeQueryValue(route.query.execution_mode, savedDefaults.executionMode || 'tool')
  selectedAccessScope.value = safeQueryValue(route.query.access_scope, savedDefaults.accessScope || 'workspace')
  selectedExecutionMode.value = executionModes.value.some((item) => item.id === selectedExecutionMode.value) ? selectedExecutionMode.value : 'tool'
  selectedAccessScope.value = accessScopes.value.some((item) => item.id === selectedAccessScope.value) ? selectedAccessScope.value : 'workspace'
  if (savedDefaults.modelId && modelOptions.value.some((model) => model.llm_id === savedDefaults.modelId)) selectedModelId.value = savedDefaults.modelId
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
  const sessionId = safeQueryValue(route.query.session_id, '')
  if (sessionId) {
    currentSessionId.value = sessionId
    await loadSessionHistory(sessionId)
  } else {
    currentSessionId.value = ''
  }
  await nextTick()
  await consumeInitialRouteMessage()
  await appendSettingsThreadFromRoute()
  workspaceHydrated.value = true
  ensureSettingsMutationObserver()
  await autosizeSettingsTextareas()
})

onUpdated(() => {
  ensureSettingsMutationObserver()
  void autosizeSettingsTextareas()
  void autosizeComposerTextarea()
})

watch([inputMessage, compactComposerVisible], () => {
  void autosizeComposerTextarea()
}, { flush: 'post' })

onBeforeUnmount(() => {
  window.removeEventListener('workspace-new-conversation', handleNewConversationRequest)
  window.removeEventListener('resize', handleViewportResize)
  window.removeEventListener('pointerdown', handleAgentPickerPointerDown)
  window.removeEventListener('workspace-settings-navigate', handleSettingsNavigateRequest as EventListener)
  settingsBubbleAnchorCleanup?.()
  settingsMutationObserver?.disconnect()
  if (autosizeFrame) window.cancelAnimationFrame(autosizeFrame)
  if (viewportResizeFrame) window.cancelAnimationFrame(viewportResizeFrame)
  if (viewportResizeTimer) window.clearTimeout(viewportResizeTimer)
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  if (settingsAnchorProgrammaticTimer) window.clearTimeout(settingsAnchorProgrammaticTimer)
  clearMessageMotionTimers()
})
</script>

<template>
  <div class="workspace-chat" :class="{ active: conversationSurfaceActive, 'session-loading': sessionHistoryLoading }">
    <div class="workspace-shell">
      <Transition name="workspace-surface">
      <div v-if="!conversationSurfaceActive" key="intro" class="intro-stack">
        <MascotPresence
          class="intro-pet"
          size="beacon"
          animated
          interactive
          aria-label="唤醒 Zuno"
          @pet-click="handleIntroPetClick"
        />
        <h1>{{ heroTitle }}</h1>
        <p>{{ heroSubtitle }}</p>
        <div class="intro-status-row" aria-label="工作台状态">
          <span class="intro-status-pill" :class="modelStatusTone">{{ modelStatusLabel }}</span>
          <span v-if="isAgentMode && activeAgentName" class="intro-status-pill subtle">Agent：{{ activeAgentName }}</span>
        </div>
        <div class="mode-switcher" :class="{ 'agent-active': selectedMode === 'agent' || agentPickerOpen }" aria-label="会话入口">
          <button :class="['mode-pill', { active: selectedMode === 'normal' && !agentPickerOpen }]" :disabled="isGenerating" @click="selectedMode = 'normal'; activeAgentName = ''; activeAgentId = ''; agentPickerOpen = false">
            Chat
          </button>
          <button :class="['mode-pill', { active: selectedMode === 'agent' || agentPickerOpen }]" :disabled="isGenerating" @click="openAgentPicker">
            Agent
          </button>
          <Transition name="agent-picker">
            <div v-if="agentPickerOpen" class="agent-picker-panel" :class="{ empty: !agentPickerLoading && agentOptions.length === 0 }" aria-label="选择 Agent">
              <div v-if="agentPickerLoading" class="agent-picker-empty">正在读取已配置的 Agent...</div>
              <template v-else>
                <button
                  v-for="agent in agentOptions"
                  :key="agent.id"
                  type="button"
                  :class="['agent-choice', { active: activeAgentId === agent.id }]"
                  @click="selectAgentOption(agent)"
                >
                  <img
                    class="agent-choice-avatar"
                    :src="agent.avatar"
                    :alt="`${agent.name} 头像`"
                    @error="handleAgentOptionAvatarError"
                  />
                  <span>
                    <strong>{{ agent.name }}</strong>
                    <small>{{ agent.description }}</small>
                  </span>
                </button>
              </template>
            </div>
          </Transition>
        </div>
      </div>
      <div
        v-else
        key="conversation"
        ref="conversationRef"
        class="conversation-panel"
        @scroll="handleConversationScroll"
        @wheel.passive="cancelSettingsBubbleAnchor"
        @touchmove.passive="cancelSettingsBubbleAnchor"
        @pointerdown.capture="lockSettingsBubbleFromEvent"
        @click.capture="lockSettingsBubbleFromEvent"
        @beforeinput.capture="lockSettingsBubbleFromEvent"
        @change.capture="lockSettingsBubbleFromEvent"
        @keydown.capture="lockSettingsBubbleFromEvent"
      >
        <div v-if="sessionHistoryLoading && !hasConversationBlocks" class="message-row assistant session-loading-row">
          <MascotPresence
            class="avatar assistant-pet-avatar"
            size="avatar"
            state="thinking"
            aria-label="Zuno"
          />
          <div class="message-bubble assistant session-loading-bubble">
            <div class="chat-message-meta">
              <strong>Zuno</strong>
              <span>正在切换</span>
            </div>
            <div class="session-loading-copy">
              <span>{{ sessionHistoryLabel }}</span>
              <i></i>
              <i></i>
              <i></i>
            </div>
          </div>
        </div>
        <template v-for="block in conversationBlocks" :key="block.type === 'message' ? `message-${block.index}` : block.thread.id">
          <div
            v-if="block.type === 'message'"
            class="message-row"
            :class="[block.message.role, block.message.motion ? `motion-${block.message.motion}` : '']"
          >
            <MascotPresence
              v-if="block.message.role === 'assistant'"
              class="avatar assistant-pet-avatar"
              size="avatar"
              :state="getAssistantMascotState(block.index)"
              aria-label="Zuno"
            />
            <div
              class="message-bubble"
              :class="[
                {
                  assistant: block.message.role === 'assistant',
                  'has-content': !!block.message.content,
                  'has-attachments': !!block.message.attachments?.length,
                  loading: block.message.role === 'assistant' && !block.message.content && isGenerating && block.index === messages.length - 1,
                },
                block.message.motion ? `motion-${block.message.motion}` : '',
              ]"
            >
              <div v-if="block.message.role === 'assistant'" class="chat-message-meta">
                <strong>Zuno</strong>
                <span v-if="shouldShowAssistantStatus(block.message, block.index)">{{ getAssistantStatusLabel(block.message, block.index) }}</span>
              </div>
              <div v-if="block.message.role === 'assistant' && !block.message.content && isGenerating && block.index === messages.length - 1" class="loading-row" :class="{ agent: isAgentMode }">
              <template v-if="isAgentMode">
                <div class="loading-head">
                  <span class="spinner orbit"></span>
                  <div class="loading-copy">
                    <strong>{{ progressHeadline }}</strong>
                    <span>{{ progressDetail }}</span>
                  </div>
                  <div class="phase-pill-group">
                    <span class="phase-pill strong">{{ effectiveRetrievalModeLabel }}</span>
                    <span class="phase-pill">{{ selectedKnowledgeIds.length > 0 ? `${selectedKnowledgeIds.length} 个知识库` : '未选知识库' }}</span>
                  </div>
                </div>
                <div class="loading-steps">
                  <div v-for="step in progressSteps" :key="step.key" class="loading-step" :class="{ active: step.active, done: step.done }">
                    <span class="progress-dot"></span>
                    <span>{{ step.label }}</span>
                  </div>
                </div>
                <div v-if="liveProgressEvents.length > 0" class="loading-events">
                  <div v-for="event in liveProgressEvents" :key="event.id" class="loading-event" :class="event.accent || 'default'">
                    <strong>{{ event.title }}</strong>
                    <span v-if="event.detail">{{ event.detail }}</span>
                  </div>
                </div>
              </template>
              <template v-else>
                <span class="spinner"></span>
                <span>Zuno 正在想一想...</span>
              </template>
            </div>
            <div
              v-else-if="block.message.content"
              class="message-content"
              :class="block.message.role === 'assistant' ? 'zuno-prose' : 'user-prose'"
            >
              <MdPreview :editorId="`workspace-message-${block.index}`" :modelValue="normalizeMessageMarkdown(block.message.content)" />
            </div>
            <div v-if="block.message.attachments?.length" class="message-attachments">
              <a
                v-for="attachment in block.message.attachments"
                :key="attachment.id || attachment.url || attachment.name"
                class="message-attachment-card"
                :class="{ image: isImageAttachment(attachment) }"
                :href="attachment.url"
                target="_blank"
                rel="noreferrer"
              >
                <img v-if="isImageAttachment(attachment)" :src="attachment.preview_url || attachment.url" :alt="attachment.name" class="message-attachment-thumb" />
                <span v-else class="message-attachment-file">FILE</span>
                <span class="message-attachment-copy">
                  <strong>{{ attachment.name }}</strong>
                  <small>{{ formatAttachmentSize(attachment.size) }}</small>
                </span>
              </a>
            </div>
            <div v-if="block.message.content" class="message-actions" aria-label="消息操作">
              <button type="button" class="message-action" title="复制" aria-label="复制消息" @click.stop="copyMessageContent(block.message)">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
          </div>
            <img v-if="block.message.role === 'user'" :src="userAvatarSrc" alt="User" class="avatar" @error="handleAvatarError" />
          </div>
          <div v-else class="settings-thread-block">
            <div
              v-for="turn in block.thread.commandVisible ? block.thread.commandTurns : []"
              :key="turn.id"
              class="message-row user settings-command-row settings-turn-enter"
            >
              <div class="message-bubble settings-command settings-command-refresh">{{ turn.command }}</div>
              <img :src="userAvatarSrc" alt="User" class="avatar" @error="handleAvatarError" />
            </div>
            <article
              v-if="block.thread.assistantVisible"
              class="message-row assistant settings-panel-row settings-turn-enter assistant"
            >
              <MascotPresence
                class="avatar assistant-pet-avatar"
                size="avatar"
                :state="getSettingsMascotState(block.thread)"
                aria-label="Zuno"
              />
              <div class="settings-message-stack" :class="{ 'is-loading': !block.thread.ready }">
                <div v-if="!block.thread.ready" class="message-bubble assistant loading motion-thinking settings-loading-bubble" aria-live="polite">
                  <div class="chat-message-meta settings-loading-meta">
                    <strong>Zuno</strong>
                    <span>{{ getThreadLoadingVerb(block.thread) }}</span>
                  </div>
                  <div class="loading-row settings-loading-row">
                    <span class="spinner"></span>
                    <span>{{ getThreadLoadingText(block.thread) }}</span>
                    <i></i>
                    <i></i>
                    <i></i>
                  </div>
                </div>
                <div v-else class="settings-message-meta">
                  <strong>Zuno</strong>
                  <span>{{ `${block.thread.label} 已打开` }}</span>
                </div>
                <div class="settings-bubble-shell" :class="{ 'is-ready': block.thread.ready }">
                  <section
                    class="settings-bubble"
                    :data-settings-thread-id="block.thread.id"
                    :data-settings-section="block.thread.section"
                    :data-settings-route="block.thread.routeName"
                    :data-settings-detail="block.thread.detail ? 'true' : 'false'"
                    :style="{ '--settings-page-icon': `url(${block.thread.icon})` }"
                  >
                    <SettingsUiModeSwitch class="settings-mode-inline-switch" :mode="settingsUiMode" compact />
                    <div v-if="canNavigateSettingsThreadBack(block.thread)" class="settings-bubble-toolbar">
                      <button
                        class="settings-bubble-nav-button"
                        type="button"
                        title="返回上一级"
                        aria-label="返回上一级"
                        @click="handleSettingsThreadBack(block.thread)"
                      >
                        <el-icon><ArrowLeft /></el-icon>
                      </button>
                    </div>
                    <Transition name="settings-page-switch">
                      <component :is="block.thread.component" :key="block.thread.routeKey" />
                    </Transition>
                  </section>
                </div>
              </div>
            </article>
          </div>
        </template>
      </div>
      </Transition>
      <div class="composer-dock" :class="{ fixed: conversationSurfaceActive }">
        <button v-if="compactComposerVisible" class="composer-collapsed" type="button" @click="expandComposer">
          <img class="composer-collapsed-icon" :src="messageIcon" alt="" aria-hidden="true" />
          <span>给 Zuno 发消息</span>
        </button>
        <div
          v-else
          class="composer-shell"
          :class="{ 'drag-active': isAttachmentDragOver, 'is-sending': isGenerating }"
          @focusout="handleComposerFocusOut"
          @dragover.prevent="handleAttachmentDragOver"
          @dragleave="handleAttachmentDragLeave"
          @drop.prevent="handleAttachmentDrop"
        >
          <div class="composer-top" :class="{ compact: compactPanel }">
            <div class="composer-actions">
              <button v-if="isAgentMode && compactPanel" class="ghost-pill subtle" type="button" @click="showTracePanel = !showTracePanel"><el-icon><ArrowDown v-if="showTracePanel" /><ArrowUp v-else /></el-icon>{{ showTracePanel ? '收起进展' : '查看进展' }}</button>
            </div>
          </div>

          <div v-if="traceVisible" class="trace-card" :class="{ generating: isGenerating }">
            <div v-if="isGenerating" class="progress-inline">
              <div class="progress-head">
                <div class="trace-head-copy">
                  <strong>{{ progressHeadline }}</strong>
                  <small>{{ progressDetail }}</small>
                </div>
                <div class="phase-pill-group">
                  <span class="progress-badge">处理中</span>
                  <span class="phase-pill strong">{{ effectiveRetrievalModeLabel }}</span>
                </div>
              </div>
              <div class="progress-steps">
                <div v-for="step in progressSteps" :key="step.key" class="progress-step" :class="{ active: step.active, done: step.done }">
                  <span class="progress-dot"></span>
                  <span>{{ step.label }}</span>
                </div>
              </div>
            </div>
            <div class="picker-head"><div class="trace-head-copy"><strong>执行进展</strong><small>{{ selectedToolCount > 0 ? `已启用 ${selectedToolCount} 项能力` : '未启用额外工具' }}</small></div></div>
            <div v-if="pendingToolApproval" class="tool-approval-card" aria-label="工具审批">
              <div class="tool-approval-copy">
                <strong>{{ pendingToolApproval.toolId }}</strong>
                <small>{{ pendingToolApproval.auditRef ? `审计：${pendingToolApproval.auditRef}` : pendingToolApproval.requiredApproval }}</small>
              </div>
              <div class="tool-approval-actions">
                <button type="button" class="tool-approval-button reject" :disabled="toolApprovalSubmitting" @click="submitToolApproval('rejected')">拒绝</button>
                <button type="button" class="tool-approval-button approve" :disabled="toolApprovalSubmitting" @click="submitToolApproval('approved')">批准</button>
              </div>
            </div>
            <div v-if="runtimeFailure" class="runtime-failure-panel" aria-label="任务失败">
              <div class="runtime-panel-head">
                <strong>{{ runtimeFailure.title }}</strong>
                <span>{{ activeRuntimeTaskId ? `task_id=${activeRuntimeTaskId}` : 'runtime' }}</span>
              </div>
              <div class="runtime-panel-copy">{{ runtimeFailure.detail }}</div>
            </div>
            <div v-if="activeRuntimeArtifact" class="runtime-artifact-panel" aria-label="Artifact">
              <div class="runtime-panel-head">
                <strong>Artifact</strong>
                <span>{{ activeRuntimeArtifact.artifactId }}</span>
              </div>
              <div v-if="activeRuntimeArtifact.uri" class="runtime-panel-copy">{{ activeRuntimeArtifact.uri }}</div>
              <div v-if="activeRuntimeArtifact.citations.length > 0 || activeRuntimeCitationIds.length > 0" class="runtime-citation-row">
                <span
                  v-for="citationId in (activeRuntimeArtifact.citations.length > 0 ? activeRuntimeArtifact.citations : activeRuntimeCitationIds)"
                  :key="citationId"
                  class="runtime-citation-chip"
                >
                  {{ citationId }}
                </span>
              </div>
            </div>
            <div v-if="activeRuntimeObservability" class="runtime-observability-panel" aria-label="Trace Eval">
              <div class="runtime-panel-head">
                <strong>Trace / Eval</strong>
                <span class="release-eval">{{ runtimeReleaseEvalStatus }}</span>
              </div>
              <div class="runtime-panel-metrics">
                <span>{{ runtimeSpanCount }} spans</span>
                <span v-if="activeRuntimeObservability.trace_replay?.trace_id">{{ activeRuntimeObservability.trace_replay.trace_id }}</span>
                <span v-if="runtimeTraceSourceRefs.length > 0">{{ runtimeTraceSourceRefs.length }} source refs</span>
              </div>
            </div>
            <div v-if="activeRuntimeTaskId && (activeRuntimeArtifact || runtimeFailure)" class="runtime-feedback-panel" aria-label="Feedback">
              <div class="runtime-panel-copy">{{ runtimeFeedbackCopy }}</div>
              <div class="runtime-feedback-actions">
                <button type="button" class="runtime-feedback-button" :disabled="feedbackSubmitting || feedbackSent" @click="submitWorkspaceFeedback('helpful')">有帮助</button>
                <button type="button" class="runtime-feedback-button" :disabled="feedbackSubmitting || feedbackSent" @click="submitWorkspaceFeedback('needs_revision')">需要调整</button>
              </div>
            </div>
            <div v-if="executionEvents.length === 0" class="empty-copy">正在等待新的执行事件...</div>
            <div v-else class="trace-list">
              <div v-for="event in executionEvents" :key="event.id" class="trace-item" :class="event.accent || 'default'">
                <div class="trace-head">
                  <strong>{{ event.title }}</strong>
                  <span>{{ event.at }}</span>
                </div>
                <div v-if="event.detail" class="trace-detail">{{ event.detail }}</div>
                <div v-if="event.artifactId || event.citationIds?.length || event.sourceRefs?.length" class="runtime-trace-meta">
                  <span v-if="event.artifactId" class="trace-pill">artifact {{ event.artifactId }}</span>
                  <span v-for="citationId in event.citationIds || []" :key="`${event.id}-${citationId}`" class="trace-pill">citation {{ citationId }}</span>
                  <span v-if="event.sourceRefs?.length" class="trace-pill">{{ event.sourceRefs.length }} source refs</span>
                </div>
                <div v-if="event.retrieval" class="retrieval-trace">
                  <div class="retrieval-meta">
                    <span class="trace-pill strong">首轮 {{ getRetrievalModeLabel(event.retrieval.firstMode) }}</span>
                    <span class="trace-pill strong">最终 {{ getRetrievalModeLabel(event.retrieval.finalMode) }}</span>
                    <span class="trace-pill">{{ event.retrieval.roundCount }} 轮</span>
                    <span v-if="event.retrieval.rewrittenQueryUsed" class="trace-pill">改写重试</span>
                  </div>
                  <div v-if="event.retrieval.fallbackReason" class="trace-reason">
                    补检原因：{{ event.retrieval.fallbackReason }}
                  </div>
                  <div v-if="event.retrieval.rounds.length > 0" class="trace-round-list">
                    <div v-for="round in event.retrieval.rounds" :key="`${event.id}-${round.round}`" class="trace-round-item">
                      <div class="trace-round-head">
                        <strong>第 {{ round.round }} 轮</strong>
                        <span>{{ getRetrievalModeLabel(round.mode) }}</span>
                      </div>
                      <div class="trace-round-body">
                        <span>{{ getRetrievalTriggerLabel(round.trigger || '') }}</span>
                        <span v-if="round.qualityReason">{{ getQualityReasonLabel(round.qualityReason) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
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
          <textarea ref="composerInputRef" v-model="inputMessage" class="composer" :rows="compactPanel ? 1 : 2" :placeholder="composerPlaceholder" @focus="handleComposerFocus" @keydown="handleKeydown" @paste="handleComposerPaste" />
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
              <button v-if="isAgentMode && canPickTools" class="attach-btn tool-create-btn" type="button" :disabled="attachmentsUploading || isGenerating" @click="openToolCreationPrompt('general')"><el-icon><Plus /></el-icon><span>新增工具</span></button>
              <div class="composer-meta"><span class="composer-hint">{{ modeFooterCopy }}</span><span class="attachment-hint">{{ attachmentHint }}</span><span v-if="isAgentMode && canPickTools" class="retrieval-hint">检索：{{ effectiveRetrievalModeLabel }}</span></div>
            </div>
            <button class="send-btn" :disabled="isGenerating || attachmentsUploading" @click="submitMessage">{{ isGenerating ? '处理中...' : '发送' }}</button>
          </div>
      </div>
      <p v-if="!hasConversationBlocks" class="composer-disclaimer">重要信息仍建议核验。</p>
    </div>
  </div>
</div>
</template>

<style scoped src="./defaultPage.css"></style>
