# Zuno

Zuno 是一个面向企业内部资料和业务系统、**前后端分离**、基于 LangGraph Single Controller 的可治理自定义 Agent / Agentic GraphRAG 平台。

它不是单一 RAG 聊天机器人、Prompt 管理器、MCP 工具箱或模型 SDK 包装层。Zuno 把企业资料摄取、证据检索、任务规划、上下文与记忆、模型路由、能力选择、工具执行、安全审批、可观测性、评测和恢复统一到一套可版本化、可审计的运行架构中。

## 产品与部署形态

```text
Web Client（Vue 3 + Vite）
Desktop Client（Electron）
External API Client
        |
        | HTTP Command / Query + SSE Projection Stream
        v
FastAPI Product Surface
        |
        v
LangGraph Single Controller Agent Runtime
        |
        +--> Knowledge / Agentic GraphRAG
        +--> Memory & Context
        +--> Model Gateway
        +--> Capability / Skill
        +--> Tool Runtime
        |
        v
Security + Observability & Eval + Infrastructure
```

主要代码入口：

```text
apps/web/               Web 工作台
apps/desktop/           Desktop 宿主与受控桥接
src/backend/zuno/       后端 API、Agent Runtime 与领域模块
```

前端只消费后端提供的版本化 Contract、Authorized Projection、AvailableAction、HTTP Query/Command 和 SSE 事件，不拥有 Plan、Evidence、Approval、Tool Effect、Memory、Eval 或 RunOutcome 等领域事实。

Zuno 支持本机开发和轻量部署，但“本地优先”不再是产品定位。Target 允许一个后端镜像承担多个角色，也允许按压力逐步拆分；十一个逻辑模块不是十一微服务的强制部署方案。

## Current、Target 与 Future

README 同时展示 Current 和 Target，但二者不能混为一谈。

| 范围 | 当前状态 |
| --- | --- |
| Web / Backend | 前后端分离实现已存在；Web、Desktop、Product API client、HTTP/SSE Contract 与浏览器 E2E 已有工程证据 |
| Agent Core | Single Controller、固定 AgentRunGraph、动态 Plan DAG、固定 StepExecutionGraph、并行控制、Final Gate 与 Publication 已有实现基线 |
| Memory & Context | Candidate、Governance、MemoryVersion、ContextPack、CompressionTrace 和 MemoryUseTrace 已有实现基线 |
| Agentic GraphRAG | 现有 KnowledgeRetrievalGraph、RetrievalPlan/Round、EvidenceLedger/Frontier、Corrective Retrieval 和 KnowledgeControlProposal 已有实现基线 |
| Evidence-Driven Agentic GraphRAG v2 | `accepted-target`，设计可用；Claim-level Evidence Deliberation、Evidence Reasoning Graph 和 Targeted Probe 尚不能声明为 Current |
| Eval 与发布质量 | 工程收口已完成；固定测量仍为 blocked，quality not yet proven，production readiness not established |

正式状态事实以 [`docs/status/production-readiness.md`](./docs/status/production-readiness.md)、最新代码、Migration、测试、Trace、Eval 和 Evidence 为准。README、类名、表名、Phase 名称或架构图本身都不能证明 Target 已实现。

## 四组架构总览

Zuno 的十一逻辑模块按照领域 Ownership 独立维护。为了理解整个系统，可以归纳为四组：

```text
01 Product Surface
02 Input / Document Ingestion
    产品入口与知识供给
            |
            v
03 Knowledge / Agentic GraphRAG
05 Memory & Context
06 Agent Core / Planning & Control
    智能核心
            |
            v
04 Model Gateway
07 Capability / Skill
08 Tool Runtime
    能力执行层

09 Security
10 Observability & Eval
11 Infrastructure
    横向贯穿全部模块的治理与运行底座
```

这四组只是便于理解的逻辑视图，不是新的事实 Owner，也不是物理部署层级。正式 Target 仍以十一份模块文档、已接受 ADR 和共享 Contract Registry 为准。

### 1. 01 + 02：产品入口与知识供给

```text
01 Product Surface
    人和任务怎样进入系统，用户怎样看到状态和结果。

02 Input / Document Ingestion
    企业资料怎样变成可索引、可引用、可追踪的知识输入。
```

#### 01 Product Surface

Product Surface 是统一北向产品边界，负责：

