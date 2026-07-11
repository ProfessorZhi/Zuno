# Queued Programs

当前 queued program：

- `PROGRAM01_real-unified-runtime-cutover.md`

该 program 是下一轮候选实现 program，状态为 `queued / not active`。它只记录后续切换真实统一 runtime 的目标、边界和 phase 拆解；当前 `.agent/programs/` 仍是 no-active，不得把该 queued program 写成 active、measured 或 completed。

旧 Program 4-6 已合并进并随 Program 3 Mega 归档：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`
- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/queued-programs/PROGRAM05_agent-planning-integration.md`
- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`

新 queued program 只能在用户明确打开下一轮 program 或后续 roadmap 时创建，并必须同步 `.agent/system.yaml`、`.agent/references/current-program.md`、verifier 和 repo tests。只有当 queued program 被真正激活为 active program 时，才更新 `.agent/programs/current.md` 并平铺 PHASE 文件。
