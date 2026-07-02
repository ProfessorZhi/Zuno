# Architecture Docs Map

## When To Use

当任务涉及 `docs/architecture/`、`.agent/architecture/`、`architecture.html`、Mermaid 图、README 架构摘要、目标架构或文档同步时，先读本文件。

## Mental Model

```text
docs/architecture/architecture.md
  -> human-facing formal architecture source
  -> rich text architecture design
  -> Mermaid source of truth

docs/architecture/architecture.html
  -> generated human-facing visual page

docs/architecture/<stable-topic>.md
  -> PHASE14 stable topic pages
  -> Current / Target boundaries and evidence paths only

.agent/architecture/architecture.md
  -> byte-for-byte Agent-facing Markdown mirror

.agent/architecture/architecture.html
  -> generated Agent-facing visual mirror

.agent/references/
  -> Agent-facing governance, maps, policies and inventories
```

## Current Truth

- `docs/architecture/README.md`：架构文档入口、阅读顺序、归档边界和维护规则。
- `docs/architecture/architecture.md`：唯一总架构 Markdown。正文必须比 HTML 更充实，说明 Current / Target / Future / History、企业私有知识库主叙事、运行时分层、Document Ingestion、Memory、Tool Control Plane、RAG / GraphRAG、安全、评测和实施落点；同一文件后半维护十类 Mermaid 图。
- `docs/architecture/document-ingestion-foundation.md`：企业知识库文档入口正式补充契约，集中说明 workspace file、ParseGateway、Document IR、parser job lifecycle、index handoff、幂等、版本、防丢、ACL、citation lineage 和 OCR / VLM enrichment 边界。
- `docs/architecture/agent-core-runtime.md`、`capability-and-skill-layer.md`、`agentic-retrieval-planner.md`、`eval-observability-and-cost.md`、`input-layer-and-document-processing.md`、`knowledge-space-product-configuration.md`：PHASE14 稳定专题说明，只承载 Current / Target 边界和证据路径。
- `docs/architecture/architecture.html`：由 `tools/agent/render_architecture.py` 生成的图形化展示页。
- `.agent/architecture/architecture.md`：Agent 侧 Markdown 镜像，必须与 `docs/architecture/architecture.md` 完全一致。
- `.agent/architecture/architecture.html`：Agent 侧 HTML 镜像，必须与 `docs/architecture/architecture.html` 由同一 Markdown 源生成。
- `docs/architecture/assets/`：正式架构附件。
- `docs/architecture/decisions/`：仍影响主线的正式架构决策。
- `docs/history/architecture-surface-cleanup-2026-06-30/`：本轮瘦身归档，保存旧拆分架构文档和旧 Agent architecture 工作集。

## Presentation Page

`architecture.html` 是图为主的展示页，不是唯一事实来源。它展示十类架构视图：

- `Logical View`
- `Development View`
- `Process View`
- `Physical View`
- `Scenarios View`
- `V&B Logical View`
- `Component-and-Connector View`
- `V&B Deployment View`
- `Quality View`
- `Agent Loop View`

HTML 必须支持页面内查看和展开全屏查看；如果图比例或连线可读性调整，只改 `docs/architecture/architecture.md` 的 Mermaid 源和 `tools/agent/render_architecture.py` 的渲染规则，然后重新生成。

## Sync Rule

架构文件保持一致的唯一方式：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

`--write` 必须同步：

- `docs/architecture/architecture.md` -> `.agent/architecture/architecture.md`
- `docs/architecture/architecture.md` -> `docs/architecture/architecture.html`
- `docs/architecture/architecture.md` -> `.agent/architecture/architecture.html`

禁止手写 `.agent/architecture/architecture.md` 或任一 HTML 后不回写源文件。

## Must Preserve

- Markdown 是主文档，HTML 是展示页。
- `docs/architecture/architecture.md` 和 `.agent/architecture/architecture.md` 必须完全一致。
- 两个 `architecture.html` 必须由同一个 Markdown 源生成。
- `docs/architecture/` 只保留当前会影响决策的少量前台文件；PHASE14 专题文档允许存在，但不能变成 phase log。
- 文档入口的企业级细节进入 `docs/architecture/document-ingestion-foundation.md` 或 `input-layer-and-document-processing.md`，不要重新拆出 `docs/architecture/phases/`、`plans/`、`programs/` 或高频 roadmap。
- `.agent/architecture/` 只保留当前 Agent 维护架构所需的镜像文件。
- 高频变化的执行计划进入 `.agent/programs/`，不要塞回架构目录。

## Forbidden Changes

- 不要恢复 `current-architecture.md`、`target-architecture.md`、`roadmap.md`、`deliverables.md` 等拆分前台入口。
- 不要恢复旧 near-term / future / decisions 工作集到 `.agent/architecture/` 前台。
- 不要让 HTML 成为唯一事实来源。
- 不要只更新 `.agent/references/` 而不更新正式架构 Markdown。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```
