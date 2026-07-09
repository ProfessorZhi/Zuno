# PHASE03 Citation-Sized Chunk Index

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE03_citation-sized-chunk-index
status: pending
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

- `Evidence Text Available@5` 可由真实 citation chunks 支撑。
- parent context 不覆盖 citation span 的 source truth。
- chunk 粒度变化有 focused tests。

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
