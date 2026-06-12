# Architecture Docs

这个目录专门存放 Zuno 的架构文档。

它的目标不是堆很多“想法记录”，而是把下面三件事讲清楚：

1. Zuno 现在的主架构是什么
2. 这套架构为什么这样分层
3. 后面往多 Agent、企业级检索治理、微服务 / 云原生、异语言后端扩展时，边界怎么保持稳定

并且现在还要把第四件事讲清楚：

4. 架构边界和文件夹结构如何对齐，而不是代码一套说法、目录另一套说法

## 目录规则

```text
docs/architecture/
  README.md
  zuno_refactor_plan.md
  specs/
  plans/
  decisions/
```

各目录职责：

- `zuno_refactor_plan.md`
  当前这一轮大改造的总方案，总结“为什么改、先改什么、最后收口到什么”。
- `specs/`
  稳定架构设计文档，描述目标结构、运行边界、治理语义、模块职责。
- `plans/`
  推进顺序、阶段任务、验收方式。这里允许存在阶段性文档，但不应代替稳定 spec。
- `decisions/`
  关键架构决策记录，解释为什么这样做，以及为什么不走别的方案。

## 当前主架构

当前 Zuno 的主线不是“聊天界面 + 若干功能插件”，而是：

```text
本地优先 Agent 工作台
  -> LangGraph runtime
  -> Retrieval Orchestrator
  -> RAG / GraphRAG / BM25 多路检索
  -> Domain Pack 领域扩展
  -> Eval / Trace / Citation / Cost control
```

这套主线当前重点服务的是：

- 合同审查这类强领域问答
- 证据驱动的 RAG / GraphRAG 检索
- 可评测、可治理的 Agent runtime

它还不是完整的企业级多 Agent 平台，也不是已经拆开的微服务系统。
但架构边界必须为这些方向预留空间。

## 当前项目结构判断

当前仓库的主结构已经收口成：

```text
Zuno/
  apps/
    web/
    desktop/
  src/
    backend/
```

这不是为了追求目录命名潮流，而是为了先把三件事收口：

1. 哪些目录是应用入口
2. 哪些目录是核心能力
3. 哪些目录是文档、评测、工具、基础设施

当前这层语义已经比较明确：

- `apps/web`
  Web 工作台应用壳
- `apps/desktop`
  Electron 桌面宿主
- `src/backend`
  真正可导入、可测试、可部署的后端源码域

所以当前正确方向已经不是继续大搬家，而是：

```text
保持 apps + src + infra + tools + tests 的边界稳定，
继续清理历史迁移痕迹和讲解口径
```

## 阶段目标总览

为了避免架构文档只讲“最终蓝图”而不讲“现在到底做到哪一步”，这里把目标拆成四层：

### 当前

当前最重要的是把下面这条主线做实：

- LangGraph 作为主运行时，而不是只用 LangChain 拼一个难以扩展的简单 Agent
- RAG / GraphRAG / BM25 检索主线成立
- 合同审查作为第一个高质量 Domain Pack 场景
- 本地评测、引用、trace、成本控制这些支撑能力存在
- 后端分层和目录边界开始清晰

### 下一步

下一步最值钱的工作不是继续堆功能，而是把治理层补清楚：

- Retrieval Orchestrator、planner、profile、RetrievalPlan 的边界继续收紧
- scope、budget、fallback、citation、index version、index health 等治理语义写清楚
- 文档、目录、README、计划文档入口继续收口，减少历史迁移痕迹对主阅读路径的干扰

### 面试前必须做到

面试前，Zuno 至少要形成一套“说得清、改得动、能证明价值”的架构：

- 架构层清晰，前端 / 后端 / 控制层 / 服务层 / DAO 层 / 基础设施层职责明确
- 代码和文档不要把很多能力写死在单一场景或单一路径里
- LangGraph 深度参与运行时，而不是停留在简单封装层
- RAG / GraphRAG 形成完整主线，并且能用本地评测证明 GraphRAG 和领域建模的价值
- 项目目录、文档、README 达到正式 GitHub 项目可展示状态
- 文件夹结构清楚到可以直接解释“应用入口 / 核心能力 / 评测 / 基础设施 / 发布边界”分别在哪里

### 面试后继续优化

面试后再继续推进这些更长期的方向：

- 更完整的多 Agent 体系
- 更严格的 citation / grounding
- 更完整的索引生命周期治理
- 微服务 / 云原生演进
- 异语言后端接入，例如 Java
- 更强的代码工作台 / 编程 Agent 能力

## 推荐阅读顺序

如果你第一次看这里，建议按这个顺序读：

