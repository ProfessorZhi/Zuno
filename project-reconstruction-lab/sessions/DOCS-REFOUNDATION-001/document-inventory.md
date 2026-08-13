# 文档重构盘点

状态：`ARTIFACT_EVIDENCE` / 工作材料

## 盘点范围

本盘点以本轮基线 `5288a1d680f339019d56e07099748895c57f8399` 为准，目标是区分当前仓库中的历史材料、当前状态、Target 架构和验证入口。它不是新的 Canonical Architecture，也不改变任何事实、ADR 或 Runtime。

## 当前形态

| 区域 | 基线内容 | 问题 | 处置 |
| --- | --- | --- | --- |
| `docs/project/facts/` | 事实 README、背景、团队、演进、交付、技术现实，以及若干扩展事实文档 | 历史事实与项目知识入口绑定，且扩展文档没有统一阅读层 | 迁入 `docs/project/history/`；扩展原稿归档 |
| `docs/project/architecture/` | 四文件总体架构展示面 | 文件数量边界合理，但正文仍路由到旧专题 Taxonomy | 保留四文件，改为跨层唯一架构入口 |
| `docs/project/{product,domain,agents,knowledge,services,data,security,eval,deployment}` | 11 份专题 Target 文档 | 与总体架构形成第二组 Canonical 入口 | 合并语义到总体架构/ADR/治理入口后归档原稿 |
| `docs/project/modules/` | 上一阶段 11 个逻辑模块及模块附录 | 旧编号仍容易被误读为当前架构边界 | 归档为 Superseded 原始材料，不再作为入口 |
| `docs/status/` | Production Readiness | 状态入口与项目入口分离，且路径被旧文档广泛引用 | 迁入 `docs/project/status/`，旧根路径不再作为 Canonical |
| `docs/history/` | 已批准的架构演进、Program 摘要 | 适合保存批准历史，不适合放整组旧专题原稿 | 新增明确的 Superseded taxonomy 子目录 |
| `project-reconstruction-lab/` | 事实恢复、Red/Blue、Candidate 和会话记录 | 不应替代正式 `docs/` | 继续作为调查和攻击工作区；本轮只新增迁移审计材料 |

## 处置原则

1. `docs/project/architecture/` 继续严格只有 `README.md`、`architecture.md`、`architecture-views.md`、`architecture.html`。
2. `docs/project/history/` 只回答“历史项目发生了什么”；未知事实继续保留 `UNKNOWN`。
3. `docs/project/status/` 只回答“当前仓库被什么证据证明、Target 处于什么状态、生产是否已证明”。
4. `docs/project/architecture/` 只回答跨层为什么这样设计；不把历史事实或实施计划写进去。
5. 旧专题和 11 模块不删除，迁入 `docs/history/superseded-document-taxonomy/`，并在归档 README 中声明不可作为当前 Canonical。
6. `project-reconstruction-lab/` 的 Session、Candidate、Red/Blue 原始材料不自动晋升为正式文档。

## 目标入口

```text
docs/project/README.md
  ├─ history/       历史项目事实与 UNKNOWN
  ├─ status/        Current / Target / Production Readiness
  └─ architecture/ 总体架构与图展示配对

docs/decisions/     ADR
docs/governance/    Owner、写作和门禁治理
docs/evidence/      可复现 Current 证据
docs/history/       批准历史与 Superseded 原稿
project-reconstruction-lab/
                   调查、攻击、候选和会话材料
```
