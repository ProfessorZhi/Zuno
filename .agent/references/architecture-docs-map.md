# Architecture Docs Map

## When To Use

当任务涉及 `docs/architecture/`、`.agent/architecture/`、`docs/modules/`、`architecture.html`、Mermaid 图、README 架构摘要、目标架构或文档同步时，先读本文件。

## Mental Model

```text
docs/architecture/
  README.md
  architecture.md
  architecture-views.md
  architecture.html
    -> only four canonical architecture files

docs/modules/
  -> eleven logical module implementation designs

docs/status/production-readiness.md
  -> Current, gaps, measurement and Future Optional

docs/decisions/
  -> ADR
docs/governance/
  -> ownership and documentation governance

.agent/architecture/
  -> four canonical architecture mirrors
.agent/modules/
  -> selected module mirrors
```

## Current Truth

- `docs/architecture/README.md`：架构入口、四文件边界和维护命令。
- `docs/architecture/architecture.md`：唯一重文字目标总架构。
- `docs/architecture/architecture-views.md`：4+1、Views & Beyond、Zuno Product Core 十类视图的 Mermaid 规范图源。
- `docs/architecture/architecture.html`：读取独立图源的原生 Mermaid visual atlas。
- `docs/modules/README.md`：十一逻辑模块入口。
- `docs/modules/06-agent-core-planning-control.md`：Agent Core V2 实施级设计。
- `docs/status/production-readiness.md`：Current、Short-term Closure Gap、Measurement Blocked、Completed、Future Optional。
- `docs/decisions/README.md`：正式 ADR 入口。
- `docs/governance/repo-ownership-matrix.md`：Repository ownership 和迁移边界。
- `.agent/architecture/architecture.md`、`.agent/architecture/architecture-views.md` 与 `.agent/architecture/architecture.html`：总架构镜像。
- `.agent/modules/06-agent-core-planning-control.md`：Agent Core 模块镜像。

## Directory Contract

以下两个目录都只能有四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

```text
docs/architecture/
.agent/architecture/
```

模块专题、状态报告、ADR、Program、ownership matrix 和实施计划不得进入 architecture 目录。

## Presentation Page

HTML 固定展示十类 canonical views：

1. Logical View (4+1)
2. Development View (4+1)
3. Process View (4+1)
4. Physical View (4+1)
5. Scenarios View (4+1)
6. Module View (Views & Beyond)
7. Component-and-Connector View (Views & Beyond)
8. Data View (Views & Beyond)
9. Quality View (Views & Beyond)
10. Agentic GraphRAG Evidence and Agent Loop (Zuno)

每类必须有一张 Overall 图和至少两张 Local 图。HTML 支持导航、筛选、横向滚动、全屏和 Mermaid source 展开。

## Sync Rule

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

`--write` 负责验证三份正式源并同步：

- `architecture.md` -> `.agent/architecture/architecture.md`
- `architecture-views.md` -> `.agent/architecture/architecture-views.md`
- `architecture.html` -> `.agent/architecture/architecture.html`

Agent Core 模块文档单独同步：

```text
docs/modules/06-agent-core-planning-control.md
.agent/modules/06-agent-core-planning-control.md
```

HTML 仍使用 `/docs/architecture/architecture-views.md` 作为运行时 Mermaid 图源。

## Must Preserve

- Markdown 是重文字架构设计，HTML 是重图展示。
- `architecture.md` 保留少量关键辅助图，不堆放全部详细图。
- `architecture-views.md` 保留十类、至少三十张 Mermaid 图。
- Current 与 Target 分离。
- RabbitMQ、LangSmith、外部数据库和 sandbox 使用可替换 Adapter 表达，不成为近期强依赖。
- `.agent` 三份总架构镜像与正式文件完全一致。
- Agent Core 模块镜像与正式模块文档完全一致。

## Forbidden Changes

- 不在 architecture 目录新增第五个文件或任何子目录。
- 不把模块设计重新塞回 `architecture.md` 所在目录。
- 不把十类图重新塞回 `architecture.md`。
- 不让 HTML 再次读取文字总架构作为图源。
- 不恢复简化 offline SVG renderer。
- 不恢复拆分的 current/target/roadmap 前台文档。
- 不把 Future Optional 写成 Current。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```
