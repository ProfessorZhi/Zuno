# Superseded Document Taxonomy

本目录保存本轮重构前的原始文档材料。它们由 Git 迁移而来，保留用于审计、考古和回溯，不再是当前 Canonical 入口。

## 子目录

- `project-facts-README.md` 与 `project-facts/`：旧事实矩阵及补充材料；当前历史入口是 [`../../project/history/README.md`](../../project/history/README.md)。
- `project-topics/`：旧 Product、Domain、Agent、Knowledge、Service、Data、Security、Eval、Deployment 专题；当前跨层架构入口是 [`../../project/architecture/architecture.md`](../../project/architecture/architecture.md)。
- `project-modules/`：上一阶段 11 Logical Modules；它们不是 11 个服务，也不是当前模块数量结论。

## 规则

归档材料中的旧路径、旧术语和旧分层只表示当时的文档组织方式。它们不得被 `.agent/`、默认入口、当前状态或新 verifier 当作 active Canonical Source。任何新结论必须写回 `docs/project/` 的当前入口、`docs/decisions/`、`docs/governance/` 或 `docs/evidence/`。
