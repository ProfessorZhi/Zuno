# 当前程序

state: active
active_program: zuno-lean-complete-product-architecture-v1
current_phase: PHASE04_docs-sync-verification-and-closure
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## 当前目标

本轮只重写 Zuno 的架构事实源和展示面，把近期目标范围从旧的 4+1 / View & Beyond 十图和过重 Production Scale 口径，收缩为 Lean Complete Agentic GraphRAG Product：

- 6 个 runtime domain。
- 1 条用户可完成任务的 golden path。
- 4 张 Mermaid 架构图和同步 HTML 展示页。
- 短期 P0 / P1 / P2 闭环清单。
- Production Scale、外部分布式中间件、外部图/向量库、OCR/VLM、在线 eval 和产品级多 Agent runtime 全部降级为 Future Optional。
- `docs/architecture/architecture.md` 保持详细、规范、可实施，继续作为后续 Program 规划事实源。

## 严格边界

- 本 program 只做 architecture / docs / renderer / verifier / tests 同步。
- 不修改核心 runtime 逻辑。
- 不把文档重写写成 runtime 质量提升。
- 不把 `architecture.md` 改成宣传页，不删除 owner、contract、数据流、控制流、配置、持久化、失败、观测、测试和验收要求。
- 不把 Agentic GraphRAG fixed benchmark、release gate 或质量门写成已经通过。
- 不把 blocked / prepared / implementation available 写成 measured。

## 当前 phase

PHASE04 负责完成验证、归档 program、恢复 no-active、提交并推送。

后续 phase：

1. PHASE02_lean-architecture-markdown
2. PHASE03_four-diagram-html-and-guardrails
3. PHASE04_docs-sync-verification-and-closure
