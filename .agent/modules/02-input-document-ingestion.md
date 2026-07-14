# 02 Input / Document Ingestion

updated: 2026-07-14
status: normative-target-module-architecture
module_number: 02
formal_path: `docs/modules/02-input-document-ingestion.md`

> 本文是 Zuno 第 02 个逻辑模块——Input / Document Ingestion——唯一的正式 Target 架构主设计。
>
> 本文定义企业级输入接入、原始证据保全、文件完整性、异步解析、结构化转换、OCR / VLM 升级、质量门、版本、删除传播和跨模块 Handoff 的目标边界。本文不描述 Current 实现事实，不包含迁移阶段、执行排期或 Codex 实施计划。Current、Gap、Measurement 与 Production Readiness 仍由 `docs/status/production-readiness.md`、最新代码、Migration、测试、Trace 和 Eval 维护。

## 0. 文档边界与规范优先级

本文统一承载：

```text
问题、目标与非目标
双输入入口与统一 Ingestion Kernel
完整上传、解析、重解析、同步、删除和临时附件流程
原始文件完整性、篡改检测、版本化与 Provenance
多格式、页面级、区域级 Parser 路由
CanonicalDocumentIR、SourceSpan、Transform Ledger 与质量门
异步 Queue、Inbox / Outbox、Lease、Fencing、Retry、Fallback 与 Recovery
PostgreSQL、S3-compatible Object Store、Redis 和 Worker Runtime 边界
02 → 03 Knowledge、02 → 06 Agent Core、02 ↔ 09 Security、02 ↔ 11 Infrastructure Contract
目标代码目录、数据库表、API、测试、Eval 和完成证据
```

文档边界：

```text
docs/modules/02-input-document-ingestion.md
    本模块唯一 Target 架构事实源。

.agent/programs/
    Current → Target 的实现、迁移、切流、回滚和收口计划。

docs/status/
    Current、Gap、Measurement、Quality 与 Production Readiness。

docs/decisions/
    只有跨模块、不可逆或需要权衡记录的独立决议。
```

规范优先级：

```text
全局架构原则
→ Wave 1 已确认跨模块 Contract / ADR
→ 本模块 Target 架构
→ 后续已确认 Program
→ 代码、Migration、测试与运行证据
```

任何 Program 或实现不得自行改变本文已经确认的 Ownership、状态、错误、恢复、安全与 Contract 原则。本文中出现的类名、表名、目录、Provider 或模型仅是 Target 规格，不代表已经实现。

### 0.1 文档内部规范层级

```text
Part I–III
    问题、边界、概念架构和完整业务流程。

Part IV–VII
    领域对象、状态机、解析、异步、存储和跨模块 Contract。

Part VIII–IX
    Failure、Security、Observability、Eval、代码与数据库实现规格。

Part X
    架构 Requirement、验证方式和完成证据。
```

字段、状态、Policy 和不变量是规范性内容。示例流程和技术候选不得覆盖规范性 Contract。

---

# Part I：定位、问题与 Ownership

# 1. 为什么需要企业级 Ingestion

企业知识资料不是“上传后提取一段文本”这么简单。输入层面对的是：

```text
文件格式不同
同一文件中页面性质不同
原始文件可能被替换或篡改
扫描件需要 OCR
表格、公式、图片、批注和隐藏内容容易丢失
Parser、模型和配置升级会改变结果
大文件处理耗时，需要异步、并行和恢复
重复上传、重复消息和 Worker 重启会重复执行
用户删除文件后，解析结果和 Knowledge 索引可能继续存在
远程 OCR / VLM 可能违反数据驻留和隐私要求
模型输出看似完整，但可能遗漏、改写或虚构原文
```

传统“清洗 → 纯文本 → 切 Chunk”会造成：

```text
无法证明答案来自哪一页、哪个区域
无法区分原文、确定性规范化和模型推断
Parser 升级后无法重放和比较
文件被覆盖后无法发现
页眉、脚注、批注、修订、公式、隐藏 Sheet 等信息永久丢失
进程崩溃后不清楚任务是否已经完成
对象已上传但数据库未提交，形成孤儿文件
数据库已提交但消息未发送，下游永远不处理
```

一句话定义：

> Input / Document Ingestion 是 Zuno 的证据保真输入平台。它把外部输入转换为可验证、可版本化、可恢复、可审计的内部文档事实，同时保留原始字节、结构、位置、不确定性和转换链；只有通过质量与安全门的不可变 ParseSnapshot 才能交给 Knowledge 或 Agent Core 使用。

# 2. 模块目标

Input / Document Ingestion 必须达到：

1. **原始证据保全**：原文件不可被清洗结果替代；任何派生结果都可回溯到原始字节。
2. **多格式统一**：不同格式通过 Adapter 转换为统一 `CanonicalDocumentIR`，不把领域 Contract 绑定到具体 Parser。
3. **信息不静默丢失**：结构、表格、公式、图片、脚注、批注、修订、隐藏内容和失败区域必须保留或显式声明缺失。
4. **完整性可验证**：上传、对象提交、Parser 读取、ParseSnapshot 和 Handoff 均有 Hash、版本与校验。
5. **篡改可发现**：原文件、元数据、Parser Bundle、模型权重和派生产物变化可被检测并审计。
6. **异步可恢复**：大文件、OCR、VLM 和批量同步通过持久队列、Lease、Fencing、Inbox / Outbox 和 Reconciler 执行。
7. **低延迟与高吞吐并存**：在线附件与批量知识摄取共享内核，但使用不同优先级、预算和 Processing Profile。
8. **自适应解析**：文件级 Profiling 后可按页面和区域路由 Native、Layout、OCR、VLM 或 Human Review。
9. **质量先于索引**：Parser 返回内容不等于成功；必须经过确定性质量检查和必要的冲突处理。
10. **安全先于外发**：远程 Parser、OCR 或 VLM 调用必须经过 Security、Residency、Credential、Budget 和 Model Gateway。
11. **版本和重解析分离**：源内容变化创建新 DocumentVersion；Parser 或配置变化创建新 ParseSnapshot。
12. **删除闭环**：逻辑不可见、领域 Tombstone、Knowledge 删除和物理清理必须可追踪并有 Receipt。
13. **Provider-neutral**：模块 Contract 不暴露 Docling、MinerU、PaddleOCR、Tika、Unstructured 或具体云 API 的对象。
14. **可观测可评测**：每个阶段有 Trace、Metric、Quality Report、Failure 和项目级 Golden Eval。
15. **弱模型可实现**：Target 字段、状态、边界和测试要求足够明确，不依赖实现者自行猜测架构原则。

# 3. 非目标

Input / Document Ingestion 不负责：

```text
Agent 任务规划、Step 调度、Reflection 或最终回答
Knowledge 的 Chunk 策略、Embedding、BM25、Vector、Graph 或 KnowledgeVersion
最终 Evidence 合成和 Citation 绑定
模型 Provider / Model 的最终路由、计费和 Circuit 状态
Security Authorization、数据分类、Retention 或 Legal Hold 的政策决策
对象存储、Queue、Redis、数据库和 Worker Lease 的物理实现
把模型输出直接提交为不可争议的原文事实
把所有 Connector、音视频、手写和专业格式作为首版完成前提
```

Input 可以编排 Parser 和请求模型能力，但不能冒充 Model Gateway、Security、Infrastructure 或 Knowledge 的事实 Owner。

# 4. 双输入入口与统一内核

Zuno 有两个业务输入入口：

```text
在线任务输入
    用户问题、临时附件、图片、知识范围和输出要求。

知识摄取输入
    文件上传、URL、Git、对象存储、企业 Connector 和批量同步。
```

两个入口的业务目标不同，但文件处理能力不得重复建设：

```text
Online Attachment Surface ─┐
                           ├→ Unified Ingestion Kernel
Durable Knowledge Surface ─┘
```

共享能力：

```text
文件接收与完整性校验
MIME / Format 检测
安全 Preflight
对象提交
Source Profiling
Parser Capability 与路由
CanonicalDocumentIR
SourceSpan
Transform Ledger
Quality Gate
ParseSnapshot
Failure / Retry / Recovery
```

差异只允许体现在：

```text
Processing Profile
Priority Class
Deadline
Retention
是否允许 Progressive Availability
是否请求 03 Knowledge 建立长期索引
是否允许远程 Parser
质量阈值
资源与成本预算
```

禁止：

```text
Agent 附件在 Graph Node 内直接调用 PyMuPDF
Agent 附件走一套图片描述逻辑，知识库走另一套 OCR 逻辑
同一种文件在不同入口生成不兼容 SourceSpan
临时附件因为生命周期短而绕过安全和完整性检查
```

# 5. Cross-module Ownership

## 5.1 Input / Ingestion Owns

```text
InputSubmission
UploadSession
SourceObject
SourceIntegrityReceipt
WorkspaceFile
Document
DocumentVersion
SourceProfile
ParsePlan
ParseJob
ParseAttempt
ParseTask
ParseSnapshot
CanonicalDocumentIR
DocumentBlock
DocumentAsset
原始 SourceSpan
TransformRecord / TransformLedger
MissingContentManifest
ParserQualityReport
ParseConflict
IndexableDocumentSnapshot
IngestionHandoff
IngestionDeletionRequest
Ingestion Domain Event
```

## 5.2 Knowledge Owns

```text
RetrievalChunk
ParentChunk
CitationChunk
ChunkPolicy
Embedding
BM25 / Vector / Graph logical index
KnowledgeVersion
KnowledgeManifest
RetrievalRound
EvidenceLedger
CitationLineage
Knowledge deletion propagation and verification
```

Input 不生成 `ParentChunk`、`CitationChunk`、BM25 Document、Vector Document、Graph Document、Evidence Item 或 KnowledgeVersion。

## 5.3 Agent Core Owns

```text
AgentRun
TaskContract
PlanVersion
StepRun
External Wait
INGESTION_COMPLETION Interrupt
RunOutcome
```

Agent Core 可以提交 Ingestion Job、等待和取消，但不能修改 ParseJob、ParseSnapshot 或 Quality Verdict。

## 5.4 Model Gateway Owns

```text
ModelRoleDefinition
ModelRoutingDecision
ModelCallAttempt
ModelResponse
UsageReceipt
Provider Failure
Provider Health / Circuit
```

Input 对文档 VLM 只提出能力请求和消费结构化结果。

## 5.5 Security Owns

```text
Upload Authorization
Data Classification
Allowed Parser / Provider
Residency
Malware and content policy
Redaction policy
Retention policy
Legal Hold decision
Effective Security Epoch
Credential scope
```

Input 执行并记录 Security Decision，不自行批准。

## 5.6 Observability & Eval Owns

```text
Trace / Metric / Log projection
Parser quality trend
Benchmark dataset
EvalRun
EvalResult
Release Gate evidence
```

Input 拥有业务质量事实，Observability 保存其投影和评测结果。

## 5.7 Infrastructure Owns

```text
Database Transaction primitive
Physical Object Store and ObjectCommit
Queue Message / Delivery
Inbox / Outbox primitive
WorkerLease / FencingToken
Redis cache primitive
Clock / Deadline
Migration / Backup / Restore
Storage encryption
Secret delivery
```

Infrastructure 不拥有 ParseJob 或 ParserQualityReport 的业务语义。

# 6. 架构不变量

1. 原始字节不可被规范化结果覆盖。
2. 所有派生产物必须引用输入 Hash、转换版本和输出 Hash。
3. `DocumentVersion` 只表示源内容业务版本，不包含 Parser 或模型版本。
4. 同一 DocumentVersion 可以有多个不可变 ParseSnapshot。
5. ParseSnapshot 激活后不可原地修改；修正、重解析或人工校正创建新 Snapshot。
6. `SourceSpan` 只表达原始来源位置，不包含 Knowledge Chunk ID。
7. Input 不决定 Retrieval Chunk、Embedding 或 Index Target。
8. Parser 成功返回不等于 Snapshot 可用；必须通过 Quality Gate。
9. 缺失、损坏、低置信度和不支持内容必须显式进入 `MissingContentManifest`。
10. `raw_text`、`normalized_text`、`search_view`、`derived_text` 不得混为同一字段。
11. 有可靠原生结构时，禁止先渲染成图片再 OCR 作为默认路径。
12. OCR 和 VLM 结果不得静默覆盖原生文本。
13. VLM 结果默认是 `MODEL_DERIVED`，除非经确定性验证或人工确认。
14. 上传、对象 Commit 和 Parser 读取必须验证内容 Hash。
15. 对象存储读取只接受 `COMMITTED` 且 Hash 匹配的对象。
16. Redis 只能加速，不能成为 SourceObject、ParseJob、Snapshot、安全或删除事实的唯一来源。
17. RabbitMQ / Queue 提供 at-least-once delivery；业务一致性依靠 Inbox、幂等和 Fencing。
18. Worker Lease 过期后的晚到结果必须被拒绝。
19. 数据库事务内不得执行对象上传、远程 HTTP、模型或 Parser 外部调用。
20. Domain Commit 与消息发布通过 Outbox 协调，不使用 XA / 2PC。
21. 同一 SourceObject 的物理字节可以在政策允许范围内去重，但逻辑 WorkspaceFile、Document 和 ACL 不合并。
22. 默认不得跨 Tenant 进行可观察的内容去重。
23. 临时附件和长期文件共享 Parser Contract，只使用不同 Retention 与 Profile。
24. 远程 OCR / VLM 必须经过 Security Gate 和 Model Gateway。
25. 任何 `BLOCK` Snapshot 不得发送给 Knowledge。
26. `DEGRADED` 只有 Processing Profile 和下游 Acceptance 都允许时才可 Handoff。
27. 文件删除首先使其对新请求不可见，再执行异步传播与物理清理。
28. Legal Hold 可以阻止物理 Purge，但不能使已撤权内容继续被新检索使用。
29. 前端显示不是状态事实源；所有状态必须从后端权威存储恢复。
30. 文档架构不依赖 MinIO、AWS S3、Docling、PaddleOCR 或特定供应商；这些都是 Adapter。

---

# Part II：概念架构与完整运行流程

# 7. 概念组件

