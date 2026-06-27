# 当前程序

当前可执行 Agent 程序是：

- `.agent/programs/zuno-target-runtime-v2/`

这个程序是在 Zuno Target Architecture Migration V1 收口后的受控首个实现切片。它打开模块边界闸门，迁移一个低风险后端应用边界，并引入最小可调用 Context Orchestrator。

后续执行顺序必须线性推进：

```text
Phase 05：记忆引擎
Phase 06 Capability / Tool Retrieval
Phase 07 Knowledge Retrieval / Fusion
Phase 08 GeneralAgent LangGraph Runtime
Phase 09：产品边界、Trace 与 Eval 收口
```

最新完成程序：

- `docs/history/programs/zuno-target-architecture-migration-v1/`

面向人的正式状态见：

- `docs/architecture/roadmap.md`

## 为什么保留归档程序

之前的 Phase 0-6 closure 已完成，是历史事实。

已完成工作从已证明的 11A/11B runtime 状态推进到目标架构和目标仓库布局，并完成 official GraphRAG cleanup 11C/12，再进入 Context/Memory 与 Capability 实现阶段。

## 已完成状态

- Target Migration Phase 00 已完成。
- Phase 01 active runtime cleanup 已完成。
- Official cleanup Phase 11A 和 11B 已完成。
- Official cleanup Phase 11C active runtime cleanup 已关闭。受限 migration aliases 只保留在 storage/eval/DB compatibility 等测试语境中。
- 旧 `tests/compat/` holding area 已退休。
- root `domain-packs/` 资产已归档到 `docs/history/domain-packs/root-contract-review/`。
- `DomainQAGraph` 后端源码和 `src/backend/zuno/services/domain_pack/` runtime service package 已从当前后端移除。
- Contract Review assets 保留为 GraphRAG Project / eval 证据，不再代表 active Domain Pack 主线。

## 当前参考文件

- `.agent/programs/zuno-target-runtime-v2/README.md`
- `.agent/programs/zuno-target-runtime-v2/implementation-roadmap.md`
- `.agent/programs/zuno-target-runtime-v2/current-phase.md`
- `.agent/programs/zuno-target-runtime-v2/closure-checklist.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。
