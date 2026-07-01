# PHASE10 Tool Sandbox Vault Network Runtime

status: pending

## 目标

把 Tool Control Plane 与 Sandbox 推进到真实隔离 sandbox、外部 vault / OAuth broker、网络代理、持久 approval DB 和 audit。

## 范围

- ToolCard registry、executor adapter、approval gate、credential ref。
- sandbox profile、network policy、audit trace。
- vault / OAuth broker 边界和本地 dev fallback。

## 禁止范围

- 不把模拟 sandbox 写成真实隔离 Current。
- 不在 repo 中保存真实 credential。
- 不让高副作用工具绕过 approval。

## 验收闸门

- 低风险工具自动通行，高风险工具强制审批。
- credential 只通过 ref 传递。
- sandbox / network / approval audit 可追踪。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_registry.py tests/agent/test_capability_layer_surfaces.py tests/api/test_workspace_security_observability_runtime.py -p no:cacheprovider
```
