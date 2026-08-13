# Zuno 总体 Target 架构

updated: 2026-08-13
status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Product、Domain、Logical Capability、Service、Data、Security、Eval 和 Deployment 如何形成可恢复的目标闭环？
owner: Cross-cutting Architecture Owner
acceptance_scope: Canonical Target；实现、测量和外部资格仍未完成
document_role: cross-cutting integration source
canonical_taxonomy: docs/project/product/、domain/、agents/、knowledge/、services/、data/、security/、eval/、deployment/
current_state_source: docs/status/production-readiness.md and docs/evidence/
decision_sources: docs/decisions/0008-legal-domain-kernel-and-host-boundary.md、0009-python-only-backend.md、0010-microservice-target-and-service-boundaries.md、0011-architecture-document-taxonomy.md

> 本文只回答跨领域集成问题。各专题的唯一 Contract、Owner 和状态由对应专题文档持有，本文不创建第二套 Domain State Machine。

## Part A — Architecture Narrative

### 这套架构要解决的业务问题

Zuno 的目标不是增加一个聊天入口，而是帮助司法或专业法律人员把分散的案件材料转化为可追溯、可复核的工作成果。这个任务同时包含业务事实、证据来源、长期执行、人工判断和可能改变外部世界的工具动作。若把它们都压缩进聊天上下文或某个 Agent Checkpoint，用户就无法判断结论基于哪一版材料，也无法解释新证据到来后旧结论为何失效。

### 一个完整的案件分析场景

这是 Target Scenario，不是历史事实：

用户创建 Matter 并上传材料；系统生成带 hash、来源和权限的 DocumentVersion，Knowledge 层解析 SourceSpan 并提供 EvidenceCandidate。Agent Runtime 根据任务形成 Plan，协调证据、争议和法律研究工作，Legal Capability 产生 FactProposal、ConflictProposal 或 FindingProposal。Domain Owner 在证据、版本、权限和必要人工复核通过后提交 Canonical Domain Version；Review 产生 HumanDecision，最终形成 WorkProduct。若需要外部动作，Tool/Security 边界只执行已授权 PreparedAction 并返回 EffectReceipt。

这条路径的关键不是组件数量，而是每一步都知道自己在处理什么类型的对象，以及哪个 Owner 可以把候选提升为正式事实。

### 业务语义、逻辑能力与物理部署

Zuno 的三层关系是：

Product / Domain：定义 Matter、Evidence、Finding、Review 和 WorkProduct 等业务语义；
Logical Capability：定义检索、法律智能、规划、工具、安全和评测等可替换能力；
Physical Service / Deployment：承载 API、长任务、重型 Worker、对象存储和索引 Provider。

本文将第二层称为 Logical Capability Architecture，将第三层称为 Physical Service / Deployment Architecture。上一阶段的 11 Logical Modules + 1 Architecture 只属于 History，不是当前物理服务清单。

业务语义需要稳定，计算 Provider 可以替换，Agent Profile 可以组合。Logical Capability 不等于 Service，Service 不等于 Process，Process 不等于 Container，也不等于团队。这个分离使 WorkBuddy 等外部 Host 可以调用 Legal Backend，也使 Native Runtime 能在公平评测中被保留或删除。

### 责任边界与不拥有的事实

Platform/Domain Owner 拥有 Canonical Business State；Agent Runtime 拥有 Run、Plan、Step、Checkpoint 等控制状态；Knowledge Owner 拥有解析、索引、检索投影和证据候选；Tool Owner 拥有 EffectReceipt 和对账；Security Owner 拥有授权、Approval 和 SecurityEpoch；Eval Owner 拥有数据集、结果和 Release Decision。

任何 Provider、Queue、Checkpoint、Memory 或 Graph 都不能直接声称法律事实。它们不负责创建 FindingVersion、HumanDecision 或 WorkProduct。跨边界只传 Proposal、Candidate、Reference、Snapshot、Receipt 或明确版本的 Query Result。

### 为什么需要这些边界

最小替代方案是 WorkBuddy 或其他 Host 加 Legal Backend；另一个替代方案是模块化 Python 服务加独立 Worker。Zuno 只有在复杂案件中证明 Domain State、Evidence Gate、Staleness、Human Review 或恢复对账带来可重复收益时，才有理由保留更强的 Native Runtime。Python-only 是目标约束，但 CPU-heavy OCR、Embedding、Graph Build 和 Eval 必须离开 API 请求线程；Microservice 是部署目标，但服务数量仍由独立扩缩容、故障、安全、资源和生命周期证据决定。每个候选都要回答 Why service? Why not library? Why not worker?。

### 最危险的失败与恢复

最危险的情况是 Domain Commit 已经成功，而 Runtime Checkpoint 仍停在执行前；或者 Tool 已经执行，Queue 又重复投递，Agent 误以为副作用未发生。另一类危险是新 Evidence 使旧 Fact、Conflict 或 Finding stale，但旧 WorkProduct 仍被展示为最终答案。恢复必须以 Domain Owner 的已提交版本和 EffectReceipt 为依据，对账后再 Resume、Retry、Replan 或请求 Human Review，不能把 HTTP 200、Queue ACK 或 Checkpoint 当成业务成功。

### 取舍与反转条件

这套架构付出的成本是版本、跨服务序列化、可观测性、恢复测试和部署运维复杂度。它换取的是业务状态不被 Runtime Provider 污染、证据链可追溯、外部动作可审计和服务资源可以隔离。若 A/B/C Benchmark 显示 C 与 B 没有稳定增益，应缩减 Native Runtime；若 Hybrid RAG 已经覆盖 Graph 任务，应让 Graph 退为条件 Provider；若模块化服务加 Worker 已满足同样的隔离和恢复语义，应合并服务。当前代码只证明部分 Python/FastAPI/Worker 表面；服务收益、质量收益、安全证明和生产状态仍属于 Current、Target、Hypothesis、Future 或 History 边界中的 Gap。

