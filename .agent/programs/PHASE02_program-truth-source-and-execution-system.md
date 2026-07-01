# PHASE02 Program Truth Source and Execution System

status: pending

## 目标

冻结 active program 真相源、phase gate、多线程执行规则、thread prompt 位置、commit/push 节奏和 verifier 期望，避免再次出现旧文档与当前 program 双轨。

## 范围

- 同步 `.agent/programs/current.md`、`.agent/programs/README.md`、`.agent/references/current-program.md`、`AGENTS.md`、`README.md`。
- 检查 `.agent/system.yaml`、workflow verifier、repo tests 对 active program 的约束。
- 如果启用多线程模式，先盘点可复用线程和 worktree，再写 `.agent/programs/thread-prompts/`。

## 禁止范围

- 不为小编辑拆线程。
- 不把提示词里的“目标模式”当成 Codex UI 目标模式。
- 不让多个线程同时大改同一目录或共享文件。

## 验收闸门

- 所有 program 状态入口一致指向本 program 和当前 phase。
- verifier / tests 能检查 active program 文件和 phase 顺序。
- 多线程提示词规则和共享文件收口 owner 明确。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py -p no:cacheprovider
```

## 需要先读取

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/system.yaml`
- `.agent/references/current-program.md`
- `AGENTS.md`
- `README.md`

## 需要修改的文件

- `.agent/programs/*`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- `AGENTS.md`
- `README.md`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify-workflow.ps1`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tests/repo/test_publish_boundary.py`

## 执行拆解

1. 确认 active program、current phase、phase 文件列表和 roadmap 完全一致。
2. 确认 `.agent/programs/` 只保存当前 active program，不混入旧 program 或临时 thread prompt。
3. 更新 verifier/test 让 active program 文件集、phase section、closure checklist 成为机器检查项。
4. 明确多线程模式：主线程负责共享文件和集成验证，worker 只能改不重叠范围。
5. 为每个 phase 写明 commit/push 节奏、验证命令和 rollback/blocked 报告方式。

## 多 agent 分工

- Thread A：检查 `.agent/programs`、`.agent/references/current-program.md`、`.agent/system.yaml`。
- Thread B：检查 `README.md`、`AGENTS.md`、docs entrypoint。
- Thread C：检查 verifier 和 tests 是否覆盖 active program。
- 主线程：统一修改共享入口、运行完整 repo verification。

## 需要返回的证据

- active program 文件清单。
- verifier/test 覆盖清单。
- 多 worktree / 多 agent 执行分工。
- 每个 phase 的共享文件 owner。

## 停止条件

- 当前分支或 worktree 有未解释的用户改动。
- verifier 需要禁止路径变更才能通过。
- 需要把旧 program 重新变成 active 才能满足测试。
