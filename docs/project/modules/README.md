# Legacy Modules（Superseded / History）

本目录保存上一阶段 `11 Logical Modules` 的迁移材料，不再是 Zuno 的 Canonical Target Architecture，也不与 `docs/project/product/`、`domain/`、`agents/`、`knowledge/`、`services/`、`data/`、`security/`、`eval/`、`deployment/` 并列拥有事实。

## Disposition

| Legacy 文档 | 新 Canonical 入口 | 状态 |
|---|---|---|
| 01 Product Surface | `../product/product-architecture.md` | Superseded |
| 02 Input / Document Ingestion | `../knowledge/knowledge-evidence-architecture.md` | Superseded |
| 03 Knowledge / GraphRAG | `../knowledge/knowledge-evidence-architecture.md` | Superseded |
| 04 Model Gateway | `../agents/agent-platform.md` + `../services/service-architecture.md` | Superseded |
| 05 Memory & Context | `../agents/agent-platform.md` + `../domain/legal-domain-model.md` | Superseded |
| 06 Agent Core | `../agents/agent-platform.md` + `../agents/multi-agent-runtime.md` | Superseded |
| 07 Capability / Skill | `../agents/agent-platform.md` | Superseded |
| 08 Tool Runtime | `../services/service-architecture.md` + `../security/security-architecture.md` | Superseded |
| 09 Security | `../security/security-architecture.md` | Superseded |
| 10 Observability / Eval | `../eval/legal-eval-and-benchmark.md` | Superseded |
| 11 Infrastructure | `../services/service-architecture.md` + `../deployment/microservice-deployment.md` | Superseded |

旧文件保留只为 Git 可追溯、QA 迁移和历史理解；新决策不得只修改旧文件。冲突时以新 Taxonomy、ADR 和专题 Owner 文档为准。完成链接迁移和历史摘要后，raw construction materials 是否移入 `docs/history/` 需有明确 disposition，不能以“目录干净”为理由删除。
