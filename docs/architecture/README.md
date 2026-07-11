# 架构文档

`docs/architecture/` 是 Zuno 的正式架构文档入口。

## 当前事实源

- `architecture.md`：详细、规范、可实施的产品与运行架构总事实源。它定义 Lean Complete Agentic GraphRAG Product、六个运行域、黄金链路、ownership、配置、状态、失败、trace、测试和完成标准。
- `architecture.html`：由 `architecture.md` 中十类 canonical view categories 和可展开 Mermaid 子图生成的架构图谱，不复制 Markdown 的全部技术细节。
- `production-readiness.md`：只维护 Current、Short-term Closure Gap、Measurement Blocked、Completed 和 Future Optional。

## 专题文档

- `document-ingestion-foundation.md`
- `agent-core-runtime.md`
- `memory-and-context.md`
- `capability-and-skill-layer.md`
- `agentic-retrieval-planner.md`
- `eval-observability-and-cost.md`
- `input-layer-and-document-processing.md`
- `knowledge-space-product-configuration.md`
- `repo-ownership-matrix.md`

专题文档保留技术细节，但必须服从六个运行域和 `architecture.md` 的边界。

## 生成规则

修改 `architecture.md` 中架构图后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

生成器同步：

- `docs/architecture/architecture.html`
- `.agent/architecture/architecture.md`
- `.agent/architecture/architecture.html`

不要手写 HTML 展示页，不恢复已归档的 split architecture docs。

## 历史入口

- 公开证据入口：`../evidence/public-demo.md`
- 旧架构清理工作集：`docs/history/architecture-surface-cleanup-2026-06-30/`
- 旧 split docs 架构入口：`docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/`
- 过时审计、旧规格、旧 phase、旧计划和旧 runbook 只保存在 `docs/history/`，不得重新作为当前入口。
