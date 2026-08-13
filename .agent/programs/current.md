# Current Program

state: `active-design-program`
active_program: `PROJECT-ARCHITECTURE-RECONSTRUCTION-V1`
queued_program: `none`
program_class: `architecture-review-and-reconstruction`
baseline_sha: `4b960408f0693a42edd9a1a89accb98ac49d1edc`

本 Program 已由用户明确启动，但它不是 implementation program。它只负责从
Canonical Facts V1、当前仓库证据和已有 Target 输入重新推导 Product Problem、Domain、
Agent Runtime、Knowledge、Service Boundary、Data Ownership、Security 和 Eval，并接受
Red Team、Blue Team、Counter Attack 与 Interview Red Team 审查。

## Scope

```text
允许：事实深度恢复、问题模型、架构候选、红蓝攻击、面试深挖、Gap 和 ADR 候选
禁止：业务 Runtime、UI、数据库 Schema/Migration、依赖升级、生产 Infra 实现
禁止：把历史 UNKNOWN 或 Target 候选升级为 Current
```

Microservice 和 Python-only 是当前 Owner Target Constraint；本 Program 仍攻击服务数量、
服务边界、Worker 形态、Runtime Provider、Multi-Agent、Graph、Memory 和自研能力是否
值得保留。五个服务不是预先批准的最终答案。

## Inputs

- `docs/project/facts/` 的十类 Canonical Facts；本轮不新增第 11、12 个事实分类；
- `docs/project/facts/` 的 Fact State 与 E0–E5 Evidence Strength；
- `project-reconstruction-lab/01-facts/` 的事实恢复、证据台账和未决问题；
- `project-reconstruction-lab/04-product/` 的问题模型与产品命题候选；
- `docs/project/architecture/`、专题文档和 ADR 0008–0011；
- 当前代码、测试、配置、Compose、Migration 和可复现验证结果；
- 已完成 Red/Blue 会话，仅作为输入和可追溯历史，不自动继承其结论。

## Two-track execution

### Track A — Fact Depth Recovery

围绕现有十类 Facts 深挖六个高价值断点：真实法院工作流与痛点、个人代码级 Ownership、
Court QA/Evaluation 协议、真实 Incident、团队协作链、Reuse/Build/Research Transfer。
事实 Gate 采用：

```text
为什么做 → 谁在用 → 团队怎么做 → 我做了什么 → 请求怎么跑
→ 遇到什么问题 → 怎么改 → 怎么测 → 客户怎样反馈 → 为什么改架构
```

缺少证据时保留 `UNKNOWN`、`USER_PARTIAL_RECALL` 或 `RECONSTRUCTED_CANDIDATE`。

### Track B — Architecture Reconstruction

从已确认或明确标注范围的事实出发，依次审查：

```text
Historical Problem
→ Product Capability
→ Domain Contract
→ Runtime Contract
→ Knowledge / Evidence
→ Logical Capability
→ Physical Service / Worker
→ Data Ownership / Recovery
→ Security / Eval / Deployment
```

每一项复杂度都必须回答：为什么存在、为什么不是 Library/Worker/Host/已有 OSS、谁拥有
状态、失败如何重试和恢复、如何幂等、如何授权和观测、怎样测试、怎样替换或删除。

## Review gates

```text
Evidence Intake
→ Fact Readiness Gate
→ Product Problem Gate
→ Red Attack
→ Blue Response
→ Counter Attack
→ Interview Red Team
→ KEEP / SIMPLIFY / EXTERNALIZE / DEFER / DELETE
→ ADR Candidate
→ User Architecture Gate
→ Canonical Docs Sync
```

在 `User Architecture Gate` 之前，只能写 Lab 候选、Spike、Benchmark 或 Gap；可以记录
带边界的 `Codex Implementation Task Candidate`，但不能激活 Runtime implementation task
或 implementation Program。`Microservice Target` 不等于五个服务已实现，`Domain-aware
Runtime` 也不等于已证明优于 Host + Legal Backend。

## Expected outputs

