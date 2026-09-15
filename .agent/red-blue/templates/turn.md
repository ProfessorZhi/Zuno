# Red / Blue Stage Artifact Templates

这个模板描述一轮中各文件保存什么。所有阶段 handoff 只通过 Round branch 上已提交的 artifact 完成。

## Stage GitHub 元数据

```text
stage:
input_head_sha:
input_files:
output_file:
output_commit_sha:
```

## `00_manifest.yaml`

至少持续记录：

```text
zuno_base_sha:
pinned skill versions:
execution_mode: BATCH_DUEL | LIVE_INTERVIEW
current_stage:
last_consumed_head_sha:
resume_status:
red_wave_1_status:
red_wave_1_question_count:
blue_wave_1_status:
blue_wave_1_answer_count:
red_wave_2_status:
red_wave_2_question_count:
blue_wave_2_status:
blue_wave_2_answer_count:
red_evaluation_status:
blue_reflection_status:
workflow_retrospective_status:
improvement_ledger_status:
round_report_status:
next_resume_candidate_status:
```

## `01_simulated_resume.md`

必须像真实投递简历。默认结构：项目简介 1 行、技术栈 1 行、约 4–6 条高价值 bullet。

```text
真实工程问题 → 本人动作 / 技术决策 → 关键机制 → 可信结果
```

不要写功能清单、证据报告或 Reviewer 免责声明。Red 可见版本不得携带 source trace、Current/Target/Evidence 标签或答案提示。

## `02_red_questions.md` — Red Wave 1

保存 **恰好 100 个问题**。

```text
# Red Wave 1 — <round-id>

question_count: 100
formal_input_head:
blind_input:
- frozen resume
- target / JD / stage
- pinned attack-model

## Thread Map
...

## Questions
### R1-Q001
question: ...
intent: <internal metadata>
resume_handle: <internal metadata>

...

### R1-Q100
...

## Red self-check
- exactly_100: true
- one_question_one_intent: true
- zuno_docs_read: false
```

## `03_blue_answers.md` — Blue Wave 1 Candidate Answers

Blue 对 R1-Q001..R1-Q100 一一回答。

```text
# Blue Wave 1 Answers — <round-id>

answer_count: 100

### R1-Q001
question: ...
answer: <candidate spoken answer>
source_support: <internal; not spoken>
boundary: <internal>

...

### R1-Q100
...
```

Candidate answer 不能主动念 PF / commit / classification。

## `03_blue_architecture_notes.md` — Sealed Wave 1 Diagnosis

这个文件对 Red Wave 2 和 Red Final **不可见**。

```text
# Blue Wave 1 Architecture Notes — <round-id>

## Signal A001
question_refs:
red_signal:
source_check:
current:
target:
evidence:
unknown:
is_answer_gap_or_system_gap:
classification:
simplest_option:
current_failure:
candidate_change:
cost:
exit_condition:
measurement_needed:
```

不得因为 Red 问到一个冷门字段，就新增 Architecture Object。

## `04_red_wave2_review_and_questions.md` — Red Wave 2

这个文件同时保存 **Blue 1 盲评 + 100 个针对性追问**。

```text
# Red Wave 2 — <round-id>

input_blue_wave_1_commit:
question_count: 100
blue_architecture_notes_read: false
zuno_docs_read: false

## Part A — Blue Wave 1 Blind Evaluation

### Thread <id>
verdict: STRONG_PASS | PASS | PARTIAL | FAIL
what_became_credible:
what_is_still_weak:
observable_handles:
question_premise_corrections:
weight_next_wave: INCREASE | KEEP | DECREASE | DROP

## Part B — 100 Targeted Follow-ups

### R2-Q001
question: ...
from_blue_1_handle: ...
intent: ...

...

### R2-Q100
...
```

Wave 2 不允许机械改写 Wave 1 原题。

## `04_blue_wave2_answers.md` — Blue Wave 2 Candidate Answers

```text
# Blue Wave 2 Answers — <round-id>

answer_count: 100
wave_1_architecture_notes_used_for_coaching: false

### R2-Q001
question: ...
answer: ...
source_support: <internal>
boundary: <internal>

...

### R2-Q100
...
```

## `04_blue_wave2_architecture_notes.md` — Sealed Wave 2 Diagnosis

结构与 Wave 1 notes 相同，但必须额外记录：

```text
blue_1_diagnosis_changed: true | false
why_changed:
red_2_pressure_effect:
```

对 Red Final Evaluation 封存。

## `04_red_evaluation.md` — Final Blind Evaluation

只评价两轮可观察 Q/A：

```text
# Red Final Evaluation — <round-id>

overall_verdict: STRONG_PASS | PASS | PARTIAL | FAIL
canonical_docs_read: false
blue_architecture_notes_read: false

## Thread <id>
verdict:
blue_1_state:
blue_2_state:
ownership:
implementation_depth:
build_buy:
failure_recovery:
evidence:
fundamentals:
communication:
strongest_exchange:
weakest_exchange:
resume_claim_risk:
```

