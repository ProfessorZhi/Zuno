# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构视图类别、Mermaid 子图、`architecture.html` 展示页或图对应解释时，使用本清单。

## Current Truth

Zuno 前台架构展示固定为十类 canonical view categories。十类图不是十张平铺图片；每一类包含一个 Overall Diagram 和至少两个 Local Diagram。

```text
4+1 View Model 五类
+ Views & Beyond 四类
+ Zuno Agentic GraphRAG 专题一类
= 十类视图
```

| # | View category | Theory lens | Typical subdiagrams | Mermaid source | HTML |
| --- | --- | --- | --- | --- | --- |
| 1 | Logical View (4+1) | 4+1 Logical | eleven modules; Memory/Context; Agent Core boundary | `docs/architecture/architecture-views.md` | yes |
| 2 | Development View (4+1) | 4+1 Development | repo ownership; runtime package; source generation | `docs/architecture/architecture-views.md` | yes |
| 3 | Process View (4+1) | 4+1 Process | LangGraph; single-step ReAct; approval/resume | `docs/architecture/architecture-views.md` | yes |
| 4 | Physical View (4+1) | 4+1 Physical | local deployment; recovery; model connectivity | `docs/architecture/architecture-views.md` | yes |
| 5 | Scenarios View (4+1) | 4+1 Scenarios | product lifecycle; document preparation; agent task | `docs/architecture/architecture-views.md` | yes |
| 6 | Module View (Views & Beyond) | V&B Module | eleven-to-six mapping; Agent Core; Knowledge | `docs/architecture/architecture-views.md` | yes |
| 7 | Component-and-Connector View (Views & Beyond) | V&B C&C | runtime contracts; model/memory; knowledge/tool | `docs/architecture/architecture-views.md` | yes |
| 8 | Data View (Views & Beyond) | V&B Data | authoritative data; citation lineage; runtime/memory lifecycle | `docs/architecture/architecture-views.md` | yes |
| 9 | Quality View (Views & Beyond) | V&B Quality | quality attributes; Security/Trace; release gate | `docs/architecture/architecture-views.md` | yes |
| 10 | Agentic GraphRAG Evidence and Agent Loop (Zuno) | Product Core | retrieval pipeline; corrective loop; claim binding | `docs/architecture/architecture-views.md` | yes |

`architecture.md` 是详细文字设计，不是十类图的主图源。`architecture.html` 是 visual atlas，不替代文字设计和 `production-readiness.md`。

## Must Preserve

- View category 名必须和 `tools/agent/render_architecture.py` 的 `EXPECTED_VIEWS` 一致。
- 详细 Mermaid 源只维护在 `docs/architecture/architecture-views.md`。
- 每类必须有一个 Overall 和至少两个 Local Mermaid 图。
- 图总数不得少于 30。
- `architecture.md` 只保留少量支持理解的关键图。
- HTML 必须支持 Mermaid v11、strict security、导航、筛选、全屏和 source disclosure。
- Security、Observability、Infrastructure 和核心 connector 必须有清晰连线标签。
- 4+1 和 Views & Beyond 是讲解视角，不代表大规模企业平台目标。

## Update Triggers

- Logical：十一模块、Memory/Tool/Knowledge/Core 关系变化。
- Development：代码 owner、repo 目录、source generation 变化。
- Process：LangGraph、ContextPack、Plan/ReAct/Reflection/Replan、approval/resume 变化。
- Physical：SQLite、Object Store、TaskQueuePort、RabbitMQ adapter、Index、Trace、Model Provider 变化。
- Scenarios：上传、解析、问答、工具审批、恢复和反馈变化。
- Module：十一逻辑模块与六物理域变化。
- Component-and-Connector：typed runtime contracts 变化。
- Data：SourceObject、DocumentIR、EvidenceLedger、GroundedAnswer、Memory、Trace 数据关系变化。
- Quality：Security、Observability、RAG metrics、token/cost、recovery、release gate 变化。
- Product Core：Agentic GraphRAG、corrective retrieval、claim binding、Reflection/Replan 变化。

## Before Editing

1. 设计含义变化时先更新 `docs/architecture/architecture.md`。
2. 图形关系变化时更新 `docs/architecture/architecture-views.md`。
3. 如新增或重命名 view category，同步更新本文件、renderer、verifier 和 tests。
4. 运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Forbidden Changes

- 不把详细图重新堆回 `architecture.md`。
- 不手写生成后的 SVG。
- 不让 view category 在 inventory、renderer、HTML 和 tests 之间漂移。
- 不把 HTML 图谱当成完整实施蓝图。
- 不把 Future Optional 画成近期强依赖。

## Debug Playbooks

- 顶层类别缺失：检查 `EXPECTED_VIEWS` 和 `architecture-views.md` 标题。
- Mermaid parse error：在浏览器控制台定位具体图，并检查 Mermaid v11 语法。
- HTML 读取失败：确认通过本地 HTTP 服务访问，并检查 `/docs/architecture/architecture-views.md`。
- HTML 或镜像漂移：运行 `python tools/agent/render_architecture.py --write`。

## Lessons Learned

图是讲解和答辩入口；完整模块职责、近期精简实现、成熟扩展边界、contract 和验收标准必须留在 `architecture.md`。
