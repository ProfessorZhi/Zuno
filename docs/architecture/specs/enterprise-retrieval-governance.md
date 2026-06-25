# Enterprise Retrieval Governance

## Purpose

这份文档只回答一个问题：

```text
当 Zuno 同时具备 Dense RAG、BM25、GraphRAG、requery、rerank、
citation check、GraphRAG Project / query policy 和本地评测能力时，
如何把它们收束成一套可解释、可审计、可降级、可控成本的企业级检索系统。
```

它不是 GraphRAG 基础概念文档，也不是某一条 retrieval pipeline 的实现说明。
它补的是现有架构文档之间缺少的“治理层”。

## What Already Exists

当前仓库里已经有不少检索与评测底座，问题不是“能力缺失”，而是“治理语义还不够收口”。

已有能力可以归成四类：

### 1. Retrieval and Runtime

- `docs/architecture/specs/retrieval-orchestrator.md`
- `docs/architecture/specs/langgraph-runtime.md`
- `src/backend/zuno/api/services/knowledge_query.py`

这部分已经说明：

- 存在统一 retrieval orchestrator 方向
- 存在 knowledge capability / query policy 的拆层
- 已有单一 `GeneralAgent` 会话入口和 GraphRAG Project query runtime

### 2. Domain Modeling and GraphRAG

- `docs/architecture/history/specs/domain-pack-langgraph-graphrag-architecture.md`
- `examples/graphrag-projects/contract_review/`
- `src/backend/zuno/services/graphrag/`

这部分已经说明：

- GraphRAG 不是孤立能力，而是受 GraphRAG Project、query policy、
  retrieval planner 和 evidence contract 共同约束
- 合同审查是当前第一条高质量领域建模主线

### 3. Evaluation and Observability

- `docs/architecture/specs/rag-evaluation-and-observability.md`
- `docs/architecture/plans/rag-local-eval-scheme.md`
- `tools/evals/zuno/rag_eval/`
- `tools/evals/zuno/contract_review_eval/`

这部分已经说明：

- 已经有本地 embedding、本地 compare matrix、五项以上指标
- 已经能在合同审查场景下比较 RAG / GraphRAG

### 4. Public Proof and Operational Docs

- `docs/development/public-demo-runbook.md`
- `docs/development/public-demo-acceptance.md`
- `docs/development/public-demo-evidence.md`
- `tools/scripts/verify_public_demo_runtime.py`

这部分已经说明：

- 已经有 GitHub-safe 的公开 demo 复现链
- 已经能提供低成本 runtime smoke proof

## What Is Still Missing

如果按企业级检索系统来要求，当前真正还缺的是治理层，而不是更多 retriever。

核心缺口有六类：

1. `profile` 还没有完全成为统一的策略包络层。
2. `planner` 与 `RetrievalPlan` 的 contract 还不够显式。
3. `budget / fallback / scope / index_version` 还更像零散 metadata，而不是硬约束。
4. `citation` 已经存在，但还没有完全升级为 claim-level grounding contract。
5. `trace` 已经有了，但还缺统一的治理视角解释模板。
6. `GraphRAG` 还没有在治理层被定义为一种 capability-scoped、domain-scoped 的受控能力。

如果这些缺口不补，系统依然更像：

```text
具备较多增强能力的高级 RAG 原型
```

而不是：

```text
可治理、可审计、可降级、可升级的企业级检索架构
```

## Governance Model

治理层推荐统一成四层：

```text
Capability
  -> Profile
  -> Plan
  -> Trace
```

### Layer 1: Capability

Capability 回答的是：

```text
这个 knowledge 当前到底具备什么检索能力
```

最少应覆盖：

- `rag`
- `rag_graph`
- `keyword`
- `rerank`
- `citation_verifier`

Capability 描述“能不能做”，不描述“这次该不该做”。

### Layer 2: Profile

Profile 回答的是：

```text
这类请求允许系统消耗多少预算，
允许启用哪些能力，
要求多严格的证据与 citation 约束
```

Profile 至少应约束：

- latency 上限
- token / cost 上限
- allowed retrievers
- requery strictness
- citation strictness
- fallback strictness

Profile 不是固定 DAG。
它是策略包络层。

### Layer 3: Plan

Plan 回答的是：

```text
这次请求在当前能力、健康度、预算和作用域下，
具体决定启用哪几条检索路径
```

Plan 是单次请求的结构化 contract。
它应该是 trace、评测、审计、降级解释的共同锚点。

### Layer 4: Trace

Trace 回答的是：

```text
为什么这次走了这条路，
为什么没走另一条，
为什么降级，
为什么保留这些证据，
为什么认为它们足以或不足以支持答案
```

没有这一层，治理无法落地。

## Boundary Definitions

这一节只定义治理对象的边界，不重复 GraphRAG 原理。

### `profile`

职责：

- 定义策略包络
- 约束成本、延迟、允许能力、citation 严格度

不负责：

- 决定本次具体走哪条 retriever
- 决定最终答案内容

### `planner`

职责：

