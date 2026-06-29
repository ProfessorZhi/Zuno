# PHASE03：Schema / Tools / Resources Directory Migration

> 状态：planned。目标 PR：Program3 PR3。

## 目标

把 `schema/`、`tools/`、`resources/` 从顶层旧目录收口到六层内部或仓库根职责区。

## 迁移范围

| 当前顶层 | 目标位置 | 策略 |
| --- | --- | --- |
| `schema/` | `api/dto/`、`agent/contracts.py`、`knowledge/contracts.py` | 按消费者拆，不保留泛 schema 作为完成态顶层 |
| `tools/` | `capability/tools/` 或仓库根 `tools/` | Agent 可调用工具进 capability；维护脚本出 runtime 包 |
| `resources/` | `platform/resources/`、`examples/` 或 `docs/` | runtime packaged resources 进 platform；示例和文档资源迁出 runtime |

## 禁止范围

- 不改 API 字段语义。
- 不改 eval baseline。
- 不改 Agent 主循环。

## 验收

- `schema/`、`tools/`、`resources/` 不再作为 `src/backend/zuno` 顶层目录存在。
- 旧 import 有 alias guard；新代码入口按六层归属。
- `DIRECTORY_MAP.md` 删除这三个顶层目录的 migrate 状态。

## 验证命令

- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `pytest -q tests/api tests/tools tests/evals -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
