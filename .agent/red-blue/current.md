# Current Red / Blue Round

state: `no-active`
active_round: `none`
mode: `none`
stage: `none`
workspace_path: `none`
simulated_resume: `none`
target_role: `none`
interview_stage: `none`
question_count: `100`
transcript_policy: `full-observable-role-io`
archive_live: `true`

Active Round 工作区统一位于：

```text
docs/red-blue/workspace/<round-id>/
```

Round 关闭后整个文件夹原样归档到：

```text
docs/red-blue/rounds/<round-id>/
```

## 允许的 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `CHATGPT_AUTO | AGENT_AUTO`
stage: `BUILD_RESUME | RED_QUESTIONS | BLUE_ANSWERS | RED_EVALUATION | BLUE_REFLECTION | WORKFLOW_RETROSPECTIVE | USER_FEEDBACK | CLOSE`
workspace_path: `docs/red-blue/workspace/<round-id>/`
simulated_resume: `docs/red-blue/workspace/<round-id>/01_simulated_resume.md`
target_role: `<role>`
interview_stage: `<stage>`
question_count: `<positive integer; default 100>`
transcript_policy: `full-observable-role-io`
archive_live: `true`
```

Round 的 Red 输入必须是 resume-first：模拟简历冻结后，Red 只能读取该简历、岗位 / JD、`.agent/red-blue/attack-model.md` 和通用模型知识。Red 不得读取 Zuno Project / Architecture / Modules / Evidence。

无论 `CHATGPT_AUTO` 还是 `AGENT_AUTO`，一轮固定保存：

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
```

用户 intervention 必须写入 `07_user_feedback.md` / `08_session_transcript.md`。全过程指可观察角色 I/O 与控制事件，不包含、也不得伪造模型私有 chain-of-thought。

当前：没有 active Round。Round #013 保留为历史，但其 Red 直接读取 Zuno docs 的方法已经被 resume-first protocol 取代。