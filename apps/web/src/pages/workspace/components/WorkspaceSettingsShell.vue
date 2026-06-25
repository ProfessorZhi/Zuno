<script setup lang="ts">
import { computed, markRaw, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Close } from '@element-plus/icons-vue'
import { getSettingsIcon } from '../../../utils/settings-icons'
import { loadSettingsUiMode } from '../../../utils/settings-preferences'
import accountConversationIcon from '../../../assets/account/conversation.svg'
import accountProfileIcon from '../../../assets/account/profile.svg'
import Agent from '../../agent'
import AgentEditor from '../../agent/agent-editor.vue'
import AgentSkillPage from '../../agent-skill'
import Dashboard from '../../dashboard'
import Knowledge from '../../knowledge'
import KnowledgeCreate from '../../knowledge/knowledge-create.vue'
import KnowledgeFile from '../../knowledge/knowledge-file.vue'
import KnowledgeSettings from '../../knowledge/knowledge-settings.vue'
import McpServer from '../../mcp-server'
import Model from '../../model'
import Profile from '../../profile'
import Tool from '../../tool'
import { ConversationArchive } from '../../account'
import SettingsUiModeSwitch from './SettingsUiModeSwitch.vue'

type NavItem = {
  key: string
  label: string
  routeName: string
  icon: string
}

const router = useRouter()
const route = useRoute()
const emit = defineEmits<{
  close: []
}>()

const settingsComponentByRouteName: Record<string, Component> = {
  workspaceSettingsAgent: markRaw(Agent),
  workspaceSettingsAgentEditor: markRaw(AgentEditor),
  workspaceSettingsModel: markRaw(Model),
  workspaceSettingsKnowledge: markRaw(Knowledge),
  workspaceSettingsKnowledgeCreate: markRaw(KnowledgeCreate),
  workspaceSettingsKnowledgeFile: markRaw(KnowledgeFile),
  workspaceSettingsKnowledgeSettings: markRaw(KnowledgeSettings),
  workspaceSettingsKnowledgeConfig: markRaw(KnowledgeSettings),
  workspaceSettingsMcp: markRaw(McpServer),
  workspaceSettingsTool: markRaw(Tool),
  workspaceSettingsSkill: markRaw(AgentSkillPage),
  workspaceSettingsDashboard: markRaw(Dashboard),
  workspaceAccountProfile: markRaw(Profile),
  workspaceAccountConversations: markRaw(ConversationArchive),
}

const settingsNavItems: NavItem[] = [
  { key: 'agent', label: '智能体', routeName: 'workspaceSettingsAgent', icon: getSettingsIcon('agent') },
  { key: 'model', label: '模型', routeName: 'workspaceSettingsModel', icon: getSettingsIcon('model') },
  { key: 'knowledge', label: '知识库', routeName: 'workspaceSettingsKnowledge', icon: getSettingsIcon('knowledge') },
  { key: 'mcp', label: 'MCP', routeName: 'workspaceSettingsMcp', icon: getSettingsIcon('mcp') },
  { key: 'tool', label: '工具', routeName: 'workspaceSettingsTool', icon: getSettingsIcon('tool') },
  { key: 'skill', label: 'Skill', routeName: 'workspaceSettingsSkill', icon: getSettingsIcon('skill') },
  { key: 'dashboard', label: '数据看板', routeName: 'workspaceSettingsDashboard', icon: getSettingsIcon('dashboard') },
]

const accountNavItems: NavItem[] = [
  { key: 'profile', label: '个人资料', routeName: 'workspaceAccountProfile', icon: accountProfileIcon },
  { key: 'conversations', label: '对话记录', routeName: 'workspaceAccountConversations', icon: accountConversationIcon },
]

