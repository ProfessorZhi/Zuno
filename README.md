# Zuno

Zuno 是一个本地优先、短小精悍但工程完整的 **Lean Complete Agentic GraphRAG Product**。

用户可以配置模型、创建 Workspace、上传资料、解析和索引文档，通过 AgentChat 使用标准检索或深度检索，由 Single Controller Agent 完成规划、混合检索、GraphRAG、证据整理、claim-level citation、回答生成、trace、成本统计和反馈。

## 当前定位

近期目标不是大规模分布式企业平台，而是一条真实可运行、可演示、可评测、可恢复的企业知识库 Agent 产品链路：

```text
配置模型
-> 创建 Workspace
-> 上传文档
-> Parse / Index
-> AgentChat 提问
-> ContextPack
-> RetrievalPlan
-> BM25 + Vector + optional Graph
-> EvidenceBundle
-> Claim-level Citation
-> Grounded Answer / Artifact
-> Trace / Cost / Eval
-> Feedback
-> Restart Recovery
```

## 四组架构总览

Zuno 的十一逻辑模块按照领域 Ownership 独立维护。为了理解整个系统，可以把它们归纳为四组：

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

这四组是便于理解的逻辑视图，不是新的事实 Owner，也不是物理部署层级。正式 Target 仍以十一份模块文档为准；Current、Gap、Measurement 和 Production Readiness 以状态文档、代码、Migration、测试、Trace 与 Eval 证据为准。

### 1. 01 + 02：产品入口与知识供给

这一组解决两个入口问题：

```text
01 Product Surface
    人和任务怎样进入系统。

02 Input / Document Ingestion
    企业资料怎样变成可索引、可引用、可追踪的知识输入。
```

**01 Product Surface** 拥有 Workspace、Agent 配置、Conversation、用户消息、附件交互、运行状态展示、AvailableAction、审批和 Interrupt 交互。它把用户目标、输出要求、会话和 Workspace 上下文提交给 Agent Core，但不拥有 Plan、Evidence、Tool Effect 或最终 RunOutcome。

**02 Input / Document Ingestion** 负责：

```text
SourceObject
-> DocumentVersion
-> ParsePlan / ParseAttempt
-> CanonicalDocumentIR
-> SourceSpan
-> Quality Gate / Human Review
-> IndexableDocumentSnapshot
```

它保证文件版本、内容 Hash、解析状态和原文定位可靠，再把不可变的索引输入快照交给 Knowledge。没有 DocumentVersion 与 SourceSpan，后续检索、GraphRAG 和 Citation 就无法形成可靠证据链。

这一组的共同作用是：

```text
01 把用户目标可靠地送进系统。
02 把企业知识可靠地送进系统。
```

### 2. 03 + 05 + 06：智能核心

这三个模块共同形成 Zuno 的任务、证据、上下文和经验闭环：

```text
06 Agent Core
    管整个任务怎么完成。

03 Knowledge
    管当前结论需要什么证据，以及证据是否充分。

05 Memory & Context
    管当前模型应该看到什么，以及什么历史经验值得保留。
```

#### 06 Agent Core：任务控制中枢

Agent Core 是一次 AgentRun 的 Single Controller，拥有 TaskContract、GoalVersion、PlanVersion、StepRun、并行调度、Interrupt、Final Gate、Publication 和 RunOutcome。

```text
固定 AgentRunGraph
+
动态 Plan DAG
+
固定 StepExecutionGraph
```

五种机制各有明确作用域：

```text
Plan-and-Execute
    管任务目标、依赖、并行和完成条件。

ReAct
    管单个 Step 内 Action -> Observation -> 下一 Action 的有界循环。

Reflection
    判断 Action、Step、Join 或最终结果是否合格。

Replan
    原计划结构、依赖或核心假设失效时创建新的 PlanVersion。

Reflexion
    Run 结束后生成受治理的跨任务经验候选，不直接写长期 Memory。
```

简单任务也必须有 Deterministic Single-Step Plan；复杂任务使用 Dynamic DAG Plan。Retry、Parameter Repair、Capability Fallback、Reflection 和 Replan 必须分开，不能把所有失败都变成重新规划。

