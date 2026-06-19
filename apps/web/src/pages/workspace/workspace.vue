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
import { isDesktopRuntime } from '../../utils/api'
import { DEFAULT_USER_AVATAR, isLegacyRemoteUserAvatar, withUserAvatarVersion } from '../../utils/user-avatars'
import SidebarMascot from '../../components/SidebarMascot.vue'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'
import WorkspaceAuthGate from './WorkspaceAuthGate.vue'
import WorkspaceSettingsShell from './components/WorkspaceSettingsShell.vue'
import accountConversationIcon from '../../assets/account/conversation.svg'
import accountProfileIcon from '../../assets/account/profile.svg'
import accountLogoutIcon from '../../assets/account/logout.svg'
import {
  loadWorkspaceDefaults,
  loadWorkspaceSessionModes,
  removeWorkspaceSessionMode,
  type WorkspaceMode,
} from '../../utils/workspace-defaults'
import { loadSettingsUiMode } from '../../utils/settings-preferences'

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
const settingsUiMode = ref(loadSettingsUiMode())
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
const desktopRuntime = computed(() => isDesktopRuntime())
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
const traditionalSettingsWindowVisible = computed(() => (
  settingsUiMode.value === 'traditional'
  && Boolean(route.meta.settingsSection || route.meta.accountSection)
))
const activeSettingsSection = computed(() => String(route.meta.settingsSection || selectedSettingsSection.value || 'agent'))
const activeSettingsLabel = computed(() => (
  settingsSections.find((section) => section.key === activeSettingsSection.value)?.label || '设置'
))

const toggleSettingsMenu = () => {
  if (!authUnlocked.value) return
  if (settingsUiMode.value === 'traditional') {
    if (traditionalSettingsWindowVisible.value) {
      void closeTraditionalSettingsWindow()
      return
    }
    void openSettingsCenter(selectedSettingsSection.value || 'agent')
    return
  }
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

const closeTraditionalSettingsWindow = async () => {
  const { settings_turn: _settingsTurn, ...restQuery } = route.query
  await router.push({
    name: 'workspaceDefaultPage',
    query: restQuery,
  })
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
  <div
    class="workspace-container"
    :class="{
      'navigation-settling': navigationSettling,
      'desktop-runtime': desktopRuntime,
      'settings-overlay-open': traditionalSettingsWindowVisible,
    }"
  >
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
      <div
        v-if="traditionalSettingsWindowVisible"
        class="settings-center-backdrop"
        @click.self="closeTraditionalSettingsWindow"
      >
        <div class="settings-center-window">
          <WorkspaceSettingsShell @close="closeTraditionalSettingsWindow" />
        </div>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped src="./workspace.scss"></style>
