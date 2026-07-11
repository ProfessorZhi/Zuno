# Architecture Update Policy

## When To Use

当改动影响 Agent Runtime、RAG、GraphRAG、Memory、Model、Tool、Security、Trace、Eval、部署或产品契约时，使用本策略判断架构同步范围。

## Mental Model

```text
behavior or boundary change
  -> update text design if meaning changed
  -> update Mermaid source if relationships changed
  -> verify HTML atlas
  -> update Current only when implementation evidence changed
  -> update agent governance and tests
```

## Source Roles

```text
docs/architecture/architecture.md
  = text-first Target design

docs/architecture/architecture-views.md
  = ten-view Mermaid source

docs/architecture/architecture.html
  = diagram-first visual atlas
docs/architecture/production-readiness.md
  = Current and measured status
```

## Change Matrix

| Change area | Text design | Mermaid views | Current/readiness | Typical views |
| --- | --- | --- | --- | --- |
| Agent Runtime | yes | yes | when runtime changes | Logical, Process, Module, C&C |
| Model Gateway | yes | yes | when provider path changes | Logical, Physical, C&C, Quality |
| Memory / Context | yes | yes | when persistence or reuse changes | Logical, Module, Data, Quality |
| Input / Parsing | yes | yes | when supported formats or jobs change | Logical, Process, Scenarios, Data |
| RAG / GraphRAG | yes | yes | when retrieval behavior changes | Module, C&C, Data, Product Core |
| Capability / Skill / MCP / Tool | yes | yes | when real execution changes | Logical, Process, C&C, Quality |
| Security | yes | yes | when gates or policies change | Logical, Quality, C&C |
| Observability / Eval | yes | yes | when trace or measurement changes | Physical, Data, Quality |
| Product API / UI | yes | yes | when default path changes | Logical, Scenarios, C&C |
| Infrastructure | yes | yes | when persistence/recovery changes | Physical, Data, Quality |

## Must Preserve

- `architecture.md` 解释职责、边界、近期精简实现、成熟扩展、contract、失败语义和完成标准。
- `architecture-views.md` 维护图形关系，不重复长篇设计说明。
- HTML 从 `architecture-views.md` 读取图源。
- `.agent/architecture/architecture.md` 与正式文字文档完全一致。
- `.agent/architecture/architecture.html` 与正式 HTML 完全一致。
- Current 只有代码、测试、trace/eval 或 verifier 证明后才能更新。
- Future Optional 不得成为近期 blocker。
- GraphRAG 补充 BM25 与 Dense Retrieval，不替代它们。
- `auto` 是 router，不是独立固定检索实现。
- Codex 多 agent 执行模式不是 Zuno 产品 runtime 默认架构。

## Before Editing

1. 判断是“设计含义变化”还是“仅图形可读性变化”。
2. 设计含义变化先更新 `architecture.md`。
3. 模块关系、流程、数据或部署关系变化时更新 `architecture-views.md`。
4. 实现事实变化时再更新 `production-readiness.md`。
5. 更新 `diagram-inventory.md`、renderer、verifier 和 tests。
6. 运行同步和验证。

## Allowed Changes

- 更新文字设计、Mermaid 图源、HTML shell、renderer、verifier 和 tests。
- 按实际需要增加 Local Diagram，但保持十类顶层 view 稳定。
- 新增 Future adapter，但必须明确 optional。

## Forbidden Changes

- 不把三十张详细图重新放入 `architecture.md`。
- 不让 HTML 解析文字总架构作为图源。
- 不恢复简化 offline SVG renderer。
- 不把远期微服务、分布式 worker、产品级多 Agent 写成近期 Current。
- 不把 fallback/retry 包装成已完成 circuit breaker。
- 不因文档中存在 Target contract 就宣称 implementation complete。

## Focused Tests

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## Docs Sync

修改本文件时检查：

- `.agent/references/architecture-docs-map.md`
- `.agent/references/diagram-inventory.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture-views.md`
- `docs/architecture/architecture.html`
- `docs/architecture/production-readiness.md`
- `tools/agent/render_architecture.py`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_docs_entrypoints.py`

## Lessons Learned

架构同步不是“补一句说明”，而是让文字设计、图谱关系、Current 状态、Agent 规则和自动验证同时收口。
