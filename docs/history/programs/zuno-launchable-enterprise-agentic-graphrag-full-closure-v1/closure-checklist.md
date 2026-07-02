# Mega Program Closure Checklist

state: completed
program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
active_program: none
current_phase: none
latest_completed_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

## 收口目标

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

## Phase Gate 清单

- [x] PHASE01 完成 truth source、program merge、owner map、workstream map 和 PR / commit plan。
- [x] PHASE02 完成 shared contract freeze。
- [x] PHASE03 完成 enterprise ingestion async infrastructure baseline。
- [x] PHASE04 完成 knowledge retrieval profile 与 GraphRAG profile baseline。
- [x] PHASE05 完成 Memory & Context Engine baseline。
- [x] PHASE06 完成 Capability / Skill / Tool / MCP layer baseline。
- [x] PHASE07 完成 Security / Governance envelope baseline。
- [x] PHASE08 完成 Model Gateway / Cost / Latency baseline。
- [x] PHASE09 完成 Planning Contract 与 Strategy Selector baseline。
- [x] PHASE10 完成 ReAct / Reflection / Dynamic Replan / Reflexion runtime baseline。
- [x] PHASE11 完成 Workspace Product API / Frontend Minimal Sync。
- [x] PHASE12 完成 End-to-End Product Runtime scenario。
- [x] PHASE13 完成 Eval / Trace / Cost / Benchmark baseline。
- [x] PHASE14 完成 Docs / Architecture Expansion。
- [x] PHASE15 完成 full verification、archive、no-active 和 local commit。

## 关键验收

- [x] `/workspace/file -> source object -> object store/local store` 可跑。
- [x] `/workspace/ingest -> parse job -> Document IR -> index job -> chunks` 可跑。
- [x] `QueueBackend + local async worker` 可跑，RabbitMQ / Redis / Postgres / MinIO 有 adapter boundary 和 probe。
- [x] `ParserWorker / IndexWorker` 本地可执行，blocked OCR / VLM 不 fake index。
- [x] Knowledge retrieval 支持标准检索 / 深度检索 profile。
- [x] Agentic Retrieval Planner / Strategy Selector 能按 profile、证据、预算选择检索计划、replan boundary 和 capability plan。
- [x] Capability Layer 有 Skill / Knowledge / Tool / MCP / Artifact capability registry contract。
- [x] Memory & Context Engine 有多重记忆和 ContextPack contract，并有 runtime / focused tests。
- [x] Planning & Control Runtime 有 StrategySelector、PlanStep、PlannerOutput、ReflectionVerdict、ReplanDecision、ReflexionLesson candidate contract 和本地 AgentControlRuntime 闭环。
- [x] Security gates 覆盖 input / retrieval / tool / output。
- [x] Eval / Trace / Cost 能记录 latency、tokens / cost estimate、retrieval rounds、citation coverage、unsupported claim、plan / replan / reflection events，并生成统一 regression summary。
- [x] E2E scenario 能跑：上传文档 -> ingest -> 标准/深度检索 -> Agent plan -> cited artifact -> trace/eval/feedback -> restart rehydrate。
- [x] Docs / Archive 准确说明 Current / Target / Production Scale，且不把外部生产服务写成 Current。

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
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
pytest -q tests/evals -p no:cacheprovider
```

## Remaining Production Scale Target

- PostgreSQL / RabbitMQ / Redis / MinIO / S3。
- External OCR / VLM / external parser workers。
- External vector / graph index。
- External LangSmith / OTel sink、Prometheus dashboard、online eval、persistent trace store、CI release gate operations。
- Production multi-tenant deployment、SSO / RBAC / DLP operations、cross-process worker lease 和 distributed exactly-once tool execution。