```text
Input Gateway
Upload Session Service
Connector Intake Service
Attachment Intake Service
Security Preflight Coordinator
Content Type Detector
Archive / Container Inspector
Object Commit Coordinator
Source Registry
Integrity & Provenance Service
Source Profiler
Parser Capability Registry
Processing Profile Registry
Parse Planner
Parse Orchestrator
Task Dispatcher
Native Parser Adapters
Layout Parser Adapters
OCR Adapters
Document VLM Adapter
Canonicalization Engine
Transform Ledger Service
SourceSpan Builder / Validator
Missing Content Collector
Parser Quality Engine
Conflict Resolver
ParseSnapshot Repository
Handoff Publisher
Deletion Coordinator
Ingestion Query Service
Progress Projection Publisher
Reconciliation Services
```

这些组件初期可以位于同一 backend codebase，并按 API / CPU Worker / GPU Worker / Maintenance Role 部署。模块边界由 Contract、Ownership、状态和测试证明，不以微服务数量证明。

# 8. 统一端到端流程

## 8.1 长期知识文件上传

```text
1. Product/API 解析 Principal、Tenant、Workspace。
2. Security 返回 UploadAuthorization 与 EffectiveSecurityEpoch。
3. Input 创建 UploadSession 和受约束 ObjectCommit。
4. 客户端或服务端将字节上传到 staging object。
5. Infrastructure 验证 size、hash、media metadata。
6. PostgreSQL 事务提交 SourceObject、WorkspaceFile、Document、DocumentVersion 和 Outbox。
7. Outbox 发布 SOURCE_COMMITTED。
8. Profiler Worker 读取已提交对象并再次校验 Hash。
9. SourceProfiler 生成 SourceProfile。
10. ParsePlanner 根据 Profile、能力、预算和安全生成不可变 ParsePlan。
11. ParseOrchestrator 创建 ParseJob、ParseTask DAG 并异步 Dispatch。
12. Native / Layout / OCR / VLM Worker 执行页面或区域 Task。
13. Join 组合结果，Canonicalization 生成 CanonicalDocumentIR。
14. SourceSpan Validator、Transform Ledger 和 MissingContentManifest 完成。
15. ParserQualityEngine 产生 PASS / DEGRADED / BLOCK。
16. PostgreSQL 事务提交不可变 ParseSnapshot 和 Handoff Outbox。
17. 02 通过 CrossModuleEnvelope 发送 IndexableDocumentSnapshot 给 03。
18. 03 返回自己的 Acceptance / Rejection Receipt。
19. WorkspaceFile 根据 Input 和下游 Receipt 更新用户可见状态。
```

## 8.2 Agent 在线附件

```text
1. Agent 请求携带 AttachmentRef 或上传请求。
2. Input 使用 ONLINE_FAST Profile 创建 temporary SourceObject。
3. 上传与完整性检查不可跳过。
4. ParsePlan 只处理当前任务需要的内容范围，但必须记录未处理部分。
5. 低延迟 Parser 优先；高质量增强可并行或延后。
6. 生成 thread-scoped ParseSnapshot。
7. 若 Agent 只需要临时上下文，返回 AttachmentDocumentRef。
8. 若需要检索，创建 thread-scoped IndexableDocumentSnapshot 交给 03。
9. Agent Core 通过 INGESTION_COMPLETION Interrupt 等待或使用 Progressive Result。
10. Retention 到期后执行 Tombstone、Knowledge 清理和物理 Purge。
```

在线路径不得直接把未经边界标记的文本拼进 Prompt。Agent Core 只能消费：

```text
attachment_ref
parse_snapshot_id
quality_verdict
content_scope
missing_content_ref
security_binding
expiry_at
```

## 8.3 Connector 增量同步

```text
Connector Poll / Webhook
→ SourceDescriptor
→ Security / Scope validation
→ remote_revision comparison
→ unchanged / metadata_changed / content_changed / deleted
```

处理规则：

```text
unchanged
    更新同步 Watermark，不创建 DocumentVersion。

metadata_changed
    创建新的 MetadataBinding / SecurityBinding Generation；
    若内容 Hash 不变，不重新解析。

content_changed
    创建新 SourceObject 或 SourceObjectVersion；
    创建新 DocumentVersion；
    提交新 ParseJob。

deleted
    创建 IngestionDeletionRequest 和 Tombstone；
    通知 Knowledge 删除；
    等待物理和索引删除 Receipt。
```

Connector 的远端 `updated_at` 不是完整性事实。必须以获取到的内容 Hash、远端版本 ID 和 Connector Receipt 共同判断。

## 8.4 同名文件重复上传

```text
同名 + 同 Hash
    创建或复用 SourceObject 物理内容；
    创建独立 WorkspaceFile Binding；
    根据 ACL、Retention 和 Profile 决定是否复用 ParseSnapshot。

同名 + 不同 Hash
    视为新源内容；
    创建新 DocumentVersion。

不同名 + 同 Hash
    可在同 Tenant / Policy Scope 内复用物理内容；
    不合并逻辑文件身份。
```

## 8.5 重解析

触发条件：

```text
Parser Bundle 升级
Parser 配置变化
IR Schema 升级
质量策略变化
原 Snapshot 被发现存在缺陷
新增 OCR / VLM 能力
人工请求高质量重解析
```

重解析流程：

```text
已有 DocumentVersion
→ 新 ParsePlan
→ 新 ParseJob / Attempt
→ 新 ParseSnapshot
→ Quality Gate
→ 新 Handoff
```

禁止：

```text
因为 Parser 升级创建新 DocumentVersion
覆盖旧 ParseSnapshot
改变历史 Handoff 的内容
```

## 8.6 源文件删除

```text
DELETE_REQUESTED
→ Security / Legal Hold Decision
→ WorkspaceFile HIDDEN_FOR_NEW_USE
→ Input Tombstone Commit
→ Handoff DELETE / REVOKE Event
→ Knowledge 删除逻辑索引并返回 Receipt
→ Object Store Retention / Hold 检查
→ Physical Purge
→ Verification
→ DELETED 或 BLOCKED_LEGAL_HOLD
```

删除完成不能只依据 API 返回成功。必须同时保留：

```text
Input tombstone receipt
Knowledge deletion receipt
Object purge or hold receipt
Cache invalidation receipt
Reconciliation verdict
```

## 8.7 源文件完整性异常

```text
Parser 读取 Hash ≠ committed source Hash
→ SOURCE_TAMPERED
→ 当前 ParseAttempt 终止
→ SourceObject QUARANTINED
→ 已生成但未激活的 Snapshot 作废
→ 已激活的下游结果进入 REVOKE / TAINT 流程
→ Security Finding + Audit Event
→ 人工或自动 Reconciliation
```

# 9. Processing Profile

Processing Profile 是版本化、可哈希的策略集合，不包含 Provider Secret。

```text
ONLINE_FAST
    在线附件，低延迟，有限范围，允许 Progressive Upgrade。

KNOWLEDGE_BALANCED
    普通知识库，完整 SourceSpan，质量与成本平衡。

HIGH_FIDELITY
    合同、规范、论文和复杂表格，严格结构、公式与引用质量。

REGULATED_LOCAL_ONLY
    敏感或受监管资料，禁止远程 Parser，强化保留和审计。

BULK_IMPORT
    历史批量导入，低优先级，大 Batch，允许长 Deadline。

METADATA_ONLY
    只登记来源和元数据，不生成可索引正文。

HUMAN_REVIEW_REQUIRED
    高风险或自动解析不足，必须人工确认后才可激活。
```

每个 Profile 至少包含：

```text
profile_id
profile_version
purpose
priority_class
latency_budget
throughput_class
allowed_parser_classes
allowed_remote_processing
allowed_model_roles
quality_threshold_ref
progressive_availability_policy
page_limit
file_size_limit
archive_expansion_limit
resource_budget
retention_policy_ref
missing_content_policy
degraded_acceptance_policy
human_review_policy
```

# 10. 优先级、Admission 与 Backpressure

优先级建议：

```text
P0 SECURITY / REVOCATION / DELETION
P1 ONLINE_ATTACHMENT
P2 USER_INITIATED_KNOWLEDGE
P3 CONNECTOR_INCREMENTAL
P4 BULK_IMPORT
P5 REPROCESS / SHADOW_EVAL
```

Admission 必须同时考虑：

```text
Tenant 并发配额
Workspace 活跃 Job 数
API 上传带宽
对象存储容量
Queue 深度
CPU Worker 容量
GPU Worker 容量
模型配额
远程 Provider 配额
文件大小与页数
Deadline
优先级
```

结果：

```text
ACCEPTED
ACCEPTED_DELAYED
REJECTED_QUOTA
REJECTED_CAPACITY
REJECTED_SECURITY
REJECTED_UNSUPPORTED
```

禁止无限接收后依赖 Queue 堆积解决容量问题。高水位时应：

```text
限制新 Bulk Import
降低预渲染和 VLM 增强
保留删除、安全和在线附件容量
返回可解释的 Retry-After / Queue Position
```

---

# Part III：原始证据、版本与完整性

# 11. InputSubmission 与 UploadSession

`InputSubmission` 表达业务意图：

```text
submission_id
tenant_id
workspace_id
principal_ref
input_kind
source_descriptor
processing_profile_ref
priority_class
requested_retention_ref
requested_knowledge_space_ref
correlation_id
deadline_at
security_context_ref
created_at
```

`UploadSession` 表达受约束上传：

```text
upload_session_id
tenant_id
workspace_id
principal_ref
object_commit_id
allowed_media_types
declared_filename
declared_media_type
max_size_bytes
multipart_policy
staging_key
expires_at
status
security_epoch_ref
created_at
completed_at
```

状态：

```text
CREATED
→ AUTHORIZED
→ UPLOADING
→ UPLOAD_COMPLETE
→ VERIFYING
→ COMMITTED
```

异常：

```text
EXPIRED
ABORTED
REJECTED_SECURITY
REJECTED_SIZE
HASH_MISMATCH
QUARANTINED
```

客户端直传只能使用短期、最小权限、绑定 Tenant / Workspace / Object Key 的凭证。前端不得拥有通用对象存储凭证。

# 12. SourceObject、WorkspaceFile、Document 与 DocumentVersion

## 12.1 SourceObject

SourceObject 是原始字节的逻辑事实：

```text
source_object_id
tenant_id
workspace_id
content_hash
hash_algorithm
size_bytes
detected_media_type
declared_media_type
original_filename
storage_object_ref
object_version_id
integrity_receipt_ref
encryption_metadata_ref
security_binding_ref
retention_policy_ref
legal_hold_refs
status
generation
created_by
created_at
tombstoned_at
purged_at
```

SourceObject 不保存 Parser、Chunk 或 Knowledge 状态。

## 12.2 WorkspaceFile

WorkspaceFile 是用户可见文件绑定：

```text
workspace_file_id
tenant_id
workspace_id
source_object_id
document_id
display_name
folder_ref
owner_ref
security_binding_ref
retention_policy_ref
lifecycle_status
processing_status
latest_document_version_id
latest_accepted_parse_snapshot_id
latest_handoff_status
generation
created_at
updated_at
```

用户可见状态是 Input 领域事实的投影，不是前端自维护状态。

## 12.3 Document

Document 是稳定业务身份：

```text
document_id
tenant_id
workspace_id
logical_source_key
document_kind
title
origin_type
connector_binding_ref
created_at
retired_at
```

同一 Document 可以有多个 DocumentVersion。

## 12.4 DocumentVersion

```text
document_version_id
document_id
tenant_id
workspace_id
source_object_id
source_content_hash
source_revision
parent_document_version_id
change_kind
security_binding_generation
created_by
created_at
status
```

`DocumentVersion` 只因源内容或明确的业务版本变化而创建：

```text
INITIAL
CONTENT_CHANGED
ROLLBACK
IMPORT_SNAPSHOT
HUMAN_CORRECTED_SOURCE
```

以下变化不创建 DocumentVersion：

```text
Parser 版本变化
OCR 模型变化
Parser 配置变化
IR Schema 变化
质量阈值变化
索引策略变化
```

# 13. Object Commit Protocol

对象存储不参与数据库 2PC。Target 使用：

```text
1. PostgreSQL Reserve ObjectCommit 与 idempotency key。
2. 事务外上传至 staging key。
3. 校验 size、SHA-256、media type、encryption metadata。
4. PostgreSQL 事务提交 StorageObject metadata、SourceObject、WorkspaceFile / DocumentVersion 引用和 Outbox。
5. 标记 COMMITTED。
6. 异步发布 SOURCE_COMMITTED。
7. Reconciler 清理过期 staging 和无领域引用的 orphan object。
```

读路径只接受：

```text
StorageObject.status = COMMITTED
SourceObject.status = AVAILABLE
expected_hash = observed_hash
security_binding valid
```

ObjectCommit 状态：

```text
PREPARED
→ UPLOADING
→ UPLOADED
→ VERIFYING
→ COMMITTING
→ COMMITTED
```

异常：

```text
ABORTED
ORPHANED
HASH_MISMATCH
QUARANTINED
PURGED
```

# 14. SourceIntegrityReceipt

```text
integrity_receipt_id
source_object_id
tenant_id
workspace_id
content_hash
hash_algorithm
size_bytes
detected_media_type
storage_object_version
storage_metadata_hash
uploader_principal_ref
object_commit_id
effective_security_epoch_ref
committed_at
service_identity_ref
signature_algorithm
signing_key_version_ref
signature
receipt_schema_version
```

Receipt 用于证明：

```text
提交时的原始内容
提交时的对象版本
上传主体
安全 Epoch
服务端提交身份
元数据未被静默改写
```

签名密钥由 Security / Infrastructure 交付，Input 只保存 Key Version Ref 与 Signature。

# 15. Hash DAG 与 Provenance

每个 ParseSnapshot 形成可验证派生 DAG：

```text
SourceObject(content_hash)
  └─usedBy→ ParseAttempt
      ├─used→ ParserBundle(bundle_hash)
      ├─used→ ParserConfig(config_hash)
      ├─used→ ModelWeight(model_hash)
      ├─generated→ RawExtractionArtifact(hash)
      ├─generated→ CanonicalIR(hash)
      ├─generated→ BlockManifest(hash)
      ├─generated→ SourceSpanManifest(hash)
      ├─generated→ MissingContentManifest(hash)
      └─generated→ ParserQualityReport(hash)
```

