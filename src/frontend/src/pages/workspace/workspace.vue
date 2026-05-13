<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Fold, Expand, Plus, Setting } from '@element-plus/icons-vue'
import { zunoAgentAvatar } from '../../utils/brand'
import { useUserStore } from '../../store/user'
import { logoutAPI, getUserInfoAPI } from '../../apis/auth'
import { getWorkspaceSessionsAPI, deleteWorkspaceSessionAPI } from '../../apis/workspace'
import { getAgentsAPI, type AgentResponse } from '../../apis/agent'
import { useResizablePanel } from '../../composables/useResizablePanel'
import { getSettingsIcon } from '../../utils/settings-icons'
import { DEFAULT_USER_AVATAR, isLegacyRemoteUserAvatar, withUserAvatarVersion } from '../../utils/user-avatars'
import SidebarMascot from '../../components/SidebarMascot.vue'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'
import WorkspaceAuthGate from './WorkspaceAuthGate.vue'
import accountConversationIcon from '../../assets/account/conversation.svg'
import accountProfileIcon from '../../assets/account/profile.svg'
import accountLogoutIcon from '../../assets/account/logout.svg'
import {
  loadWorkspaceDefaults,
  loadWorkspaceSessionModes,
  removeWorkspaceSessionMode,
  type WorkspaceMode,
} from '../../utils/workspace-defaults'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

interface WorkspaceSessionItem {
  sessionId: string
  title: string
  createTime: string
  agent: string
  workspaceMode: WorkspaceMode
}

interface SidebarAgentItem {
  id: string
  name: string
  description: string
  avatar: string
}

type AuthMode = 'choice' | 'login' | 'register'

const selectedSession = ref('')
const sessions = ref<WorkspaceSessionItem[]>([])
const agents = ref<SidebarAgentItem[]>([])
const loading = ref(false)
const SIDEBAR_COLLAPSED_KEY = 'zuno.workspace.sidebarCollapsed'
const getInitialSidebarCollapsed = () => {
  if (typeof window === 'undefined') return false
  if (window.innerWidth <= 760) return true
  if (window.innerWidth > 520) return false
  return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true'
}
const sidebarCollapsed = ref(getInitialSidebarCollapsed())
const selectedSettingsSection = ref('agent')
const settingsMenuOpen = ref(false)
const accountMenuOpen = ref(false)
const navigationSettling = ref(false)
const CHAT_SECTION_KEY = 'chat'
const SIDEBAR_PAGE_SIZE = 6
const expandedSidebarSections = ref<Record<string, boolean>>({ [CHAT_SECTION_KEY]: true })
const sidebarPages = ref<Record<string, number>>({})
let fetchSessionsRequestId = 0
let navigationSettlingTimer = 0
const handleResponsiveSidebar = () => {
  if (typeof window === 'undefined') return
  if (window.innerWidth <= 760) {
    sidebarCollapsed.value = true
  }
}
const handleWorkspacePointerDown = (event: PointerEvent) => {
  if (!settingsMenuOpen.value && !accountMenuOpen.value) return
  const target = event.target as Element | null
  if (target?.closest('.settings-float, .settings-entry')) return
  if (target?.closest('.account-float, .account-entry')) return
  settingsMenuOpen.value = false
  accountMenuOpen.value = false
}
const {
  panelStyle: historyPanelStyle,
  startResize: startHistoryResize,
  handleSeparatorKeydown: handleHistorySeparatorKeydown,
} = useResizablePanel({
  storageKey: 'zuno.layout.workspaceHistoryWidth',
  cssVariable: '--workspace-sidebar-width',
  defaultWidth: 264,
  minWidth: 204,
  maxWidth: 460,
  minAvailableContentWidth: 340,
})

const normalizeAvatarUrl = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/') || isLegacyRemoteUserAvatar(raw)) return DEFAULT_USER_AVATAR
  return withUserAvatarVersion(raw)
}

const userAvatarSrc = computed(() => normalizeAvatarUrl(userStore.userInfo?.avatar))
const wait = (ms: number) => new Promise<void>((resolve) => window.setTimeout(resolve, ms))
const hasAuthToken = () => Boolean(typeof window !== 'undefined' && window.localStorage.getItem('token'))
const authUnlocked = ref(hasAuthToken())
const authUnlocking = ref(false)
const workspaceNavVisible = computed(() => authUnlocked.value || authUnlocking.value)
const authInitialMode = computed<AuthMode>(() => {
  const rawMode = Array.isArray(route.query.auth) ? route.query.auth[0] : route.query.auth
  if (rawMode === 'login' || rawMode === 'register') return rawMode
  return 'choice'
})
const hydrateAuthenticatedWorkspace = async () => {
  if (!hasAuthToken()) {
    sessions.value = []
    agents.value = []
    return
  }

  if (userStore.isLoggedIn && userStore.userInfo && !userStore.userInfo.avatar) {
    try {
      const response = await getUserInfoAPI(userStore.userInfo.id)
      if (response.data.status_code === 200 && response.data.data) {
        const userData = response.data.data
        userStore.updateUserInfo({
          avatar: normalizeAvatarUrl(userData.user_avatar || userData.avatar),
          description: userData.user_description || userData.description,
        })
      }
    } catch (error) {
      console.error('初始化用户信息失败:', error)
    }
  }

  syncSelectedSessionFromRoute()
  await Promise.all([fetchSessions(), fetchAgents()])
}

const stripAuthQuery = async () => {
  const redirect = Array.isArray(route.query.redirect) ? route.query.redirect[0] : route.query.redirect
  if (redirect && typeof redirect === 'string' && redirect.startsWith('/')) {
    await router.replace(redirect)
    return
  }

  if ('auth' in route.query || 'redirect' in route.query) {
    const { auth, redirect: _redirect, ...nextQuery } = route.query
    await router.replace({
      name: route.name || 'workspaceDefaultPage',
      params: route.params,
      query: nextQuery,
    })
  }
}

const handleAuthenticated = async () => {
  authUnlocking.value = true
  await hydrateAuthenticatedWorkspace()
  await wait(220)
  authUnlocked.value = true
  authUnlocking.value = false
  await stripAuthQuery()
}

const syncSelectedSessionFromRoute = () => {
  const sessionId = route.query.session_id as string | undefined
  selectedSession.value = sessionId || ''
}

const agentSectionKey = (agentName: string) => `agent:${agentName}`
const isSidebarSectionExpanded = (sectionKey: string) => (
  expandedSidebarSections.value[sectionKey] ?? sectionKey === CHAT_SECTION_KEY
)
const setSidebarSectionExpanded = (sectionKey: string, expanded: boolean) => {
  expandedSidebarSections.value = {
    ...expandedSidebarSections.value,
    [sectionKey]: expanded,
  }
}
const toggleSidebarSection = (sectionKey: string) => {
  setSidebarSectionExpanded(sectionKey, !isSidebarSectionExpanded(sectionKey))
}
const sessionSectionKey = (session: WorkspaceSessionItem) => (
  session.workspaceMode === 'agent' && session.agent
    ? agentSectionKey(session.agent)
    : CHAT_SECTION_KEY
)
const expandSelectedSessionSection = () => {
  if (!selectedSession.value) return
  const session = sessions.value.find((item) => item.sessionId === selectedSession.value)
  if (session) setSidebarSectionExpanded(sessionSectionKey(session), true)
}

const pulseNavigationSettling = (duration = 420) => {
  if (navigationSettlingTimer) window.clearTimeout(navigationSettlingTimer)
  navigationSettling.value = true
  navigationSettlingTimer = window.setTimeout(() => {
    navigationSettling.value = false
    navigationSettlingTimer = 0
  }, duration)
}

const startNewConversation = async (agent?: SidebarAgentItem) => {
  if (!authUnlocked.value) return
  settingsMenuOpen.value = false
  pulseNavigationSettling(520)
  setSidebarSectionExpanded(agent ? agentSectionKey(agent.name) : CHAT_SECTION_KEY, true)
  if (settingsCenterVisible.value) {
    await router.push(defaultWorkspaceRoute())
  }
  window.dispatchEvent(new CustomEvent('workspace-new-conversation', {
    detail: agent
      ? { mode: 'agent', agentId: agent.id, agentName: agent.name }
      : { mode: 'normal' },
  }))
}

const handleWorkspaceSessionUpdated = async () => {
  if (!authUnlocked.value) return
  syncSelectedSessionFromRoute()
  await fetchSessions()
}

const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return '未知时间'
    const date = new Date(timeStr)
    if (isNaN(date.getTime())) return '未知时间'

    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) return '刚刚'
    if (diffInHours < 24) return `${Math.floor(diffInHours)} 小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)} 天前`

    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch {
    return '未知时间'
  }
}

const isRealAgentName = (value: unknown) => {
  const raw = String(value || '').trim().toLowerCase()
  return Boolean(raw && !['normal', 'simple', 'agent'].includes(raw))
}

const isPlaceholderSessionTitle = (value: unknown) => {
  const normalized = String(value || '').trim().toLowerCase()
  const compact = normalized.replace(/\s+/g, '')
  return (
    ['', '新对话', '未命名会话', '你好', '您好', 'hi', 'hello'].includes(normalized)
    || /^.+的新(对话|会话)$/.test(compact)
  )
}

