<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus } from '@element-plus/icons-vue'
import AgentEditor from './agent-editor.vue'
import { deleteAgentAPI, getAgentsAPI, searchAgentsAPI, type AgentResponse } from '../../apis/agent'
import { useUserStore } from '../../store/user'
import { zunoAgentAvatar } from '../../utils/brand'
import { getSettingsIcon } from '../../utils/settings-icons'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'
import ZunoEmptyState from '../../components/zuno-settings/ZunoEmptyState.vue'
import ZunoIconButton from '../../components/zuno-settings/ZunoIconButton.vue'
import ZunoSearchInput from '../../components/zuno-settings/ZunoSearchInput.vue'

interface AgentCardItem {
  agent_id: string
  name: string
  description: string
  logo_url: string
  tool_ids: string[]
  llm_id: string
  mcp_ids: string[]
  system_prompt: string
  knowledge_ids: string[]
  agent_skill_ids: string[]
  enable_memory: boolean
  created_time?: string
  is_custom?: boolean
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const searchLoading = ref(false)
const searchKeyword = ref('')
const agents = ref<AgentCardItem[]>([])
const editorVisible = ref(false)
const editingAgentId = ref<string | undefined>()
const LIST_PAGE_SIZE = 6
const listPage = ref(1)

const normalizeAgent = (item: AgentResponse): AgentCardItem => ({
  agent_id: item.agent_id || item.id || '',
  name: item.name || '未命名智能体',
  description: item.description || '暂无描述',
  logo_url: item.logo_url || zunoAgentAvatar,
  tool_ids: item.tool_ids || [],
  llm_id: item.llm_id || '',
  mcp_ids: item.mcp_ids || [],
  system_prompt: item.system_prompt || '',
  knowledge_ids: item.knowledge_ids || [],
  agent_skill_ids: item.agent_skill_ids || [],
  enable_memory: Boolean(item.enable_memory),
  created_time: item.create_time || item.created_time,
  is_custom: item.is_custom,
})

const sortedAgents = computed(() =>
  [...agents.value].sort((left, right) => {
    const leftOfficial = left.is_custom === false
    const rightOfficial = right.is_custom === false
    if (leftOfficial !== rightOfficial) return leftOfficial ? -1 : 1
    return (right.created_time || '').localeCompare(left.created_time || '')
  }),
)
const paginatedAgents = computed(() => sortedAgents.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')
const isWorkspaceSettings = computed(() => String(route.name || '').startsWith('workspaceSettings'))
const toolIcon = getSettingsIcon('tool')
const mcpIcon = getSettingsIcon('mcp')
const knowledgeIcon = getSettingsIcon('knowledge')

const getSettingsThreadId = (event?: Event) => {
  const target = event?.currentTarget as HTMLElement | null
  return target?.closest<HTMLElement>('.settings-bubble')?.dataset.settingsThreadId || ''
}

const navigateInWorkspaceSettings = (location: any, event?: Event) => {
  if (!isWorkspaceSettings.value) return false
  window.dispatchEvent(new CustomEvent('workspace-settings-navigate', {
    detail: {
      location,
      threadId: getSettingsThreadId(event),
    },
  }))
  return true
}

const fetchAgents = async () => {
  loading.value = true
  try {
    const response = await getAgentsAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '获取智能体列表失败')
    }
    agents.value = (response.data.data || []).map(normalizeAgent)
  } catch (error: any) {
    console.error('fetchAgents failed', error)
    ElMessage.error(error.message || '获取智能体列表失败')
    agents.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    await fetchAgents()
    return
  }

  searchLoading.value = true
  try {
    const response = await searchAgentsAPI({ name: keyword })
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '搜索智能体失败')
    }
    agents.value = (response.data.data || []).map(normalizeAgent)
  } catch (error: any) {
    console.error('searchAgents failed', error)
    ElMessage.error(error.message || '搜索智能体失败')
  } finally {
    searchLoading.value = false
  }
}

