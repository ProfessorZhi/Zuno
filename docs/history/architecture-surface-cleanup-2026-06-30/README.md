# Architecture Surface Cleanup 2026-06-30

本目录保存本轮架构前台瘦身时迁出的旧材料。

## 为什么归档

Zuno 现在已有两个当前主入口：

- `docs/architecture/overall-architecture.md`：文字总架构文档。
- `docs/architecture/architecture.html`：图形化架构展示页。

因此，原先分散在多个 Current / Target / Roadmap / Scenario / Security / Deliverables 文档中的内容被收敛到总架构文档和 HTML 中。旧材料保留为历史证据，不再作为当前前台。

## 内容

- `docs-architecture/`：原 `docs/architecture/` 下的拆分文档。
- `agent-architecture/`：原 `.agent/architecture/` 下的 near-term、future、decisions、glossary 和 index 工作集。

## 恢复规则

不要直接把本目录文件复制回前台。若确实需要恢复某个拆分文档，必须先打开新的文档重组 program，并同步：

- `AGENTS.md`
- `README.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/*`
- verifier / tests
