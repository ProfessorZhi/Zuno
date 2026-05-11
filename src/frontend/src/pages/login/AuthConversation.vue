<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, Check, Expand, Fold, Lock, Plus, Setting, User } from '@element-plus/icons-vue'
import { getUserInfoAPI, loginAPI, registerAPI } from '../../apis/auth'
import type { RegisterForm } from '../../apis/auth'
import { useUserStore } from '../../store/user'
import { zunoAgentAvatar } from '../../utils/brand'
import messageIcon from '../../assets/message.svg'
import SidebarMascot from '../../components/SidebarMascot.vue'
import MascotPresence from '../../components/MascotPresence.vue'
import { DEFAULT_USER_AVATAR } from '../../utils/user-avatars'

type AuthMode = 'choice' | 'login' | 'register'
type AuthMessage = {
  id: string
  role: 'assistant' | 'user'
  kind: 'text' | 'choice' | 'login' | 'register' | 'status'
  text?: string
  status?: 'success' | 'error' | 'thinking'
}

const props = withDefaults(defineProps<{
  initialMode?: AuthMode
}>(), {
  initialMode: 'choice',
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const conversationRef = ref<HTMLElement | null>(null)
const activeMode = ref<AuthMode>('choice')
const loading = ref(false)
const leaving = ref(false)
const isUnlocking = ref(false)
const messages = ref<AuthMessage[]>([])
const sidebarCollapsed = ref(false)
const transientThinkingId = ref<string | null>(null)

const loginForm = reactive({
  username: '',
  password: '',
})

const registerForm = reactive<RegisterForm>({
  user_name: '',
  user_email: '',
  user_password: '',
})
const confirmPassword = ref('')

const modeCopy = computed(() => {
  if (activeMode.value === 'register') return '创建账号'
  if (activeMode.value === 'login') return '登录工作台'
  return '身份确认'
})

const redirectTarget = computed(() => {
  const raw = route.query.redirect
  if (Array.isArray(raw)) return raw[0] || '/'
  return raw || '/'
})

const scrollToBottom = async () => {
  await nextTick()
  await new Promise<void>((resolve) => window.requestAnimationFrame(() => resolve()))
  const el = conversationRef.value
  if (!el) return
  el.scrollTop = el.scrollHeight
}

const wait = (ms: number) => new Promise<void>((resolve) => window.setTimeout(resolve, ms))

const appendMessage = async (message: Omit<AuthMessage, 'id'>) => {
  const lastIndex = messages.value.length - 1
  const lastMessage = messages.value[lastIndex]
  if (
    transientThinkingId.value &&
    lastMessage?.id === transientThinkingId.value &&
    lastMessage.role === 'assistant' &&
    lastMessage.kind === 'status' &&
    lastMessage.status === 'thinking' &&
    message.role === 'assistant'
  ) {
    messages.value[lastIndex] = {
      id: lastMessage.id,
      ...message,
    }
    transientThinkingId.value = null
    await scrollToBottom()
    return
  }

  messages.value.push({
    id: `${Date.now()}-${messages.value.length}`,
    ...message,
  })
  await scrollToBottom()
}

const appendThinking = async (text = 'Zuno 正在整理入口...', duration = 560) => {
  const id = `${Date.now()}-thinking-${messages.value.length}`
  messages.value.push({
    id,
    role: 'assistant',
    kind: 'status',
    status: 'thinking',
    text,
  })
  transientThinkingId.value = id
  await scrollToBottom()
  await wait(duration)
}

const extractErrorMessage = (error: any) => {
  const payload = error?.response?.data
  if (typeof payload?.status_message === 'string' && payload.status_message.trim()) return payload.status_message
  if (typeof payload?.detail === 'string' && payload.detail.trim()) return payload.detail
  if (typeof error?.message === 'string' && error.message.trim()) return error.message
  return ''
}

const resetSecrets = () => {
  loginForm.password = ''
  registerForm.user_password = ''
  confirmPassword.value = ''
}

const chooseMode = async (mode: Exclude<AuthMode, 'choice'>, fromRoute = false) => {
  if (loading.value) return
  activeMode.value = mode
  await appendMessage({
    role: 'user',
    kind: 'text',
    text: mode === 'login' ? '我想登录' : '我想创建账号',
  })
  await appendThinking(mode === 'login' ? '正在准备登录入口...' : '正在准备注册入口...')
  await appendMessage({
    role: 'assistant',
    kind: mode,
    text: mode === 'login'
      ? '好的，把账号和密码填在这里。密码只会用于登录，不会进入聊天记录。'
      : '没问题，先创建一个 Zuno 账号。完成后我会把你带回登录步骤。',
  })
  if (!fromRoute) {
    router.replace({ path: mode === 'login' ? '/login' : '/register', query: route.query })
  }
}

const showChoice = async () => {
  activeMode.value = 'choice'
  resetSecrets()
  await appendMessage({
    role: 'user',
    kind: 'text',
    text: '我想换一种进入方式',
  })
  await appendThinking('正在切换进入方式...')
  await appendMessage({
    role: 'assistant',
    kind: 'choice',
    text: '当然。你想继续登录，还是创建一个新账号？',
  })
  router.replace({ path: '/login', query: route.query })
}

const validateRegister = async () => {
  if (!registerForm.user_name.trim()) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '需要先填写用户名。' })
    return false
  }
  if (registerForm.user_name.length > 20) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '用户名不能超过 20 个字符。' })
    return false
  }
  if (registerForm.user_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.user_email)) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '邮箱格式看起来不太对，可以留空或重新填写。' })
    return false
  }
  if (!registerForm.user_password) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '需要设置一个密码。' })
    return false
  }
  if (registerForm.user_password.length < 6) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '密码至少需要 6 位。' })
    return false
  }
  if (registerForm.user_password !== confirmPassword.value) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '两次输入的密码不一致。' })
    return false
  }
  return true
}

