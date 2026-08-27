# Current Program Reference

state: `no-active`
active_program: `none`
queued_program: `none`

当前没有 active implementation 或 active architecture design program。项目故事由 `docs/project/` 维护，总体架构由 `docs/architecture/` 维护，Red / Blue 原始记录由 `docs/maintenance/history/red-blue/` 维护但不作为默认上下文。

下一次架构设计 / 实现 Program 必须由用户明确激活；下一次实现必须通过 Architecture Gate 和 Evidence Gate。历史 Round、旧施工材料和已删除工作区通过 Git history 追溯，不回到 current tree。

Red / Blue 已使用专用运行中心 `.agent/red-blue/`；当前 Round 指针见 `.agent/red-blue/current.md`。机器总路由由 `.agent/system.yaml` 与 `.agent/references/` 负责，人类可读 Red / Blue 流程见 `docs/maintenance/red-blue/`，通用仓库协作见 `docs/maintenance/agent-workflow/`。

SUPERSEDED / RETIRED：旧 facts 分拆、旧 reconstruction workspace、旧编号模块入口，以及把 Red / Blue runtime 混在 `.agent/programs/` 中的旧路由。