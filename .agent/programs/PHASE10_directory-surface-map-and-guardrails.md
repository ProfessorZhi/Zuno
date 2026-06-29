# PHASE10：Directory Surface Alignment Map And Guardrails

> 状态：active。Program 3 continuation / Directory Surface Alignment V1。

## 目标

把 Program 3 从“六层 facade 起步”修正为“目录表面与目标架构持续对齐”。本 phase 不宣布文件夹整理完成，而是先建立可执行的目录地图、迁移顺序和机器 guardrails。

## 范围

- 新增 `src/backend/zuno/DIRECTORY_MAP.md`，按 `keep / migrate / facade / retire` 标记当前一等目录。
- 新增 `.agent/references/zuno-repo-hygiene.md`，沉淀 Zuno 目录迁移 skill。
- 更新 `tools/scripts/verify_repo_structure.py` 和 repo tests，让新增 runtime 一等目录必须属于 allowlist。
- 明确 Program 4 仍是 queued / not active；本 phase 不做 runtime architecture upgrade。

## 不做

- 不一次性移动 `services/`、`core/`、`schema/` 或数据库模型。
- 不改 public API、DB schema、eval baseline 或前端行为。
- 不把 Target 写成 Current。

## 验收

- 当前 `src/backend/zuno` 每个一等目录都有归属和下一步处理策略。
- verifier 明确禁止新增未分类的一等 runtime 目录。
- `mcp_servers/`、`middleware/`、`evals/` 不再作为顶层目录恢复，只能由同名 `.py` alias module 承接旧 import。
- 文档不再写 Program 3 已完成 closure；只写 PHASE09 已完成、PHASE10 active。

## 验证命令

- `pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider`
- `pytest -q tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`
