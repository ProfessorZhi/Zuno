# 术语表

## 用途

本文只统一当前 Zuno 文档体系中的公开术语，不拥有第二套架构。总体 Target 以 [`docs/architecture/architecture.md`](./architecture/architecture.md) 为准，模块内部语义以 [`docs/modules/`](./modules/README.md) 为准，长期决策由 [`docs/decisions/`](./decisions/README.md) 约束，Current 事实由 [`docs/evidence/`](./evidence/README.md) 证明。

旧 11 模块、旧专题和 Red / Blue 过程内容不从术语表恢复为当前架构。

## 状态标签

- **Current**：已有代码、Migration、测试、Trace、Eval 或真实运行证据证明。
- **Foundation**：已有最小工程基础，但不能据此声称完整模块行为或质量已经证明。
- **Target**：当前接受的目标架构，尚未完全实现。
- **Future**：更长期可选方向，不属于当前 Target 基线。
- **Gap / Unknown**：缺少设计闭合或工程证据。
- **History**：被替换或仅用于复盘的历史内容。
- **Production Ready**：必须另有运行、安全、恢复、评测和运维证据；文档完成不能产生这个状态。

## 总体架构术语

### Generic Host（通用 Agent 宿主）

已经能够提供界面、会话、普通工作流、模型调用、基础检索、工具调用或结果展示的通用平台。Zuno 可以被这类宿主调用，也可以独立提供产品入口。通用宿主不自动拥有 Zuno 的法律领域权威。

### Domain State（领域状态）

法律业务世界正式承认的长期事实和版本。第一阶段最小 Canonical Kernel（正式领域内核）为 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct。Owner：02 Legal Domain & Work Product（法律领域与工作成果）。

### Runtime Control State（运行控制状态）

一次复杂任务执行到了哪里，包括 AgentRun、PlanVersion、StepRun、分支、预算、中断、Checkpoint 和 RunOutcome。Owner：04 Agent Runtime & Control（智能体运行与控制）。Runtime Control State 不能替代 Domain State。

### Knowledge Projection（知识派生视图）

围绕正式 DocumentVersion 生成的可重建解析、OCR、切分、关键词、向量、图和其他检索视图。Owner：03 Knowledge & Evidence（知识与证据）。知识派生可以重建，不能直接改写正式法律结果。

### Optional Context Provider（可选上下文提供方）

提供工作上下文、会话摘要、偏好或长期记忆的可替换边界。它不是一级逻辑模块，Long-term Memory（长期记忆）只有在消融 / 评测证明收益后才启用。Memory 不能成为正式领域真相。

### External Effect State（外部效果状态）

PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt 等与现实世界动作相关的状态。Owner：06 Tool Runtime & Effects（工具运行与外部效果）。外部结果未知时进入 Reconcile（对账），禁止盲目重试。

### Telemetry Projection（遥测派生视图）

Trace、Metric、日志、评测投影和诊断视图。Owner：09 Observability & Evaluation（可观测性与评测）。Telemetry 不能替代 Domain、Security、Effect 或 Durable Audit 事实。

## 02 法律领域与工作成果

### Matter（事项）

一个需要长期保存业务事实、材料、证据、结论和工作成果的法律业务范围。

### DocumentVersion（材料版本）

某一份材料的不可变业务版本，是知识派生、证据来源和正式历史引用的稳定锚点。Owner：02。Index ID、Chunk ID 或对象存储内部 ID 不能替代它的业务身份。

### Claim（主张）

被正式记录的业务主张，可由 Evidence 支持或反驳，并可能影响 Finding。

### Evidence（正式证据）

已经经过领域准入、具有稳定来源和业务关系的正式证据。与 03 的 EvidenceCandidate（证据候选）不同。

### Finding（正式结论）

经过必要证据、质量和人工业务判断后正式形成的结论版本。新 Evidence 可能使既有 Finding 进入 review-required / stale 语义。

### HumanDecision（人工业务决定）

专业人员对法律业务结果做出的接受、修改、拒绝或要求补充等正式判断。它属于 Domain State，不等于安全侧 ApprovalDecision（审批决定）。

