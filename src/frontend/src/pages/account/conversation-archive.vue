<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChatLineRound, Delete, RefreshRight } from '@element-plus/icons-vue'
import { deleteWorkspaceSessionAPI, getWorkspaceSessionsAPI } from '../../apis/workspace'
import { loadWorkspaceSessionModes, removeWorkspaceSessionMode, type WorkspaceMode } from '../../utils/workspace-defaults'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'

interface ArchiveSession {
  sessionId: string
  title: string
  createTime: string
  agent: string
  workspaceMode: WorkspaceMode
  messageCount: number
}

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const sessions = ref<ArchiveSession[]>([])
const LIST_PAGE_SIZE = 8
const listPage = ref(1)

const isRealAgentName = (value: unknown) => {
  const raw = String(value || '').trim()
  if (!raw) return false
  return !['default', '默认助手', '普通聊天', 'chat', 'normal'].includes(raw.toLowerCase())
}

const cleanupTitle = (value: unknown) => {
  const raw = String(value || '').trim()
  if (!raw || raw === '新的对话') return ''
  return raw.replace(/\s+/g, ' ').slice(0, 34)
}

const deriveTitle = (session: any) => {
  const contexts = Array.isArray(session?.contexts) ? session.contexts : []
  const firstQuery = contexts.map((context: any) => cleanupTitle(context?.query)).find(Boolean)
  return firstQuery || cleanupTitle(session.title || session.name) || '未命名对话'
}

const inferMode = (session: any): WorkspaceMode => {
  if (isRealAgentName(session.agent)) return 'agent'
  return String(session.workspace_mode || '').toLowerCase() === 'agent' ? 'agent' : 'normal'
}

const loadSessions = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await getWorkspaceSessionsAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '获取对话记录失败')
    }

    const modeOverrides = loadWorkspaceSessionModes()
    sessions.value = (response.data.data || [])
      .filter((session: any) => Array.isArray(session.contexts) && session.contexts.length > 0)
      .map((session: any) => {
        const sessionId = session.session_id || session.id
        const agent = isRealAgentName(session.agent) ? String(session.agent).trim() : ''
        const inferredMode = inferMode(session)
        const overrideMode = modeOverrides[sessionId]
        const workspaceMode = overrideMode === 'agent' && agent
          ? 'agent'
          : overrideMode === 'normal'
            ? 'normal'
            : inferredMode
        return {
          sessionId,
          title: deriveTitle(session),
          createTime: session.create_time || session.created_at || '',
          agent,
          workspaceMode,
          messageCount: Array.isArray(session.contexts) ? session.contexts.length : 0,
        }
      })
      .filter((session: ArchiveSession) => Boolean(session.sessionId))
      .sort((a: ArchiveSession, b: ArchiveSession) => new Date(b.createTime).getTime() - new Date(a.createTime).getTime())
  } catch (error: any) {
    console.error('获取对话记录失败:', error)
    errorMessage.value = '暂时连不上对话记录，后端启动后点右上角刷新即可。'
    sessions.value = []
  } finally {
    loading.value = false
  }
}

const groupedSessions = computed(() => ({
  chat: sessions.value.filter((session) => session.workspaceMode !== 'agent'),
  agent: sessions.value.filter((session) => session.workspaceMode === 'agent'),
}))

