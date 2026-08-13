# 重复概念审计

状态：`ARTIFACT_EVIDENCE` / 迁移前审计

## 已发现的重复来源

| 概念 | 旧重复来源 | 本轮唯一归属 |
| --- | --- | --- |
| 历史项目发生了什么 | `docs/project/facts/*`、`project-reconstruction-lab/02-history/*` | `docs/project/history/`（正式摘要）；Lab 只保留候选和恢复过程 |
| Product / Domain / Runtime / Knowledge / Service 的跨层关系 | `docs/project/architecture/architecture.md` 加 11 份专题文档 | `docs/project/architecture/` 四文件；专题原稿归档 |
| Current / Target / Gap / Production Readiness | `docs/status/production-readiness.md`、专题文档 front matter、模块文档 | `docs/project/status/`；架构正文只引用边界 |
| Domain State / Runtime State | Domain、Agent、Data、Product、Module 文档分别描述 | 总体架构保留跨层边界；原专题不再作为入口 |
| Service boundary / deployment | Services、Deployment、Infrastructure module、总体架构 | 总体架构的跨层目标；服务数量仍为未测量 Target/Hypothesis |
| Eval / quality proof | Eval topic、Observability module、facts evaluation history | `docs/evidence/` 当前证据 + 总体架构中的目标验证边界 |
| 11 模块编号 | `docs/project/modules/`、旧 verifier/tests、历史 ADR | 仅 `docs/history/superseded-document-taxonomy/` 的历史材料 |

## 判定规则

同一事实若既出现在历史叙事、Target 说明和 Current 状态中，必须按状态拆开，而不是复制一套新对象。旧文件迁移到归档后，其中的旧路径和旧术语只表示历史来源，不代表 active route。
