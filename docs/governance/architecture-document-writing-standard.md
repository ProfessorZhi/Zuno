# Zuno 架构文档写作标准

updated: 2026-08-11
status: active-document-governance
scope: `docs/architecture/`, `docs/modules/` 与其入口、图源、验证器

## 0. 这份标准解决什么问题

本标准约束架构文档如何组织和解释，不新增 Zuno 的领域 Contract，也不把未接受的 Target Candidate 变成正式架构事实。

它解决的是信息架构问题：读者应先理解问题和业务场景，再理解系统边界、运行流程、正确性语义和验证方式，最后才进入字段、状态和实现规格。

```text
问题
→ 场景
→ 边界与 Owner
→ 决策
→ 正常流程
→ 状态与失败
→ Contract 与实现规格
→ 安全、预算、审计
→ 观测、评测与证据
→ Current / Target / Future
→ 取舍与追问
```

## 1. 事实源和状态边界

正式架构事实的优先级为：

```text
全局原则、已接受 ADR、共享 Contract Registry
→ 对应 Owner 的 `docs/modules/<NN>-*.md`
→ `docs/architecture/architecture.md` 的跨模块集成
→ `architecture-views.md` + `architecture.html` 的展示配对
```

职责边界：

| 位置 | 唯一职责 |
| --- | --- |
| `docs/architecture/architecture.md` | 为什么需要平台、跨模块运行链、全局正确性和部署语义 |
| `docs/architecture/architecture-views.md` + `docs/architecture/architecture.html` | 不可拆分的 Mermaid 图展示配对；不拥有额外文字事实，HTML 不得手工创造架构语义 |
| `docs/modules/` | 十一个领域 Owner 的详细 Target、状态、Failure、Contract、实现规格和验证要求 |
| `docs/status/`、`docs/evidence/` | Current、Gap、Measurement 和运行证据 |
| `docs/decisions/` | 被接受或正在审查的架构决策 |
| `docs/governance/` | 写作、Ownership、共享 Contract 和工程治理 |
| `docs/verification/` | 架构消费者的验证语料，不是架构事实源 |
| `.agent/` | 路由、Program、模板、验证入口；不保存架构或模块正文镜像 |

`Current` 必须由代码、Migration、测试、Trace、Eval 或运行证据证明。类名、表名、Mock、Target Contract、QA 答案和图形存在都不能单独证明 Current。

## 2. 总架构的阅读协议

总架构按以下六个 Part 阅读。既有编号标题可以为了保留 QA 锚点继续存在，但内容必须能映射到这条主线。

### Part I — 为什么需要 Zuno

包括：

- 文档定位、事实源、Target / Current 边界；
- 统一企业 Case；
- 产品问题、目标、非目标和不可变约束；
- 每条核心原则必须说明它防止什么问题。

### Part II — 平台长什么样

包括：

- Edge / Experience Plane；
- Platform Control Plane；
- Agent Execution Plane；
- Knowledge Plane；
- Memory & Context Plane；
- Model Access Plane；
- Tool / Effect Plane；
- Security、Observability / Eval 等横切能力；
- 十一个逻辑模块与物理运行域。

Plane 是责任视图，不等于微服务，也不等于语言。未经 ADR 接受的 Java/Python、微服务拆分或 Kubernetes 方案必须标记为 Candidate，不得写成冻结事实。

### Part III — 一次任务如何运行

统一使用以下案例：

> 审查合同 A 的责任限制风险，结合企业 Legal Playbook 和适用法律形成报告，经批准后发送给法务负责人。

总架构按以下链路讲完整任务：

```text
Client
→ Gateway / Product
→ Security
→ AgentRun
→ ContextPack
→ Plan
→ Knowledge / Evidence
→ Model
→ Tool / Effect
→ Final Gate
→ Publication
→ Memory Candidate / Eval
```

局部模块再解释自己的决策细节，不在总架构复制全部字段。

### Part IV — 分布式系统如何保持正确

包括：

- 跨服务 Contract 与兼容窗口；
- Data Ownership、Logical database-per-service；
- Outbox / Inbox、幂等、Lease、Fencing；
- Long-running Run、Deadline、Retry、Circuit Breaker、Bulkhead；
- Checkpoint 与 Domain Fact 的恢复优先级；
- UNKNOWN Effect、Reconciliation 和 Compensation。

### Part V — 如何部署、扩容和演练

包括：