const sessionStats = computed(() => [
  { label: '全部', value: sessions.value.length },
  { label: 'Chat', value: groupedSessions.value.chat.length },
  { label: 'Agent', value: groupedSessions.value.agent.length },
])
const paginatedSessions = computed(() => sessions.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const formatTime = (value: string) => {
  if (!value) return '刚刚'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const openSession = (session: ArchiveSession) => {
  router.push({
    name: 'workspaceDefaultPage',
    query: {
      session_id: session.sessionId,
      mode: session.workspaceMode,
      execution_mode: 'tool',
      access_scope: 'workspace',
    },
  })
}

const removeSession = async (session: ArchiveSession, event: Event) => {
  event.stopPropagation()
  try {
    await deleteWorkspaceSessionAPI(session.sessionId)
    removeWorkspaceSessionMode(session.sessionId)
    sessions.value = sessions.value.filter((item) => item.sessionId !== session.sessionId)
    window.dispatchEvent(new CustomEvent('workspace-session-updated'))
  } catch (error) {
    console.error('删除对话失败:', error)
    errorMessage.value = '删除失败，稍后再试。'
  }
}

onMounted(loadSessions)
</script>

<template>
  <div class="conversation-archive-page">
    <header class="archive-header">
      <div class="archive-title">
        <el-icon><ChatLineRound /></el-icon>
        <h1>对话记录</h1>
      </div>
      <button class="archive-refresh" type="button" :disabled="loading" title="刷新" aria-label="刷新" @click="loadSessions">
        <el-icon><RefreshRight /></el-icon>
      </button>
    </header>

    <div class="archive-stats" aria-label="对话统计">
      <span v-for="item in sessionStats" :key="item.label">
        <strong>{{ item.value }}</strong>
        <small>{{ item.label }}</small>
      </span>
    </div>

    <p v-if="errorMessage" class="archive-state">{{ errorMessage }}</p>
    <p v-else-if="loading" class="archive-state">正在整理你的对话记录...</p>
    <p v-else-if="sessions.length === 0" class="archive-state">还没有留下对话，等第一句被保存后这里就会亮起来。</p>

    <div v-else class="archive-list">
      <button
        v-for="session in paginatedSessions"
        :key="session.sessionId"
        class="archive-row"
        type="button"
        @click="openSession(session)"
      >
        <span class="archive-row-main">
          <strong>{{ session.title }}</strong>
          <small>{{ session.workspaceMode === 'agent' ? (session.agent || 'Agent') : 'Chat' }}</small>
        </span>
        <span class="archive-row-meta">
          <small>{{ session.messageCount }} 条</small>
          <small>{{ formatTime(session.createTime) }}</small>
        </span>
        <button class="archive-delete" type="button" title="删除" aria-label="删除对话" @click="removeSession(session, $event)">
          <el-icon><Delete /></el-icon>
        </button>
      </button>
      <ZunoMiniPager v-model:page="listPage" class="archive-pager" :total="sessions.length" :page-size="LIST_PAGE_SIZE" />
    </div>
  </div>
</template>

<style scoped lang="scss">
.conversation-archive-page {
  display: grid;
  gap: 18px;
  min-width: 0;
  color: #0f172a;
}

.archive-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.archive-title {
  display: flex;
  align-items: center;
  gap: 10px;

  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 680;
    letter-spacing: 0;
  }

  .el-icon {
    color: #f59e0b;
    font-size: 28px;
  }
}

.archive-refresh,
.archive-delete {
  border: 0;
  background: transparent;
  color: #94a3b8;
  display: inline-grid;
  place-items: center;
  cursor: pointer;
}

.archive-refresh {
  width: 34px;
  height: 34px;
  font-size: 18px;

  &:hover {
    color: #b45309;
  }
}

.archive-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 22px;
  padding-bottom: 10px;

  span {
    display: inline-flex;
    align-items: baseline;
    gap: 6px;
  }

  strong {
    color: #0f172a;
    font-size: 22px;
    font-weight: 690;
  }

  small {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 620;
  }
}

.archive-state {
  margin: 8px 0 2px;
  color: #b6c0cf;
  text-align: center;
  line-height: 1.8;
}

.archive-list {
  display: grid;
  gap: 0;
}

.archive-row {
  position: relative;
  width: 100%;
  min-width: 0;
  border: 0;
  border-top: 1px solid rgba(226, 232, 240, 0.7);
  background: transparent;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 30px;
  align-items: center;
  gap: 14px;
  padding: 13px 0;
  color: inherit;
  text-align: left;
  cursor: pointer;
}

.archive-row:hover {
  .archive-row-main strong {
    color: #b45309;
  }
}

.archive-row-main,
.archive-row-meta {
  min-width: 0;
  display: grid;
  gap: 3px;
}

.archive-row-main strong {
  overflow: hidden;
  color: #0f172a;
  font-size: 15px;
  font-weight: 680;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.archive-row-main small,
.archive-row-meta small {
  color: #94a3b8;
  font-size: 12px;
}

.archive-row-meta {
  justify-items: end;
}

.archive-delete {
  width: 28px;
  height: 28px;
  font-size: 14px;
}

.archive-delete:hover {
  color: #dc2626;
}

@media (max-width: 720px) {
  .archive-row {
    grid-template-columns: minmax(0, 1fr) 28px;
  }

  .archive-row-meta {
    grid-column: 1 / -1;
    grid-row: 2;
    justify-items: start;
    grid-auto-flow: column;
    justify-content: start;
    gap: 10px;
  }
}
</style>
