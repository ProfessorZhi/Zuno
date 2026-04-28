<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import { getUserInfoAPI, loginAPI } from '../../apis/auth'
import { useUserStore } from '../../store/user'
import { zunoAgentAvatar, zunoBrandMark } from '../../utils/brand'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: '',
})

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

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }

  try {
    loading.value = true
    const response = await loginAPI(loginForm)
    const responseData = response.data

    if (responseData.status_code === 200) {
      ElMessage.success('登录成功')

      const userData = responseData.data || {}
      if (userData.access_token && userData.user_id) {
        userStore.setUserInfo(userData.access_token, {
          id: userData.user_id,
          username: loginForm.username,
        })

        try {
          const userInfoResponse = await getUserInfoAPI(userData.user_id)
          const userInfoData = userInfoResponse.data
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
      }

      router.push('/')
      return
    }

    ElMessage.error(responseData.status_message || '登录失败')
  } catch (error: any) {
    console.error('登录错误:', error)
    const message = extractErrorMessage(error)
    if (message) {
      ElMessage.error(message)
    } else {
      ElMessage.error('登录失败，请确认后端服务已启动并检查账号密码')
    }
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-page">
    <section class="intro-panel">
      <div class="intro-shell">
        <div class="brand-mark">
          <img :src="zunoBrandMark" alt="Zuno" />
        </div>
        <span class="eyebrow">Zuno Workspace</span>
        <h1>安静推进复杂任务</h1>
        <p>登录后回到你的工作台，把对话、搜索、工具与执行放进同一处界面里。</p>
      </div>
    </section>

    <section class="form-panel">
      <div class="panel-shell">
        <div class="panel-brand">
          <img :src="zunoAgentAvatar" alt="Zuno" class="panel-logo" />
          <div>
            <h2>Zuno</h2>
            <p>登录后回到你的工作台。</p>
          </div>
        </div>

        <div class="login-form">
          <div class="form-group">
            <label class="form-label">账号</label>
            <el-input
              v-model="loginForm.username"
              placeholder="输入你的账号"
              size="large"
              class="login-input"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="输入你的密码"
              size="large"
              class="login-input"
              show-password
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="form-row">
            <span class="register-text">还没有账号？</span>
            <button type="button" class="text-link" @click="goToRegister">注册</button>
          </div>

          <el-button
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            <span>进入工作台</span>
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
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 420px);
  background:
    radial-gradient(circle at top left, rgba(224, 172, 115, 0.14), transparent 28%),
    linear-gradient(180deg, #f7f2ea 0%, #f4ede4 100%);
  color: #2f261f;
}

.intro-panel,
.form-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 36px;
}

.intro-shell {
  width: min(460px, 100%);
  padding: 34px 36px;
  border-radius: 28px;
  background: rgba(255, 251, 246, 0.72);
  border: 1px solid rgba(215, 183, 146, 0.24);
  box-shadow: 0 20px 48px rgba(120, 80, 42, 0.08);
}

.brand-mark {
  width: 74px;
  height: 74px;
  display: grid;
  place-items: center;
  border-radius: 22px;
  margin-bottom: 18px;
  background: rgba(255, 249, 241, 0.92);
  border: 1px solid rgba(212, 173, 131, 0.44);

  img {
    width: 48px;
    height: 48px;
  }
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  margin-bottom: 14px;
  border-radius: 999px;
  background: rgba(244, 230, 211, 0.86);
  color: #b46a35;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.intro-shell h1 {
  margin: 0;
  font-size: 44px;
  line-height: 1.04;
  letter-spacing: -0.05em;
  color: #2f241b;
}

.intro-shell p {
  margin: 16px 0 0;
  max-width: 360px;
  color: #6f6359;
  font-size: 17px;
  line-height: 1.8;
}

.form-panel {
  border-left: 1px solid rgba(213, 183, 148, 0.18);
  background: rgba(255, 252, 247, 0.7);
  backdrop-filter: blur(10px);
}

.panel-shell {
  width: min(100%, 360px);
}

.panel-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 22px;

  h2 {
    margin: 0;
    font-size: 28px;
    line-height: 1.1;
    color: #47372b;
  }

  p {
    margin: 8px 0 0;
    color: #77685a;
    font-size: 15px;
    line-height: 1.6;
  }
}

.panel-logo {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
}

.login-form {
  padding: 24px;
  border-radius: 24px;
  border: 1px solid rgba(210, 177, 140, 0.22);
  background: rgba(255, 252, 248, 0.92);
  box-shadow: 0 16px 34px rgba(136, 88, 47, 0.08);
}

.form-group + .form-group {
  margin-top: 18px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #433428;
  font-size: 14px;
  font-weight: 600;
}

.login-input {
  :deep(.el-input__wrapper) {
    min-height: 54px;
    border-radius: 18px;
    background: #fffaf5;
    border: 1px solid rgba(212, 185, 156, 0.4);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.84);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }

  :deep(.el-input__wrapper:hover) {
    border-color: rgba(202, 128, 67, 0.34);
  }

  :deep(.el-input__wrapper.is-focus) {
    border-color: rgba(196, 114, 49, 0.7);
    box-shadow:
      0 0 0 4px rgba(221, 176, 132, 0.14),
      inset 0 1px 0 rgba(255, 255, 255, 0.88);
    background: #fffdf9;
  }

  :deep(.el-input__inner) {
    color: #342920;
    font-size: 15px;
  }

  :deep(.el-input__inner::placeholder) {
    color: #b19e8b;
  }
}

.form-row {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
  margin: 16px 0 22px;
  font-size: 14px;
}

.register-text {
  color: #8d7965;
}

.text-link {
  border: 0;
  padding: 0;
  background: transparent;
  color: #c86f34;
  font-weight: 600;
  cursor: pointer;
}

.text-link:hover {
  color: #ab5924;
}

.login-button {
  width: 100%;
  min-height: 54px;
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, #da8749 0%, #c96d31 100%);
  box-shadow: 0 12px 22px rgba(201, 109, 49, 0.18);
  font-size: 16px;
  font-weight: 600;
}

.login-button:hover {
  background: linear-gradient(135deg, #df9154 0%, #cd763a 100%);
  box-shadow: 0 14px 24px rgba(201, 109, 49, 0.22);
}

.login-button :deep(.el-icon) {
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

  a {
    color: #8c7865;
    text-decoration: none;
    font-size: 14px;
  }

  a:hover {
    color: #c96d31;
  }
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .intro-panel {
    padding: 24px 20px 10px;
  }

  .form-panel {
    padding: 10px 20px 28px;
    border-left: 0;
  }

  .intro-shell {
    padding: 28px 24px;
  }

  .intro-shell h1 {
    font-size: 36px;
  }

  .intro-shell p {
    font-size: 16px;
  }

  .panel-shell {
    width: min(100%, 420px);
  }
}
</style>
