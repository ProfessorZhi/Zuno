<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import {
  getUsageStatsAPI,
  getUsageCountAPI,
  getUsageModelsAPI,
  getUsageAgentsAPI,
  type UsageStatsRequest,
  type UsageDataByDate,
  type UsageCountByDate,
} from '../../apis/usage-stats'

const loading = ref(false)
const models = ref<string[]>([])
const agents = ref<string[]>([])
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

const loadMeta = async () => {
  try {
    const [modelResponse, agentResponse] = await Promise.all([getUsageModelsAPI(), getUsageAgentsAPI()])
    if (modelResponse.data.status_code === 200) models.value = modelResponse.data.data || []
    if (agentResponse.data.status_code === 200) agents.value = agentResponse.data.data || []
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
        <p>把模型调用量、Token 消耗和活跃智能体收拢到一页，方便你快速判断哪里在吃资源。</p>
      </div>

      <div class="filter-bar">
        <el-select v-model="filters.model" clearable placeholder="全部模型" class="filter-item" @change="loadDashboard">
          <el-option label="全部模型" value="" />
          <el-option v-for="item in models" :key="item" :label="item" :value="item" />
        </el-select>

        <el-select v-model="filters.agent" clearable placeholder="全部智能体" class="filter-item" @change="loadDashboard">
          <el-option label="全部智能体" value="" />
          <el-option v-for="item in agents" :key="item" :label="item" :value="item" />
        </el-select>

        <el-select v-model="filters.delta_days" class="filter-item" @change="loadDashboard">
          <el-option label="最近 7 天" :value="7" />
          <el-option label="最近 30 天" :value="30" />
          <el-option label="最近 365 天" :value="365" />
          <el-option label="全部时间" :value="10000" />
        </el-select>

        <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>
      </div>
    </section>

    <section class="kpi-grid" v-loading="loading">
      <article class="kpi-card">
        <span class="kpi-label">调用次数</span>
        <strong>{{ formatNumber(totalCalls) }}</strong>
        <small>{{ periodText }}</small>
      </article>
      <article class="kpi-card">
        <span class="kpi-label">输入 Token</span>
        <strong>{{ formatNumber(totalInputTokens) }}</strong>
        <small>{{ periodText }}</small>
      </article>
      <article class="kpi-card">
        <span class="kpi-label">输出 Token</span>
        <strong>{{ formatNumber(totalOutputTokens) }}</strong>
        <small>{{ periodText }}</small>
      </article>
      <article class="kpi-card">
        <span class="kpi-label">总 Token</span>
        <strong>{{ formatNumber(totalTokens) }}</strong>
        <small>{{ periodText }}</small>
      </article>
    </section>

    <section class="content-grid">
      <article class="panel-card">
        <div class="panel-head">
          <h2>最近明细</h2>
          <span>按日期汇总</span>
        </div>

        <el-table :data="usageRows" empty-text="暂无统计数据">
          <el-table-column prop="date" label="日期" min-width="140" />
          <el-table-column prop="calls" label="调用次数" min-width="120">
            <template #default="{ row }">{{ formatNumber(row.calls) }}</template>
          </el-table-column>
          <el-table-column prop="input" label="输入 Token" min-width="130">
            <template #default="{ row }">{{ formatNumber(row.input) }}</template>
          </el-table-column>
          <el-table-column prop="output" label="输出 Token" min-width="130">
            <template #default="{ row }">{{ formatNumber(row.output) }}</template>
          </el-table-column>
          <el-table-column prop="total" label="总 Token" min-width="130">
            <template #default="{ row }">{{ formatNumber(row.total) }}</template>
          </el-table-column>
        </el-table>
      </article>

      <article class="panel-card">
        <div class="panel-head">
          <h2>模型排行</h2>
          <span>按总 Token</span>
        </div>
        <div v-if="topModels.length" class="rank-list">
          <div v-for="item in topModels" :key="item.name" class="rank-item">
            <span class="rank-name">{{ item.name }}</span>
            <strong>{{ formatNumber(item.total) }}</strong>
          </div>
        </div>
        <el-empty v-else description="暂无模型数据" />
      </article>

      <article class="panel-card">
        <div class="panel-head">
          <h2>智能体排行</h2>
          <span>按调用次数</span>
        </div>
        <div v-if="topAgents.length" class="rank-list">
          <div v-for="item in topAgents" :key="item.name" class="rank-item">
            <span class="rank-name">{{ item.name }}</span>
            <strong>{{ formatNumber(item.total) }}</strong>
          </div>
        </div>
        <el-empty v-else description="暂无智能体数据" />
      </article>
    </section>
  </div>
</template>

<style scoped lang="scss">
.dashboard-page {
  min-height: 100%;
  display: grid;
  gap: 20px;
  padding: 24px;
  background: linear-gradient(180deg, #f7f2ea 0%, #fbf8f3 100%);
}

.page-header,
.panel-card,
.kpi-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 18px 36px rgba(120, 80, 42, 0.08);
}

.page-header {
  padding: 24px 26px;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.page-header h1,
.panel-head h2 {
  margin: 0;
  color: #2f241b;
}

.page-header p,
.panel-head span {
  margin: 8px 0 0;
  color: #786657;
}

.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.filter-item { width: 180px; }

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.kpi-card {
  padding: 22px;
  display: grid;
  gap: 10px;
}

.kpi-label { color: #8a7869; font-size: 14px; }
.kpi-card strong { font-size: 32px; line-height: 1; color: #34261d; }
.kpi-card small { color: #a08f81; }

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 1fr) minmax(320px, 1fr);
  gap: 16px;
}

.panel-card { padding: 20px; }
.panel-head { margin-bottom: 16px; }

.rank-list { display: grid; gap: 12px; }

.rank-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 16px;
  background: linear-gradient(180deg, #fffdf9 0%, #fff8f0 100%);
  border: 1px solid rgba(214, 132, 70, 0.1);
}

.rank-name { color: #4a392d; word-break: break-all; }

@media (max-width: 1280px) {
  .content-grid { grid-template-columns: 1fr; }
  .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 720px) {
  .dashboard-page { padding: 16px; }
  .page-header { flex-direction: column; }
  .filter-bar { width: 100%; justify-content: stretch; }
  .filter-item { width: 100%; }
  .kpi-grid { grid-template-columns: 1fr; }
}
</style>
