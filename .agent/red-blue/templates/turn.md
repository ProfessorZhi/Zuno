# Red / Blue Stage Artifact Templates

这个模板描述一轮中各文件应该保存什么。固定阶段产物直接写入同一个 Round 文件夹；阶段 handoff 只通过 Round branch 上已提交的 artifact 完成。

## 每个 Stage 的 GitHub 元数据

每个 artifact 顶部或 manifest 中至少能恢复：

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
### Zuno：<本轮最合理的项目标题>
项目简介：...
技术栈：...
1. ...
2. ...
3. ...
4. ...
```

Red 可见文件不得带 source trace、Current/Target 标签或答案提示。来源和构建边界写入 manifest / session transcript。

## `02_red_questions.md`

```text
# Red Questions — <round-id>

question_count: 100
primary_path_count: 30
reserve_count: 70
primary_persona:
cross_personas:
formal_input_head:
red_questions_status: DRAFT_REVIEW | FROZEN

## Claim map
- A — <resume claim>; risk: HIGH; reason: ...
- B — ...

## PRIMARY_PATH
### P001
question: ...
claim: A
ask_if: ALWAYS
kill_switch: none

### P002
question: ...
claim: A
ask_if: PREVIOUS_PASS
kill_switch: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED if candidate cannot name owned implementation object and mechanism

## RESERVE_FOLLOWUP
### R001
question: ...
claim: A
trigger: candidate demonstrates implementation ownership and exposes concurrency risk
```

Primary Path 默认 25–40 问，代表真实 45–60 分钟一面；Reserve 补足总压力集但不机械执行。具体实现 Claim 必须尽早出现 Ownership / mechanism probe，失败时使用 Kill Switch，避免继续堆同义问题。

题单末尾保存显式质量元数据：Claim coverage、Primary Path time realism、Kill Switch coverage、Attack Angle coverage、duplicate check。不得保存或伪造模型私有 chain-of-thought。

问题正文不附答案提示、Zuno 内部对象名答案或 source trace。

当 `red_review_gate=REQUIRED`，第一次提交的题单必须是 `DRAFT_REVIEW`。用户 `APPROVE` 后通过单独 Controller commit 冻结；用户 `REQUEST_REVISION` 时，先提交反馈，再让 Red 更新同一文件并重新进入审查。

## `03_blue_answers.md`

Blue 只能消费已经 `FROZEN` 的 Red questions。每题独立回答：

```text
### P001 / Rxxx
**Answer**
...

**Source trace**
- docs/project/...
- docs/modules/...
- Unknown: ...
```

Blue 可以明确说 Unknown / Target-only / not personally owned。

## `04_red_evaluation.md`

Red 不把 Zuno docs 作为评价输入，只按面试官视角评价：

```text
## Claim A
verdict: STRONG_PASS | PASS | PARTIAL | FAIL
ownership:
business_causality:
implementation_depth:
build_buy:
failure_recovery:
evidence:
fundamentals:
communication:

strongest_answer:
weakest_answer:
kill_switch_triggered:
resume_claim_risk:
retest_recommendation:
```

## `05_blue_architecture_reflection.md`

Blue 读取已提交 Red evaluation + 固定 Zuno docs 后，把问题路由：

```text
issue:
red_signal:
source_check:
classification: SIMULATED_RESUME_GAP | NARRATIVE_GAP | DOC_GAP | ARCHITECTURE_GAP | IMPLEMENTATION_GAP | EVIDENCE_GAP | OWNERSHIP_GAP | FUNDAMENTAL_GAP | NO_ZUNO_CHANGE
decision_impact:
recommended_owner:
retest_needed:
```

不得因为 Red 问到了一个冷门实现字段，就新增 Architecture Object。

## `06_workflow_retrospective.md`

重点评价：Primary Path 是否像真实面试、Reserve 是否真的条件化、Kill Switch 是否减少无信息增益追问，以及用户对第一轮 Red 的评价。

## `07_user_feedback.md`

按时间追加用户对本轮的直接评价：

```text
feedback_id:
when:
text:
affected_stage:
priority:
input_head_sha:
commit_sha:
```

Round 启动前已知的用户校准要求也必须在 ROUND_INIT transaction 中记录，不能后补。

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

至少记录 Round/PR 初始化、用户反馈、Resume Builder、Red、USER_RED_REVIEW、Red Revision（如有）、Blue、Evaluation、Reflection、Retrospective、CI、Archive 与 Merge。

CHATGPT_AUTO 与 AGENT_AUTO 使用同一格式。Transcript 保存可观察 I/O 和 GitHub state transition，不保存或伪造模型私有 chain-of-thought。
