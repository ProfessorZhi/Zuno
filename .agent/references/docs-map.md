# 文档同步 Skill

当任务触碰 `docs/`、`.agent/`、`AGENTS.md`、README、架构、状态、ADR、治理或术语边界时使用。

## 唯一正式入口

```text
docs/project/architecture/ = 总体架构四文件
docs/project/history/      = 历史事实与 UNKNOWN
docs/project/status/       = Current / Target / Production Readiness
docs/decisions/            = ADR
docs/governance/           = Owner、写作和门禁治理
docs/evidence/             = 可复现 Current 证据
docs/history/              = 批准历史和 Superseded 原稿
```

旧 `docs/project/facts/`、专题目录和 `modules/` 已迁入 `docs/history/superseded-document-taxonomy/`，不再是 active route。`project-reconstruction-lab/` 是调查、恢复和 Red/Blue 工作区，不拥有正式架构事实。

## 正式阅读顺序

```text
历史：     docs/project/history/README.md → 当前状态 → 总体架构
架构：     docs/project/architecture/architecture.md → ADR/governance → status/evidence
工程：     architecture → current-reality → target-status → code/evidence
面试：     history/team → history/development → history/incidents → architecture
```

`Current` 必须有代码、Migration、Test、Trace 或 Eval 证据；Target/Hypothesis 不得偷换成 Current。逻辑能力、服务、Worker、进程、容器、数据库和团队不做一一映射。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 历史项目发生了什么 | `docs/project/history/` |
| 当前仓库被什么证明 | `docs/project/status/current-reality.md` |
| Target 处于什么状态 | `docs/project/status/target-status.md` |
| 生产是否已证明 | `docs/project/status/production-readiness.md` |
| 跨层架构为什么这样设计 | `docs/project/architecture/architecture.md` |
| 图形如何展示 | `architecture-views.md` + `architecture.html` |
| 可复现证据 | `docs/evidence/` |

## Focused verification

```powershell
git diff --check
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

项目重建与 Red/Blue 任务另读 `project-reconstruction-lab/README.md` 以及对应 Session；Round-006 immutable evidence 不得修改，Round-007 只有 `READY / NOT_STARTED` 状态。
