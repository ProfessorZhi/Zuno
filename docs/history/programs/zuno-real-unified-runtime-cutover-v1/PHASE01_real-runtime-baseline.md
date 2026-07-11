# PHASE01 Real Runtime Baseline

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE01_real-runtime-baseline
state: completed
runtime_code_modified: false
measurement_status: baseline_frozen_not_measured
quality_status: not_proven
```

## 目标

激活 `zuno-real-unified-runtime-cutover-v1`，冻结当前 runtime / product / benchmark 事实，建立后续 PHASE02-PHASE07 必须收紧的 guardrail。

## 当前已冻结事实

```text
branch: codex/zuno-truth-source-production-readiness-baseline
activation_head: d90dc0013c1721a56828a6dc6f889e209454b346
program_state: completed
current_phase: PHASE01_real-runtime-baseline
```

代码事实：

- `src/backend/zuno/agent/runtime/graph.py` 已有 `build_agent_graph()`。
- `src/backend/zuno/agent/runtime/service.py` 仍有 `_run_from()` 和 `while current_node != RuntimeNode.END` 手写主循环。
- `UnifiedAgentRuntimeService.start()` 仍调用 `_run_from()`，不是 compiled graph `ainvoke()`。
- `UnifiedAgentRuntimeService.resume()` 仍把恢复状态改为 `ReflectionDecision.PASS`。
- `src/backend/zuno/agent/runtime/execution/model_step.py` 仍生成 deterministic `COMPLETED` observation，没有调用 Model Gateway。
- `src/backend/zuno/agent/runtime/execution/react_step.py` 仍生成 deterministic `COMPLETED` observation，没有真实 ReAct runner。
- `src/backend/zuno/agent/runtime/execution/knowledge_step.py` 在 `knowledge_runtime` 缺失时仍生成 synthetic `evidence:<run>:<step>` 和 `citation:<run>:<step>`。
- `src/backend/zuno/api/services/completion.py` 仍输出固定 `Unified runtime completed.` chunk。
- `src/backend/zuno/api/v1/completion.py` 默认仍走 `GeneralAgent`，unified runtime 需要 `product_mode == "unified_runtime"` 或 `ZUNO_COMPLETION_UNIFIED_RUNTIME=1`。
- EnterpriseRAG fixed paired benchmark 仍不是 measured pass。

## 范围

允许：

- `.agent/programs/**`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- `.agent/scripts/verify_agent_system.py`
- `tools/scripts/verify_current_program.py`
- `tools/scripts/verify_real_runtime_cutover.py`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/**`
- `README.md`
- `docs/architecture/README.md`
- 必要的 `.gitignore` 或 repo hygiene verifier 修正

禁止：

- 修改 `src/backend/zuno/**` 生产 runtime。
- 把 PHASE02-PHASE07 目标写成 Current。
- 把 benchmark blocked 写成 measured。
- 删除历史归档。

## PHASE01 Guardrail

新增 `tools/scripts/verify_real_runtime_cutover.py`。

PHASE01 默认模式必须验证：

- 当前缺口被诚实冻结。
- 当前 active state 与 phase 文件一致。
- `KnowledgeStepExecutor` 的 synthetic evidence fallback 被识别为待修。
- Completion canned answer 被识别为待修。
- manual loop 被识别为待修。

后续 phase 可使用 `--enforce-target` 收紧到目标态。

## verify_repo_structure 处理

PHASE01 必须处理 `python tools/scripts/verify_repo_structure.py` 的现有失败：

- 能安全修复的文档入口短语立即修复。
- `.local` 等已 ignore 的本地缓存目录不得导致 canonical verifier 永久失败。
- 仍无法安全处理的问题必须写入本文件的 blocker。

当前 blocker：无计划性 blocker；如后续 verifier 仍失败，以命令输出为准，不得在报告中写全绿。

## 验收闸门

- `current.md` 切换为 active。
- 7 个 PHASE 文件已创建。
- queued 文档已移除本机绝对 `created_from` 路径。
- `verify_real_runtime_cutover.py` 可运行并输出 PHASE01 baseline。
- repo / workflow / current program guardrail 通过，或精确记录 blocker。
- `git diff --check` 通过。

## 验证命令

```powershell
python tools/scripts/verify_real_runtime_cutover.py
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_current_program_contract.py tests/repo/test_publish_boundary.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider
git diff --check
```