### WorkProduct（工作成果）

对内或对外交付的版本化专业成果。正式版本需要能够回到所依据的材料、证据、结论和必要人工决定。

### Formal Admission（正式准入）

把 Proposal / Candidate（候选结果）提升为正式 Domain State 的领域边界。模型、知识、能力和 Runtime 都不能绕过 Formal Admission 直接提交正式结果。

### AdmissionReceipt（正式准入回执）

证明某次 run / PlanVersion / StepRun / proposal / idempotency identity 导致某个 resulting DomainVersion 的耐久因果事实。Domain mutation 与匹配 AdmissionReceipt 必须在同一个 Domain transaction durability boundary（领域事务耐久边界）提交。

### WorkProductCitationBinding（工作成果历史引用绑定）

正式 WorkProductVersion 当时实际采用的不可变 DocumentVersion、稳定来源位置和必要来源 hash / evidence hash。Owner：02。它不能随着 Index rebuild（索引重建）漂移。

### WorkProductInvalidationFact（工作成果失效事实）

声明某个正式 WorkProductVersion 已经因新材料或正式依赖变化而 stale / review-required 的 Domain fact。它不同于失效通知是否送达，也不同于外部消费者是否确认收到。

## 03 知识与证据

### KnowledgeGeneration（知识生成版本）

围绕一组明确 DocumentVersion 和 processing spec（处理规格）建立的一代可重建知识派生。它可以处于 processing、staged / built、serving、stale、failed 等语义阶段。具体 enum 尚未冻结。

### Serving Generation / Serving Watermark（当前服务生成版本 / 服务水位）

03 知识边界认可为当前可以提供检索的 generation。单个 index write 成功不能自动移动 Serving Watermark。

### ReadinessDecision（知识就绪判断）

针对某次 task scope，根据 DocumentVersion、serving KnowledgeGeneration、最低处理 / 检索要求和当前 Security 条件，判断 READY / PARTIAL / BLOCKED 类语义。

关键不变量：

```text
KnowledgeGeneration lifecycle
!=
task-level ReadinessDecision
```

一个 generation 可以构建完成，但某个要求扫描表格的任务仍然 BLOCKED；同一 generation 对另一个只需要正文定位的任务可能 READY。

### EvidenceCandidate（证据候选）

03 在当前允许的材料、Scope 和 generation 中恢复出的候选证据。它具有来源和引用信息，但还不是 02 的正式 Evidence。

```text
EvidenceCandidate != Evidence
```

### CitationLineage（检索引用链）

解释某个 EvidenceCandidate 当时怎样从指定 DocumentVersion / KnowledgeGeneration / retrieval path 被找到和排序。Owner：03。

它不同于正式 WorkProductCitationBinding：

```text
CitationLineage
    = 候选怎样被找到

WorkProductCitationBinding
    = 正式成果当时实际采用了什么
```

### RetrievalResult（检索结果）

一次检索 / 重排的任务级输出，绑定 query / task scope、KnowledgeGeneration、EvidenceCandidate 和必要 CitationLineage refs。它不是正式业务结论。

### GraphRAG（图增强检索）

按 Query Class（问题类别）和 Evidence Gate（证据门）启用的条件能力，不是所有检索的默认主干。只有对照实验能够证明稳定收益后才扩大使用范围。

### Native BM25（本地 BM25）

本地 BM25 排序算法。Elasticsearch 等外部引擎可以提供 BM25 scoring，但 Provider 不等于算法本体。

### RRF Fusion（倒数排名融合）

一种多路召回粗融合方法。具体参数属于实现 / Evaluation 范围，不是当前总体架构的长期业务 Contract。

## 04–09 关键术语

### PlanVersion（计划版本）

04 Runtime 中激活后不可变的计划版本。Replan（重规划）创建新的 PlanVersion，而不是原地修改已经激活的计划。

### Retry（重试）

计划、依赖、能力和安全假设仍然成立，只是一次执行暂时失败时再次执行。

### Replan（重规划）

