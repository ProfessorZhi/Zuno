<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Search } from '@element-plus/icons-vue'
import robotIcon from '../../assets/robot.svg'
import pluginIcon from '../../assets/plugin.svg'
import knowledgeIcon from '../../assets/knowledge.svg'
import mcpIcon from '../../assets/mcp.svg'
import { deleteAgentAPI, getAgentsAPI, searchAgentsAPI, type AgentResponse } from '../../apis/agent'
import type { Agent } from '../../type'
import { useUserStore } from '../../store/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const searchLoading = ref(false)
const searchKeyword = ref('')
const agents = ref<Agent[]>([])

const normalizeAgent = (item: AgentResponse): Agent => ({
  agent_id: item.agent_id || item.id || '',
  name: item.name || '未命名智能体',
  description: item.description || '暂无描述',
  logo_url: item.logo_url || robotIcon,
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

const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')

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

const goCreate = () => {
  router.push('/agent/editor')
}

const goEdit = (agent: Agent) => {
  if (agent.is_custom === false && !isAdmin.value) {
    ElMessage.warning('只有管理员可以编辑官方智能体')
    return
  }
  router.push({ path: '/agent/editor', query: { id: agent.agent_id } })
}

const handleDelete = async (agent: Agent) => {
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
  if (target) target.src = robotIcon
}

onMounted(fetchAgents)
</script>

<template>
  <div class="agent-page">
    <section class="agent-hero">
      <div>
        <div class="eyebrow">AGENT CENTER</div>
        <h2>智能体管理</h2>
        <p>在这里维护平台内置智能体和你创建的专属智能体。列表只展示真实后端数据，不再注入测试样例。</p>
      </div>
      <div class="hero-actions">
        <el-input
          v-model="searchKeyword"
          class="search-input"
          clearable
          placeholder="搜索智能体名称"
          @clear="clearSearch"
          @keyup.enter="handleSearch"
        />
        <el-button :icon="Search" :loading="searchLoading" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" :loading="loading" @click="fetchAgents">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="goCreate">创建智能体</el-button>
      </div>
    </section>

    <section class="agent-grid" v-loading="loading">
      <article v-for="agent in sortedAgents" :key="agent.agent_id" class="agent-card" :class="{ official: agent.is_custom === false }">
        <div v-if="agent.is_custom === false" class="official-badge">官方</div>
        <div class="card-top">
          <div class="avatar-wrap">
            <img :src="agent.logo_url || robotIcon" :alt="agent.name" @error="handleImageError" />
          </div>
          <div class="card-main">
            <h3>{{ agent.name }}</h3>
            <p>{{ agent.description || '暂无描述' }}</p>
          </div>
        </div>

        <div class="meta-row">
          <span class="meta-pill"><img :src="pluginIcon" alt="工具" />{{ agent.tool_ids?.length || 0 }} 工具</span>
          <span class="meta-pill"><img :src="mcpIcon" alt="MCP" />{{ agent.mcp_ids?.length || 0 }} MCP</span>
          <span class="meta-pill"><img :src="knowledgeIcon" alt="知识库" />{{ agent.knowledge_ids?.length || 0 }} 知识库</span>
        </div>

        <div class="card-footer">
          <span class="scope-text">{{ agent.is_custom === false ? '平台内置' : '我的智能体' }}</span>
          <div class="card-actions">
            <el-button size="small" type="primary" :icon="Edit" @click="goEdit(agent)">
              {{ agent.is_custom === false ? '查看' : '编辑' }}
            </el-button>
            <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(agent)">删除</el-button>
          </div>
        </div>
      </article>

      <div v-if="!loading && sortedAgents.length === 0" class="empty-state">
        <img :src="robotIcon" alt="空状态" />
        <h3>还没有可展示的智能体</h3>
        <p>{{ searchKeyword ? '没有匹配当前关键词的结果。' : '先创建一个智能体，或刷新列表重新拉取。' }}</p>
        <div class="empty-actions">
          <el-button v-if="searchKeyword" @click="clearSearch">查看全部</el-button>
          <el-button v-else type="primary" @click="goCreate">创建智能体</el-button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.agent-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.agent-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px 32px;
  border-radius: 28px;
  background: radial-gradient(circle at top right, rgba(214, 132, 70, 0.14), transparent 32%),
    linear-gradient(180deg, rgba(255, 252, 247, 0.96) 0%, rgba(252, 246, 238, 0.94) 100%);
  border: 1px solid rgba(214, 132, 70, 0.12);
  box-shadow: 0 18px 40px rgba(140, 100, 62, 0.08);
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
  font-size: 34px;
  color: #2f241d;
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
  gap: 12px;
}

.search-input {
  width: 260px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 18px;
}

.agent-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 22px;
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 14px 30px rgba(120, 80, 42, 0.08);
}

.agent-card.official {
  background: linear-gradient(180deg, rgba(255, 249, 241, 0.96) 0%, rgba(255, 245, 232, 0.96) 100%);
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
  gap: 16px;
}

.avatar-wrap {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  border-radius: 20px;
  background: rgba(214, 132, 70, 0.12);
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
  font-size: 22px;
  color: #2f241d;
}

.card-main p {
  margin: 10px 0 0;
  line-height: 1.7;
  color: #6f6050;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.08);
  color: #8a643e;
  font-size: 13px;
}

.meta-pill img {
  width: 14px;
  height: 14px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.scope-text {
  color: #977050;
  font-size: 13px;
}

.card-actions {
  display: flex;
  gap: 10px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 52px 20px;
  border-radius: 24px;
  border: 1px dashed rgba(214, 132, 70, 0.24);
  background: rgba(255, 252, 247, 0.8);
  color: #6f6050;
}

.empty-state img {
  width: 64px;
  height: 64px;
}

.empty-state h3 {
  margin: 0;
  color: #342820;
}

.empty-state p {
  margin: 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
}

@media (max-width: 960px) {
  .agent-hero {
    flex-direction: column;
  }

  .hero-actions {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }
}
</style>
