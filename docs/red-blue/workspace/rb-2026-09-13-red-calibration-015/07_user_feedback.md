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
