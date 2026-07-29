# Production Readiness

status: implementation_available_measurement_blocked

本文只维护 Current、Gap、Measurement 和 Production Readiness 的状态事实源，不承担完整 Target 架构设计。完整产品与运行架构以 `docs/architecture/architecture.md` 和 `docs/modules/` 为准。

## Current

Zuno 当前前台定位是 Lean Complete Agentic GraphRAG Product：本地优先、短期可闭环、可演示、可评测、可恢复的企业知识库 Agent 产品。

已证明的状态边界：

- PHASE04 completed：PostgreSQL、RabbitMQ、MinIO / S3-compatible Object Store、官方 LangGraph PostgreSQL Checkpointer、Backup/Restore、Generic Replay Framework、Fault Recovery 和 Operator Readiness 已有本地证据；SQLite、本地对象存储和本地队列只作为 Developer/CI adapter。
- PHASE05 completed：Security Control Plane 在完整 Phase Scope 内达到 `implementation_available`；不代表 production ready。
- PHASE06 completed：Observability Minimum Black Box 在完整 Phase Scope 内达到 `implementation_available`；不代表 PHASE20 Eval/Release Gate、quality proven 或 production ready。
- PHASE07 completed：Model Gateway Runtime 在完整 Phase Scope 内达到 `implementation_available`；不代表 quality proven 或 production ready。
- PHASE08 completed：Goal02 final closure 已恢复传输并完成有限 Closure Review；不代表 production ready。
- PHASE11 completed：Goal02 final closure 已恢复传输并完成有限 Closure Review；不代表 production ready。
- PHASE09 completed：Goal03 Wave A 已完成 Product Surface Backend Runtime 默认 Product Runtime、Owner dispatch、Projection/SSE/AvailableAction/Cutover focused suites 与 Product verifier；不代表 PHASE10 或 production readiness。
- PHASE12 completed：Goal03 Wave A 已完成 KnowledgeVersion / Snapshot / Index Visibility / Cutover / Standard RAG durable port；Elasticsearch BM25、Milvus Vector、Neo4j Graph 均有容器化 service readback integration；不代表 PHASE18/20 quality gate 或 production readiness。
- PHASE13 completed：Goal03 Wave B 已完成 Memory and Context Governance Runtime 默认 Agent post-turn 接线，Capture Intent、Candidate、Governance Decision、Memory Record/Version、ContextPack、Compression Trace 和 Memory Use Trace 均由 PostgreSQL Repository/UoW 持久化；不代表 PHASE19 Reflexion 或 production readiness。
- PHASE14 completed：Goal03 Wave A 已完成 Capability/Skill Definition、Version、Installation、Selection、Availability、Supply-chain guard、Planner Snapshot、progressive loading 和旁路 guard focused suites 与 Capability verifier；不代表 PHASE15。
- PHASE15 completed：Goal05 Target Coverage Audit 撤回此前 PHASE15 completed 结论后，已补齐唯一 ToolInvocationGateway、ToolRepository/UoW 默认路径、只读 CLI/OpenAPI/LangChain gateway cutover、旁路 guard、sandbox profile resolution、session isolation、limits/allowlist hash、`tool_sandbox_receipts` 默认 gateway gate，以及真实 Deno + Pyodide/WASM、真实 OCI Process Sandbox 和 Postgres integration 证据；这不代表 production ready。
- PHASE16 completed：Goal04 PR B 已完成 Tool Side Effect and Reconciliation Coordinator Closure 并通过 merge commit `d78426171df0591643af12549a36214a24734f7c` 合并到 main；P16-T01 至 P16-T22、migration、PostgreSQL integration、fault/security gate、bypass zero guard 和 recovery replay 均有本地证据；不代表 production ready。
- PHASE17 completed：Goal04 PR C 已通过 merge commit `4d14ae9e8cd953359c82e51d55279cc123ab47ae` 合并到 main；证据为 `docs/evidence/goal04-phase17-coordinator-closure.md` 和 `docs/evidence/goal04-phase17-startup-audit.md`，Alembic head 为 `20260728_49`；不代表 production ready。
- PHASE18 completed：Goal04 PR D 已完成 Agentic GraphRAG Inner Loop Coordinator Closure 并通过 merge commit `cbc04cb0be16c3915537b82a4f3f743cb7add963` 合并到 main；证据为 `docs/evidence/goal04-phase18-coordinator-closure.md`、`docs/evidence/goal04-phase18-knowledge-retrieval-graph-contract.md` 和 `docs/evidence/goal04-phase18-startup-audit.md`；固定 KnowledgeRetrievalGraph、RetrievalPlan/Round、Profile、multi-retriever dispatch plan、EvidenceLedger/Frontier、Corrective Retrieval、KnowledgeControlProposal、Agent Core accept/reject gate 和默认 PHASE18 runtime path 均有本地验证；不代表 PHASE20 quality gate 或 production readiness。
- PHASE10 completed：Goal04 PR A 已完成 Web/Desktop Product Adaptation Coordinator Closure；证据为 `docs/evidence/goal04-phase10-coordinator-closure.md` 和 `docs/evidence/goal04-phase10-startup-audit.md`；Web/Desktop Product Contract、Product API client、projection-first store、SSE resume/resync、multi interrupt / AvailableAction UI、Evidence/Citation/Artifact/Quality/Blocked view、Desktop versioned bridge、Browser cutover smoke、Desktop smoke、build/lint、legacy DTO/action/bridge removal、rollback fail-closed 和 Alembic clean upgrade 均有本地证据；不代表 production ready。
- PHASE19 completed：Goal04 已完成 Final Synthesis, Publication and Reflexion 本地 Coordinator Closure；证据为 `docs/evidence/goal04-phase19-coordinator-closure.md`；Claim/Citation/Unsupported Claim、FinalCandidate、FinalGate、Publication、RunOutcome、BudgetSettlement、Product Delivery Projection 和 ReflexionCandidate 均有 focused unit/integration/fault 证据；不代表 PHASE20 quality gate 或 production readiness。
- PHASE20 in_progress：Goal05 已新增 Eval Runtime foundation、Query / Report surface 和部分 fault semantics；证据为 `docs/evidence/goal05-phase20-eval-runtime.md`。EvalDataset/Case/Run、RAG Core Five、GraphRAG diagnostics、Agent Efficiency、Benchmark Comparison、Release Gate、EvidenceRecord、Alembic `20260729_53` / `20260729_54` / `20260729_55`、Postgres integration、API route 和 fault tests 已有 focused 证据；late revision、expired evidence、fixed profile replay 和 closure evidence 尚未完成，不代表 quality proven 或 production readiness。
- current_phase = PHASE20；PHASE21–22 不得提前冒充 Current。