const handleLogin = async () => {
  if (loading.value) return
  if (!loginForm.username.trim() || !loginForm.password) {
    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '账号和密码都需要填写。' })
    return
  }

  try {
    loading.value = true
    await appendMessage({ role: 'assistant', kind: 'status', status: 'thinking', text: '正在确认身份...' })
    const response = await loginAPI(loginForm)
    const responseData: any = response.data

    if (responseData.status_code === 200) {
      const userData = responseData.data || {}
      const accessToken = userData.access_token || responseData.token
      const userId = userData.user_id || responseData.userInfo?.id

      if (!accessToken || !userId) {
        await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: '登录接口没有返回有效令牌，请检查后端登录响应。' })
        return
      }

      userStore.setUserInfo(accessToken, {
        id: userId,
        username: responseData.userInfo?.username || loginForm.username,
        nickname: responseData.userInfo?.nickname,
        avatar: responseData.userInfo?.avatar,
      })

      try {
        const userInfoResponse = await getUserInfoAPI(userId)
        const userInfoData: any = userInfoResponse.data
        if (userInfoData.status_code === 200) {
          const completeUserData = userInfoData.data || {}
          userStore.updateUserInfo({
            avatar: completeUserData.user_avatar || completeUserData.avatar,
            description: completeUserData.user_description || completeUserData.description,
          })
        }
      } catch (error) {
        console.error('获取用户详情失败:', error)
      }

      resetSecrets()
      await appendThinking('身份确认完成，正在打开工作台...', 420)
      isUnlocking.value = true
      await appendMessage({ role: 'assistant', kind: 'status', status: 'success', text: '登录完成，工作台正在展开。' })
      await wait(1350)
      window.dispatchEvent(new CustomEvent('zuno-auth-route-mask', { detail: { duration: 2200 } }))
      await wait(520)
      await router.push(String(redirectTarget.value || '/'))
      return
    }

    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: responseData.status_message || '登录失败，请检查账号密码。' })
  } catch (error: any) {
    console.error('登录错误:', error)
    await appendMessage({
      role: 'assistant',
      kind: 'status',
      status: 'error',
      text: extractErrorMessage(error) || '登录失败，请确认后端服务已启动并检查账号密码。',
    })
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (loading.value || !(await validateRegister())) return

  try {
    loading.value = true
    await appendMessage({ role: 'assistant', kind: 'status', status: 'thinking', text: '正在创建账号...' })
    const response = await registerAPI(registerForm)
    const responseData: any = response.data

    if (responseData.status_code === 200) {
      const createdName = registerForm.user_name
      loginForm.username = createdName
      resetSecrets()
      await appendMessage({ role: 'assistant', kind: 'status', status: 'success', text: '账号已创建。现在用刚才的用户名登录即可。' })
      activeMode.value = 'login'
      await appendThinking('正在带你回到登录入口...', 460)
      await appendMessage({
        role: 'assistant',
        kind: 'login',
        text: '我已经把用户名带过来了，只需要输入密码。',
      })
      router.replace({ path: '/login', query: route.query })
      return
    }

    await appendMessage({ role: 'assistant', kind: 'status', status: 'error', text: responseData.status_message || '注册失败。' })
  } catch (error: any) {
    console.error('注册错误:', error)
    await appendMessage({
      role: 'assistant',
      kind: 'status',
      status: 'error',
      text: extractErrorMessage(error) || '注册失败，请确认后端服务已启动。',
    })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  userStore.initUserState()
  await wait(180)
  await appendMessage({
    role: 'assistant',
    kind: 'text',
    text: '欢迎回来。我先帮你确认进入方式。',
  })
  await appendThinking('Zuno 正在准备安全入口...', 620)
  await appendMessage({
    role: 'assistant',
    kind: 'choice',
    text: '你想登录已有账号，还是创建一个新账号？',
  })
  if (props.initialMode === 'login' || props.initialMode === 'register') {
    window.setTimeout(() => {
      void chooseMode(props.initialMode as Exclude<AuthMode, 'choice'>, true)
    }, 280)
  }
})
</script>

