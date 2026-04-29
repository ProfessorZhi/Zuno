<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, SwitchButton, Fold, Expand, Plus } from '@element-plus/icons-vue'
import { zunoAgentAvatar, zunoBrandMark } from '../../utils/brand'
import { useUserStore } from '../../store/user'
import { logoutAPI, getUserInfoAPI } from '../../apis/auth'
import { getWorkspaceSessionsAPI, deleteWorkspaceSessionAPI } from '../../apis/workspace'
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

const selectedSession = ref('')
const sessions = ref<WorkspaceSessionItem[]>([])
const loading = ref(false)
const SIDEBAR_COLLAPSED_KEY = 'zuno.workspace.sidebarCollapsed'
const getInitialSidebarCollapsed = () => {
  if (typeof window === 'undefined') return false
  if (window.innerWidth > 520) return false
  return window.localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true'
}
const sidebarCollapsed = ref(getInitialSidebarCollapsed())
const settingsCenterVisible = ref(false)
const activeSettingsSection = ref('model')
let fetchSessionsRequestId = 0

const syncSelectedSessionFromRoute = () => {
  const sessionId = route.query.session_id as string | undefined
  selectedSession.value = sessionId || ''
}

const startNewConversation = () => {
  window.dispatchEvent(new CustomEvent('workspace-new-conversation'))
}

const handleWorkspaceSessionUpdated = async () => {
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

const normalizeWorkspaceMode = (value: unknown): WorkspaceMode => String(value || '').toLowerCase() === 'agent' ? 'agent' : 'normal'

const normalizeAgentName = (value: unknown) => {
  const raw = String(value || '').trim()
  if (!raw || raw === 'simple' || raw === 'normal' || raw === 'agent') return '默认助手'
  return raw
}

const workspaceModeLabel = (mode: WorkspaceMode) => mode === 'agent' ? 'Agent' : 'Chat'
const settingsSections = [
  { key: 'model', label: '模型', path: '/model' },
  { key: 'mcp', label: 'MCP', path: '/mcp-server' },
  { key: 'skill', label: 'Skill', path: '/agent-skill' },
  { key: 'tool', label: '工具', path: '/tool' },
  { key: 'knowledge', label: '知识库', path: '/knowledge' },
  { key: 'agent', label: '智能体', path: '/agent' },
  { key: 'dashboard', label: '数据看板', path: '/dashboard' },
]
const activeSettings = computed(() => settingsSections.find((section) => section.key === activeSettingsSection.value) || settingsSections[0])
const activeSettingsUrl = computed(() => `${activeSettings.value.path}?embed=1`)

const openSettingsCenter = (section = 'model') => {
  activeSettingsSection.value = settingsSections.some((item) => item.key === section) ? section : 'model'
  settingsCenterVisible.value = true
}

const handleOpenSettingsCenter = (event: Event) => {
  const section = (event as CustomEvent<{ section?: string }>).detail?.section || 'model'
  openSettingsCenter(section)
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
  try {
    loading.value = true
    const response = await getWorkspaceSessionsAPI()
    if (requestId !== fetchSessionsRequestId) return
    if (response.data.status_code === 200) {
      const sessionModeOverrides = loadWorkspaceSessionModes()
      sessions.value = (response.data.data || [])
        .filter((session: any) => Array.isArray(session.contexts) && session.contexts.length > 0)
        .map((session: any) => ({
          sessionId: session.session_id || session.id,
          title: session.title || '未命名会话',
          createTime: session.create_time || session.created_at || new Date().toISOString(),
          agent: normalizeAgentName(session.agent || session.workspace_mode || 'simple'),
          workspaceMode: sessionModeOverrides[session.session_id || session.id] || normalizeWorkspaceMode(session.workspace_mode || session.agent),
        }))
      return
    }

    ElMessage.error('获取会话列表失败')
  } catch (error) {
    if (requestId !== fetchSessionsRequestId) return
    console.error('获取会话列表失败:', error)
    ElMessage.error('获取会话列表失败')
  } finally {
    if (requestId === fetchSessionsRequestId) {
      loading.value = false
    }
  }
}

const deleteSession = async (sessionId: string, event: Event) => {
  event.stopPropagation()

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
  selectedSession.value = session.sessionId
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
  router.push(defaultWorkspaceRoute())
}

const handleUserCommand = async (command: string) => {
  if (command === 'settings') {
    openSettingsCenter('model')
    return
  }

  if (command === 'profile') {
    router.push('/profile')
    return
  }

  if (command === 'logout') {
    await handleLogout()
  }
}

const handleLogout = async () => {
  try {
    await logoutAPI()
  } catch (error) {
    console.error('调用退出接口失败:', error)
  }

  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) target.src = '/src/assets/user.svg'
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

onMounted(async () => {
  userStore.initUserState()

  if (userStore.isLoggedIn && userStore.userInfo && !userStore.userInfo.avatar) {
    try {
      const response = await getUserInfoAPI(userStore.userInfo.id)
      if (response.data.status_code === 200 && response.data.data) {
        const userData = response.data.data
        userStore.updateUserInfo({
          avatar: userData.user_avatar || userData.avatar || '/src/assets/user.svg',
          description: userData.user_description || userData.description,
        })
      }
    } catch (error) {
      console.error('初始化用户信息失败:', error)
    }
  }

  syncSelectedSessionFromRoute()
  await fetchSessions()
  window.addEventListener('workspace-session-updated', handleWorkspaceSessionUpdated)
  window.addEventListener('workspace-session-mode-updated', handleWorkspaceSessionUpdated)
  window.addEventListener('workspace-open-settings', handleOpenSettingsCenter)
})

onBeforeUnmount(() => {
  window.removeEventListener('workspace-session-updated', handleWorkspaceSessionUpdated)
  window.removeEventListener('workspace-session-mode-updated', handleWorkspaceSessionUpdated)
  window.removeEventListener('workspace-open-settings', handleOpenSettingsCenter)
})

watch(
  () => route.query.session_id,
  async () => {
    syncSelectedSessionFromRoute()
    await fetchSessions()
  }
)

watch(sidebarCollapsed, (collapsed) => {
  window.localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(collapsed))
})

