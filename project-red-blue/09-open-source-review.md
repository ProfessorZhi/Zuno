# Build-vs-Buy Architecture Review

## 当前状态

这是 Zuno 的正式 Build-vs-Buy 评审协议和候选记录，不是“为什么不用开源”的面试话术，也不是已经批准的架构变更。当前结论状态允许为 `TO_REVIEW`；只有完成 Fit Analysis、Modification Surface、运行验证和用户确认后，才可把结果回写 `docs/architecture/`、`docs/modules/` 或 ADR。

核心问题不是“开源项目功能多不多”，而是：

> **为了满足 Zuno 的真实 Contract，需要修改它多深；如果把它替换掉，Zuno 的领域事实和治理责任是否仍然完整？**

## 评审对象

红队攻击的对象不是一个品牌，而是一项候选能力：

```text
Candidate Capability
  → Zuno Contract 需要什么
  → 现成方案输出什么
  → 哪些地方可通过 Adapter / Provider 接入
  → 哪些地方必须修改上游核心
  → 升级、许可证、部署和数据迁移代价
  → 当前规模是否值得
  → 是否有 Benchmark / Spike 证据
```

## 四种选择

| 选择 | 含义 |
|---|---|
| `ADOPT` | 直接采用并围绕它集成 |
| `EXTEND` | 采用基础能力，补齐 Zuno 的差异部分 |
| `BUILD` | 现有方案无法满足关键 Contract，自己实现 |
| `DEFER` | 当前用户价值或证据不足，暂不做 |

## 五道 Gate

每个候选都必须逐门记录，不允许跳过“喜欢的方案”直接进入 BUILD：

| Gate | 问题 | 最低通过条件 |
|---|---|---|
| G1 Capability Fit | 功能能不能完成目标任务？ | 用明确输入、输出和失败样例验证，而不是只看 README 名称 |
| G2 Contract Fit | 能否输出 Zuno 的 Canonical Contract？ | 能保留版本、SourceSpan/Evidence、权限、状态、错误和审计所需信息 |
| G3 Modification Surface | 需要改它多深？ | 记录触及的领域对象、运行时、持久化、安全、恢复和升级边界 |
| G4 Operational / License Fit | 能不能安全运行和长期维护？ | 部署、数据出口、许可证、升级、隔离、供应商锁定和团队能力可接受 |
| G5 Evidence | 真的比最小自建或其他候选更好吗？ | 固定数据、失败样例、延迟、成本、质量和维护 Spike 可复现 |

Gate 结果可以是：`PASS`、`FAIL`、`UNKNOWN`。`UNKNOWN` 不能被叙事改写成 PASS。

## Modification Surface

评估 Fork 与 Adapter 时至少检查六个面：

```text
S1 Domain Model
   是否要改核心业务对象、关系和事实 Owner？
S2 Runtime / State
   是否要改执行状态机、计划、暂停、恢复和人机协同？
S3 Persistence
   是否要改数据库表、事件、索引、迁移和版本语义？
S4 Security
   是否要改权限、租户、数据分类、Secret、审批和撤权？
S5 Failure / Effect
   是否要改重试、幂等、未知副作用、对账和人工接管？
S6 Upgrade / Operations
   上游升级、配置兼容、部署、观测和回滚是否仍可控？
```

判断规则：

- 只增加 Parser、Retriever、Prompt、UI 或官方 Extension Point：优先 `EXTEND`；
- 能作为独立进程或 Provider 输出 Canonical Contract：优先 `ADOPT` / `ADAPTER`；
- 必须同时穿透 S1–S5，且长期维护上游核心：高度怀疑是重度 Fork，不得轻率 `BUILD`；
- 价值、规模或证据不足：`DEFER`，不为了架构完整继续实现。

“开源项目能不能改”不是问题；问题是“改完以后还剩多少上游、谁承担下一次升级”。

## Domain Control Plane 与 Replaceable Capability Layer

候选架构方向如下，属于 `[BLUE_PROPOSAL]`，尚未回写正式架构：

```text
Zuno Domain / Control Plane
    Matter / LegalTask / Review
    Claim / Evidence / Finding
    HumanDecision / WorkProduct
    Plan / RunOutcome
    Security Decision / Audit / Recovery Contract
                │
                │ Canonical Contract
                ▼
Replaceable Capability Layer
    IngestionBackend
    RetrievalBackend
    GraphRetrievalBackend
    MemoryBackend
    AgentRuntime
    ConnectorBackend
    Parser / Reranker / Embedding
```

如果替换 RAGFlow、OpenViking、LangGraph 或 Onyx 后，Zuno 仍然能保留领域事实、权限、证据、人工决定和恢复语义，候选更接近基础设施；如果替换会丢失这些事实，说明 Contract 还没有被正确抽出来。

## 待评估矩阵

