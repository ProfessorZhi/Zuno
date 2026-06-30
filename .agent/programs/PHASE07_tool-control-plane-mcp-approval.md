# PHASE07 Tool Control Plane MCP Approval

status: pending

## 目标

把工具层从零散函数集合升级成 Tool Control Plane：ToolCard / manifest、selector、policy、approval、executor adapter、MCP 和 sandbox 都由统一 contract 治理。

## 步骤

- [ ] 定义 ToolCard manifest 字段和执行模式。
- [ ] 区分 capability domain 与 execution adapter。
- [ ] 建立 executor registry，支持 local function、SDK、API、CLI、SSH、MCP local、MCP remote 和 sandbox。
- [ ] 对高副作用工具建立 approval gate。
- [ ] 更新 send_email、CLI、OpenAPI、MCP provider 的测试。

## 验收

- 工具不再按 API / CLI 顶层分类；API / CLI 是 execution adapter。
- 高副作用工具不会裸跑。
- Tool call 有 trace、audit、result normalization。

## 验证

```powershell
pytest -q tests/agent/test_capability_system.py tests/agent/test_capability_layer_surfaces.py tests/tools -p no:cacheprovider
```