Provenance Edge：

```text
provenance_edge_id
tenant_id
subject_type
subject_id
relation
object_type
object_id
activity_type
activity_id
agent_ref
input_hash
output_hash
occurred_at
metadata_ref
```

关系至少包括：

```text
WAS_DERIVED_FROM
WAS_GENERATED_BY
USED
WAS_ATTRIBUTED_TO
WAS_REVISION_OF
WAS_INVALIDATED_BY
```

# 16. Tamper Detection

篡改检测至少发生在：

```text
上传流结束
Object Commit
Parser 读取前
页面渲染前
ParseSnapshot Commit 前
Handoff 发布前
对象后台巡检
恢复和重解析时
```

检测结果：

```text
MATCH
MISSING_OBJECT
SIZE_MISMATCH
CONTENT_HASH_MISMATCH
OBJECT_VERSION_CHANGED
METADATA_HASH_MISMATCH
SIGNATURE_INVALID
UNKNOWN
```

处理：

```text
MATCH
    继续。

UNKNOWN
    高风险 Profile fail-closed；普通 Profile 进入人工或 Reconcile。

其他不匹配
    SourceObject QUARANTINED；
    阻止新 Parse / Handoff；
    触发 Security Finding；
    对已激活下游发送 REVOCATION。
```

# 17. Object Versioning、WORM 与 Legal Hold

Object Store Target 必须支持版本化 Adapter。受监管 Profile 可以要求：

```text
object_versioning = required
object_lock_mode = GOVERNANCE / COMPLIANCE
retention_until
legal_hold
```

WORM 是可选基础能力，不是所有 Workspace 默认开启。未启用 WORM 时，应用层仍不得覆盖已提交对象 Key。

Legal Hold：

```text
阻止物理 Purge
不阻止逻辑撤权
不允许新 Handoff
保留 Tombstone、Hash、Receipt 和 Audit
```

# 18. 内容寻址与去重

物理 Object Key 建议包含：

```text
tenant_scope
content_hash
object_kind
object_version
```

逻辑示例：

```text
raw/{tenant_id}/{content_hash}/original
parse/{tenant_id}/{parse_snapshot_id}/canonical-ir.json
```

去重规则：

```text
同 Tenant + 同 Hash + 相同加密 / Retention 兼容
    可复用物理对象。

跨 Workspace
    只有 Security Policy 明确允许才可复用，逻辑 Binding 仍独立。

跨 Tenant
    默认禁止可观察去重；不得通过响应时间或错误暴露内容是否存在。
```

---

# Part IV：Source Profiling、Parser 路由与信息保真

# 19. SourceProfile

SourceProfiler 在 Parser 选择前产生不可变事实：

```text
source_profile_id
source_object_id
profile_version
detected_format
detected_media_type
media_type_confidence
declared_media_type_match
container_type
page_count
sheet_count
slide_count
archive_entry_count
encrypted
password_required
has_macros
has_embedded_objects
has_text_layer
text_layer_coverage
scanned_page_ratio
language_candidates
layout_complexity
table_density
formula_density
image_density
handwriting_likelihood
degradation_signals
estimated_cpu_cost
estimated_gpu_cost
estimated_output_size
security_findings
created_at
```

`degradation_signals` 包括：

```text
rotation
skew
blur
low_contrast
compression_artifact
screen_capture
page_curl
watermark
overlap
multi_column
dense_formula
```

Profiler 不修改源内容。

# 20. Content Type Detection

检测顺序：

```text
Magic Byte / Container Signature
→ Container Internal Structure
→ MIME Sniffing
→ Format-specific Probe
→ ML-based detector as supplementary signal
→ filename extension as low-trust hint
```

Declared MIME、扩展名和检测结果不一致时：

```text
MIME_MISMATCH
→ 根据风险进入 QUARANTINED、REJECTED 或显式 Parser Plan
```

未知格式不能默认按 UTF-8 文本解码并忽略错误。

# 21. ParserCapabilityProfile

```text
parser_capability_id
parser_id
parser_bundle_version
adapter_kind
supported_formats
supported_media_types
supported_content_features
supported_languages
input_contract_version
output_contract_version
source_span_capabilities
quality_signal_capabilities
deterministic_level
requires_network
requires_gpu
sandbox_profile_ref
resource_profile
max_file_size
max_pages
timeout_policy_ref
security_classifications_allowed
data_residency_zones
dependency_health_ref
status
bundle_hash
```

`deterministic_level`：

```text
DETERMINISTIC
HEURISTIC
MODEL_ASSISTED
MODEL_GENERATIVE
HUMAN
```

Planner 只能选择 `ACTIVE` 且满足 Security、Capacity、Deadline 和 Contract 的能力。

# 22. ParsePlan

ParsePlan 在激活后不可变：

```text
parse_plan_id
parse_plan_version
document_version_id
source_profile_id
processing_profile_ref
ir_schema_version
parser_bundle_refs
task_definitions
dependency_graph
join_policy
quality_policy_ref
fallback_policy_ref
resource_budget
deadline_at
security_binding_ref
created_by
created_at
status
content_hash
```

状态：

```text
PROPOSED
→ VALIDATING
→ VALID
→ ACTIVATED
```

异常：

```text
INVALID
REJECTED_SECURITY
REJECTED_CAPABILITY
SUPERSEDED
```

ParsePlan Validator 至少检查：

```text
Schema
任务 ID 唯一
DAG 无环
每个页面 / 区域有明确处置
Parser 能力满足
Input / Output Contract 兼容
SourceSpan 能力满足
Quality Policy 可计算
资源预算可满足
远程处理符合 Security
JoinPolicy 完整
Fallback 有界
不存在静默丢弃内容的 Task
```

# 23. 文件级、页面级与区域级 DAG

```text
File Task
  ├── Container / Metadata Task
  ├── Page Task 1
  │   ├── Native Text Region
  │   ├── Table Region
  │   └── Figure Region
  ├── Page Task 2
  │   └── OCR Full Page
  └── Page Task N
      ├── Formula Region
      └── Human Review Region
```

粒度选择规则：

```text
原生结构可靠
    使用文件或页面级 Native Parser。

部分页面扫描
    只对扫描页 OCR。

页面结构复杂
    先 Layout，再按区域解析。

只有局部低置信度
    只升级该区域到更强 Parser / VLM。

全文件损坏或加密
    整体 BLOCK，不无限拆分。
```

# 24. ParseTask

```text
parse_task_id
parse_job_id
task_kind
scope_type
scope_ref
parser_capability_ref
input_artifact_ref
input_hash
expected_output_contract
dependency_refs
priority
resource_claim
deadline_at
attempt_policy_ref
fallback_policy_ref
status
generation
created_at
```

`task_kind`：

```text
FORMAT_PROBE
CONTAINER_INSPECT
NATIVE_EXTRACT
PAGE_RENDER
LAYOUT_ANALYZE
OCR_RECOGNIZE
TABLE_PARSE
FORMULA_PARSE
FIGURE_EXTRACT
VLM_ENRICH
CANONICALIZE
SOURCE_SPAN_VALIDATE
QUALITY_EVALUATE
HUMAN_REVIEW
JOIN
```

# 25. Parser Adapter Contract

```python
class ParserAdapter(Protocol):
    async def probe(
        self,
        request: ParserProbeRequest,
    ) -> ParserProbeResult: ...

    async def execute(
        self,
        request: ParserExecutionRequest,
    ) -> ParserExecutionResult: ...

    async def cancel(
        self,
        attempt_ref: str,
    ) -> ParserCancelReceipt: ...

    async def health(
        self,
    ) -> ParserCapabilityHealth: ...
```

`ParserExecutionRequest` 不携带通用对象存储 Secret，只携带短期 Input Artifact Ref 或受控读取能力。

`ParserExecutionResult`：

```text
attempt_id
parser_id
parser_bundle_version
input_hash
output_artifact_refs
raw_elements
source_spans
quality_signals
warnings
missing_content
resource_usage
provider_receipt_ref
status
```

Adapter 不直接写最终 ParseSnapshot。

# 26. Parser 类别

## 26.1 Native Parser

适用于：

```text
TXT / Markdown
CSV / TSV
JSON / XML / YAML
HTML DOM
Office Open XML
PDF text layer
Email MIME
Git / source code
```

优先保留原生结构、原始 metadata 和明确定位。

## 26.2 Layout Parser

负责：

```text
阅读顺序
标题 / 正文 / 页眉页脚
表格区域
公式区域
图片区域
多栏布局
页面层级
```

Layout Parser 不自动把区域内容当作最终文字事实。

## 26.3 OCR

负责：

```text
文字检测
文字识别
行 / 字 / 区域坐标
方向
置信度
语言
```

OCR 输出必须保留：

```text
raw_ocr_text
normalized_ocr_text
bbox
page
confidence
engine_id
model_version
image_hash
```

## 26.4 Document VLM

适用于：

```text
复杂表格
复杂公式
图表
低质量扫描
OCR 冲突
视觉语义补充
```

VLM 输出默认是 Proposal / Derived Artifact，必须经过 Schema、范围、引用和质量验证。

## 26.5 Human Review

Human Review 产生：

```text
HumanCorrectionArtifact
reviewer_ref
review_scope
before_ref
after_ref
reason
created_at
signature / approval_ref
```

人工修订不能覆盖原始 Snapshot；创建新 ParseSnapshot 或 Correction Overlay。

# 27. 格式特定保真要求

## 27.1 PDF

必须尽可能保留：

```text
page number
bbox
char offsets
font / style hints
reading order
links
annotations
attachments
page rotation
native text layer
rendered page ref
table / formula / figure regions
```

不得把页面顺序和阅读顺序视为同一个概念。

## 27.2 DOCX / DOC

必须保留或声明：

```text
paragraph
style
heading hierarchy
list numbering
table
header / footer
footnote / endnote
comment
track changes
embedded image
hyperlink
section break
```

修订内容必须区分：

```text
CURRENT_VIEW
INSERTED
DELETED
COMMENTED
UNKNOWN_REVISION
```

## 27.3 PPTX / PPT

必须保留：

```text
slide number
shape / text box
z-order
bbox
group
speaker notes
table
chart
embedded object
hidden slide
theme / layout hints
```

文本框的视觉顺序与内部 XML 顺序冲突时必须产生 reading-order warning。

## 27.4 XLSX / XLS

必须保留：

```text
workbook
sheet
cell coordinate
formula
cached calculated value
displayed value
number format
merged range
hidden row / column / sheet
named range
comment
external link
table region
chart / image ref
```

不得只保存 Excel 展示文字而丢弃公式，也不得只保存公式而丢弃当时缓存值。

## 27.5 CSV / TSV

必须保留：

```text
encoding
delimiter
quote rules
header decision
row number
column number
malformed row
raw line
```

异常行不得静默补齐或丢弃。

## 27.6 JSON / XML / YAML

必须保留：

```text
raw value
type
JSON Pointer / XPath
array order
namespace
attributes
schema validation result
duplicate key finding
```

## 27.7 HTML / URL

必须保存：

```text
fetched URL
final URL
redirect chain
fetch timestamp
HTTP metadata
content hash
DOM path
canonical link
visible text
hidden / script / style classification
outbound link
snapshot ref
```

页面正文提取是派生视图；原始 HTML Snapshot 仍保留。

## 27.8 Email

必须保留：

```text
Message-ID
thread headers
from / to / cc / bcc
subject
sent / received timestamps
MIME tree
plain text / HTML body
attachments
inline images
signature block classification
```

## 27.9 图片

必须保留：

```text
original image
orientation
EXIF policy result
rendered / normalized image refs
OCR boxes
visual regions
derived caption
```

隐私敏感 EXIF 的移除必须作为显式 Security Transform，原始受控副本仍按政策保存。

## 27.10 代码与 Git

必须保留：

```text
repository
commit
branch / tag
path
blob hash
language
encoding
line range
symbol
AST / parser version
generated / vendored classification
```

Git Connector 的逻辑版本优先使用 Commit / Blob Hash，不使用本地文件修改时间。

## 27.11 Archive / Container

必须检查：

```text
entry count
nested depth
expanded size
compression ratio
path traversal
symlink
duplicate path
encrypted entry
embedded executable
```

解压内容形成子 SourceObject 或 ContainerEntry，不把归档内所有文件拼成一段文本。

# 28. OCR / VLM Cascade

默认级联：

```text
Native Structure
→ Layout Analysis
→ Local OCR
→ Local Document VLM
→ Approved Remote Document VLM
→ Human Review / BLOCK
```

升级触发条件：

```text
无文本层
文本覆盖率低
乱码率高
阅读顺序不稳定
表格结构不一致
关键公式缺失
OCR confidence 低
Native 与 OCR 冲突
高风险区域需要双重验证
```

禁止：

```text
所有 PDF 默认整页 VLM
对可靠文本层再次 OCR 后覆盖原文
远程 VLM 未经 Security 直接发送文件
把自然语言图片描述当精确 OCR
使用固定伪造 confidence
```

# 29. Progressive Parsing

在线 Profile 可以产生多个 Snapshot：

```text
FAST Snapshot
    低延迟、明确范围、明确缺失。

HIGH_FIDELITY Snapshot
    后续完整解析、独立质量门。
```

规则：

```text
FAST 不原地升级
HIGH_FIDELITY 创建新 Snapshot
Agent / Knowledge 明确绑定 Snapshot ID
新 Snapshot 激活后旧 Snapshot 进入 SUPERSEDED
历史 Run 仍可审计其使用的旧 Snapshot
```

# 30. CanonicalDocumentIR

```text
CanonicalDocumentIR
├── document_metadata
├── source_binding
├── pages[]
├── structure_tree
├── blocks[]
├── tables[]
├── formulas[]
├── figures[]
├── assets[]
├── source_spans[]
├── transform_ledger_ref
├── missing_content_manifest_ref
├── parser_provenance
└── schema_version
```

## 30.1 DocumentBlock

