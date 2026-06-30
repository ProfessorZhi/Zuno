# PHASE01 Program Boot Baseline

Program: `zuno-eight-deliverables-full-realization-v1`
status: active

## 为什么

当前仓库已有八交付物目标和新的 architecture markdown / HTML 基础，但 `.agent/programs/` 仍处于 no-active 状态，verifier/tests 也会拒绝 active PHASE 文件。先把 program 本身落成可验证执行入口，后续 phase 才不会靠口头提示推进。

## 范围

覆盖交付物：

- 3. 模板与执行计划系统。
- 8. 一致性与验证系统。

允许修改：

- `.agent/programs/*`
- `.agent/references/current-program.md`
- `docs/architecture/roadmap.md`
- `AGENTS.md`
- `.agent/scripts/verify_agent_system.py`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`

禁止修改：

- Runtime 行为、API response、DB schema、frontend。
- 历史归档事实。

## 执行步骤

1. 新建 active program 文件和 `PHASE01` 到 `PHASE10` 文件。
2. 将 no-active 状态面改成 active program 状态。
3. 修改 verifier/tests，让它们校验新的 active program 文件集和连续编号。
4. 运行最小验证并修复失败。

## 验收

- `.agent/programs/` 中有且只有本 program 的平铺 phase 文件。
- `current.md` 标记 `state: active`，并指向 `PHASE01_program-boot-baseline.md`。
- verifier/tests 不再要求当前无 active program，而是要求本 program 完整存在。
- `git diff --check` 和 repo agent verifier 通过。

## PR 边界

这是 program boot PR。它不实施业务 runtime，只让后续完整 program 可执行、可验证。