<template>
  <div class="workspace-container auth-shell" :class="{ leaving, unlocking: isUnlocking }">
    <button class="mobile-rail-toggle mobile-only" type="button" @click="sidebarCollapsed = !sidebarCollapsed">
      <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
    </button>

    <aside class="sidebar auth-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div v-if="sidebarCollapsed" class="sidebar-rail">
        <button class="rail-toggle desktop-only" type="button" @click="sidebarCollapsed = false">
          <el-icon><Expand /></el-icon>
        </button>
      </div>

      <div v-if="!sidebarCollapsed" class="sidebar-body">
      <div class="brand-block brand-row">
        <button class="brand-icon" type="button" @click="showChoice" title="返回登录入口">
          <img :src="zunoAgentAvatar" alt="Zuno" />
        </button>
        <div class="brand-copy">
          <strong>Zuno AI</strong>
          <span>Intelligence Workspace</span>
        </div>
        <button class="rail-toggle desktop-only" type="button" @click="sidebarCollapsed = true">
          <el-icon><Fold /></el-icon>
        </button>
      </div>

      <button class="primary-new-chat new-chat-button" type="button" @click="showChoice">
        <el-icon><Plus /></el-icon>
        <span>New Chat</span>
      </button>

      <div class="sidebar-panel-slot">
        <Transition name="sidebar-panel">
          <div v-if="!isUnlocking" key="intro" class="nav-scroll auth-intro-panel">
            <section class="auth-mascot-card" aria-label="Zuno AI">
              <div class="auth-code-pet">
                <SidebarMascot />
              </div>
            </section>
            <section class="auth-feature-card">
              <strong>Agent Workspace</strong>
              <span>聊天、智能体、工具和知识库会在同一个工作台里流动。</span>
            </section>
            <section class="nav-section auth-feature-list">
              <div class="section-title nav-title"><span>FEATURES</span></div>
              <div class="feature-row">
                <span>智能体协作</span>
                <small>为不同任务保存专属上下文</small>
              </div>
              <div class="feature-row">
                <span>工具调用</span>
                <small>MCP、Skill、知识库统一管理</small>
              </div>
              <div class="feature-row">
                <span>对话式设置</span>
                <small>配置项像消息一样打开</small>
              </div>
            </section>
            <section class="nav-section auth-entry-section">
              <div class="section-title nav-title">
                <span>ENTER</span>
                <button class="section-plus" type="button" title="重新选择入口" @click="showChoice">
                  <el-icon><Plus /></el-icon>
                </button>
              </div>
              <button class="nav-row nav-item" :class="{ active: activeMode === 'login' }" type="button" @click="chooseMode('login')">
                <el-icon><User /></el-icon>
                <span>登录</span>
                <small>进入已有工作台</small>
              </button>
              <button class="nav-row nav-item" :class="{ active: activeMode === 'register' }" type="button" @click="chooseMode('register')">
                <el-icon><Lock /></el-icon>
                <span>注册</span>
                <small>创建新的工作台</small>
              </button>
            </section>
          </div>

          <div v-else key="workspace" class="nav-scroll auth-session-list workspace-preview-list">
            <section class="nav-section">
              <div class="section-title agent-title">
                <button class="agent-title-main" type="button">
                  <img :src="zunoAgentAvatar" alt="Zuno" />
                  <span>Zuno</span>
                </button>
                <button class="section-plus" type="button" title="新建智能体对话">
                  <el-icon><Plus /></el-icon>
                </button>
              </div>
              <button class="nav-row active" type="button">
                <span>安全进入工作台</span>
              </button>
            </section>
            <section class="nav-section">
              <div class="section-title nav-title">
                <span>CHAT</span>
                <button class="section-plus" type="button" title="新建普通聊天">
                  <el-icon><Plus /></el-icon>
                </button>
              </div>
              <button class="nav-row" type="button">
                <span>New Chat</span>
              </button>
              <button class="nav-row muted" type="button">
                <span>工作区正在同步...</span>
              </button>
            </section>
          </div>
        </Transition>
      </div>

      <div class="sidebar-footer side-footer">
        <button class="settings-entry" type="button" title="登录后可进入设置" @click="showChoice">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </button>
        <div class="user-avatar-wrapper mini-avatar">
          <div class="user-avatar">
            <img :src="DEFAULT_USER_AVATAR" alt="用户头像" />
          </div>
        </div>
      </div>
      </div>
    </aside>

    <main class="content auth-main">
      <div class="workspace-chat active auth-workspace-chat">
        <div class="workspace-shell auth-workspace-shell">
      <section ref="conversationRef" class="conversation-panel auth-conversation">
        <article
          v-for="message in messages"
          :key="message.id"
          class="message-row auth-message"
          :class="[message.role, message.kind, message.status]"
        >
          <MascotPresence
            v-if="message.role === 'assistant'"
            class="avatar message-avatar auth-message-pet"
            size="avatar"
            :animated="message.status === 'thinking'"
            aria-label="Zuno"
          />
          <div class="message-stack">
            <div v-if="message.role === 'assistant'" class="message-name">Zuno</div>
            <div class="auth-bubble">
              <div v-if="message.status === 'thinking'" class="thinking-inline" aria-live="polite">
                <span>{{ message.text }}</span>
                <i></i>
                <i></i>
                <i></i>
              </div>
              <p v-else-if="message.text" class="message-text">{{ message.text }}</p>

              <div v-if="message.kind === 'choice'" class="choice-grid">
                <button type="button" class="choice-card" @click="chooseMode('login')">
                  <span class="choice-icon"><el-icon><User /></el-icon></span>
                  <strong>登录</strong>
                  <small>继续使用已有工作台</small>
                </button>
                <button type="button" class="choice-card" @click="chooseMode('register')">
                  <span class="choice-icon"><el-icon><Plus /></el-icon></span>
                  <strong>注册</strong>
                  <small>创建新的 Zuno 账号</small>
                </button>
              </div>

              <form v-if="message.kind === 'login'" class="auth-form" @submit.prevent="handleLogin">
                <label class="compact-field">
                  <span>账号</span>
                  <el-input v-model="loginForm.username" autocomplete="username" placeholder="输入账号" />
                </label>
                <label class="compact-field">
                  <span>密码</span>
                  <el-input
                    v-model="loginForm.password"
                    type="password"
                    autocomplete="current-password"
                    placeholder="输入密码"
                    show-password
                  />
                </label>
                <div class="form-actions">
                  <button type="button" class="quiet-link" @click="chooseMode('register')">创建账号</button>
                  <el-button native-type="submit" type="primary" :loading="loading">
                    进入工作台
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </div>
              </form>

              <form v-if="message.kind === 'register'" class="auth-form" @submit.prevent="handleRegister">
                <label class="compact-field">
                  <span>用户名</span>
                  <el-input v-model="registerForm.user_name" autocomplete="username" maxlength="20" placeholder="最多 20 个字符" />
                </label>
                <label class="compact-field">
                  <span>邮箱</span>
                  <el-input v-model="registerForm.user_email" autocomplete="email" placeholder="可选" />
                </label>
                <label class="compact-field">
                  <span>密码</span>
                  <el-input
                    v-model="registerForm.user_password"
                    type="password"
                    autocomplete="new-password"
                    placeholder="至少 6 位"
                    show-password
                  />
                </label>
                <label class="compact-field">
                  <span>确认</span>
                  <el-input
                    v-model="confirmPassword"
                    type="password"
                    autocomplete="new-password"
                    placeholder="再次输入密码"
                    show-password
                  />
                </label>
                <div class="form-actions">
                  <button type="button" class="quiet-link" @click="chooseMode('login')">已有账号</button>
                  <el-button native-type="submit" type="primary" :loading="loading">
                    创建账号
                    <el-icon><Check /></el-icon>
                  </el-button>
                </div>
              </form>
            </div>
          </div>
          <img v-if="message.role === 'user'" :src="DEFAULT_USER_AVATAR" alt="User" class="avatar user-avatar" />
        </article>
      </section>

      <div class="composer-dock fixed auth-composer">
        <button class="composer-collapsed composer-pill" type="button">
          <img class="composer-collapsed-icon" :src="messageIcon" alt="" />
          <span>给 Zuno 发消息</span>
        </button>
      </div>
      <div class="unlock-workspace-preview" aria-hidden="true">
        <div class="unlock-hero">
          <img :src="zunoAgentAvatar" alt="" />
          <h1>How can I help you today?</h1>
          <p>Your intelligent workspace is ready.</p>
        </div>
        <div class="unlock-composer">
          <span>输入你的问题，直接开始对话。</span>
          <button type="button">发送</button>
        </div>
      </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.auth-shell {
  height: 100vh;
  min-height: 0;
  display: grid;
  grid-template-columns: 264px minmax(0, 1fr);
  overflow: hidden;
  background:
    radial-gradient(circle at 22% 18%, rgba(245, 158, 11, 0.12), transparent 28%),
    linear-gradient(120deg, #fbfaf8 0%, #f5f2ed 42%, #faf7f1 100%);
  color: #111827;
  transition: opacity 0.42s ease, transform 0.42s ease, filter 0.42s ease;
}

.auth-shell.leaving {
  opacity: 0;
  transform: translate3d(0, -6px, 0) scale(1.002);
  filter: none;
  pointer-events: none;
}

.auth-sidebar {
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 24px 18px 20px;
  border-right: 1px solid rgba(226, 232, 240, 0.72);
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(24px);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}

.brand-icon,
.wordmark-icon,
.message-avatar,
.mini-avatar {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 247, 237, 0.96), rgba(255, 255, 255, 0.84));
  border: 1px solid rgba(245, 158, 11, 0.24);
  box-shadow: 0 12px 26px -20px rgba(146, 64, 14, 0.42);
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 14px;
}

