# ZUNO-RED-BLUE-WORKFLOW-V4.2

## Adaptive Dual-Thread Architecture Interrogation

V4.2 是 V4.1 的后继工作流契约。V4.1、V4.0 及更早 Round 保持 immutable；V4.2 只改变未来
Round 的对攻方式，不重解释历史结果，不启动 Round-006，也不修改 Canonical Architecture。

```text
workflow: ZUNO-RED-BLUE-WORKFLOW-V4.2
review_mode: QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION
round_006: ABORTED_OPERATIONAL_PILOT / WORKFLOW_EXECUTION_BLOCKER / SCORE_INVALID
round_007: READY_FOR_BATCH_ADVERSARIAL_PILOT / NOT_STARTED
default_execution_profile: BATCH_ADVERSARIAL
experimental_execution_profile: LIVE_ADAPTIVE
architecture_track: independent
implementation_track: independent
canonical_part_a: BASE_SNAPSHOT_KNOWLEDGE_SOURCE
chatgpt_merge_gate: required
whole_round_question_freeze: FORBIDDEN
```

## 1. V4.1 原则继续有效

V4.2 继续使用 Fresh Red Thread、Fresh Blue Thread、Part-A Cold-Start、Interview-Calibrated
Red、Blue 禁止读取 interview calibration、默认不读业务代码、`CONCEPT_FIRST → TERM_SECOND →
CONTRACT_LAST`、Blue-only Candidate Canonical Writer、Main-only Integrator、ChatGPT External
Merge Gate 和 Architecture/Implementation 双轨。

但 V4.2 将 V4.1 的“预生成完整问题集”替换为逐题对攻。V4.1 的 `questions_frozen_sha`、
`RED_QUESTIONS_FROZEN` 和 `red-questions.md` 只对历史 V4.1 Round 有效，不得出现在 V4.2
Live Attack Contract。

## 2. Live Interrogation 的真实顺序

Main Thread 每次只推进一个 Turn：

```text
Red 生成 Q001
  → Main 冻结 Q001
  → Blue 读取 BASE Snapshot 并回答 A001
  → Main 冻结 A001
  → Red 读取 A001，更新攻击假设
  → Red 生成 Q002 或关闭当前 Chain
```

之后重复该过程，直到 Chain 关闭，再选择新的 Root Claim。每个 Question 必须先于对应 Answer
落盘；每个 Follow-up 必须能回链到上一条已冻结 Answer。Red 不能提前写出本 Chain 的完整问题
列表，Blue 也不能修改已冻结的问题或回答。

## 3. Append-only Ledger

V4.2 使用 `question-answer-ledger.jsonl` 作为逐事件、追加式事实账本。每行是不可变事件，包含：

```text
event_seq
event_id
event_type: QUESTION_FROZEN | ANSWER_FROZEN | CHAIN_DECISION
turn_id
chain_id
question_id
question
question_sha
blue_answer
answer_sha
part_a_support
answer_source
followup_reason
followup_trigger_detail
previous_turn_ref
timestamp
rolling_hash
```

`QUESTION_FROZEN` 不得携带非空 `blue_answer` 或 `answer_sha`；`ANSWER_FROZEN` 必须复述同一
Question 并通过 hash 校验；`CHAIN_DECISION` 必须发生在 Answer 后。每个事件的
`rolling_hash` 由前一事件 hash 与当前规范化 JSON 计算，Manifest 记录最终
`rolling_ledger_hash`。这证明账本内容被追加，而不是事后重排。

`live-interrogation.md` 是同一账本的人类可读投影，顺序必须呈现：

```text
RED Q001
BLUE A001
RED CHAIN DECISION
RED Q002
BLUE A002
```

它不能先列出 Q001–Q100 再统一列答案。

## 4. Chain Spec 与 Follow-up

每条 Chain 只允许预声明：

```text
chain_id
root_claim
primary_concept
attack_intent
possible_pressure_axes
```

Chain Spec 禁止包含 `question`、`questions`、`question_ids`、`generated_questions`、Answer 或
任何完整题单。Root Question 可以没有 `followup_reason`；其余 Question 必须记录以下枚举之一
及自然语言触发说明：

```text
ANSWER_AMBIGUITY
UNJUSTIFIED_ASSUMPTION
OWNER_CONFLICT
FAILURE_GAP
ALTERNATIVE_NOT_ADDRESSED
TRADEOFF_NOT_ADDRESSED
COUNTEREXAMPLE_TRIGGERED
OVERDESIGN_RISK
REVERSAL_MISSING
BOUNDARY_UNCLEAR
CONCEPT_NOT_CLEAR
SCALE_OR_COST_PRESSURE
SECURITY_PRESSURE
RECOVERY_PRESSURE
CHAIN_COMPLETION_PROBE
```

