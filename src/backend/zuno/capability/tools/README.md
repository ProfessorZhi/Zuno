# Tools 目录边界

分类：`migration-source`

## 当前角色

`src/backend/zuno/tools/` 当前保存 runtime tool packages、tool wrappers 和部分内部 helper。它不是仓库维护脚本目录；仓库维护脚本属于根级 `tools/`。

## Target role

目标状态下，runtime tools 应进入 Capability 层的 ToolCard、权限、健康状态、成本提示和执行策略边界；具体 tool 实现可以保留旧路径，直到 capability registry、tool tests 和 import compatibility 都能证明迁移安全。

## 允许新增内容

- runtime tool 的边界说明、ToolCard 映射说明和无副作用 facade。
- 小型 helper 的归属说明，前提是不改变工具注册或执行 trace。
- 指向 `capability/`、`platform/` 或根级 `tools/` 的分类说明。

## 禁止事项

- 禁止改变工具注册、权限、执行模式、provider 调用、trace metadata 或 tool response shape。
- 禁止把仓库维护脚本放入 `src/backend/zuno/tools/`。
- 禁止直接删除 `zuno.tools.*` 旧 import path。

## Focused tests

- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- tool / capability focused tests
- `python tools/scripts/verify_repo_structure.py`
