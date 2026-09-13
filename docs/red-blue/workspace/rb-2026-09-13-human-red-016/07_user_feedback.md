# User Feedback — rb-2026-09-13-human-red-016

## UF-001 — Stop at first Red output

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: ROUND_INIT / RED_QUESTIONS / USER_RED_REVIEW
text: 本轮只运行到新版 Red 第一轮产出并交给用户检查；用户未 APPROVE 前禁止进入 Blue。

## UF-002 — Previous Red model was rejected

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: RED_QUESTIONS
text: Round #015 的 30 条 Primary 虽然技术上合理，但不够人味，像工程 / 架构 checklist 改写成复合问句。不得复用这种现场脚本结构。

## UF-003 — Human interviewer behavior is the calibration target

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: RED_QUESTIONS / USER_RED_REVIEW
text: 新 Red 必须像真实面试官：先让候选人自己暴露主线；问题简短、一次一个主要意图；下一问根据上一答里的关键词、数字、选择、困难、Ownership 或 bad case 动态生成；有价值的 thread 可以连续追，信息增益下降时自然换题。100 问只作为离线 Pressure Suite。
review_focus:
- SPOKEN_SEEDS 是否自然
- BRANCH_EXAMPLES 是否真的由上一答驱动
- 是否仍有 Reviewer checklist 味
- 是否有无信息增益的原子化追问
- 是否把 Controller rubric / Kill Switch 暴露成口头问题
