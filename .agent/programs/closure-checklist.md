# Mega Program Closure Checklist

state: active
active_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
current_phase: `PHASE12_end-to-end-product-runtime.md`
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## 收口目标

Program 完成时必须达到：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

这句话只在以下事实都由代码、focused tests、verifier、trace / eval 或可复现 evidence 证明后才能写入 closure summary。

## Phase Gate 清单

- [x] PHASE01 完成 truth source、program merge、owner map、workstream map 和 PR / commit plan。
- [x] PHASE02 完成 shared contract freeze，且明确冻结 FileInputFormat、SourceObject、BinarySourceObject、ObjectStoreRef、ObjectStoreResult、ParserCapabilityStatus、ParserDependencyProbe、ParserWorkerSpec、ParserWorkerResult、ParseJobStatus、ParseAttempt、IndexWorkerSpec、IndexWorkerResult、QueueMessage、QueueBackendResult、OutboxEvent、DeadLetterRecord、ReconcilerFinding、OCRVLMEnrichmentResult、KnowledgeSpaceConfig、FileIngestionStatus、ChangeImpactPreview、CapabilityPolicy / RiskProfile / AuditEvent、PlanStep、PlanState、StrategySelectorOutput、SelectedSkill、CapabilityPlan、RetrievalPlan、PlannerOutput、ReflectionVerdict、ReplanDecision、ReflexionLesson、ConversationRunMetrics、StageMetrics、IngestionMetrics、RetrievalMetrics、PlanningMetrics、SecurityMetrics、EvalComparisonReport、ScenarioSummary 和 TraceSummary。
- [x] PHASE03 完成 enterprise ingestion async infrastructure baseline，并覆盖 PDF / Office / image / scanned / binary target-blocked visibility、binary ObjectStore、file lifecycle、outbox、dead letter 和 reconciler。
- [x] PHASE04 完成 knowledge retrieval profile 与 GraphRAG profile baseline。
- [x] PHASE05 完成 Memory & Context Engine baseline。
- [x] PHASE06 完成 Capability / Skill / Tool / MCP layer baseline。
- [x] PHASE07 完成 Security / Governance envelope baseline。
- [x] PHASE08 完成 Model Gateway / Cost / Latency baseline。
- [x] PHASE09 完成 Planning Contract 与 Strategy Selector baseline。
- [x] PHASE10 完成 ReAct / Reflection / Dynamic Replan / Reflexion runtime baseline。
- [x] PHASE11 完成 Workspace Product API / Frontend Minimal Sync。
- [ ] PHASE12 完成 End-to-End Product Runtime scenario。
- [ ] PHASE13 完成 Eval / Trace / Cost / Benchmark baseline。
- [ ] PHASE14 完成 Docs / Architecture Expansion。
- [ ] PHASE15 完成 full verification、archive、no-active、commit 和 push。

## 12 条 Product Baseline 验收

- [ ] `/workspace/file -> source object -> object store/local store` 可跑。
- [ ] `/workspace/ingest -> parse job -> Document IR -> index job -> chunks` 可跑。
- [ ] `QueueBackend + local async worker` 可跑，RabbitMQ / Redis / Postgres / MinIO 有 adapter boundary 和 probe。
- [ ] `ParserWorker / IndexWorker` 本地可执行，blocked OCR / VLM 不 fake index。
- [x] Knowledge retrieval 支持标准检索 / 深度检索 profile。
- [x] Agentic Retrieval Planner / Strategy Selector 能按 profile、证据、预算选择标准 / 深度检索计划、replan boundary 和 capability plan；PHASE10 已证明 reflection 后 replan 会改变后续本地执行轨迹。
- [x] Capability Layer 有 Skill / Knowledge / Tool / MCP / Artifact capability registry contract。
- [x] Memory & Context Engine 有多重记忆和 ContextPack contract，并有最小 runtime / focused tests。
- [x] Planning & Control Runtime 已有 StrategySelector、PlanStep、PlannerOutput、ReflectionVerdict、ReplanDecision、ReflexionLesson candidate contract 和本地 AgentControlRuntime 闭环；PHASE11 已完成 Product API 最小接入，E2E 证明仍属 PHASE12。
- [x] Security gates 覆盖 input / retrieval / tool / output，至少有 prompt injection、ACL、tool approval、output citation safety tests。
- [ ] Eval / Trace / Cost 能记录 latency、tokens / cost estimate、retrieval rounds、citation coverage、unsupported claim、plan / replan / reflection events。
- [ ] 一个 E2E scenario 能跑：上传文档 -> ingest -> 标准/深度检索 -> Agent plan -> cited artifact -> trace/eval/feedback -> restart rehydrate。
- [ ] E2E scenario 覆盖 native text / markdown / csv / json / html / code 解析，PDF / Office target-blocked，image / scanned OCR/VLM blocked no fake index，binary source object sha256 / storage_uri traceability，local queue / worker lifecycle，dead_letter / reconciler fixture。

