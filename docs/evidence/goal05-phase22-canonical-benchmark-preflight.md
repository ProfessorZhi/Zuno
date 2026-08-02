# Goal05 PHASE22 Canonical Benchmark Preflight Evidence

日期：2026-08-02

## 结论

本证据记录 PHASE22 benchmark runtime 的一个收口切片：`runtime_mode=canonical` 不再无条件停在入口，而是在存在显式 `CanonicalRuntimeDependencies` bundle 或 `CanonicalProfileRuntimeFactory` 时进入四 profile canonical runner preflight。

该路径仍然 fail-closed：它只生成 `blocked_not_measured` 证据，不调用 stackless contract-smoke runner，不声明 fixed benchmark measured，不声明 quality proven，不声明 production ready。当前正式执行 adapter、Receipt 写入和真实四 profile runtime measurement 仍未完成。

## 代码边界

- `tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py`
  - `validate_canonical_runtime_config()` 仍拒绝缺失、空 dependency bundle 和无效 factory。
  - 非空 dependency bundle 或有效 `CanonicalProfileRuntimeFactory` 可进入 canonical profile preflight。
  - `runtime_mode=canonical` 的 profile execution dispatch 走 `CanonicalProfileRuntimeFactory`，不走 `run_stackless_local_eval`。
  - 输出 `metrics.json` / `benchmark_manifest.json` 时保持 `measurement_status=blocked_not_measured`。
- `tools/evals/zuno/rag_eval/canonical_profile_runners.py`
  - 继续由四个 canonical profile runner 返回 dependency gaps 或 `canonical_<profile>_execution_adapter_unavailable`。

## 验证

```powershell
python -m pytest -q tests/evals/test_canonical_profile_runners.py -p no:cacheprovider --tb=short
```

结果：`27 passed`。

## 剩余未完成

- 正式 canonical execution adapter 尚未接入真实 Knowledge Runtime / Index Runtime / Agent Run Runtime。
- Runtime evidence binding 仍只有 validation contract，未由 benchmark runner 写入真实 receipt bundle。
- Public benchmark review pack 仍为 `REVIEW_REQUIRED`，`reviewer_approved_count=0`，`benchmark_eligible_count=0`。
- Fixed benchmark 仍为 `BLOCKED / blocked_not_measured`，不能关闭 PHASE22。
