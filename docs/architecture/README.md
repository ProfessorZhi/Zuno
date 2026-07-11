# 架构文档

`docs/architecture/` 是 Zuno 的正式架构文档入口。

## 当前事实源

- `architecture.md`：目标架构唯一规范事实源。它定义十一逻辑能力模块、六个物理运行域，以及 4+1、Views & Beyond、Zuno Product Core 三组十类 canonical views。每类视图包含 Overall Mermaid 图和 Local Mermaid 图。
- `architecture.html`：原生 Mermaid Architecture Atlas。页面运行时读取同目录的 `architecture.md`，保留 subgraph、decision、edge label、sequence diagram、连线类型和全屏查看，不再使用简化离线 SVG parser。
- `production-readiness.md`：只维护 Current、Short-term Closure Gap、Measurement Blocked、Completed 和 Future Optional。

`architecture.md` 描述 Target；`production-readiness.md` 描述 Current。不得把目标图中的能力直接写成当前已实现事实。

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

专题文档保留技术细节，但必须服从十一逻辑模块、六个物理运行域和 `architecture.md` 的边界。

## 更新与验证

修改 `architecture.md` 或 Architecture Atlas shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

生成器负责：

- 验证十类 canonical views 全部存在；
- 验证每类都有 Overall 和 Local 图；
- 验证至少存在 30 张 Mermaid 图；
- 验证核心 connector contract 已标注；
- 同步 `.agent/architecture/architecture.md`；
- 同步 `.agent/architecture/architecture.html`。

## HTML 预览

HTML 会通过 `fetch("architecture.md")` 读取 Markdown，因此不能直接用 `file://` 双击预览。在仓库根目录运行：

```powershell
python -m http.server 8000
```

然后在浏览器打开：

```text
http://localhost:8000/docs/architecture/architecture.html
```

当前页面从固定 major 版本的 jsDelivr 路径加载 Mermaid v11，需要可访问网络。未来如需完全离线，可将同版本 Mermaid ESM 固定到仓库 vendor 目录，但不得恢复简化 SVG renderer。

## 历史入口

- 公开证据入口：`../evidence/public-demo.md`
- 旧架构清理工作集：`docs/history/architecture-surface-cleanup-2026-06-30/`
- 旧 split docs 架构入口：`docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/`
- 过时审计、旧规格、旧 phase、旧计划和旧 runbook 只保存在 `docs/history/`，不得重新作为当前入口。
