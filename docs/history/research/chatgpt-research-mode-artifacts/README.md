# ChatGPT Research Mode Artifacts

这里归档用户提供或生成的高质量 ChatGPT 研究模式产物，主要是 Zuno 架构、产品定位、实施蓝图和工程治理相关的深度分析报告。

## 边界

- 本目录是研究输入归档，不是当前架构事实源。
- 当前架构事实源仍是 `docs/architecture/architecture.md`。
- 架构 HTML 展示仍由 `docs/architecture/architecture.md` 通过 `tools/agent/render_architecture.py` 生成。
- PDF 原件作为证据保留；同名 Markdown 是文本抽取版，便于后续检索、对比和吸收。
- 从本目录吸收结论时，必须重新区分 Current、Target、Future 和 History，不能把研究报告里的目标描述直接写成当前事实。

## 当前文件

- `zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf`：Zuno 企业私有知识 Agent Workspace 目标架构研究报告原件。
- `zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md`：同名 PDF 的文本抽取版。
- `zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`：Zuno 目标架构深度研究与实施蓝图原件，是当前架构详细度基准输入。
- `zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md`：同名报告的可检索 Markdown 版。

## 使用规则

后续更新架构文档或执行计划时，优先把本目录作为 research input，正式结论必须进入：

- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `.agent/programs/implementation-roadmap.md`
- 相关 verifier / tests
