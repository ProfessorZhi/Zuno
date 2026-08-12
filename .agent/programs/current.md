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

在 `User Architecture Gate` 之前，只能写 Lab 候选、Spike、Benchmark 或 Gap；不能生成
Runtime implementation task。`Microservice Target` 不等于五个服务已实现，`Domain-aware
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
Interview Red Team               READY
Canonical Architecture Sync      BLOCKED_BY_USER_ARCHITECTURE_GATE
Implementation Program           NOT_STARTED
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
Canonical Docs Sync              NOT_APPLIED
User Architecture Gate          PENDING
Round decision                   NOT_PASSED_PENDING_USER_GATE
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
Round-002                      BLOCKED
Canonical Docs Sync             NOT_APPLIED
User Architecture Gate         PENDING
```

Repair 只写入 Lab，不修改业务 Runtime、UI、Schema/Migration 或正式 Canonical Architecture。

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
Round-002                      BLOCKED
```

Evidence Closure 不是第二轮百问，也不是 Runtime implementation。它只登记实际证据、证据范围、
反驳意见和下一步验证；所有最终 P0 仍保持 OPEN。

## P0 V4 Execution status

```text
Campaign                       RB-P0-V4-EXECUTION-001
Original P0                    12
Scope Split                   1 (Q039-C / Q039-B)
V4 executed records            6/12
V3 current/narrow records      4/12
V4 accepted by Red             0/12
Counter Retest                 NOT_RUN
P0 closed                      0/12
Implementation-dependent       4
External-blocked               1 (Q066)
V5 benchmark gaps              1 (Q039-B)
Critical Closure               0%
Round-002                      BLOCKED
Canonical Docs Sync            NOT_APPLIED
```

本轮使用 verification-only harness 和 loopback Provider emulator；它们不能证明 Current Domain
Persistence、第三方 Provider、真实 Sandbox、法院质量或 Production。Q039 的 Scope Split 不
删除原始 P0，Q039-B 继续保持 V5 Benchmark Gap。

## Exit condition

本 Program 只有在每个保留的重大设计都有 Red、Blue、Counter Attack、替代方案、验证方式和
逆转条件，并且用户明确通过 Architecture Gate 后，才可以结束设计阶段。实现 Program
必须另行生成；本文件不得把设计完成写成代码完成或 Production Ready。

旧 Program1 已 `SUPERSEDED / RETIRED`，不得恢复或重新激活。