```text
Web / Desktop / External API
Tenant / Workspace / Agent Studio / Agent Catalog
Conversation / Submission / RuntimeRequest
HTTP Command / Query
SSE Snapshot / Delta / Resume / Resync
AvailableAction / Interrupt / Approval / Cancel
Citation / Artifact / Quality / Blocked / Partial 展示
```

它拥有用户交互、Conversation、Submission、ProductCommand、Projection 和 ChannelDelivery，但不创建或激活 Plan，不直接调用模型、Retriever 或 Tool，也不把 HTTP 2xx、SSE Close 或客户端渲染当成 AgentRun 成功。

#### 02 Input / Document Ingestion

Ingestion 把原始文件转换为可靠知识输入：

```text
SourceObject
-> DocumentVersion
-> ParsePlan / ParseJob / ParseAttempt
-> CanonicalDocumentIR
-> SourceSpan
-> Quality Gate / Human Review
-> IndexableDocumentSnapshot
```

它拥有文件版本、内容 Hash、解析状态、Canonical IR、原始 SourceSpan 和索引交接。没有 DocumentVersion 与 SourceSpan，后续检索、GraphRAG 和 Citation 就无法形成可信证据链。

### 2. 03 + 05 + 06：智能核心

```text
06 Agent Core
    管整个任务怎么完成。

03 Knowledge
    管当前结论需要什么证据，以及证据是否充分。

05 Memory & Context
    管当前模型应该看到什么，以及什么历史经验值得保留。
```

#### 06 Agent Core：任务控制中枢

一次 AgentRun 只有一个 Single Controller：

```text
固定 AgentRunGraph
+
动态 Plan DAG
+
固定 StepExecutionGraph
```

所有任务都有 Plan：简单任务使用 Deterministic Single-Step Plan，复杂任务使用 Dynamic DAG Plan。正式回答不能绕过 TaskContract、GoalVersion、Plan、Trace、Budget、AnswerPolicy、Final Gate、Publication 和 RunOutcome。

五种机制有不同作用域：

```text
Plan-and-Execute
    管任务目标、依赖、并行和完成条件。

ReAct
    管单个 Step 内 Action -> Observation -> 下一 Action 的有界循环。

Reflection
    判断 Action、Step、Join 或最终结果是否合格。

Replan
    原计划结构、依赖或核心假设失效时创建新的不可变 PlanVersion。

Reflexion
    Run 结束后生成受治理的跨任务经验候选，不直接写长期 Memory。
```

Retry、Parameter Repair、Executor Escalation、Capability Fallback、Step Repair、Reflection 和 Replan 必须区分。Replan 经过 Replan Barrier；不可逆副作用必须先完成或 Reconcile，不能靠重写计划掩盖 UNKNOWN Outcome。

#### 03 Knowledge / Agentic GraphRAG：证据决策中枢

Knowledge 不发布最终答案，而是拥有：

```text
KnowledgeVersion / KnowledgeSnapshot
IndexSpec / IndexManifest 接受语义
EvidenceRequirement
RetrievalPlan / RetrievalRound
BM25 / Vector / Graph / Structured Retrieval
EvidenceLedger / EvidenceFrontier
Fusion / Rerank / CitationLineage
CorrectiveRetrievalDecision
SelectedEvidenceBundle
KnowledgeControlProposal
```

现有 Current 已具备固定 KnowledgeRetrievalGraph 和动态 RetrievalPlan/Round 的内层 Agentic GraphRAG 基线。

下一版 Target 由 [`ADR 0006`](./docs/decisions/0006-evidence-driven-agentic-graphrag.md) 定义，进一步引入：

```text
Broad Evidence Discovery
Evidence Deliberation
Claim-level Evidence State
Evidence Reasoning Graph
Targeted Evidence Probe
Safe Stop and Diagnosis
```

它把质量中心从“检索到相关 Chunk”提升到“Evidence 是否足以支持关键 Claim”。原文、Graph Local 和 Community Summary 若同源，不能被重复计票；冲突、过期、适用范围和授权边界必须显式处理。

ADR 0006 目前只证明 `design available`，不证明上述 v2 Runtime、Migration、Benchmark 或质量提升已经实现。

#### 05 Memory & Context：上下文与经验中枢

Memory & Context 同时回答：

```text
过去什么值得记住？
当前这次模型调用应该看到什么？
```

三个正交维度：

