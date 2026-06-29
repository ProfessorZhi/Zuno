# Database 目录边界

分类：`infrastructure`

## 当前角色

`src/backend/zuno/database/` 当前保存数据库 session、metadata、初始化数据、DAO 和 models。它是持久化底座，不是业务用例层，也不是 Platform facade 已经完成物理迁移的证据。

## Target role

目标状态下，数据库 wiring、持久化模型和 storage/versioned artifact 底座属于 Platform 层支撑能力。短期内 `database/` 保留为 infrastructure source，直到 import audit、DB focused tests 和 rollback plan 能证明可以迁入更明确的 platform/database 边界。

## 允许新增内容

- 数据库边界说明、无副作用的 contract 或兼容 re-export。
- DAO/model 所属关系和迁移前置条件说明。
- 不改变 schema、不打开连接的测试辅助说明。

## 禁止事项

- 禁止修改 DB schema、migration、session lifecycle、metadata 或默认连接行为。
- 禁止破坏 `zuno.database.*` public import path。
- 禁止把 API route、Agent runtime、GraphRAG query 或 product use case 编排放入 database 层。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
- storage / database focused tests
