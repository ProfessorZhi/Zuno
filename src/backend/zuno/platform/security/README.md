# Platform Security 边界

PHASE02 status: target-owner-reserved

## 当前角色

`platform/security/` 当前提供执行策略相关的轻量 import guard。真实 sandbox、审批、凭据、DLP 和工具执行治理仍分散在 `platform/services/sandbox/`、`platform/services/execution_policy.py` 以及 capability policy 中。

## Target role

目标状态下，这里负责 security policy、approval、sandbox、credential boundary、DLP 和工具执行约束。它是平台底座，不承载 API 路由、Agent 编排或业务工具实现。

## 允许新增内容

- 无副作用 policy contract、枚举、验证 helper 和 README。
- 从旧 services 路径迁移前的 owner note。

## 禁止事项

- 禁止在 PHASE02 迁移真实 sandbox runtime、凭据读取或工具执行逻辑。
- 禁止破坏 `zuno.services.sandbox.*`、`zuno.services.execution_policy` 和现有 capability policy import path。
- 禁止把完整安全沙箱写成已经完成的 Current runtime。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
