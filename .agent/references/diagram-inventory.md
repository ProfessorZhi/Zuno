# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构视图、Mermaid 源、`architecture.html` 展示页或图对应的架构解释时，使用本清单。

## Mental Model

```text
docs/architecture/architecture.md
  -> ten architecture view source blocks with second-level component detail
tools/agent/render_architecture.py
  -> validates EXPECTED_DIAGRAMS and renders HTML
docs/architecture/architecture.html
  -> generated presentation page
```

## Current Truth

Zuno 当前固定登记十类架构视图。十类图不是十张装饰图，也不是十张粗粒度模块示意图，而是十个不同架构关注面。每张图都应至少展开到二级组件，让读者能看出 Agent Core、Memory、Tool、Knowledge、Document Ingestion、Security、Trace / Eval 与 Platform 的连接关系。Memory 图层必须体现 write-manage-read：Raw Event Log、Recent Window、Task Summary、Structured Long-term Memory、Context Pack、PostTurn Pipeline、review / promotion / decay。Tool 图层必须体现 Tool Control Plane：Tool Manifest、ToolCard Registry、Capability Selector、Policy / Approval Gate、Executor Adapter、Sandbox、Result Normalizer、Tool Trace / Audit。

```text
4+1 View Model 五类图
+ View & Beyond 四类图
+ Zuno Agent Loop 专题图
= 十类图
```

Agent Loop 在理论上可以归入 Process View 或 Component-and-Connector View，但它是 Zuno Agentic RAG 内核的放大图，因此单独作为第十类专题视图维护。

| # | Diagram | Type | Theory Scope | Source docs | HTML |
| --- | --- | --- | --- | --- | --- |
| 1 | Logical View | 4+1 Logical | Model、Agent Core、Memory、Tool、Knowledge、Ingestion、Security、Eval、Platform 的职责分层；Memory 展开 Raw Event Log / Recent Window / Task Summary / Structured Memory / Context Pack；Tool 展开 Tool Control Plane | `docs/architecture/architecture.md` | yes |
| 2 | Development View | 4+1 Development | 代码、文档、`.agent` program、renderer、verifier 和 tests 如何组织 | `docs/architecture/architecture.md` | yes |
| 3 | Process View | 4+1 Process | API、Context、Agent Core、工具/检索、memory read/write、事件流和 eval trace 如何运行 | `docs/architecture/architecture.md` | yes |
| 4 | Physical View | 4+1 Physical | 本地优先部署、存储、模型、MCP、LangSmith / trace backend 和外部依赖节点 | `docs/architecture/architecture.md` | yes |
| 5 | Scenarios View | 4+1 Scenarios | 企业知识库从 upload / parse / index 到 answer / artifact，再到 memory candidate / review / durable memory 的场景贯通 | `docs/architecture/architecture.md` | yes |
| 6 | V&B Logical View | View & Beyond Logical | Runtime、Memory、Capability、Knowledge、Ingestion、Workspace、Policy 等领域子系统；Memory 是 write-manage-read 子系统，Tool 是 manifest-driven control plane | `docs/architecture/architecture.md` | yes |
| 7 | Component-and-Connector View | View & Beyond C&C | Planner、ReAct Executor、Memory Read Policy、Memory Stores、Memory Review Gate、Tool Manifest Registry、Capability Selector、Tool Policy Approval、Executor Adapter、Sandbox、Result Normalizer、Retrieval Router、Parse Gateway、Policy、Evidence、Trace 的连接 | `docs/architecture/architecture.md` | yes |
| 8 | V&B Deployment View | View & Beyond Deployment | SDK、API、CLI、SSH、MCP、Model、Search、Vector、Graph、Trace backend 的可替换 provider 边界 | `docs/architecture/architecture.md` | yes |
| 9 | Quality View | View & Beyond Quality | 输入、检索、工具、输出、安全、稳定性、观测、评测、成本和 release gate | `docs/architecture/architecture.md` | yes |
| 10 | Agent Loop View | Zuno 专题图 | prepare_context / memory read / plan / ReAct / observe / raw event append / reflect / replan / post_turn_commit / memory promotion | `docs/architecture/architecture.md` | yes |

## Update Triggers

- Logical View：职责分层、Model Gateway、Agent Runtime、Memory、Capability、Knowledge、Document Ingestion、Security、Trace / Eval、Platform 边界变化；Memory tier 或 write/read 责任变化；Tool Control Plane 责任变化。
- Development View：repo 目录、backend 六层、docs / `.agent` 边界、active program、renderer、verifier、tools / tests 组织变化。
- Process View：API、application service、Context Builder、Agent runtime、工具调用、检索、memory read/write、LLM 调用、事件流、trace / eval 关系变化。
- Physical View：本地部署、FastAPI、Web/Desktop、数据库、向量库、图存储、LLM/MCP、LangSmith / trace backend 外部依赖变化。
- Scenarios View：enterprise knowledge base、upload、parse、index、product mode、Context Builder、Basic / Enhanced / Auto、Evidence Check、Citation、Trace、memory candidate / review / promotion 流程变化。
- V&B Logical View：Runtime、Memory、Tool、Knowledge、Document Ingestion、Workspace、Policy 等领域子系统变化。
- Component-and-Connector View：API、Controller Agent、Planner、ReAct Executor、Memory Read Policy、Memory Stores、Memory Write Path、Memory Review Gate、Tool Manifest Registry、Capability Selector、Tool Policy Approval、Executor Adapter、Sandbox、Result Normalizer、Retrieval Router、Parse Gateway、Policy Guard、Evidence Checker、Citation Builder、Trace Logger 连接变化。
- V&B Deployment View：Local Storage、SQL、Vector Store、Graph Store、Model Gateway、Search、SDK/API/CLI/SSH/MCP provider、executor adapter、sandbox / approval boundary 变化。
- Quality View：performance、reliability、security、DLP、permission、observability、evaluation、cost、resilience、governance gate 变化。
- Agent Loop View：prepare_context、memory read、intent/router、Plan、ReAct、tool/retrieval dispatch、Observation、raw event append、Working Memory、Reflection、Replan、post_turn_commit、summary update、structured memory candidate / promotion 循环变化。

## Target Direction

README 首页只给出精简入口。完整十类视图保留在 `docs/architecture/architecture.md` 和 `docs/architecture/architecture.html`。后续如需要更多 exploded views，优先把它们折叠进十类视图的二级组件；只有当新的图回答了十类视图无法承载的独立架构问题时，才更新 `EXPECTED_DIAGRAMS`、本文件、`docs/architecture/architecture.md` 和 tests。

## Must Preserve

- 图名必须和 `tools/agent/render_architecture.py` 的 `EXPECTED_DIAGRAMS` 一致。
- Mermaid 源只维护在 `docs/architecture/architecture.md`。
- HTML 生成后必须保持 `python tools/agent/render_architecture.py --check` 通过。
- 不把理论映射图当成架构本体图。
- 不把 Agent Loop 误写成整个 Process View；它是 Process / C&C 的子系统放大图。
- 不把 `API / SDK / CLI / MCP` 写成 Capability 顶层业务分类；它们是 ToolCard execution adapter 或 provider metadata。

## Before Editing

1. 修改 `docs/architecture/architecture.md`。
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
- HTML 更新了但 `docs/architecture/architecture.md` 没变。
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

- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`
- `tools/agent/render_architecture.py`

## Lessons Learned

图是架构文档的入口，不是装饰。每类图都必须回答“它改变了读者的哪个判断”。