#### 03 Knowledge / Agentic GraphRAG：证据决策中枢

Knowledge 不发布最终答案，而是管理：

```text
KnowledgeVersion / KnowledgeSnapshot
EvidenceRequirement
RetrievalPlan / RetrievalRound
BM25 / Vector / Graph / Structured Retrieval
EvidenceLedger / EvidenceFrontier
Fusion / Rerank / CitationLineage
Corrective Retrieval
Evidence Verdict / KnowledgeControlProposal
```

现有架构以固定 `KnowledgeRetrievalGraph` 管治理，以动态 RetrievalPlan 和 RetrievalRound 适应问题。新的 Evidence-Driven Agentic GraphRAG Target 进一步围绕 Claim 进行 Evidence Deliberation、冲突判断、同源去重和 Targeted Evidence Probe。

```text
相关 Chunk
    不自动等于
能够支持关键 Claim 的 Evidence
```

Knowledge 可以返回充分、部分、冲突、无适合证据、授权范围内证据不可用或知识质量可疑等结果；Ask User、External Evidence、Replan、Partial、Abstain 和 Finalize 仍由 Agent Core 决定。

#### 05 Memory & Context：上下文与经验中枢

Memory & Context 同时回答两个问题：

```text
过去什么值得记住？
当前这次模型调用应该看到什么？
```

它使用三个正交维度：

```text
生命周期：Working -> Session -> Long-term
长期类型：Episodic / Semantic / Procedural
压缩强度：C0 / C1 / C2 / C3
```

长期 Memory 必须经过 Candidate、Evidence、Scope、Security、Dedup、Conflict 和 Governance；模型不能直接提交 Active Memory。`ContextPackVersion` 是一次模型调用的不可变预算化读取视图，不是新的 Memory 层，也不替代 Knowledge、Conversation 或 LangGraph Checkpoint。

三个核心模块的协作关系：

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

智能核心决定“下一步应该做什么”，能力执行层把这个决定映射为模型调用、可用能力和受治理的真实动作。

```text
04 Model Gateway
    提供统一模型调用、Role、Routing、Usage 和 Provider Failure 语义。

07 Capability / Skill
    描述系统能做什么、任务应如何做、哪些实现可作为规划候选。

08 Tool Runtime
    执行一次具体 Tool 动作，并确认执行与外部效果事实。
```

#### 04 Model Gateway：模型执行入口

Planner、Executor、Query Rewriter、Extractor、Critic、Synthesizer、Embedding、Rerank、Vision 和 Judge 等模型调用统一进入 Model Gateway。Gateway 管理 Model Role、Operation、Prompt Artifact、Provider、Routing、Quota、Usage、Fallback、Streaming 和 Structured Output。

模型只产生 Proposal、Candidate、Score 或 Model Result，不拥有 Plan、Evidence、Authorization、MemoryVersion 或 RunOutcome。模型 Provider 调用归 04，不因为底层使用 HTTP 或 SDK 就进入 Tool Runtime。

#### 07 Capability / Skill：能力语义控制面和方法包目录

Capability / Skill 回答：

```text
系统能做什么？
完成这类任务通常应该怎样做？
当前哪些实现满足所需语义、版本和环境约束？
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

Capability 使用稳定业务语义身份，例如 `collaboration.message.send`；Skill 是使用若干 Capability 完成任务的方法包、SOP、约束和验收方式。07 可以发现、过滤和选择候选能力，但不执行 Tool、不持有 Secret、不批准权限、不提交外部效果，也不激活 Plan。

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
-> Agent Core Acceptance
```

Timeout、响应丢失或进程崩溃后，Tool Runtime 必须先确认外部效果是否已经发生；副作用 Outcome 为 UNKNOWN 时，禁止跨 Provider 盲目 Retry。

#### Capability / Skill 与 Tool Runtime 的边界

这是两个不同的控制面，不能合并成一个“工具模块”。

