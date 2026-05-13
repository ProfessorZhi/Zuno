<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import callsIcon from '../../assets/dashboard/调用次数.svg'
import inputTokenIcon from '../../assets/dashboard/输入token.svg'
import outputTokenIcon from '../../assets/dashboard/输出token.svg'
import totalTokenIcon from '../../assets/dashboard/总token.svg'
import detailIcon from '../../assets/dashboard/明细.svg'
import trendIcon from '../../assets/dashboard/趋势.svg'
import modelRankIcon from '../../assets/dashboard/模型排行.svg'
import agentRankIcon from '../../assets/dashboard/智能体排行.svg'
import filterIcon from '../../assets/dashboard/筛选.svg'
import emptyIcon from '../../assets/dashboard/空数据.svg'
import {
  getUsageStatsAPI,
  getUsageCountAPI,
  getUsageModelsAPI,
  getUsageAgentsAPI,
  type UsageStatsRequest,
  type UsageDataByDate,
  type UsageCountByDate,
} from '../../apis/usage-stats'
import { getAgentsAPI } from '../../apis/agent'

const loading = ref(false)
const models = ref<string[]>([])
const agents = ref<string[]>([])
const createdAgentNames = ref<string[]>([])
const tokenUsage = ref<UsageDataByDate>({})
const usageCount = ref<UsageCountByDate>({})

const filters = ref<UsageStatsRequest>({
  model: '',
  agent: '',
  delta_days: 30,
})

const recentDates = computed(() => {
  const dates = new Set<string>([
    ...Object.keys(tokenUsage.value || {}),
    ...Object.keys(usageCount.value || {}),
  ])
  return [...dates].sort((a, b) => new Date(b).getTime() - new Date(a).getTime()).slice(0, 12)
})

const totalCalls = computed(() =>
  Object.values(usageCount.value || {}).reduce((sum, day) => {
    const agentCalls = Object.values(day.agent || {}).reduce((n, value) => n + value, 0)
    const modelCalls = Object.values(day.model || {}).reduce((n, value) => n + value, 0)
    return sum + Math.max(agentCalls, modelCalls)
  }, 0)
)

const totalInputTokens = computed(() =>
  Object.values(tokenUsage.value || {}).reduce(
    (sum, day) => sum + Object.values(day.model || {}).reduce((n, item) => n + (item.input_tokens || 0), 0),
    0
  )
)

const totalOutputTokens = computed(() =>
  Object.values(tokenUsage.value || {}).reduce(
    (sum, day) => sum + Object.values(day.model || {}).reduce((n, item) => n + (item.output_tokens || 0), 0),
    0
  )
)

const totalTokens = computed(() => totalInputTokens.value + totalOutputTokens.value)
const internalAgentNames = new Set(['simple-agent', 'wechat-agent', 'normal', 'simple', 'agent', '其他', '未指定agent'])
const normalizeAgentName = (name: string) => name.trim().toLowerCase()
const isRealDashboardAgent = (name: string) => {
  const normalized = normalizeAgentName(name)
  if (!normalized || internalAgentNames.has(normalized)) return false
  const createdNames = new Set(createdAgentNames.value.map(normalizeAgentName))
  return createdNames.size === 0 || createdNames.has(normalized)
}
const visibleAgents = computed(() => {
  const names = new Set<string>()
  createdAgentNames.value.forEach((name) => {
    if (isRealDashboardAgent(name)) names.add(name)
  })
  agents.value.forEach((name) => {
    if (isRealDashboardAgent(name)) names.add(name)
  })
  return [...names]
})

const usageRows = computed(() =>
  recentDates.value.map((date) => {
    const tokenDay = tokenUsage.value[date]
    const countDay = usageCount.value[date]
    const input = Object.values(tokenDay?.model || {}).reduce((sum, item) => sum + (item.input_tokens || 0), 0)
    const output = Object.values(tokenDay?.model || {}).reduce((sum, item) => sum + (item.output_tokens || 0), 0)
    const calls = Math.max(
      Object.values(countDay?.agent || {}).reduce((sum, item) => sum + item, 0),
      Object.values(countDay?.model || {}).reduce((sum, item) => sum + item, 0)
    )
    return { date, calls, input, output, total: input + output }
  })
)

const topModels = computed(() => {
  const map = new Map<string, number>()
  Object.values(tokenUsage.value || {}).forEach((day) => {
    Object.entries(day.model || {}).forEach(([name, item]) => {
      map.set(name, (map.get(name) || 0) + (item.total_tokens || 0))
    })
  })
  return [...map.entries()].map(([name, total]) => ({ name, total })).sort((a, b) => b.total - a.total).slice(0, 8)
})