const cleanupSessionTitleCandidate = (value: unknown) => (
  String(value || '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 32)
)

const deriveSessionTitle = (session: any) => {
  const rawTitle = String(session?.title || '').trim()
  if (rawTitle && !isPlaceholderSessionTitle(rawTitle)) return rawTitle

  const contexts = Array.isArray(session?.contexts) ? session.contexts : []
  const firstQuery = contexts
    .map((context: any) => cleanupSessionTitleCandidate(context?.query))
    .find(Boolean)
  return firstQuery || rawTitle || '未命名会话'
}

const normalizeAgentName = (value: unknown) => {
  const raw = String(value || '').trim()
  if (!isRealAgentName(raw)) return ''
  return raw
}
const inferWorkspaceMode = (session: any): WorkspaceMode => {
  if (isRealAgentName(session.agent)) return 'agent'
  const explicitMode = String(session.workspace_mode || '').trim().toLowerCase()
  if (explicitMode === 'normal') return 'normal'
  return 'normal'
}

const workspaceModeLabel = (mode: WorkspaceMode) => mode === 'agent' ? 'Agent' : 'Chat'
const settingsSections = [
  { key: 'agent', label: '智能体', icon: getSettingsIcon('agent') },
  { key: 'model', label: '模型', icon: getSettingsIcon('model') },
  { key: 'knowledge', label: '知识库', icon: getSettingsIcon('knowledge') },
  { key: 'mcp', label: 'MCP', icon: getSettingsIcon('mcp') },
  { key: 'tool', label: '工具', icon: getSettingsIcon('tool') },
  { key: 'skill', label: 'Skill', icon: getSettingsIcon('skill') },
  { key: 'dashboard', label: '数据看板', icon: getSettingsIcon('dashboard') },
]
const settingsRouteBySection: Record<string, string> = {
  agent: 'workspaceSettingsAgent',
  model: 'workspaceSettingsModel',
  knowledge: 'workspaceSettingsKnowledge',
  mcp: 'workspaceSettingsMcp',
  tool: 'workspaceSettingsTool',
  skill: 'workspaceSettingsSkill',
  dashboard: 'workspaceSettingsDashboard',
}
const settingsCenterVisible = computed(() => Boolean(route.meta.settingsSection))
const activeSettingsSection = computed(() => String(route.meta.settingsSection || selectedSettingsSection.value || 'agent'))
const activeSettingsLabel = computed(() => (
  settingsSections.find((section) => section.key === activeSettingsSection.value)?.label || '设置'
))

const toggleSettingsMenu = () => {
  if (!authUnlocked.value) return
  accountMenuOpen.value = false
  settingsMenuOpen.value = !settingsMenuOpen.value
}

const toggleAccountMenu = () => {
  if (!authUnlocked.value) return
  settingsMenuOpen.value = false
  accountMenuOpen.value = !accountMenuOpen.value
}

const openSettingsCenter = (section = 'agent', overridePath = '') => {
  if (!authUnlocked.value) return
  accountMenuOpen.value = false
  const nextSection = settingsSections.some((item) => item.key === section) ? section : 'agent'
  selectedSettingsSection.value = nextSection
  settingsMenuOpen.value = true
  const query = {
    ...route.query,
    settings_turn: String(Date.now()),
  }

  if (overridePath === '/agent/editor') {
    router.push({ name: 'workspaceSettingsAgentEditor', query })
    return
  }

  router.push({ name: settingsRouteBySection[nextSection] || 'workspaceSettingsAgent', query })
}

const openAgentCreator = () => {
  openSettingsCenter('agent', '/agent/editor')
}

const handleOpenSettingsCenter = (event: Event) => {
  const section = (event as CustomEvent<{ section?: string }>).detail?.section || 'model'
  const path = (event as CustomEvent<{ path?: string }>).detail?.path || ''
  openSettingsCenter(section, path)
}

const defaultWorkspaceRoute = () => {
  const defaults = loadWorkspaceDefaults()
  return {
    name: 'workspaceDefaultPage',
    query: {
      mode: defaults.mode,
      execution_mode: defaults.executionMode || 'tool',
      access_scope: defaults.accessScope || 'workspace',
    },
  }
}

const fetchSessions = async () => {
  const requestId = ++fetchSessionsRequestId
  if (!hasAuthToken()) {
    sessions.value = []
    loading.value = false
    return
  }

  try {
    loading.value = sessions.value.length === 0
    const response = await getWorkspaceSessionsAPI()
    if (requestId !== fetchSessionsRequestId) return
    if (response.data.status_code === 200) {
      const sessionModeOverrides = loadWorkspaceSessionModes()
      sessions.value = (response.data.data || [])
        .filter((session: any) => Array.isArray(session.contexts) && session.contexts.length > 0)
        .map((session: any) => {
          const sessionId = session.session_id || session.id
          const agentName = normalizeAgentName(session.agent)
          const inferredMode = inferWorkspaceMode(session)
          const overrideMode = sessionModeOverrides[sessionId]
          const workspaceMode = overrideMode === 'agent' && agentName
            ? 'agent'
            : overrideMode === 'normal'
              ? 'normal'
              : inferredMode
          return {
            sessionId,
            title: deriveSessionTitle(session),
            createTime: session.create_time || session.created_at || new Date().toISOString(),
            agent: agentName,
            workspaceMode,
          }
        })
      expandSelectedSessionSection()
      return
    }

    console.warn('获取会话列表失败')
  } catch (error) {
    if (requestId !== fetchSessionsRequestId) return
    console.error('获取会话列表失败:', error)
  } finally {
    if (requestId === fetchSessionsRequestId) {
      loading.value = false
    }
  }
}

const normalizeAgentAvatar = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/')) return zunoAgentAvatar
  return raw
}

const fetchAgents = async () => {
  if (!hasAuthToken()) {
    agents.value = []
    return
  }

  try {
    const response = await getAgentsAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '获取智能体列表失败')
    }

    agents.value = (response.data.data || []).map((agent: AgentResponse) => ({
      id: agent.agent_id || agent.id || agent.name,
      name: agent.name || '未命名智能体',
      description: agent.description || '暂无描述',
      avatar: normalizeAgentAvatar(agent.logo_url),
    })).filter((agent: SidebarAgentItem) => Boolean(agent.id))
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    agents.value = []
  }
}

const deleteSession = async (sessionId: string, event: Event) => {
  event.stopPropagation()
  if (!authUnlocked.value) return

  try {
    const response = await deleteWorkspaceSessionAPI(sessionId)
    if (response.data.status_code === 200) {
      ElMessage.success('会话已删除')
      removeWorkspaceSessionMode(sessionId)
      await fetchSessions()
      if (selectedSession.value === sessionId) {
        selectedSession.value = ''
        router.push(defaultWorkspaceRoute())
      }
      return
    }

    ElMessage.error('删除会话失败')
  } catch (error) {
    console.error('删除会话失败:', error)
    ElMessage.error('删除会话失败')
  }
}

const selectSession = (session: WorkspaceSessionItem) => {
  if (!authUnlocked.value) return
  if (selectedSession.value !== session.sessionId) pulseNavigationSettling()
  selectedSession.value = session.sessionId
  settingsMenuOpen.value = false
  accountMenuOpen.value = false
  setSidebarSectionExpanded(sessionSectionKey(session), true)
  router.push({
    name: 'workspaceDefaultPage',
    query: {
      session_id: session.sessionId,
      mode: session.workspaceMode,
      execution_mode: route.query.execution_mode || 'tool',
      access_scope: route.query.access_scope || 'workspace',
    },
  })
}

const goWorkspaceHome = () => {
  if (!authUnlocked.value) return
  settingsMenuOpen.value = false
  accountMenuOpen.value = false
  router.push(defaultWorkspaceRoute())
}

const openConversationArchive = () => {
  if (!authUnlocked.value) return
  accountMenuOpen.value = false
  settingsMenuOpen.value = false
  router.push({ name: 'workspaceAccountConversations', query: { account_turn: String(Date.now()) } })
}

const openAccountProfile = () => {
  if (!authUnlocked.value) return
  accountMenuOpen.value = false
  settingsMenuOpen.value = false
  router.push({ name: 'workspaceAccountProfile', query: { account_turn: String(Date.now()) } })
}

const handleLogout = async () => {
  accountMenuOpen.value = false
  try {
    await logoutAPI()
  } catch (error) {
    console.error('调用退出接口失败:', error)
  }

  userStore.logout()
  authUnlocked.value = false
  authUnlocking.value = false
  sessions.value = []
  agents.value = []
  ElMessage.success('已退出登录')
  router.push({ name: 'workspaceDefaultPage', query: { auth: 'login' } })
}

const handleAuthInvalid = () => {
  userStore.clearUserInfo()
  authUnlocked.value = false
  authUnlocking.value = false
  sessions.value = []
  agents.value = []
  settingsMenuOpen.value = false
  accountMenuOpen.value = false
}

const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) target.src = DEFAULT_USER_AVATAR
}

const groupedSessions = computed(() => {
  const groups = new Map<string, WorkspaceSessionItem[]>()
  sessions.value.forEach((session) => {
    const groupName = session.agent || '默认助手'
    if (!groups.has(groupName)) groups.set(groupName, [])
    groups.get(groupName)?.push(session)
  })
  return Array.from(groups.entries()).map(([agent, items]) => ({ agent, items }))
})

const chatSessions = computed(() => sessions.value.filter((session) => session.workspaceMode !== 'agent'))
const agentSessions = (agentName: string) => sessions.value.filter((session) => (
  session.workspaceMode === 'agent'
  && session.agent === agentName
))
const getSidebarPage = (sectionKey: string) => sidebarPages.value[sectionKey] || 1
const setSidebarPage = (sectionKey: string, page: number) => {
  sidebarPages.value = { ...sidebarPages.value, [sectionKey]: page }
}
const paginatedSidebarSessions = (sectionKey: string, list: WorkspaceSessionItem[]) => {
  const page = getSidebarPage(sectionKey)
  const start = (page - 1) * SIDEBAR_PAGE_SIZE
  return list.slice(start, start + SIDEBAR_PAGE_SIZE)
}
const orphanAgentGroups = computed(() => {
  const knownNames = new Set(agents.value.map((agent) => agent.name))
  const groups = groupedSessions.value.filter((group) => (
    group.agent && group.items.some((item) => item.workspaceMode === 'agent') && !knownNames.has(group.agent)
  ))
  return groups.map((group) => ({
    id: group.agent,
    name: group.agent,
    description: '历史智能体会话',
    avatar: zunoAgentAvatar,
  }))
})
const visibleAgents = computed(() => [...agents.value, ...orphanAgentGroups.value])

onMounted(async () => {
  userStore.initUserState()
  authUnlocked.value = hasAuthToken()

  if (authUnlocked.value) {
    await hydrateAuthenticatedWorkspace()
  } else {
    sessions.value = []
    agents.value = []
  }
  window.addEventListener('workspace-session-updated', handleWorkspaceSessionUpdated)
  window.addEventListener('workspace-session-mode-updated', handleWorkspaceSessionUpdated)
  window.addEventListener('workspace-open-settings', handleOpenSettingsCenter)
  window.addEventListener('zuno-auth-invalid', handleAuthInvalid)
  window.addEventListener('resize', handleResponsiveSidebar)
  window.addEventListener('pointerdown', handleWorkspacePointerDown)
})