.brand-icon img,
.wordmark-icon img,
.message-avatar img,
.mini-avatar img {
  width: 72%;
  height: 72%;
}

.brand-row strong {
  display: block;
  font-size: 19px;
  line-height: 1.1;
}

.brand-row span {
  display: block;
  margin-top: 3px;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
}

.new-chat-button {
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 0;
  border-radius: 9px;
  background: #f59e0b;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 14px 26px -18px rgba(245, 158, 11, 0.72);
}

.nav-section {
  display: grid;
  gap: 6px;
  margin-top: 18px;
}

.nav-title {
  margin: 0 0 4px 10px;
  color: #f59e0b;
  font-size: 11px;
  font-weight: 800;
}

.nav-item {
  height: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border: 0;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.nav-item.active,
.nav-item:hover {
  background: rgba(255, 247, 237, 0.92);
  color: #b45309;
}

.side-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(226, 232, 240, 0.78);
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #64748b;
  font-size: 13px;
  font-weight: 650;
}

.mini-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
}

.auth-main {
  position: relative;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.auth-conversation {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 36px 68px 118px;
  scroll-behavior: smooth;
}

.auth-message {
  width: min(900px, 100%);
  display: flex;
  gap: 10px;
  margin: 0 auto 10px;
  animation: authTurnEnter 0.34s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.auth-message.user {
  justify-content: flex-end;
  align-items: flex-start;
}

.message-avatar {
  width: 28px;
  height: 28px;
  margin-top: 2px;
  border-radius: 999px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  margin-top: 2px;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.28);
  background: rgba(255, 247, 237, 0.74);
  box-shadow: 0 12px 26px -20px rgba(146, 64, 14, 0.42);
}

.message-stack {
  min-width: 0;
  max-width: min(720px, calc(100% - 42px));
}

.auth-message.user .message-stack {
  max-width: min(420px, 78%);
}

.message-name {
  margin: 0 0 5px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.auth-bubble {
  padding: 12px 13px;
  border: 1px solid rgba(226, 232, 240, 0.76);
  border-radius: 18px;
  border-top-left-radius: 9px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 255, 255, 0.58)),
    rgba(255, 255, 255, 0.42);
  box-shadow:
    0 18px 44px -34px rgba(15, 23, 42, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(24px) saturate(1.12);
}

.auth-message.user .auth-bubble {
  border-color: rgba(245, 158, 11, 0.28);
  border-radius: 17px;
  border-top-right-radius: 7px;
  background: rgba(255, 247, 237, 0.82);
  color: #78350f;
}

.auth-message.user .message-stack {
  display: flex;
  justify-content: flex-end;
}

.auth-message.status .auth-bubble {
  border-radius: 14px;
}

.auth-message.success .auth-bubble {
  border-color: rgba(34, 197, 94, 0.26);
  background: rgba(240, 253, 244, 0.78);
  color: #166534;
}

.auth-message.error .auth-bubble {
  border-color: rgba(248, 113, 113, 0.34);
  background: rgba(254, 242, 242, 0.82);
  color: #991b1b;
}

.auth-message.thinking .auth-bubble {
  color: #92400e;
  background: rgba(255, 251, 235, 0.8);
}

.thinking-inline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 20px;
  color: #92400e;
  font-size: 12.5px;
  font-weight: 650;
}

.thinking-inline i {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: #f59e0b;
  opacity: 0.28;
  animation: authThinkingDot 1.12s ease-in-out infinite;
}

.thinking-inline i:nth-child(3) {
  animation-delay: 0.16s;
}

.thinking-inline i:nth-child(4) {
  animation-delay: 0.32s;
}

.message-text {
  margin: 0;
  color: inherit;
  font-size: 13px;
  line-height: 1.55;
}

.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.choice-card {
  min-height: 86px;
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  grid-template-rows: auto auto;
  align-content: center;
  gap: 3px 10px;
  padding: 12px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.58);
  cursor: pointer;
  text-align: left;
}

.choice-card:hover {
  border-color: rgba(245, 158, 11, 0.34);
  background: rgba(255, 247, 237, 0.68);
}

.choice-icon {
  grid-row: 1 / span 2;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 11px;
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.choice-card strong {
  color: #111827;
  font-size: 14px;
}

.choice-card small {
  color: #64748b;
  font-size: 11px;
}

.auth-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 11px;
}

.compact-field {
  min-width: 0;
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
}

