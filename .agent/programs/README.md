# Agent 执行计划

`.agent/programs/` 当前保存 active program：`zuno-target-architecture-runtime-full-implementation-v1`。

## 当前状态

- State: active
- Active program: `zuno-target-architecture-runtime-full-implementation-v1`
- Current phase: `PHASE04_document-ingestion-parse-runtime`
- 最近完成 program: `zuno-master-architecture-implementation-v1`
- 最近完成归档: `docs/history/programs/zuno-master-architecture-implementation-v1/`

## 本轮目标

本 program 不是继续细化架构，也不是再做一轮 contract foundation。它的目标是在不推翻现有目标架构的前提下，把 Zuno 做成可运行、可观察、可评测、可交付的完整目标架构第一版。

核心 vertical slice：

```text
上传文档
  -> parse
  -> index
  -> ask
  -> Agentic retrieval
  -> cited answer
  -> trace/eval
  -> artifact/feedback
```

只有真实 runtime 路径、API / UI 入口、trace、eval 或 verifier 证明的能力才能进入 Current。只写 contract、schema 或 README 不能关闭 runtime phase。

## 使用规则

- 每个 phase 从 `PHASE01` 顺序推进。
- 每个 phase 结束前必须有最小有效验证、commit 和 push，除非验证或 push 被阻塞。
- 不把 production runtime、Memory DB、sandbox、LangSmith sink、online eval 或 UI 闭环写成 Current，除非它们已经真实跑通并有测试 / trace / eval 证据。
- 执行工作流可以用多线程和多 agent；Zuno 产品 runtime 近期仍是 Single Controller Agent，不改成默认多 Agent 架构。
