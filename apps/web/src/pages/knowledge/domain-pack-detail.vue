<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import {
  getDomainPackDetailAPI,
  publishDomainPackAPI,
  type DomainPackDetail,
} from '../../apis/domain-packs'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const publishing = ref(false)
const detail = ref<DomainPackDetail | null>(null)
const packId = () => String(route.params.packId || '')

const loadDetail = async () => {
  loading.value = true
  try {
    const response = await getDomainPackDetailAPI(packId())
    if (response.data.status_code === 200) {
      detail.value = response.data.data || null
      return
    }
    ElMessage.error(response.data.status_message || '加载领域包详情失败')
  } catch (error) {
    console.error('加载领域包详情失败', error)
    ElMessage.error('加载领域包详情失败')
  } finally {
    loading.value = false
  }
}

const publish = async () => {
  publishing.value = true
  try {
    const response = await publishDomainPackAPI(packId())
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '发布领域包失败')
    }
    ElMessage.success('领域包已发布')
    await loadDetail()
  } catch (error) {
    console.error('发布领域包失败', error)
    ElMessage.error(error instanceof Error ? error.message : '发布领域包失败')
  } finally {
    publishing.value = false
  }
}

const usePack = () => {
  const returnTo = String(route.query.returnTo || '')
  const query = {
    ...route.query,
    domain_pack_id: detail.value?.pack_id || packId(),
    settings_turn: String(Date.now()),
  }
  if (returnTo === 'knowledge-settings' && route.query.knowledge_id) {
    router.push({
      name: 'workspaceSettingsKnowledgeSettings',
      params: { knowledgeId: String(route.query.knowledge_id) },
      query,
    })
    return
  }
  router.push({
    name: 'workspaceSettingsKnowledgeCreate',
    query,
  })
}

onMounted(loadDetail)
</script>

<template>
  <div class="domain-pack-detail-page">
    <section class="hero-card" v-loading="loading">
      <p class="eyebrow">领域包详情</p>
      <h1>{{ detail?.name || packId() }}</h1>
      <p>{{ detail?.description || '这里展示领域包本体，不直接代替知识库维护页。' }}</p>
      <div class="meta-row">
        <span>{{ detail?.status === 'published' ? '已发布' : '草稿' }}</span>
        <span>{{ detail?.version || '未设置版本' }}</span>
        <span>{{ detail?.pack_id || packId() }}</span>
      </div>
      <div class="action-row">
        <button type="button" :disabled="publishing" @click="publish">
          {{ publishing ? '发布中...' : '发布领域包' }}
        </button>
        <button type="button" @click="usePack">绑定到知识库</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.domain-pack-detail-page {
  padding: 24px;
  min-width: 0;
}

.hero-card {
  padding: 22px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.96);
  min-width: 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: #a16207;
  font-size: 12px;
}

h1,
p {
  margin: 0;
}

p {
  margin-top: 10px;
  color: #7c6b5c;
  line-height: 1.6;
}

.meta-row,
.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.meta-row span {
  padding: 4px 10px;
  border-radius: 999px;
  background: #fff4e6;
  color: #8a4b16;
  font-size: 12px;
}

button {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 999px;
  background: rgba(255, 244, 230, 0.94);
  color: #8a4b16;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.56;
}

@media (max-width: 1199px) {
  .domain-pack-detail-page {
    padding: 18px;
  }
}

@media (max-width: 767px) {
  .domain-pack-detail-page {
    padding: 0;
  }

  .hero-card {
    padding: 18px;
    border-radius: 18px;
  }

  h1 {
    font-size: 21px;
    line-height: 1.25;
  }

  .action-row {
    display: grid;
  }

  button {
    width: 100%;
  }
}
</style>
