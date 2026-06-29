# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构视图、Mermaid 源、`architecture.html` 展示页或图对应的架构解释时，使用本清单。

## Mental Model

```text
docs/architecture.md
  -> ten architecture view source blocks
tools/agent/render_architecture.py
  -> validates EXPECTED_DIAGRAMS and renders HTML
docs/architecture.html
  -> generated presentation page
```

## Current Truth

Zuno 当前固定登记十类架构视图。十类图不是十张装饰图，而是十个不同架构关注面：

```text
4+1 View Model 五类图
+ View & Beyond 四类图
+ Zuno Agent Loop 专题图
= 十类图
```

Agent Loop 在理论上可以归入 Process View 或 Component-and-Connector View，但它是 Zuno Agentic RAG 内核的放大图，因此单独作为第十类专题视图维护。

| # | Diagram | Type | Theory Scope | Source docs | HTML |
| --- | --- | --- | --- | --- | --- |
| 1 | Logical View | 4+1 Logical | 核心职责和领域层次 | `docs/architecture.md` | yes |
| 2 | Development View | 4+1 Development | 代码、文档和工作流组织 | `docs/architecture.md` | yes |
| 3 | Process View | 4+1 Process | 运行时控制流、事件流和外部调用 | `docs/architecture.md` | yes |
| 4 | Physical View | 4+1 Physical | 本地优先部署和外部依赖节点 | `docs/architecture.md` | yes |
| 5 | Scenarios View | 4+1 Scenarios | Query-to-answer 场景贯通 | `docs/architecture.md` | yes |
| 6 | V&B Logical View | View & Beyond Logical | 领域子系统和核心概念 | `docs/architecture.md` | yes |
| 7 | Component-and-Connector View | View & Beyond C&C | 运行时组件连接和通信 | `docs/architecture.md` | yes |
| 8 | V&B Deployment View | View & Beyond Deployment | 可替换部署资源和 provider 边界 | `docs/architecture.md` | yes |
| 9 | Quality View | View & Beyond Quality | 质量属性和治理机制 | `docs/architecture.md` | yes |
| 10 | Agent Loop View | Zuno 专题图 | Plan / Act / Observe / Reflect / Replan | `docs/architecture.md` | yes |

## Update Triggers

- Logical View：职责分层、Agent Runtime、Memory、Capability、Knowledge、Evidence、Platform 边界变化。
- Development View：repo 目录、backend 六层、docs / `.agent` 边界、tools / tests 组织变化。
- Process View：API、application service、Agent runtime、工具调用、检索、LLM 调用、事件流、trace 关系变化。
- Physical View：本地部署、FastAPI、Web/Desktop、数据库、向量库、图存储、LLM/MCP 外部依赖变化。
- Scenarios View：product mode、Context Builder、Basic / Enhanced / Auto、Evidence Check、Citation、Trace 流程变化。
- V&B Logical View：Runtime、Memory、Tool、Retrieval、Evidence 等领域子系统变化。
- Component-and-Connector View：API、Controller Agent、Memory Manager、Tool Registry、Retrieval Router、Evidence Checker、Citation Builder、Trace Logger 连接变化。
- V&B Deployment View：Local Storage、SQL、Vector Store、Graph Store、Model Gateway、Search、MCP provider 变化。
- Quality View：performance、reliability、security、observability、modifiability、evaluation、resilience、governance gate 变化。
- Agent Loop View：Plan、Act、Observation、Working Memory、Reflection、Replan、Final Answer 循环变化。

## Target Direction

README 首页只给出精简入口。完整十类视图保留在 `docs/architecture.md` 和 `docs/architecture.html`。

## Must Preserve

- 图名必须和 `tools/agent/render_architecture.py` 的 `EXPECTED_DIAGRAMS` 一致。
- Mermaid 源只维护在 `docs/architecture.md`。
- HTML 生成后必须保持 `python tools/agent/render_architecture.py --check` 通过。
- 不把理论映射图当成架构本体图。
- 不把 Agent Loop 误写成整个 Process View；它是 Process / C&C 的子系统放大图。

## Before Editing

1. 修改 `docs/architecture.md`。
2. 如需新增或重命名视图，先更新本文件和 `EXPECTED_DIAGRAMS`。
3. 运行 `python tools/agent/render_architecture.py --write`。
4. 运行 verifier 和相关 tests。

## Allowed Changes

- 修改图解释、Mermaid 源、映射表和更新触发条件。

## Forbidden Changes

- 不要手写生成 HTML 的 Mermaid 卡片。
- 不要让图标题在 docs、inventory、生成器之间漂移。
- 不要把十类视图退化成十张重复角度的展示图。

## Common Failure Patterns

- 图源改了但 HTML 没重新生成。
- HTML 更新了但 `docs/architecture.md` 没变。
- 新模式写进图但没写进 `target-architecture.md`。
- 为了凑数量把理论映射图算成架构图。

## Debug Playbooks

- 标题缺失：查 `EXPECTED_DIAGRAMS`。
- 样式失败：确认 Mermaid 块包含 `#f7f8fb`、`#ffffff`、`#b8c2cc`、`#16202a`、`#52616f`。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `docs/architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/deliverables.md`
- `tools/agent/render_architecture.py`

## Lessons Learned

图是架构文档的入口，不是装饰。每类图都必须回答“它改变了读者的哪个判断”。