| 维度 | 07 Capability / Skill | 08 Tool Runtime |
| --- | --- | --- |
| 核心问题 | 能做什么、应该怎样做、哪个候选满足要求 | 这一次具体动作怎样安全执行并确认效果 |
| 主要对象 | Capability、Skill、Requirement、Binding、Availability、Selection | ToolDefinition、PreparedToolAction、Attempt、Observation、Execution/Effect Receipt |
| 输出给 Agent Core | 可用于规划的版本化能力候选和选择理由 | 实际执行、观察、效果与对账事实 |
| 是否真实执行 | 否 | 是 |
| 是否持有 Secret | 否 | 只消费 Security/Infrastructure 提供的受限 Secret Lease |
| 是否批准权限 | 否 | 否，只消费 Security Decision |
| 是否拥有 Plan | 否 | 否，Agent Core 拥有 |
| 是否拥有外部效果 | 否 | 是，拥有 EffectReceipt / EffectReconciliation |

完整交接链路是：

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

必须保持以下不等价关系：

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

Tool Runtime 也不是万能 Integration Bus。Knowledge 检索归 03，模型调用归 04，Memory/Context 归 05，计划和控制归 06；模块内部普通函数、Repository 或专业领域 Runtime 不会因为使用 HTTP、SDK 或 Queue 就自动变成 Tool。

### 4. 09 + 10 + 11：治理与运行底座

这一组不是只放在系统最下面，而是横向贯穿请求、检索、模型、记忆、工具和最终发布的整个生命周期。

```text
09 Security
    确定谁可以访问什么、执行什么、披露什么。

10 Observability & Eval
    记录发生了什么，并证明系统是否真的更好。

11 Infrastructure
    提供可靠持久化、消息、对象、Checkpoint、Lease、恢复和部署 Primitive。
```

#### 09 Security

Security 拥有 Identity、Authorization、ACL、Security Epoch、Approval Policy、Credential/Secret Binding、Data Classification、Disclosure、Revocation 和 Audit Requirement。

安全门禁发生在检索、Context 构造、模型调用、工具准备与执行、Memory 提交和最终发布之前。模型、Capability、Tool Runtime 和 Product Surface 都不能自行扩大权限或伪造 Approval。

#### 10 Observability & Eval

Observability 记录 PlanVersion、Step、Model Invocation、KnowledgeSnapshot、Retrieval Round、Reflection、Replan、Tool Effect、Budget、Publication 和 Failure 等结构化 Trace。Eval 使用固定 Dataset、Case、Profile、Metric 和 Release Gate 比较不同 RAG/Agent 策略。

文档、Demo 或单次成功不能证明质量提升。Answer Correctness、Groundedness、Citation、Unsupported Claim、Conflict Disclosure、Agent Efficiency、Cost 和 Latency 必须通过可复现 Eval 证明。

#### 11 Infrastructure

Infrastructure 提供 PostgreSQL、Object Store、Queue、LangGraph Checkpointer、Transaction/UoW、Outbox/Inbox、Lease、Fencing、Idempotency Claim、Backup/Restore 和 Deployment 等 Primitive。

```text
PostgreSQL
    保存可审计的领域事实。

LangGraph Checkpointer
    保存图控制位置、Pending Send、Interrupt Cursor 和小型状态引用。

Object Store
    保存大型不可变文件、Payload、Artifact 和 Eval 证据。

Queue / Lease / Fencing
    支撑异步执行、并发控制和旧 Worker 隔离。
```

基础设施 Receipt 不等于上层业务成功：

```text
Index write success != KnowledgeVersion accepted
Queue ACK != Tool Effect success
Checkpoint commit != AgentRun domain commit
Object upload success != Artifact published
```

### 端到端关系

