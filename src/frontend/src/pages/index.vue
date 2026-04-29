<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  House,
  User,
  SwitchButton,
  ChatDotRound,
  Cpu,
  Connection,
  FolderOpened,
  Grid,
  CollectionTag,
  Box,
  DataAnalysis,
} from '@element-plus/icons-vue'
import { useAgentCardStore } from '../store/agent_card'
import { useUserStore } from '../store/user'
import { logoutAPI, getUserInfoAPI } from '../apis/auth'
import { useResizablePanel } from '../composables/useResizablePanel'
import { zunoBrandMark } from '../utils/brand'

const agentCardStore = useAgentCardStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

const itemName = ref('Zuno')
const current = ref((route.meta.current as string) || 'homepage')
const isEmbedded = computed(() => route.query.embed === '1')
const {
  panelStyle: navPanelStyle,
  startResize: startNavResize,
  handleSeparatorKeydown: handleNavSeparatorKeydown,
} = useResizablePanel({
  storageKey: 'zuno.layout.navWidth',
  cssVariable: '--zuno-sidebar-width',
  defaultWidth: 180,
  minWidth: 88,
  maxWidth: 260,
})

const navMenuItems = [
  { index: 'homepage', label: '首页', icon: House, target: 'homepage' },
  { index: 'conversation', label: '历史', icon: ChatDotRound, target: 'conversation' },
  { index: 'agent', label: '智能体', icon: Cpu, target: 'agent' },
  { index: 'mcp-server', label: 'MCP', icon: Connection, target: 'mcp-server' },
  { index: 'knowledge', label: '知识库', icon: FolderOpened, target: 'knowledge' },
  { index: 'tool', label: '工具', icon: Grid, target: 'tool' },
  { index: 'agent-skill', label: 'Skill', icon: CollectionTag, target: 'agent-skill' },
  { index: 'model', label: '模型', icon: Box, target: 'model' },
  { index: 'dashboard', label: '数据看板', icon: DataAnalysis, target: 'dashboard' },
]

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
      console.error('初始化时获取用户信息失败:', error)
    }
  }
})

const goDefault = () => {
  agentCardStore.clear()
  router.push('/homepage')
}

const goCurrent = (item: string) => {
  const routes: Record<string, string> = {
    homepage: '/homepage',
    conversation: '/conversation',
    agent: '/agent',
    'mcp-server': '/mcp-server',
    knowledge: '/knowledge',
    tool: '/tool',
    'agent-skill': '/agent-skill',
    model: '/model',
    dashboard: '/dashboard',
  }

  router.push(routes[item] || '/homepage')
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
  if (target) {
    target.src = '/src/assets/user.svg'
  }
}

watch(
  route,
  () => {
    current.value = (route.meta.current as string) || 'homepage'
  },
  { immediate: true }
)
</script>

<template>
  <div class="ai-body" :class="{ embedded: isEmbedded }" :style="navPanelStyle">
    <div v-if="!isEmbedded" class="ai-nav">
      <div class="left">
        <div class="brand-home" @click="goDefault">
          <img :src="zunoBrandMark" :alt="itemName" class="brand-logo-img" />
        </div>
      </div>
      <div class="right">
        <div class="user-info">
          <el-dropdown @command="handleUserCommand" trigger="click">
            <div class="user-avatar-wrapper">
              <div class="user-avatar">
                <img
                  :src="userStore.userInfo?.avatar || '/src/assets/user.svg'"
                  alt="用户头像"
                  style="width: 40px; height: 40px; border-radius: 50%"
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
      </div>
    </div>

    <div class="ai-main">
      <el-col v-if="!isEmbedded" :span="2">
        <div class="sidebar-content">
          <el-menu
            active-text-color="#63584d"
            background-color="#efe9de"
            class="el-menu-vertical-demo"
            :default-active="current"
            text-color="#746d63"
          >
            <el-menu-item
              v-for="item in navMenuItems"
              :key="item.index"
              :index="item.index"
              @click="goCurrent(item.target)"
            >
              <template #title>
                <span class="nav-icon-shell">
                  <el-icon class="nav-icon">
                    <component :is="item.icon" />
                  </el-icon>
                </span>
                <span>{{ item.label }}</span>
              </template>
            </el-menu-item>
          </el-menu>

          <div class="sidebar-footer">
            <div class="help-links">
              <a
                href="https://github.com/ProfessorZhi/Zuno"
                target="_blank"
                class="help-link"
                title="GitHub 仓库"
              >
                <img src="../assets/github.png" alt="GitHub" class="help-icon" />
              </a>
              <a
                href="https://github.com/ProfessorZhi/Zuno/tree/main/docs"
                target="_blank"
                class="help-link"
                title="帮助文档"
              >
                <img src="../assets/help.png" alt="帮助文档" class="help-icon" />
              </a>
            </div>
          </div>
        </div>
        <div
          class="resize-handle nav-resize-handle"
          role="separator"
          aria-label="调整主导航宽度"
          aria-orientation="vertical"
          tabindex="0"
          @pointerdown="startNavResize"
          @keydown="handleNavSeparatorKeydown"
        />
      </el-col>

      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ai-body {
  @import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=Zhi+Mang+Xing&family=Ma+Shan+Zheng&display=swap');
}

