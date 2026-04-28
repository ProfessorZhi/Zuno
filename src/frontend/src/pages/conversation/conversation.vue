<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { Close, Plus, Search } from "@element-plus/icons-vue"
import { getAgentsAPI } from "../../apis/agent"
import { createDialogAPI, deleteDialogAPI, getDialogListAPI } from "../../apis/history"
import { deleteWorkspaceSessionAPI, getWorkspaceSessionsAPI } from "../../apis/workspace"
import histortCard from "../../components/historyCard/histortCard.vue"
import { useHistoryChatStore } from "../../store/history_chat_msg"
import type { AgentResponse } from "../../apis/agent"
import type { DialogCreateType, HistoryListType } from "../../type"
import { zunoAgentAvatar } from "../../utils/brand"

const router = useRouter()
const route = useRoute()
const historyChatStore = useHistoryChatStore()

const searchKeyword = ref("")
const selectedDialog = ref("")
const showCreateDialog = ref(false)
const selectedAgent = ref("")
const agentSearchKeyword = ref("")

const dialogs = ref<HistoryListType[]>([])
const agents = ref<AgentResponse[]>([])
const loading = ref(false)
const agentsLoading = ref(false)

const normalizeSessionKind = (value: string | undefined) => {
  if (!value) return "dialog"
  if (value === "simple") return "simple"
  if (value === "wechat-agent") return "wechat-agent"
  return value
}

const formatAbsoluteTime = (timeStr: string) => {
  const date = new Date(timeStr)
  if (Number.isNaN(date.getTime())) return "未知时间"
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}

