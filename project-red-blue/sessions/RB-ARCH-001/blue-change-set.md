# RB-ARCH-001 Blue Change Set Resolution

本文件保留第一轮 100 问和 Blue Research 的提案语义，并记录本轮 User Gate 决议。第一轮 Transcript、原始 Question、Score 和 Baseline Evidence 不修改；本文件不拥有正式架构事实。

User Gate Resolution：`APPROVED_WITH_AMENDMENTS`
Canonical Sync Commit A：`PENDING_COMMIT_A`
Gate Resolution Commit B：`PENDING_COMMIT_B`
本轮禁止：Runtime、Migration、Implementation Program、SKILL.md、RB-ARCH-002 和 Mutation Retest。

## Blue Research References

以下只作为本轮 Blue Research 的外部参考，不改变当前 Zuno Canonical Contract，也不构成已采用的实现事实。所有吸收、扩展或替换结论仍需经过 User Gate、正式文档同步和后续 Retest。

- [RAGFlow 官方仓库](https://github.com/infiniflow/ragflow)：评估文档解析、通用检索、Agent/MCP、Memory 和 Connector 能力；需要进一步验证输出是否满足 Zuno 的 `DocumentVersion`、`ParseSnapshot`、`SourceSpan` 和 Evidence Contract。
- [OpenViking 官方文档](https://docs.openviking.ai/) / [官方仓库](https://github.com/volcengine/OpenViking/)：评估 Context Database、Memory/Resource/Skill、分层上下文和递归检索；Zuno 仍需拥有 Memory Governance、权限、时间有效性、冲突和 Provenance 语义。
- [Onyx Connector 文档](https://docs.onyx.app/admins/connectors/overview) / [Connector 能力说明](https://docs.onyx.app/overview/core_features/connectors)：评估持久化同步、Connector 状态和可选权限同步；权限同步的版本和发行版边界仍需单独核验。
- [Microsoft GraphRAG Query Overview](https://microsoft.github.io/graphrag/query/overview/)：支持比较 Basic、Local、Global 和 DRIFT；本轮提案将 Graph 视为条件检索能力，而不是默认 Always-On。
- [Coze Studio 官方仓库](https://github.com/coze-dev/coze-studio)：评估 Agent、Workflow、Knowledge、Plugin、API/SDK 和平台二开边界；必须额外核验其 Runtime、权限和许可证与 Zuno Contract 的适配关系。
- [LangGraph 官方文档](https://docs.langchain.com/oss/python/langgraph/overview)：参考持久化、durable execution 和 Human-in-the-loop 能力；Zuno 仍拥有自己的业务事实、Proposal、Approval、Effect 和 Reconciliation 语义。

## CHANGE-001

```text
Change ID：CHANGE-001
Source Cluster IDs：CLUSTER-001, CLUSTER-003
Target：project facts / resume boundary
Problem：项目起点、真实用户、法院/学校关系、团队和个人贡献未知。
Current Design：正式事实保持 UNKNOWN，红蓝材料存在候选重建。
Proposed Design：先建立 User Fact Gate：历史需求、团队、个人贡献、交付状态和法律场景分别确认；未确认项不进入简历或 Current。
Decision：APPROVED_WITH_AMENDMENTS
Why：这是事实问题，增加架构文字不能解决；先补证据或接受 Unknown。
Alternatives：继续用 Target Architecture 解释历史；REJECTED，因为会制造真实性风险。
Affected Modules：facts, Product Surface, Resume boundary
Contract Changes：无
Migration / Implementation Implication：收集历史材料，形成最小 A/B/C 候选和用户确认记录。
Evidence Needed：原始项目材料、Git/任务/发布记录、用户确认。
User Gate：APPROVED
Canonical Destination：docs/project/facts/；必要时 docs/status/ 与 docs/evidence/
Sync Status：PARTIAL
Canonical Paths：docs/project/facts/project-background.md; docs/project/facts/team-and-ownership.md; docs/project/facts/delivery-and-usage.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending
Validation Not Run：事实核验和用户确认未完成。
Retest IDs：NONE
```

## CHANGE-002

```text
Change ID：CHANGE-002
Source Cluster IDs：CLUSTER-002, CLUSTER-004
Target：product positioning / scope
Problem：Target Legal Agent Platform 的复杂度尚未由历史任务和规模证明。
Current Design：合同审查、Legal Domain Profile、11 逻辑模块和完整治理链均有 Target 设计。
Proposed Design：先锁定一个可核验的旗舰任务和人工确认点；Graph Global、长期 Memory、复杂 Tool Governance、多租户和生产灾备按证据逐步启用。
Decision：APPROVED_WITH_AMENDMENTS / SIMPLIFY
Why：先使产品任务、用户、最小 Work Product 和验收可证明，再扩展平台能力。
Alternatives：保留全量 Target 作为第一版；REJECTED，存在 OVERENGINEERING_GAP。
Affected Modules：01, 03, 05, 06, 08, 09, 10, 11
Contract Changes：需要后续确认 Task Profile 与最小 Evidence/Review Contract；本轮不改。
Migration / Implementation Implication：建立一条最小可观察 workflow 和基线，不启动新 Runtime Program。
Evidence Needed：真实用户任务、人工基线、规模和验收。
User Gate：APPROVED
Canonical Destination：docs/project/architecture/architecture.md；docs/project/modules/01-product-surface.md
Sync Status：PARTIAL
Canonical Paths：docs/project/architecture/architecture.md; docs/project/modules/01-product-surface.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending
Validation Not Run：Scope-down 需要用户确认历史任务和目标范围。
Retest IDs：NONE
```

## CHANGE-003

```text
Change ID：CHANGE-003
Source Cluster IDs：CLUSTER-002, CLUSTER-005
Target：02 Ingestion
Problem：RAGFlow/Docling/MinerU 与 Zuno DocumentVersion、ParseSnapshot、SourceSpan、Redline 和权限 Contract 的适配面尚未验证。
Current Design：02 有完整 Native Target，开源候选为 TO_REVIEW。
Proposed Design：以 DocumentPipelineContract 为 Zuno 边界，对 RAGFlow/Docling/MinerU 做 Adapter Spike；候选只负责解析/通用索引能力，Zuno 保留不可变版本、SourceSpan、权限和审计事实。
Decision：APPROVED_AS_EXTEND_CANDIDATE
Why：官方 RAGFlow 当前提供深度文档理解、可编排 ingestion、MinerU/Docling、MCP/Memory/Agent 能力，直接重复建设缺少证据；但 Contract Fit 尚未通过。
Alternatives：重度 Fork RAGFlow；BUILD 全部 Native；均待 G3/G5 证据。
Affected Modules：02, 03, 08, 09, 10, 11
Contract Changes：DocumentPipelineContract 候选；不在本轮正式冻结。
Migration / Implementation Implication：固定法律样本验证结构、表格、SourceSpan、失败、版本和退出路径。
Evidence Needed：源码版本、License/运营评估、Spike、结构/引用/延迟/成本结果。
User Gate：APPROVED
Canonical Destination：docs/project/modules/02-input-document-ingestion.md；docs/decisions/
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/02-input-document-ingestion.md; docs/decisions/
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; Adapter Spike not executed
Validation Not Run：未执行 Adapter Spike 或 Contract Conformance。
Retest IDs：NONE
```

## CHANGE-004

```text
Change ID：CHANGE-004
Source Cluster IDs：CLUSTER-002, CLUSTER-006
Target：03 Knowledge
Problem：GraphRAG 被面试叙事理解为默认路径，当前 Conditional Retrieval 仍缺 Query-Class Benchmark。
Current Design：03/ADR 0006 已提出 Evidence Requirement、Basic/Hybrid/Local/Global/DRIFT 和 Evidence Evaluation；ADR 是 accepted-target overlay，未完成协调实现。
Proposed Design：将上位能力固定为 Conditional Evidence Retrieval；BM25/Structural、Dense、Rerank、Graph Local/Global/DRIFT 作为可替换 Provider，通过 EvidenceRequirement 和统一 Evidence Contract 选择；只在分层结果证明有收益时启用 Graph。
Decision：APPROVED
Why：Microsoft GraphRAG 官方同时提供 Basic、Local、Global、DRIFT，且不同 Query 适用范围和成本不同；Always Graph 缺乏理由。
Alternatives：Always Graph；Fixed Vector；二者都不作为默认总策略。
Affected Modules：03, 04, 06, 10
Contract Changes：Evidence Requirement/Provider Selection/Evidence Evaluation 需要后续协调；本轮不改。
Migration / Implementation Implication：固定 Query Class、错误 Graph、Version/Authority/Permission 样本，比较五种策略。
Evidence Needed：分层 Recall、Support、Citation、Unsupported、Latency、Cost 和停止原因。
User Gate：APPROVED
Canonical Destination：docs/project/modules/03-knowledge-agentic-graphrag.md；docs/decisions/0006-evidence-driven-agentic-graphrag.md；docs/project/modules/10-observability-eval.md
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/03-knowledge-agentic-graphrag.md; docs/project/modules/10-observability-eval.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending
Validation Not Run：Benchmark 与 ADR 协调未完成。
Retest IDs：NONE
```

## CHANGE-005

```text
Change ID：CHANGE-005
Source Cluster IDs：CLUSTER-002, CLUSTER-007
Target：05 Memory
Problem：Memory Engine 与 Memory Governance 尚未形成候选 Backend 的 Fit Analysis，当前 Target 容易被解释成全部自研。
Current Design：05 定义 Working/Session/Long-term、Candidate、Version、Conflict、Quarantine、ContextPack；候选 Backend 为 TO_REVIEW。
Proposed Design：保留 Zuno Memory Governance（写入、冲突、时间、权限、Provenance、适用性、ContextPack），把存储、层级上下文和基础召回抽象为 MemoryBackend SPI，评估 OpenViking/Mem0/Graphiti。
Decision：APPROVED_AS_EXTEND_CANDIDATE
Why：OpenViking 官方将 Memory、Resource、Skill 统一为 Context Database，并提供分层加载、递归检索、Session 管理和轨迹观测；它可减少 Engine 重复建设，但不能替代 Zuno 的法律范围/权限/版本治理。
Alternatives：把 OpenViking 直接当 Canonical Memory；全部 Native；均需 Contract/Benchmark 证据。
Affected Modules：05, 03, 06, 09, 10, 11
Contract Changes：MemoryBackend SPI 候选；不在本轮正式冻结。
Migration / Implementation Implication：用污染、冲突、过期、撤权和 Context Budget 数据集做 Backend Conformance。
Evidence Needed：官方版本、License/部署、写入/召回/权限/重建 Spike 和质量成本数据。
User Gate：APPROVED
Canonical Destination：docs/project/modules/05-memory-context.md；docs/decisions/
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/05-memory-context.md; docs/decisions/
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; Memory Backend Spike not executed
Validation Not Run：Memory Backend Spike 未执行。
Retest IDs：NONE
```

## CHANGE-006

```text
Change ID：CHANGE-006
Source Cluster IDs：CLUSTER-005, CLUSTER-008
Target：06 Agent Core
Problem：Agent Core 的 Zuno Delta 与 LangGraph Runtime 责任在 Current 证据上仍未分离证明。
Current Design：Target 采用 Single Controller，LangGraph 作为低层 durable execution/checkpoint 候选；Zuno 保留 Plan、Run、Proposal、Final Gate 和业务事实。
Proposed Design：KEEP Single Controller 和 Zuno Domain Control Plane；把 LangGraph 限定为可替换 AgentRuntime Provider，必须通过 Checkpoint/Domain Fact Reconciliation、Proposal/Publication 和 Failure Contract。
Decision：APPROVED / KEEP
Why：LangGraph 官方定位是低层 Agent orchestration，支持 durable execution、persistence、interrupt/HITL；这与 Zuno 保留业务控制语义的边界一致。
Alternatives：把 LangGraph Checkpoint 当业务事实；引入自治多 Agent；均违反当前 Target 原则。
Affected Modules：01, 06, 10, 11
Contract Changes：需要后续 Runtime Conformance Evidence，不在本轮修改。
Migration / Implementation Implication：补 Current/Target 对照、崩溃恢复、迟到分支和 Final Gate 测试。
Evidence Needed：代码、Checkpoint/Domain Trace、故障测试和替换 Provider Spike。
User Gate：APPROVED
Canonical Destination：docs/project/modules/06-agent-core-planning-control.md；docs/project/architecture/architecture.md
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/06-agent-core-planning-control.md; docs/project/architecture/architecture.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending
Validation Not Run：Runtime Conformance 未执行。
Retest IDs：NONE
```

## CHANGE-007

```text
Change ID：CHANGE-007
Source Cluster IDs：CLUSTER-009
Target：07/08/09 Tool Governance
Problem：Tool Registration、Installation、Connection、Grant、Delegation、Selection、PreparedAction 和 Effect Reconciliation 的 Current 实现/Provider conformance 未证。
Current Design：Target 已明确多层权限交集、Operation 粒度、Security Epoch、Approval、Idempotency 和 UNKNOWN。
Proposed Design：不扩展 Tool 数量；先实现/验证一个受控邮件 Provider 的完整链路，记录 ToolVersion、Connection、Grant lineage、Approval、Action Hash、Epoch、Attempt、Receipt 和 Reconciliation。
Decision：APPROVED_AS_IMPLEMENTATION_EVIDENCE_GAP / Architecture KEEP
Why：面试风险集中在副作用安全和授权，而不是 MCP 数量；一条完整可测链比多 Tool 目录更有证据价值。
Alternatives：先支持更多 MCP；DEFER，避免扩展未验证的副作用面。
Affected Modules：01, 07, 08, 09, 11
Contract Changes：无新增正式 Contract；按既有 Target 做 Conformance。
Migration / Implementation Implication：构造 timeout、schema change、revocation、duplicate、unknown effect Fault Test。
Evidence Needed：Provider/Connection/Grant/Approval/Effect Trace、权限撤销和人工对账结果。
User Gate：APPROVED
Canonical Destination：docs/project/modules/07-capability-skill.md；docs/project/modules/08-tool-runtime.md；docs/project/modules/09-security.md
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/07-capability-skill.md; docs/project/modules/08-tool-runtime.md; docs/project/modules/09-security.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; Conformance/Fault Test not executed
Validation Not Run：Tool Conformance 和 Fault Test 未执行。
Retest IDs：NONE
```

## CHANGE-008

```text
Change ID：CHANGE-008
Source Cluster IDs：CLUSTER-002, CLUSTER-009
Target：Enterprise Connector
Problem：Zuno 是否应自行维护大量企业 Connector，尚未与成熟同步/权限能力比较。
Current Design：Connector Provider 方向为 TO_REVIEW，Canonical SourceObject/Access Contract 由 Zuno 保留。
Proposed Design：评估 Onyx Connector 作为同步/连接 Provider 或 Adapter；Onyx 负责连接器状态、同步和可选权限同步，Zuno 仍负责 SourceObject、DocumentVersion、Access Contract、Matter 权限和证据引用。注意其权限同步能力与版本/授权范围需核实。
Decision：APPROVED_AS_ADOPT_CANDIDATE / NOT FINAL ADOPT
Why：官方文档显示 Onyx Connector 支持持久同步、源权限同步选项、索引状态和多种企业数据源；直接复制连接器不一定有差异化。
Alternatives：全量 Native Connector；只吸收接口模式；需通过 G1–G5 决定。
Affected Modules：02, 03, 09, 11
Contract Changes：ConnectorProvider/Canonical SourceObject 候选；不在本轮冻结。
Migration / Implementation Implication：固定一个来源验证权限、删除、增量同步、失败和重建。
Evidence Needed：Onyx 版本、License/Edition、权限同步行为、Adapter Spike 和退出方案。
User Gate：APPROVED
Canonical Destination：docs/project/modules/02-input-document-ingestion.md；docs/project/modules/09-security.md；docs/decisions/
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/02-input-document-ingestion.md; docs/project/modules/09-security.md; docs/decisions/
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; Connector/Permission Spike not executed
Validation Not Run：Connector/permission Spike 未执行。
Retest IDs：NONE
```

## CHANGE-009

```text
Change ID：CHANGE-009
Source Cluster IDs：CLUSTER-006, CLUSTER-010
Target：10 Observability & Eval
Problem：当前质量和生产证据未建立，架构主张无法用单一分数证明。
Current Design：Target 定义分层 Eval、Evidence Sufficiency、Finding、Tool、Memory 和 Release Gate；Current 状态 blocked_not_measured。
Proposed Design：先建立 Query-Class、Document-Version、Permission、Failure 和 Work Product 分层 Benchmark；将 Retrieval、Finding、Unsupported、Abstention、Tool UNKNOWN、成本/延迟和 Attorney Agreement 分开报告。
Decision：APPROVED_WITH_AMENDMENTS
Why：评测 Contract 是 Zuno 必须拥有的控制面，不能由外部 Backend 的 Demo 指标替代。
Alternatives：引用公开 Benchmark 或单一 Accuracy；REJECTED，因为不能证明 Zuno 的 Contract 和业务适用性。
Affected Modules：03, 05, 06, 08, 09, 10
Contract Changes：Eval Profile/Release Gate 候选；不在本轮正式冻结。
Migration / Implementation Implication：创建固定数据集、Bad Case、指标实现和阻塞状态报告；不创建 Runtime Program。
Evidence Needed：数据集版本、运行报告、成本/延迟、失败注入和发布决策。
User Gate：APPROVED
Canonical Destination：docs/project/modules/10-observability-eval.md；docs/status/；docs/evidence/
Sync Status：PARTIAL
Canonical Paths：docs/project/modules/10-observability-eval.md; docs/status/; docs/evidence/
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; Benchmark not run
Validation Not Run：Benchmark 未运行，当前状态必须保持 blocked_not_measured。
Retest IDs：NONE
```

## CHANGE-010

```text
Change ID：CHANGE-010
Source Cluster IDs：CLUSTER-003, CLUSTER-008, CLUSTER-010
Target：model adaptation / resume scope
Problem：Fine-tuning、DPO、Self-hosted、GPU 和模型部署主张没有历史或实验依据。
Current Design：Technology Reality 全部 UNKNOWN；Model Profile/Training Lifecycle 是 Target/Proposal。
Proposed Design：在事实确认和 Baseline 之前 DEFER Fine-tuning/自建 Serving；面试与简历只保留已确认的模型调用/研究范围，若未来训练则从数据治理、Baseline、Ablation 和 Artifact Gate 开始。
Decision：APPROVED / DEFER
Why：没有训练/部署证据时继续扩写会提高 Resume Claim Risk，且不能用 Target Model Portfolio 替代历史经历。
Alternatives：把 Legal SFT、DPO、GPU 和模型部署作为已做项目；REJECTED。
Affected Modules：04, 10, 11, Resume boundary
Contract Changes：无
Migration / Implementation Implication：先做 Fact Gate 和模型现实清单，不创建训练或 Serving Program。
Evidence Needed：调用配置、Provider、实验数据、Artifact、GPU/Endpoint、发布/回滚记录。
User Gate：APPROVED
Canonical Destination：docs/project/facts/technology-reality.md；docs/project/modules/04-model-gateway.md；docs/status/；Resume source
Sync Status：PARTIAL
Canonical Paths：docs/project/facts/technology-reality.md; docs/project/modules/04-model-gateway.md
Applied Commit SHA：NONE
Validation Run：NOT RUN - Commit A pending; training/serving evidence not run
Validation Not Run：模型事实和用户贡献未确认。
Retest IDs：NONE
```
