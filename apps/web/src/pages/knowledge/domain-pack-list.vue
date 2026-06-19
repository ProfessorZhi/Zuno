<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { getDomainPacksAPI, type DomainPackSummary } from '../../apis/domain-packs'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const domainPacks = ref<DomainPackSummary[]>([])

const buildSettingsQuery = () => ({
  ...route.query,
  settings_turn: String(Date.now()),
})

const openCreate = () => {
  router.push({
    name: 'workspaceSettingsKnowledgeDomainPackCreate',
    query: buildSettingsQuery(),
  })
}

const openDetail = (packId: string) => {
  router.push({
    name: 'workspaceSettingsKnowledgeDomainPackDetail',
    params: { packId },
    query: buildSettingsQuery(),
  })
}

const loadDomainPacks = async () => {
  loading.value = true
  try {
    const response = await getDomainPacksAPI()
    if (response.data.status_code === 200) {
      domainPacks.value = response.data.data || []
      return
    }
    ElMessage.error(response.data.status_message || '加载领域包失败')
  } catch (error) {
    console.error('加载领域包失败', error)
    ElMessage.error('加载领域包失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadDomainPacks)
</script>

<template>
  <div class="domain-pack-page">
    <section class="hero-card">
      <p class="eyebrow">领域包</p>
      <h1>领域包是独立资源，知识库只负责绑定它</h1>
      <p>这里集中管理已发布模板、草稿状态，以及从知识库回跳创建新的领域包的入口。</p>
    </section>

    <section class="panel" v-loading="loading">
      <div class="panel-head">
        <h2>领域包列表</h2>
        <button type="button" @click="openCreate">创建新的领域包</button>
      </div>
      <p v-if="!domainPacks.length && !loading" class="empty-copy">还没有领域包，先创建草稿再发布。</p>
      <button
        v-for="pack in domainPacks"
        :key="pack.pack_id"
        type="button"
        class="pack-card"
        :title="`查看 ${pack.name} 领域包`"
        @click="openDetail(pack.pack_id)"
      >
        <span class="pack-status" :class="pack.status">{{ pack.status === 'published' ? '已发布' : '草稿' }}</span>
        <strong>{{ pack.name || pack.pack_id }}</strong>
        <p>{{ pack.description || '这个领域包还没有说明。' }}</p>
        <small>{{ pack.pack_id }}<template v-if="pack.version"> · {{ pack.version }}</template></small>
      </button>
    </section>
  </div>
</template>

<style scoped>
.domain-pack-page {
  display: grid;
  gap: 18px;
  padding: 24px;
  min-width: 0;
}

.hero-card,
.panel,
.pack-card {
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
h2,
p {
  margin: 0;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

button {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 999px;
  background: rgba(255, 244, 230, 0.94);
  color: #8a4b16;
}

.pack-card {
  margin-top: 14px;
  width: 100%;
  min-height: auto;
  padding: 22px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.96);
  text-align: left;
  cursor: pointer;
  color: inherit;
}

.pack-card strong {
  color: #5f3518;
}

.pack-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.pack-card small,
.empty-copy {
  display: block;
  margin-top: 10px;
  color: #9a7a60;
}

.pack-status {
  display: inline-flex;
  margin-bottom: 10px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #fff4e6;
  color: #9a4f12;
  font-size: 12px;
}

.pack-status.published {
  background: #ecfdf3;
  color: #28714b;
}

@media (max-width: 1199px) {
  .domain-pack-page {
    padding: 18px;
  }
}

@media (max-width: 767px) {
  .domain-pack-page {
    gap: 14px;
    padding: 0;
  }

  .hero-card,
  .panel,
  .pack-card {
    padding: 18px;
    border-radius: 18px;
  }

  .panel-head {
    align-items: stretch;
    flex-direction: column;
  }

  button {
    width: 100%;
  }
}
</style>