1. 历史问题模型和 Fact Readiness 结论；
2. Domain / Runtime / Knowledge / Service / Data / Security / Eval 的候选与攻击记录；
3. WorkBuddy Host、Legal Backend、Native Runtime 等简化方案的 Kill Test 结果；
4. Big Tech Interview Challenge Log 与事实/架构回流项；
5. `Architecture-to-Code Gap`，只记录迁移与证据需求，不直接改代码；
6. 经过反击的 ADR 候选与 Canonical Docs 更新清单；
7. 如果证据不足，明确留下 Open Evidence Gaps，而不是强行收敛。

## Current phase

```text
Fact Taxonomy V1                 DONE
Fact Depth Recovery              IN_PROGRESS
Product Problem Reconstruction   IN_PROGRESS
Architecture Red/Blue            READY / IN_PROGRESS
Architecture Red/Blue Round-002   COMPLETE (V3, 100Q, 80 NOVEL / 20 REGRESSION)
Architecture Red/Blue Round-003   COMPLETE (V3.1, 100Q, 85 NOVEL / 15 REGRESSION)
Interview Red Team               READY
Canonical Architecture Sync      APPLIED / ACCEPTED_TARGET (V3.1.3 Round-005 review)
Document Quality V3.1             COMPLETE (historical Part A >= 80 / Part B >= 85)
Document Normalization V3.1.1      COMPLETE (Part A >= 85 / Part B >= 85)
Human Writing V3.1.2              COMPLETE (warning report + human review package)
Architecture Red/Blue Round-004   COMPLETE (100Q consistency/failure review; immutable)
Architecture Red/Blue Round-005   COMPLETE (100Q deep failure/recovery review; V3.1.3)
Implementation Program           READY_FOR_TASK_DEFINITION (not active)
```

## V2 Round status

```text
Protocol                         ZUNO-RED-BLUE-WORKFLOW-V2
Round                            ROUND-001 / 100 independent questions
Question distribution            A10 B10 C15 D15 E10 F10 G10 H8 I7 J5
Answer raw score                 361/500 (72.2)
Architecture fitness raw score  457/500 (91.4)
Critical Gate                    OPEN
P0 / P1                          58 / 42
Canonical Docs Sync              APPLIED (after Gate Realignment)
User Architecture Gate          APPROVED (Part-A Target only)
Round decision                   DESIGN_ACCEPTED_TARGET; P0 CLOSURE OPEN
```

Round-001 的完整记录、Gap、Blue Change Set 和 Counter Retest 位于
`project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/`。这些结果只能指导下一轮 Fact
Recovery、Benchmark 和 Architecture Review，不能把 Target 候选升级为 Current，也不能生成
Runtime implementation task。

## Blue Repair status

```text
Repair                         RB-BLUE-REPAIR-001
Root-cause clusters             10
Final severity                 P0=12 P1=46 P2=32 P3=10
Final P0 closed                0/12
Evidence Coverage              0% closure-grade
Complexity Justification       10/10 structural, 0/10 measured
Counter Retest                 9 REOPEN + 1 WAITING_FOR_EVIDENCE
Round-001 closure              NOT_CLOSED
V3 Round-002                   COMPLETE
Canonical Docs Sync             APPLIED
User Architecture Gate         APPROVED
```

Repair 只写入 Lab，不修改业务 Runtime、UI、Schema/Migration 或正式 Canonical Architecture。

## V3 Round-002 status

```text
Protocol                         ZUNO-RED-BLUE-WORKFLOW-V3
Round                            RB-WORKFLOW-V3-ROUND-002
Questions / Answers / Scores     100 / 100 / 100
Novel / Regression               80 / 20
Raw / Normalized Score           371/500 / 74.20
Grade                            Architecture Requires Significant Repair
P0 / P1 / P2 / P3                8 / 23 / 69 / 0
A / I / E / X                    0 / 5 / 3 / 0
New A-P0                         0
Canonical Sync                   APPLIED (Target refinements only)
Round-003                       COMPLETE (V3.1 documentation quality)
```

V3 Round-002 没有关闭原始 P0，也没有改变 Current、Facts、Runtime、Schema/Migration、生产或
依赖状态。其完整记录位于 `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/`；
Round 文件关闭后按 immutable archive 处理。