.compact-field span {
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.compact-field :deep(.el-input__wrapper) {
  min-height: 34px;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 0 0 1px rgba(226, 232, 240, 0.86) inset;
}

.compact-field :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px rgba(245, 158, 11, 0.4) inset,
    0 0 0 4px rgba(245, 158, 11, 0.08);
}

.compact-field :deep(.el-input__inner) {
  font-size: 12.5px;
}

.form-actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  padding-top: 2px;
}

.quiet-link {
  height: 32px;
  padding: 0 10px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.quiet-link:hover {
  background: rgba(255, 247, 237, 0.8);
  color: #b45309;
}

.form-actions :deep(.el-button) {
  height: 33px;
  padding: 0 13px;
  border: 0;
  border-radius: 999px;
  background: #f59e0b;
  font-size: 12.5px;
  font-weight: 700;
}

.auth-composer {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 18px;
  display: flex;
  justify-content: center;
  pointer-events: none;
}

.composer-pill {
  min-width: min(280px, calc(100% - 48px));
  height: 52px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border: 1px solid rgba(245, 158, 11, 0.24);
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 247, 237, 0.48)),
    rgba(245, 158, 11, 0.12);
  color: #475569;
  font-size: 14px;
  font-weight: 760;
  box-shadow:
    0 18px 44px -28px rgba(146, 64, 14, 0.38),
    inset 0 1px 0 rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(28px) saturate(1.2);
}

@media (max-width: 900px) {
  .auth-shell {
    grid-template-columns: 1fr;
  }

  .auth-sidebar {
    display: none;
  }

  .auth-topbar {
    display: none;
  }

  .auth-conversation {
    padding: 20px 18px 102px;
  }

  .choice-grid,
  .auth-form {
    grid-template-columns: minmax(0, 1fr);
  }
}

.auth-shell {
  --workspace-sidebar-width: 288px;
  display: flex;
  flex-direction: row;
  background:
    radial-gradient(circle at 72% 22%, rgba(255, 255, 255, 0.9), transparent 34%),
    linear-gradient(135deg, #fbfbfd 0%, #f4f5f7 48%, #ffffff 100%);
  color: #111827;
}

.auth-sidebar {
  width: var(--workspace-sidebar-width);
  flex: 0 0 var(--workspace-sidebar-width);
  height: 100%;
  padding: 28px 24px 22px;
  gap: 22px;
  background: rgba(255, 255, 255, 0.72);
  border-right: 1px solid rgba(226, 232, 240, 0.62);
  box-shadow: 26px 0 70px rgba(15, 23, 42, 0.05);
  backdrop-filter: blur(30px);
}

.brand-row {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  align-items: center;
  gap: 14px;
  margin: 0;
  padding-bottom: 22px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.72);
}

.brand-icon {
  width: 48px;
  height: 48px;
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
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
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

.new-chat-button {
  width: 100%;
  min-height: 48px;
  height: auto;
  border-radius: 8px;
  background: #f59e0b;
  gap: 10px;
  font-size: 18px;
  box-shadow: 0 18px 34px rgba(245, 158, 11, 0.22);
  transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.new-chat-button:hover {
  background: #e89105;
  transform: translateY(-1px);
  box-shadow: 0 22px 38px rgba(245, 158, 11, 0.28);
}

.auth-session-list {
  flex: 1;
  min-height: 0;
  align-content: start;
  margin: 0;
  gap: 8px;
}

.nav-title {
  min-height: 32px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #f59e0b;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.01em;
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
}

.section-plus:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.nav-item {
  position: relative;
  width: 100%;
  min-height: 44px;
  height: auto;
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  align-content: center;
  align-items: center;
  justify-items: start;
  gap: 2px 10px;
  padding: 0 16px;
  border-radius: 8px;
  color: #8da0bc;
  text-align: left;
}

.nav-item span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  font-weight: 650;
}

.nav-item small {
  grid-column: 2;
  color: #aab7c8;
  font-size: 11px;
  line-height: 1.1;
}

.nav-item.active,
.nav-item:hover {
  color: #6b7f9a;
  background: rgba(245, 158, 11, 0.06);
}

.side-footer {
  position: relative;
  z-index: 12;
  gap: 12px;
  margin-top: auto;
  padding-top: 22px;
  border-top: 1px solid rgba(226, 232, 240, 0.72);
  color: #64748b;
  font-size: 16px;
  font-weight: 650;
}

.mini-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(226, 232, 240, 0.9);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.auth-main {
  flex: 1;
  background: #fffdf9;
}

.auth-conversation {
  width: min(860px, calc(100% - 24px));
  margin: 0 auto;
  padding: 24px 0 94px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-message {
  width: 100%;
  gap: 8px;
  margin: 0;
}

.message-avatar,
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex: 0 0 auto;
  background: transparent;
  border: none;
  box-shadow: none;
}

.message-avatar img,
.user-avatar {
  width: 28px;
  height: 28px;
}

.message-name {
  margin: 0 0 2px;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.message-stack {
  max-width: min(720px, calc(100% - 44px));
}

.auth-message.user .message-stack {
  max-width: min(420px, calc(100% - 44px));
}

.auth-bubble {
  padding: 9px 12px;
  border: none;
  border-radius: 18px;
  background: #f1f1f1;
  color: #171717;
  box-shadow: none;
  backdrop-filter: none;
  font-size: 14px;
  line-height: 1.6;
}

.auth-message.assistant .auth-bubble {
  background: transparent;
  color: #171717;
  padding-left: 2px;
}

.auth-message.user .auth-bubble {
  background: #f59e0b;
  color: #ffffff;
  border: none;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.16);
}

.auth-message.choice .auth-bubble,
.auth-message.login .auth-bubble,
.auth-message.register .auth-bubble {
  width: min(760px, calc(100vw - var(--workspace-sidebar-width) - 88px));
  padding: 18px;
  border-radius: 24px;
  border: 1px solid rgba(226, 232, 240, 0.84);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.68)),
    rgba(255, 247, 237, 0.24);
  box-shadow:
    0 20px 54px -32px rgba(15, 23, 42, 0.28),
    0 1px 0 rgba(255, 255, 255, 0.92) inset,
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  backdrop-filter: blur(28px) saturate(1.18);
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
}