## Goal05 Target Coverage Boundary

Goal05 一次性 Target Coverage Audit 已冻结：

```text
docs/evidence/goal05-target-coverage-audit.md
.agent/programs/work-products/goal05-target-gap-ledger.yaml
```

冻结结论：十一模块仍存在 Mandatory Gap，主要集中在 PHASE20–22 的 Eval / Fault / Closure 范围。当前可以声明 PHASE15 sandbox contract 与真实 WASM/OCI runtime 已进入 `ToolInvocationGateway` 默认链，并有 `tool_sandbox_receipts` migration、unit/repo tests 和真实运行证据；也可以声明 PHASE20 Eval Runtime foundation 已有代码、migration 和 Postgres integration。不能声明 PHASE20 completed、quality proven、22/22 completed 或 production ready。

不得声明完整 Zuno、quality proven、完整 CI 通过、not production ready 之外的生产可用状态，或 production ready。

## Goal02 Closure Boundary

Goal02 completed：PHASE08 completed；PHASE11 completed；PHASE09 ready；PHASE12 ready；not production ready。

## Goal03 Closure Boundary

Goal03 historical closure：PHASE09、PHASE12、PHASE13、PHASE14 的完成结论仍保留；PHASE15 completed 结论已被 Goal05 一次性 Target Coverage Audit 撤回并在真实 sandbox runtime 证据补齐后重新关闭；production readiness not established。

## Goal04 PR A / D Boundary

PHASE16 Tool Side Effect and Reconciliation 已由 PR B 合并到 main。PHASE17 Dynamic Plan DAG and Parallel Control 已由 PR C 合并到 main。PHASE18 PR D 已由 merge commit `cbc04cb0be16c3915537b82a4f3f743cb7add963` 合并到 main。PHASE10 PR A 已由 merge commit `0351eab1c135601a7e1ac4406e967a4c7af07bc4` 合并到 main。PHASE19 已完成本地 Coordinator Closure；Goal05 已重新关闭 PHASE15，PHASE20 正在实现 Eval Runtime、fault/recovery、query/report 和 release gate 证据。当前不得把 production readiness 写成 completed。

PHASE08 当前保留的部分证据：