## V3.1 Round-003 status

```text
Protocol                         ZUNO-RED-BLUE-WORKFLOW-V3.1
Round                            RB-WORKFLOW-V3-ROUND-003
Questions / Answers / Scores     100 / 100 / 100
Novel / Regression               85 / 15
Raw / Normalized Score           392/500 / 78.40
Part A / Part B Quality Gate     PASS / PASS
Document Quality                 DOC_QUALITY_COMPLETE
New A-P0                         0
Canonical Sync                   APPLIED (documentation Target refinement only)
Round-004                       COMPLETE (V3.1.2)
```

Round-003 只修复 Canonical 文档的同文件 Part A/Part B 可读性与 Contract 表达，删除过程性
Round trace；没有改变 Facts、Runtime、Schema/Migration、依赖、生产状态或既有 ADR 原则。完整
记录位于 `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-003/`。

## V3.1.1 normalization status

```text
Session                         RB-DOCUMENT-NORMALIZATION-V3.1.1
Canonical Docs                  12 audited / 12 full-part rewritten
Part A target / strong          85 / 90
Part B target                   85
Sync mode                       FULL_PART_REWRITE; APPEND forbidden
Facts / Runtime / ADR           NONE / NONE / NONE
Round-004                       COMPLETE (V3.1.2)
```

## Evidence Closure status

```text
Campaign                       RB-EVIDENCE-CLOSURE-001
Baseline SHA                   e0e67ede267025f5203ff8b06bc6c185b8a96000
Final P0                       12
Executed focused evidence      10/12 (V3 narrow claims)
Closure-grade evidence         0/12 = 0%
P0 closed                      0/12
Red Evidence Review            completed; no closure accepted
Counter Retest                 NOT_RUN
Canonical Docs Sync            NOT_APPLIED
V3 Round-002                   COMPLETE; this evidence campaign remains OPEN
```

Evidence Closure 不是第二轮百问，也不是 Runtime implementation。它只登记实际证据、证据范围、
反驳意见和下一步验证；所有最终 P0 仍保持 OPEN。

## P0 V4 Execution status

```text
Campaign                       RB-P0-V4-EXECUTION-001
Original P0                    12
Scope Split                   1 (Q039-C / Q039-B)
V4 executed records            6/12
V3 current/narrow records      5/12
V4 accepted by Red             0/12
Counter Retest                 NOT_RUN
P0 closed                      0/12
Implementation-dependent       4
External-blocked               1 (Q066)
V5 benchmark gaps              1 (Q039-B)
Critical Closure               0%
V3 Round-002                   COMPLETE; this execution campaign remains OPEN
Canonical Docs Sync            NOT_APPLIED
```

本轮使用 verification-only harness 和 loopback Provider emulator；它们不能证明 Current Domain
Persistence、第三方 Provider、真实 Sandbox、法院质量或 Production。Q039 的 Scope Split 不
删除原始 P0，Q039-B 继续保持 V5 Benchmark Gap。

## Gate Realignment status

```text
Campaign                       RB-GATE-REALIGNMENT-001
Original P0                    12
Derived closure records        13 (Q039-C / Q039-B)
A-P0 / I-P0 / E-P0 / X-P0     0 / 11 / 1 / 1
Original P0 closed             0 / 12
User Architecture Gate         APPROVED
Canonical Sync                  APPLIED / ACCEPTED_TARGET
Implementation Program          READY_FOR_TASK_DEFINITION (not active)
```

Closure Class 只决定阻塞面，不改变历史 Severity 或 P0 Closure。用户 Gate 已批准后，
Implementation Task Candidate 仍不能自动激活或写成 Current；必须另行定义并启动实现 Program。

## Exit condition

本 Program 的 Part-A 设计阶段已通过用户 Gate 并完成 Canonical Sync；事实深度、面试挑战和
后续反事实审查仍可继续。实现 Program 必须另行生成；本文件不得把设计完成写成代码完成或
Production Ready。

旧 Program1 已 `SUPERSEDED / RETIRED`，不得恢复或重新激活。
