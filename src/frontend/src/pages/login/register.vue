<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import { registerAPI } from '../../apis/auth'
import type { RegisterForm } from '../../apis/auth'
import zunoAvatar from '../../assets/zuno-avatar.svg'
import zunoWordmark from '../../assets/zuno-wordmark.svg'

const router = useRouter()

const registerForm = reactive<RegisterForm>({
  user_name: '',
  user_email: '',
  user_password: '',
})

const confirmPassword = ref('')
const loading = ref(false)

const extractErrorMessage = (error: any) => {
  const payload = error?.response?.data
  if (typeof payload?.status_message === 'string' && payload.status_message.trim()) {
    return payload.status_message
  }
  if (typeof payload?.detail === 'string' && payload.detail.trim()) {
    return payload.detail
  }
  return ''
}

const validateForm = () => {
  if (!registerForm.user_name) {
    ElMessage.warning('请输入用户名')
    return false
  }

  if (registerForm.user_name.length > 20) {
    ElMessage.warning('用户名长度不能超过 20 个字符')
    return false
  }

  if (!registerForm.user_password) {
    ElMessage.warning('请输入密码')
    return false
  }

  if (registerForm.user_password.length < 6) {
    ElMessage.warning('密码长度至少 6 个字符')
    return false
  }

  if (registerForm.user_password !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致')
    return false
  }

  if (registerForm.user_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.user_email)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validateForm()) return

  try {
    loading.value = true
    const response = await registerAPI(registerForm)

    if (response.data.status_code === 200) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
      return
    }

    ElMessage.error(response.data.status_message || '注册失败')
  } catch (error: any) {
    console.error('注册错误:', error)
    const message = extractErrorMessage(error)
    if (message) {
      ElMessage.error(message)
    } else {
      ElMessage.error('注册失败，请确认后端服务已启动')
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-page">
    <section class="register-hero">
      <div class="hero-surface">
        <div class="hero-badge">Create your Zuno account</div>
        <img :src="zunoAvatar" alt="Zuno" class="hero-avatar" />
        <h1>让你的工作台从这里开始</h1>
        <p>创建账号后，你就能把对话、搜索、工具和执行流都收进同一套工作空间里，用更稳定的方式推进任务。</p>
        <div class="hero-points">
          <span>聊天即工作流</span>
          <span>搜索默认可用</span>
          <span>会话持续保存</span>
        </div>
      </div>
    </section>

    <section class="register-panel">
      <div class="panel-shell">
        <div class="brand-block">
          <img :src="zunoWordmark" alt="Zuno" class="brand-wordmark" />
          <p>创建一个新的 Zuno 账号。</p>
        </div>

        <div class="register-form">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <el-input
              v-model="registerForm.user_name"
              placeholder="输入用户名，最多 20 个字符"
              size="large"
              class="register-input"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">邮箱</label>
            <el-input
              v-model="registerForm.user_email"
              placeholder="输入邮箱地址，可选"
              size="large"
              class="register-input"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <el-input
              v-model="registerForm.user_password"
              type="password"
              placeholder="输入密码，至少 6 位"
              size="large"
              class="register-input"
              show-password
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">确认密码</label>
            <el-input
              v-model="confirmPassword"
              type="password"
              placeholder="再次输入密码"
              size="large"
              class="register-input"
              show-password
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-row">
            <span class="login-text">已经有账号？</span>
            <button type="button" class="text-link" @click="goToLogin">登录</button>
          </div>

          <el-button
            type="primary"
            size="large"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            <span>创建账号</span>
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>

        <div class="panel-footer">
          <div class="version-badge">v2.4.0</div>
          <div class="footer-links">
            <a href="https://github.com/ProfessorZhi/Zuno" target="_blank" rel="noreferrer">GitHub</a>
            <a href="https://github.com/ProfessorZhi/Zuno/tree/main/docs" target="_blank" rel="noreferrer">帮助</a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(360px, 470px);
  background:
    radial-gradient(circle at top left, rgba(214, 138, 68, 0.18), transparent 32%),
    radial-gradient(circle at bottom left, rgba(231, 203, 165, 0.18), transparent 28%),
    linear-gradient(180deg, #f7f0e6 0%, #f4ede2 100%);
  color: #2f261f;
}

.register-hero {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
}

.hero-surface {
  width: min(560px, 100%);
  padding: 48px;
  border-radius: 32px;
  border: 1px solid rgba(205, 162, 115, 0.22);
  background: linear-gradient(180deg, rgba(255, 250, 244, 0.92) 0%, rgba(250, 242, 232, 0.94) 100%);
  box-shadow:
    0 28px 80px rgba(143, 91, 42, 0.11),
    inset 0 1px 0 rgba(255, 255, 255, 0.72);
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 16px;
  border-radius: 999px;
  background: rgba(240, 225, 208, 0.86);
  border: 1px solid rgba(205, 162, 115, 0.24);
  color: #9d5b28;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.hero-avatar {
  width: 88px;
  height: 88px;
  margin: 28px 0 22px;
  filter: drop-shadow(0 18px 24px rgba(210, 132, 70, 0.16));
}

.hero-surface h1 {
  margin: 0;
  font-size: 46px;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: #31261d;
}

.hero-surface p {
  margin: 18px 0 0;
  max-width: 430px;
  font-size: 17px;
  line-height: 1.85;
  color: #6f6257;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.hero-points span {
  display: inline-flex;
  align-items: center;
  min-height: 40px;
  padding: 0 16px;
  border-radius: 999px;
  background: rgba(255, 250, 245, 0.92);
  border: 1px solid rgba(205, 162, 115, 0.18);
  color: #7b6552;
  font-size: 14px;
}

.register-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background: rgba(255, 252, 248, 0.74);
  border-left: 1px solid rgba(205, 162, 115, 0.14);
  backdrop-filter: blur(12px);
}

.panel-shell {
  width: min(100%, 360px);
}

.brand-block {
  margin-bottom: 32px;
}

.brand-wordmark {
  width: 172px;
  height: auto;
}

.brand-block p {
  margin: 16px 0 0;
  color: #76675a;
  font-size: 16px;
  line-height: 1.75;
}

.register-form {
  padding: 28px;
  border-radius: 28px;
  border: 1px solid rgba(205, 162, 115, 0.2);
  background: rgba(255, 252, 248, 0.9);
  box-shadow: 0 22px 46px rgba(146, 94, 48, 0.1);
}

.form-group + .form-group {
  margin-top: 16px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #45362a;
  font-size: 14px;
  font-weight: 600;
}

.register-input {
  :deep(.el-input__wrapper) {
    min-height: 54px;
    border-radius: 18px;
    background: #fffaf5;
    border: 1px solid rgba(210, 183, 154, 0.45);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
    transition:
      border-color 0.22s ease,
      box-shadow 0.22s ease,
      background-color 0.22s ease;
  }

  :deep(.el-input__wrapper:hover) {
    border-color: rgba(209, 127, 63, 0.42);
    background: #fffdf9;
  }

  :deep(.el-input__wrapper.is-focus) {
    border-color: rgba(205, 121, 55, 0.72);
    box-shadow:
      0 0 0 4px rgba(223, 168, 123, 0.16),
      inset 0 1px 0 rgba(255, 255, 255, 0.86);
    background: #fffdf9;
  }

  :deep(.el-input__inner) {
    font-size: 15px;
    color: #342920;
  }

  :deep(.el-input__inner::placeholder) {
    color: #b2a190;
  }
}

.form-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  margin: 18px 0 22px;
  font-size: 14px;
}

