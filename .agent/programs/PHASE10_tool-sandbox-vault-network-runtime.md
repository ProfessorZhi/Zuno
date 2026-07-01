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

## 需要先读取

- `src/backend/zuno/capability/control_plane.py`
- `src/backend/zuno/capability/runtime.py`
- `src/backend/zuno/capability/policy.py`
- `src/backend/zuno/platform/security/governance.py`
- `src/backend/zuno/platform/observability/trace_eval.py`
- `tests/agent/test_capability_system.py`

## 需要修改的文件

- `src/backend/zuno/capability/**`
- `src/backend/zuno/platform/security/**`
- `src/backend/zuno/platform/observability/**`
- credential / sandbox / network policy adapters
- `tests/agent/test_capability_*.py`
- `tests/api/test_workspace_security_observability_runtime.py`

## 执行拆解

1. 明确 ToolCard、executor、approval、credential ref、sandbox context、audit event 的接口。
2. 为真实 sandbox 设计 adapter：rootless / gVisor / Firecracker 为 Target，local deterministic sandbox 为 Current fallback。
3. 为 vault / OAuth broker 设计 credential ref 和 dev fallback，禁止真实 secret 入 repo。
4. 接入 network policy 和 tool audit trace。
5. 确保高副作用工具必须走 approval gate。

## 多 agent 分工

- Thread A：ToolCard / executor registry。
- Thread B：approval / credential ref。
- Thread C：sandbox / network policy。
- Thread D：security observability tests。
- 主线程：审查高风险工具路径和 secret safety。

## 需要返回的证据

- tool risk matrix。
- approval flow 示例。
- sandbox adapter current/target 边界。
- credential ref 示例。
- audit trace 样例。

## 停止条件

- 需要真实 vault / OAuth 凭据。
- 需要真实隔离运行时但本机不可用。
- 高副作用工具无法强制审批。
