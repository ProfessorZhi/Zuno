# 当前程序

当前可执行 Agent 程序是：

- `.agent/programs/`

当前 program 是 `zuno-architecture-surface-cleanup-v1`。它接在目标运行时第一轮 slice 之后，目标不是继续堆 feature，而是成熟项目封面化、分层目录落地、本地 Agent Skill System 收口、tools/tests 防回归和架构图展示。

后续执行顺序必须线性推进：

```text
PHASE01：公开封面与架构叙事收口（已完成）
PHASE02：本地 Agent Skill System 收口（已完成）
PHASE03：tools / tests 工作流防回归（已完成）
PHASE04：后端六层 facade 分层（当前待打开）
PHASE05：大文件轻拆
PHASE06：架构图与 HTML 展示页
```

当前执行焦点是 PHASE04。PHASE05 只能先做只读拆分审计和计划，PHASE06 可以并行做架构图/HTML 展示页，但主线程必须负责最终合并和集成验证。

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

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE01_public-architecture-surface.md`
- `.agent/programs/PHASE02_local-agent-skill-system.md`
- `.agent/programs/PHASE03_tools-tests-guardrails.md`
- `.agent/programs/PHASE04_backend-facade-layers.md`
- `.agent/programs/PHASE05_large-file-light-split.md`
- `.agent/programs/PHASE06_architecture-diagrams-html.md`
- `.agent/programs/closure-checklist.md`
- `docs/history/programs/zuno-target-runtime-v2/`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md`
- `docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md`
- `docs/history/programs/official-graphrag-cleanup-v1/implementation-phases/`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。不要把旧 active Phase 05-09 恢复到 `.agent/programs/` 当前前台；它们只属于 history。