onBeforeUnmount(() => {
  window.removeEventListener('workspace-session-updated', handleWorkspaceSessionUpdated)
  window.removeEventListener('workspace-session-mode-updated', handleWorkspaceSessionUpdated)
  window.removeEventListener('workspace-open-settings', handleOpenSettingsCenter)
  window.removeEventListener('zuno-auth-invalid', handleAuthInvalid)
  window.removeEventListener('resize', handleResponsiveSidebar)
  window.removeEventListener('pointerdown', handleWorkspacePointerDown)
  if (navigationSettlingTimer) window.clearTimeout(navigationSettlingTimer)
})

watch(
  () => route.query.session_id,
  async () => {
    if (!authUnlocked.value) return
    syncSelectedSessionFromRoute()
    await fetchSessions()
  }
)

watch(settingsCenterVisible, async (visible, wasVisible) => {
  if (!authUnlocked.value) return
  if (!visible && wasVisible) {
    await Promise.all([fetchAgents(), fetchSessions()])
  }
})

watch(() => userStore.isLoggedIn, async () => {
  if (hasAuthToken()) return
  authUnlocked.value = false
  authUnlocking.value = false
  sessions.value = []
  agents.value = []
  settingsMenuOpen.value = false
  accountMenuOpen.value = false
})

watch(sidebarCollapsed, (collapsed) => {
  window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(collapsed))
  if (collapsed) {
    settingsMenuOpen.value = false
    accountMenuOpen.value = false
  }
})

</script>

<template>
  <div class="workspace-container" :class="{ 'navigation-settling': navigationSettling }">
    <button class="mobile-rail-toggle mobile-only" type="button" @click="sidebarCollapsed = !sidebarCollapsed">
      <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
    </button>

    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }" :style="historyPanelStyle">
      <div v-if="sidebarCollapsed" class="sidebar-rail">
        <button class="rail-toggle desktop-only" type="button" @click="sidebarCollapsed = false">
          <el-icon><Expand /></el-icon>
        </button>
      </div>

      <div v-if="!sidebarCollapsed" class="sidebar-body">
        <div class="brand-block">
          <button class="brand-icon" type="button" @click="goWorkspaceHome" title="返回主页">
            <img :src="zunoAgentAvatar" alt="Zuno" />
          </button>
          <div class="brand-copy">
            <strong>Zuno AI</strong>
          </div>
          <button class="rail-toggle desktop-only" type="button" @click="sidebarCollapsed = true">
            <el-icon><Fold /></el-icon>
          </button>
        </div>

        <div class="sidebar-state-slot">
          <Transition name="sidebar-unlock">
            <div v-if="workspaceNavVisible" key="unlocked" class="sidebar-unlocked">
        <button class="primary-new-chat" type="button" @click="startNewConversation()">
          <el-icon><Plus /></el-icon>
          <span>New Chat</span>
        </button>

        <div class="nav-scroll">
          <section class="nav-section">
            <div class="section-title chat-title">
              <button
                class="section-title-main"
                type="button"
                :aria-expanded="isSidebarSectionExpanded(CHAT_SECTION_KEY)"
                @click="toggleSidebarSection(CHAT_SECTION_KEY)"
              >
                <span class="section-chevron" :class="{ expanded: isSidebarSectionExpanded(CHAT_SECTION_KEY) }">›</span>
                <span>Chat</span>
              </button>
              <button class="section-plus" type="button" title="新建普通聊天" @click.stop="startNewConversation()">
                <el-icon><Plus /></el-icon>
              </button>
            </div>

            <Transition name="nav-collapse">
              <div v-if="isSidebarSectionExpanded(CHAT_SECTION_KEY)" class="nav-section-body">
                <div v-if="loading" class="sidebar-note">正在加载会话...</div>
                <button
                  v-for="session in paginatedSidebarSessions(CHAT_SECTION_KEY, chatSessions)"
                  :key="session.sessionId"
                  :class="['nav-row', { active: selectedSession === session.sessionId }]"
                  type="button"
                  @click="selectSession(session)"
                >
                  <span>{{ session.title }}</span>
                  <small>{{ formatTime(session.createTime) }}</small>
                  <button class="delete-btn" type="button" @click="deleteSession(session.sessionId, $event)">×</button>
                </button>
                <ZunoMiniPager
                  v-if="!loading"
                  class="sidebar-pager"
                  align="center"
                  :page="getSidebarPage(CHAT_SECTION_KEY)"
                  :total="chatSessions.length"
                  :page-size="SIDEBAR_PAGE_SIZE"
                  @update:page="setSidebarPage(CHAT_SECTION_KEY, $event)"
                />
                <div v-if="!loading && chatSessions.length === 0" class="sidebar-note">还没有普通聊天记录</div>
              </div>
            </Transition>
          </section>

          <section v-for="agent in visibleAgents" :key="agent.id" class="nav-section">
            <div class="section-title agent-title">
              <button
                class="section-title-main agent-title-main"
                type="button"
                :aria-expanded="isSidebarSectionExpanded(agentSectionKey(agent.name))"
                @click="toggleSidebarSection(agentSectionKey(agent.name))"
              >
                <span class="section-chevron" :class="{ expanded: isSidebarSectionExpanded(agentSectionKey(agent.name)) }">›</span>
                <span>{{ agent.name }}</span>
              </button>
              <button class="section-plus" type="button" :title="`以 ${agent.name} 新开对话`" @click.stop="startNewConversation(agent)">
                <el-icon><Plus /></el-icon>
              </button>
            </div>

            <Transition name="nav-collapse">
              <div v-if="isSidebarSectionExpanded(agentSectionKey(agent.name))" class="nav-section-body">
                <button
                  v-for="session in paginatedSidebarSessions(agentSectionKey(agent.name), agentSessions(agent.name))"
                  :key="session.sessionId"
                  :class="['nav-row', { active: selectedSession === session.sessionId }]"
                  type="button"
                  @click="selectSession(session)"
                >
                  <span>{{ session.title }}</span>
                  <small>{{ formatTime(session.createTime) }}</small>
                  <button class="delete-btn" type="button" @click="deleteSession(session.sessionId, $event)">×</button>
                </button>
                <ZunoMiniPager
                  class="sidebar-pager"
                  align="center"
                  :page="getSidebarPage(agentSectionKey(agent.name))"
                  :total="agentSessions(agent.name).length"
                  :page-size="SIDEBAR_PAGE_SIZE"
                  @update:page="setSidebarPage(agentSectionKey(agent.name), $event)"
                />
                <div v-if="agentSessions(agent.name).length === 0" class="sidebar-note">暂无对话记录</div>
              </div>
            </Transition>
          </section>
        </div>

        <Transition name="settings-float">
          <nav v-if="settingsMenuOpen" class="settings-float" aria-label="设置入口">
            <button
              v-for="section in settingsSections"
              :key="section.key"
              type="button"
              :class="['settings-float-item', { active: activeSettingsSection === section.key }]"
              @click="openSettingsCenter(section.key)"
            >
              <img class="settings-float-icon" :src="section.icon" :alt="section.label" />
              <span>{{ section.label }}</span>
            </button>
          </nav>
        </Transition>

        <div class="sidebar-footer">
          <button
            :class="['settings-entry', { active: settingsMenuOpen || settingsCenterVisible }]"
            type="button"
            @click="toggleSettingsMenu"
          >
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </button>

          <Transition name="account-float">
            <nav v-if="accountMenuOpen" class="account-float" aria-label="账号入口">
              <button class="account-float-item" type="button" @click="openConversationArchive">
                <img class="account-float-icon" :src="accountConversationIcon" alt="" aria-hidden="true" />
                <span>对话记录</span>
              </button>
              <button class="account-float-item" type="button" @click="openAccountProfile">
                <img class="account-float-icon" :src="accountProfileIcon" alt="" aria-hidden="true" />
                <span>个人资料</span>
              </button>
              <span class="account-float-divider" aria-hidden="true" />
              <button class="account-float-item danger" type="button" @click="handleLogout">
                <img class="account-float-icon" :src="accountLogoutIcon" alt="" aria-hidden="true" />
                <span>退出登录</span>
              </button>
            </nav>
          </Transition>

          <button
            :class="['account-entry', { active: accountMenuOpen }]"
            type="button"
            aria-label="账号菜单"
            :aria-expanded="accountMenuOpen"
            @click="toggleAccountMenu"
          >
            <span class="user-avatar-wrapper">
              <div class="user-avatar">
                <img
                  :src="userAvatarSrc"
                  alt="用户头像"
                  @error="handleAvatarError"
                  referrerpolicy="no-referrer"
                />
              </div>
            </span>
          </button>
        </div>
          </div>

            <div v-else key="locked" class="sidebar-locked">
              <div class="sidebar-mascot-slot" aria-label="Zuno AI">
                <SidebarMascot />
              </div>
            </div>
          </Transition>
        </div>
      </div>

      <div
        v-if="!sidebarCollapsed"
        class="sidebar-resize-handle"
        role="separator"
        aria-label="调整侧边栏宽度"
        aria-orientation="vertical"
        tabindex="0"
        @pointerdown="startHistoryResize"
        @keydown="handleHistorySeparatorKeydown"
      />
    </aside>

    <main class="content">
      <router-view v-slot="{ Component }">
        <Transition name="workspace-main-swap">
          <WorkspaceAuthGate
            v-if="!authUnlocked"
            :initial-mode="authInitialMode"
            :unlocking="authUnlocking"
            @authenticated="handleAuthenticated"
          />
          <component :is="Component" v-else />
        </Transition>
      </router-view>
    </main>
  </div>
</template>

<style lang="scss" scoped>
.workspace-container {
  --workspace-sidebar-width: 300px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.92), transparent 42%),
    linear-gradient(180deg, #f5efe4 0%, #efe8dc 100%);
  color: #33271f;
}

.workspace-nav {
  height: 62px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(244, 236, 225, 0.94);
  border-bottom: 1px solid rgba(212, 188, 159, 0.24);
  backdrop-filter: blur(16px);
}

.brand-side {
  display: flex;
  align-items: center;
}

.brand-mark {
  border: none;
  background: transparent;
  padding: 0;
  cursor: pointer;
}

