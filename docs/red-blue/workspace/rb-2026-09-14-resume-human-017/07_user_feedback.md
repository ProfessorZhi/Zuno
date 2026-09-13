# User Feedback — rb-2026-09-14-resume-human-017

## UF-001 — Resume must look like an actual resume

when: 2026-09-14T01:30:00+08:00
priority: highest
affected_stage: BUILD_RESUME / USER_RESUME_REVIEW
text: 模拟简历不能像 Evidence / provenance 摘要。先对照用户本人真实简历和公开优秀 AI / Agent 简历的字数、句长、版式与信息密度，产出真正可投递的一页简历项目块，再交给 Red。

## UF-002 — Use old resume style, not old resume facts

when: 2026-09-14T01:30:00+08:00
priority: highest
affected_stage: BUILD_RESUME
text: 用户本人旧简历的项目标题、日期、Ownership 与 Current 事实可能已过时或与 canonical evidence 冲突；只能复用其招聘语体、句长、动词、单页布局和信息密度。事实必须重新从当前 Zuno canonical sources 构建。

## UF-003 — Density target

when: 2026-09-14T01:30:00+08:00
priority: highest
affected_stage: BUILD_RESUME
text: 用户旧 Zuno 段平均约 65 字符/条，但 8 条 Zuno + 10 条 Astrid + 7 条技能整体偏满。新模拟 Zuno 默认收敛到 4–5 条最强贡献，一条一个主要故事；技术深度交给面试追问展开。

## UF-004 — Stop before Red

when: 2026-09-14T01:30:00+08:00
priority: highest
affected_stage: USER_RESUME_REVIEW
text: 本轮先只检查模拟简历。用户未 APPROVE 前禁止 Red、Blue 或任何基于该简历的采访产物。
