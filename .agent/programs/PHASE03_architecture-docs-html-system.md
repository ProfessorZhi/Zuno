# PHASE03 Architecture Docs And HTML System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

架构文档和 HTML 展示页是外部读者理解 Zuno 的第一入口。它们必须共享一个正式来源，不能让 markdown、HTML、README、Agent references 各说各话。

## 范围

覆盖交付物：

- 4. 正式架构文档系统。
- 5. 架构 HTML 展示系统。
- 6. 完善的 Zuno 目标架构。
- 8. 一致性与验证系统。

主要文件：

- `docs/architecture.md`
- `docs/architecture.html`
- `docs/architecture/*`
- `docs/deliverables.md`
- `tools/agent/render_architecture.py`
- `.agent/references/architecture-*.md`
- `.agent/references/diagram-inventory.md`
- `README.md`

## 执行步骤

1. 审计正式架构来源：Current、Target、Future、History 是否混写。
2. 确认 `docs/architecture.md` 是 HTML 生成源，HTML 不成为第二套事实。
3. 补齐八交付物、RAG、GraphRAG、Agentic RAG、runtime contracts 和目录结构的图文对应关系。
4. 让 render 脚本和 verifier 校验 source / HTML 同步。
5. 做一次页面渲染或截图检查，确认展示页不是空白、图没有明显溢出。

## 验收

- `python tools/agent/render_architecture.py --check` 通过。
- `docs/architecture.md`、`docs/architecture.html`、`docs/architecture/target-architecture.md` 和 roadmap 对同一目标架构表述一致。
- 被删除的旧 HTML 入口不再被前台引用。
- README 能把读者导向正式架构入口。

## PR 边界

可以拆成 architecture source PR 和 HTML/render PR；最终必须保持同一事实源。

## Phase Summary

- Multi-agent: enabled in the main Codex goal-mode thread; Architecture / Docs、Runtime / Code、Verification、Integration Reviewer 工作组均已完成并关闭。
- Result: canonical ten-view contract 已在 renderer、docs、deliverables、diagram inventory、HTML、docs verifier 和 repo tests 中同步；`docs/architecture.html` 由 `docs/architecture.md` 精确生成校验。
- Current / Target / Future / History: 修正 current 文档中的目标图引用、README 目标角色命名、absorbed reference wording 和 future-only term guard，未把 Target/Future 写成 Current。
- Visual QA: Playwright smoke 通过 desktop/mobile 检查，10 个 Mermaid SVG 渲染、0 Mermaid error、0 document-level horizontal overflow；截图通过 Playwright 工具捕获，不在仓库保留临时产物。
- Runtime boundary: 未修改 runtime/API/DB/frontend/dependency；本 phase 只触碰 docs、renderer、verifier、repo tests 和 phase status surfaces。
- Validation: full base verifier stack、architecture render check、workflow verifier、repo tests and Playwright visual smoke passed before commit.
- PR: to be created as stacked PHASE03 PR after commit and push.