.ai-body {
  --zuno-header-height: 88px;
  --zuno-brand-logo-height: 54px;
  --zuno-sidebar-width: 180px;
  overflow: hidden;

  .ai-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: var(--zuno-header-height);
    background: linear-gradient(180deg, #f7f2e9 0%, #efe7db 100%);
    padding: 0 24px;
    box-shadow: 0 1px 0 rgba(15, 23, 42, 0.06);
    position: relative;
    z-index: 3000;
    box-sizing: border-box;

    .left {
      display: flex;
      align-items: center;
      font-weight: 600;
      color: #0f172a;
      cursor: pointer;
      transition: opacity 0.24s ease;

      &:hover {
        opacity: 0.88;
      }

      .brand-home {
        display: flex;
        align-items: center;
        padding: 8px 16px;
        border-radius: 18px;
        background: rgba(255, 251, 245, 0.92);
        border: 1px solid rgba(212, 176, 137, 0.42);
        box-shadow:
          0 2px 10px rgba(118, 86, 50, 0.08),
          inset 0 1px 0 rgba(255, 255, 255, 0.92);
      }

      .brand-logo-img {
        height: var(--zuno-brand-logo-height);
        max-width: min(220px, 100%);
        width: auto;
        display: block;
        filter: drop-shadow(0 4px 12px rgba(118, 86, 50, 0.12));
        user-select: none;
      }
    }

    .right {
      display: flex;
      align-items: center;

      .user-info {
        .user-avatar-wrapper {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 50px;
          height: 50px;
          padding: 4px;
          border-radius: 50%;
          background: rgba(255, 251, 245, 0.94);
          border: 1px solid rgba(212, 176, 137, 0.38);
          box-shadow:
            0 2px 10px rgba(118, 86, 50, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
          cursor: pointer;
          transition: all 0.24s ease;

          &:hover {
            background: rgba(255, 249, 242, 1);
            border-color: rgba(201, 108, 45, 0.24);
            transform: translateY(-1px);
            box-shadow:
              0 6px 18px rgba(118, 86, 50, 0.12),
              inset 0 1px 0 rgba(255, 255, 255, 0.92);
          }

          .user-avatar {
            img {
              display: block;
              background: #f3e8da;
              border: 2px solid rgba(255, 255, 255, 0.58);
              object-fit: cover;
              box-shadow: 0 2px 8px rgba(118, 86, 50, 0.1);
              transition: all 0.24s ease;

              &:hover {
                border-color: rgba(255, 255, 255, 0.88);
                transform: scale(1.02);
              }
            }
          }
        }
      }
    }
  }

  .ai-main {
    display: flex;
    height: calc(100vh - var(--zuno-header-height));
    background-color: var(--zuno-bg-canvas);
    min-height: 0;
    overflow-x: auto;
    overflow-y: hidden;

    :deep(.el-col-2) {
      display: flex;
      width: var(--zuno-sidebar-width);
      min-width: var(--zuno-sidebar-width);
      position: relative;
      flex: 0 0 var(--zuno-sidebar-width);
      max-width: var(--zuno-sidebar-width);
    }

    .sidebar-content {
      display: flex;
      flex-direction: column;
      height: 100%;
      width: 100%;
      background: linear-gradient(180deg, #f1ebe1 0%, #e8dfd1 100%);
      border-right: 1px solid var(--zuno-border-soft);
      padding: 3px 0;
      box-sizing: border-box;
      box-shadow: 2px 0 12px rgba(0, 0, 0, 0.08);
    }

    .sidebar-footer {
      margin-top: auto;
      padding: 0 24px 24px;
      display: none;
      justify-content: center;
      align-items: center;

      .help-links {
        display: flex;
        gap: 16px;

        .help-link {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 48px;
          height: 48px;
          border: 1px solid rgba(214, 132, 70, 0.18);
          border-radius: 16px;
          padding: 10px;
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(20px);

          &:hover {
            background: rgba(255, 247, 239, 0.96);
            border-color: rgba(214, 132, 70, 0.32);
            transform: translateY(-3px) scale(1.1);
            box-shadow: 0 12px 24px rgba(194, 110, 46, 0.16);
          }

          .help-icon {
            width: 26px;
            height: 26px;
            transition: all 0.4s ease;
            filter: saturate(0.8);
          }

          &:hover .help-icon {
            filter: saturate(1.3) hue-rotate(10deg);
            transform: scale(1.1);
          }
        }
      }
    }

    .content {
      flex: 1 0 520px;
      min-width: 520px;
      min-height: 0;
      overflow: auto;
      background-color: var(--zuno-bg-content);
      border-radius: 20px 0 0 0;
      margin-left: 4px;
      padding: 18px 20px 22px;
      box-sizing: border-box;
      box-shadow: -4px 0 16px rgba(0, 0, 0, 0.05);
    }
  }
}

.ai-body.embedded {
  height: 100vh;
  overflow: hidden;

  .ai-main {
    height: 100vh;
    overflow: hidden;

    .content {
      flex: 1 1 auto;
      min-width: 0;
      border-radius: 0;
      margin-left: 0;
      padding: 0;
      box-shadow: none;
      overflow: auto;
    }
  }
}

.resize-handle {
  position: absolute;
  top: 0;
  right: -5px;
  z-index: 20;
  width: 10px;
  height: 100%;
  cursor: col-resize;
  touch-action: none;

  &::after {
    content: "";
    position: absolute;
    top: 14px;
    bottom: 14px;
    left: 4px;
    width: 2px;
    border-radius: 999px;
    background: transparent;
    transition: background 0.18s ease, box-shadow 0.18s ease;
  }

  &:hover::after,
  &:focus-visible::after {
    background: rgba(201, 108, 45, 0.42);
    box-shadow: 0 0 0 3px rgba(201, 108, 45, 0.1);
  }

  &:focus-visible {
    outline: none;
  }
}

:global(body.zuno-is-resizing) {
  cursor: col-resize;
  user-select: none;
}

:deep(.el-dropdown-menu) {
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border-radius: 8px;
  overflow: hidden;

  .el-dropdown-menu__item {
    padding: 12px 16px;
    font-size: 14px;

    &:hover {
      background-color: #f5f7fa;
      color: #c96c2d;
    }

    .el-icon {
      margin-right: 8px;
    }
  }
}

:deep(.el-menu-vertical-demo) {
  border-right: none;
  background: transparent;
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;

  .el-menu-item {
    border-radius: 22px;
    margin: 8px 14px;
    padding: 0 18px;
    height: 60px;
    line-height: 60px;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.2px;
    transition: all 0.28s ease;
    position: relative;
    overflow: hidden;
    color: #6d645b;

    &:hover {
      background: rgba(255, 252, 247, 0.92);
      color: #c96c2d;
      transform: translateX(2px);

      .nav-icon-shell {
        background: rgba(223, 150, 88, 0.14);
        border-color: rgba(214, 132, 70, 0.22);
      }

      .nav-icon {
        color: #cc6b2c;
      }
    }

    &.is-active {
      background: rgba(255, 251, 245, 0.96);
      color: #c96c2d;
      box-shadow: 0 10px 24px rgba(194, 110, 46, 0.1);
      border: 1px solid rgba(222, 164, 116, 0.22);

      .nav-icon-shell {
        background: rgba(223, 150, 88, 0.18);
        border-color: rgba(214, 132, 70, 0.28);
      }

      .nav-icon {
        color: #c96c2d;
      }

      span {
        font-weight: 600;
        color: #c96c2d !important;
      }
    }

    .nav-icon-shell {
      width: 32px;
      height: 32px;
      margin-right: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      background: transparent;
      border: 1px solid transparent;
      transition: all 0.28s ease;
      flex-shrink: 0;
    }

    .nav-icon {
      width: 18px;
      height: 18px;
      color: #d68446;

      svg {
        width: 18px;
        height: 18px;
      }
    }

    span {
      position: relative;
      z-index: 1;
      transition: all 0.4s ease;
      font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
    }
  }
}

@media (max-width: 960px) {
  .ai-body {
    --zuno-header-height: 76px;
    --zuno-brand-logo-height: 44px;
  }
}
</style>
