# zuno-real-unified-runtime-cutover-v1

状态：completed / archived

关闭口径：

```text
implementation_status: implementation_complete
measurement_status: measurement_blocked
quality_gate_status: quality_not_proven
```

本 program 完成了 Completion / Workspace 产品主路径到统一 runtime 的本地 implementation cutover：

- `UnifiedAgentRuntimeService` 通过 compiled LangGraph 执行。
- `RuntimeDependencyFactory` 统一装配 Model Gateway、Memory、Knowledge 和 Tool Control Plane。
- ModelStep 通过 Model Gateway 执行并记录 metrics / trace。
- ReActStep 只执行当前 PlanStep 的单步 reason / act / observe。
- Knowledge 缺失时 blocked，不伪造 evidence / citation。
- filesystem.read / filesystem.write 通过 Tool Control Plane 执行，write 保持审批和幂等。
- Memory 覆盖 pre-turn read、in-turn selected refs、post-turn raw event / summary 和 pending Reflexion candidate。
- Completion 默认走 unified runtime；legacy GeneralAgent 只通过 `ZUNO_AGENT_RUNTIME=legacy_general_agent` rollback。

Benchmark 状态：

- raw EnterpriseRAG parquet 路径 `.local/evals/raw/enterprise_rag_bench/hf/data/questions/test.parquet` 不存在，runner 直接 `FileNotFoundError`。
- tracked sample-8 JSONL 尝试运行到 184 秒超时，只生成了 baseline / local / deep partial profile artifacts，没有 agentic profile 和顶层 `metrics.json` / `report.md`。
- 因此 fixed EnterpriseRAG paired benchmark 未形成完整 measured profile，不允许写成 measured pass / fail。

主要本地验证：

- `pytest -q tests/agent/runtime tests/api -p no:cacheprovider`
- `pytest -q tests/agent/runtime tests/e2e -p no:cacheprovider`
- `pytest -q tests/api tests/e2e tests/agent/runtime -p no:cacheprovider`
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-langgraph`
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-dependencies`
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-real-execution`
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-knowledge-tool-memory`
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-product-cutover`
- `python tools/scripts/verify_current_program.py`
- `python .agent/scripts/verify_agent_system.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`
- `python tools/scripts/verify_docs_entrypoints.py`
- `python tools/scripts/verify_repo_structure.py`
- `git diff --check`
