# Build-vs-Buy Architecture Review

## 当前状态

这是 Zuno 的正式 Build-vs-Buy 评审协议和候选记录，不是“为什么不用开源”的面试话术，也不是已经批准的架构变更。当前结论状态允许为 `TO_REVIEW`；只有完成 Fit Analysis、Modification Surface、运行验证和用户确认后，才可把结果回写 `docs/project/architecture/`、`docs/project/<topic>/` 或 ADR。

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
| Memory backend | OpenViking / Mem0 / Graphiti / Cognee | `EXTEND_CANDIDATE / TO_REVIEW` |
| Agent workflow | LangGraph / Dify / 自建 | `ADOPT_CANDIDATE / TO_REVIEW` |
| GraphRAG | Microsoft GraphRAG / LightRAG / LlamaIndex / 自建 | `TO_REVIEW` |
| Retrieval | RAGFlow / LightRAG / OpenSearch / Milvus / pgvector / 自建 | `TO_REVIEW` |

## 本轮优先评审顺序

| Zuno 能力 | 候选方向 | 首要验证问题 | 当前状态 |
|---|---|---|---|
| 02 Ingestion | RAGFlow / Docling / MinerU / Native | 结构、表格、Redline、SourceSpan 和版本能否进入 `DocumentPipelineContract`？ | `EXTEND_CANDIDATE / TO_REVIEW` |
| 03 Knowledge | RAGFlow / Microsoft GraphRAG / LightRAG / Native | 能否按 Evidence Requirement 选择 Basic/Hybrid/Local/Global/DRIFT，并回到 Citation？ | `TO_REVIEW` |
| 05 Memory | OpenViking / Mem0 / Graphiti / Native | Engine 能否被 Zuno Memory Governance 约束写入、冲突、时效、权限和 Provenance？ | `EXTEND_CANDIDATE / TO_REVIEW` |
| 06 Agent Core | LangGraph / Native Controller | LangGraph 负责 Runtime，Zuno 保留哪些 Plan、Run、Proposal 和业务完成语义？ | `ADOPT_CANDIDATE / TO_REVIEW` |
| Enterprise Connector | Onyx / Native Connector | 能否吸收连接、同步、权限和索引状态而不丢 Zuno `SourceObject` / Access Contract？ | `ADOPT_CANDIDATE / TO_REVIEW` |
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

## Reuse-first Capability Atlas（2026-08-12 官方资料快照）

下表是本轮 Blue Research 的能力地图，不是正式 Adopt 清单。`HEAD` 只用于复现本轮资料快照；它不代表已完成 Spike、Contract Conformance、许可证审批或生产部署。

