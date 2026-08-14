# Zuno 架构文档写作标准

updated: 2026-08-13
status: active-document-governance
scope: `docs/architecture/`、`docs/facts/` 与 `docs/modules/`

## 0. 这份标准解决什么问题

本标准只规定文档如何表达，不新增领域 Contract，也不把 Target、Hypothesis 或 Future 写成 Current。架构文档从问题和业务场景出发，再说明边界、Owner、状态、失败和验证。

```text
问题与场景
→ Product / Domain 边界
→ Logical Capability
→ Physical Service / Worker
→ Data Ownership
→ Security / Failure / Recovery
→ Current / Target / Hypothesis / Future / History
→ Verification and Reversal Criteria
```

## 1. Canonical taxonomy 与事实源

正式项目知识按三个问题层路由：

| 目录 | Canonical Question |
| --- | --- |
| `docs/facts/` | 今天仍然有效的项目上下文和 Current / Production Readiness 有什么证据？ |
| `docs/architecture/` | Product、Domain、Logical Capability、Physical Service/Deployment 如何形成跨层闭环？ |

`docs/architecture/architecture.md` 只回答跨层集成；`architecture-views.md` 与 `architecture.html` 是展示配对。旧 Product/Domain/Agents/Knowledge/Services/Data/Security/Eval/Deployment 专题和 11 模块原稿不再是当前 Canonical 入口；Red/Blue 过程只从 `docs/history/red-blue/` 按需读取。历史上下文和开发过程位于 `docs/facts/`，不因它们描述过去就自动成为 Current。

## 2. 每份 Canonical Owner 文档的强制双层协议

每个专题必须在头部声明：

```yaml
status: normative-target | current-fact | hypothesis | history
architecture_state: ACCEPTED_TARGET | PROPOSED | UNDER_ATTACK | REJECTED | DEFERRED
canonical_question: ...
owner: ...
replaces: ...
```

`architecture_state` 与 `status` 正交：`ACCEPTED_TARGET` 只表示用户已经接受该设计作为
下一阶段 Canonical Target，不表示代码已实现、验证、测量或具备生产资格。实现、证据和外部
资格仍分别由 `Current / Target / Gap`、ADR、Program 和 `docs/evidence/README.md` 记录。

每份 Canonical Owner 文档必须严格、且只能在同一文件中包含以下两个顶层正文部分，顺序固定：

1. `Part A — Architecture Narrative`：回答 WHY、WHAT 和 BIG PICTURE；说明 Problem/Motivation、
   Concrete Target Scenario、Architectural Drivers、Responsibilities、Non-responsibilities、
   Upstream/Downstream、Core Concepts、Conceptual Boundary、Happy Path、Canonical Ownership、
   Major Failure Story、Architecture Reasoning、Simpler/OSS Alternative、Tradeoff、Reversal/Kill
   Condition 和 Current/Target/Gap。
2. `Part B — Detailed Architecture Specification`：回答 HOW EXACTLY；说明 Contract、Input/Output、
   State/Version、Concurrency/CAS、Failure Propagation、Retry/Recovery、Idempotency、Security、
   Approval、Audit、Observability、Data Ownership、Storage、Scaling、Compatibility、Testing、
   Fault Injection、Benchmark、Evidence Requirement 和 Implementation Gap。

Required Concerns 不是 Required Headings。不同专题可以用不同的叙事顺序和小标题；禁止复制同一
模板、Checklist 或 Round Summary。Part A 与 Part B 必须合并旧正文中的对应内容，不能在 Part B
之后继续出现第三套 Legacy Main Body、Part-A subsection、旧 Contract 或重复 State Machine。
不能创建 `*-human.md`、`*-spec.md` 或 `.agent` 镜像。

### Human Writing Contract V3.1.2

Part A 是写给参与系统设计的高级工程师看的解释性正文。它应从一个具体业务或失败场景开始，
逐步说明问题、边界、责任、取舍和反转条件，再引出必要的技术术语。`Owner`、`Contract`、
`State`、`Provider`、`Receipt` 等词不能代替推导；重要术语首次出现时要用中文解释其作用，
后文保持叫法稳定。Part A 可以使用“我们不希望……”或“直觉上可以……但……”这样的工程判断，
但不能添加未被 Facts 支持的历史故事，也不能把 Target Scenario 写成 Current。

Part A 至少要让读者看见一条完整路径和一条具体失败路径：发生了什么、谁拥有决定权、状态如何
变化、为什么不能直接重试、如何恢复，以及该设计带来的成本。替代方案应在取舍讨论中自然出现，
不要求每篇文档使用相同小标题。Part A 以 prose 为主；Part B 继续保持精确的 Contract、表格、
状态和测试定义。Required Concerns are not Required Paragraphs；Architecture consistency takes
precedence over template consistency。

`HUMAN_WRITING_REVIEW` 与 Part A 数值评分分开。Verifier 只报告模板短语、标题密度、列表/表格
占比、英文术语密度和场景/失败/取舍标记等确定性 warning，不自动宣称 Human Writing PASS。最终
结论必须由 Blue self-review、Red documentation review 和 ChatGPT review 共同给出。

### Human Writing Continuity V3.1.3