.brand-logo-img {
  height: 54px;
  width: auto;
  display: block;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-wrapper {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: transparent;
  border: 0;
  cursor: pointer;
  box-shadow: none;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 0;
  background: transparent;
  overflow: hidden;
  display: grid;
  place-items: center;
  box-shadow: none;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: inherit;
}

.workspace-main {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
  background: #fffaf4;
}

.sidebar {
  position: relative;
  width: var(--workspace-sidebar-width);
  flex: 0 0 var(--workspace-sidebar-width);
  display: flex;
  flex-direction: column;
  background: #f7f1e8;
  border-right: 1px solid rgba(214, 198, 178, 0.58);
  transition: width 0.22s ease, flex-basis 0.22s ease;
  min-width: 0;
}

.sidebar.collapsed {
  width: 52px;
  flex-basis: 52px;
}

.sidebar-resize-handle {
  position: absolute;
  top: 0;
  right: -7px;
  z-index: 5;
  width: 14px;
  height: 100%;
  cursor: col-resize;
  outline: none;
  touch-action: none;
  user-select: none;
}

.sidebar-resize-handle::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 6px;
  width: 1px;
  background: rgba(214, 198, 178, 0.72);
  transition: background 0.16s ease, box-shadow 0.16s ease;
}

.sidebar-resize-handle:hover::before,
.sidebar-resize-handle:focus-visible::before {
  background: rgba(198, 108, 50, 0.7);
  box-shadow: 0 0 0 3px rgba(198, 108, 50, 0.12);
}

.sidebar-rail {
  width: 100%;
  flex: 0 0 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 8px;
}

.sidebar-body {
  flex: 1;
  min-width: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  overflow: visible;
}

.rail-toggle {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 9px;
  background: rgba(255, 251, 246, 0.9);
  color: #7f6248;
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(130, 71, 31, 0.06);
}

.sidebar-head {
  padding: 12px 14px 10px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
}

.sidebar-title-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.sidebar-title-wrap strong {
  font-size: 14px;
  font-weight: 650;
  color: #34271f;
  white-space: nowrap;
}

.sidebar-title-wrap span {
  padding: 3px 7px;
  border-radius: 999px;
  background: rgba(212, 138, 79, 0.12);
  color: #9b6a42;
  font-size: 11px;
}

.sidebar-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.new-session-btn {
  border: none;
  background: rgba(255, 251, 246, 0.72);
  color: #5f4e40;
  border-radius: 8px;
  padding: 0 9px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex: 1 1 auto;
  cursor: pointer;
  font-size: 13px;
  justify-content: flex-start;
}

.new-session-btn span {
  white-space: nowrap;
}

.new-session-btn:hover {
  border-color: rgba(212, 138, 79, 0.45);
  color: #a85f2d;
}

.sidebar-toggle {
  flex: 0 0 auto;
}

.session-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 4px 8px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading-state,
.empty-state {
  min-height: 160px;
  display: grid;
  place-items: center;
  color: #8a745f;
  text-align: center;
}

.empty-mark {
  font-size: 22px;
  opacity: 0.55;
}

.session-group {
  display: grid;
  gap: 2px;
}

.group-head {
  padding: 8px 8px 4px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #8d8074;
  font-size: 12px;
  font-weight: 500;
}

.group-head span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-head small {
  min-width: 18px;
  height: 18px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  background: rgba(80, 72, 64, 0.06);
  color: #8d8074;
  font-size: 11px;
}

.session-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease;
}

.session-card:hover {
  background: rgba(255, 251, 246, 0.68);
}

.session-card.active {
  border-color: transparent;
  background: rgba(226, 218, 208, 0.72);
}

.session-icon {
  width: 26px;
  height: 26px;
  flex: 0 0 auto;
  border-radius: 7px;
  background: rgba(255, 251, 246, 0.84);
  border: 1px solid rgba(226, 210, 192, 0.72);
  display: grid;
  place-items: center;
}

.session-icon img {
  width: 18px;
  height: 18px;
}

.session-info {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 4px;
}

.session-title-row {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.session-title {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  font-weight: 500;
  color: #3c2f25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mode-tag {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  min-height: 17px;
  padding: 0 5px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 500;
  border: 1px solid rgba(217, 190, 166, 0.7);
  color: #7e644c;
  background: rgba(255, 251, 246, 0.8);
}

.mode-tag.agent {
  color: #a85f2d;
  border-color: rgba(201, 108, 45, 0.28);
  background: rgba(212, 138, 79, 0.12);
}

.session-time {
  font-size: 12px;
  color: #8d8074;
}

.delete-btn {
  border: none;
  background: transparent;
  color: #9f8b78;
  font-size: 15px;
  cursor: pointer;
  width: 22px;
  height: 22px;
  border-radius: 7px;
  opacity: 0;
  transition: opacity 0.16s ease, background 0.16s ease;
}

.session-card:hover .delete-btn,
.session-card.active .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(212, 138, 79, 0.12);
  color: #a8572c;
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #fffaf4;
}

.content :deep(.workspace-chat) {
  flex: 1;
  min-height: 0;
}

.settings-center-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(40, 31, 24, 0.22);
  backdrop-filter: blur(10px);
}

.settings-center {
  width: min(90vw, 1480px);
  height: min(90vh, 920px);
  min-width: min(960px, calc(100vw - 32px));
  min-height: min(620px, calc(100vh - 32px));
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-radius: 18px;
  border: 1px solid rgba(222, 204, 184, 0.92);
  background: rgba(255, 253, 250, 0.98);
  box-shadow: 0 28px 80px rgba(53, 36, 22, 0.22);
}

.settings-center-head {
  height: 58px;
  flex: 0 0 auto;
  padding: 0 18px 0 22px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid rgba(229, 212, 194, 0.82);
}

.settings-center-kicker {
  display: block;
  margin-bottom: 3px;
  color: #9a7658;
  font-size: 11px;
}

.settings-center-head strong {
  color: #302820;
  font-size: 18px;
}

.settings-center-close {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 999px;
  background: rgba(247, 239, 230, 0.92);
  color: #7b624a;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
}

.settings-center-body {
  flex: 1;
  min-height: 0;
  display: flex;
  background: rgba(250, 246, 240, 0.95);
}

.settings-center-tabs {
  width: 148px;
  flex: 0 0 148px;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-right: 1px solid rgba(229, 212, 194, 0.82);
  background: rgba(245, 237, 226, 0.88);
}

.settings-tab {
  height: 38px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #735d48;
  text-align: left;
  padding: 0 12px;
  cursor: pointer;
  font-size: 14px;
}

.settings-tab:hover,
.settings-tab.active {
  background: rgba(255, 251, 246, 0.94);
  color: #b76332;
}

.settings-frame {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: none;
  background: #fffaf4;
}

.mobile-only {
  display: none;
}

@media (max-width: 900px) {
  .workspace-container {
    --workspace-sidebar-width: 220px;
  }

  .sidebar-head {
    padding-inline: 10px;
  }

  .session-list {
    padding-inline: 6px;
  }

  .session-card {
    gap: 7px;
    padding: 7px 6px;
  }

  .mode-tag {
    font-size: 10px;
    padding-inline: 5px;
  }
}

:global(body.zuno-is-resizing) {
  cursor: col-resize;
  user-select: none;
}

@media (max-width: 480px) {
  .workspace-nav {
    padding: 0 12px;
  }

  .mobile-only {
    display: grid;
  }

  .desktop-only {
    display: none;
  }

  .sidebar {
    position: absolute;
    left: 0;
    top: 58px;
    bottom: 0;
    z-index: 20;
    width: min(280px, calc(100vw - 56px));
    flex-basis: min(280px, calc(100vw - 56px));
    box-shadow: 10px 0 30px rgba(62, 44, 28, 0.12);
  }

  .sidebar-resize-handle {
    display: none;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}

.workspace-container {
  --workspace-sidebar-width: 288px;
  height: 100vh;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  background:
    radial-gradient(circle at 72% 22%, rgba(255, 255, 255, 0.9), transparent 34%),
    linear-gradient(135deg, #fbfbfd 0%, #f4f5f7 48%, #ffffff 100%);
  color: #111827;
}

.sidebar {
  width: var(--workspace-sidebar-width);
  flex: 0 0 var(--workspace-sidebar-width);
  background: rgba(255, 255, 255, 0.72);
  border-right: 1px solid rgba(226, 232, 240, 0.62);
  box-shadow: 26px 0 70px rgba(15, 23, 42, 0.05);
  backdrop-filter: blur(30px);
}

.sidebar.collapsed {
  width: 56px;
  flex-basis: 56px;
  transform: none;
}

.sidebar-body {
  height: 100%;
  padding: 28px 24px 22px;
  gap: 22px;
}

.brand-block {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) 30px;
  align-items: center;
  gap: 14px;
  padding-bottom: 22px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.72);
}

.brand-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  box-shadow: none;
}

.brand-icon img {
  width: 48px;
  height: 48px;
  object-fit: contain;
  filter: none;
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 0;
  align-content: center;
}

.brand-copy strong {
  color: #0f172a;
  font-size: 22px;
  font-weight: 700;
  line-height: 1.05;
}

.brand-copy span {
  color: #64748b;
  font-size: 14px;
  line-height: 1.2;
}

.rail-toggle,
.mobile-rail-toggle {
  border: none;
  color: #64748b;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: none;
}

.primary-new-chat {
  width: 100%;
  min-height: 48px;
  border: none;
  border-radius: 8px;
  background: #f59e0b;
  color: #ffffff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 18px 34px rgba(245, 158, 11, 0.22);
  transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.primary-new-chat:hover {
  background: #e89105;
  transform: translateY(-1px);
  box-shadow: 0 22px 38px rgba(245, 158, 11, 0.28);
}

.nav-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: grid;
  align-content: start;
  gap: 24px;
  padding-right: 2px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.45) transparent;
}

.nav-section {
  display: grid;
  gap: 8px;
}

.section-title {
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #f59e0b;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.agent-title-main {
  min-width: 0;
  border: none;
  background: transparent;
  color: inherit;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
  font: inherit;
}

.agent-title-main span,
.section-title > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-plus {
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  border: none;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #94a3b8;
  background: transparent;
  cursor: pointer;
  transition: color 0.18s ease, background 0.18s ease;
}

.section-plus:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.nav-row {
  position: relative;
  width: 100%;
  min-height: 44px;
  border: none;
  border-radius: 8px;
  padding: 0 38px 0 16px;
  background: transparent;
  color: #8da0bc;
  display: grid;
  align-content: center;
  gap: 2px;
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}

.nav-row span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  font-weight: 650;
}

.nav-row small {
  color: #aab7c8;
  font-size: 11px;
}