const settingsUiMode = computed(() => loadSettingsUiMode())
const activeKey = computed(() => String(route.meta.settingsSection || route.meta.accountSection || 'agent'))
const activeComponent = computed(() => settingsComponentByRouteName[String(route.name || '')] || null)
const activeItem = computed(() => (
  [...settingsNavItems, ...accountNavItems].find((item) => item.key === activeKey.value) || settingsNavItems[0]
))
const isDetailView = computed(() => Boolean(route.meta.settingsDetail))
const canBackToSection = computed(() => isDetailView.value && Boolean(route.meta.settingsSection))

const buildSettingsQuery = () => {
  const { settings_turn: _settingsTurn, ...restQuery } = route.query
  return {
    ...restQuery,
    settings_turn: String(Date.now()),
  }
}

const openNavItem = async (item: NavItem) => {
  if (String(route.name || '') === item.routeName && !route.meta.settingsDetail) return
  await router.push({
    name: item.routeName,
    query: buildSettingsQuery(),
  })
}

const openSectionRoot = async () => {
  const item = settingsNavItems.find((entry) => entry.key === activeKey.value) || settingsNavItems[0]
  await openNavItem(item)
}

const backToWorkspace = async () => {
  const { settings_turn: _settingsTurn, ...restQuery } = route.query
  await router.push({
    name: 'workspaceDefaultPage',
    query: restQuery,
  })
  emit('close')
}
</script>

<template>
  <div class="settings-shell-page">
    <aside class="settings-shell-sidebar">
      <div class="settings-shell-sidebar-top">
        <button type="button" class="settings-shell-back" @click="backToWorkspace">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回应用</span>
        </button>
      </div>

      <section class="settings-shell-group">
        <button
          v-for="item in settingsNavItems"
          :key="item.key"
          type="button"
          class="settings-shell-nav"
          :class="{ active: item.key === activeKey }"
          @click="openNavItem(item)"
        >
          <img :src="item.icon" alt="" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </button>
      </section>

      <section class="settings-shell-group settings-shell-group-account">
        <button
          v-for="item in accountNavItems"
          :key="item.key"
          type="button"
          class="settings-shell-nav"
          :class="{ active: item.key === activeKey }"
          @click="openNavItem(item)"
        >
          <img :src="item.icon" alt="" aria-hidden="true" />
          <span>{{ item.label }}</span>
        </button>
      </section>

      <div class="settings-shell-sidebar-footer">
        <SettingsUiModeSwitch :mode="settingsUiMode" compact />
      </div>
    </aside>

    <main class="settings-shell-main">
      <header class="settings-shell-header">
        <div class="settings-shell-title-row">
          <button
            v-if="canBackToSection"
            type="button"
            class="settings-shell-detail-back"
            @click="openSectionRoot"
          >
            <el-icon><ArrowLeft /></el-icon>
          </button>
          <h1>{{ activeItem.label }}</h1>
        </div>
        <button type="button" class="settings-shell-close" aria-label="关闭设置窗口" @click="backToWorkspace">
          <el-icon><Close /></el-icon>
        </button>
      </header>

      <section class="settings-shell-content">
        <component :is="activeComponent" v-if="activeComponent" :key="route.fullPath" />
      </section>
    </main>
  </div>
</template>

<style scoped>
.settings-shell-page {
  display: grid;
  grid-template-columns: 284px minmax(0, 1fr);
  height: 100%;
  min-width: 0;
  min-height: 0;
  gap: 0;
  padding: 0;
  background: #ffffff;
  border: 1px solid #d8e0e8;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(22, 30, 39, 0.18);
}

.settings-shell-sidebar {
  display: grid;
  grid-template-rows: auto 1fr auto;
  min-height: 0;
  min-width: 0;
  gap: 18px;
  padding: 14px 10px 14px 12px;
  border-right: 1px solid #d9e0e7;
  background: #edf4fb;
}

.settings-shell-sidebar-top {
  padding: 2px 0 0;
}

.settings-shell-back,
.settings-shell-nav,
.settings-shell-detail-back {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  border: none;
  background: none;
  cursor: pointer;
}

