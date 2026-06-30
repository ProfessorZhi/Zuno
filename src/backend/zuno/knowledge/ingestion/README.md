# Knowledge Ingestion 边界

PHASE02 status: target-owner-reserved

## 当前角色

`knowledge/ingestion/` 是 Document Ingestion / Parse Gateway 的目标 owner 入口。PHASE02 只建立 README 和 import guard，用来阻止后续解析、chunk、provenance、parser golden tests 继续散落到 `platform/services`。

当前真实 runtime 仍在 `platform/services/convert_files/`、`platform/services/pipeline/` 和相关 API 服务中；这些实现不能在本 phase 被写成 Current。

## Target role

目标状态下，这里负责 parser router、Document IR、chunk/provenance、解析任务 contract 和 parser golden tests。它向 Knowledge 层提供可引用、可追踪的文档解析结果，不直接承载 API 路由、队列 worker 或模型 provider。

## 允许新增内容

- 无副作用 contract、类型、README、parser fixture 索引和 import guard。
- 从旧路径迁移前的 ownership note。

## 禁止事项

- 禁止在 PHASE02 直接迁移真实 parser runtime、pipeline manager、队列 worker 或 API 上传逻辑。
- 禁止破坏 `zuno.services.convert_files.*`、`zuno.services.pipeline.*` 旧 import path。
- 禁止把 Parse Gateway 写成已经完成的 Current runtime。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