.nav-row:hover,
.nav-row.active {
  color: #6b7f9a;
  background: rgba(245, 158, 11, 0.06);
}

.nav-row.muted {
  color: #9aa9bd;
}

.delete-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px;
  height: 22px;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  opacity: 0;
}

.nav-row:hover .delete-btn,
.nav-row.active .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #ba1a1a;
  background: #ffdad6;
}

.sidebar-note {
  padding: 10px 16px;
  color: #94a3b8;
  font-size: 13px;
}

.settings-sidebar-head {
  display: grid;
  gap: 14px;
}

.settings-sidebar-head strong {
  color: #111827;
  font-size: 24px;
}

.back-settings {
  justify-self: start;
  border: none;
  background: rgba(148, 163, 184, 0.12);
  color: #64748b;
  border-radius: 999px;
  min-height: 34px;
  padding: 0 12px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
}

.settings-nav {
  flex: 1;
  display: grid;
  align-content: start;
  gap: 8px;
}

.settings-tab {
  width: 100%;
  min-height: 42px;
  border: none;
  border-radius: 8px;
  padding: 0 16px;
  background: transparent;
  color: #64748b;
  text-align: left;
  font-size: 15px;
  font-weight: 650;
  cursor: pointer;
}

.settings-tab:hover,
.settings-tab.active {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.sidebar-footer {
  position: relative;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
  padding-top: 22px;
  border-top: 1px solid rgba(226, 232, 240, 0.72);
}

.settings-entry {
  border: none;
  background: transparent;
  color: #64748b;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-height: 38px;
  padding: 0 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 650;
}

.settings-entry:hover {
  color: #f59e0b;
  background: transparent;
}

.settings-entry.active {
  color: #b45309;
  background: transparent;
}

.settings-float {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 62px;
  z-index: 11;
  display: grid;
  gap: 3px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.76), rgba(255, 247, 238, 0.48)),
    rgba(255, 255, 255, 0.42);
  box-shadow:
    0 22px 56px rgba(15, 23, 42, 0.14),
    0 10px 26px rgba(180, 83, 9, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px) saturate(1.45);
  transform-origin: 50% 100%;
}

.settings-float::before {
  content: '';
  position: absolute;
  inset: 1px;
  pointer-events: none;
  border-radius: 15px;
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 255, 255, 0.82), transparent 38%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), transparent 58%);
}

.settings-float-item {
  position: relative;
  z-index: 1;
  min-height: 32px;
  border: none;
  border-radius: 10px;
  padding: 0 10px 0 8px;
  background: transparent;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  text-align: left;
  cursor: pointer;
  font-size: 12px;
  font-weight: 560;
  line-height: 1;
  transition: color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.settings-float-icon {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  object-fit: contain;
  filter: drop-shadow(0 5px 9px rgba(245, 158, 11, 0.16));
}

.settings-float-item:hover,
.settings-float-item.active {
  color: #a16207;
  background: rgba(255, 255, 255, 0.66);
  box-shadow:
    0 9px 22px rgba(146, 64, 14, 0.08),
    inset 0 0 0 1px rgba(245, 158, 11, 0.12);
}

.settings-float-item:active {
  transform: translateY(1px);
}

.settings-float-enter-active,
.settings-float-leave-active {
  transition: opacity 0.2s ease, transform 0.22s cubic-bezier(0.2, 0.8, 0.2, 1), filter 0.22s ease;
}

.settings-float-enter-from,
.settings-float-leave-to {
  opacity: 0;
  filter: blur(4px);
  transform: translateY(16px) scale(0.96);
}

.account-entry {
  border: 0;
  background: transparent;
  padding: 0;
  display: inline-grid;
  place-items: center;
  cursor: pointer;
  border-radius: 14px;
}

.account-entry.active .user-avatar-wrapper,
.account-entry:hover .user-avatar-wrapper {
  transform: translateY(-1px);
}

.account-float {
  position: absolute;
  right: 2px;
  bottom: 54px;
  z-index: 13;
  width: 124px;
  display: grid;
  gap: 2px;
  padding: 7px 6px;
  border: 1px solid rgba(255, 255, 255, 0.72);
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.76), rgba(255, 247, 238, 0.48)),
    rgba(255, 255, 255, 0.42);
  box-shadow:
    0 22px 56px rgba(15, 23, 42, 0.14),
    0 10px 26px rgba(180, 83, 9, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px) saturate(1.45);
  transform-origin: 88% 100%;
  overflow: hidden;
  isolation: isolate;
}

.account-float::before {
  content: '';
  position: absolute;
  inset: 1px;
  z-index: -1;
  pointer-events: none;
  border-radius: 15px;
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 255, 255, 0.82), transparent 38%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), transparent 58%);
}

.account-float-item {
  position: relative;
  z-index: 1;
  min-height: 29px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  padding: 0 6px;
  text-align: left;
  cursor: pointer;
  font-size: 12px;
  font-weight: 560;
  line-height: 1;
  transition: color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.account-float-icon {
  width: 16px;
  height: 16px;
  display: block;
  object-fit: contain;
  opacity: 0.86;
  transition: opacity 160ms ease, transform 160ms ease;
}

.account-float-item:hover {
  color: #a16207;
  background: rgba(255, 255, 255, 0.62);
  box-shadow:
    0 9px 22px rgba(146, 64, 14, 0.07),
    inset 0 0 0 1px rgba(245, 158, 11, 0.1);
}

.account-float-item:hover .account-float-icon {
  opacity: 1;
  transform: translateY(-1px);
}

.account-float-item.danger:hover {
  color: #dc2626;
}

.account-float-divider {
  height: 1px;
  margin: 4px 4px;
  background: rgba(226, 232, 240, 0.62);
}

.account-float-enter-active,
.account-float-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.26s cubic-bezier(0.2, 0.8, 0.2, 1),
    filter 0.24s ease;
}

.account-float-enter-from,
.account-float-leave-to {
  opacity: 0;
  filter: blur(6px);
  transform: translateY(14px) scale(0.95);
}

.user-avatar-wrapper {
  width: 40px;
  height: 40px;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  transition: transform 160ms ease, filter 160ms ease;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 13px;
  border-color: transparent;
  box-shadow: none;
  background: transparent !important;
}

.account-entry.active .user-avatar,
.account-entry:hover .user-avatar {
  filter: drop-shadow(0 12px 18px rgba(245, 158, 11, 0.18));
}

.content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.settings-frame {
  width: 100%;
  height: 100%;
  border: none;
  background: #fbfbfd;
}

.sidebar-resize-handle::before {
  background: transparent;
}

.sidebar-resize-handle:hover::before,
.sidebar-resize-handle:focus-visible::before {
  background: rgba(245, 158, 11, 0.45);
}

@media (max-width: 760px) {
  .workspace-container {
    --workspace-sidebar-width: 286px;
  }

  .mobile-only {
    display: grid;
  }

  .mobile-rail-toggle {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 40;
    width: 40px;
    height: 40px;
    border-radius: 12px;
  }

  .sidebar {
    position: fixed;
    inset: 0 auto 0 0;
    z-index: 35;
    width: min(286px, calc(100vw - 52px));
    flex-basis: auto;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .sidebar-body {
    padding: 22px 18px;
  }

  .sidebar-resize-handle {
    display: none;
  }
}

/* Minimal sidebar refinement, keeping the workspace interaction model intact. */
.workspace-container {
  --workspace-sidebar-width: 264px;
  font-family: var(--zuno-font-sans);
  background:
    radial-gradient(circle at 74% 20%, rgba(255, 255, 255, 0.88), transparent 34%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.055), transparent 30%),
    #f9f9fb;
  color: #0f172a;
}

