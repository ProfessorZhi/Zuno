<template>
  <div class="domain-pack-page">
    <section class="hero-card">
      <p class="eyebrow">领域包</p>
      <h1>领域包是独立资源，知识库只负责绑定它</h1>
      <p>这里集中管理已发布模板、草稿状态，以及从知识库回跳创建新的领域包的入口。</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>领域包列表</h2>
        <button type="button">创建新的领域包</button>
      </div>
      <article class="pack-card">
        <strong>contract_review</strong>
        <p>合同审查模板，包含 schema、retrieval policy 和 report prompt。</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.domain-pack-page {
  display: grid;
  gap: 18px;
  padding: 24px;
}

.hero-card,
.panel,
.pack-card {
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
}

.pack-card strong {
  color: #5f3518;
}

.pack-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}
</style>
