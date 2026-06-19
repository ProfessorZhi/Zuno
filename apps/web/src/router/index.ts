import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import NotFound from '../pages/notFound/index'
import Index from '../pages/index.vue'
import Login from '../pages/login'
import { Register } from '../pages/login'
import Workspace from '../pages/workspace/workspace.vue'
import WorkspaceDefaultPage from '../pages/workspace/defaultPage/defaultPage.vue'
import { isDesktopRuntime } from '../utils/api'

const shouldUseHashHistory = () => {
  if (typeof window === 'undefined') return false
  if (!isDesktopRuntime()) return false
  return window.location.protocol === 'file:'
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { requiresAuth: false },
  },
  {
    path: '/workspace',
    name: 'workspace',
    component: Workspace,
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        name: 'workspaceDefaultPage',
        component: WorkspaceDefaultPage,
      },
      {
        path: 'settings',
        redirect: { name: 'workspaceSettingsAgent' },
      },
      {
        path: 'settings/agent',
        name: 'workspaceSettingsAgent',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'agent' },
      },
      {
        path: 'settings/agent/editor',
        name: 'workspaceSettingsAgentEditor',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'agent', settingsDetail: true },
      },
      {
        path: 'settings/model',
        name: 'workspaceSettingsModel',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'model' },
      },
      {
        path: 'settings/knowledge',
        name: 'workspaceSettingsKnowledge',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge' },
      },
      {
        path: 'settings/knowledge/create',
        name: 'workspaceSettingsKnowledgeCreate',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/knowledge/:knowledgeId/files',
        name: 'workspaceSettingsKnowledgeFile',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/knowledge/:knowledgeId/settings',
        name: 'workspaceSettingsKnowledgeSettings',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/knowledge/:knowledgeId/config',
        name: 'workspaceSettingsKnowledgeConfig',
        redirect: (to) => ({
          name: 'workspaceSettingsKnowledgeSettings',
          params: to.params,
          query: to.query,
        }),
      },
      {
        path: 'settings/knowledge/domain-packs',
        name: 'workspaceSettingsKnowledgeDomainPacks',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/knowledge/domain-packs/create',
        name: 'workspaceSettingsKnowledgeDomainPackCreate',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/knowledge/domain-packs/:packId',
        name: 'workspaceSettingsKnowledgeDomainPackDetail',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'knowledge', settingsDetail: true },
      },
      {
        path: 'settings/mcp',
        name: 'workspaceSettingsMcp',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'mcp' },
      },
      {
        path: 'settings/tool',
        name: 'workspaceSettingsTool',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'tool' },
      },
      {
        path: 'settings/skill',
        name: 'workspaceSettingsSkill',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'skill' },
      },
      {
        path: 'settings/dashboard',
        name: 'workspaceSettingsDashboard',
        component: WorkspaceDefaultPage,
        meta: { settingsSection: 'dashboard' },
      },
      {
        path: 'settings/profile',
        redirect: { name: 'workspaceAccountProfile' },
      },
      {
        path: 'account/profile',
        name: 'workspaceAccountProfile',
        component: WorkspaceDefaultPage,
        meta: { accountSection: 'profile' },
      },
      {
        path: 'account/conversations',
        name: 'workspaceAccountConversations',
        component: WorkspaceDefaultPage,
        meta: { accountSection: 'conversations' },
      },
    ],
  },
  {
    path: '/',
    redirect: {
      name: 'workspaceDefaultPage',
      query: {
        mode: 'normal',
        execution_mode: 'tool',
        access_scope: 'workspace',
      },
    },
    name: 'index',
    component: Index,
    meta: { requiresAuth: false },
    children: [
      {
        path: '/homepage',
        name: 'homepage',
        redirect: {
          name: 'workspaceDefaultPage',
          query: {
            mode: 'normal',
            execution_mode: 'tool',
            access_scope: 'workspace',
          },
        },
        meta: { current: 'homepage' },
      },
      {
        path: '/conversation',
        name: 'conversation',
        redirect: { name: 'workspaceAccountConversations' },
        meta: { current: 'conversation' },
      },
      {
        path: '/conversation/',
        name: 'defaultPage',
        redirect: { name: 'workspaceAccountConversations' },
        meta: { current: 'conversation' },
      },
      {
        path: '/conversation/chatPage',
        name: 'chatPage',
        redirect: (to) => ({ name: 'workspaceDefaultPage', query: to.query }),
        meta: { current: 'conversation' },
      },
      {
        path: '/construct',
        name: 'construct',
        meta: { current: 'construct' },
        redirect: { name: 'workspaceSettingsAgent' },
      },
      {
        path: '/configuration',
        name: 'configuration',
        meta: { current: 'configuration' },
        redirect: (to) => ({ name: 'workspaceSettingsTool', query: to.query }),
      },
      {
        path: '/agent',
        name: 'agent',
        meta: { current: 'agent' },
        redirect: { name: 'workspaceSettingsAgent' },
      },
      {
        path: '/agent/editor',
        name: 'agent-editor',
        meta: { current: 'agent' },
        redirect: (to) => ({ name: 'workspaceSettingsAgentEditor', query: to.query }),
      },
      {
        path: '/mcp-server',
        name: 'mcp-server',
        meta: { current: 'mcp-server' },
        redirect: { name: 'workspaceSettingsMcp' },
      },
      {
        path: '/knowledge',
        name: 'knowledge',
        meta: { current: 'knowledge' },
        redirect: { name: 'workspaceSettingsKnowledge' },
      },
      {
        path: '/knowledge/create',
        name: 'knowledge-create',
        meta: { current: 'knowledge' },
        redirect: { name: 'workspaceSettingsKnowledgeCreate' },
      },
      {
        path: '/knowledge/:knowledgeId/files',
        name: 'knowledge-file',
        meta: { current: 'knowledge' },
        redirect: (to) => ({
          name: 'workspaceSettingsKnowledgeFile',
          params: to.params,
          query: to.query,
        }),
      },
      {
        path: '/knowledge/:knowledgeId/settings',
        name: 'knowledge-settings',
        meta: { current: 'knowledge' },
        redirect: (to) => ({
          name: 'workspaceSettingsKnowledgeSettings',
          params: to.params,
          query: to.query,
        }),
      },
      {
        path: '/knowledge/:knowledgeId/config',
        name: 'knowledge-config',
        meta: { current: 'knowledge' },
        redirect: (to) => ({
          name: 'workspaceSettingsKnowledgeSettings',
          params: to.params,
          query: to.query,
        }),
      },
      {
        path: '/knowledge/domain-packs',
        name: 'knowledge-domain-packs',
        meta: { current: 'knowledge' },
        redirect: { name: 'workspaceSettingsKnowledgeDomainPacks' },
      },
      {
        path: '/tool',
        name: 'tool',
        meta: { current: 'tool' },
        redirect: { name: 'workspaceSettingsTool' },
      },
      {
        path: '/agent-skill',
        name: 'agent-skill',
        meta: { current: 'agent-skill' },
        redirect: { name: 'workspaceSettingsSkill' },
      },
      {
        path: '/model',
        name: 'model',
        meta: { current: 'model' },
        redirect: { name: 'workspaceSettingsModel' },
      },
      {
        path: '/model/editor',
        name: 'model-editor',
        meta: { current: 'model' },
        redirect: { name: 'workspaceSettingsModel' },
      },
      {
        path: '/profile',
        name: 'profile',
        meta: { current: 'profile' },
        redirect: { name: 'workspaceAccountProfile' },
      },
      {
        path: '/dashboard',
        name: 'dashboard',
        meta: { current: 'dashboard' },
        redirect: { name: 'workspaceSettingsDashboard' },
      },
    ],
  },
  {
    path: '/:catchAll(.*)',
    name: 'not-found',
    component: NotFound,
  },
]

const router = createRouter({
  history: shouldUseHashHistory() ? createWebHashHistory() : createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const isWorkspaceRoute = to.path === '/workspace' || to.path.startsWith('/workspace/')

  if (to.path === '/login' || to.path === '/register') {
    next({
      name: 'workspaceDefaultPage',
      query: {
        ...to.query,
        auth: to.path === '/register' ? 'register' : 'login',
      },
    })
    return
  }

  if (!token && !isWorkspaceRoute) {
    next({
      name: 'workspaceDefaultPage',
      query: {
        auth: 'login',
        redirect: to.fullPath,
      },
    })
    return
  }

  if (to.meta.requiresAuth) {
    if (token) {
      next()
    } else {
      next({
        name: 'workspaceDefaultPage',
        query: {
          auth: 'login',
          redirect: to.fullPath,
        },
      })
    }
    return
  }

  next()
})

export default router
