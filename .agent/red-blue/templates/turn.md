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
pinned skill versions:
current_stage:
last_consumed_head_sha:
resume_status:
red_questions_status:
live_interview_status:
live_turn_index:
next_actor: RED | BLUE | NONE
red_evaluation_status:
blue_reflection_status:
workflow_retrospective_status:
improvement_ledger_status:
next_resume_candidate_status:
```

每个 stage / live turn 提交时同步更新；下一个 actor 必须从新的 manifest + branch HEAD 重新开始。

## `01_simulated_resume.md`

必须像候选人真实会投递的简历项目块。默认结构：项目简介 1 行、技术栈 1 行、约 4–6 条高价值 bullet。

每条优先写：

```text
真实工程问题 → 本人动作 / 技术决策 → 关键机制 → 可信结果
```

不要写功能清单、证据报告或 Reviewer 免责声明。Red 可见版本不得携带 source trace、Current/Target/Evidence 标签或答案提示。

## `02_red_questions.md`

保存 **Red Interview Plan + Pressure Suite**，不保存固定现场脚本。

```text
# Red Interview Plan — <round-id>

question_count: 100
seed_question_count: 8
live_followups: DYNAMIC
one_question_one_intent: true
formal_input_head:
red_questions_status: DRAFT_REVIEW | FROZEN

## Interview threads
...

## SPOKEN_SEEDS
S001. ...

## FOLLOWUP_POLICY
...

## BRANCH_EXAMPLES
...

## PRESSURE_SUITE
...

## Red self-check
...
```

## `03_blue_answers.md` — Live Interview Exchange Ledger

这个文件不再是一口气生成的批量答案。它按真实顺序追加 Red / Blue exchanges：

```text
# Live Interview — <round-id>

## Exchange 001
thread: <thread id>
red_question_commit_sha: <sha>
red_question: <spoken question>
blue_answer_commit_sha: <sha>
blue_answer: <spoken answer>
observable_handles_for_next_turn:
  - <keyword / number / decision / failure exposed by answer>

## Exchange 002
...

## Interview Stop
reason:
threads_completed:
approx_elapsed:
```

规则：

```text
Red question committed
→ Blue re-read HEAD and answer
→ Blue answer committed
→ Red re-read HEAD and choose next question
```

一个 exchange 的 question / answer 不能在同一角色步骤里预生成。

Blue spoken answer 不主动念 source trace。内部可在回答后附隐藏于 artifact 语义层的 `source_support` 字段供后续 Blue Reflection 使用，但现场文本必须像面试回答。

## `04_red_evaluation.md`

评价实际发生的 thread：

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
why_this_classification:
decision_impact:
recommended_owner:
retest_needed:
```

不得因为 Red 问到一个冷门字段，就新增 Architecture Object。

## `06_workflow_retrospective.md`

固定四部分：

```text
## Resume Builder Reflection
- what worked
- what selected the wrong story / metric / wording
- resume-builder changes needed

## Red Skill Reflection
- listening / adaptation
- depth / pivot
- realism
- attack-model changes needed

## Blue Skill Reflection
- directness
- ownership
- mechanism depth
- evidence / boundary honesty
- conversational quality
- defense-model changes needed

## Harness Reflection
- turn ordering
- firewall
- stage/gate friction
- artifact quality
- protocol/template changes needed
```

每个 proposed change 必须标注 `NEXT_ROUND_ONLY`。

## `07_user_feedback.md`

按时间追加用户评价。用户指出“Red 问得假”“Blue 太像文档”“简历没技术含量”“架构解释有问题”等，都原样进入反馈，再由后续 synthesis 分类。

## `08_session_transcript.md`

记录 workflow event，不替代 Live Interview Ledger：

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

用户 Gate 决定哪些 item 可以执行。

## `10_next_resume_candidate.md`

轮末从 post-improvement HEAD 生成下一轮候选简历：

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

CHATGPT_AUTO 与 AGENT_AUTO 使用同一 artifact 结构。任何文件都不保存或伪造模型私有 chain-of-thought。