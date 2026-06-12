<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, Check, Plus, User } from '@element-plus/icons-vue'
import { getUserInfoAPI, loginAPI, registerAPI } from '../../apis/auth'
import type { RegisterForm } from '../../apis/auth'
import { useUserStore } from '../../store/user'
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
  unlocking?: boolean
}>(), {
  initialMode: 'choice',
  unlocking: false,
})

const emit = defineEmits<{
  (event: 'authenticated'): void
}>()

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const conversationRef = ref<HTMLElement | null>(null)
const activeMode = ref<AuthMode>('choice')
const loading = ref(false)
const messages = ref<AuthMessage[]>([])
const introStarted = ref(false)
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

const zunoAscii = [
  '███████╗  ██╗   ██╗  ███╗   ██╗   ██████╗        █████╗   ██╗',
  '╚══███╔╝  ██║   ██║  ████╗  ██║  ██╔═══██╗      ██╔══██╗  ██║',
  '  ███╔╝   ██║   ██║  ██╔██╗ ██║  ██║   ██║      ███████║  ██║',
  ' ███╔╝    ██║   ██║  ██║╚██╗██║  ██║   ██║      ██╔══██║  ██║',
  '███████╗  ╚██████╔╝  ██║ ╚████║  ╚██████╔╝      ██║  ██║  ██║',
  '╚══════╝   ╚═════╝   ╚═╝  ╚═══╝   ╚═════╝       ╚═╝  ╚═╝  ╚═╝',
].join('\n')

const heroLifted = computed(() => introStarted.value)
const INTRO_FIRST_MESSAGE_DELAY = 1040

const wait = (ms: number) => new Promise<void>((resolve) => window.setTimeout(resolve, ms))

const scrollToBottom = async () => {
  await nextTick()
  await new Promise<void>((resolve) => window.requestAnimationFrame(() => resolve()))
  const target = conversationRef.value
  if (!target) return
  target.scrollTop = target.scrollHeight
}

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

