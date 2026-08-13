# 文档迁移地图

状态：`PROPOSED` / 本轮文档迁移工作材料

| 旧入口 | 新归属 | 操作 | Canonical 结果 |
| --- | --- | --- | --- |
| `docs/project/facts/project-background.md` | `docs/project/history/project-background.md` | MOVE / 人类可读化 | 历史入口 |
| `docs/project/facts/requirements-and-workflows.md` | `docs/project/history/requirements-and-workflows.md` | MOVE | 历史入口 |
| `docs/project/facts/team-and-ownership.md` | `docs/project/history/team-and-ownership.md` | MOVE | 历史入口 |
| `docs/project/facts/development-evolution.md` | `docs/project/history/development-history.md` | MOVE / RENAME | 历史入口 |
| `docs/project/facts/incidents-and-improvements.md` | `docs/project/history/incidents-and-improvements.md` | MOVE | 历史入口 |
| `docs/project/facts/delivery-and-usage.md` | `docs/project/history/delivery-and-usage.md` | MOVE | 历史入口 |
| `docs/project/facts/technology-reality.md` | `docs/project/history/technology-history.md` | MOVE / RENAME | 历史入口 |
| `docs/project/facts/README.md` | `docs/history/superseded-document-taxonomy/project-facts-README.md` | ARCHIVE | 不再作为事实入口 |
| `docs/project/facts/engineering-collaboration.md` | `docs/history/superseded-document-taxonomy/project-facts/engineering-collaboration.md` | ARCHIVE；内容由 team/development 引用 | 原始补充材料 |
| `docs/project/facts/data-and-evaluation-history.md` | `docs/history/superseded-document-taxonomy/project-facts/data-and-evaluation-history.md` | ARCHIVE；内容由 history/status 引用 | 原始补充材料 |
| `docs/project/facts/reuse-and-research-transfer.md` | `docs/history/superseded-document-taxonomy/project-facts/reuse-and-research-transfer.md` | ARCHIVE；研究边界保留在治理/Target说明 | 原始补充材料 |
| `docs/project/{product,domain,agents,knowledge,services,data,security,eval,deployment}/` | `docs/history/superseded-document-taxonomy/project-topics/` | ARCHIVE | 不再作为并行 Canonical |
| `docs/project/modules/` | `docs/history/superseded-document-taxonomy/project-modules/` | ARCHIVE | 上一阶段 11 模块历史材料 |
| `docs/status/production-readiness.md` | `docs/project/status/production-readiness.md` | MOVE | 当前状态入口 |
| 无 | `docs/project/status/README.md` | ADD | 状态目录边界 |
| 无 | `docs/project/status/current-reality.md` | ADD | 当前仓库事实入口 |
| 无 | `docs/project/status/target-status.md` | ADD | Target/Hypothesis/Future 入口 |

## 不做的迁移

- 不修改 `docs/project/architecture/` 的架构决策内容，不增加第五个文件。
- 不修改 Facts 的事实级别，不把候选恢复升级为事实。
- 不修改 ADR，尤其不把本轮目录迁移倒灌成新的架构决策。
- 不启动 Round-007，不创建 Red/Blue Session 或 Candidate Branch。
- 不迁移或删除 `project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-ROUND-006/`。