| 能力 | 候选 | 当前状态 |
|---|---|---|
| Memory backend | OpenViking / Mem0 / Graphiti / Cognee | `TO_REVIEW` |
| Agent workflow | LangGraph / Dify / 自建 | `TO_REVIEW` |
| GraphRAG | Microsoft GraphRAG / LightRAG / LlamaIndex / 自建 | `TO_REVIEW` |
| Retrieval | OpenSearch / Milvus / pgvector / 自建 | `TO_REVIEW` |

## 本轮优先评审顺序

| Zuno 能力 | 候选方向 | 首要验证问题 | 当前状态 |
|---|---|---|---|
| 02 Ingestion | RAGFlow / Docling / MinerU / Native | 结构、表格、Redline、SourceSpan 和版本能否进入 `DocumentPipelineContract`？ | `TO_REVIEW` |
| 03 Knowledge | RAGFlow / Microsoft GraphRAG / LightRAG / Native | 能否按 Evidence Requirement 选择 Basic/Hybrid/Local/Global/DRIFT，并回到 Citation？ | `TO_REVIEW` |
| 05 Memory | OpenViking / Mem0 / Graphiti / Native | Engine 能否被 Zuno Memory Governance 约束写入、冲突、时效、权限和 Provenance？ | `TO_REVIEW` |
| 06 Agent Core | LangGraph / Native Controller | LangGraph 负责 Runtime，Zuno 保留哪些 Plan、Run、Proposal 和业务完成语义？ | `ADOPT_CANDIDATE` |
| Enterprise Connector | Onyx / Native Connector | 能否吸收连接、同步、权限和索引状态而不丢 Zuno `SourceObject` / Access Contract？ | `TO_REVIEW` |
| Product / Platform | Coze / MaxKB / Dify / Native | Fork 会触及多少 Domain/Runtime/Security/Persistence，是否应作为入口或 Backend？ | `TO_REVIEW` |

`ADOPT_CANDIDATE` 不是生产结论；它只表示该候选与现有“低层 Agent orchestration + Zuno Domain Control Plane”方向初步一致，仍需检查 Zuno 当前实现和部署要求。

## Conditional Evidence Retrieval：Graph 不是默认路径

本轮新增一个架构评审候选：`03 Knowledge` 的上位能力应描述为**受控证据检索（Evidence Retrieval）**，而不是默认“Agentic GraphRAG”。Graph 只是可选 Retrieval Capability：

```text
Evidence Requirement
  → Query / Task Features
  → Lexical / Dense / Structural / Graph Strategy
  → Fusion
  → Rerank
  → Evidence Evaluation
  → Enough?
       ├─ Yes → Citation / Finding
       └─ No  → Corrective Retrieval / User Clarification
```

候选路由：

| 问题类型 | 默认候选 |
|---|---|
| 精确条款、编号、法条号 | Lexical / Structural |
| 语义相似和表达改写 | Dense + Rerank |
| Defined Term、Cross Reference、多跳关系 | Graph Local |
| 全局主题和跨文档总结 | Graph Global |
| 需要逐步探索且成本可接受 | DRIFT / Agentic Retrieval |

必须用分层 Benchmark 比较 `Fixed Vector`、`Fixed Hybrid`、`Always Graph`、`Agentic RAG without Graph` 和 `Conditional Graph Retrieval`；没有分层结果时，不得宣称 GraphRAG 总体更好。

## 固定问题

1. 现成方案解决了哪个明确问题？
2. 它的权限、版本、数据隔离、可观测性和失败语义是否满足 Contract？
3. 如果扩展，真正的 Delta 是什么，维护边界由谁负责？
4. 迁移、升级、许可证、供应商锁定和数据出口成本是什么？
5. 今天从零开始，仍会 Build 吗？如果会，为什么；如果不会，应该采用什么？
6. 当前规模和团队是否值得承担自研成本？

7. 如果只加一个 Adapter，是否已经满足 80% 需求？
8. 如果必须改核心 Domain、State、Persistence、Security 和 Recovery，为什么还叫“轻量二开”？
9. 上游下一次升级时，Modification Surface 中哪些补丁必须重做？
10. 如果今天重做，最终选择会是 ADOPT、EXTEND、BUILD 还是 DEFER？证据是什么？

## 评审记录模板

```text
Candidate：
Zuno Capability：
版本 / Commit：
G1 Capability Fit：PASS / FAIL / UNKNOWN
G2 Contract Fit：PASS / FAIL / UNKNOWN
G3 Modification Surface：S1 / S2 / S3 / S4 / S5 / S6
G4 Operational / License Fit：PASS / FAIL / UNKNOWN
G5 Evidence：
候选决策：ADOPT / EXTEND / BUILD / DEFER / PENDING
Zuno 保留的 Canonical Contract：
候选项目负责的范围：
Adapter / Provider 边界：
升级与退出方案：
Benchmark / Spike：
待确认 Gap：
```

`PENDING` 只允许出现在研究阶段，不能进入最终架构决策。

任何“比 WorkBuddy 强”“开源方案不适合企业”等结论都必须进入待验证状态，不能用品牌印象替代技术和业务证据。
