import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import ChatPage from '../pages/conversation/chatPage/chatPage.vue'
import NotFound from '../pages/notFound/index'
import Index from '../pages/index.vue'
import Conversation from '../pages/conversation/conversation.vue'
import DefaultPage from '../pages/conversation/defaultPage/defaultPage.vue'
import Construct from '../pages/construct'
import Configuration from '../pages/configuration'
import Login from '../pages/login'
import { Register } from '../pages/login'
import Agent from '../pages/agent'
import AgentEditor from '../pages/agent/agent-editor.vue'
import McpServer from '../pages/mcp-server'
import Knowledge from '../pages/knowledge'
import KnowledgeFile from '../pages/knowledge/knowledge-file.vue'
import KnowledgeConfig from '../pages/knowledge/knowledge-config.vue'
import Tool from '../pages/tool'
import AgentSkill from '../pages/agent-skill'
import Model from '../pages/model'
import ModelEditor from '../pages/model/model-editor.vue'
import Profile from '../pages/profile'
import Workspace from '../pages/workspace/workspace.vue'
import WorkspaceDefaultPage from '../pages/workspace/defaultPage/defaultPage.vue'
import Dashboard from '../pages/dashboard'
import { isDesktopRuntime } from '../utils/api'

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
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'workspaceDefaultPage',
        component: WorkspaceDefaultPage,
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
    meta: { requiresAuth: true },
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
        component: Conversation,
        meta: { current: 'conversation' },
        children: [
          {
            path: '/conversation/',
            name: 'defaultPage',
            component: DefaultPage,
          },
          {
            path: '/conversation/chatPage',
            name: 'chatPage',
            component: ChatPage,
          },
        ],
      },
      {
        path: '/construct',
        name: 'construct',
        meta: { current: 'construct' },
        component: Construct,
      },
      {
        path: '/configuration',
        name: 'configuration',
        meta: { current: 'configuration' },
        component: Configuration,
      },
      {
        path: '/agent',
        name: 'agent',
        meta: { current: 'agent' },
        component: Agent,
      },
      {
        path: '/agent/editor',
        name: 'agent-editor',
        meta: { current: 'agent' },
        component: AgentEditor,
      },
      {
        path: '/mcp-server',
        name: 'mcp-server',
        meta: { current: 'mcp-server' },
        component: McpServer,
      },
      {
        path: '/knowledge',
        name: 'knowledge',
        meta: { current: 'knowledge' },
        component: Knowledge,
      },
      {
        path: '/knowledge/:knowledgeId/files',
        name: 'knowledge-file',
        meta: { current: 'knowledge' },
        component: KnowledgeFile,
      },
      {
        path: '/knowledge/:knowledgeId/config',
        name: 'knowledge-config',
        meta: { current: 'knowledge' },
        component: KnowledgeConfig,
      },
      {
        path: '/tool',
        name: 'tool',
        meta: { current: 'tool' },
        component: Tool,
      },
      {
        path: '/agent-skill',
        name: 'agent-skill',
        meta: { current: 'agent-skill' },
        component: AgentSkill,
      },
      {
        path: '/model',
        name: 'model',
        meta: { current: 'model' },
        component: Model,
      },
      {
        path: '/model/editor',
        name: 'model-editor',
        meta: { current: 'model' },
        component: ModelEditor,
      },
      {
        path: '/profile',
        name: 'profile',
        meta: { current: 'profile' },
        component: Profile,
      },
      {
        path: '/dashboard',
        name: 'dashboard',
        meta: { current: 'dashboard' },
        component: Dashboard,
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
  history: isDesktopRuntime() ? createWebHashHistory() : createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth) {
    if (token) {
      next()
    } else {
      next('/login')
    }
    return
  }

  if (to.path === '/login' && token) {
    next('/')
    return
  }

  next()
})

export default router
