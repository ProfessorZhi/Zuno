# Platform Observability 边界

PHASE02 status: target-owner-reserved

PHASE10 status: contract-foundation

## 当前角色

`platform/observability/` 当前提供 LangSmith-compatible metadata、trace helper、OTel / LangSmith-compatible span schema、redacted export adapter、eval dataset schema、release baseline contract 和 sandbox audit span bridge。真实 trace storage、在线 eval、LangSmith 产品化写入和可视化平台仍未形成完整平台能力。

## Target role

目标状态下，这里负责 OTel / LangSmith-compatible trace、metrics、eval export、run metadata 和跨层 observability contract。它只提供平台观测能力，不把 Agent 或 Knowledge 的业务流程搬进平台层。

## 允许新增内容

- 无副作用 trace contract、metadata helper、README、eval export 边界说明和 release baseline schema。
- 从 `platform/common/runtime_observability.py` 迁移前的 owner note。

## 禁止事项

- 禁止把 PHASE10 contract foundation 写成完整 trace storage、LangSmith 产品化面板或 eval runtime。
- 禁止破坏 `zuno.utils.runtime_observability` 旧 import path。
- 禁止把 LangSmith-compatible Trace / Eval 写成已经完成的 Current runtime。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `pytest -q tests/evals/test_observability_trace_contract.py tests/agent/test_platform_layer_surfaces.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py -p no:cacheprovider`