const topAgents = computed(() => {
  const map = new Map<string, number>()
  Object.values(usageCount.value || {}).forEach((day) => {
    Object.entries(day.agent || {}).forEach(([name, count]) => {
      if (!isRealDashboardAgent(name)) return
      map.set(name, (map.get(name) || 0) + count)
    })
  })
  return [...map.entries()].map(([name, total]) => ({ name, total })).sort((a, b) => b.total - a.total).slice(0, 8)
})

const periodText = computed(() => {
  switch (filters.value.delta_days) {
    case 7:
      return '最近 7 天'
    case 30:
      return '最近 30 天'
    case 365:
      return '最近 365 天'
    default:
      return '全部时间'
  }
})

const formatNumber = (value: number) => new Intl.NumberFormat('zh-CN').format(value || 0)

const maxDailyTotal = computed(() => Math.max(...usageRows.value.map((item) => item.total), 1))
const maxDailyCalls = computed(() => Math.max(...usageRows.value.map((item) => item.calls), 1))
const maxModelTotal = computed(() => Math.max(...topModels.value.map((item) => item.total), 1))
const maxAgentTotal = computed(() => Math.max(...topAgents.value.map((item) => item.total), 1))

const getPercent = (value: number, max: number) => `${Math.max(4, Math.round(((value || 0) / max) * 100))}%`

const kpiCards = computed(() => [
  { label: '调用次数', value: totalCalls.value, icon: callsIcon },
  { label: '输入 Token', value: totalInputTokens.value, icon: inputTokenIcon },
  { label: '输出 Token', value: totalOutputTokens.value, icon: outputTokenIcon },
  { label: '总 Token', value: totalTokens.value, icon: totalTokenIcon },
])

const loadMeta = async () => {
  try {
    const [modelResponse, agentResponse, createdAgentResponse] = await Promise.all([
      getUsageModelsAPI(),
      getUsageAgentsAPI(),
      getAgentsAPI(),
    ])
    if (modelResponse.data.status_code === 200) models.value = modelResponse.data.data || []
    if (createdAgentResponse.data.status_code === 200) {
      createdAgentNames.value = (createdAgentResponse.data.data || [])
        .map((item: any) => String(item?.name || '').trim())
        .filter(Boolean)
    }
    if (agentResponse.data.status_code === 200) agents.value = (agentResponse.data.data || []).filter(isRealDashboardAgent)
  } catch (error) {
    console.error('加载统计筛选项失败:', error)
  }
}

const loadDashboard = async () => {
  loading.value = true
  try {
    const payload: UsageStatsRequest = {
      model: filters.value.model || '',
      agent: filters.value.agent || '',
      delta_days: filters.value.delta_days || 30,
    }

    const [tokenResponse, countResponse] = await Promise.all([getUsageStatsAPI(payload), getUsageCountAPI(payload)])

    if (tokenResponse.data.status_code === 200) {
      tokenUsage.value = tokenResponse.data.data || {}
    } else {
      ElMessage.error(tokenResponse.data.status_message || '加载 Token 统计失败')
    }

    if (countResponse.data.status_code === 200) {
      usageCount.value = countResponse.data.data || {}
    } else {
      ElMessage.error(countResponse.data.status_message || '加载调用统计失败')
    }
  } catch (error) {
    console.error('加载数据看板失败:', error)
    ElMessage.error('加载数据看板失败')
  } finally {
    loading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadMeta(), loadDashboard()])
}

onMounted(refreshAll)
</script>