.choice-grid {
  gap: 10px;
}

.choice-card {
  min-height: 82px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.58);
}

.compact-field :deep(.el-input__wrapper) {
  min-height: 36px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.78);
}

.form-actions :deep(.el-button) {
  min-height: 36px;
  border-radius: 999px;
  background: #f59e0b;
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.auth-composer {
  bottom: 20px;
}

.composer-pill {
  width: fit-content;
  min-width: min(276px, calc(100% - 40px));
  height: 54px;
  margin: 0 auto 8px;
  padding: 0 28px;
  border: 1px solid rgba(255, 255, 255, 0.68);
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.36), rgba(255, 255, 255, 0.18)),
    rgba(255, 255, 255, 0.16);
  color: rgba(51, 65, 85, 0.86);
  box-shadow:
    0 16px 42px -28px rgba(15, 23, 42, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(26px) saturate(1.28);
  font-size: 15px;
  font-weight: 620;
}

@media (max-width: 900px) {
  .auth-shell {
    --workspace-sidebar-width: 0px;
  }

  .auth-conversation {
    width: min(860px, calc(100% - 36px));
    padding: 20px 0 94px;
  }

  .auth-message.choice .auth-bubble,
  .auth-message.login .auth-bubble,
  .auth-message.register .auth-bubble {
    width: 100%;
  }
}

/* Login is a workspace state, not a separate product surface. Keep these
   values in lockstep with workspace.vue/defaultPage.vue's final density pass. */
.workspace-container.auth-shell {
  --workspace-sidebar-width: 264px;
  height: 100vh;
  min-height: 0;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  font-family: var(--zuno-font-sans);
  background:
    radial-gradient(circle at 74% 20%, rgba(255, 255, 255, 0.88), transparent 34%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.055), transparent 30%),
    #f9f9fb;
  color: #0f172a;
}

.mobile-only {
  display: none;
}

.auth-sidebar {
  width: var(--workspace-sidebar-width);
  flex: 0 0 var(--workspace-sidebar-width);
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: visible;
  padding: 0;
  background: rgba(255, 255, 255, 0.7);
  border-right: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 40px 0 80px -20px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(30px);
}

.auth-sidebar.collapsed {
  width: 54px;
  flex-basis: 54px;
}

.sidebar-rail {
  height: 100%;
  display: grid;
  align-content: start;
  justify-items: center;
  padding: 18px 10px;
}

.sidebar-body {
  height: 100%;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  overflow: visible;
}

.brand-row.brand-block {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr) 22px;
  align-items: center;
  gap: 10px;
  margin: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.brand-icon {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 10px;
  background: transparent;
  box-shadow: none;
  padding: 0;
}

.brand-icon img {
  width: 34px;
  height: 34px;
  object-fit: contain;
  filter: none;
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 2px;
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
  border: none;
  border-radius: 8px;
  display: grid;
  place-items: center;
  color: #94a3b8;
  background: transparent;
  cursor: pointer;
}

.rail-toggle:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
}

.primary-new-chat.new-chat-button {
  width: 100%;
  min-height: 36px;
  height: auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: none;
  border-radius: 8px;
  background: #f59e0b;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.primary-new-chat.new-chat-button:hover {
  background: #e89105;
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(245, 158, 11, 0.22);
}

.auth-session-list {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 2px;
  margin: 0;
  overflow: hidden auto;
}

.auth-intro-panel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding-top: 2px;
  overflow: hidden auto;
}

.sidebar-panel-slot {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
  display: flex;
  overflow: hidden;
  isolation: isolate;
}

.sidebar-panel-slot > .nav-scroll {
  width: 100%;
  min-width: 0;
  will-change: transform, opacity;
  backface-visibility: hidden;
}

.auth-intro-panel > *,
.workspace-preview-list > .nav-section {
  animation: sidebarItemRise 0.42s cubic-bezier(0.18, 0.82, 0.18, 1) both;
}

.auth-intro-panel > *:nth-child(2),
.workspace-preview-list > .nav-section:nth-child(2) {
  animation-delay: 0.05s;
}

.auth-intro-panel > *:nth-child(3),
.workspace-preview-list > .nav-section:nth-child(3) {
  animation-delay: 0.1s;
}

.auth-intro-panel > *:nth-child(4),
.workspace-preview-list > .nav-section:nth-child(4) {
  animation-delay: 0.15s;
}

.auth-mascot-card {
  min-height: 196px;
  display: grid;
  place-items: center;
  padding: 10px 0 4px;
  overflow: visible;
}

.auth-code-pet {
  width: 120px;
  height: 120px;
  transform: translateZ(0) scale(1.32);
  transform-origin: center center;
  backface-visibility: hidden;
  will-change: transform;
}

.auth-feature-card {
  display: grid;
  gap: 6px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(245, 158, 11, 0.16);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 247, 237, 0.42)),
    rgba(245, 158, 11, 0.06);
  box-shadow: 0 14px 30px -26px rgba(146, 64, 14, 0.34);
}

.auth-feature-card strong {
  color: #92400e;
  font-size: 13px;
  font-weight: 650;
}

.auth-feature-card span,
.feature-row small {
  color: #94a3b8;
  font-size: 11px;
  line-height: 1.45;
}

.auth-feature-list {
  display: grid;
  gap: 6px;
}

.feature-row {
  display: grid;
  gap: 2px;
  padding: 8px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.46);
}

.feature-row span {
  color: #64748b;
  font-size: 12px;
  font-weight: 560;
}

.sidebar-panel-enter-active,
.sidebar-panel-leave-active {
  transition:
    opacity 0.28s ease,
    transform 0.34s cubic-bezier(0.18, 0.82, 0.18, 1);
}