```text
block_id
block_type
parent_block_id
ordinal
page_ref
raw_text
normalized_text
search_view
derived_text
language
source_span_refs
asset_refs
structure_path
style_hints
confidence
origin_class
visibility_class
security_tags
metadata
```

`origin_class`：

```text
NATIVE
OCR_DERIVED
MODEL_DERIVED
HUMAN_CORRECTED
SYNTHETIC_METADATA
```

`visibility_class`：

```text
BODY
DOCUMENT_FURNITURE
HIDDEN_SOURCE_CONTENT
COMMENT
REVISION
METADATA
```

## 30.2 SourceSpan

```text
source_span_id
source_object_id
document_version_id
page
bbox
polygon
char_start
char_end
line_start
line_end
slide
sheet
cell_range
dom_path
json_pointer
xpath
code_path
code_line_start
code_line_end
raw_text_hash
render_asset_ref
```

SourceSpan 不含：

```text
chunk_id
parent_chunk_id
neighbor_chunk_ids
embedding ref
knowledge version
```

## 30.3 Structure Tree

结构边关系：

```text
CONTAINS
PRECEDES
CONTINUES
CAPTION_OF
FOOTNOTE_OF
COMMENT_ON
REVISION_OF
CELL_OF
GROUPED_WITH
```

结构顺序与视觉坐标均保留，不能只依赖单一线性排序。

# 31. Transform Ledger

清洗改名为可追溯 Transform。

```text
TransformRecord
    transform_id
    transform_type
    transformer_id
    transformer_version
    config_hash
    input_ref
    input_hash
    output_ref
    output_hash
    loss_class
    affected_scope
    operations
    warnings
    created_at
```

`loss_class`：

```text
LOSSLESS
STRUCTURE_REPAIR
LOSSY_VIEW
MODEL_DERIVED
HUMAN_CORRECTED
SECURITY_REDACTED
```

规范化规则：

```text
Unicode normalization
newline normalization
control character classification
hyphenation repair
whitespace repair
reading order repair
header / footer classification
```

禁止：

```text
删除原始 Block
覆盖 raw_text
无记录地去重段落
无记录地移除页眉页脚
把 OCR 文本写入 native raw_text
把 VLM 总结写成原文
```

`search_view` 可以排除 `DOCUMENT_FURNITURE`，但原始和 normalized view 必须保留。

# 32. MissingContentManifest

```text
missing_manifest_id
parse_snapshot_id
scope_items
overall_completeness
created_at
```

每个 Scope Item：

```text
scope_type
scope_ref
missing_kind
reason_code
severity
expected_content
observed_content
recoverability
suggested_action
evidence_refs
```

`missing_kind`：

```text
PAGE
TEXT
TABLE
FORMULA
FIGURE
COMMENT
FOOTNOTE
ATTACHMENT
HIDDEN_CONTENT
METADATA
SOURCE_SPAN
```

任何未处理页面、截断、超预算或 Parser 不支持必须进入 Manifest。

# 33. ParseConflict

```text
parse_conflict_id
parse_job_id
scope_ref
conflict_type
candidate_refs
deterministic_checks
resolution_status
selected_candidate_ref
resolution_reason
resolved_by
created_at
```

冲突类型：

```text
NATIVE_VS_OCR
OCR_VS_VLM
READING_ORDER
TABLE_STRUCTURE
FORMULA
LANGUAGE
DUPLICATE_CONTENT
SOURCE_SPAN
```

状态：

```text
OPEN
AUTO_RESOLVED
HUMAN_REQUIRED
RESOLVED
UNRESOLVED_BLOCKING
```

只有低置信度或高风险区域才触发昂贵多模型交叉验证。

# 34. ParserQualityReport

```text
quality_report_id
parse_snapshot_id
quality_policy_ref
content_coverage
source_span_coverage
layout_coverage
reading_order_confidence
table_structure_fidelity
formula_fidelity
figure_capture_coverage
ocr_confidence
garbled_text_ratio
empty_page_ratio
missing_page_count
unprocessed_region_count
duplicate_content_ratio
native_ocr_conflict_count
unresolved_conflict_count
critical_region_failure_count
security_findings
resource_limit_findings
warnings
verdict
verdict_reasons
created_at
```

Verdict：

```text
PASS
DEGRADED
BLOCK
```

规则：

```text
PASS
    满足 Profile 所有硬门和质量阈值。

DEGRADED
    存在显式缺失或低质量区域，但 Profile 允许有限使用；
    必须附 MissingContentManifest。

BLOCK
    安全、完整性、关键内容、SourceSpan 或质量硬门失败。
```

确定性硬门示例：

```text
source hash mismatch → BLOCK
malware / forbidden content → BLOCK
no usable content → BLOCK
critical page missing → BLOCK
source_span_coverage below strict threshold → BLOCK
unresolved high-risk conflict → BLOCK
remote processing forbidden but required → BLOCK
```

模型 Critic 可以产生质量建议，但最终 Verdict 由确定性 Policy Engine 提交。

---

# Part V：异步运行、并行、Redis 与恢复

# 35. ParseJob

```text
parse_job_id
tenant_id
workspace_id
document_version_id
parse_plan_id
processing_profile_ref
priority_class
status
generation
attempt_count
active_attempt_id
quality_verdict
accepted_snapshot_id
deadline_at
cancellation_ref
security_binding_ref
created_at
started_at
terminal_at
```

状态：

```text
CREATED
→ QUEUED
→ PROFILING
→ PLANNING
→ DISPATCHING
→ RUNNING
→ JOINING
→ CANONICALIZING
→ QUALITY_EVALUATING
→ ACCEPTED
```

非成功终态：

```text
BLOCKED
FAILED_FINAL
DEAD_LETTERED
CANCELLED
EXPIRED
SUPERSEDED
```

中间控制状态：

```text
RETRY_WAIT
FALLBACK_PENDING
HUMAN_REVIEW_REQUIRED
RECONCILING
```

# 36. ParseAttempt

```text
parse_attempt_id
parse_job_id
attempt_no
execution_epoch
worker_lease_ref
fencing_token
parser_bundle_refs
input_hash
status
failure_ref
resource_usage_ref
started_at
heartbeat_at
ended_at
```

状态：

```text
CREATED
→ CLAIMED
→ RUNNING
→ SUCCEEDED
```

失败终态：

```text
FAILED_RETRYABLE
FAILED_FINAL
LEASE_EXPIRED
CANCELLED
LATE_RESULT_REJECTED
UNKNOWN
```

Job 和 Attempt 必须分离。一个 Job 可以有多个 Attempt，但只能有一个被接受的终端结果。

# 37. ParseTask 并行与 Join

Ready Task 只有在以下条件同时满足时可 Dispatch：

```text
依赖完成
输入 Artifact 已提交
Security Binding 仍有效
资源无冲突
预算可分配
Deadline 可满足
Worker Capability 可用
并行度未超限
```

默认可并行：

```text
独立页面
独立 Sheet
独立 Slide
独立 Region
独立 Archive Entry
```

默认串行或受控：

```text
同一输出 Artifact 写入
全局 Reading Order
跨页表格合并
冲突解决
Final Canonicalization
Quality Verdict
Snapshot Activation
Deletion Finalization
```

JoinPolicy：

```text
ALL_REQUIRED
BEST_EFFORT_WITH_MANIFEST
QUORUM
FIRST_VALID
CUSTOM_DETERMINISTIC
```

`BEST_EFFORT_WITH_MANIFEST` 不能隐藏失败；所有未完成 Task 进入 MissingContentManifest。

# 38. Queue 拓扑

建议逻辑队列：

```text
ingestion.preflight
ingestion.profile
ingestion.parse.cpu
ingestion.layout
ingestion.ocr.cpu
ingestion.ocr.gpu
ingestion.vlm.local
ingestion.vlm.remote
ingestion.canonicalize
ingestion.quality
ingestion.handoff
ingestion.deletion
ingestion.reconcile
ingestion.dead-letter
```

优先级通过独立 Queue、Priority Class 或 Consumer Pool 实现，但不得依赖单一全局无界优先队列。

Queue Message 只携带引用：

```text
message_id
contract_name
contract_version
tenant_id
workspace_id
correlation_id
causation_id
idempotency_key
aggregate_id
aggregate_generation
payload_ref
payload_hash
deadline_at
priority
effective_security_epoch_ref
trace_id
```

不得把大型 PDF、页面图或完整 IR 放入消息正文。

# 39. RabbitMQ 语义

Canonical Server Target 使用持久工作队列 Adapter，默认可选 RabbitMQ Quorum Queue：

```text
durable queue
publisher confirm
manual consumer ack
dead letter routing
delivery limit
bounded retry delay
consumer prefetch
backpressure
```

消息投递是 at-least-once。业务必须接受重复，不能假定 exactly-once。

ACK 时机：

```text
1. Inbox Claim
2. 重读最新领域事实
3. 校验 generation / security epoch / fencing
4. 执行业务
5. PostgreSQL 事务提交结果、Inbox 和 Outbox
6. COMMIT
7. ACK
```

# 40. Redis 加速边界

Redis 是可丢失的加速层。

允许：

```text
Job Progress 热缓存
Workspace 活跃 Job 数缓存
Parser Capability / Worker Capacity Snapshot
SourceProfile 短期缓存
Page Render Cache
OCR Region Cache
Dedupe Hint
Admission Token Bucket
Rate-limit acceleration
Negative Cache
SSE / polling projection
```

禁止作为唯一来源：

```text
SourceObject 状态
DocumentVersion
ParseJob 终态
ParseSnapshot
Quality Verdict
Security Authorization
Retention / Legal Hold
唯一 Idempotency Claim
唯一 Worker Lease
删除完成事实
```

建议 Key：

```text
ingest:progress:{job_id}
ingest:capacity:{pool_id}
ingest:profile:{source_hash}:{profiler_version}
ingest:render:{source_hash}:{page}:{dpi}:{renderer_version}
ingest:ocr:{image_hash}:{model_hash}:{config_hash}
ingest:dedupe-hint:{tenant_id}:{source_hash}
ingest:admission:{tenant_id}:{resource_class}
```

每个 Key 必须定义：

```text
TTL
eviction tolerance
rebuild source
max size
security classification
```

Redis 故障不得改变领域正确性，只允许增加延迟、减少缓存命中或触发 Admission 降级。

# 41. Cache Correctness

缓存命中必须校验：

```text
tenant / policy scope
input hash
parser / model bundle hash
config hash
IR schema version
security binding compatibility
```

缓存 Artifact 不能跨不兼容 Security Scope 复用。

Cache Stampede 控制可以使用：

```text
短期 single-flight hint
request coalescing
bounded wait
```

但最终结果提交仍由 PostgreSQL Idempotency 和 Fencing 保证。

# 42. Lease、Heartbeat 与 Fencing

WorkerLease：

```text
lease_id
resource_type
resource_id
owner_instance_id
execution_epoch
fencing_token
status
acquired_at
heartbeat_at
expires_at
released_at
```

状态：

```text
ACQUIRED
ACTIVE
EXPIRED
RELEASED
REVOKED
```

规则：

```text
Claim 时生成单调递增 fencing_token
Heartbeat 只能续租当前 token
所有结果提交校验 token
Lease 过期后可由新 Worker 接管
旧 Worker 的晚到结果进入 LATE_RESULT_REJECTED
GPU / remote model 调用完成也不能绕过 Fencing
```

Redis 可以缓存 Lease 状态用于调度，但 PostgreSQL / Infrastructure Lease Store 才是权威。

# 43. Idempotency

## 43.1 Upload

```text
upload_idempotency_key =
    hash(tenant_id + workspace_id + client_request_id)
```

## 43.2 Parse

```text
parse_idempotency_key =
    hash(
        tenant_id
        + document_version_id
        + processing_profile_version
        + parser_bundle_set_hash
        + parser_config_hash
        + ir_schema_version
    )
```

## 43.3 Task

```text
task_idempotency_key =
    hash(parse_plan_id + task_scope + parser_capability_version + input_hash)
```

## 43.4 Handoff

```text
handoff_idempotency_key =
    hash(parse_snapshot_id + handoff_contract_version + security_binding_generation)
```

Idempotency 结果必须持久化。重复请求返回原结果或明确的 in-progress handle，不重新产生副作用。

# 44. Retry、Fallback、Reparse 与 Replan

## 44.1 Retry

计划仍正确，只是执行暂时失败：

```text
network timeout
temporary provider 5xx
worker crash
transient object read
GPU capacity unavailable
database serialization
```

Retry 不改变 Parser 类别和 Task 结构。

## 44.2 Parameter Repair

Parser 能力仍正确，但参数不合适：

```text
DPI 调整
language hint
table mode
page batch size
timeout
memory limit
```

必须有有界次数并记录新 Attempt 参数。

## 44.3 Fallback

原 Parser 能力不足：

```text
Native → Layout
Layout → OCR
OCR → Document VLM
Local → approved remote
Automatic → Human Review
```

Fallback 必须由已激活 ParsePlan 的 Policy 允许，或创建新 ParsePlan Version。

## 44.4 Reparse

对同一 DocumentVersion 使用新 Parser Bundle / Config / IR Schema 创建新 Snapshot。

## 44.5 Agent Replan

Agent Core 因 Ingestion 结果改变任务计划。Input 不执行 Agent Replan，只返回状态、Failure 和建议动作。

# 45. Deadline、Cancellation 与 Budget

Deadline 传播：

```text
InputSubmission.deadline_at
→ ParseJob
→ ParseTask
→ Parser Attempt
→ Model Gateway Request
```

Worker 开始前必须判断剩余时间是否足以完成。

Cancellation：

```text
REQUESTED
→ STOP_DISPATCH
→ CANCEL_ACTIVE_ATTEMPTS
→ WAIT / FORCE_TERMINATE
→ CANCELLED
```

已提交 SourceObject 不因 Parse Cancellation 自动删除。删除需要独立 Deletion Request。

预算耗尽：

```text
不再升级昂贵 Parser
完成已允许的确定性阶段
生成 MissingContentManifest
根据 Profile 进入 DEGRADED / BLOCK
```

不得伪造完整结果。

# 46. Outbox / Inbox

领域事务内写：

```text
ParseJob / Snapshot / Deletion 状态
Domain Event
OutboxRecord
```