.settings-shell-back {
  justify-content: flex-start;
  width: 100%;
  min-height: 38px;
  padding: 0 10px;
  border-radius: 10px;
  color: #4d5966;
  transition: background 0.2s ease, color 0.2s ease;
}

.settings-shell-back:hover {
  background: rgba(173, 187, 201, 0.24);
  color: #1f2d3d;
}

.settings-shell-group {
  display: grid;
  align-content: start;
  gap: 4px;
}

.settings-shell-nav {
  width: 100%;
  min-height: 42px;
  padding: 0 12px;
  border-radius: 12px;
  color: #213243;
  transition: background 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
}

.settings-shell-nav img {
  width: 18px;
  height: 18px;
  opacity: 0.9;
}

.settings-shell-nav.active {
  background: rgba(176, 187, 199, 0.42);
  color: #0f1d2b;
  box-shadow: none;
}

.settings-shell-nav:hover {
  background: rgba(176, 187, 199, 0.22);
}

.settings-shell-group-account {
  align-self: end;
}

.settings-shell-sidebar-footer {
  padding-top: 8px;
}

.settings-shell-main {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-width: 0;
  min-height: 0;
  background: #ffffff;
}

.settings-shell-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 0 28px;
  border-bottom: 1px solid #dde3ea;
  background: #ffffff;
}

.settings-shell-title-row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.settings-shell-title-row h1 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.2;
  color: #1c2733;
}

.settings-shell-detail-back {
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  color: #4d5966;
  background: rgba(239, 243, 247, 0.96);
}

.settings-shell-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 9px;
  background: rgba(239, 243, 247, 0.96);
  color: #4d5966;
  cursor: pointer;
}

.settings-shell-content {
  min-width: 0;
  min-height: 0;
  padding: 20px 28px 28px;
  overflow: auto;
  background: #ffffff;
}

@media (max-width: 1199px) {
  .settings-shell-page {
    grid-template-columns: 214px minmax(0, 1fr);
  }

  .settings-shell-sidebar {
    gap: 14px;
    padding: 12px 8px 12px 10px;
  }

  .settings-shell-nav {
    min-height: 40px;
    padding: 0 10px;
  }

  .settings-shell-header {
    min-height: 64px;
    padding: 0 20px;
  }

  .settings-shell-content {
    padding: 16px 20px 20px;
  }
}

@media (max-width: 767px) {
  .settings-shell-page {
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(0, 1fr);
    height: 100%;
    border-radius: 0;
    border: none;
    box-shadow: none;
  }

  .settings-shell-sidebar {
    grid-template-rows: auto auto auto auto;
    gap: 8px;
    min-height: auto;
    padding: 10px 12px 8px;
    border-right: none;
    border-bottom: 1px solid #d9e0e7;
    background: rgba(237, 244, 251, 0.92);
  }

  .settings-shell-back {
    min-height: 36px;
    padding: 0 8px;
  }

  .settings-shell-group,
  .settings-shell-group-account {
    display: flex;
    align-items: center;
    gap: 8px;
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 2px;
    scrollbar-width: none;
  }

  .settings-shell-group-account {
    display: none;
  }

  .settings-shell-group::-webkit-scrollbar,
  .settings-shell-group-account::-webkit-scrollbar {
    display: none;
  }

  .settings-shell-nav {
    width: auto;
    min-width: max-content;
    min-height: 34px;
    padding: 0 12px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.72);
    flex: 0 0 auto;
  }

  .settings-shell-nav.active {
    background: rgba(176, 187, 199, 0.42);
  }

  .settings-shell-sidebar-footer {
    display: none;
  }

  .settings-shell-main {
    min-height: 0;
  }

  .settings-shell-header {
    min-height: 56px;
    padding: 0 14px;
  }

  .settings-shell-content {
    padding: 12px;
  }
}
</style>
