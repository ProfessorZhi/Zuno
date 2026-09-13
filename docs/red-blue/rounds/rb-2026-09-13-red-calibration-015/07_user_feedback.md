# User Feedback — rb-2026-09-13-red-calibration-015

## UF-001 — Stop at first Red output for human inspection

when: 2026-09-13T20:16:00+08:00
affected_stage: ROUND_INIT / RED_QUESTIONS / USER_RED_REVIEW
priority: highest
text: 继续收敛 Red/Blue 工作流，只运行到 Red 第一轮产出并交给用户检查；在用户明确批准前不要继续 Blue。
required_behavior:
- 全程继续通过 GitHub stage transaction 交互
- Red 第一轮产出后进入 USER_RED_REVIEW
- 用户未 APPROVE 时 03_blue_answers.md 保持 BLOCKED

## UF-002 — Red first output must be interview-realistic

when: 2026-09-13T20:16:00+08:00
affected_stage: RED_QUESTIONS
priority: highest
text: 本轮首先检查 Red 本身是否合格。Primary Path 应像真实大厂技术一面，不把 100 问机械当脚本；高风险实现 Claim 先做 Ownership / mechanism probe，低信息增益时使用 Kill Switch，Reserve 只做条件追问。

## UF-003 — Red lacks natural interviewer behavior

when: 2026-09-13T21:51:00+08:00
affected_stage: USER_RED_REVIEW / RED_SKILL
priority: highest
review_decision: REQUEST_REVISION
text: 当前 Red 问题不够人味，仍然像工程 checklist 改写成问句。先研究真实面经并完善 Red 思维框架，再重新生成问题。
required_behavior:
- 不进入 Blue
- 不只润色旧题
- 研究公开的大厂 Agent / LLM 应用 / AI 后端面经
- 提炼真实面试官的对话节奏、临场追问、回答驱动分支和重点转移
- 将这些行为写入 Red Skill
- 更新 Skill 后重新生成 Red；当前第一版不算通过
