# Current Red / Blue Round

state: `active-red-blue`
active_round: `rb-2026-09-13-human-red-016`
mode: `CHATGPT_AUTO`
stage: `BUILD_RESUME`
workspace_path: `docs/red-blue/workspace/rb-2026-09-13-human-red-016/`
simulated_resume: `docs/red-blue/workspace/rb-2026-09-13-human-red-016/01_simulated_resume.md`
target_role: `Agent 开发工程师 / AI 应用工程师`
interview_stage: `项目深挖 / 技术一面`
pressure_suite_count: `100`
seed_question_target: `8`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
red_review_gate: `REQUIRED`
red_questions_status: `NOT_STARTED`
round_branch: `red-blue/rb-2026-09-13-human-red-016`
round_pr: `231`
last_consumed_head_sha: `56c2d83842f606f6d78efd0115dadc9b5d17c23c`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED`
strict_blind_red_certification: `false`
transcript_policy: `full-observable-role-io`
archive_live: `true`

本轮验证 answer-driven Red：现场只有少量自然 Seed，后续问题由上一答动态生成；100 问只作为离线 Pressure Suite。用户要求第一版 Red 提交后立即进入 USER_RED_REVIEW，未经 APPROVE 不得运行 Blue。
