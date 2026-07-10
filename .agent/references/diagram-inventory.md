# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构图、Mermaid 源、`architecture.html` 展示页或图对应解释时，使用本清单。

## Current Truth

Zuno 前台架构展示固定为十张 canonical Mermaid 图。十图密度用于架构讲解、答辩和后续实施规划，但内容仍围绕 Lean Complete Agentic GraphRAG Product，不恢复旧大规模企业平台主叙事。

| # | Diagram | Focus | Source | HTML |
| --- | --- | --- | --- | --- |
| 1 | Lean System Overview | 六个运行域、owner 边界和依赖关系 | `docs/architecture/architecture.md` | yes |
| 2 | Golden Path Runtime | 配置模型到 restart recovery 的产品黄金链路 | `docs/architecture/architecture.md` | yes |
| 3 | Agentic GraphRAG and Agent Loop | standard/deep/agentic、EvidenceBundle、claim binding、reflection/replan、release gate | `docs/architecture/architecture.md` | yes |
| 4 | Product and API Surface | AgentChat、Workspace、Knowledge Space、DTO、SSE、Citation UI、Trace summary 与后端事实源 | `docs/architecture/architecture.md` | yes |
| 5 | Input and Knowledge Pipeline | SourceObject、ParseJob、Document IR、SourceSpan、CitationChunk、IndexManifest、CitationLineage、EvidenceBundle | `docs/architecture/architecture.md` | yes |
| 6 | Agent Core Control Loop | Model Gateway、ContextPack、Memory、StrategySelector、PlannerOutput、Observation、Reflection、Memory Commit | `docs/architecture/architecture.md` | yes |
| 7 | Agentic GraphRAG Evidence Flow | query planning、BM25/vector/graph、fusion/rerank、EvidenceBundle、claim binding、failure buckets、release gate | `docs/architecture/architecture.md` | yes |
| 8 | Capability and Tool Control Plane | SkillCard、CapabilityRouter、Policy/Approval、CredentialRef、ExecutionAdapter、ResultNormalizer、ToolTrace | `docs/architecture/architecture.md` | yes |
| 9 | Governance Observability and Release Gate | gates、ZunoSpan tree、usage/cost、failure buckets、EvalRun、Release Gate | `docs/architecture/architecture.md` | yes |
| 10 | Local Deployment and State | Web、FastAPI、SQLite、LocalObjectStore、LocalQueue、LocalIndex、Model Provider、TraceStore 和 future adapters | `docs/architecture/architecture.md` | yes |

十张图是架构图谱，不替代 `architecture.md` 的详细实施蓝图。`architecture.md` 仍负责 owner、contract、配置、状态、失败、trace、测试和验收矩阵；HTML 渲染十张 canonical 图。

## Must Preserve

- 图名必须和 `tools/agent/render_architecture.py` 的 `EXPECTED_DIAGRAMS` 一致。
- Mermaid 源只维护在 `docs/architecture/architecture.md`。
- `.agent/architecture/architecture.md` 必须由 renderer 同步。
- 两份 HTML 必须由同一个 Markdown 源生成。
- HTML 必须保留 Mermaid strict security、fullscreen dialog 和 responsive rendering。
- 不恢复旧十图硬约束，不以前台标题突出旧理论视图。

## Update Triggers

- Lean System Overview：六个运行域、owner、主要依赖或治理边界变化。
- Golden Path Runtime：用户产品链路、状态持久化、trace/cost/eval、recovery 变化。
- Agentic GraphRAG and Agent Loop：strategy、RetrievalPlan、Graph expansion、EvidenceBundle、claim binding、reflection/replan、abstain 或 quality gate 变化。
- Product and API Surface：AgentChat、Workspace、DTO、SSE、Citation UI、trace summary 或后端事实源变化。
- Input and Knowledge Pipeline：SourceObject、ParseJob、IR、SourceSpan、CitationChunk、IndexManifest 或 EvidenceBundle 变化。
- Agent Core Control Loop：Model Gateway、ContextPack、Memory、PlannerOutput、Observation、Reflection 或 Memory Commit 变化。
- Agentic GraphRAG Evidence Flow：retrieval plan、BM25/vector/graph、fusion/rerank、claim binding、failure bucket 或 release gate 变化。
- Capability and Tool Control Plane：Skill/Capability/Tool、approval、credential ref、adapter、normalizer 或 ToolTrace 变化。
- Governance Observability and Release Gate：gates、trace tree、usage/cost、EvalRun、blocked/measured 语义或 release threshold 变化。
- Local Deployment and State：本地存储、queue、index、trace store、model provider、config 或 optional adapter 边界变化。

## Before Editing

1. 修改 `docs/architecture/architecture.md`。
2. 如需新增或重命名图，先更新本文件、`EXPECTED_DIAGRAMS`、verifier 和 tests。
3. 运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Forbidden Changes

- 不手写生成 HTML 的 Mermaid 卡片。
- 不让图标题在 docs、inventory、生成器和 tests 之间漂移。
- 不把 HTML 图谱当成完整实施蓝图。
- 不把 Future Optional 画成近期必做基础设施。

## Debug Playbooks

- 标题缺失：查 `EXPECTED_DIAGRAMS`。
- 样式失败：确认 Mermaid 块包含 `#f7f8fb`、`#ffffff`、`#b8c2cc`、`#16202a`、`#52616f`。
- HTML 漂移：运行 `python tools/agent/render_architecture.py --write`。

## Lessons Learned

图是项目介绍和答辩入口，不是架构细节的唯一载体。详细 contract 和验收标准必须留在 Markdown。
