# ROUND-001 Gaps and Blocker Burn-down

本文件把逐题 Gap 聚类；Blue Proposal 不会自动关闭 Gap。所有 Gap 当前至少是 `OPEN` 或 `BLUE_PROPOSED`，需要事实恢复、Benchmark、ADR 或实现证据后再重开评审。

## CLUSTER-001

Gap IDs: GAP-V2-001, GAP-V2-002, GAP-V2-003, GAP-V2-005
Questions: Q001, Q002, Q003, Q004, Q005, Q007, Q009, Q075, Q091, Q092, Q100
Category: FACT_GAP
Description: 法院原始工作流、客户 QA/Gold Evidence、业务验收和法律对象真实范围仍未完全恢复。
Why It Matters: 没有真实任务和人工基线，Domain、Graph、Memory 和评测都可能是技术倒推。
Required Evidence: 用户确认、旧 QA/PPT/截图/任务记录、脱敏样例、反馈协议。
User Recall Prompt: 收到什么材料、人工怎样处理、客户 Demo 具体问什么、哪类错误被指出？
Architecture Impact: 可能缩减 Matter/Finding/Review 或改变 Retrieval/Agent 优先级。
Status: OPEN
Resolution: NEEDS FACT RECOVERY

## CLUSTER-002

Gap IDs: GAP-V2-004, GAP-V2-020
Questions: Q008, Q010, Q018, Q029, Q035, Q038, Q041, Q042, Q044, Q049, Q050, Q089, Q090, Q091, Q092, Q095, Q100
Category: BENCHMARK_BLOCKER
Description: WorkBuddy+Legal Backend、Native Runtime、Graph、Memory、Single Agent 等替代方案尚无受控测量。
Why It Matters: 没有 A/B/C 和消融不能证明 Zuno Runtime 或专业组件创造增益。
Required Evidence: 固定模型/语料/工具/预算、held-out 任务、逐阶段指标、成本/延迟/调用 Trace、Reviewer 结果。
Architecture Impact: C≈B 时删除 Native Runtime；Graph/Memory/Multi-Agent 可能 DEFER/DELETE。
Status: OPEN
Resolution: NEEDS BENCHMARK

## CLUSTER-003

Gap IDs: GAP-V2-006, GAP-V2-007, GAP-V2-014
Questions: Q021, Q022, Q023, Q024, Q025, Q026, Q030, Q031, Q032, Q033, Q034, Q035, Q053, Q059, Q074
Category: RUNTIME_STATE_GAP
Description: Plan、Branch、Budget、Replan、HITL、Domain Generation 和 Runtime Checkpoint 的 Current reconciliation trace 未证明。
Why It Matters: 设计可解释不代表 Crash/Resume/Concurrent Plan 已实现。
Required Evidence: failure injection、checkpoint/domain 双写矩阵、PlanVersion/epoch/Join tests。
Architecture Impact: 可能削薄 LangGraph/Native Runtime，或先采用普通 Workflow。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-004

Gap IDs: GAP-V2-009, GAP-V2-010
Questions: Q006, Q028, Q036, Q037, Q038, Q039, Q040, Q041, Q042, Q043, Q044, Q050, Q057
Category: KNOWLEDGE_GRAPH_GAP
Description: Evidence Sufficiency、Graph Projection、Index Version、Conditional Retrieval 和 Graph Kill Benchmark 未执行。
Why It Matters: Graph 可能只是投影成本，不能代替 Domain Evidence。
Required Evidence: Query Class 数据集、Vector/Hybrid/Always Graph/Conditional 对照、source span/版本/权限、错误边重建测试。
Architecture Impact: Graph 可能降为 Conditional Provider 或删除。
Status: OPEN
Resolution: NEEDS BENCHMARK

## CLUSTER-005

