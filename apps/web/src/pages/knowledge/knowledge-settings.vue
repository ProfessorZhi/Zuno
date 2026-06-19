<template>
  <div class="knowledge-settings-page">
    <section class="hero-card">
      <p class="eyebrow">知识库维护页</p>
      <h1>把查询参数、索引状态和重建动作放到同一页里看清楚</h1>
    </section>

    <section class="status-grid">
      <article class="status-card">
        <strong>文本索引</strong>
        <p>Embedding 变化后需要重建文本索引。</p>
      </article>
      <article class="status-card">
        <strong>BM25</strong>
        <p>默认开启，关键词检索作为稳定兜底链路。</p>
      </article>
      <article class="status-card">
        <strong>图谱索引</strong>
        <p>领域包 schema 或抽取策略变化后更新图谱。</p>
      </article>
      <article class="status-card">
        <strong>社区发现</strong>
        <p>Community GraphRAG 只在增强检索链路里作为全局层能力。</p>
      </article>
      <article class="status-card">
        <strong>社区报告</strong>
        <p>当社区数据过期时，可单独重新生成社区报告。</p>
      </article>
    </section>

    <section class="action-panel">
      <h2>可执行动作</h2>
      <div class="action-row">
        <button type="button">保存配置</button>
        <button type="button">重建文本索引</button>
        <button type="button">更新图谱</button>
        <button type="button">重新发现社区</button>
        <button type="button">重新生成社区报告</button>
        <button type="button">完整重建</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.knowledge-settings-page {
  display: grid;
  gap: 18px;
  padding: 24px;
}

.hero-card,
.status-card,
.action-panel {
  padding: 22px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.96);
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

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.status-card strong {
  color: #5f3518;
}

.status-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

button {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 999px;
  background: rgba(255, 244, 230, 0.94);
  color: #8a4b16;
}
</style>
