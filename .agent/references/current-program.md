# 当前 Program 状态

## Current Truth

当前没有 active program。

state: no-active-program

最新完成 program：`zuno-repo-layout-cleanup-v1`。

`.agent/programs/` 当前保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`

## 最近完成事实

Program 3 已完成六层目录收口和 final alias surface closure：`src/backend/zuno` 顶层目录已经收敛为：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`

根目录只保留：

- `__init__.py`
- `main.py`

旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
