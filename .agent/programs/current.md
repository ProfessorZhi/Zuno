# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## 当前状态

`.agent/programs/` 当前没有 active program。最近完成并归档的是：

- `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`

成熟度和 runtime-first 交付物边界仍以 `docs/architecture/production-readiness.md` 为准。

完成结论：

```text
Evidence-span Agentic GraphRAG hardening baseline completed.
Release gate output surface is available.
Fixed EnterpriseRAG measured pass remains blocked by incomplete local agentic profile run.
```

## 最近完成边界

- 最近完成 program 的 phase 文件已完整归档。
- 已完成 failure bucket 诊断、source span provenance、citation-sized chunks、lexical / phrase evidence retrieval、graph evidence lineage、evidence-aware reranker、claim-level citation binder、hard negative coverage 和 release gate 输出面。
- 两次真实本地 EnterpriseRAG paired eval 尝试未完成 agentic profile，因此没有 measured pass；不得把 blocked run 写成 measured。
- 后续如继续 evidence-span hardening，必须新开 program 或明确重开 phase。

## 前台文件

no-active 状态下，`.agent/programs/` 根目录保留：

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/README.md`

平铺 `PHASE*.md` 文件已归档到 `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`，前台不保留 active phase 文件。
