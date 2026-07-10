# PHASE03 four-diagram-html-and-guardrails

status: completed
program: zuno-lean-complete-product-architecture-v1

## 目标

将前台 HTML 展示和文档 guardrail 从十图契约改为四图契约，并保持 Mermaid strict security、fullscreen 和 responsive rendering。

## 必改范围

- `tools/agent/render_architecture.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_docs_entrypoints.py`
- `.agent/references/diagram-inventory.md`
- 生成文件：
  - `docs/architecture/architecture.html`
  - `.agent/architecture/architecture.md`
  - `.agent/architecture/architecture.html`

## 四张图

1. Lean System Overview
2. Golden Path Runtime
3. Agentic GraphRAG and Agent Loop
4. Local Deployment and State

## 验收

- [x] `EXPECTED_DIAGRAMS` 只包含四张图。
- [x] `GROUPS`、`VIEW_META`、HTML header 和章节标签不再要求旧理论视图。
- [x] Markdown 恰好四个 canonical Mermaid block。
- [x] HTML 恰好四个 diagram section。
- [x] `.agent/architecture/architecture.md` 与 `docs/architecture/architecture.md` 完全一致。
- [x] 两份 HTML 完全一致。
- [x] `python tools/agent/render_architecture.py --check` 通过。
