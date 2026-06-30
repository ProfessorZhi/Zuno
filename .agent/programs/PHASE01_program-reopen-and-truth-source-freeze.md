# PHASE01 program-reopen-and-truth-source-freeze

status: active

## 目标

打开 `zuno-target-architecture-runtime-full-implementation-v1`，把本轮目标从 contract foundation 改为 runtime-first / vertical-slice-first，并冻结 active program 事实源。

## 范围

- 更新 `.agent/programs/` 为 active program。
- 同步 `.agent/references/current-program.md`、README、AGENTS、architecture program 状态摘要。
- 更新 verifier / tests，让 active program、12 个 phase 文件和 runtime-first 验收口径可机器检查。
- 记录上一轮偏差：`zuno-master-architecture-implementation-v1` 完成的是可验证 contract foundation，不是完整产品级 runtime。

## 禁止范围

- 不实现 runtime feature。
- 不改 public API、DB schema、前端交互或后端主循环。
- 不把 Target 能力写成 Current。

## 验收闸门

- `.agent/programs/current.md` 声明 active program 和当前 phase。
- `.agent/programs/implementation-roadmap.md` 明确 12 个 runtime-first phase。
- `.agent/references/current-program.md` 同时保留历史完成事实和新 active program。
- verifiers/tests 不再要求 `.agent/programs/` 处于 no-active。

## 验证命令

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py -p no:cacheprovider
```