const appendThinking = async (text = 'Zuno 正在准备入口...', duration = 560) => {
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

const replaceAuthModeQuery = (mode: AuthMode) => {
  router.replace({
    name: route.name || 'workspaceDefaultPage',
    params: route.params,
    query: {
      ...route.query,
      auth: mode,
    },
  })
}

const chooseMode = async (mode: Exclude<AuthMode, 'choice'>, fromRoute = false) => {
  if (loading.value) return
  activeMode.value = mode
  await appendMessage({
    role: 'user',
    kind: 'text',
    text: mode === 'login' ? '我想登录' : '我想注册',
  })
  await appendThinking('收到，我先把入口准备好...', 520)
  await appendMessage({
    role: 'assistant',
    kind: 'text',
    text: mode === 'login' ? '接下来只需要确认账号和密码。' : '接下来创建一个轻量账号。',
  })
  await appendThinking(mode === 'login' ? '正在展开登录气泡...' : '正在展开注册气泡...', 560)
  await appendMessage({
    role: 'assistant',
    kind: mode,
    text: mode === 'login'
      ? '好的，填入账号和密码。确认通过后，工作台会在这里自然浮现。'
      : '没问题，先创建账号。注册完成后，我会把你带回登录步骤。',
  })
  if (!fromRoute) replaceAuthModeQuery(mode)
}

const presentModeForm = async (mode: Exclude<AuthMode, 'choice'>) => {
  if (loading.value) return
  activeMode.value = mode
  await appendThinking(mode === 'login' ? '正在展开登录气泡...' : '正在展开注册气泡...', 560)
  await appendMessage({
    role: 'assistant',
    kind: mode,
    text: mode === 'login'
      ? '把账号和密码填在这里。确认通过后，工作台会在这里自然浮现。'
      : '先创建一个 Zuno 账号。完成后我会把你带回登录步骤。',
  })
}

const showChoice = async () => {
  if (loading.value) return
  activeMode.value = 'choice'
  resetSecrets()
  await appendMessage({
    role: 'user',
    kind: 'text',
    text: '我想换一种进入方式',
  })
  await appendThinking('正在整理两个入口...')
  await appendMessage({
    role: 'assistant',
    kind: 'choice',
    text: '当然。你想登录已有账号，还是注册一个新账号？',
  })
  replaceAuthModeQuery('choice')
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
    await appendThinking('正在确认身份...', 520)
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
      await appendMessage({ role: 'assistant', kind: 'status', status: 'success', text: '身份确认完成，正在打开工作台。' })
      await wait(380)
      emit('authenticated')
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
    await appendThinking('正在创建账号...', 520)
    const response = await registerAPI(registerForm)
    const responseData: any = response.data

    if (responseData.status_code === 200) {
      const createdName = registerForm.user_name
      loginForm.username = createdName
      resetSecrets()
      await appendMessage({ role: 'assistant', kind: 'status', status: 'success', text: '账号已创建。现在输入密码就能进入工作台。' })
      activeMode.value = 'login'
      await appendThinking('正在切回登录入口...', 460)
      await appendMessage({
        role: 'assistant',
        kind: 'login',
        text: '我已经把用户名带过来了，只需要输入密码。',
      })
      replaceAuthModeQuery('login')
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

const startIntro = async () => {
  if (introStarted.value) return
  introStarted.value = true
  await wait(INTRO_FIRST_MESSAGE_DELAY)
  await appendMessage({
    role: 'assistant',
    kind: 'text',
    text: '你好，我是 Zuno。工作台还在门后，先确认一下身份。',
  })
  await wait(760)
  await appendMessage({
    role: 'assistant',
    kind: 'text',
    text: '登录前不会加载聊天、智能体或设置内容。',
  })
  await appendThinking('正在准备安全入口...', 980)
  await appendMessage({
    role: 'assistant',
    kind: 'text',
    text: props.initialMode === 'login'
      ? '准备好了，我把登录入口放在下面。'
      : props.initialMode === 'register'
        ? '准备好了，我把注册入口放在下面。'
        : '准备好了。选择一种进入方式就行。',
  })
  if (props.initialMode === 'login' || props.initialMode === 'register') {
    window.setTimeout(() => {
      void presentModeForm(props.initialMode as Exclude<AuthMode, 'choice'>)
    }, 620)
    return
  }
  await wait(520)
  await appendMessage({
    role: 'assistant',
    kind: 'choice',
    text: '你想登录已有账号，还是注册一个新账号？',
  })
}

onMounted(() => {
  userStore.initUserState()
})
</script>

<template>
  <section class="workspace-auth-gate" :class="{ unlocking: props.unlocking, 'hero-lifted': heroLifted }">
    <div class="auth-stage">
      <button class="auth-hero" type="button" aria-label="唤醒 Zuno" @click="startIntro">
        <pre class="zuno-ascii">{{ zunoAscii }}</pre>
      </button>

      <div ref="conversationRef" class="auth-conversation">
        <article
          v-for="message in messages"
          :key="message.id"
          class="auth-message"
          :class="[message.role, message.kind, message.status]"
        >
          <MascotPresence
            v-if="message.role === 'assistant'"
            class="auth-avatar assistant-pet-avatar"
            size="avatar"
            :animated="message.status === 'thinking'"
            aria-label="Zuno"
          />
          <div class="auth-stack">
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
                  <small>进入已有工作台</small>
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
                  <button type="button" class="quiet-link" @click="chooseMode('register')">
                    创建账号
                  </button>
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
                  <button type="button" class="quiet-link" @click="chooseMode('login')">
                    已有账号
                  </button>
                  <el-button native-type="submit" type="primary" :loading="loading">
                    创建账号
                    <el-icon><Check /></el-icon>
                  </el-button>
                </div>
              </form>
            </div>
          </div>

          <img v-if="message.role === 'user'" :src="DEFAULT_USER_AVATAR" alt="User" class="auth-avatar user" />
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped lang="scss">
.workspace-auth-gate {
  height: 100%;
  min-height: 0;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 28%, rgba(245, 158, 11, 0.09), transparent 32%),
    radial-gradient(circle at 78% 8%, rgba(255, 255, 255, 0.92), transparent 30%),
    linear-gradient(180deg, rgba(250, 250, 249, 0.86), rgba(248, 245, 239, 0.78));
  transition: opacity 0.55s ease, transform 0.55s ease, filter 0.55s ease;
}

.workspace-auth-gate.unlocking {
  opacity: 0;
  transform: translate3d(0, -18px, 0) scale(0.992);
  filter: none;
  pointer-events: none;
}

.auth-stage {
  height: 100%;
  min-height: 0;
  position: relative;
  overflow: hidden;
}

.auth-hero {
  position: absolute;
  top: 47%;
  left: 50%;
  z-index: 4;
  width: min(900px, 84vw);
  display: grid;
  justify-items: center;
  gap: 24px;
  border: none;
  padding: 0;
  background: transparent;
  color: rgba(15, 23, 42, 0.78);
  text-align: center;
  cursor: pointer;
  transform: translate3d(-50%, -50%, 0) scale(1);
  transform-origin: center center;
  backface-visibility: hidden;
  contain: layout;
  transition: none;
}

.auth-hero:focus-visible {
  outline: none;
}

.hero-lifted .auth-hero {
  z-index: 3;
  top: 47%;
  filter: none;
  pointer-events: none;
  animation: auth-hero-lift 1.9s linear both;
}

.zuno-ascii {
  margin: 0;
  white-space: pre;
  font-family: var(--zuno-font-mono);
  font-weight: 800;
  letter-spacing: 0;
  line-height: 1.08;
  text-shadow: none;
  color: #0f172a;
  font-size: clamp(8px, 1vw, 15px);
}

.auth-conversation {
  position: absolute;
  inset: 0;
  z-index: 2;
  min-height: 0;
  overflow-y: auto;
  overflow-anchor: none;
  padding:
    clamp(198px, 29vh, 256px)
    clamp(60px, 9vw, 150px)
    76px
    clamp(72px, 10vw, 170px);
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.28) transparent;
  scroll-behavior: auto;
  opacity: 0;
  transform: translate3d(0, 10px, 0);
  transition:
    opacity 0.58s cubic-bezier(0.22, 1, 0.36, 1),
    transform 0.62s cubic-bezier(0.22, 1, 0.36, 1),
    padding-top 1.2s cubic-bezier(.16, .78, .18, 1);
}

.hero-lifted .auth-conversation {
  opacity: 1;
  transform: translate3d(0, 0, 0);
}

.auth-conversation::-webkit-scrollbar {
  width: 8px;
}

.auth-conversation::-webkit-scrollbar-thumb {
  border: 3px solid transparent;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.28);
  background-clip: padding-box;
}

