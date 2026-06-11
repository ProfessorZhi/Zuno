# Architecture Docs

这个目录是 Zuno 的稳定架构入口。

它要回答的不是“最近做了什么”，而是下面四件事：

1. Zuno 现在的主架构是什么
2. 为什么要按这种方式分层
3. 后续往更复杂能力演进时，哪些边界必须保持稳定
4. 代码结构、目录结构、文档口径怎样保持一致

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
  解释总目标、总顺序、总理由
- `specs/`
  稳定架构定义
- `plans/`
  阶段推进顺序、退出条件、当前阶段判断
- `decisions/`
  关键架构决策记录

## 当前主架构

当前 Zuno 的主线不是“聊天界面 + 若干插件”，而是：

```text
本地优先 Agent 工作台
  -> LangGraph runtime
  -> Retrieval Orchestrator
  -> RAG / GraphRAG / BM25
  -> Domain Pack
  -> Eval / Trace / Citation / Cost control
```

当前重点服务的是：

- 强领域问答
- 证据驱动检索
- 可评测、可治理的 Agent runtime

## 当前执行状态

下面这组状态是当前仓库的权威串行账本：

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: current serial phase
- `Phase 5`: pending
- `Phase 6`: pending
- `Phase 7`: pending

当前默认主线是进入 `Phase 4`，不要提前宣称更后面的 phase 已经完成。

## 推荐阅读顺序

如果你第一次看这个目录，按下面顺序读：

1. [Zuno Refactor Plan](./zuno_refactor_plan.md)
2. [Architecture Specs](./specs/README.md)
3. [Architecture Plans](./plans/README.md)
4. [Current Phase Audit](./plans/current-phase-audit.md)
5. [Zuno Refactor Execution Plan](./plans/zuno-refactor-execution-plan.md)

如果你只想理解稳定架构主线，优先看：

1. [Domain Pack + LangGraph + GraphRAG Architecture](./specs/domain-pack-langgraph-graphrag-architecture.md)
2. [Retrieval Orchestrator](./specs/retrieval-orchestrator.md)
3. [Enterprise Retrieval Governance](./specs/enterprise-retrieval-governance.md)
4. [Layered Backend And Service Evolution](./specs/layered-backend-and-service-evolution.md)
5. [RAG Evaluation And Observability](./specs/rag-evaluation-and-observability.md)

## 当前最重要的文档边界

当前公开阅读路径要保持成一条主线：

1. `README.md`
2. `docs/README.md`
3. `docs/architecture/README.md`
4. `docs/architecture/specs/README.md`
5. `docs/architecture/plans/README.md`
6. `docs/architecture/plans/current-phase-audit.md`

下面这些内容可以继续存在，但不应占据当前主阅读路径：

- 未来 phase 的预备计划
- 面向后续展示的专题材料
- 仅适用于某次阶段状态的临时说明

## 文档维护原则

后续每完成一个大阶段，都必须回看：

- `README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/architecture/specs/README.md`
- `docs/architecture/plans/README.md`

原则：

```text
主阅读路径只保留当前真正稳定、真正有效的入口。
已经失效、冲突、过早暴露的叙事，要么降级，要么移出主路径。
```