.sidebar-panel-leave-active {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.sidebar-panel-enter-from {
  opacity: 0;
  transform: translate3d(-10px, 0, 0);
}

.sidebar-panel-leave-to {
  opacity: 0;
  transform: translate3d(8px, 0, 0);
}

.auth-session-list .nav-section {
  display: grid;
  gap: 6px;
}

.section-title.nav-title {
  min-height: 20px;
  margin: 0;
  padding: 0 2px 0 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #f59e0b;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.section-plus {
  width: 20px;
  height: 20px;
  flex-basis: 20px;
  border: none;
  border-radius: 7px;
  display: grid;
  place-items: center;
  color: #94a3b8;
  background: transparent;
  cursor: pointer;
}

.section-plus:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.nav-row.nav-item {
  width: 100%;
  min-height: 28px;
  height: auto;
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  align-content: center;
  align-items: center;
  justify-items: start;
  gap: 0 8px;
  padding: 0 10px;
  border: none;
  border-radius: 8px;
  color: #94a3b8;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.nav-row.nav-item span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: inherit;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.35;
}

.nav-row.nav-item small {
  display: none;
}

.nav-row.nav-item:hover,
.nav-row.nav-item.active {
  color: #b45309;
  background: rgba(245, 158, 11, 0.075);
}

.workspace-preview-list .section-title {
  padding: 0 2px 0 10px;
}

.agent-title {
  min-height: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.agent-title-main {
  min-width: 0;
  border: none;
  padding: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #f59e0b;
  background: transparent;
  font: inherit;
  cursor: default;
}

.agent-title-main img {
  width: 16px;
  height: 16px;
  border-radius: 5px;
}

.workspace-preview-list .nav-row {
  width: 100%;
  min-height: 28px;
  border: none;
  border-radius: 8px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  background: transparent;
  text-align: left;
}

.workspace-preview-list .nav-row span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  font-weight: 500;
}

.workspace-preview-list .nav-row.active {
  color: #b45309;
  background: rgba(245, 158, 11, 0.075);
}

.workspace-preview-list .nav-row.muted {
  min-height: auto;
  padding-block: 5px;
  color: #a3b1c2;
}

.sidebar-footer.side-footer {
  position: relative;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.58);
}

.settings-entry {
  min-height: 30px;
  padding: 0 6px;
  border: none;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  background: transparent;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
}

.settings-entry:hover {
  color: #b45309;
  background: transparent;
}

.user-avatar-wrapper.mini-avatar {
  width: 30px;
  height: 30px;
  display: grid;
  place-items: center;
  overflow: hidden;
  border-radius: 50%;
  background: rgba(255, 251, 245, 0.96);
  border: 1px solid rgba(226, 232, 240, 0.78);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06) !important;
}

.user-avatar-wrapper .user-avatar {
  width: 23px;
  height: 23px;
  border-radius: 50%;
  overflow: hidden;
}

.user-avatar-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.auth-main {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  overflow: hidden;
  background: #fffdf9;
}

.auth-workspace-chat {
  flex: 1;
  height: 100%;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fffdf9;
}

.auth-workspace-shell {
  flex: 1;
  height: 100%;
  min-height: 0;
  min-width: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0 18px 24px;
  overflow: hidden;
}

.auth-conversation.conversation-panel {
  flex: 1 1 auto;
  width: min(1010px, calc(100% - 44px));
  margin: 0 auto;
  min-height: 0;
  min-width: 0;
  padding: 20px 30px 92px 0;
  border-radius: 0 22px 22px 0;
  overflow-y: auto;
  overflow-x: hidden;
  overflow-anchor: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background:
    linear-gradient(
      90deg,
      transparent 0,
      transparent calc(100% - 58px),
      rgba(255, 255, 255, 0.3) calc(100% - 58px),
      rgba(255, 247, 237, 0.18) 100%
    );
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: rgba(120, 113, 108, 0.22) transparent;
  scroll-behavior: auto;
  transition: opacity 0.62s ease, transform 0.62s cubic-bezier(0.2, 0.8, 0.2, 1), filter 0.62s ease;
}

.auth-conversation::-webkit-scrollbar {
  width: 16px;
}

.auth-conversation::-webkit-scrollbar-track {
  margin: 18px 0 108px;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.2), rgba(255, 247, 237, 0.18)),
    rgba(255, 255, 255, 0.14);
}

.auth-conversation::-webkit-scrollbar-thumb {
  min-height: 56px;
  border: 6px solid transparent;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(146, 64, 14, 0.26), rgba(120, 113, 108, 0.2))
    content-box;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.28);
}

.auth-message.message-row {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0;
  contain: layout paint;
  transform-origin: left top;
  backface-visibility: hidden;
  will-change: opacity, transform;
  animation: authTurnEnter 0.34s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

.auth-message.user {
  justify-content: flex-end;
  transform-origin: right top;
}

.avatar.message-avatar,
.avatar.user-avatar {
  width: 28px;
  height: 28px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: transparent;
  border: none;
  box-shadow: none;
}

.avatar.message-avatar img,
.avatar.user-avatar {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.avatar.message-avatar.auth-message-pet {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  margin-top: 17px;
  border-radius: 0;
  background: transparent;
  border: none;
  box-shadow: none;
  --mascot-slot-size: 44px;
  --mascot-scale: 0.3666667;
}

.message-stack {
  min-width: 0;
  max-width: min(720px, calc(100% - 44px));
  display: grid;
  gap: 3px;
}

.auth-message.user .message-stack {
  max-width: min(420px, calc(100% - 44px));
}

.message-name {
  margin: 0 0 2px;
  padding-left: 2px;
  color: #64748b;
  font-size: 12px;
  font-weight: 650;
}

.auth-bubble {
  width: fit-content;
  max-width: 100%;
  padding: 9px 12px;
  border-radius: 22px;
  border: 1px solid rgba(226, 232, 240, 0.74);
  background: rgba(255, 255, 255, 0.76);
  color: #171717;
  box-shadow: 0 14px 34px -28px rgba(15, 23, 42, 0.24);
  font-size: 14px;
  line-height: 1.6;
  backdrop-filter: blur(22px);
}

.auth-message.assistant.text .auth-bubble,
.auth-message.assistant.status .auth-bubble {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
  backdrop-filter: none;
  padding-left: 2px;
}

.auth-message.user .auth-bubble {
  background: #f59e0b;
  color: #ffffff;
  border-color: transparent;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.16);
}

.auth-message.choice .auth-bubble,
.auth-message.login .auth-bubble,
.auth-message.register .auth-bubble {
  width: min(860px, calc(100vw - var(--workspace-sidebar-width) - 92px));
  padding: 18px;
  border-radius: var(--zuno-radius-composer, 26px) var(--zuno-radius-composer, 26px) var(--zuno-radius-composer, 26px) 10px;
  border: 1px solid var(--zuno-glass-border, rgba(226, 232, 240, 0.84));
  background: var(--zuno-glass-surface, rgba(255, 255, 255, 0.76));
  box-shadow: var(--zuno-shadow-composer, 0 20px 60px -15px rgba(15, 23, 42, 0.11)), inset 0 1px 0 rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(28px);
}

.auth-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
  margin-top: 10px;
}