必须判断 Blue 2 是真正解释，还是换话术补洞。

## `05_blue_architecture_reflection.md` — Final Architecture Reflection

```text
# Blue Final Architecture Reflection — <round-id>

## Issue <id>
red_signal:
blue_1_diagnosis:
blue_2_diagnosis:
red_final_signal:
source_check:
classification: SIMULATED_RESUME_GAP | NARRATIVE_GAP | DOC_GAP | ARCHITECTURE_GAP | IMPLEMENTATION_GAP | EVIDENCE_GAP | OWNERSHIP_GAP | FUNDAMENTAL_GAP | NO_ZUNO_CHANGE
current:
target:
evidence:
unknown:
real_problem:
simplest_solution:
where_current_design_fails:
alternatives:
recommended_change:
owner_authority_impact:
cost:
exit_condition:
measurement_needed:
retest_needed:
```

Multi-Agent / GraphRAG / Native Runtime 等复杂方案必须有出现条件和删除条件。

## `06_workflow_retrospective.md`

固定五部分：

```text
## Resume Builder Reflection
- selected real engineering stories?
- wording / metrics / ownership errors?

## Red Thinking Framework Reflection
- Wave 1 question construction
- Wave 2 blind evaluation quality
- answer-driven adaptation
- depth / realism / neutrality
- attack-model changes needed

## Blue Candidate Framework Reflection
- Historical / Current / Target / Open Design classification
- directness / ownership / mechanism / evidence
- over-defensiveness / invented detail
- defense-model changes needed

## Blue Architecture Framework Reflection
- failure-driven reasoning
- simplest baseline respected?
- answer gap vs architecture gap separated?
- complexity cost / exit condition present?
- architecture reasoning changes needed

## Harness Reflection
- 100/100/100/100 invariant
- sealed notes firewall
- commit barriers
- batch link checkpoints
- stage/gate friction
- artifact quality
```

每个 proposed change 标注 `NEXT_ROUND_ONLY`。

## `07_user_feedback.md`

按时间追加用户评价，包括对 Resume、Red、Blue、架构、工作流节奏和批次链接的反馈。

## `08_session_transcript.md`

记录 workflow event：

```text
### Event <n>
actor: Controller | User | ResumeBuilder | Red | BlueCandidate | BlueArchitecture | RedEvaluation | WorkflowRetrospective | ImprovementSynthesizer
stage:
input_head_sha:
input_files:
observable_input_summary:
observable_output_summary:
output_files:
output_commit_sha:
next_stage:
```

## `09_improvement_ledger.md`

```text
# Round Improvement Ledger — <round-id>

## Finding IMP-001
signal:
source_artifacts:
root_cause:
primary_class: RESUME_GAP | RED_SKILL_GAP | BLUE_SKILL_GAP | HARNESS_GAP | NARRATIVE_GAP | DOC_GAP | ARCHITECTURE_GAP | IMPLEMENTATION_GAP | EVIDENCE_GAP | OWNERSHIP_GAP | FUNDAMENTAL_GAP | NO_CHANGE
secondary_class:
owner:
proposed_change:
evidence_needed:
risk_if_changed:
status: APPLY | DEFER | REJECT | NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest:
```

## `09_round_report.md`

面向用户的轮末报告：

```text
# Round Report — <round-id>

## Red 1 打出了什么
## Blue 1 暴露了什么
## Red 2 如何针对追杀
## Blue 2 是否顶住
## 最终候选人评价
## 架构真实缺陷
## Red / Blue 思维框架缺陷
## Harness 缺陷
## 建议修改
## 不建议修改
## 下一轮复测
```

## `10_next_resume_candidate.md`

```text
# Next Resume Candidate — from <round-id>
source_head_sha:
source_round:
status: BUILT | BLOCKED

<resume content>

## Carry-forward constraints
- <unresolved evidence / ownership / implementation boundaries>
```

它不是当前轮 Frozen Resume。下一轮仍要重新校验并经过 USER_RESUME_REVIEW。

## BATCH_CHECKPOINT 用户输出

每完成一个正式批次，默认聊天只返回该 GitHub 文档链接：

```text
Red Wave 1 → 02_red_questions.md
Blue Wave 1 → 03_blue_answers.md
Red Wave 2 → 04_red_wave2_review_and_questions.md
Blue Wave 2 → 04_blue_wave2_answers.md
```

用户无需逐题作答。

## LIVE_INTERVIEW Exchange Ledger（可选）

若显式进入 LIVE_INTERVIEW，仍使用真正的 Red question committed → Blue answer committed → 下一 Red follow-up。Live Interview Exchange Ledger 可以保存到独立追加 artifact；它不是自动 BATCH_DUEL 默认。

CHATGPT_AUTO 与 AGENT_AUTO 使用同一事实边界。任何文件都不保存或伪造模型私有 chain-of-thought。