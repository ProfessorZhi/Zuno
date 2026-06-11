# Backend Layering Guidelines

当前后端的最小稳定分层约束是：

- 控制层：`src/backend/zuno/api/v1/*`
- 服务层：`src/backend/zuno/services/*`
- DAO 层：`src/backend/zuno/database/dao/*`
- 基础设施适配继续通过服务层和 DAO 层暴露，不直接污染控制层

这份规则当前主要服务 `Phase 2` 和 `Phase 4`：

- `Phase 2` 先把目录职责讲清楚
- `Phase 4` 再把高价值代码路径上的分层边界进一步收硬

