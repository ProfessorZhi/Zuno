# PHASE02：根目录与 Docs Hygiene
> 状态：pending。等待 PHASE01 审计结果后执行。

## 目标

清理根目录和 docs 前台，把历史、生成物、临时文件、旧入口归位。

根目录目标是少而稳定：只保留必要项目入口、一等目录和 package/config 文件。对 `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 等先确认 tracked 状态、用途和 `.gitignore`，再决定移动、归档、忽略或删除。

`docs/` 前台只承载正式真相；历史材料、旧计划、旧审计和生成报告进入 `docs/history/` 或被 `.gitignore` 排除。

## 验收

根目录职责清楚，docs 前台只保留 current / target / roadmap / diagrams / decisions。
