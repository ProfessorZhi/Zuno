# Red / Blue Stage Artifact Templates

这个模板描述一轮中各文件应该保存什么。阶段 handoff 只通过 Round branch 上已提交的 artifact 完成。

## Stage GitHub 元数据

```text
stage:
input_head_sha:
input_files:
output_file:
output_commit_sha:
```

## `00_manifest.yaml`

Manifest 是 Round Controller 的机器状态，不保存面试内容本身。至少持续记录：

```text
zuno_base_sha:
mode: CHATGPT_AUTO | AGENT_AUTO
execution_mode: BATCH_DUEL | LIVE_INTERVIEW
pinned skill versions:
current_stage:
last_consumed_head_sha:
resume_status:
red_questions_status:
batch_duel_status:
batch_wave_index:
live_interview_status:
live_turn_index:
next_actor: RED | BLUE | NONE
red_evaluation_status:
blue_reflection_status:
workflow_retrospective_status:
improvement_ledger_status:
next_resume_candidate_status:
```

每个 stage / batch wave / live turn 提交时同步更新；下一个 actor 必须从新的 manifest + branch HEAD 重新开始。

## `01_simulated_resume.md`

必须像候选人真实会投递的简历项目块。默认项目简介 1 行、技术栈 1 行、约 4–6 条高价值 bullet。

每条优先写：

```text
真实工程问题 → 本人动作 / 技术决策 → 关键机制 → 可信结果
```

不要写功能清单、证据报告或 Reviewer 免责声明。Red 可见版本不得携带 source trace、Current/Target/Evidence 标签或答案提示。

## `02_red_questions.md`

保存 **Red Interview Plan + PRESSURE_SUITE + executed Red waves/turn plan**。

```text
# Red Interview Plan — <round-id>

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
formal_input_head:
red_questions_status: DRAFT_REVIEW | FROZEN

## Interview threads
## SPOKEN_SEEDS
## FOLLOWUP_POLICY
## BRANCH_EXAMPLES
## PRESSURE_SUITE
## Red self-check
```

### BATCH_DUEL

Plan 冻结后在同一 artifact 追加：

```text
## RED_WAVE_1
input_head_sha:
selected_question_count:
questions:
- ...

## RED_WAVE_2
input_blue_wave1_commit_sha:
observable_gaps_used:
- <Blue Wave 1 暴露的数字 / Unknown / failure / claim>
questions:
- ...
```

Red Wave 2 必须在 Blue Wave 1 commit 后生成。`PRESSURE_SUITE` 是覆盖库，不要求 100 题全部进入 Wave 1。

### LIVE_INTERVIEW

`SPOKEN_SEEDS` 启动后，真正 follow-up 每次只生成一个主要意图；Red question 先 commit，Blue 才回答。

## `03_blue_answers.md`

### BATCH_DUEL — Batch Answer Ledger

```text
# Blue Batch Answers — <round-id>

## BLUE_WAVE_1
input_red_wave1_commit_sha:
### Q...
spoken_answer: ...
source_support: ...
boundary: ...

## BLUE_WAVE_2
input_red_wave2_commit_sha:
### Q...
spoken_answer: ...
source_support: ...
boundary: ...
```

`spoken_answer` 像真实候选人口语；`source_support / boundary` 只供后续 Reflection 使用，不念给面试官。

Blue Wave 2 只能回答已经提交的 Red Wave 2，不预读未来 Evaluation。

### LIVE_INTERVIEW — Exchange Ledger

```text
# Live Interview — <round-id>

## Exchange 001
thread:
red_question_commit_sha:
red_question:
blue_answer_commit_sha:
blue_answer:
observable_handles_for_next_turn:
  - ...
```

规则：

```text
Red question committed
→ Blue re-read HEAD and answer
→ Blue answer committed
→ Red re-read HEAD and choose next question
```

## `04_red_evaluation.md`

评价实际执行的 batch waves 或 live threads：

```text
thread:
verdict: STRONG_PASS | PASS | PARTIAL | FAIL
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

Red Evaluation 不读取 Zuno canonical docs。

## `05_blue_architecture_reflection.md`

```text
issue:
red_signal:
source_check:
classification: SIMULATED_RESUME_GAP | NARRATIVE_GAP | DOC_GAP | ARCHITECTURE_GAP | IMPLEMENTATION_GAP | EVIDENCE_GAP | OWNERSHIP_GAP | FUNDAMENTAL_GAP | NO_ZUNO_CHANGE
why_this_classification:
decision_impact:
recommended_owner:
retest_needed:
```

不得因为 Red 问到一个字段，就新增 Architecture Object。

## `06_workflow_retrospective.md`

固定四部分：

```text
## Resume Builder Reflection
## Red Skill Reflection
## Blue Skill Reflection
## Harness Reflection
```

BATCH_DUEL 要额外检查：

- Wave 1 是否选高信息量问题而非机械消费 100 问；
- Wave 2 是否真的读取 Blue Wave 1；
- Batch answer 是否仍像候选人，不像 Evidence report；
- 用户是否被错误要求逐题扮演候选人。

LIVE_INTERVIEW 检查 turn ordering、listening、one-intent、pivot。

所有 proposed change 标注 `NEXT_ROUND_ONLY`。

## `07_user_feedback.md`

按时间追加用户评价。用户对 Resume、Red、Blue、架构目标、Batch/Live execution preference 的反馈都先进入这里，再由 Improvement synthesis 分类。

## `08_session_transcript.md`

记录 workflow event：

```text
### Event <n>
actor: Controller | User | ResumeBuilder | Red | Blue | RedEvaluation | BlueReflection | WorkflowRetrospective | ImprovementSynthesizer
stage:
input_head_sha:
input_files:
observable_input_summary:
observable_output_summary:
output_files:
output_commit_sha:
next_stage:
```

BATCH_DUEL 每个 wave 单独一个 event；LIVE_INTERVIEW 每个 turn 可以逐条记录或按已提交 exchange 聚合，但不能伪造未发生的回答。

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

用户 Gate 决定未预先批准的 item 是否执行。

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

它不是当前轮 Frozen Resume，也不是下一轮自动 FROZEN Resume。下一轮仍要重新校验并经过 USER_RESUME_REVIEW。

CHATGPT_AUTO 与 AGENT_AUTO 使用同一 artifact 结构；execution mode 独立选择。任何文件都不保存或伪造模型私有 chain-of-thought。
