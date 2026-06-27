# 当前执行状态

当前 active program 就是 `.agent/programs/` 根目录这一层。不要再进入子目录找当前计划。

## 状态

- 当前 program：`zuno-architecture-surface-cleanup-v1`。
- 旧 `zuno-target-runtime-v2` 当前前台 phase 已移除，历史证据保留在 `docs/history/programs/zuno-target-runtime-v2/`。
- 已完成并合入 `main`：`PHASE01` 公开封面与架构叙事收口、`PHASE02` 本地 Agent Skill System 收口、`PHASE03` tools / tests 工作流防回归、`PHASE04` 后端六层 facade 分层、`PHASE05` 大文件轻拆只读审计与计划、`PHASE06` 架构图与 HTML 展示页。
- 当前待打开 phase：无。
- 后续剩余 phase：无；下一步是按 [closure-checklist.md](closure-checklist.md) 做 program closure、状态归档和后续 program 决策。
- 下一轮候选短期目标：目标架构继续升版、本地文档系统和工作流自洽、文件夹继续分门别类、架构 HTML 重做清晰。
- 当前执行顺序以 [implementation-roadmap.md](implementation-roadmap.md) 和各 phase 文件为准。

## 当前计划文件

- [implementation-roadmap.md](implementation-roadmap.md)
- [PHASE01_public-architecture-surface.md](PHASE01_public-architecture-surface.md)
- [PHASE02_local-agent-skill-system.md](PHASE02_local-agent-skill-system.md)
- [PHASE03_tools-tests-guardrails.md](PHASE03_tools-tests-guardrails.md)
- [PHASE04_backend-facade-layers.md](PHASE04_backend-facade-layers.md)
- [PHASE05_large-file-light-split.md](PHASE05_large-file-light-split.md)
- [PHASE06_architecture-diagrams-html.md](PHASE06_architecture-diagrams-html.md)
- [closure-checklist.md](closure-checklist.md)

## 停止线

PHASE01-06 已完成并推送。当前不要继续追加新 feature，也不要把 PHASE04 facade 写成旧代码已经物理迁移完成。PHASE05 只完成了只读审计和拆分计划，不等于已经拆分 `general_agent.py`、capabilities、retrieval orchestrator 或 fusion。PHASE06 已完成三张核心图和 HTML 生成/同步规则，不要再引入第二套图谱真相。

正式面向人的状态汇总在 `docs/architecture/roadmap.md`。已完成或被替换的 program 归档在 `docs/history/programs/`。

下一轮如果继续推进短期四目标，必须新开 program，并从 `PHASE01` 开始编号；不要在当前已完成 program 里继续追加 `PHASE07`。