## Part B — Detailed Architecture Specification

### Cross-layer Contract Registry

| Contract | 输入 | 输出 | 唯一 Owner | 失败与验证 |
|---|---|---|---|---|
| Domain Admission | 带 DomainVersion 的 Proposal、Evidence Reference、权限上下文 | Canonical Version、review_required 或 rejected | Platform/Domain | CAS 冲突、来源不足；Admission Contract Test |
| Runtime Execution | PlanVersion、Domain Snapshot、Budget | Step/Branch Result、Checkpoint、RunOutcome | Agent Runtime | Checkpoint 与 Domain Generation 不一致；Recovery Replay |
| Evidence Retrieval | QueryClass、Claim、Scope、DocumentVersion | EvidenceCandidate、CitationLineage、RetrievalReceipt | Knowledge | 索引 stale、ACL 泄漏、引用错 span；Citation/Graph Ablation |
| External Effect | PreparedAction、SecurityEpoch、Approval | EffectReceipt、outcome_unknown 或 rejected | Tool/Security | 超时、重复副作用；Idempotency/Fault Injection |
| Evaluation | DatasetVersion、Variant、预算、Trace | RawResult、Metric、Comparison、ReleaseDecision | Eval | 分母变化、不可比、阻塞；Reproducible Eval |

### Service、通信与队列边界

Edge/API 负责认证、路由、上传、Review 和 Run 接口；Platform/Domain 负责事务型业务状态；Agent Runtime 负责长任务和控制状态；Knowledge 负责摄取、检索和投影；Tool/Sandbox 负责高风险动作。候选物理角色是 edge-api、platform-domain-service、agent-runtime-service、knowledge-service 和 tool-sandbox-service；五个角色不是冻结的服务数量，也不是 Current。五个候选服务角色，不是冻结的服务数量，也不是 Current。Eval 可以是独立批处理 Worker，不因存在评测目录就成为同步 CRUD 服务。

CRUD、小命令和外部互操作默认使用 HTTP/API；Agent Run、Ingestion、Embedding、Graph Build、Sandbox 和 Eval 使用带 JobId、Attempt、Timeout、Cancellation、Retry、DLQ 和 Backpressure 的队列。高吞吐内部 gRPC 只是 Candidate。Queue ACK、Index Write、Checkpoint Commit 和 HTTP 2xx 各自只能证明本边界。

FastAPI 是 Application / HTTP Interface；LangGraph 若被保留，只承担 Agent orchestration、Checkpoint 和 Resume，不承载普通 CRUD。PostgreSQL 保存 Canonical Domain State；LangGraph Checkpoint 保存 Graph Control State。Checkpoint、DomainVersion 与 Reconciliation 必须分开验证，不能把 Runtime State 当作法律事实。

### State、Version 与 Recovery Contract

DomainVersion 是业务事实版本；PlanVersion 激活后不可变；Step 必须记录输入 DomainVersion/Snapshot。提交时版本不一致只能进入 conflict、retry、replan、review_required 或 rejected。Runtime Checkpoint 保存控制位置，不保存 Canonical Case Fact。Recovery 先读取最后合法 DomainGeneration，再检查 EffectReceipt、Provider Operation ID、Outbox/Inbox 和当前权限，最后决定 Resume、Retry、Replan 或人工介入。

### Owner Registry

| Owner | Canonical State | 允许跨边界输出 |
|---|---|---|
| Domain | Matter、DocumentVersion、Fact、Evidence、Conflict、Finding、HumanDecision、WorkProduct | Proposal、Version、Reference |
| Runtime | AgentRun、Plan、Step、Branch、Reducer、Interrupt、Checkpoint、Budget | Snapshot、RunOutcome、Control Receipt |
| Knowledge | Source、Parse、Chunk、Index、Retrieval、CitationLineage、Projection | Candidate、Reference、Retrieval Receipt |
| Security | Principal、Grant、Approval、SecurityEpoch、Policy Decision | Authorization Decision |
| Tool | PreparedAction、ToolAttempt、EffectReceipt、Reconciliation | Receipt、Outcome |
| Eval | DatasetVersion、EvaluationRun、Metric、Comparison、ReleaseDecision | Evidence Report |

### Security、Deployment 与验证要求

每个跨边界操作绑定 Tenant、Matter、Scope、Policy Epoch、Idempotency Key 和 Trace。不可逆 Effect 必须 execute-time 授权和 Approval；不可信文档不能改写策略。Developer、Staging、Production 是不同证据等级，不因 Compose、Kubernetes、容器或配置文件存在而声称生产就绪。验证必须覆盖质量、效率、失败恢复、No-egress、租户隔离、工具副作用和替换成本。

### Implementation / Measurement / External Gaps

Current 只由代码、测试、Trace、Migration 或真实运行证据证明；Target 记录 Python-only、Domain/Runtime 分离和候选服务边界；Hypothesis 包括 Native Runtime、Graph、Memory、服务数量和安全可验证性收益；Gap 包括 Court QA、A/B/C、负载、故障注入、HA、备份恢复和外部资格。History 只保存被替换的 11+1 组织方式和旧过程材料。

专题路由：`product-architecture.md`、`legal-domain-model.md`、`domain-state-lifecycle.md`、`agent-platform.md`、`multi-agent-runtime.md`、`knowledge-evidence-architecture.md`、`service-architecture.md`、`data-ownership-and-recovery.md`、`security-architecture.md`、`legal-eval-and-benchmark.md`、`microservice-deployment.md`。这些专题各自拥有一个 Canonical Question；总架构只负责跨层关系，不复制专题状态机。
