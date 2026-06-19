<template>
  <div class="domain-pack-create-page">
    <section class="hero-card">
      <p class="eyebrow">领域包构建页</p>
      <h1>先用代表性文件生成草稿，再人工审核后发布</h1>
    </section>

    <section class="panel">
      <h2>创建新的领域包</h2>
      <div class="grid">
        <article class="card">
          <strong>代表性文件</strong>
          <p>从上传样本或已有知识库中挑代表性文件生成草稿，不直接改动正式知识库。</p>
        </article>
        <article class="card">
          <strong>审核 schema / prompt</strong>
          <p>审核实体、关系、extraction prompt、retrieval policy、community report prompt。</p>
        </article>
        <article class="card">
          <strong>发布领域包</strong>
          <p>确认后发布一个可绑定到多个知识库的领域包版本。</p>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped>
.domain-pack-create-page {
  display: grid;
  gap: 18px;
  padding: 24px;
}

.hero-card,
.panel,
.card {
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.card strong {
  color: #5f3518;
}

.card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}
</style>
