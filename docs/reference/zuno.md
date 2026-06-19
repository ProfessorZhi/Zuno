# Zuno 项目参考

这份文档提供 Zuno 的稳定参考视图，不承担当前 phase 或迁移决策说明。

如果你要看当前执行真相，请先读：

- [README](05_TopDown_题库学习/项目/02_项目映射/Zuno/README.md)
- [当前架构](current-architecture.md)
- [当前 phase 程序](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/architecture/phases/README.md)

## 核心入口

- `apps/web/`：Vue 3 + Vite Web 工作台
- `apps/desktop/`：Electron 桌面端壳层
- `src/backend/zuno/`：当前稳定后端恢复基线
- `infra/db/`：数据库迁移与 Alembic 配置
- `infra/docker/`：Dockerfile、Compose、nginx 和容器运行配置
- `tools/launchers/windows/`：Windows Web/Desktop 启动入口
- `tools/scripts/`：本地维护脚本
- `tools/evals/`：本地评测与验证工具

## 当前说明

仓库里仍能看到部分迁移期结构，但当前规则是：

- 前台文档以稳定恢复优先的 phase 口径为准
- 历史迁移材料不再作为默认阅读入口
- 是否继续更大规模目录迁移，要等 Phase 0 恢复验证后再决定

## 运行入口

- Web UI：`http://127.0.0.1:8090`
- 后端健康检查：`http://127.0.0.1:7860/health`
- API 文档：`http://127.0.0.1:7860/docs`
- 桌面本地前端：`http://127.0.0.1:8091`

## 本地资料与配置

- `.local/` 放个人资料、学习材料和历史运行数据，不提交
- `infra/docker/docker_config.local.yaml` 放 Docker 本地模型配置和密钥，不提交
- `.local/config/zuno/config.local.yaml` 放本地后端覆盖配置，不提交
- Docker named volumes 保存 PostgreSQL、Redis、Neo4j、MinIO 和后端向量库数据

## 相关文档

- [README](05_TopDown_题库学习/项目/02_项目映射/Zuno/README.md)
- [核心架构](core.md)
- [数据库结构](database.md)
- [API 参考](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/reference/api.md)
- [Docker 运行](05_TopDown_题库学习/项目/02_项目映射/Zuno/infra/docker/README.md)
- [数据库迁移](05_TopDown_题库学习/项目/02_项目映射/Zuno/infra/db/README.md)