```text
生命周期：Working -> Session -> Long-term
长期类型：Episodic / Semantic / Procedural
压缩强度：C0 / C1 / C2 / C3
```

长期 Memory 必须经过 Candidate、Evidence、Scope、Security、Dedup、Conflict、Governance、Version、Projection Verification 和 Activation。模型不能直接写 Active Memory。

`ContextPackVersion` 是一次模型调用的不可变预算化读取视图，可以组合 Goal、Plan、Session Summary、Memory、Knowledge Evidence、Tool Observation 和 Policy，但不替代这些 Source Owner，也不替代 LangGraph Checkpoint。

三个核心模块形成闭环：

```text
06 Agent Core 创建 Goal、Plan 和 Step
        |                         |
        v                         v
05 Memory & Context         03 Knowledge
构造 ContextPack            获取并审议 Evidence
召回约束和经验              判断充分、冲突和缺口
        |                         |
        +-----------+-------------+
                    v
              06 Agent Core
      ReAct / Reflection / Replan
                    |
                    v
           Final Gate / RunOutcome
                    |
                    v
          Reflexion Candidate
                    |
                    v
          05 Memory Governance
```

### 3. 04 + 07 + 08：能力执行层

智能核心决定“下一步应该做什么”，能力执行层把这个决定映射为模型调用、能力候选和受治理的真实动作。

```text
04 Model Gateway
    提供统一模型调用、Role、Routing、Usage 和 Provider Failure 语义。

07 Capability / Skill
    描述系统能做什么、任务应如何做、哪些实现可以成为规划候选。

08 Tool Runtime
    执行一次具体 Tool 动作，并确认执行与外部效果事实。
```

#### 04 Model Gateway

Planner、Executor、Query Rewriter、Extractor、Critic、Synthesizer、Embedding、Rerank、Vision 和 Judge 等模型调用统一进入 Model Gateway。

Gateway 管理 Model Role、Operation、Prompt Artifact、Provider、Routing、Quota、Usage、Fallback、Streaming 和 Structured Output。模型只产生 Proposal、Candidate、Score 或 Model Result，不拥有 Plan、Evidence、Authorization、MemoryVersion 或 RunOutcome。

模型 Provider 调用归 04；底层即使使用 HTTP 或 SDK，也不会因此进入 Tool Runtime。

#### 07 Capability / Skill：能力语义控制面

Capability / Skill 回答：

```text
系统能做什么？
完成这类任务通常应该怎样做？
当前哪些实现满足语义、版本和环境约束？
为什么选择或拒绝某个候选？
```

07 拥有：

```text
CapabilityDefinition / CapabilityVersion
CapabilityRequirement
SkillDefinition / SkillVersion
Skill Instruction / Resource Manifest / Acceptance Criteria
ToolCapabilityDescriptor / ToolDefinitionRef
CapabilityProviderBinding
ProviderConformanceRecord
CapabilityAvailabilitySnapshot
CapabilitySelectionResult
```

Capability 使用稳定业务语义身份；Skill 是使用若干 Capability 完成任务的方法包、SOP、约束和验收方式。

07 可以发现、过滤和选择候选能力，但：

```text
不执行 Tool
不持有 Secret
不批准权限
不提交外部效果
不激活 Plan
```

#### 08 Tool Runtime：受治理工具效果执行平面

Tool Runtime 回答：

```text
这一次具体 Tool 动作如何准备、授权、执行、观察、对账和恢复？
```

08 拥有权威可执行定义和执行事实：

```text
ToolProviderDefinition
ToolDefinition / ToolVersion / ToolOperation
ToolInstallation / Activation
PreparedToolAction
ToolAttempt
ToolObservation
ToolExecutionReceipt
EffectReceipt
EffectReconciliation
Adapter Binding / Conformance
```

一次真实工具动作遵循：

```text
ActionProposal
-> PreparedToolAction
-> Schema / Target Resource / Effect Classification
-> Security Authorization / Approval
-> Idempotency Claim / Lease / Secret Lease
-> Sandbox or Adapter Dispatch
-> ToolAttempt / ToolObservation
-> ToolExecutionReceipt
-> EffectReceipt or EffectReconciliation
-> Agent Core Step Acceptance
```

Timeout、响应丢失或进程崩溃后，Tool Runtime 必须先确认外部效果是否已经发生；副作用 Outcome 为 UNKNOWN 时，禁止跨 Provider 盲目 Retry。