1. [Zuno Refactor Plan](./zuno_refactor_plan.md)
2. [Domain Pack + LangGraph + GraphRAG Architecture](./specs/domain-pack-langgraph-graphrag-architecture.md)
3. [Retrieval Orchestrator](./specs/retrieval-orchestrator.md)
4. [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
5. [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
6. [Platform Evolution And Future Direction](./specs/platform-evolution-and-future-direction.md)
7. [RAG Evaluation And Observability](./specs/rag-evaluation-and-observability.md)
8. [Current Phase Audit](./plans/current-phase-audit.md)
9. [Retrieval Governance Upgrade Plan](./plans/retrieval-governance-upgrade-plan.md)

如果你只想快速理解“当前系统为什么这样设计”，前五篇就够。

如果你这轮重点是把“项目结构也整理清楚”，额外优先看：

8. [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
9. [Zuno Refactor Execution Plan](./plans/zuno-refactor-execution-plan.md)

## 当前最重要的文档

- [Domain Pack + LangGraph + GraphRAG Architecture](./specs/domain-pack-langgraph-graphrag-architecture.md)
- [Retrieval Orchestrator](./specs/retrieval-orchestrator.md)
- [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
- [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
- [RAG Evaluation And Observability](./specs/rag-evaluation-and-observability.md)
- [LangGraph Runtime](./specs/langgraph-runtime.md)
- [Current Phase Audit](./plans/current-phase-audit.md)
- [Retrieval Governance Upgrade Plan](./plans/retrieval-governance-upgrade-plan.md)

如果只想抓主线，优先看前五篇：

1. `zuno_refactor_plan.md`
2. `specs/domain-pack-langgraph-graphrag-architecture.md`
3. `specs/retrieval-orchestrator.md`
4. `specs/enterprise-retrieval-governance.md`
5. `specs/layered-backend-and-service-evolution.md`

## 未来努力方向

当前文档体系里，未来方向主要沿三条线展开：

1. 企业级检索治理
   - 把多路检索能力升级成可解释、可审计、可降级、可评测的治理系统
2. 多 Agent 演进
   - 从单主 Agent + workflow，逐步走向 supervisor + specialist 的显式协作
3. 平台工程化演进
   - 保持前后端分层清晰，并为未来微服务 / 云原生 / Java 等异语言后端接入保留边界

对应文档：

- [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
- [Platform Evolution And Future Direction](./specs/platform-evolution-and-future-direction.md)
- [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)

## 当前不建议继续扩散的文档类型

后面新增文档时，尽量避免继续增加下面这类“看着很多、实际边界不清”的内容：

- 重复解释 GraphRAG 基础概念的笔记
- 只适用于某一天状态的阶段总结
- 把 spec、plan、audit 混写在同一篇里的长文
- 没有明确目标读者和职责边界的“方向随笔”

需要新增时，优先判断它属于：

- `spec`
- `plan`
- `decision`

不要再放第四种灰色地带文档。

## Current Execution Status

This section is the authoritative phase-status summary for the current repository state and supersedes older historical notes later in this file.

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: completed
- `Phase 5`: completed
- `Phase 6`: evaluation and evidence-chain hardening completed
- Current serial focus: `Phase 7` interview-facing total cleanup

## 当前阶段结论

当前最准确的判断是：

```text
`Phase 1-6` 已经拿到最小闭门证据与独立 GitHub 节点，
当前默认主线应切到 `Phase 7`，
开始把代码、目录、文档、评测、展示面与讲解口径
统一成面试前可稳定演示与稳定讲解的公开版本。
```

所以现在最重要的不是继续补 `Phase 5` 边角，而是：

1. 保持 `Phase 1-6` 的验收结果稳定
2. 进入 `Phase 7` 做最终总收口
3. 用统一后的公开版本准备演示、讲解与 GitHub 展示面

## 最终面试讲解路径

面试前公开讲解建议固定成下面这条路径：

1. `README.md`
2. `docs/architecture/README.md`
3. `docs/architecture/plans/current-phase-audit.md`
4. `docs/development/public-demo-evidence.md`
5. `docs/development/public-demo-runbook.md`
6. `docs/development/public-demo-acceptance.md`

最终统一验证入口：

- `python tools/scripts/verify_phase7_readiness.py`

## 后续阶段划分

为了让接下来的推进顺序更稳定，当前文档体系把后续工作拆成新的七个显式阶段：

1. `Phase 1`
   运行时收口与可运行恢复。
2. `Phase 2`
   项目文件夹与结构硬治理。
3. `Phase 3`
   文档与展示面硬收口。
4. `Phase 4`
   分层架构与运行时边界强化。
5. `Phase 5`
   LangGraph + GraphRAG 主线深化。
6. `Phase 6`
   评测与证据链固化。
7. `Phase 7`
   面试前总收口。

这些阶段默认遵守两条硬规则：

1. phase 与 phase 之间线性推进，不并行推进多个 phase
2. 单个 phase 内部可以并行做多项任务，但 phase 结束前必须统一验收

推荐顺序：

```text
完成 Phase 1
  -> 完成 Phase 2
  -> 完成 Phase 3
  -> 完成 Phase 4
  -> 再完成 Phase 5
  -> 再完成 Phase 6
  -> 最后完成 Phase 7
```

并且每个 phase 结束后都要先做一次简单测试，再同步文档并上传 GitHub。
