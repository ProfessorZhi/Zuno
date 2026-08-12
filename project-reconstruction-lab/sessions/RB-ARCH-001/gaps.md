# RB-ARCH-001 Gap Clusters

本轮 100 个问题结束后才进行聚类。Gap 仍处于 OPEN、RESEARCH_REQUIRED 或 USER_GATE，不因蓝队写出 Target Proposal 而关闭。

## CLUSTER-001

```text
Cluster ID：CLUSTER-001
Gap IDs：GAP-001, GAP-002, GAP-003
Questions：Q001, Q002, Q003, Q004, Q005, Q007, Q092
Failed Claim：Zuno 的历史起点、用户、合作关系和法律场景已经确认。
Root Cause：正式事实源没有原始需求、As-Is Workflow、直接合作证据或用户确认。
Gap Types：BACKGROUND_GAP, PROJECT_REALITY_GAP, RECONSTRUCTION_CONFIDENCE_GAP
Current Evidence：Target Architecture 只证明当前设计，不证明历史。
Required Research：历史 Git/任务/原始面试、用户材料和直接项目证据；公开学校/法院资料只能作为周边 Context。
Suggested Blue Route：PROJECT_FACT_RESEARCH
Status：USER_GATE
```

## CLUSTER-002

```text
Cluster ID：CLUSTER-002
Gap IDs：GAP-004, GAP-005
Questions：Q008, Q011, Q012, Q013, Q014, Q015, Q016, Q017
Failed Claim：Zuno 必须独立拥有当前完整平台，而不是通用平台/成熟子系统的 Adapter。
Root Cause：当前 Build-vs-Buy 仍为 TO_REVIEW，没有 Capability/Contract/Modification Surface/License/Benchmark 证据。
Gap Types：PRODUCT_POSITIONING_GAP, BUILD_BUY_GAP, OVERENGINEERING_GAP
Current Evidence：已有五道 Gate 和 Domain Control Plane 候选，但没有候选项目源码级 Fit Analysis。
Required Research：RAGFlow/Docling/MinerU、GraphRAG/LightRAG、OpenViking/Mem0/Graphiti、Onyx、Coze/Dify 的固定版本 Spike 和替代成本。
Suggested Blue Route：ADOPT_EXTEND_REVIEW
Status：RESEARCH_REQUIRED
```

## CLUSTER-003

```text
Cluster ID：CLUSTER-003
Gap IDs：GAP-006, GAP-007, GAP-021
Questions：Q018, Q019, Q020, Q021, Q022, Q023, Q024, Q025, Q096, Q097, Q098
Failed Claim：团队、个人贡献、开发过程和交付责任可以按当前 11 模块直接复述。
Root Cause：没有已确认团队人数、提交/任务映射、评审发布记录、接替关系或个人贡献材料。
Gap Types：OWNERSHIP_GAP, DELIVERY_PROCESS_GAP, RESUME_CLAIM_RISK
Current Evidence：正式事实明确保持 UNKNOWN；目标 Ownership 只能回答未来责任。
Required Research：历史 Git/任务/会议/发布/面试原始材料；用户最小确认团队和本人边界。
Suggested Blue Route：PROJECT_FACT_RESEARCH
Status：USER_GATE
```

## CLUSTER-004

```text
Cluster ID：CLUSTER-004
Gap IDs：GAP-008, GAP-024
Questions：Q004, Q005, Q006, Q008, Q011, Q021, Q022, Q025, Q036, Q048, Q095, Q100
Failed Claim：当前 Legal Domain Model、11 逻辑模块和复杂治理与真实业务规模相匹配。
Root Cause：历史业务和规模未知，缺少最小版本、人工基线、范围收缩和成本约束证据。
Gap Types：PROJECT_ARCHITECTURE_ALIGNMENT_GAP, OVERENGINEERING_GAP
Current Evidence：Target 有 Domain Profile、轻量部署和 Defer 原则；没有历史验证。
Required Research：建立真实任务候选、最小落地路径、物理部署/团队约束和复杂度预算。
Suggested Blue Route：SCOPE_DOWN
Status：RESEARCH_REQUIRED
```

## CLUSTER-005

```text
Cluster ID：CLUSTER-005
Gap IDs：GAP-009, GAP-025
Questions：Q010, Q017, Q027, Q028, Q030, Q032, Q034, Q047, Q049, Q050, Q063, Q068, Q094
Failed Claim：Target 中的 Owner、状态、恢复、版本和提交语义已经在 Current 中运行并可证明。
Root Cause：模块文档和 Verifier 证明设计/静态约束，但缺少完整 Runtime Trace、故障演练、Migration 和生产证据；另有缺失的 `.agent/references/interview-red-team-workflow.md` 引用。
Gap Types：CURRENT_EVIDENCE_GAP, FAILURE_RECOVERY_GAP, WORKFLOW_GAP
Current Evidence：Production Readiness 为 NOT_ESTABLISHED，当前没有 active implementation program。
Required Research：代码/测试/Trace/Eval 对照清单；确认缺失 Reference 是否需要后续治理修复。
Suggested Blue Route：IMPLEMENTATION_TASK
Status：USER_GATE
```

## CLUSTER-006