const clearSearch = async () => {
  searchKeyword.value = ''
  await fetchAgents()
}

const goCreate = (event?: Event) => {
  if (isWorkspaceSettings.value) {
    if (editorVisible.value && !editingAgentId.value) {
      editorVisible.value = false
      return
    }
    editingAgentId.value = undefined
    editorVisible.value = true
    return
  }
  const location = { name: 'workspaceSettingsAgentEditor' }
  if (navigateInWorkspaceSettings(location, event)) {
    return
  }
  router.push('/agent/editor')
}

const goEdit = (agent: AgentCardItem, event?: Event) => {
  if (agent.is_custom === false && !isAdmin.value) {
    ElMessage.warning('只有管理员可以编辑官方智能体')
    return
  }
  if (isWorkspaceSettings.value) {
    editingAgentId.value = agent.agent_id
    editorVisible.value = true
    return
  }
  const location = { name: 'workspaceSettingsAgentEditor', query: { id: agent.agent_id } }
  if (navigateInWorkspaceSettings(location, event)) {
    return
  }
  router.push({ path: '/agent/editor', query: { id: agent.agent_id } })
}

const closeEditor = () => {
  editorVisible.value = false
  editingAgentId.value = undefined
}

const handleEditorSaved = async () => {
  await fetchAgents()
}

const handleDelete = async (agent: AgentCardItem) => {
  if (agent.is_custom === false && !isAdmin.value) {
    ElMessage.warning('只有管理员可以删除官方智能体')
    return
  }

  try {
    await ElMessageBox.confirm(`确认删除智能体“${agent.name}”吗？`, '删除智能体', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })

    const response = await deleteAgentAPI({ agent_id: agent.agent_id })
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '删除智能体失败')
    }

    ElMessage.success('智能体已删除')
    await fetchAgents()
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return
    console.error('deleteAgent failed', error)
    ElMessage.error(error.message || '删除智能体失败')
  }
}

const handleImageError = (event: Event) => {
  const target = event.target as HTMLImageElement | null
  if (target) target.src = zunoAgentAvatar
}

onMounted(fetchAgents)
</script>

<template>
  <div class="agent-page">
    <section class="agent-hero">
      <div>
        <h2>智能体</h2>
      </div>
      <div class="hero-actions">
        <ZunoIconButton
          type="primary"
          :icon="Plus"
          :active="editorVisible && !editingAgentId"
          :title="editorVisible && !editingAgentId ? '收起创建智能体' : '创建智能体'"
          @click="goCreate($event)"
        />
      </div>
      <div class="settings-search-row">
        <ZunoSearchInput
          v-model="searchKeyword"
          placeholder="搜索智能体名称"
          @clear="clearSearch"
          @enter="handleSearch"
        />
      </div>
    </section>

    <Transition name="settings-panel">
      <AgentEditor
        v-if="editorVisible"
        embedded
        :embedded-agent-id="editingAgentId"
        class="agent-inline-editor"
        @close="closeEditor"
        @saved="handleEditorSaved"
      />
    </Transition>

    <section class="agent-grid" v-loading="loading">
      <article v-for="agent in paginatedAgents" :key="agent.agent_id" class="agent-card" :class="{ official: agent.is_custom === false }">
        <div v-if="agent.is_custom === false" class="official-badge">官方</div>
        <div class="card-top">
          <div class="avatar-wrap">
            <img :src="agent.logo_url || zunoAgentAvatar" :alt="agent.name" @error="handleImageError" />
          </div>
          <div class="card-main">
            <h3>{{ agent.name }}</h3>
            <p>{{ agent.description || '暂无描述' }}</p>
          </div>
        </div>

        <div class="meta-row">
          <span class="meta-pill"><img :src="toolIcon" alt="工具" />{{ agent.tool_ids?.length || 0 }} 工具</span>
          <span class="meta-pill"><img :src="mcpIcon" alt="MCP" />{{ agent.mcp_ids?.length || 0 }} MCP</span>
          <span class="meta-pill"><img :src="knowledgeIcon" alt="知识库" />{{ agent.knowledge_ids?.length || 0 }} 知识库</span>
        </div>

        <div class="card-footer">
          <span class="scope-text">{{ agent.is_custom === false ? '平台内置' : '我的智能体' }}</span>
          <div class="card-actions">
            <el-button class="agent-icon-button" type="primary" :icon="Edit" circle :title="agent.is_custom === false ? '查看' : '编辑'" :aria-label="agent.is_custom === false ? '查看' : '编辑'" @click="goEdit(agent, $event)" />
            <el-button class="agent-icon-button danger" type="danger" :icon="Delete" circle title="删除" aria-label="删除" @click="handleDelete(agent)" />
          </div>
        </div>
      </article>

      <ZunoEmptyState v-if="!loading && sortedAgents.length === 0">
        {{ searchKeyword ? '没有匹配到智能体，换个关键词试试看吧 (´･_･`)' : '这里还空着，点右上角的小加号召唤第一位伙伴吧 (๑•̀ㅂ•́)و✧' }}
      </ZunoEmptyState>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="sortedAgents.length" :page-size="LIST_PAGE_SIZE" />
    </section>
  </div>
