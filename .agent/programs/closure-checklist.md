# zuno-target-architecture-runtime-full-implementation-v1 Closure Checklist

## Program Closure 自维护审查

- [ ] `AGENTS.md` 是否仍准确描述 active program、工作模式和收尾规则。
- [ ] `.agent/system.yaml` 的 docs_sync、verify 和 route 是否覆盖本 program。
- [ ] `.agent/references/current-program.md` 是否记录 active / completed / remaining Target 边界。
- [ ] `.agent/references/workflow.md`、workflow change log 或 known pitfalls 是否沉淀本轮发现。
- [ ] `.agent/programs/` 是否只保留当前 active program，或在 PHASE12 后进入 no-active 等待态。
- [ ] completed program 是否已归档到 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。
- [ ] `docs/architecture/architecture.md` 是否只把真实证明的能力写入 Current。
- [ ] `.agent/architecture/architecture.md` 是否与 `docs/architecture/architecture.md` 完全一致。
- [ ] 两个 `architecture.html` 是否由同一个 Markdown 源生成并通过 `render_architecture.py --check`。
- [ ] verifier / tests 是否覆盖 runtime-first 验收口径，避免下一轮退回 contract-only closure。

## Runtime E2E Release Gate

- [ ] 上传文档。
- [ ] parse 成 Canonical Document IR。
- [ ] 生成可追踪 chunk / provenance / ACL。
- [ ] 写入 BM25 / vector / graph 至少一种真实可查询 index。
- [ ] 创建 task 并产生 task / session / trace id。
- [ ] Single Controller runtime 执行 plan / retrieval / evidence check / answer。
- [ ] 输出 citation-rich answer。
- [ ] 生成 artifact 或 report。
- [ ] 写入 ZunoSpan / eval baseline。
- [ ] 前端或 API 可提交 feedback。
- [ ] release evidence 能从 task 回放到 source document block。

## 禁止关闭条件

- [ ] 不能只因新增 contract、type 或 README 就关闭 runtime phase。
- [ ] 不能把 Target/Future 写成 Current。
- [ ] 不能删除兼容路径来制造“目录清爽”。
- [ ] 不能跳过 focused tests、verifier、trace 或 eval evidence。