当一轮审查修改 Part A 时，审查者必须从第一段重新读到最后一段，而不能只看变更行。重点检查场景、
问题、决策、代价和反转条件是否仍然连成一条叙事；连续的补丁式短段、重复 Current/Target 声明、
突然出现的英文 Contract 名词和 Round-specific wording 都必须合并或移回 Lab Session。禁止为了满足
检查项在正文结尾追加“此外”“Runtime 仍然”“这项约束”式孤立段落。

Part A 先讲业务事件和失败后果，再引出术语；Part B 保持精确的状态、版本、并发、失败、恢复、授权、
对账和测试 Contract。`closure_class_rationale` 只属于 Red/Blue Session，不得进入 Canonical 正文。
确定性检查只能报告 narrative warning，不能把机器信号升级为人工 `PASS`。

## 3. Logical 与 Physical 的写作边界

```text
Product / Domain
    ≠ Logical Capability
Logical Capability
    ≠ Physical Service
Physical Service
    ≠ Process / Container / Team
```

每个服务候选必须回答 `Why service? Why not library? Why not worker? Who owns the state? How does it recover?`。用户规模不是单独拆服务的理由；只有 Independent Scaling、Failure Isolation、Security Isolation、Independent Deployment、Distinct Availability 或 Data Ownership 等证据才允许拆分。

FastAPI 是 Application/HTTP Interface；LangGraph 只属于 Agent Runtime orchestration。PostgreSQL Canonical Domain State 与 Runtime Checkpoint 必须分别归属并设计 Recovery Reconciliation。

## 4. 状态与证据规则

- `Current` 必须由代码、Migration、测试、Trace、Eval 或真实运行证据证明；类名、Mock、目录和 Target 文档不算实现证据。
- `Target` 是已经接受的设计目标，不是已经部署的事实。
- `Hypothesis` 必须给出 Benchmark、Spike、User Validation 或 Security Evidence 的关闭方式。
- `History` 只解释被替换的结构，不得与新 taxonomy 并列为 Canonical Truth。
- 不同文档不得各自定义同一 Fact、State Machine、Service Owner 或指标含义；需要引用唯一 Owner。

## 5. 图源、入口和验证

`docs/architecture/` 只能有四个文件。图形语义变化时同步更新 `architecture-views.md` 与 `architecture.html`，并运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
```

图只用于解释关系，不取代文字 Canonical Owner；HTML 不得创造图源不存在的新事实。历史 QA/验证材料不属于当前架构事实源，应从 Git 历史或项目重建实验室按需查阅。

## 6. Canonical Rewrite 与过程痕迹边界

Canonical Sync 默认使用 `SECTION_REWRITE`；影响核心概念、服务边界、Owner、Runtime、Security、
Memory、Graph 或 Eval 的 Delta 使用 `FULL_PART_REWRITE`。`APPEND` 不是允许的同步模式。同步过程
必须先定位 Owner 和 `document_impact`，重写受影响部分，删除 superseded wording，再检查 Narrative
与 Contract 一致性。Round、Dxxx、Qxxx、Score、Red Finding、Blue Decision 和 Target Refinement
等过程痕迹只能进入 Lab Session、Decision Trace、ADR 或 History，不得进入 Canonical 正文。

## 7. 评审完成条件

每轮 Red / Blue 必须经过：

```text
Red Attack → Blue Response → Counter Attack
→ Architecture Decision → ADR
→ Canonical Doc Update → Red Retest
```

没有满足证据门的复杂度进入 `DEFER` 或 `HYPOTHESIS`；验证器只能检查确定性结构，不能把文档存在误报成 Runtime、质量或 Production Ready。

### V4.1 Interview Explainability

Canonical Part A 还必须通过 Fresh-Context 的概念可解释性审查：读者不看业务实现代码，只看
Part A、必要 Facts、ADR、Governance 和自身通用架构知识，应能先用普通软件工程语言讲清问题、
边界、Owner、流程、失败、Retry/Replan/Recovery、替代、代价和反转条件，再使用必要术语。
`Concept First → Term Second → Contract Last` 不是术语词典规则，而是避免 Part A 被内部英文名词
统治的叙事顺序。

V4.1 Red 可以使用会话级 `interview-calibration-packet.md` 生成连续 Deep-Dive Chain，但该
packet 只包含提问行为，不包含答案、包装话术或候选人事实；Blue 不读取它。Red Judge 的
`INTERVIEW_EXPLAINABILITY`（`CLEAR | DENSE | TERM_DEPENDENT | MISSING`）和 Human Writing Review
均需人工判断，确定性 verifier 只能提供 warning，不能宣称人工 PASS。

### V4.2 Live Answer Evidence Boundary

V4.2 的 Live Answer 是 BASE Snapshot 的 Cold-Start Evidence，不是 Canonical Rewrite。文档审查时
必须能从 `live-interrogation.md` 看见 `RED Q → BLUE A → RED CHAIN DECISION` 的真实交替；不能用
预生成题单、事后批量答案或 Candidate 中的修订内容替代这条证据。Part-A Support 必须明确为
`SUFFICIENT`、`PARTIAL` 或 `GAP`，并区分 Answer 来自 Part A、Part A 加通用知识，还是通用架构
推理。只有 Live Attack 完成后，Blue 才能把聚类后的 Architecture Decision Set 写入 Candidate。
