# Retrieval Governance Upgrade Plan

## Purpose

这份计划文档不重复讲 GraphRAG 原理，也不替代当前架构升级主文档。

它只负责回答：

```text
在当前已有本地 RAG / GraphRAG / 合同审查评测 / LangGraph runtime 的基础上，
企业级检索治理这一层下一步应该怎么补，按什么顺序补，补到什么算阶段成立。
```

## Current Starting Point

当前已经成立的前提：

- 已有本地 embedding 与本地 compare matrix
- 已有合同审查 Domain Pack 与 GraphRAG 主线
- 已有公开 demo runbook、acceptance、runtime smoke
- 已有 Retrieval Orchestrator / Query Policy / Governance spec 文档骨架

因此这份计划不再从“先证明 GraphRAG 有用”开始，而是从“如何把已有能力升级成企业级治理层”开始。

## What This Plan Is Trying To Close

当前最缺的不是更多 retriever，而是以下四类治理交付：

1. 统一的 `profile -> planner -> RetrievalPlan -> trace` contract
2. 显式的 `budget / fallback / citation / scope / index_version` 硬约束
3. 能进入 compare matrix / runtime smoke / public demo 解释层的治理证据
4. 在未来多 agent、微服务、异语言后端下仍能保留的检索治理边界

## Upgrade Order

### Phase A: Profile and Plan Explicitization

目标：

- 把当前散落在 runtime settings、retrieval mode、fallback metadata 里的信息显式提升为 `profile` 与 `RetrievalPlan`

最低交付：

- `requested_profile`
- `resolved_profile`
- `requested_mode`
- `resolved_mode`
- `enabled_retrievers`
- `fallback_reason`

验收：

- runtime trace 能解释“请求想要什么”和“系统最终接受了什么”
- compare matrix 报告至少能展示 resolved mode 与 fallback 信息

### Phase B: Scope / Version / Health Hardening

目标：

- 把作用域、索引版本、索引健康度从“背景信息”提升为 planner 的硬输入

最低交付：

- `knowledge_id` 前置约束
- `status=active`
- `index_version`
- `index_health`
- `domain_pack_id`

验收：

- planner 输入结构里显式出现这些字段
- trace 能记录这些字段
- public demo 文档能说明结果属于哪种作用域和索引版本语义

### Phase C: Citation Contract Upgrade

目标：

- 把 citation 从“结果后检查”升级为“evidence-first grounding contract”

最低交付：

- evidence bundle
- strict profile 下的 claim support check
- 允许“证据不足”

验收：

- 合同审查严格场景能区分“有依据的结论”和“证据不足”
- public demo acceptance 能描述 citation 严格度差异

### Phase D: Budget and Degradation Observability

目标：

- 让 graph、rerank、requery 的预算消耗和降级事件真正可见

最低交付：

- graph budget counters
- rerank budget counters
- requery budget counters
- degradation event schema

验收：

- compare matrix / runtime smoke / trace 至少一处能看到这些字段
- 能解释某次运行为什么降级

### Phase E: Portable Governance Contract

目标：

- 让治理层在未来多 agent、微服务、异语言后端下仍然成立

最低交付：

- planner 不和单一 agent 强绑定
- RetrievalPlan 可以跨进程 / 跨服务边界传递
- scope / budget / citation / index_version 不依赖 Python 单体内部隐式状态

验收：

- 架构文档能清楚说明这些 contract 在未来演进中的位置

## Immediate Next Work

如果目标是“尽快靠近目标文档要求”，下一步最值钱的工作顺序是：

1. 先把 `profile / plan` contract 显式化
2. 再把 `scope / index_version / health` 收进 planner 输入
3. 再把 citation 升级成 strict grounded contract
4. 最后补预算和降级的统一可观测层

原因：

- 当前最不清楚的不是 retriever 能力，而是控制面 contract
- 如果 contract 不先定下来，后面加治理字段只会继续分散

## Relationship To Other Docs

- `zuno_refactor_plan.md`
  - 现已降级到 `docs/architecture/history/`，只保留历史上下文价值
- `specs/architecture-upgrade-2026-06.md`
  - 负责当前架构升级的目标结构、phase 分层与 workflow 规则
- `enterprise-retrieval-governance.md`
  - 负责治理层语义边界
- `retrieval-orchestrator.md`
  - 负责控制面骨架
- `rag-evaluation-and-observability.md`
  - 负责评测与 trace 基础能力
- `public-demo-acceptance.md`
  - 负责对外可验证交付面

这份文档的职责只是一件事：

```text
把治理层升级工作拆成按阶段可落地、可验收、可对齐现有文档体系的执行顺序
```