事务外 Publisher 投递。

Outbox 状态：

```text
PENDING
CLAIMED
PUBLISHED
RETRY_SCHEDULED
DEAD_LETTER
```

Inbox 状态：

```text
CLAIMED
COMMITTED
REJECTED
DUPLICATE
```

同一 Aggregate 的 Event 使用单调 `event_sequence_no`。Consumer 对 `message_id` 和 `idempotency_key` 去重。

# 47. Reconciliation

必须定义：

```text
ObjectCommitReconciler
    清理 staging / orphan，验证 committed object。

SourceIntegrityReconciler
    周期性抽检 Hash、Object Version 和 Signature。

ParseJobReconciler
    非终态 Job 无活动 Attempt 时恢复、重试或 Block。

LeaseReconciler
    处理过期 Lease 和晚到结果。

OutboxReconciler
    重发未发布 Event，处理 Claim 超时和 Dead Letter。

SnapshotReconciler
    检查 Snapshot Artifact、Hash、Manifest 和数据库引用一致性。

HandoffReconciler
    处理已提交未发送、已发送无 Receipt、重复 Receipt。

DeletionReconciler
    对账 Input Tombstone、Knowledge 删除和 Object Purge。

CacheReconciler
    失效 Redis 热状态；缓存不是完成 Gate。
```

通用流程：

```text
扫描候选
→ Claim
→ 重读最新事实
→ 校验 generation / fencing / epoch
→ 幂等修复
→ 提交 ReconciliationRecord
→ 发布事件
```

---

# Part VI：领域状态机与 Contract

# 48. SourceObject 状态机

```text
RESERVED
→ UPLOADING
→ STAGED
→ VERIFYING
→ AVAILABLE
```

其他状态：

```text
QUARANTINED
TOMBSTONED
PURGE_PENDING
PURGED
```

转换规则：

| From | Trigger | Guard | To | 领域事实 |
| --- | --- | --- | --- | --- |
| RESERVED | START_UPLOAD | UploadSession valid | UPLOADING | upload started |
| UPLOADING | UPLOAD_COMPLETE | size within limit | STAGED | staged ref |
| STAGED | VERIFY | object readable | VERIFYING | verification attempt |
| VERIFYING | VERIFIED | hash/size/mime valid | AVAILABLE | integrity receipt |
| VERIFYING | MISMATCH | deterministic mismatch | QUARANTINED | finding |
| AVAILABLE | DELETE_REQUESTED | authorization committed | TOMBSTONED | tombstone |
| TOMBSTONED | PURGE_ALLOWED | no legal hold | PURGE_PENDING | purge request |
| PURGE_PENDING | PURGE_VERIFIED | object absent/version removed | PURGED | purge receipt |

# 49. WorkspaceFile 状态机

生命周期：

```text
REGISTERED
ACTIVE
HIDDEN
TOMBSTONED
DELETED
BLOCKED_LEGAL_HOLD
```

处理状态：

```text
NOT_SUBMITTED
QUEUED
PROCESSING
READY
DEGRADED
BLOCKED
FAILED
DELETION_PENDING
```

生命周期和处理状态分离。`FAILED` 不代表文件不存在；`DELETED` 不代表历史 Audit 被抹除。

# 50. DocumentVersion 状态机

```text
CREATED
→ PARSE_PENDING
→ PARSING
→ PARSED
→ ACTIVE
```

其他状态：

```text
BLOCKED
SUPERSEDED
TOMBSTONED
REVOKED
```

DocumentVersion 的 ACTIVE 只表示当前业务源版本，不等于其所有 ParseSnapshot 都可用。

# 51. ParsePlan 状态机

```text
PROPOSED
→ VALIDATING
→ VALID
→ ACTIVATED
```

终态：

```text
INVALID
REJECTED
SUPERSEDED
```

激活后的 Plan 不可变。Fallback 超出 Plan Policy 时创建新 Plan Version。

# 52. ParseSnapshot 状态机

```text
ASSEMBLING
→ INTEGRITY_VALIDATING
→ QUALITY_EVALUATING
→ ACCEPTED
```

其他状态：

```text
DEGRADED_ACCEPTED
REJECTED
QUARANTINED
SUPERSEDED
REVOKED
```

只有 `ACCEPTED` 和策略允许的 `DEGRADED_ACCEPTED` 可 Handoff。

# 53. Handoff 状态机

```text
PREPARED
→ OUTBOX_COMMITTED
→ DISPATCHED
→ RECEIVED
→ ACCEPTED
```

其他终态：

```text
REJECTED
DUPLICATE
EXPIRED
REVOKED
DEAD_LETTERED
```

Input 只拥有 Handoff 发送状态。Knowledge 的 Index / KnowledgeVersion 状态由 03 拥有。

# 54. Deletion 状态机

```text
REQUESTED
→ AUTHORIZED
→ INPUT_TOMBSTONED
→ DOWNSTREAM_NOTIFIED
→ KNOWLEDGE_ACKNOWLEDGED
→ PHYSICAL_VERIFICATION_PENDING
→ VERIFIED
```

其他：

```text
REJECTED
PARTIAL
BLOCKED_LEGAL_HOLD
RECONCILING
FAILED_FINAL
```

用户新请求在 `INPUT_TOMBSTONED` 后不得读取该文件，即使物理 Purge 尚未完成。

# 55. CrossModuleEnvelope

02 发出的跨模块消息必须使用已确认的 `CrossModuleEnvelopeV1`，至少绑定：

```text
contract_name / version / bundle_version
message_id
producer_module = INPUT_INGESTION
consumer_module
tenant_id
workspace_id
correlation_id
causation_id
idempotency_key
aggregate_id / type / version
expected_generation
effective_security_epoch_ref / hash
principal_ref
security_context_ref
authorization_decision_ref
deadline_at
trace_id
classification
redaction_ref
audit_context_ref
occurred_at
recorded_at
payload or payload_ref
payload_hash
payload_schema_hash
```

Unknown Version、Hash Mismatch、Stale Security Epoch、Missing Tenant 和 Generation Conflict 默认 fail-closed 或 quarantine。

# 56. IndexableDocumentSnapshotV1

```text
snapshot_contract_id
parse_snapshot_id
tenant_id
workspace_id
source_object_id
document_id
document_version_id
canonical_ir_ref
canonical_ir_hash
ir_schema_version
block_manifest_ref
block_manifest_hash
source_span_manifest_ref
source_span_manifest_hash
asset_manifest_ref
asset_manifest_hash
missing_content_manifest_ref
missing_content_manifest_hash
parser_provenance_ref
parser_bundle_set_hash
parser_config_hash
quality_report_ref
quality_report_hash
quality_verdict
allowed_content_scope
security_binding_ref
effective_security_epoch_ref
retention_policy_ref
generation
change_kind
created_at
```

`change_kind`：

```text
UPSERT
REPARSE
REVOKE
DELETE
SECURITY_REBIND
```

明确禁止包含：

```text
requested_index_targets
retrieval chunk
parent chunk
citation chunk
embedding
BM25 / vector / graph document
KnowledgeVersion
Evidence
Citation
```

# 57. Knowledge Receipt

Input 只消费 03 返回的 Provider-neutral Receipt：

```text
handoff_receipt_id
handoff_id
parse_snapshot_id
consumer_module
status
consumer_generation
failure_ref
knowledge_manifest_ref
received_at
committed_at
```

状态：

```text
ACCEPTED
REJECTED_CONTRACT
REJECTED_SECURITY
REJECTED_QUALITY
DUPLICATE
EXPIRED
```

Input 不解析 Knowledge 内部 Index 细节来判断成功。

# 58. Agent Core IngestionPort

```python
class IngestionPort(Protocol):
    async def submit(
        self,
        request: SubmitIngestionRequest,
    ) -> ExternalJobHandle: ...

    async def get_status(
        self,
        job_id: str,
    ) -> ExternalJobStatus: ...

    async def get_result(
        self,
        job_id: str,
    ) -> IngestionResultRef: ...

    async def cancel(
        self,
        job_id: str,
        command_ref: str,
    ) -> CancellationReceipt: ...
```

`ExternalJobStatus`：

```text
job_id
status
progress
quality_state
result_ref
failure_ref
retry_after
deadline_at
updated_at
```

Agent Core 不轮询数据库内部表，只通过 Port 或 Event 等待。

# 59. AttachmentDocumentRef

```text
attachment_document_ref
run_id
thread_id
source_object_id
document_version_id
parse_snapshot_id
quality_verdict
content_scope
missing_content_ref
security_binding_ref
expires_at
```

Agent Core 只能将其作为上下文来源引用，不直接重写内部内容。

# 60. Security Contract

Input 消费：

```text
UploadAuthorizationDecision
ParserSecurityDecision
RemoteProcessingDecision
DataClassification
EffectiveSecurityEpochRef
RetentionPolicyRef
LegalHoldBinding
RedactionDecision
CredentialScopeRef
```

每次高风险边界重新校验：

```text
UploadSession 创建
Object Commit
Parser Dispatch
远程 OCR / VLM Dispatch
Snapshot Activation
Handoff
Delete / Purge
```

安全 Epoch 变化不要求自动重解析原内容，但必须：

```text
创建新 SecurityBinding Generation
使旧 Handoff 对新请求失效
必要时发布 SECURITY_REBIND / REVOKE
```

---

# Part VII：持久化、对象、API 与部署规格

# 61. PostgreSQL 领域表

## 61.1 `ingestion_submissions`

```text
submission_id PK
tenant_id
workspace_id
principal_ref
input_kind
source_descriptor_json
processing_profile_id
processing_profile_version
priority_class
deadline_at
security_context_ref
status
created_at
```

索引：

```text
(tenant_id, workspace_id, created_at)
(status, priority_class, created_at)
```

## 61.2 `upload_sessions`

```text
upload_session_id PK
tenant_id
workspace_id
object_commit_id UNIQUE
status
declared_filename
declared_media_type
max_size_bytes
staging_key
expires_at
security_epoch_ref
created_at
completed_at
generation
```

## 61.3 `source_objects`

```text
source_object_id PK
tenant_id
workspace_id
content_hash
hash_algorithm
size_bytes
detected_media_type
declared_media_type
original_filename
storage_object_ref
object_version_id
integrity_receipt_id
security_binding_id
retention_policy_ref
status
generation
created_by
created_at
tombstoned_at
purged_at
```

约束：

```text
UNIQUE(tenant_id, source_object_id)
INDEX(tenant_id, content_hash)
CHECK(size_bytes >= 0)
```

## 61.4 `source_integrity_receipts`

```text
integrity_receipt_id PK
source_object_id FK
content_hash
size_bytes
storage_metadata_hash
object_version_id
service_identity_ref
signing_key_version_ref
signature
security_epoch_ref
committed_at
schema_version
```

## 61.5 `workspace_files`

```text
workspace_file_id PK
tenant_id
workspace_id
source_object_id FK
document_id FK
display_name
folder_ref
lifecycle_status
processing_status
latest_document_version_id
latest_accepted_parse_snapshot_id
security_binding_id
retention_policy_ref
generation
created_at
updated_at
```

## 61.6 `documents`

```text
document_id PK
tenant_id
workspace_id
logical_source_key
document_kind
title
origin_type
connector_binding_ref
created_at
retired_at
```

约束：

```text
UNIQUE(tenant_id, workspace_id, logical_source_key)
```

## 61.7 `document_versions`

```text
document_version_id PK
document_id FK
tenant_id
workspace_id
source_object_id FK
source_content_hash
source_revision
parent_document_version_id
change_kind
security_binding_generation
status
created_by
created_at
```

## 61.8 `source_profiles`

```text
source_profile_id PK
source_object_id FK
profile_version
profile_json_ref
profile_hash
detected_format
page_count
text_layer_coverage
scanned_page_ratio
layout_complexity
security_findings_ref
created_at
```

## 61.9 `parse_plans`

```text
parse_plan_id PK
parse_plan_version
document_version_id FK
source_profile_id FK
processing_profile_ref
plan_ref
plan_hash
status
security_binding_ref
deadline_at
created_at
```

## 61.10 `parse_jobs`

```text
parse_job_id PK
tenant_id
workspace_id
document_version_id FK
parse_plan_id FK
processing_profile_ref
priority_class
status
generation
attempt_count
active_attempt_id
quality_verdict
accepted_snapshot_id
deadline_at
created_at
started_at
terminal_at
```

关键索引：

```text
(tenant_id, workspace_id, status, priority_class)
(status, deadline_at)
(document_version_id, created_at)
```

## 61.11 `parse_attempts`

```text
parse_attempt_id PK
parse_job_id FK
attempt_no
execution_epoch
worker_lease_ref
fencing_token
parser_bundle_set_hash
input_hash
status
failure_ref
resource_usage_ref
started_at
heartbeat_at
ended_at
```

约束：

```text
UNIQUE(parse_job_id, attempt_no)
```

## 61.12 `parse_tasks`

```text
parse_task_id PK
parse_job_id FK
task_kind
scope_type
scope_ref
parser_capability_ref
input_artifact_ref
input_hash
status
generation
priority
deadline_at
failure_ref
created_at
started_at
terminal_at
```

## 61.13 `parse_snapshots`

```text
parse_snapshot_id PK
parse_job_id FK
document_version_id FK
status
canonical_ir_ref
canonical_ir_hash
ir_schema_version
block_manifest_ref
block_manifest_hash
source_span_manifest_ref
source_span_manifest_hash
asset_manifest_ref
asset_manifest_hash
missing_content_manifest_ref
missing_content_manifest_hash
parser_bundle_set_hash
parser_config_hash
quality_report_id
security_binding_ref
generation
created_at
superseded_at
revoked_at
```

## 61.14 `document_blocks`

数据库中的 Block 是查询投影，不是完整 IR 唯一权威副本：

```text
block_row_id PK
parse_snapshot_id FK
block_id
tenant_id
workspace_id
document_id
document_version_id
block_type
origin_class
visibility_class
normalized_text
search_view
page_no
structure_path
confidence
metadata_json
security_tags
```

完整 `raw_text`、复杂结构和大型 Artifact 可以存 Object Store，并由 Ref 关联。

