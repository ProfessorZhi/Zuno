# 当前执行状态

当前 active program 就是 `.agent/programs/` 根目录这一层。不要再进入子目录找当前计划。

## 状态

- 当前 program：`zuno-architecture-surface-cleanup-v1`。
- 旧 `zuno-target-runtime-v2` 当前前台 phase 已移除，历史证据保留在 `docs/history/programs/zuno-target-runtime-v2/`。
- 当前待打开 phase：`PHASE01` 公开封面与架构叙事收口。
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

不要在 PHASE01 没有完成 README、docs/architecture 和 Mermaid 三图的公开叙事收口前打开 PHASE02。不要在 PHASE02 没有把 `.agent` 定义为本地 Skill System、补齐 `system.yaml` 路由和模板边界前打开 PHASE03。不要在 PHASE03 没有把 verify / tests guard 更新完成前打开 PHASE04。

正式面向人的状态汇总在 `docs/architecture/roadmap.md`。已完成或被替换的 program 归档在 `docs/history/programs/`。
