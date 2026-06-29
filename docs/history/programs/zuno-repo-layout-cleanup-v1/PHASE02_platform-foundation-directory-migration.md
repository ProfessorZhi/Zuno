# PHASE02：Platform Foundation Directory Migration

> 状态：planned。目标 PR：Program3 PR2。

## 目标

把低风险平台基础目录从 `src/backend/zuno` 顶层下沉到 `platform/`，同时用 alias module 或 compatibility facade 保护旧 import。

## 迁移范围

| 当前顶层 | 目标位置 | 策略 |
| --- | --- | --- |
| `config/` | `platform/config/` 或 `platform/config.py` | 先移动实现，再保留 `zuno.config` alias |
| `database/` | `platform/database/` | 移动 DAO/session/model 入口，旧 `zuno.database.*` re-export |
| `compatibility/` | `platform/compatibility/` | 下沉 legacy/vendor 兼容边界，禁止新业务逻辑 |

## 禁止范围

- 不改 DB schema。
- 不改 public API response/request。
- 不移动 `services/` 或 `core/`。

## 验收

- `src/backend/zuno/config/`、`database/`、`compatibility/` 不再作为顶层目录存在。
- 旧 import `zuno.config.*`、`zuno.database.*`、`zuno.compatibility.*` 继续通过 alias/facade 工作。
- `platform/README.md` 和 `DIRECTORY_MAP.md` 更新为 Current。

## 验证命令

- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `pytest -q tests/api tests/storage -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