</template>

<style scoped>
.agent-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 0;
}

.agent-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 12px 4px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.eyebrow {
  display: inline-flex;
  margin-bottom: 10px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #b86c33;
  font-size: 12px;
  letter-spacing: 0.14em;
}

.agent-hero h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
}

.agent-hero p {
  margin: 12px 0 0;
  max-width: 720px;
  line-height: 1.8;
  color: #6e5d4e;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  flex: 0 1 520px;
}

.hero-actions :deep(.el-button + .el-button),
.card-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.hero-actions .is-create-open :deep(.el-icon) {
  transform: rotate(45deg);
  transition: transform 180ms cubic-bezier(.2, .8, .2, 1);
}

.agent-inline-editor {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.96), rgba(255, 250, 245, 0.88)),
    rgba(255, 255, 255, 0.84);
  box-shadow: 0 16px 36px rgba(160, 95, 42, 0.08);
  padding: 18px 22px 20px;
}

.agent-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
}

.agent-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px;
  padding: 14px 4px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.agent-card.official {
  background: transparent;
}

.official-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #d68446;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.card-top {
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 0;
}

.card-main {
  flex: 1;
  min-width: 0;
}

.avatar-wrap {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 12px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.avatar-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-main h3 {
  margin: 0;
  font-size: 16px;
  color: #2f241d;
  padding-right: 0;
  line-height: 1.28;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-main p {
  margin: 4px 0 0;
  line-height: 1.35;
  color: #64748b;
  font-size: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-row {
  grid-column: 1 / -1;
  margin-left: 46px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 0 6px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.055);
  color: #6b7a90;
  font-size: 10.5px;
  font-weight: 650;
  min-height: 18px;
  line-height: 18px;
}

.meta-pill img {
  width: 13px;
  height: 13px;
  object-fit: contain;
  opacity: 0.86;
}

.card-footer {
  grid-column: 2;
  grid-row: 1 / span 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.scope-text {
  display: none;
  color: #977050;
  font-size: 13px;
}

.card-actions {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
  justify-content: flex-end;
  margin-left: auto;
}

.agent-icon-button {
  width: 30px;
  height: 30px;
  min-width: 30px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}

.agent-icon-button.danger {
  border-color: rgba(239, 68, 68, 0.16);
  background: rgba(239, 68, 68, 0.07);
  color: #b91c1c;
}

@media (max-width: 960px) {
  .agent-hero {
    flex-direction: column;
  }

  .hero-actions {
    width: 100%;
    justify-content: flex-start;
  }

}
</style>