.auth-message.register .auth-form {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.compact-field {
  display: grid;
  grid-template-columns: 46px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.compact-field span {
  color: #475569;
  font-size: 12px;
  font-weight: 650;
}

.compact-field :deep(.el-input__wrapper) {
  min-height: 32px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 0 0 1px rgba(226, 232, 240, 0.86) inset;
}

.form-actions {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.form-actions :deep(.el-button) {
  min-height: 32px;
  border-radius: 999px;
  background: #f59e0b;
  border-color: #f59e0b;
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.choice-card {
  min-height: 74px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.58);
}

.auth-composer.composer-dock.fixed {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 14px;
  z-index: 18;
  width: 100%;
  padding: 0 24px;
  background: transparent !important;
  pointer-events: none;
}

.auth-composer.composer-dock.fixed > * {
  pointer-events: auto;
}

.composer-pill.composer-collapsed {
  width: fit-content;
  min-width: min(276px, calc(100% - 40px));
  height: 54px;
  margin: 0 auto 8px;
  padding: 0 28px;
  border: 1px solid rgba(245, 158, 11, 0.26);
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(255, 247, 237, 0.48)),
    rgba(245, 158, 11, 0.16);
  color: rgba(120, 53, 15, 0.9);
  box-shadow:
    0 18px 44px -28px rgba(146, 64, 14, 0.44),
    0 1px 0 rgba(255, 255, 255, 0.72) inset;
  backdrop-filter: blur(32px) saturate(1.35);
  font-size: 15px;
  font-weight: 620;
}

.composer-collapsed-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
  filter: drop-shadow(0 8px 12px rgba(180, 83, 9, 0.18));
}

.unlock-workspace-preview {
  position: absolute;
  inset: 0 18px 24px;
  z-index: 16;
  display: grid;
  place-items: center;
  pointer-events: none;
  opacity: 0;
  transform: translate3d(0, 28px, 0) scale(0.99);
  filter: none;
  transition:
    opacity 0.68s ease 0.12s,
    transform 0.68s cubic-bezier(0.2, 0.8, 0.2, 1) 0.12s;
}

.unlock-hero {
  width: min(720px, calc(100% - 24px));
  display: grid;
  justify-items: center;
  gap: 10px;
  margin-bottom: 120px;
  text-align: center;
}

.unlock-hero img {
  width: 58px;
  height: 58px;
  object-fit: contain;
  filter: drop-shadow(0 14px 24px rgba(245, 158, 11, 0.18));
}

.unlock-hero h1 {
  margin: 0;
  color: #171717;
  font-size: 32px;
  font-weight: 520;
  line-height: 1.2;
  letter-spacing: 0;
}

.unlock-hero p {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}

.unlock-composer {
  position: absolute;
  left: 50%;
  bottom: 132px;
  width: min(720px, calc(100% - 48px));
  min-height: 112px;
  transform: translateX(-50%);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.74);
  box-shadow:
    0 30px 80px rgba(15, 23, 42, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(26px) saturate(1.2);
}

.unlock-composer span {
  color: #94a3b8;
  font-size: 15px;
}

.unlock-composer button {
  align-self: flex-end;
  min-width: 74px;
  height: 36px;
  border: none;
  border-radius: 999px;
  color: #ffffff;
  background: #f59e0b;
  font-weight: 650;
}

.auth-shell.unlocking .auth-conversation {
  opacity: 0.08;
  transform: translate3d(0, -30px, 0) scale(0.99);
  filter: none;
}

.auth-shell.unlocking .auth-composer {
  opacity: 0;
  transform: translateY(18px);
  transition: opacity 0.36s ease, transform 0.36s ease;
}

.auth-shell.unlocking .unlock-workspace-preview {
  opacity: 1;
  transform: translate3d(0, 0, 0) scale(1);
  filter: none;
}

@media (max-width: 900px) {
  .workspace-container.auth-shell {
    --workspace-sidebar-width: 0px;
  }

  .auth-sidebar {
    display: none;
  }

  .mobile-only {
    display: grid;
  }

  .auth-workspace-shell {
    padding: 72px 16px 18px;
  }

  .auth-conversation.conversation-panel {
    width: min(100%, calc(100% - 8px));
    padding-right: 8px;
    padding-bottom: 84px;
  }

  .auth-message.choice .auth-bubble,
  .auth-message.login .auth-bubble,
  .auth-message.register .auth-bubble {
    width: 100%;
  }

  .auth-form,
  .auth-message.register .auth-form {
    grid-template-columns: 1fr;
  }
}

@keyframes authTurnEnter {
  from {
    opacity: 0;
    transform: translate3d(0, 10px, 0) scale(0.988);
    filter: none;
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
    filter: none;
  }
}

@keyframes sidebarItemRise {
  from {
    opacity: 0;
    transform: translate3d(-10px, 0, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

@keyframes authThinkingDot {
  0%, 100% {
    opacity: 0.24;
    transform: translateY(0);
  }
  45% {
    opacity: 0.88;
    transform: translateY(-3px);
  }
}
</style>
