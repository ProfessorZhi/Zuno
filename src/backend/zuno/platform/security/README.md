# Platform Security 边界

PHASE09 status: contract-foundation

## 当前角色

`platform/security/` 当前提供执行策略相关的轻量 import guard，并通过 `governance.py` 固定 PHASE09 security governance contract：input gate、retrieval gate、tool gate、output gate、ToolSecurityProfile、SandboxAuditEvent、policy decision trace 和 secret / PII redaction helper。真实 sandbox runtime、approval UI、凭据 broker、生产级 DLP 和工具执行治理仍是 Target。

## Target role

目标状态下，这里负责 security policy、approval、sandbox、credential boundary、DLP 和工具执行约束。它是平台底座，不承载 API 路由、Agent 编排或业务工具实现。

## 允许新增内容

- 无副作用 policy contract、枚举、验证 helper、redaction helper 和 README。
- 从旧 services 路径迁移前的 owner note。

## 禁止事项

- 禁止在 PHASE09 迁移真实 sandbox runtime、凭据读取、approval UI 或工具执行逻辑。
- 禁止破坏 `zuno.services.sandbox.*`、`zuno.services.execution_policy` 和现有 capability policy import path。
- 禁止把完整安全沙箱写成已经完成的 Current runtime。

## Focused tests

- `pytest -q tests/security tests/tools tests/agent/test_capability_system.py tests/agent/test_platform_layer_surfaces.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