<template>
  <div class="dashboard-page">
    <section class="page-header">
      <div>
        <h1>数据看板</h1>
      </div>

      <div class="filter-bar">
        <img :src="filterIcon" alt="" class="filter-icon" />
        <el-select v-model="filters.model" clearable placeholder="全部模型" class="filter-item" @change="loadDashboard">
          <el-option label="全部模型" value="" />
          <el-option v-for="item in models" :key="item" :label="item" :value="item" />
        </el-select>

        <el-select v-model="filters.agent" clearable placeholder="全部智能体" class="filter-item" @change="loadDashboard">
          <el-option label="全部智能体" value="" />
          <el-option v-for="item in visibleAgents" :key="item" :label="item" :value="item" />
        </el-select>

        <el-select v-model="filters.delta_days" class="filter-item" @change="loadDashboard">
          <el-option label="最近 7 天" :value="7" />
          <el-option label="最近 30 天" :value="30" />
          <el-option label="最近 365 天" :value="365" />
          <el-option label="全部时间" :value="10000" />
        </el-select>
      </div>
    </section>

    <section class="kpi-grid" v-loading="loading">
      <article v-for="item in kpiCards" :key="item.label" class="kpi-card">
        <img :src="item.icon" alt="" class="kpi-icon" />
        <span class="kpi-label">{{ item.label }}</span>
        <strong>{{ formatNumber(item.value) }}</strong>
        <small>{{ periodText }}</small>
      </article>
    </section>

    <section class="content-grid">
      <article class="panel-card trend-panel">
        <div class="panel-head">
          <div class="panel-title">
            <img :src="trendIcon" alt="" class="panel-icon" />
            <h2>趋势</h2>
          </div>
          <span>{{ periodText }}</span>
        </div>
        <div v-if="usageRows.length" class="trend-list">
          <div v-for="row in usageRows.slice().reverse()" :key="row.date" class="trend-row">
            <span>{{ row.date.slice(5) }}</span>
            <div class="trend-track">
              <i :style="{ width: getPercent(row.total, maxDailyTotal) }" />
            </div>
            <strong>{{ formatNumber(row.total) }}</strong>
          </div>
        </div>
        <div v-else class="empty-panel">
          <img :src="emptyIcon" alt="" />
          <span>暂无趋势数据</span>
        </div>
      </article>

      <article class="panel-card detail-panel">
        <div class="panel-head">
          <div class="panel-title">
            <img :src="detailIcon" alt="" class="panel-icon" />
            <h2>最近明细</h2>
          </div>
          <span>按日期汇总</span>
        </div>
        <div v-if="usageRows.length" class="detail-list">
          <div v-for="row in usageRows" :key="row.date" class="detail-row">
            <div class="date-cell">
              <strong>{{ row.date.slice(5) }}</strong>
              <span>{{ row.date.slice(0, 4) }}</span>
            </div>
            <div class="metric-cell">
              <span>调用</span>
              <strong>{{ formatNumber(row.calls) }}</strong>
              <i :style="{ width: getPercent(row.calls, maxDailyCalls) }" />
            </div>
            <div class="metric-cell">
              <span>输入</span>
              <strong>{{ formatNumber(row.input) }}</strong>
            </div>
            <div class="metric-cell">
              <span>输出</span>
              <strong>{{ formatNumber(row.output) }}</strong>
            </div>
            <div class="metric-cell total">
              <span>总量</span>
              <strong>{{ formatNumber(row.total) }}</strong>
              <i :style="{ width: getPercent(row.total, maxDailyTotal) }" />
            </div>
          </div>
        </div>
        <div v-else class="empty-panel">
          <img :src="emptyIcon" alt="" />
          <span>暂无明细数据</span>
        </div>
      </article>

      <article class="panel-card model-rank-panel">
        <div class="panel-head">
          <div class="panel-title">
            <img :src="modelRankIcon" alt="" class="panel-icon" />
            <h2>模型排行</h2>
          </div>
          <span>按总 Token</span>
        </div>
        <div v-if="topModels.length" class="rank-list">
          <div v-for="(item, index) in topModels" :key="item.name" class="rank-item">
            <div class="rank-line">
              <span class="rank-index">{{ index + 1 }}</span>
              <span class="rank-name">{{ item.name }}</span>
              <strong>{{ formatNumber(item.total) }}</strong>
            </div>
            <i :style="{ width: getPercent(item.total, maxModelTotal) }" />
          </div>
        </div>
        <div v-else class="empty-panel">
          <img :src="emptyIcon" alt="" />
          <span>暂无模型数据</span>
        </div>
      </article>

      <article class="panel-card agent-rank-panel">
        <div class="panel-head">
          <div class="panel-title">
            <img :src="agentRankIcon" alt="" class="panel-icon" />
            <h2>智能体排行</h2>
          </div>
          <span>按调用次数</span>
        </div>
        <div v-if="topAgents.length" class="rank-list">
          <div v-for="(item, index) in topAgents" :key="item.name" class="rank-item">
            <div class="rank-line">
              <span class="rank-index">{{ index + 1 }}</span>
              <span class="rank-name">{{ item.name }}</span>
              <strong>{{ formatNumber(item.total) }}</strong>
            </div>
            <i :style="{ width: getPercent(item.total, maxAgentTotal) }" />
          </div>
        </div>
        <div v-else class="empty-panel">
          <img :src="emptyIcon" alt="" />
          <span>暂无智能体数据</span>
        </div>
      </article>
    </section>
  </div>
</template>