.sidebar {
  background: rgba(255, 255, 255, 0.7);
  border-right: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 40px 0 80px -20px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(30px);
  container-type: inline-size;
}

  .sidebar-body {
    padding: 18px;
    gap: 14px;
  }

  .sidebar-unlocked,
  .sidebar-locked {
    flex: 1;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .sidebar-locked {
    justify-content: flex-start;
    align-items: center;
    padding: clamp(178px, calc(43vh - 96px), 318px) 0 24px;
  }

  .sidebar-mascot-slot {
    width: 100%;
    max-width: min(100%, 320px);
    margin: 0;
    display: grid;
    place-items: center;
    overflow: visible;
    transform-origin: center center;
  }

  .sidebar-unlock-enter-active,
  .sidebar-unlock-leave-active {
    transition: opacity 0.68s ease, transform 0.68s cubic-bezier(.16, .78, .18, 1), filter 0.68s ease;
  }

  .sidebar-unlock-enter-from {
    opacity: 0;
    transform: translateY(18px) scale(0.985);
    filter: blur(8px);
  }

  .sidebar-unlock-leave-to {
    opacity: 0;
    transform: translateY(-18px) scale(0.94);
    filter: blur(10px);
  }

  .sidebar-unlock-leave-active .sidebar-mascot-slot {
    animation: zuno-bot-release 0.68s cubic-bezier(.16, .78, .18, 1) both;
  }


  @keyframes zuno-bot-release {
    0% {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    38% {
      opacity: 1;
      transform: translateY(-3px) scale(1.018);
    }
    100% {
      opacity: 0;
      transform: translateY(-18px) scale(0.82);
    }
  }


  @media (prefers-reduced-motion: reduce) {
    .sidebar-mascot-slot {
      animation: none;
    }
  }

  .workspace-main-swap-enter-active,
  .workspace-main-swap-leave-active {
    transition: opacity 0.62s ease, transform 0.62s cubic-bezier(.2, .72, .18, 1), filter 0.62s ease;
  }

  .workspace-main-swap-enter-from {
    opacity: 0;
    transform: translateY(26px) scale(0.992);
    filter: blur(12px);
  }

  .workspace-main-swap-leave-to {
    opacity: 0;
    transform: translateY(-18px) scale(0.99);
    filter: blur(10px);
  }

.brand-block {
  grid-template-columns: 34px minmax(0, 1fr) 22px;
  gap: 10px;
  padding-bottom: 0;
  border-bottom: none;
}

.brand-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: transparent;
  box-shadow: none;
}

.brand-icon img {
  width: 34px;
  height: 34px;
  filter: none;
}

.brand-copy {
  gap: 0;
  align-content: center;
}

.brand-copy strong {
  color: #0f172a;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.18;
  letter-spacing: 0;
}

.brand-copy span {
  color: #94a3b8;
  font-size: 11px;
  line-height: 1.25;
}

.rail-toggle {
  width: 24px;
  height: 24px;
  color: #94a3b8;
  background: transparent;
}

.primary-new-chat {
  min-height: 36px;
  gap: 8px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.primary-new-chat:hover {
  box-shadow: 0 12px 24px rgba(245, 158, 11, 0.22);
}

.nav-scroll {
  gap: 16px;
  padding-top: 2px;
}

.nav-section {
  gap: 6px;
}

.section-title {
  min-height: 20px;
  padding: 0 2px 0 10px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.agent-title-main {
  gap: 8px;
}

.section-plus {
  width: 20px;
  height: 20px;
  flex-basis: 20px;
  color: #94a3b8;
  border-radius: 7px;
}

.nav-row {
  min-height: 28px;
  padding: 0 28px 0 10px;
  color: #94a3b8;
  gap: 0;
}

.nav-row span {
  font-size: 12px;
  font-weight: 500;
  line-height: 1.35;
}

.nav-row small {
  display: none;
}

.nav-row:hover,
.nav-row.active {
  background: rgba(245, 158, 11, 0.075);
}

.nav-row:hover {
  color: #64748b;
}

.nav-row.active {
  color: #f59e0b;
}

.nav-row.active span {
  color: #f59e0b;
  font-weight: 650;
}

.nav-row.muted {
  min-height: auto;
  padding-block: 5px;
  color: #a3b1c2;
}

.delete-btn {
  right: 6px;
  width: 20px;
  height: 20px;
  border-radius: 6px;
  color: #cbd5e1;
}

.sidebar-note {
  padding: 6px 10px;
  color: #a3b1c2;
  font-size: 11px;
}

.section-title-main {
  min-width: 0;
  flex: 1 1 auto;
  border: 0;
  background: transparent;
  color: inherit;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 0;
  text-align: left;
  cursor: pointer;
}

.section-title-main > span:not(.section-chevron) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-chevron {
  width: 12px;
  flex: 0 0 12px;
  color: #c4cfdd;
  font-size: 14px;
  line-height: 1;
  transform: rotate(0deg);
  transform-origin: center;
  transition: transform 0.2s cubic-bezier(0.2, 0.82, 0.18, 1), color 0.18s ease;
}

.section-chevron.expanded {
  color: #c4cfdd;
  transform: rotate(90deg);
}

.nav-section-body {
  min-width: 0;
  display: grid;
  gap: 6px;
  overflow: hidden;
}

.nav-collapse-enter-active,
.nav-collapse-leave-active {
  max-height: 420px;
  overflow: hidden;
  transition:
    max-height 0.22s cubic-bezier(0.2, 0.82, 0.18, 1),
    opacity 0.18s ease,
    transform 0.18s ease;
}

.nav-collapse-enter-from,
.nav-collapse-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-3px);
}

.nav-collapse-enter-to,
.nav-collapse-leave-from {
  max-height: 420px;
  opacity: 1;
  transform: translateY(0);
}

.sidebar-footer {
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.58);
}

.settings-entry {
  min-height: 30px;
  padding: 0 6px;
  gap: 8px;
  color: #64748b;
  font-size: 12.5px;
  font-weight: 500;
}

.user-avatar-wrapper {
  width: 40px;
  height: 40px;
  box-shadow: none !important;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 13px;
}

.settings-sidebar-head strong {
  font-size: 22px;
  font-weight: 600;
}

.settings-tab {
  min-height: 38px;
  padding: 0 12px;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.settings-frame {
  background: #f9f9fb;
}

.settings-content {
  background:
    radial-gradient(circle at 58% 24%, rgba(255, 255, 255, 0.9), transparent 33%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.055), transparent 30%),
    #f9f9fb;
}

.settings-content-shell {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 28px 38px 64px 30px;
  color: #0f172a;
  scrollbar-gutter: stable both-edges;
  scrollbar-width: thin;
  scrollbar-color: rgba(120, 113, 108, 0.2) transparent;
}

.settings-content-shell::-webkit-scrollbar {
  width: 16px;
}

.settings-content-shell::-webkit-scrollbar-track {
  margin: 18px 0 28px;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.22), rgba(255, 247, 237, 0.16)),
    rgba(255, 255, 255, 0.12);
}

.settings-content-shell::-webkit-scrollbar-thumb {
  min-height: 56px;
  border: 6px solid transparent;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(146, 64, 14, 0.24), rgba(120, 113, 108, 0.18))
    content-box;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.settings-content-shell::-webkit-scrollbar-thumb:hover {
  background:
    linear-gradient(180deg, rgba(146, 64, 14, 0.36), rgba(120, 113, 108, 0.28))
    content-box;
}

.settings-thread {
  width: min(1080px, 100%);
  margin: 0 auto;
  display: grid;
  align-content: start;
}

.settings-message {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  align-items: start;
  gap: 12px;
}

.settings-message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: var(--zuno-glass-card);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: var(--zuno-shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(18px);
}

.settings-message-avatar img {
  width: 22px;
  height: 22px;
  object-fit: contain;
}

.settings-message-stack {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.settings-message-meta {
  min-height: 24px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 12px;
}

.settings-message-meta strong {
  color: #0f172a;
  font-size: 13px;
  font-weight: 650;
}

.settings-bubble {
  min-width: 0;
  padding: 18px;
  border-radius: var(--zuno-radius-composer) var(--zuno-radius-composer) var(--zuno-radius-composer) 10px;
  border: 1px solid var(--zuno-glass-border);
  background: var(--zuno-glass-surface);
  box-shadow: var(--zuno-shadow-composer), inset 0 1px 0 rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(28px);
}

.settings-bubble-enter-active,
.settings-bubble-leave-active {
  transition: opacity 0.2s ease, transform 0.24s cubic-bezier(0.2, 0.8, 0.2, 1), filter 0.24s ease;
}

.settings-bubble-enter-from {
  opacity: 0;
  filter: blur(5px);
  transform: translateY(16px) scale(0.985);
}

.settings-bubble-leave-to {
  opacity: 0;
  filter: blur(3px);
  transform: translateY(-6px) scale(0.995);
}

.settings-bubble :deep(.agent-page),
.settings-bubble :deep(.agent-editor-page),
.settings-bubble :deep(.model-page),
.settings-bubble :deep(.knowledge-page),
.settings-bubble :deep(.knowledge-file-page),
.settings-bubble :deep(.knowledge-config-page),
.settings-bubble :deep(.mcp-page),
.settings-bubble :deep(.tool-page),
.settings-bubble :deep(.skill-page),
.settings-bubble :deep(.dashboard-page) {
  max-width: none;
  margin: 0;
  padding: 0 !important;
  gap: 14px !important;
  font-family: var(--zuno-font-sans);
}

.settings-bubble :deep(.agent-hero),
.settings-bubble :deep(.page-header),
.settings-bubble :deep(.page-hero),
.settings-bubble :deep(.hero-card) {
  align-items: flex-start;
  padding: 0 0 12px !important;
  border: none !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.72) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.logo-panel),
.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.mcp-card),
.settings-bubble :deep(.tool-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.kpi-card),
.settings-bubble :deep(.panel-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.config-card),
.settings-bubble :deep(.preview-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.summary-block) {
  border: 1px solid rgba(226, 232, 240, 0.82) !important;
  border-radius: var(--zuno-radius-card) !important;
  background: var(--zuno-glass-card) !important;
  box-shadow: var(--zuno-shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(18px);
}

.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.preview-card) {
  padding: 12px !important;
}

