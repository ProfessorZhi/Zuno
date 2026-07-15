# PHASE02 Rollback and Recovery Playbook

phase_id: PHASE02
task_id: P02-T05
start_commit: 000928c7fc46224264e43677a5877d76731cd04c
status_boundary: "Rollback 不能恢复到绕过 Security、Audit、Approval、Budget 或 Final Gate 的旧路径；窗口结束必须删除。"

| surface | trigger | max_window | data_reconcile | security_impact | operator_command | evidence | removal_task |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Product API adapter | command acceptance mismatch, missing RunOutcome, projection parity failure | PHASE09-PHASE10 | compare ProductCommand/WorkspaceTask hashes and projection source watermark | must preserve server auth and AvailableAction checks | `set product_api_v1_adapter=ROLLBACK_WINDOW` | contract parity report + projection rebuild log | P22-T03 |
| Completion legacy rollback | unified runtime unavailable before PHASE08 closure | until PHASE08 default path proven | no domain migration; trace missing must be disclosed | cannot skip budget/trace disclosure; legacy path is temporary | `ZUNO_AGENT_RUNTIME=legacy_general_agent` | runtime chain test + legacy invocation counter | P22-T03 |
| Workspace SSE stream | cursor gap, resume failure, reconnect auth failure | PHASE10 rollout window | mark projection GAP and resync snapshot from source facts | reconnect must reauthorize; revoked cursor fails closed | `disable workspace_projection_stream_v1; enable projection query polling` | SSE gap/resume test report | P22-T03 |
| PostgreSQL UoW shadow | migration partial, lock/isolation failure, failed downgrade rehearsal | before WRITE_CUTOVER only | resume/rollback/forward-fix migration run; compare source/target hashes | security epoch writes must not be downgraded | `stop admission; rollback alembic revision or forward-fix per migration runbook` | Alembic upgrade/downgrade + fault evidence | P22-T03 |
| RabbitMQ Outbox/Inbox | backlog, duplicate side effect risk, ACK crash failure | PHASE04 rollout window | use Outbox publisher replay and Inbox dedup; never redo committed domain mutation | audit backpressure fail mode preserved | `pause consumers; drain queue; replay outbox from sequence` | duplicate/redelivery fault report | P22-T03 |
| Object Store | hash mismatch, orphan object, missing committed object | PHASE04/PHASE11 rollout window | quarantine mismatches; orphan cleanup from ObjectCommitReconciler | revoked object reads fail closed | `disable new object store writes; run object reconcile` | object hash and orphan receipt | P22-T03 |
| Model Gateway | provider timeout/error mapping mismatch, usage receipt missing | PHASE07 rollout window | usage correction is append-only; do not edit prior receipt | model security decision must be enforced before dispatch | `route provider to fallback profile` | ModelGateway trace + budget/fallback test | P22-T03 |
| Tool Runtime read-only | prepared action hash mismatch, adapter conformance fail | before side-effect cutover | read-only observations can be replayed; side effects not retried blindly | approval and audit not bypassed | `disable tool_runtime_readonly_gateway` | adapter conformance report | P22-T03 |
| Tool side effect | UNKNOWN, response lost, duplicate effect risk | no blind rollback after dispatch | EffectReconciliation decides CONFIRMED/NOT_EXECUTED/COMPENSATED | Security approval cannot be reused if hash/epoch changed | `force reconciliation; block ordinary retry` | UNKNOWN reconciliation evidence | P22-T03 |
| Frontend rollout | browser E2E fail, multi approval UI mismatch, artifact auth fail | PHASE10 rollout window | no domain changes; resync projection and clear stale action tokens | revoked tokens/cursors/download sessions invalidated | `serve previous frontend bundle; keep Product API adapter` | browser/desktop E2E report | P22-T03 |

## Non-negotiable Recovery Rules

- HTTP 2xx, SSE close, Queue ACK, Object Commit and Audit Delivery are boundary receipts, not domain success.
- Schema rollback after WRITE_CUTOVER requires Coordinator decision; use forward-fix when downgrade would lose facts.
- Tool UNKNOWN never rolls back by ordinary retry; it enters EffectReconciliation.
- Frontend rollback cannot make the client the source of Run, Approval, Effect, Evidence, Memory or Eval facts.