`previous_turn_ref` 必须指向触发 Follow-up 的上一条 Answer，而不是只指向 Chain 名称。

## 5. Chain Stop

每个 Answer 后 Red 必须落盘一个 `CHAIN_DECISION`：

```text
CONTINUE_CHAIN
CLOSE_CHAIN
ESCALATE_FINDING
```

`CONTINUE_CHAIN` 后只能继续当前 Chain；`CLOSE_CHAIN` 或 `ESCALATE_FINDING` 后，下一条问题
必须属于新的 Root Claim。关闭条件是概念、Owner、Failure/Recovery、替代、Tradeoff 和 Reversal
已经足够闭合，继续追问不会产生新的 Architecture Information。不得为了达到固定深度重复追问。

## 6. Question Budget 与 Novelty

```text
question_target: 100
question_max: 100
normal_min: 80
```

实际 Question 数按账本计算，不按预设题单计算。80–99 题可以正常关闭，但必须记录
`NO_NEW_ARCHITECTURE_INFORMATION` 或 `ALL_PRIORITY_CHAINS_CLOSED`；少于 80 题只能在
`USER_GATE` 或 `ARCHITECTURE_BLOCKER` 下关闭，并标记 `QUESTION_COVERAGE_INSUFFICIENT`。

每个 Question 记录 `NOVEL` 或 `REGRESSION`。V4.1 的目标继续保留为至少 75% Novel、最多 25%
Regression，但统计对象是实际生成的 Question。若目标未达成，不能伪造 READY，应报告
`QUESTION_QUALITY_BLOCKED`。

## 7. Blue Live Answer 边界

Live Attack 阶段 Blue 只能读取 BASE Canonical Snapshot、必要 Facts、Active ADR、Governance、
Fixed Principles 和自身通用架构知识。Blue 不得读取：

- Candidate Rewrite；
- Interview Calibration；
- Business Code；
- Previous Blue Session；
- 本轮此前 Answer 之外的未授权推理材料。

每个 Answer 记录：

```text
part_a_support: SUFFICIENT | PARTIAL | GAP
answer_source: PART_A | PART_A_PLUS_GENERAL_KNOWLEDGE | GENERAL_ARCHITECTURE_REASONING
```

若使用 `GENERAL_ARCHITECTURE_REASONING`，必须解释 Part A 缺失了哪一层概念。Live Attack 阶段
Blue 不得修改 Part A、Part B 或任何 Canonical；所有 Answer 都基于同一个 BASE Snapshot，才能
作为真实 Cold-Start Evidence。

## 8. Attack 完成后的 Blue Synthesis

只有状态进入 `LIVE_ATTACK_COMPLETE` 后，Blue 才能读取完整 Ledger、Part-A Support Gap、Red
Findings 和 BASE Canonical，进入 `BLUE_ARCHITECTURE_SYNTHESIS`。Blue 应聚类 Root Architecture
Gaps，形成 Architecture Decision Set，不得把 100 个 Answer 机械转成 100 个补丁。

随后 Blue 在 Candidate Branch 执行 `SECTION_REWRITE`、`FULL_PART_REWRITE`、`NO_CHANGE` 或
`ESCALATION`。Part A 吸收概念、理由、边界、场景、失败、替代、代价和反转；Part B 吸收精确
Contract、State、Version、Retry、Recovery 和 Security。Canonical Rewrite 必须发生在 Live
Attack 之后。

## 9. Judge 与 Counter-Retest

同一 Round 的 Red Thread 可以保留对攻上下文进入 Judge Phase；这是 V4.2 允许的同 Round 例外，
不等于跨 Round Context Pollution。Judge 只能读取 Judge Packet：BASE Part A、完整 Ledger、Blue
Decisions、Canonical Delta、Final Part A/Part B 和 Candidate SHA。

Judge 顺序固定为：

1. 只读 Final Part A，判断 `CLEAR | PARTIAL | MISSING`；
2. 读取 Part B，核对 Narrative 与 Contract；
3. 核对 Delta、Answer 和 Candidate；
4. 每个高风险 Chain 至少提出一个不同问法的 Counter-Retest Question。

Counter-Retest 不能只是原问题改标点；它必须改变场景、约束或失败条件，检验 Blue 是否理解
不变量、边界、Failure、替代、Tradeoff 和 Reversal。

## 10. V4.2 状态机