## 61.15 `source_spans`

```text
source_span_id PK
parse_snapshot_id FK
block_id
source_object_id
page_no
bbox_json
polygon_json
char_start
char_end
line_start
line_end
slide_no
sheet_name
cell_range
dom_path
json_pointer
xpath
code_path
code_line_start
code_line_end
raw_text_hash
render_asset_ref
```

## 61.16 `transform_records`

```text
transform_id PK
parse_snapshot_id FK
transform_type
transformer_id
transformer_version
config_hash
input_ref
input_hash
output_ref
output_hash
loss_class
affected_scope
operations_json
warnings_json
created_at
```

## 61.17 `parser_quality_reports`

```text
quality_report_id PK
parse_snapshot_id UNIQUE FK
quality_policy_ref
metrics_json
verdict
verdict_reasons_json
created_at
```

## 61.18 `parse_conflicts`

```text
parse_conflict_id PK
parse_job_id FK
scope_ref
conflict_type
candidate_refs_json
resolution_status
selected_candidate_ref
resolution_reason
resolved_by
created_at
```

## 61.19 `ingestion_handoffs`

```text
handoff_id PK
parse_snapshot_id FK
contract_name
contract_version
payload_ref
payload_hash
idempotency_key UNIQUE
status
consumer_module
consumer_receipt_ref
attempt_count
next_attempt_at
created_at
terminal_at
```

## 61.20 `ingestion_deletion_requests`

```text
deletion_request_id PK
tenant_id
workspace_id
subject_type
subject_id
status
authorization_ref
legal_hold_ref
input_tombstone_ref
knowledge_receipt_ref
object_purge_receipt_ref
verification_ref
created_at
terminal_at
```

## 61.21 `provenance_edges`

```text
provenance_edge_id PK
tenant_id
subject_type
subject_id
relation
object_type
object_id
activity_type
activity_id
agent_ref
input_hash
output_hash
occurred_at
metadata_ref
```

# 62. 数据库事务规则

1. Repository 不自行 commit；Application Service 使用 Unit of Work。
2. 外部对象、Queue、Redis、HTTP、Parser、模型调用不在 DB Transaction 内。
3. `generation`、`security_epoch`、`fencing_token` 使用条件写。
4. Unique / FK / Check Violation 不盲目重试。
5. Serialization / Deadlock 只按有界 Policy 重试整个事务。
6. Snapshot Activation 与 Handoff Outbox 在同一事务提交。
7. Tombstone 与删除 Outbox 在同一事务提交。
8. Redis 更新发生在领域 Commit 后，失败只影响缓存。
9. 大型 JSON Artifact 不作为所有查询的唯一数据库列。
10. Migration 必须可回滚或提供明确 Roll-forward，禁止 `create_all` 作为生产 Schema 管理。

# 63. Object Store 逻辑布局

```text
/staging/{tenant}/{upload_session_id}/...
/raw/{tenant}/{source_object_id}/{object_version}/original
/parse/{tenant}/{parse_snapshot_id}/raw-extraction.json
/parse/{tenant}/{parse_snapshot_id}/canonical-ir.json
/parse/{tenant}/{parse_snapshot_id}/block-manifest.json
/parse/{tenant}/{parse_snapshot_id}/source-span-manifest.json
/parse/{tenant}/{parse_snapshot_id}/missing-content.json
/parse/{tenant}/{parse_snapshot_id}/quality-report.json
/parse/{tenant}/{parse_snapshot_id}/pages/{page}.webp
/parse/{tenant}/{parse_snapshot_id}/regions/{region}.png
/parse/{tenant}/{parse_snapshot_id}/tables/{table}.json
/parse/{tenant}/{parse_snapshot_id}/formulas/{formula}.json
/quarantine/{tenant}/{source_object_id}/...
```

对象 Key 是实现细节，领域层只保存 typed ObjectRef。

# 64. ObjectRef

```text
object_id
object_kind
storage_uri
version_id
content_hash
size_bytes
media_type
encryption_key_ref
commit_id
status
retention_policy_ref
legal_hold_refs
```

任何 ObjectRef 的消费都要校验：

```text
status
tenant scope
content hash
security binding
retention / hold
```

# 65. API Surface

建议 Product API：

```text
POST   /api/v1/workspaces/{workspace_id}/ingestion/submissions
POST   /api/v1/workspaces/{workspace_id}/uploads
POST   /api/v1/uploads/{upload_session_id}/complete
GET    /api/v1/ingestion/jobs/{job_id}
POST   /api/v1/ingestion/jobs/{job_id}/cancel
POST   /api/v1/ingestion/jobs/{job_id}/reparse
GET    /api/v1/files/{workspace_file_id}
GET    /api/v1/files/{workspace_file_id}/versions
GET    /api/v1/parse-snapshots/{parse_snapshot_id}
GET    /api/v1/parse-snapshots/{parse_snapshot_id}/quality
DELETE /api/v1/files/{workspace_file_id}
```

API 返回领域状态和 Handle，不暴露内部 Queue、Bucket Key、数据库 ID 组合或 Provider Secret。

上传 API 使用：

```text
Create UploadSession
→ controlled direct upload or server stream
→ Complete Upload
→ HTTP 202 + ingestion job handle
```

# 66. 部署角色

同一 backend image 可以按 Role 启动：

```text
api
ingestion-controller
parser-cpu-worker
parser-gpu-worker
remote-parser-worker
connector-worker
reconciler
maintenance
```

只有隔离、扩缩容或安全需要时才拆独立镜像。

CPU Worker：

```text
format detection
native parsing
container inspection
basic layout
canonicalization
quality checks
```

GPU Worker：

```text
OCR batch
document VLM
complex layout / formula / table
```

远程 Parser Worker：

```text
Security-approved external calls
Model Gateway binding
rate limit
usage receipt
```

# 67. 模型和 Parser 制品

每个 Parser Bundle 必须固定：

```text
source package version
container image digest
native dependency versions
model weight hash
tokenizer / processor version
config schema version
license metadata
security scan receipt
capability profile hash
```

Worker 启动时发布 `ParserCapabilityHealth`。缺失模型权重时必须报告 `MODEL_WEIGHT_MISSING`，不能使用隐式下载后静默改变版本。

---

# Part VIII：Security、Failure、Observability 与 Eval

# 68. Security Gate

## 68.1 上传前

```text
Principal authorization
Tenant / Workspace binding
file size and type policy
source origin policy
rate / quota
retention request
```

## 68.2 上传后、解析前

```text
magic-byte MIME
archive bomb
path traversal
malware scan
macro / executable
encrypted file
embedded object
remote URL SSRF
data classification
```

## 68.3 Parser Dispatch 前

```text
Parser allowed
network policy
sandbox policy
data residency
remote provider allowed
credential scope
effective security epoch
```

## 68.4 Snapshot / Handoff 前

```text
security tags propagated
redaction policy applied
hidden / comment / revision policy
quality acceptable
epoch still valid
consumer authorized
```

# 69. Sandbox

不可信文件 Parser 运行要求：

```text
non-root
read-only base filesystem
ephemeral workspace
no host mounts
network deny by default
CPU / memory / disk / process limits
timeout
archive limits
syscall / seccomp profile
temporary file cleanup
```

Office 宏、嵌入对象和 Archive Entry 不执行。

# 70. Remote URL Security

URL Connector 必须防止：

```text
SSRF
private network access
DNS rebinding
redirect to forbidden host
credential leakage
unbounded response
content-type mismatch
decompression bomb
```

流程：

```text
URL normalize
→ scheme / host allow policy
→ DNS resolution and IP classification
→ connect with bounded redirect
→ stream size limit
→ content hash / snapshot
→ parse committed object
```

Parser 不直接反复访问原 URL。

# 71. Failure Taxonomy

## 71.1 Input / Validation

```text
INGESTION_INVALID_REQUEST
INGESTION_UNSUPPORTED_FORMAT
INGESTION_MIME_MISMATCH
INGESTION_SIZE_LIMIT
INGESTION_PAGE_LIMIT
INGESTION_ARCHIVE_BOMB
INGESTION_ENCRYPTED_DOCUMENT
INGESTION_MALWARE_DETECTED
INGESTION_SECURITY_BLOCKED
```

## 71.2 Object / Integrity

```text
INGESTION_OBJECT_UPLOAD_FAILED
INGESTION_OBJECT_MISSING
INGESTION_OBJECT_HASH_MISMATCH
INGESTION_OBJECT_VERSION_CHANGED
INGESTION_SIGNATURE_INVALID
INGESTION_SOURCE_TAMPERED
INGESTION_OBJECT_ORPHANED
```

## 71.3 Parser

```text
INGESTION_PARSER_UNAVAILABLE
INGESTION_DEPENDENCY_MISSING
INGESTION_MODEL_WEIGHT_MISSING
INGESTION_PARSER_TIMEOUT
INGESTION_PARSER_CRASH
INGESTION_GPU_OOM
INGESTION_REMOTE_PROVIDER_FAILED
INGESTION_OCR_LOW_CONFIDENCE
INGESTION_STRUCTURE_LOSS
INGESTION_SOURCE_SPAN_INCOMPLETE
INGESTION_PARSE_CONFLICT
INGESTION_QUALITY_REJECTED
```

## 71.4 Runtime

```text
INGESTION_QUEUE_PUBLISH_FAILED
INGESTION_DUPLICATE_DELIVERY
INGESTION_LEASE_EXPIRED
INGESTION_LATE_RESULT_REJECTED
INGESTION_DEADLINE_EXCEEDED
INGESTION_CANCELLED
INGESTION_RECONCILIATION_REQUIRED
```

## 71.5 Handoff / Deletion

```text
INGESTION_HANDOFF_REJECTED
INGESTION_HANDOFF_EXPIRED
INGESTION_HANDOFF_DEAD_LETTER
INGESTION_DELETE_PARTIAL
INGESTION_DELETE_BLOCKED_LEGAL_HOLD
INGESTION_DELETE_VERIFICATION_FAILED
```

# 72. Failure Record

```text
failure_id
failure_code
failure_class
owner_module
subject_type
subject_id
attempt_id
retryable
fallback_allowed
reparse_required
human_required
security_impact
message
details_ref
caused_by_ref
occurred_at
```

Input 返回结构化失败，不返回“失败了请重试”作为唯一语义。

# 73. Failure Ownership

| Failure | Detect | Decide | Recover |
| --- | --- | --- | --- |
| MIME mismatch | Input | Input + Security policy | Input |
| Malware | Security scanner / Input | Security | Input quarantine / Infrastructure isolate |
| Object hash mismatch | Infrastructure / Input | Input integrity policy | Infrastructure + Input |
| Parser timeout | Parser Runtime | Input retry policy | Input |
| Model provider 5xx | Model Gateway | Model Gateway suggestion / Input fallback | Model Gateway + Input |
| Lease expired | Infrastructure | Input task policy | Infrastructure + Input |
| Quality rejected | Input | Input quality policy | Input |
| Handoff contract rejected | Knowledge | Knowledge | Input repair / reparse |
| Legal hold | Security | Security | Infrastructure enforcement |
| Physical purge failure | Infrastructure | Input deletion state | Infrastructure reconciler |

# 74. Crash Matrix

## 74.1 对象上传成功、DB Commit 前崩溃

```text
staging object 存在
SourceObject 不存在
→ ObjectCommitReconciler 标记 ORPHANED
→ TTL 后清理
```

## 74.2 DB Commit 成功、Outbox 发布前崩溃

```text
SourceObject / ParseSnapshot 有效
Outbox PENDING
→ OutboxReconciler 发布
```

## 74.3 Worker 执行成功、结果 Commit 前崩溃

```text
Attempt 无终态
Lease 到期
→ 新 Worker 接管
→ Idempotency / Cache 可复用 Artifact
→ 旧结果提交因 Fencing 被拒绝
```

## 74.4 Snapshot Commit 成功、Handoff 发送前崩溃

```text
Snapshot ACCEPTED
Handoff Outbox PENDING
→ HandoffReconciler 重发
```

## 74.5 Handoff 已被 Knowledge 接受、Receipt 丢失

```text
Input 重发同一 message / idempotency key
→ Knowledge 返回 DUPLICATE + original receipt
```

## 74.6 Tombstone Commit 成功、下游删除未完成

```text
用户新请求已不可见
Deletion 状态 PARTIAL / RECONCILING
→ 重试下游删除和物理验证
```

# 75. Observability

每个 Job 关联：

```text
trace_id
correlation_id
submission_id
source_object_id
document_version_id
parse_plan_id
parse_job_id
parse_attempt_id
parse_task_id
parse_snapshot_id
handoff_id
```

Trace Span：

```text
ingestion.submit
ingestion.upload
ingestion.object_commit
ingestion.preflight
ingestion.profile
ingestion.plan
ingestion.dispatch
ingestion.parse.native
ingestion.parse.layout
ingestion.parse.ocr
ingestion.parse.vlm
ingestion.canonicalize
ingestion.quality
ingestion.snapshot_commit
ingestion.handoff
ingestion.delete
ingestion.reconcile
```

禁止记录：

```text
完整敏感文档
模型隐藏思维链
明文 Credential
不必要的原始 OCR 全文
```

# 76. Metrics

## 76.1 吞吐和延迟

```text
ingestion_submissions_total
ingestion_upload_bytes_total
ingestion_job_latency_seconds
ingestion_time_to_first_usable_snapshot_seconds
ingestion_time_to_high_fidelity_snapshot_seconds
ingestion_pages_processed_total
ingestion_queue_depth
ingestion_queue_wait_seconds
```

## 76.2 质量

```text
ingestion_quality_pass_ratio
ingestion_quality_degraded_ratio
ingestion_quality_block_ratio
ingestion_source_span_coverage
ingestion_ocr_confidence
ingestion_table_fidelity
ingestion_formula_fidelity
ingestion_missing_region_count
ingestion_parse_conflict_count
```

## 76.3 可靠性

```text
ingestion_retry_total
ingestion_fallback_total
ingestion_dead_letter_total
ingestion_lease_expired_total
ingestion_late_result_rejected_total
ingestion_object_orphan_total
ingestion_integrity_mismatch_total
ingestion_reconciliation_backlog
```