#### Capability / Skill 与 Tool Runtime 的边界

| 维度 | 07 Capability / Skill | 08 Tool Runtime |
| --- | --- | --- |
| 核心问题 | 能做什么、应该怎样做、哪个候选满足要求 | 这一次具体动作怎样安全执行并确认效果 |
| 主要对象 | Capability、Skill、Requirement、Binding、Availability、Selection | ToolDefinition、PreparedToolAction、Attempt、Observation、Execution/Effect Receipt |
| 输出给 Agent Core | 版本化能力候选、选择结果和拒绝理由 | 实际执行、观察、效果与对账事实 |
| 是否真实执行 | 否 | 是 |
| 是否持有 Secret | 否 | 只消费受限 Secret Lease |
| 是否批准权限 | 否 | 否，只消费 Security Decision |
| 是否拥有 Plan | 否 | 否，Agent Core 拥有 |
| 是否拥有外部效果 | 否 | 是，拥有 EffectReceipt / EffectReconciliation |

完整交接链路：

```text
PlanStep
-> CapabilityRequirement
-> CapabilityAvailabilitySnapshot
-> CapabilitySelectionResult
-> Agent Core StepFeasibilityDecision
-> ActionProposal
-> Tool Runtime PreparedToolAction
-> Security / Approval / Idempotency / Secret / Sandbox
-> ToolAttempt / Observation / Effect
-> Agent Core Step Acceptance
```

必须保持：

```text
Skill != Capability
Capability != Tool
Availability != Authorization
Availability != Execution Readiness
Capability Selection != Step Feasibility
Function Calling != Tool Execution
Approval != Dispatch
HTTP 2xx != EffectReceipt
ToolExecutionReceipt != Agent Step Accepted
```

Tool Runtime 不是万能 Integration Bus。Knowledge Retrieval 归 03，模型调用归 04，Memory / Context 归 05，Plan / Control 归 06；模块内部普通函数、Repository 或专业领域 Runtime 不会因为使用 HTTP、SDK 或 Queue 就自动变成 Tool。

### 4. 09 + 10 + 11：治理与运行底座

这三个模块横向贯穿请求、检索、模型、记忆、工具和最终发布的完整生命周期。

```text
09 Security
    确定谁可以访问什么、执行什么、披露什么。

10 Observability & Eval
    记录发生了什么，并证明系统是否真的更好。

11 Infrastructure
    提供持久化、消息、对象、Checkpoint、Lease、恢复和部署 Primitive。
```

#### 09 Security

Security 拥有 Identity、Authorization、ACL、Security Epoch、Approval Policy、Credential / Secret Binding、Data Classification、Disclosure、Revocation 和 Audit Requirement。

安全门禁发生在检索、Context 构造、模型调用、工具准备与执行、Memory 提交和最终发布之前。模型、Capability、Tool Runtime 和 Product Surface 都不能自行扩大权限或伪造 Approval。

#### 10 Observability & Eval

Observability 记录 PlanVersion、Step、Model Invocation、KnowledgeSnapshot、RetrievalRound、Reflection、Replan、Tool Effect、Budget、Publication 和 Failure 等结构化 Trace。

Eval 使用固定 Dataset、Case、Profile、Metric 和 Release Gate 比较 Vector-only RAG、Hybrid RAG、Fixed GraphRAG、Agentic Routing 和 Evidence-Driven Agentic GraphRAG。文档、Demo 或单次成功不能证明质量提升。

#### 11 Infrastructure

Infrastructure 提供：

```text
PostgreSQL
RabbitMQ / Queue
MinIO / S3-compatible Object Store
LangGraph PostgreSQL Checkpointer
Transaction / UoW
Outbox / Inbox
Lease / Fencing
Idempotency Claim
Backup / Restore
Deployment / Health / Capacity
```

基础设施 Receipt 不等于上层业务成功：

```text
Index write success != KnowledgeVersion accepted
Queue ACK != Tool Effect success
Checkpoint commit != AgentRun domain commit
Object upload success != Artifact published
```

## 端到端关系