Gap IDs: GAP-V2-011, GAP-V2-012
Questions: Q015, Q017, Q047, Q048, Q049, Q100
Category: MEMORY_GAP
Description: Memory 的历史用途、OpenViking 接入细节、Scope/Authority/Conflict/Recall/污染和 Provider Fit 未完整恢复/验证。
Why It Matters: Memory 不能成为隐性 Domain Fact Store，也不能因为历史参与就成为 Current。
Required Evidence: 用户具体任务回忆、旧 Adapter/API/Trace、Memory benchmark、权限/污染 fault test。
Architecture Impact: OpenViking 可能只是 Provider、Matter DB+Checkpoint 可能足够。
Status: OPEN
Resolution: NEEDS FACT RECOVERY + BENCHMARK

## CLUSTER-006

Gap IDs: GAP-V2-013
Questions: Q016, Q025, Q040, Q051, Q052, Q056, Q059, Q073, Q078, Q094, Q097
Category: DATA_RECOVERY_GAP
Description: Domain DB、Projection、Cache、Checkpoint、Outbox 和 Trace 的实际 ownership/rebuild/restore 证据缺失。
Why It Matters: 多存储架构的核心风险是双写、丢失和事实冲突。
Required Evidence: owner registry、restore/rebuild、outbox、checkpoint failure 和 trace completeness tests。
Architecture Impact: 可能合并数据层或推迟服务拆分。
Status: OPEN
Resolution: NEEDS ADR + IMPLEMENTATION EVIDENCE

## CLUSTER-007

Gap IDs: GAP-V2-015, GAP-V2-016
Questions: Q027, Q033, Q043, Q048, Q061, Q063, Q064, Q065, Q066, Q067, Q070, Q096, Q100
Category: SECURITY_BLOCKER
Description: 权限前置过滤、Approval/Epoch、Tool Scope、Sandbox、Prompt Injection、Secret Trace 和 Effect Gate 尚无完整测试。
Why It Matters: 任何安全/审批绕过都是 P0，无论 Round 分数多高都不能通过。
Required Evidence: cross-tenant、revocation、injection+tool、secret leakage、sandbox boundary、stale credential、approval replay tests。
Architecture Impact: Tool/Sandbox 边界可能加强或合并，但不能移除最小安全 Contract。
Status: OPEN
Resolution: NEEDS SECURITY REVIEW

## CLUSTER-008

Gap IDs: GAP-V2-017
Questions: Q064, Q068, Q071, Q072, Q073, Q076, Q077, Q078, Q080, Q097, Q100
Category: FAILURE_BLOCKER
Description: Queue/Worker/Effect/Lease/Unknown Outcome/Retry Storm 的运行参数、故障演练和对账证据缺失。
Why It Matters: 不可逆副作用和重复执行必须有可恢复语义。
Required Evidence: idempotency key、provider operation ID、lease/fencing、DLQ、timeout/cancel、fault injection。
Architecture Impact: 可能把部分异步能力降为同步或外部化，但不能靠“重试”隐藏未知结果。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-009

Gap IDs: GAP-V2-018
Questions: Q013, Q055, Q069, Q080, Q081, Q082, Q083, Q084, Q085, Q087, Q088, Q100
Category: SERVICE_BOUNDARY_GAP
Description: Microservice Target 已固定，但五服务数量、edge 物理拆分、Knowledge Worker 与 Tool/Sandbox 边界没有 workload/failure/security/lifecycle 证据。
Why It Matters: Microservice 不等于 11 模块或五服务已获批。
Required Evidence: CPU/GPU/IO、队列、SLO、失败域、安全隔离、独立发布和本地开发成本矩阵。
Architecture Impact: 五服务可合并/拆分；逻辑 capability 与 physical service 继续分离。
Status: OPEN
Resolution: NEEDS SERVICE BOUNDARY REVIEW

## CLUSTER-010

Gap IDs: GAP-V2-019
Questions: Q086, Q093, Q094
Category: DEPLOYMENT_OBSERVABILITY_GAP
Description: Developer/Staging/Production profile、Trace、Artifact、Backup/DR、HA 和 Release Rollback 未由运行证据证明。
Why It Matters: Compose/Verifier/Target 文档不能证明 Production Ready。
Required Evidence: profile E2E、load/fault/DR/security/observability/artifact evidence。
Architecture Impact: Production Profile 和 deployment technology 继续 DEFER。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-011