- AgentRunGraph 使用官方 LangGraph PostgreSQL Checkpointer，生产入口无隐式 InMemorySaver 回退。
- Native interrupt / `Command(resume=...)` 可在 restart 后从同一 thread checkpoint 继续，且不重复 Plan。
- 固定 AgentRunGraph 节点对齐 `initialize → authorize → context_snapshot → create_plan → validate_plan → activate_plan → execute_step → final_gate → finalize → run_outcome`。
- 固定 StepExecutionGraph 节点对齐 `load_step → resolve_input → security_gate → proposal → deterministic_validation → execute_owner_port → observation → action_evaluation → step_acceptance → commit_step_result`。
- TaskContract、GoalVersion、PlanVersion、ExecutionContextSnapshot 和 Budget 领域事实使用 PostgreSQL Repository / Alembic migration。

PHASE11 当前保留的部分证据来自 2026-07-23 前后的 durable ingestion 实现、迁移和测试。该证据不足以关闭完整 Goal02 Mandatory Scope，尤其不能把 Review Resume、外部 cleanup confirmation、MinIO absence verification 和 crash-safe reconciliation 视为已完成。

PHASE11 当前保留的部分证据：

- 生产默认 upload/parser 路径进入 SourceObject → DocumentVersion → ParsePlan → ParseJob → ParseAttempt → ParseSnapshot → CanonicalDocumentIR → SourceSpan → Quality Gate / Human Review → IndexableDocumentSnapshot → Outbox Handoff。
- 默认路径使用正式 PostgreSQL Repository/UoW。
- 默认路径接入 PHASE04 既有 S3/MinIO Object Store，不建设第二套 Object 事实源。
- 生产配置支持真实 RabbitMQ dispatch、publisher confirm、consumer ACK、retry、retry exhausted、DLQ、replay、reconnect、cancel/deadline 和 worker crash。
- Lease、Heartbeat、Fencing、orphan Attempt reconciliation、stale worker late result rejection 和 idempotent commit 有故障证据。
- Native、PDF、Layout、OCR、VLM、Office、Archive 使用统一 Parser Adapter Contract；OCR/VLM 不能只以 `target_blocked` 占位关闭。
- CanonicalDocumentIR、SourceSpan、TransformLedger、PDF citation、OCR bbox、normalization provenance 和 schema round-trip 可验证。
- Quality Gate 和 Human Review 包含 PASS / BLOCK / REVIEW / FALLBACK、ReviewTask、ReviewDecision / Receipt、pending / approved / rejected / expired / cancelled、reviewer scope、Security Epoch、decision hash 和 duplicate decision。
- Input 只提交 immutable IndexableDocumentSnapshotV1，不直接写 Chunk、Entity、Relation、KnowledgeVersion 或 Index。
- Delete / Legal Hold / Restore 按 visibility revoke → cleanup request → physical delete → verification 顺序验证，restore 不自动恢复已撤销授权。
- Legacy upload/parser 默认入口完成 cutover、进入期限 Adapter 或删除。

PHASE11 当前证据不证明以下后续模块；该列表只约束 Goal02 / PHASE11 证据边界，不覆盖 Goal03 后续实现证据：

- PHASE12 KnowledgeVersion、Index Cutover 或 Standard RAG 已完成。
- PHASE09 / PHASE10 Product Backend、Web 或 Desktop 默认路径已完成。
- 完整 release gate、fixed benchmark、quality measurement 或 production readiness 已通过。

## Measurement Blocked

Agentic GraphRAG 当前不能写成 quality completed。

```text
implementation available
measurement blocked
quality not yet proven
```

blocked、prepared、runtime observed 和 measured 必须严格区分。缺 trace 字段时输出 `unavailable_due_to_missing_trace_fields`，不得编造 failure bucket。

## Completed

近期可作为 completed 的内容只限已经由代码、测试、trace/eval 或 verifier 支撑的本地实现基线和文档/guardrail 收口。

历史 program 完成事实保留在：

- `docs/history/programs/README.md`

历史完成不等于当前 quality gate 已通过。

## Future Optional

以下内容是可选未来扩展，不是短期 blocker：

- Redis 高级缓存、Kafka、Kubernetes、Service Mesh 和多区域部署。
- Managed PostgreSQL / Managed Queue / Managed Object Store。
- 外部 Milvus / Neo4j 集群和分布式 graph/vector index 的企业级部署。
- 复杂 SSO / DLP / Vault、Firecracker。
- 大规模在线评测平台和企业运维门户。
- 大量 parser/provider 并行接入、OCR/VLM enrichment 平台化。
- Single Controller 下多 Agent Role 协作；产品级自治 Multi-Agent runtime 仍是更长期 Future Optional。
