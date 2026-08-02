# Goal05 PHASE22 Four-profile Canonical Factory Adapter 接线证据

## 结论

本切片修复 PHASE22 benchmark runtime 的默认路径缺口：`CanonicalProfileRuntimeFactory(runtime_mode="canonical")` 已经能进入 canonical preflight，但四个 profile 仍部分返回 placeholder runner，导致 formal adapter 代码不在默认 canonical benchmark 路径中。

修复后：

- `standard_rag` 由 `CanonicalProfileRuntimeFactory` 创建 `StandardRAGCanonicalAdapter`；
- `local_graphrag` 由 `CanonicalProfileRuntimeFactory` 创建 `LocalGraphRAGCanonicalAdapter`；
- `deep_graphrag` 由 `CanonicalProfileRuntimeFactory` 创建 `DeepGraphRAGCanonicalAdapter`；
- `agentic_graphrag` 由 `CanonicalProfileRuntimeFactory` 创建 `AgenticGraphRAGCanonicalAdapter`；
- `run_enterprise_rag_paired_benchmark(runtime_mode="canonical")` 通过 factory 调用四个 formal boundary adapter，并把注入 runtime port 的 blocked evidence 写入 `metrics.json`；
- 结果仍为 `BLOCKED / blocked_not_measured`，因为 Product Runtime attestation、formal receipt refs、usage receipt 和 budget settlement 还没有形成 measured evidence。

## 代码证据

- `tools/evals/zuno/rag_eval/profile_runtime_factory.py`
  - canonical factory 对 `standard_rag` 接入 `StandardRAGCanonicalAdapter`；
  - canonical factory 对 `local_graphrag` 接入 `LocalGraphRAGCanonicalAdapter`；
  - canonical factory 对 `deep_graphrag` 接入 `DeepGraphRAGCanonicalAdapter`；
  - canonical factory 对 `agentic_graphrag` 接入 `AgenticGraphRAGCanonicalAdapter`。
- `tools/evals/zuno/rag_eval/adapters/retrieval.py`
  - Standard / Local formal boundary adapter 只调用注入 port，不创建 runtime；
  - 不传入 gold document / gold evidence；
  - runtime observation 只能形成 blocked evidence，不能直接成为 measured production evidence。
- `tests/evals/test_canonical_profile_runners.py`
  - `test_09b_factory_uses_formal_deep_and_agentic_adapters_for_canonical_mode` 验证 factory 默认路径返回 Deep / Agentic formal adapter；
  - `test_09c_factory_uses_formal_standard_and_local_adapters_for_canonical_mode` 验证 factory 默认路径返回 Standard / Local formal adapter；
  - `test_06b_canonical_ready_dataset_uses_profile_factory_not_stackless` 验证 canonical benchmark 不调用 stackless runner，并在 `metrics.json` 中出现四个 adapter 经注入 port 产生的 blocked evidence。

## 验证命令

```powershell
python -m pytest -q tests/evals/test_canonical_profile_runners.py -p no:cacheprovider --tb=short
python -m pytest -q tests/evals/test_canonical_profile_runners.py tests/evals/test_canonical_deep_agentic_runtime.py tests/integration/evals/test_canonical_deep_agentic_integration.py tests/repo/test_phase22_eval_package_contract.py tests/repo/test_phase22_completion_blockers.py -p no:cacheprovider --tb=short
python tools/scripts/verify_phase22_completion_blockers.py
python tools/scripts/verify_current_program.py
python tools/scripts/verify_docs_entrypoints.py
```

## 边界

本证据不关闭 PHASE22。

仍未完成：

- Product Runtime attestation；
- formal receipt refs、usage receipt、budget settlement；
- 固定公开 benchmark human review 与 eligible case 证据；
- 四 profile measured runtime；
- Production Readiness 决策；
- Program archive / no-active reset。
