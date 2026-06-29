# Program Roadmap

## 当前状态

当前没有 active program。最近完成的 program 是：

```text
zuno-repo-layout-cleanup-v1
```

Program 3 已完成并归档到：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

`.agent/programs/` 只保留当前状态、路线图和 closure checklist。每次新 program 都从 `PHASE01` 开始编号，旧 active phase 文件不能留在前台路径。

## 最近完成

Program 3 完成了后端目录收口：

- `src/backend/zuno` 顶层目录只保留 `api / agent / memory / capability / knowledge / platform`。
- 旧 runtime 顶层目录已下沉到六层内部。
- 旧 import path 通过顶层 `.py` alias module 兼容。
- `tools/scripts/verify_repo_structure.py` 和 repo tests 已固定六层目录与 alias module allowlist。

## Queued / Not Active

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