.auth-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 18px;
  opacity: 0;
  transform: translateY(12px);
  contain: layout;
  transform-origin: left top;
  backface-visibility: visible;
  animation: auth-message-in 0.46s cubic-bezier(.2, .7, .16, 1) forwards;
}

.auth-message.user {
  justify-content: flex-end;
  transform-origin: right top;
}

.auth-avatar {
  width: 28px;
  height: 28px;
  flex: 0 0 28px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.86);
  box-shadow: none;
}

.auth-avatar img,
.auth-avatar.user {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}

.auth-avatar.assistant-pet-avatar {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  margin-top: 22px;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  --mascot-slot-size: 44px;
  --mascot-scale: 0.3666667;
}

.auth-stack {
  max-width: min(760px, calc(100vw - 440px));
}

.message-name {
  margin: 1px 0 8px;
  color: #111827;
  font-size: 14px;
  font-weight: 800;
}

.auth-bubble {
  border: 1px solid rgba(226, 232, 240, 0.74);
  border-radius: 24px;
  border-top-left-radius: 10px;
  padding: 18px 20px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: none;
  backdrop-filter: none;
  filter: none;
  contain: layout;
}

.auth-message.user .auth-bubble {
  border-radius: 20px;
  border-top-right-radius: 8px;
  background: #f59e0b;
  color: #fff;
  box-shadow: 0 16px 36px rgba(245, 158, 11, 0.22);
}

.message-text {
  margin: 0;
  color: #64748b;
  font-size: 15px;
  line-height: 1.7;
}

.auth-message.user .message-text {
  color: #fff;
  font-weight: 700;
}

.thinking-inline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 14px;
  font-weight: 650;
}

.thinking-inline i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #f59e0b;
  animation: thinking-dot 0.95s ease-in-out infinite;
}

.thinking-inline i:nth-child(3) {
  animation-delay: 0.12s;
}

.thinking-inline i:nth-child(4) {
  animation-delay: 0.24s;
}

.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.choice-card {
  min-height: 112px;
  display: grid;
  align-content: center;
  gap: 7px;
  padding: 16px;
  border: 1px solid rgba(245, 158, 11, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.78);
  color: #111827;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.choice-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.42);
  box-shadow: 0 16px 34px rgba(245, 158, 11, 0.12);
}

.choice-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 13px;
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  font-size: 18px;
}

.choice-card strong {
  font-size: 17px;
  font-weight: 850;
}

.choice-card small {
  color: #64748b;
  font-size: 13px;
  line-height: 1.45;
}

.auth-form {
  display: grid;
  gap: 12px;
  min-width: min(520px, 62vw);
  margin-top: 16px;
}

.compact-field {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
}

.compact-field > span {
  color: #64748b;
  font-size: 13px;
  font-weight: 750;
}

.compact-field :deep(.el-input__wrapper) {
  min-height: 38px;
  border-radius: 14px;
  box-shadow: 0 0 0 1px rgba(226, 232, 240, 0.9) inset;
  background: rgba(255, 255, 255, 0.74);
}

.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 4px;
}

.quiet-link {
  border: none;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.form-actions :deep(.el-button--primary) {
  min-height: 38px;
  padding: 0 18px;
  border: none;
  border-radius: 999px;
  background: #f59e0b;
  box-shadow: 0 16px 30px rgba(245, 158, 11, 0.2);
}

@keyframes auth-message-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes auth-hero-lift {
  from {
    opacity: 1;
    transform: translate3d(-50%, -50%, 0) scale(1);
  }
  to {
    opacity: 0.12;
    transform: translate3d(-50%, calc(-50% - min(34vh, 260px)), 0) scale(0.48);
  }
}

@keyframes thinking-dot {
  0%,
  100% {
    opacity: 0.26;
    transform: translateY(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

@media (max-width: 860px) {
  .auth-hero {
    width: 88vw;
  }

  .auth-conversation {
    padding:
      170px
      16px
      42px
      16px;
  }

  .auth-stack {
    max-width: calc(100vw - 84px);
  }

  .auth-avatar.assistant-pet-avatar {
    width: 38px;
    height: 38px;
    flex-basis: 38px;
    margin-top: 22px;
    --mascot-slot-size: 38px;
    --mascot-scale: 0.3166667;
  }

  .choice-grid {
    grid-template-columns: 1fr;
  }

  .auth-form {
    min-width: 0;
  }

  .compact-field {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