```text
用户通过 01 提交任务
-> 02 提供可靠文档、Canonical IR 和 SourceSpan
-> 06 创建 Goal、Plan 和 Step
-> 05 构造 ContextPack、召回约束和经验
-> 03 获取并审议 Evidence
-> 07 解析 CapabilityRequirement 并选择候选
-> 04 执行受治理模型调用
-> 08 执行具体 Tool 动作并确认 Effect
-> 06 完成 Acceptance、Reflection、Replan 和 Final Gate
-> 01 展示 Answer、Citation、Artifact、Blocked 或 Partial Outcome
```

整个过程中：

```text
09 保证每次读取、执行和披露被允许。
10 保证每次关键决策可观测、可评测、可证明。
11 保证领域事实可靠持久化、可恢复、可幂等重放。
```

## 文档入口

- [Zuno 项目知识入口](./docs/project/README.md)
- [总体 Target 架构](./docs/project/architecture/architecture.md)
- [架构视图 HTML](./docs/project/architecture/architecture.html)
- [十一逻辑模块设计](./docs/project/modules/README.md)
- [Production Readiness 状态](./docs/status/production-readiness.md)
- [Evidence-Driven Agentic GraphRAG ADR](./docs/decisions/0006-evidence-driven-agentic-graphrag.md)
- [架构决策](./docs/decisions/README.md)
- [Repository Ownership Matrix](./docs/governance/repo-ownership-matrix.md)
- [文档总入口](./docs/README.md)
- [当前证据入口](./docs/evidence/README.md)
- [历史归档入口](./docs/history/README.md)

十一模块：

- [01 Product Surface](./docs/project/modules/01-product-surface.md)
- [02 Input / Document Ingestion](./docs/project/modules/02-input-document-ingestion.md)
- [03 Knowledge / Agentic GraphRAG](./docs/project/modules/03-knowledge-agentic-graphrag.md)
- [04 Model Gateway](./docs/project/modules/04-model-gateway.md)
- [05 Memory & Context](./docs/project/modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./docs/project/modules/06-agent-core-planning-control.md)
- [07 Capability / Skill](./docs/project/modules/07-capability-skill.md)
- [08 Tool Runtime](./docs/project/modules/08-tool-runtime.md)
- [09 Security](./docs/project/modules/09-security.md)
- [10 Observability & Eval](./docs/project/modules/10-observability-eval.md)
- [11 Infrastructure](./docs/project/modules/11-infrastructure.md)

## Program 状态

- 当前 active program：无；`zuno-canonical-architecture-runtime-realization-v1` 已归档
- 最近收口：Program1 queued design 的 repository closure follow-up 已完成，未激活完整七阶段实现计划
- Program 入口：[`.agent/programs/current.md`](./.agent/programs/current.md)

当前仍以最新 Current、正式架构文档和 closure evidence 为准。ADR 0006 是下一版 accepted-target overlay；新的实现 Program 需在设计确认后由用户明确打开。

## 开发与验证入口

### 后端

```bash
poetry install
poetry run uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

### Web 前端

在仓库根目录：

```bash
npm install
npm run frontend:dev
```

或在 `apps/web/`：

```bash
npm install
npm run dev
```

Web 默认连接 `http://127.0.0.1:7860` 的后端 HTTP / SSE 接口。

### Desktop

```bash
npm install
npm run desktop:dev
```

### 文档与仓库验证

```bash
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py
```

完整依赖、容器、Migration、Fault、E2E 和 CI 验证以当前代码、文档和 Workflow 为准。

## Agent 协作

仓库治理与 Agent 协作规则见：

- [`AGENTS.md`](./AGENTS.md)
- [`.agent/references/workflow.md`](./.agent/references/workflow.md)
- [`.agent/references/task-routing.md`](./.agent/references/task-routing.md)

Worker 贡献只是候选；架构 Owner 与 Coordinator 必须审查 Diff、Contract、状态机、错误语义、安全、恢复、测试和 Evidence 后再合并。README 不记录机器专属 worktree 绝对路径、个人环境或临时 Session。

## 当前质量声明

```text
implementation available
measurement in progress / blocked by formal benchmark prerequisites
quality not yet proven
production readiness not established
```

现有 Agentic GraphRAG Inner Loop 已有实现与 focused verification；Evidence-Driven Agentic GraphRAG v2 仍是 accepted-target。固定 Benchmark、正式四 Profile measured runtime、Reviewer / Credential / Budget attestation、完整 Closure 和 Release Gate 尚未完成前，不得声明 Agentic GraphRAG 稳定优于 Baseline，也不得声明 production ready。
