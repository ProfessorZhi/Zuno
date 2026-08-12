# USER-ARCHITECTURE-GATE-001 — User Decision Package

```text
Status: APPROVED
User decision: APPROVE
Canonical Sync: APPLIED
Approved scope: Canonical Part-A Target Architecture only
Architecture state: ACCEPTED_TARGET
```

本包记录用户明确的 `APPROVE`。批准只接受当前 Part-A 作为下一阶段 Canonical Target；不把
Target 标记为 `IMPLEMENTED`、`VERIFIED`、`MEASURED` 或 `PRODUCTION_PROVEN`。

批准条件：服务数量和物理边界仍可按证据合并/拆分；OpenViking 只是可替换 Memory Provider；
所有未测量的质量、效率、安全和竞品优势仍保持 Hypothesis。

## 1. Product / Architecture Thesis

Target 产品候选仍为 Legal Case Intelligence & Agent Platform：以案件/法律 Domain State、
证据语义和专业能力 Contract 作为可验证差异；Agent Runtime、Knowledge Provider 和
部署单元可以替换。该命题是 Target，不是历史项目的 Current 证明，也不是已优于 WorkBuddy
或其他平台的事实。

## 2. Part-A 当前 Target

Part-A 的最小边界是：Canonical Domain State、Runtime Control State、Knowledge Projection、
Tool Effect Receipt、Security/Review Contract 和 Eval Contract 分离；Provider 只产生
Proposal/Candidate/Observation/Reference/Receipt，Canonical Owner 才能提交业务事实。

## 3. Canonical State Ownership

```text
Domain Service      → accepted Matter/DocumentVersion/Fact/Evidence/Finding/Decision
Agent Runtime       → Run/Plan/Step/Checkpoint/Resume control state
Knowledge           → parsing/index/retrieval/projection/evidence candidate lineage
Tool/Sandbox        → ToolAttempt/EffectReceipt/Provider Operation/Reconciliation
Security            → authorization/approval/epoch/secret decision
Eval                → dataset/metric/raw result/release decision
```

跨边界传 Proposal、Reference、Snapshot、Receipt 或 ID，不复制最终事实。

## 4. Runtime vs Domain State

PostgreSQL Domain State 是业务事实 Owner；LangGraph Checkpoint（如保留）只保存 Graph
Control/Execution State。恢复时 Domain Generation、EffectReceipt 和事务结果优先；Checkpoint
可重建，不能反向制造 Domain Fact。该设计仍待 I-P0 实现证据。

## 5. Tool Side-effect Contract

高风险 Effect 必须有 Prepare、execute-time authorization、Approval（如需要）、Idempotency
Key、Provider Operation ID、EffectReceipt、`outcome_unknown` 和 Reconciliation。未知结果先
对账，不能直接重试。当前 Q061/Q063/Q064/Q070 仍未形成 closure-grade evidence。

## 6. Memory Contract / Provider Boundary

Memory 保存可过期、可压缩、可删除的上下文/经验；不拥有 Case Fact、Evidence 或 Finding。
OpenViking 等 Provider 只能通过 Context/Memory Contract 接入，不能直接成为 Canonical
Domain Store；历史接入事实与当前仓库实现继续分开。

## 7. Knowledge / Graph Boundary

Knowledge 负责检索、Evidence Candidate、Citation Lineage 和 Projection。Graph 是 Conditional
Projection/Provider，只有 Query-Class Benchmark 证明收益才保留；Graph Path 必须回到
SourceSpan/DocumentVersion，不能直接成为法律事实。

## 8. Database / Projection Ownership

Domain DB 保存当前业务事实及版本；Vector/BM25/Graph/Cache 是可重建 Projection，带
DocumentVersion/IndexVersion/Provenance。共享 PostgreSQL 的物理部署不是本轮已实现事实，
物理拆分仍由 scaling、failure、security 和 lifecycle 证据决定。

## 9. Microservice Boundary Candidates

候选物理边界为 Platform/Domain、Agent Runtime、Knowledge、Tool/Sandbox，以及可选的
Eval/Observability Worker。候选服务不是 11 Modules 的机械映射；每个边界仍需独立扩缩容、
失败隔离、安全隔离、部署生命周期或数据 Ownership 证据。

## 10. Security / Sandbox Boundary

Tool/Sandbox 是独立安全边界候选，要求 least privilege、network allowlist、secret scoping、
filesystem/process/resource isolation、approval 和 audit。Q066 当前为 P0-X：Target 可以审阅，
但 Docker/Deno 不可用导致安全资格测试未完成。

## 11. Eval Architecture

法律效果使用 Court QA / A-B-C 对照和 Evidence Sufficiency、Citation Correctness、Unsupported
Claim Rate、Conflict/Dispute F1、Fact–Article F1、Reviewer Acceptance 等指标；同时记录
Latency、Token、Cost、Calls、Retrieval Rounds 和 State Reuse。Q039-B 是 P0-E，未测量不得写成质量优势。