.login-text {
  color: #8d7a67;
}

.text-link {
  padding: 0;
  border: 0;
  background: transparent;
  color: #c96d31;
  font-weight: 600;
  cursor: pointer;
}

.text-link:hover {
  color: #ae5921;
}

.register-button {
  width: 100%;
  min-height: 54px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, #d78446 0%, #c96d31 100%);
  box-shadow: 0 14px 28px rgba(201, 109, 49, 0.22);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.register-button:hover {
  background: linear-gradient(135deg, #dd9054 0%, #cc7338 100%);
  box-shadow: 0 18px 32px rgba(201, 109, 49, 0.26);
}

.register-button :deep(.el-icon) {
  margin-left: 8px;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 18px;
  padding: 0 4px;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: rgba(245, 236, 225, 0.88);
  border: 1px solid rgba(205, 162, 115, 0.18);
  color: #9a6d41;
  font-size: 13px;
  font-weight: 600;
}

.footer-links {
  display: flex;
  gap: 14px;
}

.footer-links a {
  color: #8b7866;
  font-size: 14px;
  text-decoration: none;
}

.footer-links a:hover {
  color: #c96d31;
}

@media (max-width: 980px) {
  .register-page {
    grid-template-columns: 1fr;
  }

  .register-hero {
    padding: 28px 20px 12px;
  }

  .hero-surface {
    padding: 36px 28px;
  }

  .hero-surface h1 {
    font-size: 36px;
  }

  .register-panel {
    padding: 12px 20px 28px;
    border-left: 0;
  }

  .panel-shell {
    width: min(100%, 420px);
  }
}
</style>
