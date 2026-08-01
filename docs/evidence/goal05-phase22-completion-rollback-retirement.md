# Goal05 PHASE22 Completion Rollback Retirement Evidence

status: CLEANUP_SLICE_VERIFIED_NOT_PHASE22_COMPLETE
date: 2026-08-01
branch: codex/goal05-phase22-completion-rollback-retirement
base_branch: main
base_sha: 3b97e1abe665a1094dfbd5d663f58e5edfd4851d
work_package: P22-T03 / P22-T04

## Scope

本证据记录 PHASE22 cleanup 的 completion rollback 退役切片：`POST /api/v1/completion` 不再通过 `ZUNO_COMPLETION_CUTOVER_MODE=rollback` 回到 `GeneralAgent.astream()`；rollback mode 现在在 `CompletionService.resolve_cutover_mode()` fail-closed。

本切片不声明 PHASE22 completed，不声明 fixed benchmark measured，不声明 production ready，不声明 `GeneralAgent` 类物理删除。`GeneralAgent` 仍作为 agent-layer focused runtime surface 存在，但不再是 completion 产品入口的默认或 rollback 执行路径。

## Implemented

- `src/backend/zuno/api/v1/completion.py` 删除 `_LazyClassProxy`、`AgentConfig`、`GeneralAgent`、`_create_chat_agent` 和 rollback branch。
- `POST /api/v1/completion` 只对 `shadow`、`canary`、`new_default` 调用 `CompletionService.stream_unified_runtime()`。
- `src/backend/zuno/api/services/completion.py::resolve_cutover_mode()` 对 `ZUNO_COMPLETION_CUTOVER_MODE=rollback` 抛出 fail-closed error。
- `tests/api/test_completion_unified_runtime.py` 覆盖 rollback 被拒绝且不会触达 product runtime request。
- `tests/agent/test_completion_agent_config_compatibility.py` 覆盖 completion route 不再导出或构造 `GeneralAgent`。
- `tools/scripts/verify_phase22_cleanup_boundary.py` 新增 completion rollback retirement guard。
- `.agent/programs/work-products/phase22-removal-candidates.yaml` 把 GeneralAgent completion rollback candidate 改为 `resolved_retired`。

## Still Open

- `GeneralAgent` 类仍存在，作为 contained agent-layer surface 和 focused tests 的当前实现；本切片只证明 completion 产品入口不再回滚到它。
- Fixed benchmark 仍是 `BLOCKED / blocked_not_measured`。
- Full final verification、program archive 和 `.agent/programs/` no-active reset 仍未完成。
- Production readiness 仍未建立。

## Verification

```text
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_real_runtime_cutover.py --enforce-product-cutover
python -m pytest -q tests/api/test_completion_unified_runtime.py tests/agent/test_completion_agent_config_compatibility.py tests/api/test_layered_api_boundaries.py::test_api_services_use_canonical_platform_imports -p no:cacheprovider
rg -n "_create_chat_agent|completion\.GeneralAgent|ZUNO_COMPLETION_CUTOVER_MODE=rollback only|rollback.*GeneralAgent|GeneralAgent.*rollback" src/backend/zuno/api tests tools/scripts .agent/programs/work-products docs/status docs/modules
git diff --check
```

预期结果：verifier 与 focused tests 通过；当前代码、测试、脚本和活跃 work-products 不再把 completion rollback 描述为可执行 GeneralAgent 路径。