计划结构、依赖、能力、权限或事实假设已经失效，需要建立新的 PlanVersion。

### Reconcile（对账）

外部副作用结果未知时，通过操作身份、幂等键、Receipt 或外部状态确认现实世界究竟发生了什么。不是普通 Retry。

### Capability（专业能力）

05 提供的版本化专业分析 Contract，例如事件抽取、冲突检测、事实—法条对应和法律适用性。Capability 输出是 Proposal / Candidate / Observation / Reference，不直接成为 Domain State。

### Skill（技能）

对一组能力调用方式、约束或组合的可复用封装。Skill 不等于 Tool，也不自动拥有外部副作用。

### PreparedAction（准备动作）

06 在现实副作用执行前固定操作身份、参数、工具 / 能力版本、幂等身份和必要安全引用的动作表示。

### EffectReceipt（效果回执）

06 对一次外部动作结果的耐久记录。它记录 Zuno 已确认的执行结果，但外部系统仍拥有其内部现实事实。

### AuthorizationDecision（授权决定）

08 Security & Governance（安全与治理）对“当前主体是否可以在当前 Scope 做某项受保护访问 / 操作”的权威决定。

### ApprovalDecision（审批决定）

08 对高风险动作是否获得所需批准的安全事实。它不同于 02 的 HumanDecision。

### Security Epoch（安全策略版本）

用于说明授权 / 策略判断依赖的当前安全版本。长任务中的新读取、模型外发、工具执行和正式准入不能无限复用已经失效的旧授权。

### Effective Lifecycle Policy（有效生命周期政策）

Retention（保留）、Deletion（删除）、Legal Hold（法律保全）和 Compliance Exception（合规例外）的权威政策。Owner：08；各 Store 是执行 Owner。

### AuditPersistenceReceipt（审计持久化回执）

证明某个被要求耐久化的 Audit Fact 已经成功进入对应耐久边界的 Receipt。普通 Trace / LangSmith / OpenTelemetry 不能替代它。

### OTel-compatible Telemetry Contract（OpenTelemetry 兼容遥测契约）

09 使用的 Provider-neutral（提供方中立）遥测边界。LangSmith 可以是首选 Agent Trace / Eval Provider，但不是架构唯一事实源。

## Current 代码名与 Target 架构名的关系

以下名称可以作为当前代码或工程证据中的实现名出现，但不能因为代码存在就自动成为 Target 责任域或正式业务对象：

- `GeneralAgent` / `GeneralAgent single loop`：当前或历史运行实现名；Target Runtime 仍以 04 Agent Runtime & Control 的责任语义描述。
- `KnowledgeQueryService`：当前 application knowledge query service；不能替代 03 模块完整 Target。
- `GraphRAGQueryService`：当前 GraphRAG query runtime / service surface；GraphRAG Target 仍是条件能力。
- `GraphRAGProjectSnapshot`：实现层 project / config snapshot；不是 Domain State。
- `KnowledgeQueryResult`：实现层查询结果；不自动等于 Target `RetrievalResult`、`EvidenceCandidate` 或正式 Evidence。
- `ToolCard`：工具、MCP connector、skill 或 knowledge capability 的轻量检索元数据；不是完整 tool schema，也不是 Capability 本体。

Current 代码名用于 Evidence 和代码导航；Target 架构名用于责任、Contract 和长期语义。两者只有在 Evidence 明确证明实现对齐以后，才可以声明某项 Target 已经进入 Current。

## 退休 / 非 Canonical 术语

以下名称不属于当前架构入口或当前默认 Target：

- `Domain Pack`
- `domain_pack_id`
- `DomainQAGraph`
- `MultiAgentSupervisorGraph`
- “11 个逻辑模块 = 11 个微服务”
- Persistent Autonomous Multi-Agent Runtime（持久自治多智能体运行时）作为默认产品运行模式

Event、Conflict、Dispute、LegalIssue、ApplicableLaw、SimilarCase 等不是“退休概念”，但第一阶段默认属于 Proposal / Projection / Derived View / Capability Output，而不是新的 Canonical Domain Object。
