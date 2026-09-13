# Current Red / Blue Round

state: `active-red-blue`
active_round: `rb-2026-09-13-resume-first-014`
mode: `CHATGPT_AUTO`
stage: `RED_QUESTIONS`
workspace_path: `docs/red-blue/workspace/rb-2026-09-13-resume-first-014/`
simulated_resume: `docs/red-blue/workspace/rb-2026-09-13-resume-first-014/01_simulated_resume.md`
target_role: `Agent 开发工程师 / AI 应用工程师`
interview_stage: `项目深挖 / 技术一面`
question_count: `100`
round_branch: `red-blue/rb-2026-09-13-resume-first-014`
round_pr: `226`
stage_head_sha: `2ee974298f1322c0d4f88731da55cd3fe3ba4b31`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED`
strict_blind_red_certification: `false`
transcript_policy: `full-observable-role-io`
archive_live: `true`

Live GitHub branch HEAD is authoritative for stage input. `stage_head_sha` records the GitHub HEAD consumed by the just-completed BUILD_RESUME stage.

当前阶段：RED_QUESTIONS。Red 的正式输入仅允许来自冻结后的 `01_simulated_resume.md`、manifest 中的岗位 / 轮次、`.agent/red-blue/attack-model.md` 与模型通用知识。CHATGPT_AUTO 不声明严格 blind Red certification。
