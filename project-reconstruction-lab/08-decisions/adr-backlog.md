# ADR Backlog

候选 ADR 仅作排队，不自动创建：

| Topic | Trigger | Prerequisite |
|---|---|---|
| Python-only backend | 用户 Target Constraint | workload/team/schema comparison |
| Microservice target boundaries | Target Constraint 已存在 | 每服务独立 scaling/failure/security evidence |
| Domain State vs Runtime State | Domain-aware Runtime survives | state reconciliation test |
| Multi-Agent model | Single Agent Kill Test 失败 | task/cost/failure benchmark |
| Conditional Graph Retrieval | Hybrid Kill Test 失败 | query-class benchmark |
| OpenViking provider boundary | 历史 Artifact 与 provider conformance | Memory contract/spike/license |
| Architecture Lab taxonomy | 本轮目录重构 | entrypoint/link verifier |

ADR 只能记录决策和 reversal criteria，不复制事实矩阵。