## 12. 12 P0 Gate Classification

完整分类见 [closure-classification.md](closure-classification.md)：原始 12 项保持 OPEN，Q039
拆为 Q039-C 与 Q039-B，派生记录共 13 条；`A=0 / I=11 / E=1 / X=1`。

## 13. A-P0

当前 12 项 Final P0 范围内为 `0`。这不表示所有 Target 细节都已被用户接受；若用户在
本包审阅中发现 Canonical Owner、State 或 Failure Contract 的设计矛盾，应新增 A-P0，Gate
不得通过。

## 14. I-P0

`Q005、Q016、Q033、Q039-C、Q053、Q061、Q063、Q064、Q067、Q070、Q097`。它们必须继续
保持 OPEN；本包只为它们提供 Target Contract 和第一批 Implementation Task Candidate，不
把 candidate 变成 active Program。

## 15. E-P0

`Q039-B`。需要冻结 Court QA 数据、参考材料/答案、评审协议和 A/B/C 公平对照，之后才能
报告 MEASURED 结果。没有该证据，不能声称 Zuno 优于通用 Host。

## 16. X-P0

`Q066`。需要可审计的真实 Sandbox 环境和 fault/security test；环境不可用时保持
`BLOCKED_EXTERNAL`，不能用 in-process contract 或目录存在替代。

## 17. Architecture changes made by Red/Blue

本轮对治理的修改是：增加 Closure Class；分离 User Architecture Gate 与 Evidence/Production
Closure；允许 `SURVIVED` 设计在实现前进入用户审阅；将 I/E/X 变成可追踪的后续轨道。用户批准
后，本包的 Part-A Target 已同步到 Canonical Architecture 与专题 Owner 文档；没有修改 Product
Runtime、Schema/Migration 或历史 P0 记录。

## 18. Known Current gaps

- Domain Owner persistence、Plan/Domain 联合写回和四方 recovery store 尚未形成 Current evidence。
- CitationBinder 的 wrong-span provenance 校验仍为已暴露缺口。
- execute-time revoke、完整 Tool Effect receipt chain 和跨服务 trace 尚未形成 closure evidence。
- 真实 Sandbox 不可执行；解释器环境也存在裸 batch verifier 的导入环境差距。

## 19. Benchmark gaps

- Court QA / A-B/C / Legal Effectiveness（Q039-B）。
- Graph、Memory、Multi-Agent 和 Host-vs-Zuno 的消融仍是 Hypothesis，不得提前写成收益。

## 20. External qualification gaps

- Docker/Deno 或等价可审计 Sandbox 运行资格（Q066）。
- 真实 Provider、部署环境、负载、网络和安全环境的资格证据仍未建立。

## 21. Applied Canonical Sync Scope

仅在用户批准后，候选同步范围为：

1. 总架构中的 Gate/State maturity wording；
2. Domain/Runtime/Data/Security/Eval 专题中的 Target Contract 和 evidence-gap 引用；
3. `docs/governance/` 的 Gate policy 已在本轮作为治理变更记录，但不改变 Target→Current；
4. 相关 ADR/Program 引用和 `docs/status/` 的 Current/Gaps（不把本包写成 Current）。

当前 `Canonical Sync Status: APPLIED`。同步写入 `docs/project/architecture/`、Product/Domain/
Agents/Knowledge/Services/Data/Security/Eval/Deployment 专题及 `docs/status/`；没有新增 ADR，
因为 ADR-0008/0009/0010/0011 已记录本次设计决定。

## 22. Proposed first Codex implementation tasks

以下是已具备定义条件、但尚未激活的候选；状态为 `READY_FOR_TASK_DEFINITION`，不能在本轮执行：

1. `TASK-CANDIDATE-001`：Canonical Domain Mutation / Version Contract（Q005）。
2. `TASK-CANDIDATE-002`：PlanVersion ↔ DomainVersion optimistic concurrency / replan（Q053）。
3. `TASK-CANDIDATE-003`：CitationBinder DocumentVersion / SourceSpan provenance guard（Q039-C）。
4. `TASK-CANDIDATE-004`：Tool execute-time authorization and SecurityEpoch revocation（Q061）。
5. `TASK-CANDIDATE-005`：EffectReceipt、`outcome_unknown` 和 reconcile（Q063/Q064/Q070）。
6. `TASK-CANDIDATE-006`：Domain/Checkpoint/Effect/Queue recovery reconciliation（Q016/Q097）。

建议波次：Wave 1=`001/003`；Wave 2=`002/004`；Wave 3=`005`；Wave 4=`006`。

激活前置条件：用户 Gate `APPROVED`、Canonical Sync 完成、Stop Condition 已确认、每项
任务有 Allowed/Forbidden Scope、Migration、Rollback、Test 和 Evidence Acceptance Criteria。
