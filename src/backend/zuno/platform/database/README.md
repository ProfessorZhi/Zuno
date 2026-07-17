# Database 目录边界

分类：`infrastructure`

## 当前角色

`src/backend/zuno/platform/database/` 保存数据库 Runtime Factory、Session/UoW、物理 Claim/Lease/Delivery/Migration receipt、metadata、初始化数据、DAO 和 models。旧 public import path `zuno.database.*` 由 `platform/compatibility/legacy_aliases.py` 映射到这里；它是持久化底座，不是业务用例层。

## Target role

目标状态下，数据库 wiring、sync/async Session Factory、显式事务边界、持久化模型和 migration/recovery control 属于 Platform 层支撑能力。短期内 `platform/database/` 保留为 infrastructure source，并继续保护 `zuno.database.*` alias，直到 import audit、默认路径 cutover、DB fault tests 和 rollback plan 能证明可以进一步收窄或重命名。

## 允许新增内容

- 无导入时连接副作用的 Runtime Config、Engine/Session Factory 和 UoW。
- Infrastructure Owner 的 Claim、Lease、Delivery、Migration、Backup/Restore receipt 与控制逻辑。
- DAO/model 所属关系、Alembic migration 和真实 PostgreSQL fault/integration test。

## 禁止事项

- 禁止在 Infrastructure 表或 receipt 中复制领域终态，或把 commit/ACK/checkpoint receipt 解释为领域成功。
- 禁止绕过 Alembic、tenant context、transaction boundary、idempotency、lease/fencing 或恢复验证。
- 禁止新增导入时创建的全局 Session；旧全局 Engine 只能作为有退出条件的 compatibility surface。
- 禁止破坏 `zuno.database.*` public import path 或把它误写成物理 `src/backend/zuno/database/` Current 目录。
- 禁止把 API route、Agent runtime、GraphRAG query 或 product use case 编排放入 database 层。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
- storage / database focused tests