<style scoped lang="scss">
.dashboard-page {
  min-height: 100%;
  display: grid;
  gap: 14px;
  padding: 24px;
  background: transparent;
}

.page-header,
.panel-card,
.kpi-card {
  border-radius: 18px;
  border: 1px solid rgba(226, 232, 240, 0.78);
  background: rgba(255, 255, 255, 0.58);
  box-shadow: 0 16px 42px -34px rgba(15, 23, 42, 0.28);
  backdrop-filter: blur(16px);
}

.page-header {
  padding: 0 0 8px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px 16px;
  align-items: center;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}

.page-header h1,
.panel-head h2 {
  margin: 0;
  color: #0f172a;
}

.page-header p,
.panel-head span {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 12px;
}

.filter-bar {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 22px repeat(3, minmax(0, 1fr));
  gap: 8px;
  align-items: center;
  padding-top: 2px;
}

.filter-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
}

.filter-item { width: 100%; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
}

.kpi-card {
  position: relative;
  min-height: 86px;
  padding: 12px 12px 10px 46px;
  display: grid;
  gap: 4px;
  align-content: center;
  overflow: hidden;
}

.kpi-icon {
  position: absolute;
  left: 13px;
  top: 14px;
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.kpi-label { color: #64748b; font-size: 11px; }
.kpi-card strong { font-size: 21px; line-height: 1; color: #0f172a; letter-spacing: 0; }
.kpi-card small { color: #94a3b8; font-size: 10px; }

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 1.45fr);
  grid-template-areas:
    "trend detail"
    "model detail"
    "agent detail";
  grid-auto-rows: minmax(116px, auto);
  gap: 10px;
  align-items: stretch;
}

.panel-card { padding: 12px; }

.trend-panel {
  grid-area: trend;
}

.detail-panel {
  grid-area: detail;
  min-height: 100%;
}

.model-rank-panel {
  grid-area: model;
}

.agent-rank-panel {
  grid-area: agent;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 10px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.panel-icon {
  width: 21px;
  height: 21px;
  object-fit: contain;
}

.panel-head h2 {
  font-size: 15px;
  font-weight: 680;
}

.trend-list,
.detail-list,
.rank-list {
  display: grid;
  gap: 6px;
}

.trend-row {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr) 72px;
  gap: 8px;
  align-items: center;
  min-height: 24px;
  color: #64748b;
  font-size: 11px;
}

.trend-row strong {
  justify-self: end;
  color: #334155;
  font-size: 11px;
}

.trend-track,
.metric-cell i,
.rank-item i {
  position: relative;
  height: 4px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.08);
}

.trend-track i,
.metric-cell i,
.rank-item i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.86), rgba(217, 119, 6, 0.48));
}

.detail-row {
  display: grid;
  grid-template-columns: 64px repeat(4, minmax(0, 1fr));
  gap: 8px;
  align-items: center;
  min-height: 38px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.detail-row:last-child {
  border-bottom: 0;
}

.date-cell,
.metric-cell {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.date-cell strong,
.metric-cell strong {
  color: #0f172a;
  font-size: 12px;
  line-height: 1.2;
}

.date-cell span,
.metric-cell span {
  color: #94a3b8;
  font-size: 10px;
  line-height: 1.2;
}

.metric-cell i {
  width: 100%;
  margin-top: 2px;
}

.rank-item {
  display: grid;
  gap: 5px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}

.rank-item:last-child {
  border-bottom: 0;
}

.rank-line {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rank-index {
  width: 18px;
  height: 18px;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
  font-size: 10px;
  font-weight: 650;
}

.rank-name {
  flex: 1 1 auto;
  min-width: 0;
  color: #334155;
  font-size: 11.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-line strong {
  flex: 0 0 auto;
  color: #0f172a;
  font-size: 11.5px;
}

.empty-panel {
  min-height: 82px;
  display: grid;
  place-items: center;
  gap: 4px;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  color: #94a3b8;
  font-size: 11px;
}

.empty-panel img {
  width: 34px;
  height: 34px;
  object-fit: contain;
  opacity: 0.72;
}

@media (max-width: 1280px) {
  .content-grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "trend"
      "detail"
      "model"
      "agent";
    grid-auto-rows: auto;
  }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 720px) {
  .dashboard-page { padding: 16px; }
  .page-header { grid-template-columns: 1fr; }
  .filter-bar { grid-template-columns: 1fr; }
  .filter-icon { display: none; }
  .filter-item { width: 100%; }
  .kpi-grid { grid-template-columns: 1fr; }
  .detail-row { grid-template-columns: 1fr 1fr; }
}
</style>
