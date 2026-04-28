<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, SwitchButton, Fold, Expand, Plus } from '@element-plus/icons-vue'
import { zunoAgentAvatar, zunoBrandMark } from '../../utils/brand'
import { useUserStore } from '../../store/user'
import { logoutAPI, getUserInfoAPI } from '../../apis/auth'
import { getWorkspaceSessionsAPI, deleteWorkspaceSessionAPI } from '../../apis/workspace'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const selectedSession = ref('')
const sessions = ref<any[]>([])
const loading = ref(false)
const sidebarCollapsed = ref(false)
const currentMode = computed(() => ((route.query.mode as string) === 'agent' ? 'agent' : 'normal'))
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

const fetchSessions = async () => {
  const requestId = ++fetchSessionsRequestId
  try {
    loading.value = true
    const response = await getWorkspaceSessionsAPI(currentMode.value)
    if (requestId !== fetchSessionsRequestId) return
    if (response.data.status_code === 200) {
      sessions.value = (response.data.data || [])
        .filter((session: any) => Array.isArray(session.contexts) && session.contexts.length > 0)
        .map((session: any) => ({
          sessionId: session.session_id || session.id,
          title: session.title || '未命名会话',
          createTime: session.create_time || session.created_at || new Date().toISOString(),
          agent: session.agent || 'simple',
          workspaceMode: session.workspace_mode || 'normal',
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
      await fetchSessions()
      if (selectedSession.value === sessionId) {
        selectedSession.value = ''
        router.push('/workspace')
      }
      return
    }

    ElMessage.error('删除会话失败')
  } catch (error) {
    console.error('删除会话失败:', error)
    ElMessage.error('删除会话失败')
  }
}

const selectSession = (sessionId: string) => {
  selectedSession.value = sessionId
  router.push({
    name: 'workspaceDefaultPage',
    query: {
      session_id: sessionId,
      mode: route.query.mode || 'normal',
      execution_mode: route.query.execution_mode || 'tool',
      access_scope: route.query.access_scope || 'workspace',
    },
  })
}

const goWorkspaceHome = () => {
  router.push('/homepage')
}

const handleUserCommand = async (command: string) => {
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

const visibleSessions = computed(() => sessions.value.filter((session) => session.workspaceMode === currentMode.value))

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
})

onBeforeUnmount(() => {
  window.removeEventListener('workspace-session-updated', handleWorkspaceSessionUpdated)
})

watch(
  () => route.query.session_id,
  async () => {
    syncSelectedSessionFromRoute()
    await fetchSessions()
  }
)

watch(currentMode, async () => {
  syncSelectedSessionFromRoute()
  await fetchSessions()
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
              <span>{{ visibleSessions.length }} 条</span>
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

            <div v-else-if="visibleSessions.length === 0" class="empty-state">
              <div class="empty-mark">Z</div>
              <div class="empty-text">还没有会话记录</div>
            </div>

            <div
              v-for="session in visibleSessions"
              :key="session.sessionId"
              :class="['session-card', { active: selectedSession === session.sessionId }]"
              @click="selectSession(session.sessionId)"
            >
              <div class="session-icon">
                <img :src="zunoAgentAvatar" width="22" height="22" alt="" />
              </div>
              <div class="session-info">
                <div class="session-title">{{ session.title }}</div>
                <div class="session-time">{{ formatTime(session.createTime) }}</div>
              </div>
              <button class="delete-btn" @click="deleteSession(session.sessionId, $event)" title="删除会话">
                ×
              </button>
            </div>
          </div>
        </div>
      </aside>

      <main class="content">
        <router-view />
      </main>
    </div>
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
}

.sidebar {
  width: 282px;
  flex: 0 0 282px;
  display: flex;
  flex-direction: column;
  background: rgba(248, 241, 231, 0.72);
  border-right: 1px solid rgba(204, 185, 162, 0.32);
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
  border-left: 1px solid rgba(255, 255, 255, 0.28);
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
  padding: 16px 18px 12px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
}

.sidebar-title-wrap {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.sidebar-title-wrap strong {
  font-size: 18px;
  color: #34271f;
  white-space: nowrap;
}

.sidebar-title-wrap span {
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(212, 138, 79, 0.12);
  color: #9b6a42;
  font-size: 12px;
}

.sidebar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.new-session-btn {
  border: 1px solid rgba(214, 188, 164, 0.8);
  background: linear-gradient(180deg, rgba(255, 252, 248, 0.98) 0%, rgba(248, 240, 230, 0.92) 100%);
  color: #7f5b39;
  border-radius: 999px;
  padding: 0 12px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex: 0 0 auto;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(130, 71, 31, 0.06);
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
  padding: 4px 14px 14px;
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

.session-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 18px;
  border: 1px solid rgba(228, 210, 190, 0.72);
  background: rgba(255, 252, 248, 0.88);
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.session-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(117, 79, 40, 0.06);
}

.session-card.active {
  border-color: rgba(212, 138, 79, 0.5);
  background: linear-gradient(180deg, #fff8f0 0%, #fff4e9 100%);
}

.session-icon {
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  border-radius: 12px;
  background: rgba(255, 247, 240, 0.96);
  border: 1px solid rgba(226, 201, 178, 0.8);
  display: grid;
  place-items: center;
}

.session-info {
  flex: 1;
  min-width: 0;
  display: grid;
  gap: 4px;
}

.session-title {
  font-size: 15px;
  font-weight: 600;
  color: #3c2f25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 12px;
  color: #8d7258;
}

.delete-btn {
  border: none;
  background: transparent;
  color: #b08b6a;
  font-size: 18px;
  cursor: pointer;
  width: 26px;
  height: 26px;
  border-radius: 999px;
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
}

.content :deep(.workspace-chat) {
  flex: 1;
  min-height: 0;
}

.mobile-only {
  display: none;
}

@media (max-width: 900px) {
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
    width: 282px;
    flex-basis: 282px;
    box-shadow: 10px 0 30px rgba(62, 44, 28, 0.12);
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }
}
</style>
