# Program Roadmap

## 当前状态

当前没有 active program。

最新完成 program 是：

```text
zuno-repo-layout-cleanup-v1
```

Program 3 final alias surface closure 已完成并归档。Directory Surface Alignment V1 和本轮 PHASE10-15 均保存在：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 4/5 仍是 queued / not active。

## 新完成标准

Program 3 完成态中，`src/backend/zuno` 根目录只允许：

```text
__init__.py
main.py
api/
agent/
memory/
capability/
knowledge/
platform/
```

旧 import path 必须继续可用，例如：

```text
zuno.services.*
zuno.core.*
zuno.database.*
zuno.schema.*
zuno.tools.*
zuno.utils.*
zuno.config.*
zuno.resources.*
zuno.compatibility.*
zuno.settings
zuno.mcp_servers.*
zuno.middleware.*
zuno.evals.*
```

兼容实现已收敛到六层内部，核心入口是 `platform/compatibility/legacy_aliases.py`。

## 已归档 Phase Set

1. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE10_alias-inventory-and-target-contract.md`
2. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE11_import-smoke-and-compat-registry-design.md`
3. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE12_low-risk-alias-surface-cleanup.md`
4. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE13_medium-risk-alias-surface-cleanup.md`
5. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE14_high-risk-core-services-settings-cleanup.md`
6. `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE15_final-root-surface-guard-and-closure.md`

每次新 program 都从 `PHASE01` 开始编号；本轮属于 Program 3 continuation，执行中从 `PHASE01` 重跑，归档时接在历史 Program3 后作为 PHASE10-15。

## Queued / Not Active

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