```text
PREPARING
→ RED_THREAD_READY
→ BLUE_THREAD_READY
→ LIVE_ATTACK
→ CHAIN_OPEN
→ QUESTION_FROZEN
→ BLUE_ANSWER_FROZEN
→ CHAIN_CLOSED
→ LIVE_ATTACK_COMPLETE
→ BLUE_ARCHITECTURE_SYNTHESIS
→ BLUE_CANONICAL_SYNC
→ BLUE_CANDIDATE_READY
→ RED_COUNTER_REVIEW
→ WAITING_FOR_CHATGPT_REVIEW
→ CHATGPT_REPAIR_REQUIRED
→ CLOSED
```

`BLOCKED_BY_USER_GATE` 可以从需要用户决策的阶段退出。V4.2 废弃 Whole-Round
`RED_QUESTIONS_FROZEN`；Question Freeze 只描述当前 Question，不是整个 Round。

## 11. Main、Candidate 与外部 Gate

Main 负责 Snapshot、Session 创建指引、逐 Turn handoff、Question/Answer Freeze、Rolling Hash、
Chain State、Judge Packet、Verifier、ChatGPT Review Package 和最终 Merge。Main 不回答架构问题。

Blue 只能在 `candidate_branch != main_branch` 工作，Red 只读，ChatGPT 是外部审核者。只有
`ACCEPT` 或 `ACCEPT_WITH_DEBT` 才允许 Main Merge。Bootstrap 与未合并 Round 使用
`artifact_base_sha`、`artifact_content_state`、`external_reviewed_sha`，不得要求 Commit 自己
写入自己的 Final SHA。

## 12. V4.2 Execution Profiles

V4.2 保留同一套 Fresh Context、Part-A Cold-Start、Role Boundary、Candidate Branch 和外部
Merge Gate 契约，但执行 Profile 不再混用：

| Profile | 状态 | 用途 | 问题生成方式 |
|---|---|---|---|
| `BATCH_ADVERSARIAL` | 默认 | 稳定的跨角色架构审查 | Red 可在独立 Attack Session 中生成完整 100Q；Blue、Counter、Synthesis、Judge 分别使用新的角色 Session |
| `LIVE_ADAPTIVE` | 实验性 | 验证 Answer-triggered Follow-up 与逐 Turn Handoff | 每次只冻结一个 Question；下一题必须由上一 Answer 触发；禁止预生成整轮题单 |

`BATCH_ADVERSARIAL` 不是把旧的静态题库重新命名。它要求完整 Question/Answer 覆盖、每个
Counter Question 引用真实 Blue Answer、Synthesis 晚于 Counter、Judge 使用新 Session，并由
`verify_red_blue_workflow_v42.py --profile batch_adversarial` 验证。默认 Batch 的角色链为：

```text
Fresh Red Attack
→ Fresh Blue Defense
→ Fresh Red Counter
→ Fresh Blue Counter Defense
→ Fresh Blue Synthesis
→ Fresh Red Judge
→ ChatGPT External Merge Gate
```

`LIVE_ADAPTIVE` 只作为实验性 Profile 保留。Round-006 已完成三个真实短距离 Turn，但在
`WF-API-001` 后以 `ABORTED_OPERATIONAL_PILOT` 收口；这证明了短距离 Follow-up，不证明长距离
Session Handoff 稳定。因此 Round-007 的默认状态是
`READY_FOR_BATCH_ADVERSARIAL_PILOT / NOT_STARTED`，本协议不会自动启动它。

## 13. V4.2 Operational Pilot Boundary

V4.2 Bootstrap 只证明 `WORKFLOW_CONTRACT_AVAILABLE`，外部 Verdict 为
`ACCEPT_WITH_DEBT`，不证明 Thread 真实创建、Context 真正隔离、Calibration 真正 Red-only 或
Main Merge Gate 已运行。Round-006 的 Operational Pilot 已以 Workflow Execution Blocker 中止，
其 Architecture Score 无效。未来 Round-007 才能在默认 Batch Profile 下提供新的运行证据，本
Bootstrap 和 Round-006 都不会自动启动它。

当前工作流状态为：

```text
V4.2_WORKFLOW_ACCEPTED_WITH_DEBT
ROUND-006 ABORTED_OPERATIONAL_PILOT / SCORE_INVALID
ROUND-007 READY_FOR_BATCH_ADVERSARIAL_PILOT / NOT_STARTED
```

## 验证入口

```powershell
python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v42.py --round project-reconstruction-lab/sessions/<round-id>
python tools/scripts/verify_red_blue_workflow_v42.py --profile batch_adversarial --round project-reconstruction-lab/sessions/<batch-round-id>
python tools/scripts/verify_red_blue_round006_closure.py --round project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-ROUND-006
```

Verifier 只验证落盘 Artifact 的时序、hash、权限和状态不变量；不创建 Thread、不启动 Round、不
读取代码替代 Part A、不修改 Canonical，也不代签 ChatGPT。