## Workstream 收口清单

- [ ] Coordinator 审查所有 shared contract 和共享文件，没有跨 workstream 未解决冲突。
- [ ] Workstream A 提交 Input / Async Infrastructure evidence。
- [ ] Workstream B 提交 Knowledge / Retrieval / GraphRAG evidence。
- [ ] Workstream C 提交 Memory / Context evidence。
- [x] Workstream D 提交 Capability / Skill / Tool / MCP evidence。
- [x] Workstream E 提交 Security / Governance evidence。
- [x] Workstream F 提交 Planning / Agent Runtime evidence。
- [ ] Workstream G 提交 Eval / Trace / Cost benchmark evidence；PHASE08 Model Gateway / Cost / Latency evidence 已完成，PHASE13 仍未关闭。
- [x] Workstream H 提交 Product API / Frontend Minimal Sync evidence。
- [ ] Workstream I 提交 Docs / Verifier / Closure evidence。

## 目标架构拼接验收

- [x] Product Surface 能把用户的 AgentChat goal、knowledge selection、标准检索 / 深度检索传入 runtime。
- [ ] Input / Async Infrastructure 的 source object、parse job、document version、index manifest 和 citation lineage 能被 Knowledge Retrieval 消费。
- [ ] Input / Async Infrastructure 的 file status timeline、dependency probe、blocked reason、worker event、index status 和 binary source object refs 能被 Product API、E2E 和 Eval 消费。
- [ ] Knowledge Retrieval 输出的 EvidenceBundle / CitationLineage 能被 Planning、Reflection、Output Gate 和 Eval 共同消费。
- [x] Memory & Context Engine 输出的 ContextPack 能被 Strategy Selector 消费，且 sensitive exclusion 已生效。
- [ ] Capability Layer 的 SkillCard / ToolCard / MCPCapability 能被 Planner 选择，并受 Tool Gate 约束。
- [x] Security / Governance 的 Input / Retrieval / Tool / Output gates 能影响 plan / replan / refuse / ask_user。
- [x] Model Gateway 的 token / latency / cost metrics 能进入 trace，并影响 budget guard。
- [x] Planning & Control Runtime 能从 Skill、Capability、Evidence、Security verdict 和 budget verdict 生成 plan / verdict，并在 Reflection 后动态 replan 改变本地轨迹；PHASE11 已把 plan / reflection / replan summary 接入 Product API，PHASE12 仍需 E2E 证明。
- [ ] Eval / Trace / Cost 层能从 E2E scenario 输出 regression summary。
- [ ] Docs / Archive 能准确说明 Current / Target / Production Scale，且不把外部生产服务写成 Current。

## Current / Target 边界

- [ ] SQLite、local object store、local queue、local worker、local state store 可作为 Current。
- [ ] PostgreSQL / RabbitMQ / Redis / MinIO / S3 / external OCR / VLM / external index 没有真实 provider 和 tests 前只能写成 Production Scale Target 或 target-blocked evidence。
- [ ] PDF / Office / OCR / VLM 没有真实 Docling / PyMuPDF、Unstructured / MarkItDown、MinerU / PaddleOCR / VLM worker 前只能写成 target-blocked boundary / Launchable Target / Production Scale Target，不能写成 Current。
- [ ] Current 格式能力只把 native deterministic `txt / md / csv / json / html / code` 写成稳定解析；多格式 matrix 覆盖不等于生产解析完成。
- [ ] Basic RAG 和 Static GraphRAG 只能作为 eval baseline，不写成最终产品模式。
- [ ] Skill 不写成 Tool，不写成 Knowledge，不写成产品级多 Agent runtime。
- [ ] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。

## 文档同步检查

- [ ] `.agent/programs/current.md` 与 mega program active 状态一致。
- [ ] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1 / 2 completed 与 Program 3 Mega active。
- [ ] `.agent/programs/queued-programs/` 中原 Program 4-6 标注 superseded / merged_into，不写成 completed。
- [ ] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [ ] `AGENTS.md` 和 README 当前 program 摘要一致。
- [ ] `docs/architecture/architecture.md`、`.agent/architecture/architecture.md` 和两个 architecture HTML 同步。
- [ ] `docs/architecture/production-readiness.md` 与 mega program Current / Target 边界一致。
- [ ] `docs/architecture/document-ingestion-foundation.md` 与 async ingestion / E2E baseline 边界一致。
- [ ] `docs/architecture/document-ingestion-foundation.md` 包含 Input Format Support Matrix、Binary Source Object Target、Async Ingestion Pipeline、Queue / Worker / Outbox / Reconciler、OCR / VLM / Scanned 边界和 File-level Lifecycle。
- [ ] verifier / repo tests 覆盖 active program 文件清单、superseded Program 4-6 和 latest completed archive。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 归档目标

Program 完成后整体归档到：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

归档必须包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- PHASE01-PHASE15 文件
