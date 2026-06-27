# 当前执行状态

当前 active program 就是 `.agent/programs/` 根目录这一层。不要再进入子目录找当前计划。

## 状态

- 当前 program：`zuno-architecture-surface-cleanup-v1`。
- 旧 `zuno-target-runtime-v2` 当前前台 phase 已移除，历史证据保留在 `docs/history/programs/zuno-target-runtime-v2/`。
- 已完成并合入 `main`：`PHASE01` 公开封面与架构叙事收口、`PHASE02` 本地 Agent Skill System 收口、`PHASE03` tools / tests 工作流防回归。
- 当前待打开 phase：`PHASE04` 后端六层 facade 分层。
- 后续剩余 phase：`PHASE05` 大文件轻拆、`PHASE06` 架构图与 HTML 展示页。
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

PHASE01-03 已完成并推送。当前可以打开 PHASE04，但 PHASE04 只能做后端六层 facade re-export 和聚焦 import tests；不要删除旧路径、不要改 runtime 行为、不要改 public API、不要改 DB schema。PHASE05 大文件轻拆必须先从只读审计和拆分计划开始，PHASE06 架构图/HTML 不能引入第二套图谱真相。

正式面向人的状态汇总在 `docs/architecture/roadmap.md`。已完成或被替换的 program 归档在 `docs/history/programs/`。
