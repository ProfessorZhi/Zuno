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

## UF-005 — Participation breadth is too thin

when: 2026-09-14T01:42:00+08:00
priority: highest
affected_stage: USER_RESUME_REVIEW / RESUME_REVISION
text: 当前四条版本虽然更像简历，但把项目参与范围压得过窄，读起来像只做了四个孤立修补点。需要在保持招聘可读性的同时恢复足够的参与 breadth，让 Agent、Tool/MCP、GraphRAG、Context/Memory、测试与工程判断等主要参与面能够被看见。
required_change:
- 不回退到 Evidence memo 式长 bullet
- 允许 5–6 条核心贡献，而不是机械坚持 4 条
- Tool Calling strategy 与 Workspace route hardening 可以分开写，体现连续参与
- Context/Memory foundation 与后续 readback/review hardening 可在必要时拆成两条
- 保留 GraphRAG 质量闭环及最有区分度的数字
- 可以补一条工程化/测试/架构判断，但不得把 Target Architecture 冒充个人已实现
- Red 继续 BLOCKED；修订后的简历重新交 USER_RESUME_REVIEW

## UF-006 — Raise writing quality; avoid suspicious perfect metrics

when: 2026-09-14T09:25:00+08:00
priority: highest
affected_stage: USER_RESUME_REVIEW / RESUME_REVISION
text: 六条版本的方向比四条好，但整体简历质量还需要更高。GraphRAG 直接写 Recall@5 0.80→1.00 在只有 5 条 smoke 的背景下，一眼容易像人为挑样本或包装 100% 指标，即使数据真实也不适合作为简历 headline。
required_change:
- GraphRAG 不再把 1.00 / 100% 作为简历卖点；明确小样本研发 smoke，并改写为“定位并修复 regression，使样本恢复到 baseline 水平”
- 每条 bullet 同时做到贡献对象清楚、动作有力度、技术信息有区分度、结果可信
- 用工程结果和问题闭环替代术语堆叠
- 有个人实现证据时使用主动动词，不机械写“参与”
- 不增加无法证明的业务收益、性能数字或 Production Claim
- Red / Blue 继续 BLOCKED，revision 3 重新交 USER_RESUME_REVIEW
