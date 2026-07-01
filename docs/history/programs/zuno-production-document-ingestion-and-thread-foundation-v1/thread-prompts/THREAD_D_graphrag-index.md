# THREAD D - GraphRAG / Index

## UI Mode

本线程必须在 Codex UI 目标模式执行。提示词中的“目标模式”不能替代真实 UI 模式。

## Goal

执行 Program 2 的 GraphRAG / Index 子任务：固定 enterprise knowledge schema、EvidenceBundle 字段、local RRF / rerank trace、Static GraphRAG baseline runner，并继续把 Elasticsearch / Milvus / Neo4j 等外部 index 写成 adapter boundary / Target。

## Safety Gate

先执行并报告：

```powershell
git fetch --prune
git status --short --branch
git log --oneline -5 --decorate
```

必须切到独立 worktree 和分支：

- Branch: `codex/zuno-p2-graphrag-index`
- Suggested worktree: `F:\internship-work\resume&resume project\02_projects\Zuno-worktrees\p2-graphrag-index`

如果无法确认独立 worktree / branch，停止并返回证据。

## Program 1 Shared Facts

- Document IR feeds index manifest fields for parse job id, parse attempt id, document version id, source sha256, parser config hash, IR schema version, diagnostics digest and parser diagnostics.
- Retrieval chunk metadata carries `citation_lineage`, including index job, document, block, parse and source hash fields.
- Agentic retrieval evidence provenance can inherit manifest lineage.
- External parser and external index services are target-blocked; do not claim production Elasticsearch / Milvus / Neo4j, LLM graph extraction or community report pipeline as Current.

GraphRAG / Index must consume Program 1 lineage directly in evidence, citation, trace and eval handoff.

## Allowed Paths

- `src/backend/zuno/knowledge/**`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tests/agent/test_agentic_retrieval_runtime.py`
- `tests/graphrag/**`
- `tests/retrieval/**`
- `tests/evals/test_multihop_eval_real_runtime_runner.py`

## Forbidden Paths

- `AGENTS.md`
- `README.md`
- `docs/**`
- `.agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- shared verifier / workflow scripts

If a fix requires forbidden paths, stop and report the exact reason.

## Required Work

1. Write failing tests for enterprise knowledge schema and EvidenceBundle fields.
2. Prove local RRF / rerank trace includes retrieval methods, source spans, citation lineage and unsupported claim metrics.
3. Add or strengthen Static GraphRAG baseline runner for Program 4 eval handoff.
4. Keep external graph index, production LLM extraction and production reranker as Target / adapter boundary.
5. Use internal subagents only for independent, non-overlapping work.

## Focused Tests

```powershell
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/agent/test_agentic_retrieval_runtime.py tests/graphrag tests/retrieval -p no:cacheprovider
git diff --check
```

## Stop Conditions

- Requires external Elasticsearch / Milvus / Neo4j, production LLM extraction, production reranker or online eval platform.
- Requires modifying Memory / Tool / Security ownership.
- New evidence fields conflict with Program 1 citation lineage.

## Closure

Before finishing, run focused tests, review diff, commit, and push.

Report:

- Branch
- Commit hash
- Push status
- Files changed
- Tests run and results
- Any blocked / forbidden-path evidence
