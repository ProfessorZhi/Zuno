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
primary_persona:
cross_personas:

## Claim A — <resume claim>
Q001. ...
Q002. ...
...
```

可以在文件末尾保存 Red 自己的显式质量元数据：Claim coverage、Attack Angle coverage、duplicate check。不得保存或伪造模型私有 chain-of-thought。

问题正文不附答案提示、Zuno 内部对象名答案或 source trace。

## `03_blue_answers.md`

每题独立回答：

```text
### Q001
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
why_interviewer_would_continue:
resume_claim_risk:
retest_recommendation:
```

同时给出整轮最危险的 3–10 个面试断点。

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

这是对 Red / Harness 的复盘，不是第二份 Blue findings。

```text
# Workflow Retrospective

## User feedback considered
...

## Red quality score
Resume Grounding:
Technical Depth:
Full-chain Coverage:
Non-duplication:
Build/Buy Skepticism:
Failure Pressure:
Fundamentals Drilldown:
Interview Realism:
Information Gain:
User Alignment:

## Low-value questions
- Q... why low value

## Missing attack chains
...

## Skill defects
...

## Protocol defects
...

## Proposed next-round changes
...
```

用户对问题质量的明确批评优先于模型自评分。

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

影响当前 Round 的 feedback 先提交，再进入后续 stage。即使用户没有追加评价，也保留文件并写 `no_additional_feedback`。

## `08_session_transcript.md`

保存可观察过程，并让阶段交接可以从 GitHub history 重放：

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

至少记录：

```text
Round branch / Draft PR initialization
Controller / user events
Resume Builder event
Red input boundary + output event
Blue input boundary + output event
Red Evaluation event
Blue Reflection event
Workflow Retrospective event
GitHub commit / CI / archive / merge events
```

CHATGPT_AUTO 与 AGENT_AUTO 使用同一格式。Transcript 保存的是可观察 I/O 和 GitHub state transition，不保存或伪造模型私有 chain-of-thought。