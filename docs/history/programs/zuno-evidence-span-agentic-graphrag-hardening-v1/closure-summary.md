# Program Closure Summary

program: zuno-evidence-span-agentic-graphrag-hardening-v1
status: completed
closed_at: 2026-07-10

## 完成结论

本 program 已完成 PHASE01-PHASE08 的 evidence-span hardening 基线：failure bucket 诊断、source span provenance、citation-sized chunks、lexical / phrase evidence retriever、graph evidence lineage、evidence-aware reranker、claim-level citation binder、hard negative coverage 和 release gate 输出面。

本轮不能写成 fixed benchmark measured pass。两次真实本地 EnterpriseRAG paired eval 尝试分别使用 `sample_size=80` 和 `sample_size=8`，都完成了部分 profile 产物，但 agentic profile 未在本轮运行窗口内完成。当前 gate 结论是 `blocked_not_measured_due_to_agentic_profile_incomplete`。

## Current Evidence

- `metrics.json` / `report.md` / `failure_cases.md` 可区分 `doc_miss`、`doc_hit_text_miss`、`text_hit_citation_miss` 和 `citation_hit_answer_wrong`。
- Evidence Text Available@5 与 strict citation 已明确分层：source-doc citation 不能冒充 source-span citation。
- Runtime citation lineage 保留 source span、chunk、block、source URI、hash、parser 和 citation lineage 字段。
- Citation-sized chunks 保留 parent context 与 neighbor chunk references。
- Lexical / phrase retriever、graph lineage、evidence-aware reranker 和 claim binder 都进入 local deterministic runtime trace。
- Claim binder 输出 `supported`、`contradicted`、`insufficient`，无 source span 的 doc-level citation 不算 strict claim citation。
- PHASE08 release gate 输出 `hard_negative_coverage` 与 `release_gate`，blocked / prepared / incomplete eval 不写成 measured。

## 验证

- `pytest -q tests/agent -p no:cacheprovider` -> 187 passed。
- `pytest -q tests/knowledge -p no:cacheprovider` -> 60 passed。
- `pytest -q tests/evals/test_enterprise_rag_paired_benchmark.py tests/evals/test_rag_eval_metrics.py -p no:cacheprovider` -> 63 passed。
- `pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider` -> 16 passed。
- `python .agent/scripts/verify_agent_system.py` -> passed。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1` -> passed。
- `python tools/scripts/verify_docs_entrypoints.py` -> passed。
- `git diff --check` -> passed。

## 后续 Target

- 修复或拆分 agentic profile runner，使 fixed EnterpriseRAG paired eval 能完整产出 measured `agentic_graphrag` profile。
- 重新运行 release gate，并只在真实 fixed benchmark 产出后判断质量闸门是否达成。
- 若 quality gate 仍失败，优先按 failure bucket 投入：evidence text、citation binding 或 answer synthesis，而不是继续堆 doc-level recall。
