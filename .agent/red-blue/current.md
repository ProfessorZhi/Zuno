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
round_branch: `none`
round_pr: `none`
stage_head_sha: `none`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `none`
strict_blind_red_certification: `false`
transcript_policy: `full-observable-role-io`
archive_live: `true`

正式 Round 在独立 GitHub branch 和 Draft PR 上执行。Round branch 中的 Active Workspace 位于：

```text
docs/red-blue/workspace/<round-id>/
```

Round 关闭前归档到：

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
round_branch: `red-blue/<round-id>`
round_pr: `<GitHub PR number>`
stage_head_sha: `<current Round branch HEAD>`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED | PHYSICAL_CONTEXT_ISOLATION`
strict_blind_red_certification: `false | true`
transcript_policy: `full-observable-role-io`
archive_live: `true`
```

模式映射：

```text
CHATGPT_AUTO -> LOGICAL_GITHUB_MEDIATED -> strict_blind_red_certification: false
AGENT_AUTO   -> PHYSICAL_CONTEXT_ISOLATION -> strict_blind_red_certification: true
```

每个阶段开始前必须从 `stage_head_sha` 对应的 GitHub HEAD 重新读取 manifest 和本阶段允许输入。前一阶段只有在目标 artifact、manifest state 和 `08_session_transcript.md` 已提交后才完成。

模拟简历冻结后，Red 的正式业务输入只能来自已提交的模拟简历、岗位 / JD、`.agent/red-blue/attack-model.md` 和模型通用知识。`CHATGPT_AUTO` 提供可审计的逻辑隔离；需要严格 blind Red 验收时使用 `AGENT_AUTO`。

无论哪种模式，一轮固定保存：

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

用户 intervention 必须先写入 `07_user_feedback.md` / `08_session_transcript.md` 并提交，再推进阶段。

当前：没有 active Round。Round #013 保留为历史，但其 Red 直接读取 Zuno docs 的方法已经被 resume-first protocol 取代。