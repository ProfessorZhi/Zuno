# 架构文档

`docs/architecture/` 是 Zuno 的正式架构文档入口。

## 当前事实源

- `architecture.md`：**重文字的目标总架构设计文档**。它解释项目定位、轻量实现与成熟设计原则、十一逻辑模块、完整 Agent 闭环、typed contract、状态、失败语义和完成标准，只保留少量关键 Mermaid 图辅助理解。
- `architecture-views.md`：**十类 canonical views 的 Mermaid 规范图源**。包含 4+1、Views & Beyond 和 Zuno Product Core 三组十类视图，每类一张 Overall 图和至少两张 Local 图。
- `architecture.html`：**以 Mermaid 图为主的 Architecture Atlas**。页面运行时读取 `/docs/architecture/architecture-views.md`，保留 decision、sequence、edge label、循环、搜索和全屏查看。
- `production-readiness.md`：只维护 Current、Short-term Closure Gap、Measurement Blocked、Completed 和 Future Optional。

职责边界：

```text
architecture.md        讲设计
architecture-views.md  维护图源
architecture.html      看图
production-readiness   讲当前事实
```

不得把目标文档或目标图中的能力直接写成当前已经实现。

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

`agent-core-runtime.md` 是 Agent Core V2 的实施级专题规范，包含 LangGraph 双层图、Plan DAG、默认安全并行、Domain/Contract/ORM 分层、PostgreSQL 精确表结构和 Alembic Migration 计划。它在 `.agent/architecture/agent-core-runtime.md` 保留字节级镜像；正式事实源始终是 `docs/architecture/agent-core-runtime.md`。

## 更新与验证

修改 `architecture.md`、`architecture-views.md` 或 HTML shell 后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

生成器负责：

- 验证 `architecture.md` 的十一模块文字设计、轻量实现边界和核心 contract 完整；
- 限制 `architecture.md` 只保留少量辅助 Mermaid 图；
- 验证 `architecture-views.md` 的十类 canonical views 全部存在；
- 验证每类有 Overall 和至少两张 Local 图；
- 验证至少存在 30 张 Mermaid 图；
- 验证 HTML 读取独立图源并使用 Mermaid v11；
- 同步 `.agent/architecture/architecture.md`；
- 同步 `.agent/architecture/architecture-views.md`；
- 同步 `.agent/architecture/architecture.html`。

专题镜像当前需要在同一变更中显式同步：

```text
docs/architecture/agent-core-runtime.md
.agent/architecture/agent-core-runtime.md
```

两份文件必须保持字节级一致。

## HTML 预览

HTML 会通过 HTTP 读取 `/docs/architecture/architecture-views.md`，不能直接用 `file://` 双击预览。在仓库根目录运行：

```powershell
python -m http.server 8000
```

浏览器打开：

```text
http://localhost:8000/docs/architecture/architecture.html
```

当前页面从固定 major 版本的 jsDelivr 路径加载 Mermaid v11，需要可访问网络。未来如需完全离线，可将同版本 Mermaid ESM 固定到仓库 vendor 目录，但不得恢复简化 SVG renderer。

## 历史入口

- 公开证据入口：`../evidence/public-demo.md`
- 旧架构清理工作集：`docs/history/architecture-surface-cleanup-2026-06-30/`
- 旧 split docs 架构入口：`docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/`
- 过时审计、旧规格、旧 phase、旧计划和旧 runbook 只保存在 `docs/history/`，不得重新作为当前入口。