const formatRelativeTime = (timeStr: string) => {
  const date = new Date(timeStr)
  if (Number.isNaN(date.getTime())) return "未知时间"

  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

  if (diffInHours < 1) return "刚刚"
  if (diffInHours < 24) return `${Math.floor(diffInHours)} 小时前`
  if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)} 天前`
  return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" })
}

const getSortTime = (item: Pick<HistoryListType, "updatedTime" | "createTime">) => {
  const date = new Date(item.updatedTime || item.createTime)
  return Number.isNaN(date.getTime()) ? 0 : date.getTime()
}

const normalizeDialogItem = (dialog: any): HistoryListType => {
  const updatedTime = dialog.update_time || dialog.create_time || new Date().toISOString()
  const createTime = dialog.create_time || updatedTime
  return {
    dialogId: dialog.dialog_id,
    sourceType: "dialog",
    sessionKind: normalizeSessionKind(dialog.agent_type || "Agent"),
    name: dialog.dialog_name || dialog.name || "未命名会话",
    agent: dialog.agent_name || dialog.agent_type || "默认聊天 Agent",
    createTime,
    updatedTime,
    absoluteTime: formatAbsoluteTime(updatedTime),
    logo: dialog.logo_url || zunoAgentAvatar,
  }
}

const normalizeWorkspaceItem = (session: any): HistoryListType => {
  const updatedTime = session.update_time || session.create_time || new Date().toISOString()
  const createTime = session.create_time || updatedTime
  const sessionKind = normalizeSessionKind(session.agent)
  return {
    dialogId: session.session_id || session.id,
    sourceType: "workspace",
    sessionKind,
    name: session.title || "未命名会话",
    agent: sessionKind === "simple" ? "简化聊天模式" : "工作台会话",
    createTime,
    updatedTime,
    absoluteTime: formatAbsoluteTime(updatedTime),
    logo: zunoAgentAvatar,
  }
}

const filteredDialogs = computed(() => {
  if (!searchKeyword.value.trim()) return dialogs.value
  const keyword = searchKeyword.value.trim().toLowerCase()
  return dialogs.value.filter((dialog) => {
    const name = dialog.name?.toLowerCase?.() ?? ""
    const agent = dialog.agent?.toLowerCase?.() ?? ""
    return name.includes(keyword) || agent.includes(keyword)
  })
})

const groupedDialogs = computed(() => {
  const today: HistoryListType[] = []
  const lastWeek: HistoryListType[] = []
  const earlier: HistoryListType[] = []
  const now = new Date()

  filteredDialogs.value.forEach((dialog) => {
    const date = new Date(dialog.updatedTime || dialog.createTime)
    if (Number.isNaN(date.getTime())) {
      earlier.push(dialog)
      return
    }

    const diffInDays = (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)

    if (diffInDays < 1) {
      today.push(dialog)
    } else if (diffInDays < 7) {
      lastWeek.push(dialog)
    } else {
      earlier.push(dialog)
    }
  })

  return [
    { key: "today", label: "今天", items: today },
    { key: "last-week", label: "最近 7 天", items: lastWeek },
    { key: "earlier", label: "更早", items: earlier },
  ].filter((group) => group.items.length > 0)
})

const filteredAgents = computed(() => {
  if (!agentSearchKeyword.value.trim()) return agents.value
  const keyword = agentSearchKeyword.value.trim().toLowerCase()
  return agents.value.filter((agent) => {
    const name = agent.name?.toLowerCase?.() ?? ""
    const description = agent.description?.toLowerCase?.() ?? ""
    return name.includes(keyword) || description.includes(keyword)
  })
})

const selectedAgentName = computed(() => (
  agents.value.find((item) => item.agent_id === selectedAgent.value || String((item as any).id) === String(selectedAgent.value))?.name
    || "未选择"
))

const syncSelectedDialog = () => {
  selectedDialog.value = String(route.query.dialog_id || route.query.session_id || historyChatStore.dialogId || "")
}

const fetchAgents = async () => {
  try {
    agentsLoading.value = true
    const response = await getAgentsAPI()
    if (response.data.status_code === 200) {
      agents.value = response.data.data
      return
    }
    ElMessage.error(`获取智能体列表失败: ${response.data.status_message}`)
  } catch (error) {
    console.error("获取智能体列表出错:", error)
    ElMessage.error("获取智能体列表失败，请检查网络连接")
  } finally {
    agentsLoading.value = false
  }
}

const fetchDialogs = async () => {
  try {
    loading.value = true
    const [dialogResponse, workspaceResponse] = await Promise.all([
      getDialogListAPI(),
      getWorkspaceSessionsAPI(),
    ])
    const merged: HistoryListType[] = []
    const failedSources: string[] = []

    if (dialogResponse.data.status_code === 200) {
      merged.push(...(dialogResponse.data.data || []).map(normalizeDialogItem))
    } else {
      failedSources.push("Agent 会话")
      console.warn("fetch dialog history failed:", dialogResponse.data.status_message)
    }

    if (workspaceResponse.data.status_code === 200) {
      merged.push(
        ...(workspaceResponse.data.data || [])
          .filter((session: any) => Array.isArray(session.contexts) && session.contexts.length > 0)
          .map(normalizeWorkspaceItem)
      )
    } else {
      failedSources.push("工作台会话")
      console.warn("fetch workspace history failed:", workspaceResponse.data.status_message)
    }

    if (failedSources.length === 2) {
      dialogs.value = []
      ElMessage.error("获取历史列表失败，请检查网络连接")
      return
    }

    if (failedSources.length === 1) {
      ElMessage.warning(`${failedSources[0]} 暂时加载失败，已展示其余历史`)
    }

    dialogs.value = merged.sort((left, right) => getSortTime(right) - getSortTime(left))
    syncSelectedDialog()
  } catch (error) {
    console.error("获取历史列表出错:", error)
    ElMessage.error("获取历史列表失败，请检查网络连接")
  } finally {
    loading.value = false
  }
}

const handleWorkspaceSessionUpdated = async () => {
  await fetchDialogs()
}

const createDialog = async () => {
  if (!selectedAgent.value) {
    ElMessage.warning("请选择一个智能体")
    return
  }

  const agent = agents.value.find((item) => {
    const agentIdMatch = item.agent_id === selectedAgent.value || String(item.agent_id) === String(selectedAgent.value)
    const idMatch = (item as any).id === selectedAgent.value || String((item as any).id) === String(selectedAgent.value)
    return agentIdMatch || idMatch
  })

  if (!agent) {
    ElMessage.error("未找到选中的智能体")
    return
  }

  try {
    const dialogData: DialogCreateType = {
      name: `与 ${agent.name} 的对话`,
      agent_id: (agent as any).id || agent.agent_id,
      agent_type: "Agent",
    }

    const response = await createDialogAPI(dialogData)
    if (response.data.status_code !== 200) {
      ElMessage.error(`创建会话失败: ${response.data.status_message}`)
      return
    }

    const dialogId = response.data.data.dialog_id
    historyChatStore.dialogId = dialogId
    historyChatStore.name = dialogData.name
    historyChatStore.logo = agent.logo_url || zunoAgentAvatar

    selectedAgent.value = ""
    agentSearchKeyword.value = ""
    showCreateDialog.value = false
    await fetchDialogs()

    router.push({
      path: "/conversation/chatPage",
      query: { dialog_id: dialogId },
    })
  } catch (error) {
    console.error("创建会话出错:", error)
    ElMessage.error("创建会话失败，请检查网络连接")
  }
}

const deleteHistoryItem = async (item: HistoryListType) => {
  try {
    const response = item.sourceType === "workspace"
      ? await deleteWorkspaceSessionAPI(item.dialogId)
      : await deleteDialogAPI(item.dialogId)

    if (response.data.status_code !== 200) {
      ElMessage.error(`删除会话失败: ${response.data.status_message}`)
      return
    }

    ElMessage.success("会话已删除")
    if (selectedDialog.value === item.dialogId) {
      selectedDialog.value = ""
    }
    await fetchDialogs()
  } catch (error) {
    console.error("删除会话出错:", error)
    ElMessage.error("删除会话失败，请检查网络连接")
  }
}

const selectDialog = (dialog: HistoryListType) => {
  selectedDialog.value = dialog.dialogId
  historyChatStore.dialogId = dialog.dialogId
  historyChatStore.name = dialog.name
  historyChatStore.logo = dialog.logo

  if (dialog.sourceType === "workspace") {
    router.push({
      name: "workspaceDefaultPage",
      query: {
        session_id: dialog.dialogId,
        mode: dialog.sessionKind === "simple" ? "normal" : "agent",
        execution_mode: "tool",
        access_scope: "workspace",
      },
    })
    return
  }

  router.push({
    path: "/conversation/chatPage",
    query: { dialog_id: dialog.dialogId },
  })
}

const openCreateDialog = async () => {
  showCreateDialog.value = true
  selectedAgent.value = ""
  agentSearchKeyword.value = ""
  if (!agents.value.length) {
    await fetchAgents()
  }
}

const selectAgent = (agentId: string) => {
  const agent = agents.value.find((item) => {
    const agentIdMatch = item.agent_id === agentId || String(item.agent_id) === String(agentId)
    const idMatch = (item as any).id === agentId || String((item as any).id) === String(agentId)
    return agentIdMatch || idMatch
  })

  if (agent) {
    selectedAgent.value = String((agent as any).id || agent.agent_id)
  }
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  selectedAgent.value = ""
  agentSearchKeyword.value = ""
}

onMounted(async () => {
  await Promise.all([fetchAgents(), fetchDialogs()])
  syncSelectedDialog()
  window.addEventListener("workspace-session-updated", handleWorkspaceSessionUpdated)
})

onBeforeUnmount(() => {
  window.removeEventListener("workspace-session-updated", handleWorkspaceSessionUpdated)
})

watch(() => route.query.dialog_id, syncSelectedDialog)
watch(() => route.query.session_id, syncSelectedDialog)
</script>

<template>
  <div class="conversation-main">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-copy">
          <span class="eyebrow">Zuno</span>
          <h2>工作历史</h2>
          <p>这里统一展示 Agent 对话、默认聊天和简化模式的所有历史。</p>
        </div>
        <button class="create-btn-native" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          <span>新建 Agent 对话</span>
        </button>
      </div>

      <div class="search-section">
        <label class="search-shell">
          <el-icon><Search /></el-icon>
          <input
            v-model="searchKeyword"
            class="search-input"
            type="text"
            placeholder="搜索会话标题或模式"
          />
          <button
            v-if="searchKeyword"
            type="button"
            class="search-clear"
            aria-label="清除搜索"
            @click="searchKeyword = ''"
          >
            <el-icon><Close /></el-icon>
          </button>
        </label>
      </div>

      <div class="list-header">
        <span class="title">全部会话</span>
        <span class="count">{{ filteredDialogs.length }}</span>
      </div>

      <div class="dialog-list">
        <div v-if="loading" class="feedback-state">
          <div class="state-dot"></div>
          <div class="state-text">正在整理你的工作历史...</div>
        </div>

        <div v-else-if="filteredDialogs.length === 0" class="feedback-state empty">
          <div class="empty-mark">Z</div>
          <div class="state-text">{{ searchKeyword ? "没有找到相关会话" : "还没有工作历史" }}</div>
          <div class="state-hint">
            {{ searchKeyword ? "换个关键词再试试" : "从上方开始新的对话即可" }}
          </div>
        </div>

        <template v-else>
          <section
            v-for="group in groupedDialogs"
            :key="group.key"
            class="dialog-group"
          >
            <div class="group-header">
              <span>{{ group.label }}</span>
            </div>
            <histortCard
              v-for="dialog in group.items"
              :key="`${dialog.sourceType}-${dialog.dialogId}`"
              :item="dialog"
              :time-label="formatRelativeTime(dialog.updatedTime || dialog.createTime)"
              :class="{ active: selectedDialog === dialog.dialogId }"
              @select="selectDialog(dialog)"
              @delete="deleteHistoryItem(dialog)"
            />
          </section>
        </template>
      </div>
    </aside>

    <main class="content">
      <router-view />
    </main>

    <div v-if="showCreateDialog" class="create-dialog-overlay" @click="closeCreateDialog">
      <div class="create-dialog" @click.stop>
        <div class="dialog-header">
          <div>
            <p class="dialog-eyebrow">新建 Agent 对话</p>
            <h3>选择一个智能体作为起点</h3>
          </div>
          <button class="close-btn" @click="closeCreateDialog" aria-label="关闭">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <div class="dialog-body">
          <div class="search-section modal-search">
            <label class="search-shell">
              <el-icon><Search /></el-icon>
              <input
                v-model="agentSearchKeyword"
                class="search-input"
                type="text"
                placeholder="搜索智能体"
              />
            </label>
          </div>

          <div class="agents-section">
            <div class="section-header">
              <span class="title">可用智能体</span>
              <span class="count">{{ filteredAgents.length }}</span>
            </div>

            <div v-if="agentsLoading" class="feedback-state modal-state">
              <div class="state-dot"></div>
              <div class="state-text">正在加载智能体...</div>
            </div>

            <div v-else-if="filteredAgents.length === 0" class="feedback-state empty modal-state">
              <div class="empty-mark">Z</div>
              <div class="state-text">{{ agentSearchKeyword ? "没有找到相关智能体" : "暂无可用智能体" }}</div>
              <div class="state-hint">
                {{ agentSearchKeyword ? "试试别的关键词" : "请先创建或发布一个智能体" }}
              </div>
            </div>

            <div v-else class="agents-grid">
              <button
                v-for="agent in filteredAgents"
                :key="(agent as any).id || agent.agent_id"
                type="button"
                :class="['agent-card', selectedAgent === String((agent as any).id || agent.agent_id) ? 'active' : '']"
                @click="selectAgent(String((agent as any).id || agent.agent_id))"
              >
                <div class="agent-avatar">
                  <img :src="agent.logo_url || zunoAgentAvatar" alt="" />
                </div>
                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-description">{{ agent.description || "从这里开始新的任务流。" }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <div class="selection-copy">
            当前选择：
            <span>{{ selectedAgentName }}</span>
          </div>
          <div class="footer-actions">
            <button class="btn-cancel" @click="closeCreateDialog">取消</button>
            <button class="btn-confirm" :disabled="!selectedAgent" @click="createDialog">
              创建会话
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.conversation-main {
  display: flex;
  height: calc(100vh - 64px);
  background: var(--zuno-bg-canvas);
}

.sidebar {
  width: 340px;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  background: var(--zuno-bg-sidebar);
  border-right: 1px solid var(--zuno-border-soft);
}

.sidebar-header {
  padding: 24px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.sidebar-copy {
  .eyebrow {
    display: inline-flex;
    min-height: 28px;
    padding: 0 12px;
    border-radius: 999px;
    background: rgba(201, 117, 61, 0.08);
    color: #ad6736;
    font-size: 12px;
    align-items: center;
  }

  h2 {
    margin: 14px 0 6px;
    color: #2f261f;
    font-size: 22px;
    font-weight: 600;
  }

  p {
    margin: 0;
    color: var(--zuno-text-secondary);
    font-size: 14px;
    line-height: 1.7;
  }
}

.create-btn-native {
  min-height: 52px;
  border: 1px solid rgba(209, 179, 150, 0.5);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  color: #453527;
  font-size: 15px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 18px 30px rgba(91, 63, 32, 0.08);
  }
}

.search-section {
  padding: 0 20px 16px;
}

.search-shell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 48px;
  padding: 0 14px;
  border: 1px solid rgba(209, 179, 150, 0.42);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.76);
  color: var(--zuno-text-secondary);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: #2f261f;
  font-size: 14px;
}

.search-clear {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--zuno-text-muted);
  cursor: pointer;
}

.list-header,
.section-header {
  padding: 0 20px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--zuno-text-secondary);
  font-size: 13px;
  font-weight: 600;

  .count {
    min-width: 28px;
    min-height: 28px;
    padding: 0 10px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(201, 117, 61, 0.08);
    color: #ad6736;
  }
}

.dialog-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 16px 20px;
}

.dialog-group + .dialog-group {
  margin-top: 14px;
}

.group-header {
  margin-bottom: 10px;
  color: var(--zuno-text-muted);
  font-size: 12px;
  font-weight: 600;
}

.feedback-state {
  min-height: 180px;
  border: 1px dashed rgba(209, 179, 150, 0.4);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.58);
  display: grid;
  place-items: center;
  text-align: center;
  padding: 24px;
}

.state-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #c8753d;
  animation: pulse 1.2s infinite ease-in-out;
}

.state-text {
  color: #413428;
  font-size: 15px;
  font-weight: 600;
}

.state-hint {
  color: var(--zuno-text-secondary);
  font-size: 13px;
}

.empty-mark {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: rgba(201, 117, 61, 0.12);
  color: #ad6736;
  font-size: 28px;
  font-weight: 700;
}

.content {
  flex: 1;
  min-width: 0;
  background: linear-gradient(180deg, rgba(255, 251, 244, 0.96), rgba(252, 248, 241, 0.98));
}

.create-dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(50, 35, 24, 0.18);
  display: grid;
  place-items: center;
  z-index: 40;
}

.create-dialog {
  width: min(760px, calc(100vw - 32px));
  max-height: calc(100vh - 48px);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-radius: 28px;
  background: #fffaf4;
  box-shadow: 0 30px 80px rgba(53, 37, 26, 0.18);
}

.dialog-header,
.dialog-footer {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid rgba(209, 179, 150, 0.26);
}

.dialog-footer {
  border-top: 1px solid rgba(209, 179, 150, 0.26);
  border-bottom: none;
}

.dialog-eyebrow {
  margin: 0 0 4px;
  color: #ad6736;
  font-size: 12px;
  font-weight: 600;
}

.dialog-header h3 {
  margin: 0;
  color: #2f261f;
  font-size: 22px;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 999px;
  background: rgba(201, 117, 61, 0.08);
  color: #8b5431;
  cursor: pointer;
}

.dialog-body {
  overflow-y: auto;
  padding: 20px 24px;
}

.modal-search {
  padding: 0 0 16px;
}

.agents-grid {
  display: grid;
  gap: 12px;
}

.agent-card {
  width: 100%;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid rgba(209, 179, 150, 0.42);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  text-align: left;
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover,
  &.active {
    border-color: rgba(201, 117, 61, 0.4);
    box-shadow: 0 16px 28px rgba(91, 63, 32, 0.08);
  }
}

.agent-avatar {
  width: 48px;
  height: 48px;
  overflow: hidden;
  border-radius: 16px;
  background: rgba(201, 117, 61, 0.08);
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.agent-name {
  color: #2f261f;
  font-size: 15px;
  font-weight: 600;
}

.agent-description {
  margin-top: 4px;
  color: var(--zuno-text-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.selection-copy {
  color: var(--zuno-text-secondary);
  font-size: 14px;

  span {
    color: #2f261f;
    font-weight: 600;
  }
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.btn-cancel,
.btn-confirm {
  min-width: 104px;
  height: 42px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel {
  border: 1px solid rgba(209, 179, 150, 0.52);
  background: transparent;
  color: #594636;
}

.btn-confirm {
  border: none;
  background: #c8753d;
  color: #fff8f2;

  &:disabled {
    cursor: not-allowed;
    opacity: 0.48;
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(0.88);
    opacity: 0.7;
  }
}

@media (max-width: 960px) {
  .conversation-main {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 64px);
  }

  .sidebar {
    width: 100%;
    min-width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--zuno-border-soft);
  }
}
</style>
