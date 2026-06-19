<script setup lang="ts">
const retrievalModes = [
  {
    title: '标准检索',
    subtitle: '普通文档问答、FAQ、具体内容查找',
  },
  {
    title: '增强检索',
    subtitle: '关系推理、跨文档分析、图谱增强问答',
  },
]
</script>

<template>
  <div class="knowledge-create-page">
    <section class="hero-card">
      <p class="eyebrow">知识库创建向导</p>
      <h1>先选产品模式，再决定模型、Domain Pack 和构建计划</h1>
      <p class="copy">
        这里把知识库创建和后续参数维护拆开。创建时只做一次性的构建决策，后续调参放到维护页。
      </p>
    </section>

    <section class="panel">
      <h2>1. 选择检索模式</h2>
      <div class="mode-grid">
        <article v-for="item in retrievalModes" :key="item.title" class="mode-card">
          <strong>{{ item.title }}</strong>
          <p>{{ item.subtitle }}</p>
        </article>
      </div>
    </section>

    <section class="panel form-panel">
      <h2>2. 选择索引与领域模板</h2>
      <div class="form-grid">
        <label>
          <span>Embedding</span>
          <input type="text" placeholder="选择文本 / 多模态 Embedding" />
        </label>
        <label>
          <span>Rerank</span>
          <input type="text" placeholder="选择排序模型" />
        </label>
        <label>
          <span>Domain Pack</span>
          <input type="text" placeholder="选择已发布领域包，或跳转创建新的领域包" />
        </label>
        <label>
          <span>构建计划</span>
          <input type="text" placeholder="上传文件后预览文本索引、图谱索引、社区能力开关" />
        </label>
      </div>
    </section>
  </div>
</template>

<style scoped>
.knowledge-create-page {
  display: grid;
  gap: 18px;
  padding: 24px;
}

.hero-card,
.panel {
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

h1 {
  font-size: 28px;
  color: #171717;
}

.copy {
  margin-top: 10px;
  color: #7c6b5c;
  line-height: 1.7;
}

.mode-grid,
.form-grid {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.mode-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.mode-card {
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  background: rgba(255, 248, 240, 0.92);
}

.mode-card strong {
  color: #5f3518;
}

.mode-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.form-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

label {
  display: grid;
  gap: 8px;
}

label span {
  color: #5f3518;
  font-weight: 700;
}

input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 12px;
}
</style>
