# PHASE22 LangSmith Observability Delivery Truth

status: current_evidence_available
phase_id: PHASE22

## 目标

修正 LangSmith trace adapter 的 delivery 语义，使 canonical runtime 和平台 observability 不会把失败交付误当作有效 trace 证据。

## 事实

- `LangSmithTraceAdapter` 在 `create_run` / `update_run` 失败时会累加 `delivery_failures`。
- `fail_open=True` 仅表示不抛异常，不表示伪造成功 trace handle 或 ended span。
- canonical profile helper 现在会把 `delivery_failures` 增量识别为 `trace_delivery_failed` 并 fail closed。

## 验证

```bash
python -m pytest -q tests/platform/test_langsmith_trace_adapter.py tests/platform/test_langsmith_adapter_factory.py -p no:cacheprovider --tb=short
python -m pytest -q tests/evals/test_canonical_profile_runners.py::test_09f_standard_adapter_trace_delivery_failure_fails_closed -p no:cacheprovider --tb=short
```

## 边界

这不是 PHASE22 completion evidence。它只修正 observability delivery truth，避免 runtime trace delivery 失败被当作可用证据。