## 76.4 成本与资源

```text
ingestion_cpu_seconds
ingestion_gpu_seconds
ingestion_remote_model_cost
ingestion_object_bytes
ingestion_cache_hit_ratio
ingestion_cache_saved_compute
```

# 77. Eval

项目必须维护自己的 Golden Corpus，覆盖：

```text
文本 PDF
扫描 PDF
混合 PDF
多栏论文
复杂表格
公式
合同
Word 修订 / 批注
PPT 备注 / 图表
Excel 公式 / 隐藏 Sheet
HTML 模板噪声
Email MIME / 附件
图片拍照、倾斜、模糊、低光
代码和 Git 历史
Archive Bomb / 恶意样本
多语言
超大文件
损坏文件
```

退化变换：

```text
rotation
skew
blur
noise
compression
low contrast
screen capture
watermark
partial crop
page curl
mixed orientation
```

评测指标：

```text
text accuracy
layout accuracy
reading order
table structure
formula accuracy
source span grounding
missing-content recall
tamper detection
latency
throughput
cost
memory
recovery correctness
```

不能只使用单一公开 Benchmark 得分声明 production ready。

# 78. Shadow Evaluation

新 Parser Bundle 上线前可以：

```text
读取已提交 SourceObject
→ Shadow Parse
→ 不激活 Snapshot
→ 与当前 Snapshot 比较
→ 生成 EvalResult
```

Shadow 结果不得影响用户可见状态或 Knowledge，除非经过发布 Gate。

# 79. SLO / SLI Target

SLO 必须按 Profile 定义，不使用一个数字覆盖全部文件。

示例 SLI：

```text
upload_commit_latency
queue_wait
time_to_first_usable_snapshot
time_to_accepted_snapshot
quality_pass_rate
integrity_detection_rate
recovery_time
deletion_visibility_latency
deletion_verification_latency
```

具体阈值由 Program 和测量证据确定；本文只要求所有 Profile 有版本化 SLO Policy 和 Release Gate。

---

# Part IX：目标代码边界与实现规格

# 80. 目标代码目录

```text
src/backend/zuno/input/
├── domain/
│   ├── submissions.py
│   ├── source_objects.py
│   ├── documents.py
│   ├── parse_plans.py
│   ├── parse_jobs.py
│   ├── parse_snapshots.py
│   ├── quality.py
│   ├── provenance.py
│   ├── deletion.py
│   ├── events.py
│   └── failures.py
├── application/
│   ├── submit_ingestion.py
│   ├── complete_upload.py
│   ├── profile_source.py
│   ├── plan_parse.py
│   ├── dispatch_parse.py
│   ├── assemble_snapshot.py
│   ├── evaluate_quality.py
│   ├── publish_handoff.py
│   ├── reparse_document.py
│   ├── delete_source.py
│   └── query_ingestion.py
├── contracts/
│   ├── api.py
│   ├── parser.py
│   ├── knowledge.py
│   ├── agent_core.py
│   ├── security.py
│   ├── infrastructure.py
│   └── observability.py
├── parsing/
│   ├── capability_registry.py
│   ├── profiles.py
│   ├── profiler.py
│   ├── planner.py
│   ├── canonicalizer.py
│   ├── source_spans.py
│   ├── transforms.py
│   ├── quality_engine.py
│   ├── conflict_resolver.py
│   └── adapters/
│       ├── native/
│       ├── pdf/
│       ├── office/
│       ├── table/
│       ├── ocr/
│       ├── vlm/
│       ├── html/
│       ├── email/
│       ├── code/
│       └── archive/
├── runtime/
│   ├── controller.py
│   ├── dispatcher.py
│   ├── worker.py
│   ├── join.py
│   ├── admission.py
│   ├── cache.py
│   └── reconcilers/
├── infrastructure/
│   ├── repositories/
│   ├── object_ports.py
│   ├── queue_ports.py
│   ├── redis_ports.py
│   ├── lease_ports.py
│   └── uow.py
└── api/
    ├── routes.py
    ├── dto.py
    └── dependencies.py
```

目录是 Target 逻辑边界，不要求一次性大重构。旧 `knowledge/ingestion` 实现迁移必须由后续 Program 管理。

# 81. 依赖方向

```text
api
→ application
→ domain / contracts

parsing
→ domain / parser contracts

runtime
→ application / contracts

infrastructure adapters
→ infrastructure ports

domain
    不依赖 FastAPI、SQLAlchemy、RabbitMQ、Redis、MinIO、
    Docling、PaddleOCR、具体模型 SDK。
```

禁止：

```text
Parser Adapter 直接写数据库终态
API Route 直接构造 Knowledge Chunk
Domain Model 导入 Provider SDK
Redis Client 出现在 Domain
Object Store URI 解析散落业务代码
```

# 82. Repository 与 Unit of Work

```python
class IngestionUnitOfWork(Protocol):
    sources: SourceObjectRepository
    files: WorkspaceFileRepository
    documents: DocumentRepository
    plans: ParsePlanRepository
    jobs: ParseJobRepository
    snapshots: ParseSnapshotRepository
    handoffs: HandoffRepository
    deletions: DeletionRepository
    outbox: OutboxRepository

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
```

Repository 只处理领域对象和条件写，不执行 Queue、HTTP、Parser 或 Redis。

# 83. Parser Plugin 注册

Parser Adapter 注册必须通过版本化 Manifest：

```text
parser_id
adapter_kind
entrypoint
capability_profile_ref
input_schema
output_schema
bundle_hash
sandbox_profile_ref
health_check
```

动态插件不能绕过：

```text
签名 / 完整性验证
Allow List
依赖扫描
License policy
Sandbox
Capability Validation
```

# 84. Migration 要求

后续实现必须使用 Alembic：

```text
所有表有显式 Migration
外键和唯一约束可验证
大表索引并发创建策略
JSON / Artifact Ref 迁移策略
Backfill 可重入
旧表读写兼容窗口
Rollback / Roll-forward 决策
```

本文不定义迁移阶段或 Cutover 顺序。

# 85. API 幂等与错误

所有创建 API 支持：

```text
Idempotency-Key
correlation_id
deadline
processing_profile
```

错误返回：

```text
failure_code
message
retryable
retry_after
job_ref
details_ref
trace_id
```

不得把内部 Exception、Bucket Credential 或 Provider 响应原文直接返回前端。

# 86. Schema 版本

必须独立版本化：

```text
Canonical IR Schema
Parser Adapter Input / Output
Quality Policy
Processing Profile
CrossModuleEnvelope
IndexableDocumentSnapshot
Failure Schema
ObjectRef
```

Schema 不兼容时：

```text
拒绝
转换到受支持版本
或进入 BLOCKED_INCOMPATIBLE_SCHEMA
```

不得静默丢弃未知字段。

# 87. Configuration

配置分层：

```text
静态启动配置
    DB / Object / Queue / Redis Port、Worker Role。

版本化业务配置
    ProcessingProfile、QualityPolicy、ParserCapability。

Secret Ref
    对象、模型、Connector Credential。

运行时容量
    Worker Health、Queue Depth、Admission Snapshot。
```

配置变更不能原地改变已激活 ParsePlan 或正在执行的 Attempt。

# 88. 性能设计

## 88.1 上传

```text
streaming hash
multipart upload
direct-to-object-store
bounded server proxy
incremental malware / MIME checks
```

## 88.2 Parser

```text
只处理需要 OCR 的页面
只对低置信度区域升级
page / region bounded parallelism
CPU / GPU pool separation
GPU micro-batching
render cache
source profile cache
```

## 88.3 数据库

```text
小事务
批量 Block 投影写入
Artifact 大对象外置
SKIP LOCKED Claim
按 Tenant / Status / Deadline 索引
避免每个 OCR token 单行写入
```

## 88.4 下游

```text
Handoff 传 Ref + Hash
不传完整 IR
增量 DocumentVersion
Snapshot 复用
```

性能优化不得牺牲 Hash、SourceSpan、MissingContent 或 Quality Gate。

---

# Part X：测试、Requirement 与完成证据

# 89. 测试分层

## 89.1 Unit

```text
状态转换
幂等键
Hash / Signature 校验
SourceProfile
ParsePlan Validator
Transform Ledger
SourceSpan
Quality Verdict
Failure Mapping
Deletion Policy
```

## 89.2 Contract

```text
Parser Adapter
Object Port
Queue Envelope
Redis Cache Port
Model Gateway
Security Gate
02 → 03 Handoff
02 → 06 IngestionPort
```

## 89.3 Integration

```text
PostgreSQL UoW
S3-compatible Object Store
RabbitMQ
Redis loss / eviction
CPU Parser Worker
GPU / mock model Worker
Outbox / Inbox
Lease / Fencing
```

## 89.4 E2E

```text
上传 → 解析 → Quality → Knowledge Receipt
临时附件 → Agent Wait → Result
Connector 更新 → 新 DocumentVersion
Parser 升级 → 新 ParseSnapshot
删除 → 下游清理 → 物理验证
```

## 89.5 Fault Injection

```text
上传一半断线
对象成功、DB 失败
DB 成功、Outbox 失败
消息重复
Worker 崩溃
Lease 过期
晚到结果
Redis 清空
RabbitMQ 重启
GPU OOM
Provider 503
Hash 篡改
Signature 无效
Knowledge Receipt 丢失
删除部分失败
```

## 89.6 Security

```text
SSRF
DNS rebinding
archive bomb
path traversal
macro / executable
malware fixture
MIME spoof
cross-tenant object access
expired presigned upload
stale security epoch
remote VLM forbidden
```

# 90. 架构 Requirement

