# User Feedback — rb-2026-09-13-resume-first-014

## UF-001 — GitHub-mediated single-chat workflow

when: 2026-09-13T16:05:00+08:00
affected_stage: ROUND_INIT / ALL
priority: highest
text: CHATGPT 单对话工作流必须自洽，全程通过 GitHub 过程交互；不能只在同一聊天里切角色后把 GitHub 当事后存档。
resolution_before_round: PR #225 merged at main 10869d9176d2ef34b46577478bba62d9e254158a; Round #014 uses GitHub branch / Draft PR / commit-then-reread handoffs.

## UF-002 — Previous Red quality was not acceptable

when: 2026-09-13T16:05:00+08:00
affected_stage: RED_QUESTIONS / WORKFLOW_RETROSPECTIVE
priority: highest
text: 上一版 Red 在用户看来不合格。问题不能像知道 Zuno 文档答案以后反推出来的 Architecture Reviewer checklist；需要使用此前从用户真实面试和公开面经中提炼的 Red attack skill，强调精品思维、全链路追踪、不重复造轮子、Implementation / Fundamentals 深挖，并让 Red 自己接受质量审判。
quality_signals_requested:
- 不为凑 100 问制造重复题
- 从简历 Claim 出发，而不是从 Zuno 内部模块名出发
- 业务背景 → baseline → failure → implementation → concurrency/recovery → evidence → fundamentals → delete condition
- 固定攻击 Build / Buy / Extend / Defer
- 项目自然下钻 Python / DB / network / Agent/RAG 基础
- Workflow Retrospective 必须能判 Red skill / persona / question budget 有问题
resolution_in_round_014: Red uses frozen simulated resume + attack-model as formal inputs and generated five claim-grounded attack chains with implementation/fundamentals pressure. Final quality verdict remains for 06_workflow_retrospective.md.
