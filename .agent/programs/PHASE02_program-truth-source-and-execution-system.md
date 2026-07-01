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
