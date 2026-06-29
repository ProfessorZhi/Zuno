# Config 目录边界

分类：`infrastructure`

## 当前角色

`src/backend/zuno/config/` 当前保存后端运行所需的静态配置资源和少量配置 helper，例如 avatar、tool、MCP server 和 Elasticsearch index 配置。它不是六层里的独立业务层，和 `settings.py`、`platform/` 的目标叙事有重叠。

## Target role

目标状态下，配置底座归入 Platform 层叙事；`config/` 只有在旧 import path、资源路径或启动配置需要兼容时才保留为 infrastructure source。后续如果收敛到 `platform/config`，必须先证明资源加载路径和 settings tests 不漂移。

## 允许新增内容

- 配置资源说明、无副作用的配置 contract 或兼容 wrapper。
- 指向 `platform/` 和 `settings.py` 的迁移说明。
- 不改变默认值、不触发外部连接的轻量 facade。

## 禁止事项

- 禁止直接修改 settings defaults、环境变量语义、provider 配置或外部服务连接。
- 禁止破坏 `zuno.config.*` 旧 import path 或配置文件相对路径。
- 禁止把配置业务规则写进 API、Agent、Knowledge 或 Capability 层。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`
- settings / config focused tests