```text
用户通过 01 提交任务
-> 02 提供可靠文档和 SourceSpan
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

一句话概括：

> 01 + 02 把人和知识可靠地送进系统；03 + 05 + 06 决定目标、证据、上下文和行动；04 + 07 + 08 把决策变成模型能力、能力选择和现实动作；09 + 10 + 11 保证所有事情被允许、看得见、跑得稳、能恢复。

后端主路径位于 `src/backend/zuno`，按各领域 Owner 分层维护。模块之间只通过版本化 Contract、不可变引用、领域事件和受控 Port 协作，不共享数据库 Session、Provider SDK 或内部 Repository。

## 文档入口

- [总架构](./docs/architecture/architecture.md)
- [架构十类图 HTML 展示](./docs/architecture/architecture.html)
- [十一逻辑模块设计](./docs/modules/README.md)
- [Production Readiness 状态](./docs/status/production-readiness.md)
- [01 Product Surface](./docs/modules/01-product-surface.md)
- [02 Input / Document Ingestion](./docs/modules/02-input-document-ingestion.md)
- [03 Knowledge / Agentic GraphRAG](./docs/modules/03-knowledge-agentic-graphrag.md)
- [04 Model Gateway](./docs/modules/04-model-gateway.md)
- [05 Memory & Context](./docs/modules/05-memory-context.md)
- [06 Agent Core / Planning & Control](./docs/modules/06-agent-core-planning-control.md)
- [07 Capability / Skill](./docs/modules/07-capability-skill.md)
- [08 Tool Runtime](./docs/modules/08-tool-runtime.md)
- [09 Security](./docs/modules/09-security.md)
- [10 Observability & Eval](./docs/modules/10-observability-eval.md)
- [11 Infrastructure](./docs/modules/11-infrastructure.md)
- [Evidence-Driven Agentic GraphRAG ADR](./docs/decisions/0006-evidence-driven-agentic-graphrag.md)
- [架构决策](./docs/decisions/README.md)
- [Repository Ownership Matrix](./docs/governance/repo-ownership-matrix.md)
- [文档总入口](./docs/README.md)
- [公开证据入口](./docs/evidence/public-demo.md)
- [历史归档入口](./docs/history/programs/README.md)

`docs/architecture/` 只保留：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## Program 入口

- 当前 program 前台：`.agent/programs/`
- 当前 active program：`zuno-canonical-architecture-runtime-realization-v1`
- 当前 phase：`PHASE22`
- 最近完成归档：`docs/history/programs/zuno-real-unified-runtime-cutover-v1/`
- 历史生产完成归档：`docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
- 历史 runtime-first 归档：`docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
- 历史 master architecture 归档：`docs/history/programs/zuno-master-architecture-implementation-v1/`

## Agent 协作入口

Zuno 主仓库目录保持为最终集成仓库；临时 worker worktree 放在：

```text
F:\internship-work\resume project\worktrees\
```

每个 worker 使用独立 worktree 和 `codex/` branch。Claude Code worker 优先处理简单、大量、重复、下载、环境探测、日志整理和低风险候选补丁；Codex coordinator 负责复杂架构判断、根因定位、安全 / 并发 / 恢复 / 幂等语义、review、合并、最终验证和 push。

worker 的 worktree、branch、commit、evidence、PR 标题和 PR 描述必须带 `agent + model + worker` 身份标签。Claude Code session 用 `stream-json --verbose` 创建并记录真实 `session_id`；同一 PR / handoff 的后续修复优先用 `--resume <session_id>` 复用。时间和成本按单个 agent 的一次 PR / handoff 统计，不按一轮对话统计；API token 估算成本和 provider 平台额度扣减分开记录。

Codex coordinator 必须审查 worker diff、evidence、验证结果、风险和成本账，并按 100 分 scorecard 打分后决定 accept、request changes、reject 或 block。worker PR 只是候选贡献；最终合并、集成验证和 push 只由 coordinator 收口。详细规则见 `.agent/references/workflow.md`、`.agent/references/command-catalog.md` 和 `.agent/templates/phase-closure-report.md`。

## 本地验证入口

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

## 当前质量声明

Evidence-span Agentic GraphRAG 的本地实现基线已经存在，但 fixed EnterpriseRAG measured pass 仍未完成。

最近完成的 `zuno-unified-agent-runtime-closure-v1` 已把 unified runtime implementation baseline 归档为 `implementation_complete_measurement_blocked`。PHASE13 sample-8 运行产出 `blocked_not_measured`，原因是本地 embedding profile runner 未配置；sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。

```text
implementation available
measurement blocked
quality not yet proven
```

不得把 doc-level recall、prepared benchmark 或 incomplete run 写成 strict citation / answer correctness 已完成。Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。
