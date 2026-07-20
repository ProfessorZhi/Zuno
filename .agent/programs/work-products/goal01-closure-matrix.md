# Goal01 Closure Matrix

status: reopened

frozen_at: 2026-07-19

branch: `integration/goal01-control-plane-model-ingestion`

start_sha_after_fetch: `36130924f5602c894d3d89eaaf6cefc3c8624a89`

origin_main_sha_after_fetch: `ed787ee962f7f567163388188e56b4b765c27877`

璇存槑锛氭湰鏂囧喕缁?PHASE05銆丳HASE06銆丳HASE07銆丳HASE11 鐨勬湁闄?Closure Matrix銆傚悗缁彧澶勭悊鏈枃涓?`mandatory_open` 鎴?`completion_candidate` 琛岋紱闄ら潪娴嬭瘯璇佹槑鏋舵瀯缂洪櫡锛屼笉缁х画寮€鏀惧紡鎵╄寖鍥淬€?
## PHASE05 PEP/PDP Cutover Matrix

| 鍏ュ彛 | 褰撳墠褰掔被 | 鐘舵€?| 璇佹嵁 | 鍓╀綑澶勭悊 |
| --- | --- | --- | --- | --- |
| Execute / Side Effect | `canonical_security_guard` | `completion_candidate` | Tool Runtime approval fact sink銆乸re-effect hash/epoch/deadline validation銆乻ink outage fail-closed fault tests | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Approval / Resume | `canonical_security_guard` | `completion_candidate` | workspace approval resume `task.resume.*` product action guard 涓?403 deny test | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Artifact Read / Download | `canonical_security_guard` | `completion_candidate` | workspace `artifact.read` / `artifact.download` product action guard銆乻tartup Postgres guard wiring | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Citation / Source Access | `canonical_security_guard` | `completion_candidate` | workspace `citation.read` guard for artifact response and task snapshot | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Admin 绠＄悊闈細MCP HTTP/SSE + stdio | `canonical_security_guard` | `completion_candidate` | MCP admin override guard銆乻tartup guard wiring銆乨eny-before-DAO tests | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Admin 绠＄悊闈細Agent / Tool / Dialog / MCP Agent / LLM / Knowledge / Knowledge File | `canonical_security_guard` | `completion_candidate` | 鍏变韩 `security_admin_actions`銆乿erifier銆乪vidence 鍜?`test_phase05_admin_action_reauthorization.py` 宸茶鐩?Agent/Tool/Dialog/MCP Agent/LLM/Knowledge/Knowledge File admin override deny-before-DAO | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| Secret Lease | `canonical_security_guard` | `completion_candidate` | `SecurityRepository.record_secret_ref` / `issue_secret_lease` / `validate_secret_lease` 瑕嗙洊 wrong audience銆乪xpired lease銆乺evoked secret | Pre-Closure 鍓嶈仛鍚堥獙璇?|
| External Export | `future_runtime_not_current` | `not_current` | 褰撳墠 active runtime 鏃犳寮?external export 榛樿璺緞锛汸HASE06 external sink isolation 宸茶瘉鏄庡閮?sink 涓嶅啋鍏呬笟鍔℃垚鍔?| 褰掑睘鍚庣画 Product/Publication/Integration Phase锛屼笉鑳介樆濉?PHASE05 褰撳墠榛樿璺緞 closure |
| Legacy Approval Boolean 鍒?Decision/Ref | `temporary_versioned_adapter` | `completion_candidate` | Tool Runtime `approved: bool` 宸茬粦瀹?`temporary.adapter.tool_runtime.approved_bool` 涓庡垹闄?Phase `PHASE16`锛泈orkspace 榛樿 resume path 宸蹭紶鍏?`security-approval-decision:*` decision ref锛汸HASE05 verifier 闃绘鏂板 legacy boolean owner | Pre-Closure 鍓嶈仛鍚堥獙璇?|

## PHASE06 Adapter Cutover Matrix

| 杩愯鍩?| Producer | Envelope / Adapter | 榛樿鎺ョ嚎鐐?| 澶辫触绛栫暐 | 鐘舵€?| 鍓╀綑澶勭悊 |
| --- | --- | --- | --- | --- | --- | --- |
| Agent | Agent runtime / workspace runtime | typed runtime event / span adapter | workspace runtime security and retrieval spans | local append-only first | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Model | Model Gateway runtime | model attempt / runtime event envelope | Gateway-owned call path | provider failure becomes attempt failure, not audit success | `completion_candidate` | `PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event` 宸叉秷璐?Gateway trace_event 鍐欏叆 model span/runtime event/audit锛汸HASE06 verifier 闃叉柇绾匡紱PHASE07 closure 浠嶉渶鐙珛渚濊禆鎵瑰噯 |
| Knowledge | Agentic retrieval / ingestion | retrieval trace / citation metrics | workspace retrieval observability | raw event retained, query freshness exposed | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Capability | Capability / Skill runtime | capability plan/runtime event | workspace capability snapshot | local facts persist before external sink | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Tool | Tool Runtime | approval/security span adapter | Tool Runtime approval path | sink outage fail-closed before side effect | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Security | Security repository / audit | immutable audit ledger adapter | Security pre-effect/audit facts | audit not sampled; failure visible | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Infrastructure | DB / outbox / external sink | dead-letter and local fact envelope | observability persistence adapter | external sink failure does not roll back local facts | `completion_candidate` | 鑱氬悎楠岃瘉 |
| Product Query | Observability query service | read-only freshness/completeness response | `/api/v1/observability/traces/{trace_id}` + product query service | returns freshness/completeness and dead letters; non-admin API access returns 403 | `completion_candidate` | 鑱氬悎楠岃瘉 |

