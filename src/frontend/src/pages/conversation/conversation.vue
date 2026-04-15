<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { Plus, Search, Close } from "@element-plus/icons-vue"
import { getAgentsAPI } from "../../apis/agent"
import { createDialogAPI, deleteDialogAPI, getDialogListAPI } from "../../apis/history"
import type { AgentResponse } from "../../apis/agent"
import type { DialogCreateType, HistoryListType } from "../../type"
import histortCard from "../../components/historyCard/histortCard.vue"
import { useHistoryChatStore } from "../../store/history_chat_msg"
import zunoAvatar from "../../assets/zuno-avatar.svg"

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

const filteredDialogs = computed(() => {
  if (!searchKeyword.value.trim()) return dialogs.value
  const keyword = searchKeyword.value.trim().toLowerCase()
  return dialogs.value.filter((dialog) => {
    const name = dialog.name?.toLowerCase?.() ?? ""
    const agent = dialog.agent?.toLowerCase?.() ?? ""
    return name.includes(keyword) || agent.includes(keyword)
  })
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

const groupedDialogs = computed(() => {
  const today: HistoryListType[] = []
  const lastWeek: HistoryListType[] = []
  const earlier: HistoryListType[] = []
  const now = new Date()

  filteredDialogs.value.forEach((dialog) => {
    const date = new Date(dialog.createTime)
    if (Number.isNaN(date.getTime())) {
      earlier.push(dialog)
      return
    }

    const diff = now.getTime() - date.getTime()
    const diffInDays = diff / (1000 * 60 * 60 * 24)

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
    { key: "earlier", label: "更早", items: earlier }
  ].filter((group) => group.items.length > 0)
})

const formatTime = (timeStr: string) => {
  try {
    if (!timeStr) return "未知时间"
    const date = new Date(timeStr)
    if (Number.isNaN(date.getTime())) return "未知时间"

    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) return "刚刚"
    if (diffInHours < 24) return `${Math.floor(diffInHours)} 小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)} 天前`
    return date.toLocaleDateString("zh-CN", { month: "short", day: "numeric" })
  } catch (error) {
    console.error("时间格式化失败:", error)
    return "未知时间"
  }
}

const syncSelectedDialog = () => {
  const dialogId = String(route.query.dialog_id || historyChatStore.dialogId || "")
  selectedDialog.value = dialogId
}

const fetchAgents = async () => {
  try {
    agentsLoading.value = true
    const response = await getAgentsAPI()
    if (response.data.status_code === 200) {
      agents.value = response.data.data
    } else {
      ElMessage.error(`获取智能体列表失败: ${response.data.status_message}`)
    }
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
    const response = await getDialogListAPI()
    if (response.data.status_code === 200) {
      dialogs.value = response.data.data.map((dialog: any) => ({
        dialogId: dialog.dialog_id,
        name: dialog.name,
        agent: dialog.name,
        createTime: dialog.create_time || dialog.update_time || new Date().toISOString(),
        logo: dialog.logo_url || zunoAvatar
      }))

      syncSelectedDialog()

      if (dialogs.value.length > 0 && router.currentRoute.value.name === "defaultPage") {
        const firstDialog = dialogs.value[0]
        selectedDialog.value = firstDialog.dialogId
        historyChatStore.dialogId = firstDialog.dialogId
        historyChatStore.name = firstDialog.name
        historyChatStore.logo = firstDialog.logo
        router.push({
          path: "/conversation/chatPage",
          query: { dialog_id: firstDialog.dialogId }
        })
      }
    } else {
      ElMessage.error(`获取会话列表失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error("获取会话列表出错:", error)
    ElMessage.error("获取会话列表失败，请检查网络连接")
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (router.currentRoute.value.path === "/conversation") {
    await fetchDialogs()
    if (router.currentRoute.value.name === "defaultPage") {
      await fetchAgents()
    }
  } else {
    await Promise.all([fetchAgents(), fetchDialogs()])
  }
  syncSelectedDialog()
})

watch(() => route.query.dialog_id, syncSelectedDialog)

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
      name: `与${agent.name}的对话`,
      agent_id: (agent as any).id || agent.agent_id,
      agent_type: "Agent"
    }

    const response = await createDialogAPI(dialogData)
    if (response.data.status_code === 200) {
      ElMessage.success("会话创建成功")

      const dialogId = response.data.data.dialog_id
      await fetchDialogs()
      showCreateDialog.value = false
      selectedAgent.value = ""
      agentSearchKeyword.value = ""

      if (dialogId) {
        selectedDialog.value = dialogId
        historyChatStore.dialogId = dialogId
        historyChatStore.name = dialogData.name
        historyChatStore.logo = agent.logo_url || zunoAvatar
        router.push({
          path: "/conversation/chatPage",
          query: { dialog_id: dialogId }
        })
      }
    } else {
      ElMessage.error(`创建会话失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error("创建会话出错:", error)
    ElMessage.error("创建会话失败，请检查网络连接")
  }
}

const deleteDialog = async (dialogId: string) => {
  try {
    const response = await deleteDialogAPI(dialogId)
    if (response.data.status_code === 200) {
      ElMessage.success("会话已删除")
      await fetchDialogs()
      if (selectedDialog.value === dialogId) {
        selectedDialog.value = ""
      }
    } else {
      ElMessage.error(`删除会话失败: ${response.data.status_message}`)
    }
  } catch (error) {
    console.error("删除会话出错:", error)
    ElMessage.error("删除会话失败，请检查网络连接")
  }
}

const selectDialog = (dialogId: string) => {
  const dialog = dialogs.value.find((item) => item.dialogId === dialogId)
  if (!dialog) return

  selectedDialog.value = dialogId
  historyChatStore.dialogId = dialogId
  historyChatStore.name = dialog.name
  historyChatStore.logo = dialog.logo

  router.push({
    path: "/conversation/chatPage",
    query: { dialog_id: dialogId }
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
    selectedAgent.value = (agent as any).id || agent.agent_id
  }
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  selectedAgent.value = ""
  agentSearchKeyword.value = ""
}
</script>

<template>
  <div class="conversation-main">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-copy">
          <span class="eyebrow">Zuno</span>
          <h2>工作历史</h2>
          <p>继续之前的对话，或开启一条新的思路。</p>
        </div>
        <button class="create-btn-native" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </button>
      </div>

      <div class="search-section">
        <label class="search-shell">
          <el-icon><Search /></el-icon>
          <input
            v-model="searchKeyword"
            class="search-input"
            type="text"
            placeholder="搜索工作历史"
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
          <div class="state-text">正在整理你的工作历史…</div>
        </div>

        <div v-else-if="filteredDialogs.length === 0" class="feedback-state empty">
          <div class="empty-mark">Z</div>
          <div class="state-text">{{ searchKeyword ? "没有找到相关会话" : "还没有工作历史" }}</div>
          <div class="state-hint">
            {{ searchKeyword ? "换个关键词再试试" : "从上方开始一条新的对话即可" }}
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
              :key="dialog.dialogId"
              :item="dialog"
              :time-label="formatTime(dialog.createTime)"
              :class="{ active: selectedDialog === dialog.dialogId }"
              @select="selectDialog(dialog.dialogId)"
              @delete="deleteDialog(dialog.dialogId)"
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
            <p class="dialog-eyebrow">新建对话</p>
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
              <div class="state-text">正在加载智能体…</div>
            </div>

            <div v-else-if="filteredAgents.length === 0" class="feedback-state empty modal-state">
              <div class="empty-mark">Z</div>
              <div class="state-text">{{ agentSearchKeyword ? "没有找到相关智能体" : "暂无可用智能体" }}</div>
              <div class="state-hint">
                {{ agentSearchKeyword ? "试试别的关键词" : "请先添加或发布一个智能体" }}
              </div>
            </div>

            <div v-else class="agents-grid">
              <button
                v-for="agent in filteredAgents"
                :key="(agent as any).id || agent.agent_id"
                type="button"
                :class="[
                  'agent-card',
                  selectedAgent === ((agent as any).id || agent.agent_id) ? 'active' : ''
                ]"
                @click="selectAgent((agent as any).id || agent.agent_id)"
              >
                <div class="agent-avatar">
                  <img :src="agent.logo_url || zunoAvatar" alt="" />
                </div>
                <div class="agent-info">
                  <div class="agent-name">{{ agent.name }}</div>
                  <div class="agent-description">{{ agent.description || "从这里开始新的工作流。" }}</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <div class="selection-copy">
            当前选择：
            <span>{{
              selectedAgent
                ? agents.find((item) => item.agent_id === selectedAgent || (item as any).id === selectedAgent)?.name || selectedAgent
                : "未选择"
            }}</span>
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
  width: 328px;
  min-width: 328px;
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
    align-items: center;
    min-height: 24px;
    padding: 0 10px;
    border-radius: 999px;
    background: var(--zuno-bg-muted);
    color: var(--zuno-text-tertiary);
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h2 {
    margin: 14px 0 8px;
    color: var(--zuno-text-primary);
    font-size: 22px;
    font-weight: 600;
    line-height: 1.2;
  }

  p {
    margin: 0;
    color: var(--zuno-text-secondary);
    font-size: 13px;
    line-height: 1.6;
  }
}

.create-btn-native {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  height: 46px;
  border: 1px solid var(--zuno-border-strong);
  border-radius: var(--zuno-radius-md);
  background: var(--zuno-surface-raised);
  color: var(--zuno-text-primary);
  font-size: 14px;
  font-weight: 600;
  transition: var(--zuno-transition-base);
  cursor: pointer;

  &:hover {
    background: var(--zuno-hover);
    box-shadow: var(--zuno-shadow-soft);
  }

  &:focus-visible {
    outline: none;
    box-shadow: var(--zuno-focus-ring);
  }
}

.search-section {
  padding: 0 20px 16px;
}

.search-shell {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0 14px;
  border: 1px solid var(--zuno-border-soft);
  border-radius: var(--zuno-radius-md);
  background: var(--zuno-surface-raised);
  color: var(--zuno-text-tertiary);
  transition: var(--zuno-transition-base);

  &:focus-within {
    border-color: var(--zuno-border-strong);
    box-shadow: var(--zuno-focus-ring);
    background: var(--zuno-bg-elevated);
  }
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--zuno-text-primary);
  font-size: 14px;

  &:focus {
    outline: none;
  }

  &::placeholder {
    color: var(--zuno-text-muted);
  }
}

.search-clear {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--zuno-text-tertiary);
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover {
    background: var(--zuno-hover);
    color: var(--zuno-text-primary);
  }
}

.list-header,
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px 12px;

  .title {
    color: var(--zuno-text-secondary);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 28px;
    height: 24px;
    padding: 0 8px;
    border-radius: 999px;
    background: var(--zuno-bg-muted);
    color: var(--zuno-text-tertiary);
    font-size: 12px;
    font-weight: 600;
  }
}

