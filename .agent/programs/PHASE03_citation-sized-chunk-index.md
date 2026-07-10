# PHASE03 Citation-Sized Chunk Index

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE03_citation-sized-chunk-index
status: completed
owner: Knowledge / Retrieval

## 目标

建立 small citation chunks + parent context chunks：检索保留语义完整性，citation 能落到更小 evidence span。

## 范围

- citation-sized chunks。
- parent / neighbor context。
- chunk manifest 和 eval manifest 对齐。

## 禁止范围

- 不重写整个 ingestion pipeline。
- 不把 citation chunk 命中伪装成 answer correctness。

## 验收闸门

- [x] citation chunks 保留 `citation_chunk_id` / `chunk_id`、`parent_chunk_id`、`neighbor_chunk_ids` 和 source span。
- [x] retrieval payload 返回 citation chunk，并携带 parent context。
- [x] `runtime_config.citation_chunking` 进入 EnterpriseRAG paired metrics/report。

## 完成事实

PHASE03 已完成本地 citation-sized chunk handoff 和 retrieval metadata，不表示 PHASE04 lexical/phrase evidence retrieval 或 PHASE07 claim-level binding 已完成。

Current 已实现：

- 每个 Document IR block 生成一个 `parent_context` chunk 和若干 `citation` chunks。
- BM25、vector、GraphRAG、evidence 和 citation handoff 使用 citation chunks，避免 parent context 挤掉 citation span。
- Citation chunk metadata 保留 `parent_chunk_id`、`neighbor_chunk_ids`、`parent_context`、`citation_chunking`、source span provenance 和 raw / normalized text。
- Index runtime retrieval payload 返回 citation chunk，并保留 parent context 与 citation lineage。
- EnterpriseRAG paired `metrics.json` / `report.md` 暴露 `citation_sized_with_parent_context` 配置。

边界：

- 当前只完成 local deterministic chunking baseline；没有声明 Evidence Text Available@5 已达标。
- Chunk boundary 当前按 sentence / fallback char 边界实现，section、paragraph、table row/cell、code block 的更细粒度优化留给后续 hardening。

## 验证命令

```powershell
pytest -q tests/knowledge tests/evals/test_enterprise_rag_paired_benchmark.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/**`
- `tools/evals/zuno/rag_eval/**`
- `tests/evals/test_enterprise_rag_paired_benchmark.py`

## 需要修改的文件

预计修改范围：

- `src/backend/zuno/knowledge/**`
- `tools/evals/zuno/rag_eval/**`
- `tests/knowledge/**`
- `tests/evals/**`

## 执行拆解

1. 设计 citation chunk 与 parent chunk 的 id 映射。
2. 扩展 index handoff 和 eval fixture。
3. 验证 retrieval context 能包含 citation-sized evidence。

## 多 agent 分工

默认单线程，避免 chunk contract 分裂。

## 需要返回的证据

- chunk id 映射示例。
- Evidence Text Available 指标变化。
- regression tests。

## 停止条件

只有 citation chunks 真实参与 eval 后才能关闭。