| ID | Requirement | Control | Required validation | Evidence |
| --- | --- | --- | --- | --- |
| ARCH-ING-001 | 原始字节必须以不可变 SourceObject 保存，派生结果不得覆盖原对象。 | SourceObject + ObjectCommit | unit/integration/object-store | SourceObject/IntegrityReceipt |
| ARCH-ING-002 | 每次对象提交必须验证 size、content hash 和 media type。 | ObjectCommit VERIFYING | integration/fault | ObjectCommitReceipt |
| ARCH-ING-003 | Parser 读取前必须重新校验 SourceObject Hash。 | Tamper Detection Gate | integration/security | IntegrityCheckRecord |
| ARCH-ING-004 | SourceObject Hash 不匹配时必须 quarantine 并阻止 Handoff。 | SourceObject state machine | fault/security | SecurityFinding |
| ARCH-ING-005 | DocumentVersion 只随源内容或业务版本变化。 | DocumentVersion invariant | unit/contract | DocumentVersionRecord |
| ARCH-ING-006 | Parser、模型或配置变化必须创建新 ParseSnapshot，不创建新 DocumentVersion。 | Reparse protocol | unit/e2e | ParseSnapshot lineage |
| ARCH-ING-007 | 激活后的 ParsePlan 和 ParseSnapshot 不可原地修改。 | Immutable versioning | unit/database | generation/history |
| ARCH-ING-008 | 在线附件和知识库文件必须共享同一 Ingestion Kernel。 | dual surface architecture | e2e/repo-boundary | shared contracts |
| ARCH-ING-009 | Agent Core 不得在 Graph Node 内直接调用文档 Parser。 | IngestionPort boundary | repo/contract | dependency check |
| ARCH-ING-010 | Input 不得生成 RetrievalChunk、Embedding、Index 或 KnowledgeVersion。 | 02/03 ownership | repo/contract | handoff schema |
| ARCH-ING-011 | SourceSpan 不得包含 Knowledge Chunk ID。 | SourceSpan schema | unit/contract | schema validation |
| ARCH-ING-012 | 所有未处理或失败区域必须进入 MissingContentManifest。 | missing-content policy | unit/golden | manifest artifact |
| ARCH-ING-013 | raw、normalized、search 和 model-derived 内容必须分字段保存。 | CanonicalDocumentIR | unit/schema | IR artifact |
| ARCH-ING-014 | 每次 Transform 必须记录输入 Hash、输出 Hash、版本和 Loss Class。 | Transform Ledger | unit/integration | TransformRecord |
| ARCH-ING-015 | 任何 Lossy Transform 只能生成派生 View，不能删除原始内容。 | loss policy | unit/golden | before/after artifacts |
| ARCH-ING-016 | 可靠原生结构存在时不得默认整文档 OCR。 | Parser Planner policy | unit/performance | ParsePlan |
| ARCH-ING-017 | OCR 输出必须保留坐标、置信度、模型版本和图像 Hash。 | OCR Adapter Contract | contract/golden | OCR artifact |
| ARCH-ING-018 | VLM 输出默认标记 MODEL_DERIVED。 | origin classification | unit/contract | block origin |
| ARCH-ING-019 | 远程 OCR/VLM 必须经过 Security Gate 和 Model Gateway。 | remote parser dispatch | integration/security | routing/security receipts |
| ARCH-ING-020 | Parser 选择必须综合格式、文本层、复杂度、安全、成本和 Deadline。 | SourceProfile + ParsePlanner | unit/golden | ParsePlan |
| ARCH-ING-021 | 系统必须支持文件、页面和区域三级 Parser 路由。 | ParseTask DAG | integration/golden | task graph |
| ARCH-ING-022 | Parser Adapter 必须是 Provider-neutral typed contract。 | ParserAdapter Protocol | contract | adapter conformance |
| ARCH-ING-023 | Parser 成功返回不等于 Snapshot 可用。 | Quality Gate | unit/e2e | QualityReport |
| ARCH-ING-024 | Quality Verdict 必须为 PASS、DEGRADED 或 BLOCK。 | ParserQualityReport | unit/contract | verdict record |
| ARCH-ING-025 | BLOCK Snapshot 不得发布给 Knowledge。 | Handoff guard | integration/fault | no handoff evidence |
| ARCH-ING-026 | DEGRADED Handoff 必须由 Profile 明确允许并携带缺失清单。 | degraded policy | unit/e2e | Handoff payload |
| ARCH-ING-027 | Quality Verdict 最终提交必须由确定性 Policy Engine 完成。 | quality ownership | unit/contract | decision record |
| ARCH-ING-028 | ParseJob 与 ParseAttempt 必须分离。 | domain model | unit/database | job/attempt records |
| ARCH-ING-029 | 每个 Attempt 必须绑定 execution epoch、Lease 和 Fencing Token。 | worker protocol | integration/fault | lease record |
| ARCH-ING-030 | Lease 过期后的晚到结果必须被拒绝。 | conditional write | fault | LATE_RESULT_REJECTED |
| ARCH-ING-031 | Queue 采用 at-least-once 语义，消费者必须幂等。 | Inbox/idempotency | integration/fault | duplicate receipt |
| ARCH-ING-032 | 领域 Commit 与消息发布必须使用 Outbox。 | transactional outbox | integration/fault | outbox record |
| ARCH-ING-033 | 消费者必须在领域 Commit 后 ACK。 | Inbox/ACK protocol | integration/fault | delivery/inbox record |
| ARCH-ING-034 | 大型 Payload 只能通过 ObjectRef 传递，不进入 Queue Message。 | message envelope limit | contract/performance | payload ref |
| ARCH-ING-035 | Redis 不得成为任何最终领域状态的唯一来源。 | cache boundary | fault/repo | recovery without Redis |
| ARCH-ING-036 | Redis 清空或驱逐后系统必须保持正确，只允许性能下降。 | cache tolerance | fault | rebuild evidence |
| ARCH-ING-037 | Redis Cache 命中必须校验 Tenant、Input Hash、Bundle Hash 和 Config Hash。 | cache correctness | unit/security | cache key record |
| ARCH-ING-038 | 去重的最终判断必须由 PostgreSQL 唯一约束或条件写完成。 | idempotency store | integration/concurrency | DB conflict receipt |
| ARCH-ING-039 | 默认不得跨 Tenant 进行可观察内容去重。 | tenant isolation | security | cross-tenant test |
| ARCH-ING-040 | 上传、解析和 Handoff API 必须支持 Idempotency-Key。 | API contract | api/integration | idempotency record |
| ARCH-ING-041 | 数据库事务内不得执行对象、Queue、Redis、HTTP、Parser 或模型调用。 | UoW boundary | repo/integration | transaction trace |
| ARCH-ING-042 | 生产 Schema 必须由 Alembic Migration 管理。 | migration policy | repo/migration | migration history |
| ARCH-ING-043 | 完整 IR 的大型权威 Artifact 必须存 Object Store，数据库保存 Ref/Hash 与查询投影。 | storage boundary | integration/performance | artifact refs |
| ARCH-ING-044 | 对象读取必须要求 COMMITTED 状态和 Hash 匹配。 | ObjectRef guard | integration/fault | read receipt |
| ARCH-ING-045 | 对象上传成功但 DB 未提交时必须由 Reconciler 清理孤儿。 | ObjectCommitReconciler | fault | orphan purge receipt |
| ARCH-ING-046 | DB 已提交但消息未发布时必须由 Outbox 恢复。 | OutboxReconciler | fault | published event |
| ARCH-ING-047 | Snapshot 已提交但 Handoff Receipt 丢失时必须幂等重发。 | HandoffReconciler | fault/e2e | duplicate receipt |
| ARCH-ING-048 | 删除必须先阻止新读取，再异步完成下游和物理清理。 | Deletion state machine | e2e/fault | tombstone and receipts |
| ARCH-ING-049 | Legal Hold 只能阻止物理 Purge，不能恢复已撤权内容的新访问。 | security/deletion policy | security/e2e | hold + access evidence |
| ARCH-ING-050 | 删除完成必须有 Input、Knowledge、Object 和 Verification Receipt。 | deletion completion gate | e2e | deletion bundle |
| ARCH-ING-051 | 安全 Epoch 变化必须使不兼容旧 Handoff 对新请求失效。 | security binding generation | security/integration | rebind/revoke event |
| ARCH-ING-052 | 所有远程 URL 获取必须防 SSRF、DNS Rebinding 和无界响应。 | URL security gate | security | attack tests |
| ARCH-ING-053 | Archive 解析必须限制深度、条目数、展开大小和路径。 | container inspector | security | archive tests |
| ARCH-ING-054 | 不可信 Parser 必须运行在受限 Sandbox。 | sandbox profile | security/integration | runtime attestation |
| ARCH-ING-055 | Parser Bundle 必须固定依赖版本、镜像 Digest 和模型权重 Hash。 | artifact provenance | integration | bundle manifest |
| ARCH-ING-056 | 缺失模型权重必须显式失败，不得静默下载并改变版本。 | worker startup policy | fault | MODEL_WEIGHT_MISSING |
| ARCH-ING-057 | Profile 必须版本化、可哈希，并固定到 ParsePlan。 | ProcessingProfile | unit/database | profile ref/hash |
| ARCH-ING-058 | Priority 和 Admission 必须为删除、安全和在线附件保留容量。 | admission policy | load/fault | capacity metrics |
| ARCH-ING-059 | 批量任务不得无限占用页面并行和 GPU Batch。 | bounded parallelism | load | concurrency evidence |
| ARCH-ING-060 | 在线 Fast Snapshot 和高质量 Snapshot 必须是两个独立版本。 | progressive parsing | e2e | snapshot lineage |
| ARCH-ING-061 | 每个 Snapshot 必须绑定 Parser Bundle、Config、IR Schema 和 Quality Policy。 | snapshot provenance | unit/integration | snapshot manifest |
| ARCH-ING-062 | 每个跨模块 Handoff 必须使用 CrossModuleEnvelopeV1。 | shared contract | contract | envelope validation |
| ARCH-ING-063 | Handoff Payload 必须同时校验 payload hash 和 schema hash。 | envelope integrity | contract/security | validation receipt |
| ARCH-ING-064 | Unknown Contract Version、Missing Tenant 和 Stale Epoch 默认 fail-closed。 | consumer guard | contract/security | rejection receipt |
| ARCH-ING-065 | Input 必须保留表格、公式、图片和隐藏内容，或显式声明缺失。 | format fidelity | golden/e2e | IR and missing manifest |
| ARCH-ING-066 | Excel 必须同时保留公式、缓存值和显示值。 | XLSX adapter | golden | cell artifact |
| ARCH-ING-067 | Word 必须保留或声明修订、批注、脚注和页眉页脚。 | DOCX adapter | golden | document artifact |
| ARCH-ING-068 | PPT 必须保留文本框、位置、备注、隐藏页和嵌入对象信息。 | PPTX adapter | golden | slide artifact |
| ARCH-ING-069 | HTML 必须保存原始 Snapshot、最终 URL、重定向链和 DOM 定位。 | HTML adapter | integration/security | web snapshot |
| ARCH-ING-070 | Git / Code 必须绑定 Commit、Blob Hash、Path、Symbol 和 Line。 | Git adapter | integration/golden | code provenance |
| ARCH-ING-071 | ParserQualityReport 必须可计算 SourceSpan Coverage 和 Missing Content。 | quality engine | unit/golden | quality report |
| ARCH-ING-072 | 新 Parser Bundle 必须通过 Shadow Eval 后才能成为 Active Candidate。 | release gate | eval | EvalResult |
| ARCH-ING-073 | 公开 Benchmark 不得替代 Zuno 自己的 Golden Corpus。 | eval governance | repo/eval | dataset manifest |
| ARCH-ING-074 | Trace 不得记录完整敏感文档、明文 Secret 或隐藏思维链。 | telemetry policy | security/observability | redaction test |
| ARCH-ING-075 | 所有状态必须可从 PostgreSQL 和 Object Store 重建，不依赖前端或 Redis。 | recovery invariant | fault/e2e | restart recovery |
| ARCH-ING-076 | Reconciler 必须使用 Claim、Generation 和 Fencing，且修复动作幂等。 | reconciliation contract | fault/concurrency | ReconciliationRecord |
| ARCH-ING-077 | 用户取消 Parse 不得自动删除已提交 SourceObject。 | cancellation boundary | unit/e2e | source remains |
| ARCH-ING-078 | 预算耗尽必须产生缺失声明或 BLOCK，不得伪造完整解析。 | budget policy | unit/fault | missing manifest |
| ARCH-ING-079 | Input API 不得暴露 Bucket Credential、Provider Secret 或内部 Queue 细节。 | API security | api/security | response contract |
| ARCH-ING-080 | Target 只有在代码、Migration、测试、Trace、Eval 和运行证据齐备后才能提升为 Current。 | status governance | repo/governance | production-readiness evidence |

# 91. 完成证据

本模块从 Target 提升为 Current，至少需要：

```text
真实多格式 Adapter 代码
PostgreSQL Alembic Migration
S3-compatible ObjectCommit Integration
RabbitMQ Queue / Inbox / Outbox Integration
Redis Eviction / Loss Fault Test
Worker Lease / Fencing Fault Test
真实 PDF / Office / OCR / Table / Formula Golden Test
SourceSpan Grounding Test
Tamper Detection 与 Signature Test
Crash Matrix Fault Injection
Agent Attachment E2E
Knowledge Handoff E2E
Connector Incremental Update E2E
Deletion / Legal Hold E2E
Trace / Metric / Audit Evidence
Performance / Capacity Measurement
Security Attack Test
Parser Eval 与 Release Gate
Backup / Restore 和 Reconciliation Evidence
```

推荐状态表达：

```text
design available
implementation available
measurement blocked
quality not yet proven
production ready
```

`implementation available` 不等于 `production ready`。没有故障注入、真实文档 Eval、安全验证、删除闭环和运行证据时，不得声明 production ready。

# 92. 明确禁止的实现捷径

```text
只根据文件扩展名选 Parser
把所有格式统一成纯文本后丢弃结构
清洗后删除原文件
用固定置信度伪装 OCR
把 VLM 总结当原文
用 Redis Lock 作为唯一正确性保证
用 Queue ACK 作为领域 Commit
把完整 PDF 放进 RabbitMQ
在数据库事务里调用对象存储或模型
用 create_all 替代 Alembic
Parser Adapter 直接写最终 Snapshot
Input 创建 Knowledge Chunk 或 KnowledgeVersion
Agent Node 直接解析附件
删除数据库行但不清理 Knowledge / Object
MinIO Bucket 默认公开读取
跨 Tenant 暴露内容去重
把文档存在于设计文档当作已经实现
```

---

# Appendix A：研究与成熟项目依据（非规范）

本附录只解释设计来源，不改变前述规范。

## A.1 Docling

Docling 将 PDF、Office、图片和其他格式转换为统一的结构化文档表示，并保留 Layout、Table、图片和 Provenance 能力。Zuno 借鉴其“统一表示 + 可替换 Pipeline”，但不把 CanonicalDocumentIR 绑定到 Docling 类型。

- Technical report: https://arxiv.org/abs/2408.09869
- Supported formats: https://docling-project.github.io/docling/usage/supported_formats/

## A.2 MinerU2.5 / MinerU2.5-Pro

MinerU2.5 的 coarse-to-fine 方案将低分辨率全局布局分析和原分辨率局部识别分离，支持 Zuno 的文件、页面、区域三级路由。MinerU2.5-Pro 对困难样本、数据质量和 Judge-and-Refine 的强调，支持项目级 Golden Corpus、冲突验证和精细质量门。

- MinerU2.5: https://arxiv.org/abs/2509.22186
- MinerU2.5-Pro: https://arxiv.org/abs/2604.04771

## A.3 PaddleOCR / PaddleOCR-VL

PaddleOCR 的 OCR、结构和文档 VLM 分层说明本地轻量 OCR 与高质量 VLM 应是级联能力，不应将所有文档默认发送给大模型。

- PaddleOCR 3.0: https://arxiv.org/abs/2507.05595
- PaddleOCR-VL-1.6: https://arxiv.org/abs/2606.03264

## A.4 olmOCR

olmOCR 展示了针对大规模 PDF 的 VLM 解析和批处理价值。Zuno 将其视为可选高质量 GPU Adapter，而不是所有上传的默认依赖。

- https://arxiv.org/abs/2502.18443

## A.5 Unstructured 与 Apache Tika

Unstructured 展示按文件类型路由、Fast / Hi-Res / OCR Strategy 和结构元素输出；Apache Tika 展示广泛格式检测与元数据提取。Zuno 可以把它们用作 Adapter 或长尾 Fallback，但必须保留自身 Contract、质量门和 Provenance。

- https://docs.unstructured.io/open-source/core-functionality/partitioning
- https://tika.apache.org/

## A.6 W3C PROV

W3C PROV 的 Entity、Activity、Agent 与 generated / used / derived-from 关系为 Zuno 的 SourceObject、ParseAttempt、Snapshot 和 Transform Provenance 提供概念基础。

- https://www.w3.org/TR/prov-overview/

## A.7 RabbitMQ Quorum Queue

RabbitMQ Quorum Queue 的持久复制、Publisher Confirm、Manual ACK 和 Delivery Limit 适合作为服务器端可靠工作队列 Adapter。Zuno 仍通过 Inbox、Outbox、Idempotency 和 Fencing 保证业务一致性。

- https://www.rabbitmq.com/docs/quorum-queues

## A.8 Redis

Redis 适合作为可驱逐的热缓存、进度投影、Admission 和容量加速层。因为 Key 可以过期或被驱逐，Zuno 明确不让 Redis 成为领域终态、安全、Lease 或删除事实的唯一来源。

- https://redis.io/docs/latest/develop/reference/eviction/

## A.9 S3 Object Lock

S3 Object Lock 的 Versioning、Retention 和 Legal Hold 提供 WORM 能力。Zuno 将其作为受监管 Profile 的可选 Infrastructure Capability，不写死为所有 Workspace 的必需项。

- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html

---

# Appendix B：模块标识

```text
Module Number: 02
Module Name: Input / Document Ingestion
Canonical Owner Namespace: INPUT_INGESTION
Formal Target Document: docs/modules/02-input-document-ingestion.md
Primary Upstream: Product Surface / Connector / Agent Attachment
Primary Downstream: 03 Knowledge / 06 Agent Core
Control Dependencies: 09 Security / 10 Observability & Eval / 11 Infrastructure / 04 Model Gateway
```

本文是架构设计，不是执行计划。后续 Codex Program 必须将实现任务、Migration、切流、回滚和验证命令写入独立 `.agent/programs/`，不得把执行阶段重新塞回本文。
