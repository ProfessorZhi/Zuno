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

`output_commit_sha` 可以由 Git history / transcript 记录，不要求文件在同一次 commit 内自引用自身 SHA。

## `01_simulated_resume.md`

```text
# 模拟简历 — <round-id>

求职方向：<role>

## 项目经历
### Zuno：<project title>
项目简介：...
技术栈：...
1. ...
2. ...
3. ...
4. ...
```

Red 可见文件不得带 source trace、Current/Target 标签或答案提示。

## `02_red_questions.md`

这个文件现在保存 **Red Interview Plan + Pressure Suite**，不再保存固定 30 问线性脚本。

```text
# Red Interview Plan — <round-id>

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
primary_persona:
cross_personas:
formal_input_head:
red_questions_status: DRAFT_REVIEW | FROZEN

## Interview threads
- A — <resume claim / thread>; risk: HIGH; initial suspicion: ...
- B — ...

## SPOKEN_SEEDS
S001. <自然、单意图的开场问题>
S002. ...

## FOLLOWUP_POLICY
- candidate mentions a precise metric -> ask where the number came from; wait for answer before asking dataset/metric details
- candidate says "我们做了" -> naturally clarify own contribution
- candidate describes a real failure -> stay on that failure and trace diagnosis / fix / result
- thread stops producing information -> pivot

## BRANCH_EXAMPLES
### Branch 1
candidate_answer_summary: ...
next_spoken_question: ...
why_this_handle: <observable interviewer reason; not hidden chain-of-thought>

## PRESSURE_SUITE
### Q001
question: ...
thread: A
trigger: ...
...

## Red self-check
...
```

`SPOKEN_SEEDS` 是第一次用户校准时重点检查的表面问题。它默认 6–10 条，只负责启动对话。后续真正说给候选人的问题由上一答动态生成，不要求事先编号。

`PRESSURE_SUITE` 默认保留 100 问，用于离线覆盖和 retrospective；它不是实际 45–60 分钟面试会逐题执行的脚本。

Controller Metadata 可以记录 thread、risk、Kill Switch 和触发条件，但面试官口头问题不附 Claim 标签、评分 rubric 或 Kill Switch。

当 `red_review_gate=REQUIRED`，第一次提交必须是 `DRAFT_REVIEW`。用户 `APPROVE` 后单独冻结；`REQUEST_REVISION` 时先提交反馈，再更新同一文件。

## `03_blue_answers.md`

Blue 只能消费已经 `FROZEN` 的 Red plan 与实际 interview transcript。回答继续保留 Source trace，并可明确 Unknown / Target-only / not personally owned。

## `04_red_evaluation.md`

Red Evaluation 应评价候选人在**实际对话分支**上的表现，而不是检查 100 问是否逐题答完：

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
kill_switch_triggered:
resume_claim_risk:
```

## `05_blue_architecture_reflection.md`

```text
issue:
red_signal:
source_check:
classification: SIMULATED_RESUME_GAP | NARRATIVE_GAP | DOC_GAP | ARCHITECTURE_GAP | IMPLEMENTATION_GAP | EVIDENCE_GAP | OWNERSHIP_GAP | FUNDAMENTAL_GAP | NO_ZUNO_CHANGE
decision_impact:
recommended_owner:
retest_needed:
```

不得因为 Red 问到冷门实现字段，就新增 Architecture Object。

## `06_workflow_retrospective.md`

重点评价：Seed 是否自然、Follow-up 是否真的使用上一答、线程切换是否像真人、是否存在复合长问或无信息增益原子化，以及 Pressure Suite 有没有被误当成现场脚本。

## `07_user_feedback.md`

按时间追加用户评价。Round 启动前已知的校准要求也在 ROUND_INIT transaction 中记录。

## `08_session_transcript.md`

```text
### Event <n>
actor: Controller | User | ResumeBuilder | Red | Blue | RedEvaluation | BlueReflection | WorkflowRetrospective
stage:
input_head_sha:
input_files:
observable_input_summary:
observable_output_summary:
output_files:
output_commit_sha:
next_stage:
```

如果实际执行 Live Interview，transcript 还应保存可观察的 interviewer question / candidate answer exchange，使后续 Red Evaluation 能依据真正发生的分支评价，而不是依据预写题库。

CHATGPT_AUTO 与 AGENT_AUTO 使用同一格式。Transcript 不保存或伪造模型私有 chain-of-thought。