- 消费 query、capability、GraphRAG Project policy、scope、budget、health
- 产出结构化 `RetrievalPlan`

不负责：

- 真正执行 retriever
- 最终答案生成

### `RetrievalPlan`

职责：

- 记录本次请求的检索合同

至少应包含：

- `requested_profile`
- `resolved_profile`
- `requested_mode`
- `resolved_mode`
- `enabled_retrievers`
- `requery_policy`
- `rerank_policy`
- `citation_policy`
- `fallback_policy`
- `budget_policy`
- `scope_policy`
- `trace_policy`

### `trace`

职责：

- 提供可解释性与可审计性

至少应解释：

- 为什么启用 graph
- 为什么触发 requery
- 为什么放弃 rerank
- 为什么降级
- 为什么当前 evidence 足够或不足

### `budget`

职责：

- 作为 planner 的硬约束输入

至少要约束：

- rewrite 次数
- rerank 候选规模
- graph traversal 宽度
- context token 预算
- 端到端延迟预算

### `fallback`

职责：

- 定义允许的优雅降级路径

要求：

- 必须显式
- 必须进入 trace
- 必须说明降级前后差异

### `citation`

职责：

- 约束答案建立在当前 evidence bundle 之上

在严格场景下，应接近 claim-level grounding contract，而不是结果后装饰。

### `scope`

职责：

- 定义硬边界，不是召回后的软过滤

至少约束：

- tenant
- knowledge
- GraphRAG Project / migration alias scope
- active status

### `index_version`

职责：

- 记录这次结果使用的是哪一版索引、哪一版 schema、哪一版 graph extraction

没有 index version，就没有真正的可复现与可审计。

### `graph update`

职责：

- 定义文档变化之后，向量索引和图谱索引如何一起增量更新

面试前至少要形成：

- `document_hash`
- `chunk_hash`
- 增量 embedding 更新
- 增量 graph extraction
- 旧关系 `inactive`
- 查询只用 `status=active + 当前 index_version`

## Current Governance Gaps By Topic

### Profile Gap

当前已经有 retrieval mode、runtime settings、fallback 信息。
但它们还没有完全上升成统一 profile 语义。

缺的不是更多 mode，而是：

- `requested_profile`
- `resolved_profile`
- profile 与 budget / citation / fallback 的一致 contract

### Planner Gap

当前已经有 planner / orchestrator 方向。
但还缺对单次请求计划的正式 contract。

缺的不是“再加一个 planner”，而是：

- 计划结构固定
- 降级原因固定
- scope / health / index version 进入计划输入

### Trace Gap

当前已有 trace 和 compare matrix。
但 trace 还没有完全按治理视角结构化：

- 为什么 graph 被允许
- 为什么 graph 被拒绝
- 为什么 rerank 被跳过
- 为什么 strict citation 被降级

### Citation Gap

当前 citation 更接近“验证结果是否看起来对”。
企业级治理需要更进一步：

- evidence bundle
- claim grounding
- strict profile 下允许“证据不足”

### Scope and Version Gap

当前 scope 和 version 语义还不够显式。

企业级要求下，planner 至少要显式接收：

- `knowledge_id`
- `graphrag_project_id`
- `index_version`
- `index_health`
- `status=active`

### Graph Update Gap

当前已经有 graph extractor、writer、index version、cache 相关骨架。
但治理层还需要把“动态更新”正式定义成必需能力，而不是实现细节。

## Requery Governance

### Requery Is Conditional

Requery 不能默认执行。
它应只在以下情况触发：

- query 过于模糊
- 首轮 recall 偏低
- 问题明显是 relation-heavy
- evidence coverage 有缺口
- citation verification 失败

### Domain-Aware Requery

在合同审查等领域场景里，requery 应优先受 GraphRAG Project query policy
驱动，而不是纯通用 rewrite。

例如 `contract_review` project policy 应能定义：

- 风险槽位
- clause / obligation / regulation 相关的补检提示
- relation-heavy query 的重写模板

### Requery Budget Cap

Requery 必须受预算硬约束：

- `max_rounds`
- `max_rewrites`
- `max_extra_contexts`
- `timeout_ms`
- `max_incremental_cost`

## Citation Governance

### Citation Check Is Not Enough

企业级治理下，citation 不应只是“答案生成后再检查一下”。

推荐顺序是：

```text
retrieve evidence
  -> build evidence bundle
  -> generate grounded claims
  -> verify support
  -> compose final answer
```

### Strict Profiles Must Allow Insufficient Evidence

对于 `strict_grounded` 场景，系统必须允许输出：

```text
当前证据不足，无法确认
```

而不是为了回答完整性硬补结论。

## GraphRAG Governance

### GraphRAG Is Capability-Scoped

不是所有 knowledge 都应默认启用 graph route。

只有满足以下条件时，planner 才应认真考虑 GraphRAG：

- knowledge 具备 `rag_graph`
- graph index health 正常
- 当前 GraphRAG Project 定义了有效 schema / retrieval policy
- query 明显具有关联或结构化需求