.settings-bubble :deep(.hero-actions),
.settings-bubble :deep(.header-actions),
.settings-bubble :deep(.card-actions),
.settings-bubble :deep(.filter-bar),
.settings-bubble :deep(.toolbar-card) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 10px !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(h2),
.settings-bubble :deep(h3) {
  color: #0f172a !important;
  letter-spacing: 0 !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(.agent-hero h2),
.settings-bubble :deep(.hero-card h2),
.settings-bubble :deep(.page-hero h1) {
  margin: 0 !important;
  font-size: 21px !important;
  font-weight: 650 !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(h2) {
  font-size: 16px !important;
  font-weight: 650 !important;
}

.settings-bubble :deep(h3),
.settings-bubble :deep(.card-title),
.settings-bubble :deep(.side-title-row strong),
.settings-bubble :deep(.profile-meta strong) {
  font-size: 14px !important;
  font-weight: 620 !important;
}

.settings-bubble :deep(p),
.settings-bubble :deep(.meta-row),
.settings-bubble :deep(.scope-text),
.settings-bubble :deep(.skill-meta),
.settings-bubble :deep(.summary-item span),
.settings-bubble :deep(.card-subtitle),
.settings-bubble :deep(.profile-meta span),
.settings-bubble :deep(.empty-text),
.settings-bubble :deep(.tool-description),
.settings-bubble :deep(.server-subtitle),
.settings-bubble :deep(.server-hint) {
  color: #64748b !important;
  font-size: 12.5px !important;
  line-height: 1.5 !important;
}

.settings-bubble :deep(.eyebrow),
.settings-bubble :deep(.empty-kicker),
.settings-bubble :deep(.official-badge),
.settings-bubble :deep(.badge),
.settings-bubble :deep(.config-badge),
.settings-bubble :deep(.meta-pill),
.settings-bubble :deep(.meta-badge),
.settings-bubble :deep(.hint-chip),
.settings-bubble :deep(.official-tag),
.settings-bubble :deep(.status-pill),
.settings-bubble :deep(.el-tag) {
  border-radius: 999px !important;
  border-color: rgba(245, 158, 11, 0.22) !important;
  background: rgba(245, 158, 11, 0.08) !important;
  color: #b45309 !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.kpi-grid),
.settings-bubble :deep(.content-grid) {
  display: grid !important;
  gap: 10px !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid) {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
}

.settings-bubble :deep(.content-grid) {
  grid-template-columns: minmax(0, 1.35fr) minmax(220px, 0.82fr) minmax(220px, 0.82fr) !important;
}

.settings-bubble :deep(.tool-row) {
  display: grid !important;
  grid-template-columns: 38px minmax(0, 1fr) auto !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 11px !important;
  border-radius: var(--zuno-radius-card) !important;
  border: 1px solid rgba(226, 232, 240, 0.82) !important;
  background: var(--zuno-glass-card) !important;
  box-shadow: var(--zuno-shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
}

.settings-bubble :deep(.server-table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;
}

.settings-bubble :deep(.server-table th) {
  color: #94a3b8;
  font-size: 11.5px;
  font-weight: 560;
  text-align: left;
}

.settings-bubble :deep(.server-table td) {
  padding: 9px 10px !important;
  background: rgba(255, 255, 255, 0.78);
  border-top: 1px solid rgba(226, 232, 240, 0.78);
  border-bottom: 1px solid rgba(226, 232, 240, 0.78);
}

.settings-bubble :deep(.server-table td:first-child) {
  border-left: 1px solid rgba(226, 232, 240, 0.78);
  border-radius: 8px 0 0 8px;
}

.settings-bubble :deep(.server-table td:last-child) {
  border-right: 1px solid rgba(226, 232, 240, 0.78);
  border-radius: 0 8px 8px 0;
}

.settings-bubble :deep(.page-icon),
.settings-bubble :deep(.title-icon),
.settings-bubble :deep(.header-icon) {
  width: 36px !important;
  height: 36px !important;
  border-radius: 12px !important;
}

.settings-bubble :deep(.title-block),
.settings-bubble :deep(.header-left),
.settings-bubble :deep(.card-top),
.settings-bubble :deep(.skill-title-wrap),
.settings-bubble :deep(.server-cell) {
  gap: 10px !important;
}

.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.skill-icon-wrap),
.settings-bubble :deep(.server-logo) {
  width: 40px !important;
  height: 40px !important;
  border-radius: 12px !important;
}

.settings-bubble :deep(.meta-grid),
.settings-bubble :deep(.summary-grid),
.settings-bubble :deep(.field-grid),
.settings-bubble :deep(.dialog-grid),
.settings-bubble :deep(.basic-grid),
.settings-bubble :deep(.options-grid) {
  gap: 10px !important;
}

.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.kpi-card) {
  min-height: 0 !important;
  padding: 12px !important;
}

.settings-bubble :deep(.card-footer),
.settings-bubble :deep(.tool-side),
.settings-bubble :deep(.skill-actions),
.settings-bubble :deep(.row-actions),
.settings-bubble :deep(.action-row) {
  gap: 8px !important;
}

.settings-bubble :deep(.tool-side) {
  min-width: 104px !important;
  align-items: center !important;
  justify-content: flex-end !important;
}

.settings-bubble :deep(.tool-side .action-row) {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: flex-end !important;
  width: max-content !important;
  min-width: max-content !important;
}

.settings-bubble :deep(.tool-title-row) {
  min-width: 0 !important;
  align-items: baseline !important;
}

.settings-bubble :deep(.tool-name) {
  flex: 0 1 auto !important;
  min-width: 0 !important;
  max-width: min(220px, 34%) !important;
}

.settings-bubble :deep(.tool-description) {
  min-width: 120px !important;
}

.settings-bubble :deep(.tool-meta-row) {
  min-width: 0 !important;
  max-width: 100% !important;
}

.settings-bubble :deep(.hint-chip),
.settings-bubble :deep(.status-pill) {
  white-space: nowrap !important;
}

.settings-bubble :deep(.el-button) {
  min-height: 32px;
  border-radius: var(--zuno-radius-control);
  padding: 7px 11px;
  font-size: 12.5px;
  font-weight: 500;
}

.settings-bubble :deep(.el-button--primary) {
  --el-button-bg-color: #f59e0b;
  --el-button-border-color: #f59e0b;
  --el-button-hover-bg-color: #d97706;
  --el-button-hover-border-color: #d97706;
  --el-button-active-bg-color: #b45309;
  --el-button-active-border-color: #b45309;
  box-shadow: 0 8px 18px rgba(245, 158, 11, 0.16);
}

.settings-bubble :deep(.el-input__wrapper),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__wrapper) {
  min-height: 32px;
  border-radius: var(--zuno-radius-control) !important;
  background: rgba(255, 255, 255, 0.88) !important;
  box-shadow:
    inset 0 0 0 1px rgba(226, 232, 240, 0.92),
    inset 0 1px 0 rgba(255, 255, 255, 0.98),
    0 8px 18px -16px rgba(15, 23, 42, 0.2) !important;
}

.settings-bubble :deep(.el-input__inner),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__selected-item),
.settings-bubble :deep(.el-select__placeholder) {
  font-size: 12.5px !important;
}

.settings-bubble :deep(.empty-state) {
  border: 1px dashed rgba(203, 213, 225, 0.95) !important;
  border-radius: var(--zuno-radius-card) !important;
  background: rgba(248, 250, 252, 0.56) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.76) !important;
}

.settings-bubble :deep(.logo-preview),
.settings-bubble :deep(.side-avatar),
.settings-bubble :deep(.summary-item),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.server-logo),
.settings-bubble :deep(.skill-icon-wrap) {
  border-color: rgba(226, 232, 240, 0.9) !important;
  background: #ffffff !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.empty-visual) {
  filter: saturate(0.82);
  transform: scale(0.88);
}

.settings-bubble :deep(.el-table) {
  --el-table-border-color: rgba(226, 232, 240, 0.72);
  --el-table-header-bg-color: rgba(248, 250, 252, 0.9);
  --el-table-row-hover-bg-color: rgba(245, 158, 11, 0.045);
  border-radius: 8px;
  overflow: hidden;
}

.settings-bubble :deep(.el-dialog) {
  border-radius: 8px;
}

@media (max-width: 760px) {
  .workspace-container {
    --workspace-sidebar-width: 286px;
  }

  .sidebar-body {
    padding: 22px 18px;
  }

  .mobile-rail-toggle {
    background: rgba(255, 255, 255, 0.82);
  }

  .settings-content-shell {
    padding: 76px 16px 20px;
  }

  .settings-message {
    grid-template-columns: 34px minmax(0, 1fr);
    gap: 10px;
  }

  .settings-message-avatar {
    width: 34px;
    height: 34px;
    border-radius: 11px;
  }

  .settings-message-avatar img {
    width: 21px;
    height: 21px;
  }

  .settings-bubble {
    padding: 16px;
    border-radius: 20px 20px 20px 8px;
  }

  .settings-bubble :deep(.agent-hero),
  .settings-bubble :deep(.page-header),
  .settings-bubble :deep(.page-hero),
  .settings-bubble :deep(.hero-card) {
    padding-bottom: 14px !important;
  }

  .settings-bubble :deep(.content-grid),
  .settings-bubble :deep(.editor-layout),
  .settings-bubble :deep(.workspace-grid),
  .settings-bubble :deep(.config-layout) {
    grid-template-columns: 1fr !important;
  }

  .settings-bubble :deep(.tool-row) {
    grid-template-columns: 38px minmax(0, 1fr) !important;
    align-items: start !important;
  }

  .settings-bubble :deep(.tool-side) {
    grid-column: 2 !important;
    grid-row: 2 !important;
    min-width: 0 !important;
    width: 100% !important;
    align-items: center !important;
    justify-content: flex-end !important;
    align-self: center !important;
  }

  .settings-bubble :deep(.tool-side .action-row) {
    width: auto !important;
    min-width: 0 !important;
  }

  .settings-bubble :deep(.tool-title-row) {
    display: grid !important;
    grid-template-columns: minmax(92px, max-content) minmax(0, 1fr) !important;
    column-gap: 10px !important;
    row-gap: 2px !important;
  }

  .settings-bubble :deep(.tool-name) {
    max-width: 160px !important;
  }

  .settings-bubble :deep(.tool-description) {
    min-width: 0 !important;
  }

  .settings-bubble :deep(.tool-meta-row) {
    padding-right: 112px !important;
  }

  .settings-bubble :deep(.server-table) {
    min-width: 720px;
  }
}

/* Motion pass: keep route and sidebar transitions in the same liquid rhythm. */
.workspace-container {
  --zuno-motion-ease: cubic-bezier(0.2, 0.78, 0.22, 1);
  --zuno-motion-soft: cubic-bezier(0.16, 0.84, 0.22, 1);
}

.content {
  position: relative;
  isolation: isolate;
}

.workspace-main-swap-enter-active,
.workspace-main-swap-leave-active {
  transition:
    opacity 0.34s var(--zuno-motion-ease),
    transform 0.38s var(--zuno-motion-ease),
    filter 0.38s var(--zuno-motion-ease);
}

.workspace-main-swap-enter-active {
  position: relative;
  z-index: 2;
}

.workspace-main-swap-leave-active {
  position: absolute;
  inset: 0;
  z-index: 1;
  width: 100%;
  pointer-events: none;
}

.workspace-main-swap-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.996);
  filter: blur(8px);
}

.workspace-main-swap-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.998);
  filter: blur(6px);
}

.sidebar-unlocked {
  animation: sidebarPanelSettle 0.46s var(--zuno-motion-ease) both;
}

.nav-section {
  animation: navSectionIn 0.34s var(--zuno-motion-ease) both;
}

.nav-section:nth-child(2) { animation-delay: 30ms; }
.nav-section:nth-child(3) { animation-delay: 60ms; }
.nav-section:nth-child(4) { animation-delay: 90ms; }
.nav-section:nth-child(5) { animation-delay: 120ms; }

.nav-section-body > .nav-row,
.nav-section-body > .sidebar-note {
  animation: navItemIn 0.28s var(--zuno-motion-ease) both;
}

.nav-section-body > .nav-row:nth-child(2) { animation-delay: 18ms; }
.nav-section-body > .nav-row:nth-child(3) { animation-delay: 36ms; }
.nav-section-body > .nav-row:nth-child(4) { animation-delay: 54ms; }
.nav-section-body > .nav-row:nth-child(5) { animation-delay: 72ms; }

.nav-row {
  overflow: hidden;
  transform: translateZ(0);
  transition:
    color 0.2s ease,
    background 0.22s ease,
    transform 0.22s var(--zuno-motion-ease);
}

.nav-row::before {
  content: '';
  position: absolute;
  top: 6px;
  bottom: 6px;
  left: 4px;
  width: 2px;
  border-radius: 999px;
  background: #f59e0b;
  opacity: 0;
  transform: scaleY(0.45);
  transform-origin: center;
  transition:
    opacity 0.2s ease,
    transform 0.24s var(--zuno-motion-ease);
}

.nav-row:hover {
  transform: translateX(1px);
}

.nav-row.active::before {
  opacity: 1;
  transform: scaleY(1);
}

