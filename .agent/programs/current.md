# 当前程序

当前没有 active program。

最新完成 program：

```text
zuno-repo-layout-cleanup-v1
```

状态：Program 3 final alias surface closure 已完成并归档。

## 当前判断

Program 3 已完成 Directory Surface Alignment V1 和 final alias surface closure：`src/backend/zuno` 顶层目录只剩 `api / agent / memory / capability / knowledge / platform` 六层，根目录只保留 `__init__.py` 和 `main.py` 两个文件。旧 public import path 通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

## 归档位置

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

## 不属于本 Program

- 不做 Program 4 runtime architecture upgrade。
- 不改 API 行为。
- 不改 DB schema。
- 不改 frontend。
- 不改 eval baseline。
- 不删除旧 public import path；只能改变兼容实现方式。

## 等待打开的 Program

queued draft / not active：

- Program 4：`.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- Program 5：`.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
