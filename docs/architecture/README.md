# 架构文档

`docs/architecture/` 是 Zuno 当前面向人的正式架构入口。这里保持少而精：一个充实的总架构 Markdown、一个由它生成的 HTML 展示页、正式附件和仍然生效的 ADR。

PHASE11 已将 PHASE02-PHASE10 的已验证事实写入总架构：目录 ownership、企业知识库产品闭环、Document IR、Single Controller runtime harness、MemoryEngine、Tool Control Plane、Agentic GraphRAG / Evidence / Citation、Security Governance、`ZunoSpan` / release baseline contract。生产级 LangSmith 写入、在线 eval、持久 trace store、真实 sandbox runtime 和完整 UI 闭环仍是 Target。

## 当前前台

```text
docs/architecture/
  README.md
  architecture.md
  architecture.html
  repo-ownership-matrix.md
  assets/
  decisions/
```

## 阅读顺序

1. `architecture.md`：总架构文档，正文详细说明 Current / Target 边界、企业私有知识库主叙事、运行时分层、文档解析、Memory、工具、安全、评测和实施落点；后半部分维护 Mermaid 图源。
2. `architecture.html`：图形化展示页，适合快速看完整架构图，不替代 Markdown 正文。
3. `repo-ownership-matrix.md`：PHASE02 的目录 ownership、compat/vendor 边界和 provider 分类事实表；它是代码布局治理的正式 Current 证据。
4. `.agent/architecture/architecture.md` 与 `.agent/architecture/architecture.html`：Agent 侧镜像，必须由 `tools/agent/render_architecture.py --write` 同步。
5. `decisions/README.md`：仍影响当前主线的正式架构决策。
6. `../evidence/public-demo.md`：公开证据入口。

研究输入归档在 `docs/history/research/chatgpt-research-mode-artifacts/`。这些 PDF / Markdown 抽取版用于补充架构论证，不替代当前正式架构源。

当前最新详细度基准附件也保存在 `assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`，方便从架构目录直接打开阅读。正式结论仍以 `architecture.md` 和由它生成的 HTML 为准。

## 已归档拆分文档

以下拆分文档已经被 `architecture.md` 和 `architecture.html` 吸收，不再作为当前前台入口：

- `current-architecture.md`
- `target-architecture.md`
- `roadmap.md`
- `product-scenario-enterprise-kb.md`
- `security-and-sandbox.md`
- `deliverables.md`

归档位置：

- `docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/`
- `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/`

## 维护规则

- 改文字架构和 Mermaid 图源，都先改 `docs/architecture/architecture.md`。
- 运行 `python tools/agent/render_architecture.py --write` 同步 `.agent/architecture/architecture.md`、`docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html`。
- `docs/architecture/architecture.md` 的文字内容应比 HTML 更充实；HTML 偏图形化浏览，不承载全部设计论证。
- 不要在 `docs/architecture/` 重新增加高频变化的 roadmap、phase、workflow change log 或 Agent 操作规则。
- 过时审计、旧规格、旧 phase、旧计划和旧 runbook 进入 `docs/history/`，不要留在当前前台。

## 验证

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```
