# Diagram Inventory

## When To Use

当新增、重命名、删除或修改架构图、Mermaid 源、`architecture.html` 展示页或图对应解释时，使用本清单。

## Current Truth

Zuno 前台架构展示固定为四张 canonical Mermaid 图：

| # | Diagram | Focus | Source | HTML |
| --- | --- | --- | --- | --- |
| 1 | Lean System Overview | 六个运行域、owner 边界和依赖关系 | `docs/architecture/architecture.md` | yes |
| 2 | Golden Path Runtime | 配置模型到 restart recovery 的产品黄金链路 | `docs/architecture/architecture.md` | yes |
| 3 | Agentic GraphRAG and Agent Loop | standard/deep/agentic、EvidenceBundle、claim binding、reflection/replan、release gate | `docs/architecture/architecture.md` | yes |
| 4 | Local Deployment and State | Web、FastAPI、SQLite、LocalObjectStore、LocalQueue、LocalIndex、Model Provider、TraceStore 和 future adapters | `docs/architecture/architecture.md` | yes |

四张图是展示摘要，不替代 `architecture.md` 的详细实施蓝图。`architecture.md` 可以包含 owner、contract、配置、状态、失败、trace、测试和验收矩阵；HTML 只渲染这四张图。

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
- 不把 HTML 展示页当成完整实施蓝图。
- 不把 Future Optional 画成近期必做基础设施。

## Debug Playbooks

- 标题缺失：查 `EXPECTED_DIAGRAMS`。
- 样式失败：确认 Mermaid 块包含 `#f7f8fb`、`#ffffff`、`#b8c2cc`、`#16202a`、`#52616f`。
- HTML 漂移：运行 `python tools/agent/render_architecture.py --write`。

## Lessons Learned

图是项目介绍和答辩入口，不是架构细节的唯一载体。详细 contract 和验收标准必须留在 Markdown。
