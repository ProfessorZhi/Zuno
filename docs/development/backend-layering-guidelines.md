# Backend Layering Guidelines

当前后端的最小稳定分层约束是：

- 控制层：`src/backend/zuno/api/v1/*`
- 服务层：`src/backend/zuno/services/*`
- DAO 层：`src/backend/zuno/database/dao/*`
- 基础设施适配继续通过服务层和 DAO 层暴露，不直接污染控制层

这份规则当前主要服务 `Phase 2` 和 `Phase 4`：

- `Phase 2` 先把目录职责讲清楚
- `Phase 4` 再把高价值代码路径上的分层边界进一步收硬

## Phase 4 Boundary Rule

从 `Phase 4` 开始，`core/`、`database/` 和运行时导向的 `services/` 模块不应再直接依赖 `zuno.api.services.*`。

如果下层代码需要复用已有业务服务，默认走：

- `zuno.services.application.*`

原因不是“换个 import 名字更好看”，而是要把下面这条边界收硬：

```text
controller-facing namespace
  !=
runtime/service/database lower-layer dependency surface
```

这意味着：

- `api/v1/*` 可以继续依赖 `zuno.api.services.*`
- `core/*` 不应直接依赖 `zuno.api.services.*`
- `database/*` 不应直接依赖 `zuno.api.services.*`
- `services/rag/*`、`services/retrieval/*`、`services/pipeline/*`、`services/capability_registry.py`
  这类运行时导向模块不应直接依赖 `zuno.api.services.*`

最低守门入口：

```powershell
python tools/scripts/verify_backend_layering.py
pytest tests/test_backend_layering_boundaries.py
pytest tests/test_phase4_runtime_boundary_smoke.py
```