| 能力 | Candidate | 官方资料 / HEAD | Reuse Mode | Zuno Contract Owner | Modification Surface | License / 运营观察 | G1 | G2 | G3 | G4 | G5 | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Document Pipeline | RAGFlow | [repo](https://github.com/infiniflow/ragflow) / `a0e091e75051f278ab21e7e1c2ce3d1fcccbd5a2` | `EXTEND_CANDIDATE` | 02 | S1/S3/S4/S5 需验证 | Apache-2.0；需核验部署、数据出口和版本兼容 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Document Parser | Docling | [repo](https://github.com/docling-project/docling) / exact pin pending Spike | `ADAPTER_CANDIDATE` | 02 | S1/S3/S5 需验证 | 需按实际版本和依赖清单核验 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Document Parser | MinerU | [repo](https://github.com/opendatalab/MinerU) / exact pin pending Spike | `ADAPTER_CANDIDATE` | 02 | S1/S3/S5 需验证 | 需按实际模型、服务和许可证核验 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Retrieval / Graph | Microsoft GraphRAG | [query docs](https://microsoft.github.io/graphrag/query/overview/) / [repo](https://github.com/microsoft/graphrag) / `14a00ad88fc33cf2b52f4f113f25807556f8e25e` | `ADAPTER_CANDIDATE` | 03 | S1/S2/S3/S5 需验证 | Query Engine 同时包含 Basic、Local、Global、DRIFT；不能直接替代 Zuno Evidence Contract | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Retrieval / Graph | LightRAG | [repo](https://github.com/HKUDS/LightRAG) / `6f50fddd8b4a0520d62639b7ea0a1f173d7e5dfc` | `ADAPTER_CANDIDATE` | 03 | S1/S2/S3/S5 需验证 | 提供 API、图检索、存储后端和评测集成；许可证与部署需按 pin 核验 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Memory | OpenViking | [docs](https://docs.openviking.ai/) / [repo](https://github.com/volcengine/OpenViking) / `00f3738edbc3615481011054012b3fe171f91dd3` | `EXTEND_CANDIDATE` | 05 | S1/S2/S3/S4/S5 需验证 | Context Database；Memory/Resource/Skill、分层上下文和递归检索；License、版本和部署需复核 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `EXTEND_CANDIDATE / TO_REVIEW` |
| Memory | Mem0 | [repo](https://github.com/mem0ai/mem0) / exact pin pending Spike | `ADAPTER_CANDIDATE` | 05 | S1/S3/S4/S5 需验证 | 需核验存储、Scope、删除、冲突和许可证边界 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Memory / Graph | Graphiti | [repo](https://github.com/getzep/graphiti) / exact pin pending Spike | `ADAPTER_CANDIDATE` | 05 | S1/S3/S4/S5 需验证 | 需核验时间知识图谱、权限和数据退出能力 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Agent Runtime | LangGraph | [persistence docs](https://docs.langchain.com/oss/python/langgraph/persistence) / [repo](https://github.com/langchain-ai/langgraph) / `644815f9e5bc52ad8f7a5227a456227e9c3e639b` | `ADOPT_CANDIDATE` | 06 | S2/S3/S5 需验证 | Checkpoint、Interrupt、Resume 和 HITL 机制；Zuno 仍拥有 Domain Fact 和 Business Completion | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `ADOPT_CANDIDATE / TO_REVIEW` |
| Connector | Onyx | [connector docs](https://docs.onyx.app/admins/connectors/overview) / [repo](https://github.com/onyx-dot-app/onyx) / `e2125952f0bacdc02e3e8a879edf21e33d4a999d` | `ADOPT_CANDIDATE` | 02/03/09 | S1/S3/S4/S5 需验证 | 持久同步和权限同步能力；Permission Sync 为 Enterprise/Cloud 边界，需核验 CE/EE、退出和权限映射 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `ADOPT_CANDIDATE / TO_REVIEW` |
| Full Agent Platform | Coze Studio | [repo](https://github.com/coze-dev/coze-studio) / `fefb05ff27be1da939612fbf9faf5db62583b8ae` | `FORK_OR_ENTRY_CANDIDATE` | 01/06/07/08/09 | S1/S2/S3/S4/S5 需验证 | Agent、Workflow、Knowledge、Plugin、API/SDK；Apache-2.0，但完整 Fork 的 Domain/Runtime/Security 面需实测 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Full Agent Platform | MaxKB | [repo](https://github.com/1Panel-dev/maxkb) / `d59728533538130fc77656559c4a1caa78e9aa01` | `FORK_OR_ENTRY_CANDIDATE` | 01/03/06/08/09 | S1/S2/S3/S4/S5 需验证 | Agent/RAG/Workflow/MCP；GPLv3，必须先做 G4 许可证和部署模型评估 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Full Agent Platform | Dify | [repo](https://github.com/langgenius/dify) / `ef8544b173fd6cd7a8e71df2cab576e52bebbfbc` | `FORK_OR_ENTRY_CANDIDATE` | 01/03/04/06/07/08/09 | S1/S2/S3/S4/S5 需验证 | Agent Workflow、RAG、Model、Observability；Dify Open Source License 含额外条件，需做 G4 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Full Agent Platform | FastGPT | [repo](https://github.com/labring/FastGPT) / `08dc58e9e1051ecc414b718a5ac36e2226633ee0` | `FORK_OR_ENTRY_CANDIDATE` | 01/03/06/07/08 | S1/S2/S3/S4/S5 需验证 | RAG、数据处理、可视化 Workflow；官方 Open Source License 对 SaaS/商用有额外条件，需做 G4 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `TO_REVIEW` |
| Horizontal Agent Surface | WorkBuddy | [official site](https://www.workbuddy.cn/work/) / version not applicable | `FUTURE_INTEGRATION_CANDIDATE` | 01/03/06/07/08/09 via Skill/MCP/API | S1/S2/S3/S4/S5 需验证 | 商业产品入口，不按开源 Fork 评估；需按公开接口和企业合作边界核验 | FACT | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | `FUTURE` |

### 本表中的结论层级

- `FACT`：官方资料明确声明的能力、许可证或公开接口；不等于 Zuno 已经采用。
- `INFERENCE`：基于公开资料对潜在适配面的推断，必须回源码、测试或 Spike 验证。
- `CANDIDATE`：可进入 Adapter / Provider 评估的方向。
- `TARGET DECISION`：只有完成 G1–G5、用户批准和必要 ADR 后才能进入正式 Architecture。

### DeepWiki / Wiki 研究协议

```text
README
→ Official Docs / Wiki
→ DeepWiki 等辅助 Architecture Map
→ Source Code
→ Tests
→ Issues / Releases
→ License
→ Zuno Contract Mapping
→ Spike
→ Decision
```

DeepWiki 或 Wiki 只用于导航和源码地图，不能作为 Security、Failure、Recovery、Permission 或 Idempotency 的最终证据；关键结论必须回到官方文档、源码和测试。

## RED-KERNEL-V3 分层复核（2026-08-12）

本节是本轮竞争性反证的官方资料快照，不是 Adopt 清单，也不把产品按一个总分排序。完整来源、访问日期、UNKNOWN 和许可证备注见 `project-reconstruction-lab/sources/red-kernel-v3-official-platform-matrix.md`。

| 产品/项目 | 正确比较层级 | 公开资料支持的最小判断 | 保持 UNKNOWN 的关键边界 | V3 处置 |
|---|---|---|---|---|
| [WorkBuddy](https://www.workbuddy.cn/work/) | Horizontal Agent Workspace / Host | Expert、Skill、MCP、自然语言任务执行；企业页面另有模型、权限、审计、OpenAPI/插件等能力描述 | Legal Canonical State、Evidence Dependency、Finding Review、法律 Eval Contract | 默认 Host 候选；不作安全负面断言 |
| [Dify](https://dify.ai/) | Agent / Workflow App Platform | Workflow、RAG、Agent、Tools、MCP/API、Observability、自托管/VPC | 法律 Domain State；仓库许可证额外条件的具体商用部署适配 | BUY/EXTEND 候选；G4 必须复核 |
| [Pi mono](https://github.com/badlogic/pi-mono) | Agent Harness / Toolkit | Agent Core、tool calling、session/state、LLM API 与 coding agent 组件 | 企业租户、法律 Owner、审计、HITL、生产部署 | Runtime/嵌入候选，不是完整产品竞品 |
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) | Agent Runtime Framework | Durable execution、checkpoint/persistence、interrupt/resume、HITL、低层编排 | Domain Fact、法律正确性、Evidence Owner | 可替换 Runtime Provider；不承载法律事实 |
| [RAGFlow](https://github.com/infiniflow/ragflow) | Retrieval / Context Provider | 文档理解、chunking、多路召回/融合/rerank、引用、MCP/API | Canonical Matter/Fact/Finding、人工决定、依赖失效 | Retrieval Provider 候选；Graph 需 Kill Test |

结论：WorkBuddy、Dify、Pi、LangGraph 和 RAGFlow 不是完全同层竞品。它们的公开能力足以击穿“Zuno 必须自建全部 Host/Runtime/RAG/Memory”的命题；它们没有公开证明“法律业务状态后端”必然多余。这个剩余命题只能由 A/B/C 和替换 Spike 证明，不能由品牌比较证明。
