# PHASE02：根目录与 Docs Hygiene
> 状态：pending。等待 PHASE01 审计结果后执行。

## 目标

清理根目录和 docs 前台，把历史、生成物、临时文件、旧入口归位。

根目录目标是少而稳定：只保留必要项目入口、一等目录和 package/config 文件。对 `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 等先确认 tracked 状态、用途和 `.gitignore`，再决定移动、归档、忽略或删除。

`docs/` 前台只承载正式真相；历史材料、旧计划、旧审计和生成报告进入 `docs/history/` 或被 `.gitignore` 排除。

## PHASE01 输入

- Thread A 确认根目录当前没有 `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 实体，也没有 tracked 脏目录。
- `reports/` 和 `data/` 不能盲删或整目录粗暴忽略，需要白名单语义：正式证据进 `docs/evidence/`，示例输入进 `examples/` 或 `tools/evals/`，运行生成物保持 local/ignored。
- `docs/architecture/README.md` 和 `docs/architecture/target-architecture.md` 需要判断是否承载了过细的 active phase / queued program 执行状态。
- `.agent/templates/goal-mode-prompt.md` 需要瘦身为模板骨架，不保存固定路径或历史 program 事实。

## 验收

根目录职责清楚，docs 前台只保留 current / target / roadmap / diagrams / decisions。