```text
Cluster ID：CLUSTER-006
Gap IDs：GAP-010, GAP-011
Questions：Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q088
Failed Claim：Agentic GraphRAG/Graph 总体优于普通 RAG，且当前参数与效果已经证明。
Root Cause：Target 已转向 Conditional Evidence Retrieval，但缺少按 Query Class 的 Baseline、Hard Case、参数、延迟、成本和错误 Graph 评测。
Gap Types：ARCHITECTURE_GAP, BUILD_BUY_GAP, IMPLEMENTATION_DEPTH_GAP, MEASUREMENT_GAP
Current Evidence：ADR 0006 是 accepted-target overlay；明确不构成实现或质量证据。
Required Research：比较 Fixed Vector、Fixed Hybrid、Always Graph、Agentic RAG without Graph、Conditional Graph Retrieval。
Suggested Blue Route：ADOPT_EXTEND_REVIEW
Status：RESEARCH_REQUIRED
```

## CLUSTER-007

```text
Cluster ID：CLUSTER-007
Gap IDs：GAP-012
Questions：Q059, Q060, Q061, Q062, Q063, Q064, Q070, Q098
Failed Claim：Memory 已经真实支持抽取、冲突、时间、污染、权限和 Context Pack。
Root Cause：Memory 文档有完整 Target 语义，但没有历史需求、当前实现、数据样本、召回和污染测试证据。
Gap Types：ARCHITECTURE_GAP, IMPLEMENTATION_DEPTH_GAP, SECURITY_GAP, CURRENT_EVIDENCE_GAP
Current Evidence：Target 区分 Memory Governance 与可替换 Memory Engine；真实 Backend 和使用状态未知。
Required Research：Memory Engine Fit Analysis、写入/冲突/失效/召回 Benchmark、权限与污染 Fault Test。
Suggested Blue Route：ADOPT_EXTEND_REVIEW
Status：RESEARCH_REQUIRED
```

## CLUSTER-008

```text
Cluster ID：CLUSTER-008
Gap IDs：GAP-013, GAP-014, GAP-015
Questions：Q030, Q031, Q032, Q033, Q035, Q036, Q037, Q038, Q039, Q040, Q041, Q042, Q043, Q044, Q045, Q065, Q066, Q067, Q068, Q069, Q071
Failed Claim：Agent Core、Model Gateway、Fine-tuning 和 Legal Profile 已按 Target 真实实现或产生历史贡献。
Root Cause：Target 设计与模型/Agent/训练现实没有被代码、配置、实验、Provider、Artifact 或个人 Ownership 连接起来。
Gap Types：IMPLEMENTATION_DEPTH_GAP, PROJECT_REALITY_GAP, MEASUREMENT_GAP, CURRENT_EVIDENCE_GAP
Current Evidence：Model Provider/Hosted/Self-hosted/Fine-tuning 均 UNKNOWN；LangGraph 只在 Target/候选层出现。
Required Research：模型配置、调用 Trace、训练实验、Artifact Lineage、Agent Runtime 代码和任务 Ownership。
Suggested Blue Route：PROJECT_FACT_RESEARCH
Status：USER_GATE
```

## CLUSTER-009

```text
Cluster ID：CLUSTER-009
Gap IDs：GAP-016, GAP-017, GAP-018
Questions：Q034, Q037, Q038, Q046, Q047, Q048, Q049, Q076, Q081, Q083, Q084, Q085, Q086, Q087, Q098
Failed Claim：企业级部署、Tool Effect、权限委派、Security Epoch 和审计已经可运行。
Root Cause：Current 环境/用户/Provider/Connection/Grant/故障演练和安全证据缺失。
Gap Types：PROJECT_REALITY_GAP, FAILURE_RECOVERY_GAP, SECURITY_GAP, CURRENT_EVIDENCE_GAP
Current Evidence：Target 对执行链和安全交集定义完整，Production Readiness 未建立。
Required Research：Provider Conformance、Tool/Grant/Approval Trace、权限撤销 Fault Test、部署/容量/灾备证据。
Suggested Blue Route：SECURITY_REVIEW
Status：RESEARCH_REQUIRED
```

## CLUSTER-010

```text
Cluster ID：CLUSTER-010
Gap IDs：GAP-019, GAP-020, GAP-022, GAP-023
Questions：Q041, Q044, Q045, Q046, Q077, Q078, Q079, Q080, Q081, Q088, Q089, Q090, Q091, Q092, Q093, Q094
Failed Claim：系统质量、基础设施稳定性、上线收益和模型/检索改进已经被测量。
Root Cause：缺少固定 Dataset、Baseline、Trace、账单、压测、用户反馈、故障演练和 Release Gate 结果；基础题只证明知识，不证明项目实现。
Gap Types：MEASUREMENT_GAP, CURRENT_EVIDENCE_GAP, FUNDAMENTAL_GAP, PROJECT_REALITY_GAP
Current Evidence：当前 Quality 为 not_yet_proven，Measurement blocked_not_measured。
Required Research：分层 Eval、Load/Fault Test、成本和线上证据；基础题另行补强。
Suggested Blue Route：EVAL_TASK
Status：RESEARCH_REQUIRED
```
