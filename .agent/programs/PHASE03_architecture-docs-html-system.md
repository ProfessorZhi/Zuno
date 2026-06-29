# PHASE03 Architecture Docs And HTML System

Program: `zuno-eight-deliverables-full-realization-v1`
status: planned

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
