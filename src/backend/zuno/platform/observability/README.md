# Platform Observability 边界

PHASE02 status: target-owner-reserved

## 当前角色

`platform/observability/` 当前提供 LangSmith-compatible metadata 和 trace helper 的轻量 import guard。真实 trace、eval export 和产品可视化仍未形成完整平台能力。

## Target role

目标状态下，这里负责 OTel / LangSmith-compatible trace、metrics、eval export、run metadata 和跨层 observability contract。它只提供平台观测能力，不把 Agent 或 Knowledge 的业务流程搬进平台层。

## 允许新增内容

- 无副作用 trace contract、metadata helper、README 和 eval export 边界说明。
- 从 `platform/common/runtime_observability.py` 迁移前的 owner note。

## 禁止事项

- 禁止在 PHASE02 实现完整 trace storage、LangSmith 产品化面板或 eval runtime。
- 禁止破坏 `zuno.utils.runtime_observability` 旧 import path。
- 禁止把 LangSmith-compatible Trace / Eval 写成已经完成的 Current runtime。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
