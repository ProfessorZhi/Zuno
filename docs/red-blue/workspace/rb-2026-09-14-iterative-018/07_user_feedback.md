# User Feedback — rb-2026-09-14-iterative-018

## UF-001 — Use the real resume register

when: 2026-09-14T15:32:00+08:00
priority: highest
affected_stage: ROUND_INIT / BUILD_RESUME
text: 继续以用户本人一页简历的项目标题、项目简介、技术栈、短 bullet 节奏为主要招聘语体参考；旧简历事实不自动继承，事实重新从当前 canonical Zuno sources 构建。

## UF-002 — Participation breadth must remain visible

when: 2026-09-14T15:32:00+08:00
priority: highest
affected_stage: BUILD_RESUME
text: 不要因为压缩字数把参与范围削成三四个孤立修补点。允许约 6 条高价值 bullet，但每条必须是独立技术故事，不能回到 Evidence memo 或模块清单。

## UF-003 — Avoid suspicious perfect metrics

when: 2026-09-14T15:32:00+08:00
priority: highest
affected_stage: BUILD_RESUME
text: GraphRAG 的 5-query development smoke 可以作为范围限定和 regression evidence，但不把 0.80→1.00 / 100% 当简历 headline；优先表达 regression、诊断、ranking invariant、修复与恢复 baseline 水平。

## UF-004 — Raise technical content

when: 2026-09-14T15:32:00+08:00
priority: highest
affected_stage: BUILD_RESUME
text: 简历要像用户收藏的优秀 Agent/RAG 简历那样，优先写“系统哪里出问题、做了什么技术决策、机制如何改变、结果如何验证”，而不是“用了 LangGraph/MCP/GraphRAG/Memory”。技术名词必须服务于问题和决策。

## UF-005 — Start the first full iterative round from the improved resume

when: 2026-09-14T15:32:00+08:00
priority: highest
affected_stage: ROUND_INIT / USER_RESUME_REVIEW
text: 用户要求重新检查简历、完善后作为第一轮起点。本轮定义为新 closed-loop workflow 的 Iteration 1（仓库序号 #018）。Resume 先进入 USER_RESUME_REVIEW；未明确 APPROVE 前禁止启动 Red。

## UF-006 — Resume approved; start Red

when: 2026-09-14T16:18:00+08:00
priority: highest
affected_stage: USER_RESUME_REVIEW / RED_QUESTIONS
text: 用户明确要求“然后开始红队进攻”，视为对当前 01_simulated_resume.md 的 APPROVE。冻结当前 Resume，进入 RED_QUESTIONS；仍保留 USER_RED_REVIEW，未审阅 Red Plan 前不运行 Blue。

## UF-007 — Current architecture is a baseline, not a protected answer

when: 2026-09-14T16:18:00+08:00
priority: highest
affected_stage: BLUE_REFLECTION / WORKFLOW_RETROSPECTIVE / IMPROVEMENT_SYNTHESIS
text: 本轮最终目的不是证明当前架构正确，而是通过 Red/Blue 压力完善架构。允许在证据支持时修改现有架构，包括采用 Multi-Agent、Supervisor/Specialist、Subgraph、通用 Agent Host + Zuno Backend 或其他结构；Multi-Agent 只是候选方案，不预设为正确答案。简单方案满足约束时继续尊重简单方案，所有新增复杂度必须说明出现原因、收益、成本、退出条件与复测方式。