</script>

<template>
  <div class="workspace-container">
    <header class="workspace-nav">
      <div class="brand-side">
        <button class="brand-mark" type="button" @click="goWorkspaceHome" title="返回首页">
          <img :src="zunoBrandMark" alt="Zuno" class="brand-logo-img" />
        </button>
      </div>

      <div class="nav-right">
        <button class="rail-toggle mobile-only" type="button" @click="sidebarCollapsed = !sidebarCollapsed">
          <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
        </button>

        <el-dropdown @command="handleUserCommand" trigger="click">
          <div class="user-avatar-wrapper">
            <div class="user-avatar">
              <img
                :src="userStore.userInfo?.avatar || '/src/assets/user.svg'"
                alt="用户头像"
                @error="handleAvatarError"
                referrerpolicy="no-referrer"
              />
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="settings">设置</el-dropdown-item>
              <el-dropdown-item command="profile" :icon="User">个人资料</el-dropdown-item>
              <el-dropdown-item divided command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <div class="workspace-main">
      <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div v-if="sidebarCollapsed" class="sidebar-rail">
          <button class="rail-toggle desktop-only" type="button" @click="sidebarCollapsed = false">
            <el-icon><Expand /></el-icon>
          </button>
        </div>

        <div v-if="!sidebarCollapsed" class="sidebar-body">
          <div class="sidebar-head">
            <div class="sidebar-title-wrap">
              <strong>会话记录</strong>
              <span>{{ sessions.length }} 条</span>
            </div>
            <div class="sidebar-actions">
              <button class="new-session-btn" type="button" @click="startNewConversation">
                <el-icon><Plus /></el-icon>
                <span>新会话</span>
              </button>
              <button class="rail-toggle desktop-only sidebar-toggle" type="button" @click="sidebarCollapsed = true">
                <el-icon><Fold /></el-icon>
              </button>
            </div>
          </div>

          <div class="session-list">
            <div v-if="loading" class="loading-state">
              <div class="loading-text">正在加载会话...</div>
            </div>

            <div v-else-if="sessions.length === 0" class="empty-state">
              <div class="empty-mark">Z</div>
              <div class="empty-text">还没有会话记录</div>
            </div>

            <div v-for="group in groupedSessions" :key="group.agent" class="session-group">
              <div class="group-head">
                <span>{{ group.agent }}</span>
                <small>{{ group.items.length }}</small>
              </div>

              <div
                v-for="session in group.items"
                :key="session.sessionId"
                :class="['session-card', { active: selectedSession === session.sessionId }]"
                @click="selectSession(session)"
              >
                <div class="session-icon">
                  <img :src="zunoAgentAvatar" width="22" height="22" alt="" />
                </div>
                <div class="session-info">
                  <div class="session-title-row">
                    <span class="session-title">{{ session.title }}</span>
                    <span class="mode-tag" :class="session.workspaceMode">{{ workspaceModeLabel(session.workspaceMode) }}</span>
                  </div>
                  <div class="session-time">{{ formatTime(session.createTime) }}</div>
                </div>
                <button class="delete-btn" @click="deleteSession(session.sessionId, $event)" title="删除会话">
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main class="content">
        <router-view />
      </main>
    </div>

    <Teleport to="body">
      <div v-if="settingsCenterVisible" class="settings-center-backdrop" @click.self="settingsCenterVisible = false">
        <section class="settings-center" role="dialog" aria-modal="true" aria-label="设置">
          <header class="settings-center-head">
            <div>
              <span class="settings-center-kicker">设置</span>
              <strong>{{ activeSettings.label }}</strong>
            </div>
            <button class="settings-center-close" type="button" aria-label="关闭设置" @click="settingsCenterVisible = false">×</button>
          </header>

          <div class="settings-center-body">
            <nav class="settings-center-tabs" aria-label="设置分类">
              <button
                v-for="section in settingsSections"
                :key="section.key"
                type="button"
                :class="['settings-tab', { active: activeSettingsSection === section.key }]"
                @click="activeSettingsSection = section.key"
              >
                {{ section.label }}
              </button>
            </nav>

            <iframe class="settings-frame" :src="activeSettingsUrl" :title="activeSettings.label"></iframe>
          </div>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<style lang="scss" scoped>
.workspace-container {
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
  width: 46px;
  height: 46px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 251, 246, 0.92);
  border: 1px solid rgba(216, 164, 120, 0.32);
  cursor: pointer;
  box-shadow: 0 10px 20px rgba(130, 71, 31, 0.08);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid rgba(216, 164, 120, 0.32);
  background: rgba(255, 251, 246, 0.92);
  overflow: hidden;
  display: grid;
  place-items: center;
  box-shadow: 0 10px 20px rgba(130, 71, 31, 0.08);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.workspace-main {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
  background: #fffaf4;
}

.sidebar {
  width: 288px;
  flex: 0 0 288px;
  display: flex;
  flex-direction: column;
  background: #f7f1e8;
  border-right: 1px solid rgba(214, 198, 178, 0.58);
  transition: width 0.22s ease, flex-basis 0.22s ease;
}

.sidebar.collapsed {
  width: 52px;
  flex-basis: 52px;
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
  display: flex;
  flex-direction: column;
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

@media (max-width: 520px) {
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
    width: min(288px, calc(100vw - 56px));
    flex-basis: min(288px, calc(100vw - 56px));
    box-shadow: 10px 0 30px rgba(62, 44, 28, 0.12);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}
</style>