### GraphRAG Must Be Source-Backed

graph path 不能脱离原文证据独立存在。

至少应能回链到：

- source document
- source chunk
- extraction evidence
- schema version

### GraphRAG Project Controls Path Semantics

GraphRAG 的 path 语义不应统一硬编码。

例如 `contract_review` GraphRAG Project 应能定义：

- 哪些 relation 更重要
- 哪些 path 优先返回
- 哪些 relation 在当前 query 下属于噪声

### GraphRAG Must Support Incremental Update

如果文档一变化就只能全量重建，GraphRAG 仍然更像 demo。

面试前建议至少做到：

- 文档 hash 检测变化
- chunk hash 比较变化
- 未变化 chunk 复用 embedding / extraction cache
- 变化 chunk 重新抽图并 upsert
- 删除 chunk 对应关系失效而不是直接无痕删除

## Fallback Governance

### Degrade Gracefully

企业级检索系统必须允许优雅降级。

例如：

```text
graph unavailable
  -> dense + bm25

reranker unavailable
  -> fusion only

citation verifier unavailable
  -> downgrade strictness and record risk
```

### Every Degradation Must Be Visible

每次降级都必须进入 trace。

至少记录：

- 降级前计划
- 触发原因
- 降级后计划
- 影响范围

## Budget Governance

预算不是事后统计，而是 planner 的输入约束。

至少要对下面这些对象设上限：

- LLM rewrite calls
- rerank candidate size
- graph traversal breadth
- context tokens
- overall latency

## Scope and Index Version Governance

### Scope Is A Hard Constraint

作用域必须前置：

- `tenant_id`
- `knowledge_id`
- `graphrag_project_id`
- `status=active`

### Index Version Must Be Traceable

当 schema、graph extraction、index rebuild 发生变化时，系统必须能回答：

```text
这次答案到底基于哪一版索引和哪一版图抽取
```

## Phased Upgrade Route

治理层不应该一次做满，推荐按现有架构主线分阶段推进。

### Stage 1: Make Existing Policy Explicit

目标：

- 把已有 runtime settings / retrieval mode / fallback 信息显式提升为 `profile + plan` 语义

最低交付：

- `requested_profile / resolved_profile`
- `requested_mode / resolved_mode`
- `fallback_reason`
- `budget_policy`

### Stage 2: Make Scope And Version Hard Constraints

目标：

- 把 `scope` 和 `index_version` 从“记录信息”升级为 planner 的硬约束输入

最低交付：

- `knowledge_id` 过滤前置
- `status=active`
- `index_version` 入 trace
- `index_health` 进入 planner

### Stage 2.5: Make Graph Update Incremental

目标：

- 把 GraphRAG 从“一次建图”提升为“可增量维护的图谱索引”

最低交付：

- `document_hash`
- `chunk_hash`
- graph extraction cache
- graph relation `inactive`
- vector / graph index consistency rules

### Stage 3: Make Citation A Governance Contract

目标：

- 把 citation 从结果后处理升级为 evidence-first 约束

最低交付：

- evidence bundle
- claim support check
- strict profile 下允许“证据不足”

### Stage 4: Make Budget And Fallback Observable

目标：

- 让预算消耗、降级事件、graph route 放弃原因稳定进入 trace 与评测报告

最低交付：

- degradation event schema
- requery / rerank / graph budget counters
- compare matrix 和 demo runbook 能解释这些事件

### Stage 5: Make Governance Portable

目标：

- 让治理 contract 在未来多 agent、微服务、异语言后端下仍然成立

最低交付：

- planner contract 不依赖单一 agent 实现
- RetrievalPlan 可跨服务边界传递
- scope / budget / citation / index_version 语义不依赖 Python 单体

## Relationship To Existing Docs

这份文档不是替代已有 spec，而是补它们之间缺少的治理层。

- `retrieval-orchestrator.md` 负责统一控制面骨架
- `../history/specs/domain-pack-langgraph-graphrag-architecture.md` 只保留 Domain Pack-era
  迁移上下文；当前总体结构以 GraphRAG Project / query policy 为准
- `rag-evaluation-and-observability.md` 负责评测与 trace 基础要求

这份文档额外定义的是：

- `profile` 的企业级语义
- `planner` 与 `RetrievalPlan` 的治理边界
- `trace / budget / fallback / citation / scope / index_version` 的硬约束语义
- `GraphRAG` 动态更新进入治理层后的边界语义

## First Acceptance Bar

第一阶段不要求把所有治理点一次性做满。
但至少要保证下面五点成立：

1. `profile` 与 `plan` 明确分离
2. planner 能基于 `budget / capability / health` 做显式降级
3. `strict_grounded` 至少具备基本的 claim-to-evidence 约束
4. trace 能解释为什么启用或放弃 graph / requery / rerank
5. retrieval scope 至少按 `knowledge_id / index_version / status` 收紧

如果这五点还不成立，系统仍然更接近“增强型 RAG 原型”，而不是企业级可治理检索架构。
