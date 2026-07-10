# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构视图类别、Mermaid 子图、`architecture.html` 展示页或图对应解释时，使用本清单。

## Current Truth

Zuno 前台架构展示固定为十类 canonical view categories。十类图不是十张平铺图片；每一类 view category 可以包含一个主图和若干局部展开图，例如 Logical View 可以同时包含系统逻辑图和 Memory Context 子系统图。

当前十类视图由两个通用架构视角和一个 Zuno 专题视角组成：

```text
4+1 View Model 五类
+ Views & Beyond 四类
+ Zuno Agentic GraphRAG 专题一类
= 十类视图
```

| # | View category | Theory lens | Typical subdiagrams | Source | HTML |
| --- | --- | --- | --- | --- | --- |
| 1 | Logical View (4+1) | 4+1 Logical | system logical structure; Memory Context subsystem | `docs/architecture/architecture.md` | yes |
| 2 | Development View (4+1) | 4+1 Development | code ownership and repo organization | `docs/architecture/architecture.md` | yes |
| 3 | Process View (4+1) | 4+1 Process | controller runtime process | `docs/architecture/architecture.md` | yes |
| 4 | Physical View (4+1) | 4+1 Physical | local deployment and state | `docs/architecture/architecture.md` | yes |
| 5 | Scenarios View (4+1) | 4+1 Scenarios | golden product scenario | `docs/architecture/architecture.md` | yes |
| 6 | Module View (Views & Beyond) | V&B Module | product/API module; six runtime domains | `docs/architecture/architecture.md` | yes |
| 7 | Component-and-Connector View (Views & Beyond) | V&B C&C | evidence connector; Tool Control connector | `docs/architecture/architecture.md` | yes |
| 8 | Data View (Views & Beyond) | V&B Data / Information | source object to evidence bundle lineage | `docs/architecture/architecture.md` | yes |
| 9 | Quality View (Views & Beyond) | V&B Quality | governance, observability and release gate | `docs/architecture/architecture.md` | yes |
| 10 | Agentic GraphRAG Evidence and Agent Loop (Zuno) | Zuno Product Core | agentic strategy loop and evidence-span citation loop | `docs/architecture/architecture.md` | yes |

HTML 是十类视图的 visual atlas，不替代 `architecture.md` 的详细实施蓝图。`architecture.md` 仍负责 owner、contract、配置、状态、失败、trace、测试和验收矩阵。

## Must Preserve

- 顶层 view category 名必须和 `tools/agent/render_architecture.py` 的 `EXPECTED_DIAGRAMS` 一致。
- Mermaid 源只维护在 `docs/architecture/architecture.md`。
- 每个 view category 至少有一个 Mermaid 子图。
- 关键复杂类别允许多个子图，HTML 必须能渲染多个 `.diagram-card`。
- `.agent/architecture/architecture.md` 必须由 renderer 同步。
- 两份 HTML 必须由同一个 Markdown 源生成。
- HTML 必须保留 Mermaid strict security、fullscreen dialog 和 responsive rendering。
- 不把 Views & Beyond 或 4+1 写成大规模企业平台目标；它们只是讲解视角。

## Update Triggers

- Logical View：运行域、核心概念、Memory/Tool/Knowledge 等逻辑关系变化。
- Development View：代码 owner、repo 目录、docs / tools / tests 组织变化。
- Process View：AgentChat request、ContextPack、planner、retrieval、tool、citation、trace 执行过程变化。
- Physical View：本地部署、SQLite、ObjectStore、Queue、Index、TraceStore、Model Provider 或 optional adapter 变化。
- Scenarios View：黄金产品链路、用户流程、状态恢复和 feedback 变化。
- Module View：六运行域拆分、Product/API、Knowledge、Agent Core、Capability、Governance、Infrastructure 模块边界变化。
- Component-and-Connector View：runtime connector、retrieval connector、tool connector、trace connector 变化。
- Data View：SourceObject、Document IR、Chunk、Index、CitationLineage、EvidenceBundle、TraceSpan 等数据关系变化。
- Quality View：correctness、citation、security、observability、recoverability、cost、release gate 变化。
- Zuno 专题视图：Agentic GraphRAG、evidence-span、claim binding、reflection/replan、fixed benchmark gate 变化。

## Before Editing

1. 修改 `docs/architecture/architecture.md`。
2. 如需新增或重命名 view category，先更新本文件、`EXPECTED_DIAGRAMS`、verifier 和 tests。
3. 如只在某类下新增子图，更新 Markdown 后运行 renderer 和 focused tests。
4. 运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Forbidden Changes

- 不手写生成 HTML 的 Mermaid 卡片。
- 不让 view category 标题在 docs、inventory、生成器和 tests 之间漂移。
- 不把 HTML 图谱当成完整实施蓝图。
- 不把 Future Optional 画成近期必做基础设施。

## Debug Playbooks

- 顶层类别缺失：查 `EXPECTED_DIAGRAMS`。
- 子图样式失败：确认 Mermaid 块包含 `#f7f8fb`、`#ffffff`、`#b8c2cc`、`#16202a`、`#52616f`。
- HTML 漂移：运行 `python tools/agent/render_architecture.py --write`。

## Lessons Learned

十类图的重点是“分类视角”，不是凑十张图片。图是讲解和答辩入口；详细 contract 和验收标准必须留在 Markdown。