.dialog-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 14px 18px;
}

.dialog-group + .dialog-group {
  margin-top: 18px;
}

.group-header {
  padding: 0 6px 8px;
  color: var(--zuno-text-muted);
  font-size: 12px;
  font-weight: 600;
}

.feedback-state {
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 10px;
  padding: 24px;
  color: var(--zuno-text-secondary);
}

.state-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--zuno-accent);
  box-shadow: 0 0 0 8px rgba(141, 123, 106, 0.12);
  animation: pulse 1.6s ease-in-out infinite;
}

.state-text {
  color: var(--zuno-text-secondary);
  font-size: 14px;
}

.state-hint {
  color: var(--zuno-text-muted);
  font-size: 12px;
}

.feedback-state.empty {
  margin-top: 32px;
  border: 1px dashed var(--zuno-border-soft);
  border-radius: var(--zuno-radius-lg);
  background: rgba(255, 255, 255, 0.52);
}

.empty-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: var(--zuno-bg-muted);
  color: var(--zuno-text-primary);
  font-size: 20px;
  font-weight: 600;
}

.content {
  flex: 1;
  overflow: hidden;
  background: var(--zuno-bg-content);
}

.create-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(40, 35, 30, 0.18);
  backdrop-filter: blur(10px);
}

.create-dialog {
  width: min(680px, 92vw);
  max-height: 82vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--zuno-border-soft);
  border-radius: 24px;
  background: var(--zuno-bg-elevated);
  box-shadow: var(--zuno-shadow-strong);
}

.dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 18px;
  border-bottom: 1px solid var(--zuno-border-soft);

  h3 {
    margin: 6px 0 0;
    color: var(--zuno-text-primary);
    font-size: 22px;
    font-weight: 600;
  }
}

.dialog-eyebrow {
  margin: 0;
  color: var(--zuno-text-tertiary);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--zuno-text-tertiary);
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover {
    background: var(--zuno-hover);
    color: var(--zuno-text-primary);
  }
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 8px;
}

.modal-search {
  padding: 0 0 20px;
}

.modal-state {
  min-height: 180px;
}

.agents-grid {
  display: grid;
  gap: 12px;
  padding-bottom: 16px;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 14px;
  border: 1px solid var(--zuno-border-soft);
  border-radius: var(--zuno-radius-lg);
  background: var(--zuno-surface-raised);
  text-align: left;
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover {
    background: var(--zuno-hover);
    box-shadow: var(--zuno-shadow-soft);
  }

  &.active {
    border-color: var(--zuno-border-strong);
    background: var(--zuno-selected);
    box-shadow: 0 0 0 1px rgba(164, 149, 133, 0.36);
  }
}

.agent-avatar {
  width: 48px;
  height: 48px;
  overflow: hidden;
  border: 1px solid var(--zuno-border-soft);
  border-radius: 16px;
  background: var(--zuno-bg-muted);
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.agent-info {
  min-width: 0;
}

.agent-name {
  color: var(--zuno-text-primary);
  font-size: 15px;
  font-weight: 600;
}

.agent-description {
  margin-top: 4px;
  color: var(--zuno-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 24px 24px;
  border-top: 1px solid var(--zuno-border-soft);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0), rgba(247, 243, 236, 0.72));
}

.selection-copy {
  color: var(--zuno-text-secondary);
  font-size: 13px;

  span {
    color: var(--zuno-text-primary);
    font-weight: 600;
  }
}

.footer-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-cancel,
.btn-confirm {
  min-width: 92px;
  height: 42px;
  padding: 0 16px;
  border-radius: var(--zuno-radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--zuno-transition-base);
}

.btn-cancel {
  border: 1px solid var(--zuno-border-soft);
  background: var(--zuno-surface-raised);
  color: var(--zuno-text-secondary);

  &:hover {
    background: var(--zuno-hover);
  }
}

.btn-confirm {
  border: 1px solid transparent;
  background: var(--zuno-button-primary);
  color: #fffdf9;

  &:hover:not(:disabled) {
    background: var(--zuno-button-primary-hover);
    box-shadow: var(--zuno-shadow-soft);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

@media (max-width: 960px) {
  .sidebar {
    width: 300px;
    min-width: 300px;
  }
}

@media (max-width: 768px) {
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

  .dialog-list {
    max-height: 360px;
  }

  .dialog-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .footer-actions {
    justify-content: flex-end;
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
    opacity: 0.72;
  }
}
</style>