.navigation-settling .nav-row.active {
  animation: navActiveSettle 0.42s var(--zuno-motion-ease) both;
}

.primary-new-chat,
.section-plus,
.settings-entry,
.settings-float-item,
.account-entry,
.account-float-item {
  will-change: transform;
}

.primary-new-chat:active,
.section-plus:active,
.settings-entry:active,
.settings-float-item:active,
.account-entry:active,
.account-float-item:active {
  transform: translateY(1px) scale(0.985);
}

.settings-float-enter-active,
.settings-float-leave-active {
  transition:
    opacity 0.24s ease,
    transform 0.28s var(--zuno-motion-ease),
    filter 0.28s ease;
}

.settings-float-enter-from,
.settings-float-leave-to {
  opacity: 0;
  filter: blur(8px);
  transform: translateY(18px) scale(0.94);
}

@keyframes sidebarPanelSettle {
  from {
    opacity: 0;
    transform: translateY(8px);
    filter: blur(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
}

@keyframes navSectionIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes navItemIn {
  from {
    opacity: 0;
    transform: translateX(-6px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes navActiveSettle {
  0% {
    background: rgba(245, 158, 11, 0.02);
    transform: translateX(0);
  }
  45% {
    background: rgba(245, 158, 11, 0.12);
    transform: translateX(2px);
  }
  100% {
    background: rgba(245, 158, 11, 0.075);
    transform: translateX(0);
  }
}

/* Zuno shell polish: fewer pills, clearer brand line, smoother navigation language. */
.workspace-container {
  background:
    radial-gradient(circle at 68% 18%, rgba(255, 255, 255, 0.96), transparent 30%),
    radial-gradient(circle at 12% 88%, rgba(245, 158, 11, 0.055), transparent 26%),
    linear-gradient(180deg, #fbfcff 0%, #f7f8fb 100%);
}

.sidebar {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(248, 250, 252, 0.66)),
    rgba(255, 255, 255, 0.62);
  border-right: 1px solid rgba(226, 232, 240, 0.68);
  box-shadow: 34px 0 72px -34px rgba(15, 23, 42, 0.18);
}

.brand-copy span {
  display: none;
}

.primary-new-chat {
  min-height: 36px;
  border-radius: 8px;
  background: linear-gradient(180deg, #f8aa1b, #f59e0b);
  box-shadow:
    0 16px 30px -24px rgba(180, 83, 9, 0.82),
    inset 0 1px 0 rgba(255, 255, 255, 0.34);
}

.primary-new-chat:hover {
  background: linear-gradient(180deg, #ffb52a, #e89105);
  transform: translateY(-1px);
}

.section-title {
  padding-inline: 0 2px;
  color: #94a3b8;
  letter-spacing: 0.02em;
  text-transform: none;
}

.nav-row {
  min-height: 30px;
  padding: 0 28px 0 14px;
  border-radius: 0;
  background: transparent;
}

.nav-row:hover {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0.07), rgba(245, 158, 11, 0.025), transparent);
}

.nav-row.active {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.035), transparent);
}

.nav-row::before {
  left: 0;
  top: 5px;
  bottom: 5px;
  border-radius: 0;
}

.section-plus,
.delete-btn,
.rail-toggle {
  border-radius: 6px;
}

.section-plus:hover,
.delete-btn:hover,
.rail-toggle:hover {
  color: #b45309;
  background: rgba(245, 158, 11, 0.08);
}

.settings-entry {
  border-radius: 0;
  background: transparent !important;
}

.settings-entry.active,
.settings-entry:hover {
  color: #b45309;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.02), transparent) !important;
}

.settings-float {
  border-radius: 12px;
  border-color: rgba(226, 232, 240, 0.72);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(248, 250, 252, 0.56)),
    rgba(255, 255, 255, 0.54);
  box-shadow:
    0 24px 60px -32px rgba(15, 23, 42, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.settings-float::before {
  border-radius: 11px;
}

.settings-float-item {
  min-height: 31px;
  border-radius: 0;
}

.settings-float-item::before {
  content: '';
  width: 2px;
  align-self: stretch;
  margin: 7px 0;
  background: #f59e0b;
  opacity: 0;
  transform: scaleY(0.5);
  transition: opacity 0.18s ease, transform 0.2s var(--zuno-motion-ease);
}

.settings-float-item:hover,
.settings-float-item.active {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0.09), rgba(245, 158, 11, 0.02), transparent);
  box-shadow: none;
}

.settings-float-item:hover::before,
.settings-float-item.active::before {
  opacity: 1;
  transform: scaleY(1);
}

.settings-content,
.settings-frame {
  background:
    radial-gradient(circle at 58% 24%, rgba(255, 255, 255, 0.96), transparent 33%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.052), transparent 30%),
    #f7f8fb;
}

@media (prefers-reduced-motion: reduce) {
  .workspace-main-swap-enter-active,
  .workspace-main-swap-leave-active,
  .settings-float-enter-active,
  .settings-float-leave-active,
  .account-float-enter-active,
  .account-float-leave-active,
  .nav-section,
  .nav-section-body > .nav-row,
  .nav-section-body > .sidebar-note,
  .sidebar-unlocked,
  .navigation-settling .nav-row.active {
    animation: none !important;
    transition-duration: 1ms !important;
    filter: none !important;
    transform: none !important;
  }
}

/* Correction pass: no orange label backplates in sidebar/settings navigation. */
.settings-entry,
.settings-entry.active,
.settings-entry:hover {
  background: transparent !important;
  box-shadow: none !important;
}

.settings-entry.active,
.settings-entry:hover {
  color: #b45309;
}

.settings-float-item,
.settings-float-item:hover,
.settings-float-item.active,
.account-float-item,
.account-float-item:hover,
.settings-tab,
.settings-tab:hover,
.settings-tab.active {
  background: transparent !important;
  box-shadow: none !important;
}

.settings-float-item:hover,
.settings-float-item.active,
.account-float-item:hover,
.settings-tab:hover,
.settings-tab.active {
  color: #b45309;
}

.settings-float-item::before {
  background: #f59e0b;
}

/* Sidebar icon rhythm: every text-leading icon sits in the same optical slot. */
.section-title-main,
.settings-entry,
.settings-float-item,
.account-float-item,
.primary-new-chat {
  align-items: center;
}

.section-title-main {
  min-height: 22px;
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  column-gap: 6px;
}

.section-chevron,
.settings-entry :deep(.el-icon),
.account-float-item :deep(.el-icon),
.primary-new-chat :deep(.el-icon) {
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  display: inline-grid;
  place-items: center;
  line-height: 1;
}

.section-chevron {
  font-size: 15px;
  transform-origin: 50% 50%;
}

.section-chevron.expanded {
  transform: rotate(90deg);
}

.section-title-main > span:not(.section-chevron),
.settings-entry span,
.settings-float-item span,
.primary-new-chat span {
  display: inline-flex;
  align-items: center;
  min-height: 16px;
  line-height: 16px;
}

.settings-entry {
  gap: 7px;
}

.settings-entry :deep(.el-icon) {
  font-size: 14px;
  transform: translateY(0.25px);
}

.account-entry {
  width: 32px;
  height: 32px;
  overflow: visible;
  background: transparent !important;
  box-shadow: none !important;
}

.account-entry .user-avatar-wrapper,
.account-entry .user-avatar {
  width: 32px !important;
  height: 32px !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.account-entry .user-avatar {
  border-radius: 10px !important;
}

.account-entry .user-avatar img {
  width: 100%;
  height: 100%;
  border-radius: inherit;
  object-fit: cover;
}

.account-float {
  right: 2px;
  bottom: 48px;
  width: 108px;
  gap: 1px;
  padding: 6px;
  border-radius: 12px;
  border-color: rgba(226, 232, 240, 0.72);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.8), rgba(248, 250, 252, 0.58)),
    rgba(255, 255, 255, 0.56);
  box-shadow:
    0 28px 68px -26px rgba(15, 23, 42, 0.36),
    0 16px 34px -20px rgba(180, 83, 9, 0.26),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  clip-path: none;
}

.account-float::before {
  border-radius: 11px;
}

.account-float-item {
  min-height: 28px;
  grid-template-columns: 14px minmax(0, 1fr);
  gap: 5px;
  padding: 0 5px;
  font-size: 12px;
  font-weight: 560;
}

.account-float-icon {
  width: 14px;
  height: 14px;
}

.account-float-divider {
  margin: 3px 5px;
}

.settings-float-icon {
  width: 17px;
  height: 17px;
  flex-basis: 17px;
  object-position: center;
}

@keyframes navActiveSettle {
  0%,
  45%,
  100% {
    background: transparent;
    transform: translateX(0);
  }
}

/* Auth-to-workspace sidebar handoff: keep both states in one stable slot.
   This removes the previous vertical release/settle motion that felt like a flip. */
.sidebar-state-slot {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  width: 100%;
  overflow: hidden;
  contain: layout paint;
}

.sidebar-state-slot > .sidebar-unlocked,
.sidebar-state-slot > .sidebar-locked {
  flex: 1 1 auto;
  width: 100%;
  min-width: 0;
  min-height: 0;
  backface-visibility: hidden;
  transform: translateZ(0);
}

.sidebar-unlock-enter-active,
.sidebar-unlock-leave-active {
  transition:
    opacity 0.46s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.5s cubic-bezier(0.22, 1, 0.36, 1) !important;
  filter: none !important;
  transform-origin: left center;
  will-change: opacity, transform;
}

.sidebar-unlock-leave-active {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.sidebar-unlock-enter-from {
  opacity: 0;
  transform: translate3d(-14px, 0, 0) !important;
  filter: none !important;
}

.sidebar-unlock-leave-to {
  opacity: 0;
  transform: translate3d(12px, 0, 0) !important;
  filter: none !important;
}

.sidebar-unlock-leave-active .sidebar-mascot-slot {
  animation: none !important;
}

.sidebar-unlocked {
  animation: sidebarPanelGlide 0.48s cubic-bezier(0.22, 1, 0.36, 1) both !important;
}

.nav-section {
  animation-name: navSectionGlide !important;
}

@keyframes sidebarPanelGlide {
  from {
    opacity: 0;
    transform: translate3d(-8px, 0, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

@keyframes navSectionGlide {
  from {
    opacity: 0;
    transform: translate3d(-6px, 0, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}
</style>