- API Tier / Worker Tier；
- 不同服务的 Scaling Signal、Quota、Backpressure 和 Fairness；
- Drain、Canary、Progressive Rollout；
- Fault Injection、Backup / Restore、DR 和 Runbook；
- Observability、Audit、Offline / Online Eval 与 Release Gate。

### Part VI — 如何验证和演进

包括：

- Cross-module Ownership Summary；
- ADR 与 Trade-off；
- Current / Target / Future / History 路由；
- Architecture QA Coverage；
- 设计完成、实现完成、质量证明和 Production Ready 的区分。

## 3. 模块文档的七 Part 协议

十一模块可以保留各自已有的稳定 Part 标题和 QA 锚点，但内容必须覆盖以下七类语义：

### Part I — Why / Boundary

问题、目标、典型业务 Case、Responsibilities / Non-responsibilities、Ownership、Trust Boundary、核心不变量。

### Part II — Conceptual Architecture

核心概念、模块内部组件、一个 Mermaid、统一 Case 的正常流程。

### Part III — Decision & Runtime Strategy

每个重要决策至少回答：

```text
Problem
Trigger
Inputs
Decision Owner
Proposal vs Deterministic Decision
Normal Path
State Change
Failure
Fallback / Recovery
Observability
Test
```

### Part IV — State / Failure / Recovery

状态转换必须写成 `State → Trigger → Guard → Next State`；Failure 必须说明是否可 Retry、谁处理、如何传播、最终状态和人工介入条件。

### Part V — Security / Governance / Budget

包括 Scope、Authorization、Approval、Quota、Budget、Privacy、Information Flow 和 Audit；不把模型输出写成安全决定。

### Part VI — Contract & Implementation Specification

按以下顺序写：

```text
Domain Contract
→ API / Event / ObjectRef
→ Storage / Index / Queue
→ Transaction / Migration
→ Code Package / Adapter Boundary
```

### Part VII — Verification / Status / Trade-offs

包括 Trace、Metric、Unit / Contract / Integration / Fault / E2E / Eval、Completion Evidence、Current / Target / Gap / Future、替代方案和 Interview QA 引用。

## 4. 写作规则

- 重要概念第一次出现时，先写问题和原因，再给术语、字段或状态名。
- 每个重要章节以一句结论句开始，再用 2–4 段解释、必要图表和异常 Case 支撑。
- 标题优先写问题或决策，例如“为什么 RRF 后仍需要 Rerank”，而不是只写“Rerank”。
- H1 只用于文档标题、Part 和一级架构章节；H2 负责设计问题；H3 负责问题内部策略。
- 表格用于比较、Ownership、Strategy Matrix、Failure Matrix、State Transition 和 Service Mapping；不使用超大表格承载整章叙事。
- Schema 只展示表达语义所需字段；完整字段由 Owner 模块的实现规格持有。
- Mermaid 一张图只回答一个问题；必须保留 Gate、Commit、Barrier、Proposal、Effect、Interrupt、Reconciliation 等改变语义的节点。
- `architecture.md` 是唯一总架构文字事实；展示配对只负责帮助阅读，不得反向成为事实源。
- `Current`、`Target`、`Future`、`History` 必须显式标注，禁止用目标语气暗示已经实现。

## 5. 图源、入口和引用规则

`docs/architecture/` 只能存在以下四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

图形关系变化时，将 `architecture-views.md` 与 `architecture.html` 作为一个整体同步，运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

模块细节必须链接到唯一 Owner 文档，不在总架构或 `.agent/` 创建镜像。QA 只能引用 canonical file 和 section；章节重排应优先保留稳定标题锚点。若语义消失，先标记 PARTIAL / MISSING，修复事实源后再更新为 FULL，不能为了让 QA 通过而改覆盖状态。

## 6. 评审与验证规则

写作标准验证器只检查确定性规则，不评价文风：

- 架构目录仍是四文件；
- 不存在 `.agent/architecture/`、`.agent/modules/`；
- 总架构包含六 Part 语义入口和统一 Case；
- 十一个模块均可路由到唯一正式文档；
- 模块文档可以定位 Problem、Ownership、Runtime Flow、State / Failure、Security、Observability、Current / Target；
- 展示配对、内部链接和 QA references 可解析；
- 未接受 Candidate 不被标为 accepted / normative Current。

建议验证顺序：

```powershell
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
```

本标准只说明如何写文档；它不能证明 Runtime 已实现、质量已证明或系统已 Production Ready。