Gap IDs: GAP-V2-022
Questions: Q005, Q011, Q012, Q014, Q016, Q017, Q019, Q020, Q034, Q045, Q100
Category: CONTRACT_GOVERNANCE_GAP
Description: Domain/Capability/Provider/Document/Service/Runtime 的唯一 Owner 和 Contract 已有 Target，但 Current conformance、mutation denial 和 Canonical Write Gate 仍需加强。
Why It Matters: 没有 Contract verifier，语义可能随 Prompt/Provider/文档漂移。
Required Evidence: schema/conformance/mutation/ownership verifier、Debate Trace 到 Canonical Path 的追踪。
Architecture Impact: Kernel 可能缩小为 Contract+Owner；文档 taxonomy 不等于行为证明。
Status: BLUE_PROPOSED
Resolution: NEEDS ADR + VERIFIER

## CLUSTER-012

Gap IDs: GAP-V2-023
Questions: Q045, Q046, Q087, Q093, Q099
Category: BUILD_BUY_LICENSE_GAP
Description: 法律研究、OpenViking、RAG/Graph/Memory Provider 的源码、模型、数据、License、升级和退出路径未完成逐项审查。
Why It Matters: Public GitHub/论文不自动等于可商业复用。
Required Evidence: official source/license、SBOM、modification surface、adapter spike、migration/exit plan。
Architecture Impact: Adopt/Extend/Build/Delete 可能改变。
Status: OPEN
Resolution: NEEDS BUILD_BUY_REVIEW

## CLUSTER-013

Gap IDs: GAP-V2-024
Questions: Q062, Q071, Q098
Category: PERSONAL_OWNERSHIP_GAP
Description: 用户确认的 Agent/Memory/OpenViking/Tool Calling 参与范围已有锚点，但具体任务、文件、输入输出、Bug、调试和验证仍未知。
Why It Matters: 不能把团队、框架或 Target 架构写成个人实现。
Required Evidence: 用户场景回忆、旧提交/任务/Review/截图；不确定部分保持 UNKNOWN。
Architecture Impact: 影响面试叙事和实施归属，不直接改变 Domain Target。
Status: OPEN
Resolution: NEEDS FACT RECOVERY

## Blocker Burn-down

| Blocker | Related Clusters | Current Decision | Owner | Status |
|---|---|---|---|---|
| Concept Blocker | 001, 002, 005 | 保持最小 Domain/Host 假设 | Product/Domain/Eval | OPEN |
| Fact Blocker | 001, 005, 013 | 进入 Fact Recovery Queue | Facts Owner / User | OPEN |
| Contract Blocker | 003, 006, 011 | 补 Contract/Mutation/Owner 验证 | Domain/Runtime/Data | OPEN |
| State Blocker | 003, 006 | 双状态、版本和 stale 对账 | Runtime/Domain | OPEN |
| Failure Blocker | 006, 008 | Receipt/Idempotency/Reconcile | Tool/Runtime/Data | OPEN |
| Security Blocker | 007 | 先做安全测试再宣称通过 | Security/Tool | OPEN |
| Data Blocker | 006 | Source/Projection/Cache/Checkpoint 分层 | Data/Knowledge | OPEN |
| Benchmark Blocker | 002, 004, 005 | A/B/C、Graph、Memory、Agent 消融 | Eval | OPEN |
| Implementation Evidence Blocker | 003, 008, 009, 010 | Trace/Fault/E2E/DR | Engineering | OPEN |

## Resolution Routing

```text
Fact Recovery：CLUSTER-001 / 005 / 013
Benchmark：CLUSTER-002 / 004 / 005
ADR / Contract：CLUSTER-003 / 006 / 011
Security Review：CLUSTER-007
Service Boundary Review：CLUSTER-009
Implementation Evidence：CLUSTER-006 / 008 / 010
Build-vs-Buy / License：CLUSTER-012
```
