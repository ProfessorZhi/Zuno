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