## PHASE07 Runtime Closure Matrix

| 鑼冨洿 | 褰撳墠褰掔被 | 鐘舵€?| 璇佹嵁 | 鍓╀綑澶勭悊 |
| --- | --- | --- | --- | --- |
| Provider SDK bypass | `canonical_gateway_boundary` | `completion_candidate` | `verify_model_gateway_bypass.py --strict` 鐩爣宸茶揪鍒?strict-zero锛屼絾鍙厑璁?Pre-Closure 鍓嶈繍琛屼竴娆?| PHASE05/06 closure 鍚庤繍琛屼竴娆?strict gate |
| Model / Role / Capability Registry | `canonical_gateway_runtime` | `completion_candidate` | Model Gateway runtime batch evidence | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Routing Policy / Immutable Snapshot | `canonical_gateway_runtime` | `completion_candidate` | Routing snapshot and policy tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Provider Adapter SPI | `canonical_gateway_runtime` | `completion_candidate` | adapter boundary and conformance tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| ModelAttempt lifecycle | `canonical_gateway_runtime` | `completion_candidate` | attempt lifecycle tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Structured Output Validation | `canonical_gateway_runtime` | `completion_candidate` | structured validation / repair evidence | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Streaming / Timeout / Cancel | `canonical_gateway_runtime` | `completion_candidate` | streaming, timeout, cancel tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Usage Reservation / Settlement | `canonical_gateway_runtime` | `completion_candidate` | reservation and settlement tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Retry / Fallback / Circuit | `canonical_gateway_runtime` | `completion_candidate` | retry/fallback/circuit tests | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Trace / Audit 鎺ュ叆 | `depends_on_phase06` | `completion_candidate` | PHASE06 Coordinator Closure 宸叉壒鍑嗭紱`PostgresObservabilityRuntimeAdapter.record_model_gateway_trace_event` 涓?PHASE06 persistence verifier 宸茶瘉鏄?Gateway trace/audit 鎺ュ叆 | PHASE07 Pre-Closure 鑱氬悎楠岃瘉 |
| Chat / Embedding / Rerank / Judge 榛樿璺緞 | `canonical_gateway_runtime` | `completion_candidate` | default entry tests and bypass guard | PHASE05/06 Closure 鍚庤繘鍏?PHASE07 closure review |

## PHASE11 Ingestion Closure Matrix

| 鑼冨洿 | 褰撳墠褰掔被 | 鐘舵€?| 璇佹嵁 | 鍓╀綑澶勭悊 |
| --- | --- | --- | --- | --- |
| SourceObject upload init / commit | `canonical_ingestion_runtime` | `target_not_current` | source-lineage schema/repository + input runtime batch evidence | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| DocumentVersion / ParseSnapshot 鍒嗙 | `canonical_ingestion_runtime` | `target_not_current` | source-lineage schema/repository + persistence runtime tests | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| ParsePlan / Job / Attempt | `canonical_ingestion_runtime` | `target_not_current` | parse gateway/runtime tests + source-lineage persistence evidence | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| RabbitMQ dispatch / ACK / Retry / Dead Letter | `canonical_ingestion_runtime` | `target_not_current` | LocalQueue ACK/retry/dead-letter/replay verified锛汻abbitMQ target-blocked dependency probe does not fake production dependency | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Lease / Heartbeat / Fencing / Worker Crash Recovery | `canonical_ingestion_runtime` | `target_not_current` | ParseAttemptControl lease/fencing/late-result rejection and async worker/reconciler tests | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Native / PDF / Layout / OCR / VLM / Office / Archive Adapter | `mixed_current_future` | `target_not_current` | Native/PDF current adapters verified锛汷CR/VLM external target blocked with stable diagnostics and no fake index; Office/archive preservation boundary covered by input runtime batch | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| CanonicalDocumentIR | `canonical_ingestion_runtime` | `target_not_current` | ingestion contract tests | 鑱氬悎楠岃瘉 |
| SourceSpan / TransformLedger | `canonical_ingestion_runtime` | `target_not_current` | SourceSpan provenance and TransformRecord loss/lineage evidence in input runtime batch | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Quality Gate / Human Review | `canonical_ingestion_runtime` | `target_not_current` | QualityReport PASS/DEGRADED/BLOCK and IndexableDocumentSnapshot quality FK gate verified; human review remains explicit degraded/block boundary | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| IndexableDocumentSnapshot Outbox Handoff | `canonical_ingestion_runtime` | `target_not_current` | Indexable snapshot persistence + outbox handoff tests | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Visibility Revoke | `canonical_ingestion_runtime` | `target_not_current` | deletion receipts and visibility revocation sequence covered by input runtime batch | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Legal Hold | `canonical_ingestion_runtime` | `target_not_current` | Legal Hold blocks purge only and does not restore revoked access | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Physical Delete / Restore / Verification | `canonical_ingestion_runtime` | `target_not_current` | Input/Knowledge/Object/Verification delete receipts and persistence restore tests | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
| Legacy upload/parser 榛樿璺緞 Cutover | `temporary_versioned_adapter` | `target_not_current` | legacy chunks normalize to CanonicalDocumentIR with ACL/source-span provenance; default worker uses ParseGateway and durable store handoff | PHASE11 Pre-Closure 鑱氬悎楠岃瘉 |
## 2026-07-20 PHASE11 Reopen Audit

PHASE11 section 的旧 `completion_candidate` 全部降为 `target_not_current`。已有证据保留为线索，但 LocalQueue、SQLite runtime batch、target-blocked OCR/VLM 和不完整 Human Review 不能关闭 PHASE11。PHASE08 仍 ready；PHASE12 planned，等待 PHASE08 completed 与 PHASE11 completed。