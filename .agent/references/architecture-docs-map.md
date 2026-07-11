# Architecture Docs Map

## When To Use

当任务涉及 `docs/architecture/`、`.agent/architecture/`、`architecture.html`、Mermaid 图、README 架构摘要、目标架构或文档同步时，先读本文件。

## Mental Model

```text
docs/architecture/architecture.md
  -> human-facing formal target architecture
  -> text-first design document
  -> a few supporting Mermaid diagrams

docs/architecture/architecture-views.md
  -> ten canonical view categories
  -> thirty native Mermaid diagrams

docs/architecture/architecture.html
  -> diagram-first visual atlas
  -> loads architecture-views.md at runtime
docs/architecture/production-readiness.md
  -> Current, gaps, measurement and Future Optional

.agent/architecture/architecture.md
  -> byte-for-byte text design mirror
.agent/architecture/architecture-views.md
  -> byte-for-byte Mermaid source mirror
.agent/architecture/architecture.html
  -> byte-for-byte visual shell mirror
```

## Current Truth

- `docs/architecture/README.md`：架构入口、文件职责和维护命令。
- `docs/architecture/architecture.md`：唯一重文字目标总架构。必须解释轻量实现、成熟设计、十一模块、Agent 闭环、Memory、Planning、Tool/MCP/Skill、Agentic GraphRAG、Security、Observability、Infrastructure、contract、失败语义和验收。
- `docs/architecture/architecture-views.md`：4+1、Views & Beyond、Zuno Product Core 十类视图的 Mermaid 规范图源。
- `docs/architecture/architecture.html`：读取独立图源的原生 Mermaid visual atlas。
- `docs/architecture/production-readiness.md`：Current、Short-term Closure Gap、Measurement Blocked、Completed、Future Optional。
- 稳定专题文档：Document Ingestion、Agent Core、Memory、Capability/Tool、Agentic Retrieval、Eval/Observability、Input 和 Knowledge Space。
- `.agent/architecture/architecture.md`、`.agent/architecture/architecture-views.md` 与 `.agent/architecture/architecture.html`：Agent 侧镜像，不是独立事实源。

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

HTML 仍使用 `/docs/architecture/architecture-views.md` 作为运行时 Mermaid 图源；`.agent` 中的副本只用于 Agent 工作区一致性和离线审阅。

## Must Preserve

- Markdown 是重文字架构设计，HTML 是重图展示。
- `architecture.md` 保留 2–8 张关键辅助图，不堆放 30 张详细图。
- `architecture-views.md` 保留十类、至少三十张 Mermaid 图。
- Current 与 Target 分离。
- RabbitMQ、LangSmith、外部数据库和 sandbox 使用可替换 adapter 表达，不成为近期强依赖。
- `.agent` 三份镜像与正式文件完全一致。

## Forbidden Changes

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
