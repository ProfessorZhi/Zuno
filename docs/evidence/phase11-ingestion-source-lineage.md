# PHASE11 Ingestion Source Lineage Evidence

status: `reopened_partial_evidence`
phase_completion: `reopened_pending`

鏈枃璁板綍 PHASE11 Durable Ingestion and Source Lineage 鐨勫疄鐜拌瘉鎹細鐢熶骇 PostgreSQL schema 杈圭晫宸蹭负 SourceObject銆丏ocumentVersion銆丳arsePlan銆丳arseJob銆丳arseAttempt銆丳arseSnapshot銆丼ourceSpan銆丵uality Gate銆両ndexableDocumentSnapshot銆丱utbox 鍜?Dead Letter 寤虹珛姝ｅ紡鎸佷箙鍖栬〃锛沗input-runtime-batch` 宸茶鐩?`ARCH-ING-001` 鍒?`ARCH-ING-080` 鐨?runtime batch 琛屼负銆?
## Current Boundary

```text
infra/db/alembic/versions/20260719_18_ingestion_source_lineage.py
src/backend/zuno/platform/database/schema_registry.py
src/backend/zuno/platform/database/ingestion/persistence.py
tools/scripts/verify_phase11_ingestion_source_lineage.py
tests/repo/test_phase11_ingestion_source_lineage.py
tests/integration/test_phase11_ingestion_persistence_runtime.py
docs/evidence/input-runtime-batch.md
```

## Verified Behavior

- Migration 閾炬帴鍒?`20260719_17`锛岄伩鍏嶄骇鐢熺浜?Alembic head銆?- `ingestion_*` 琛ㄧ粺涓€褰掑睘 `Input / Document Ingestion`銆?- SourceObject 淇濈暀 object manifest銆乭ash銆乧lassification 鍜?security epoch銆?- DocumentVersion 涓?ParseSnapshot 鍒嗙锛孭arseSnapshot 缁戝畾 ParseJob銆丳arseAttempt 鍜?DocumentVersion銆?- ParseAttempt 鎸佷箙鍖?lease銆乫encing token銆乤ttempt number 鍜岀姸鎬併€?- SourceSpan 鍙洖婧?ParseSnapshot 涓?DocumentVersion銆?- Quality Gate 鏄?IndexableDocumentSnapshot 鍙戝竷鍓嶇疆鏉′欢銆?- Input migration 涓嶅垱寤?Chunk銆丒ntity銆丷elation銆並nowledgeVersion銆丅M25 鎴?Vector Index銆?- `IngestionUnitOfWork` 鍙湪涓€绗?PostgreSQL transaction 涓啓鍏?SourceObject 鍒?IndexableDocumentSnapshot 鍜?outbox event銆?- IndexableDocumentSnapshot 蹇呴』寮曠敤 QualityGateDecision锛涚己璐ㄩ噺闂ㄦ椂鏁版嵁搴?FK 鎷掔粷 handoff銆?- SourceObject 鍐欏叆鍓嶉獙璇?`source_sha256` 鏄?64 浣?hash銆?- LocalQueue ACK / retry / dead-letter / replay銆丷abbitMQ target-blocked probe銆丷edis fallback boundary 鍧囧凡楠岃瘉锛屽閮ㄤ緷璧栦笉鍙敤涓嶄細鍐掑厖 production dependency銆?- ParseAttemptControl 瑕嗙洊 lease銆乫encing token 鍜?late result rejection銆?- Native/PDF current adapter銆丱CR/VLM target-blocked diagnostics銆丱ffice/archive preservation boundary銆乨elete receipts銆乴egal hold 鍜?restore verification 鍧囩敱 `input-runtime-batch` 璁板綍銆?
## Validation

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider
python tools/scripts/verify_input_runtime_batch.py
pytest -q tests/knowledge/test_input_runtime_batch.py tests/knowledge/test_ingestion_async_infrastructure.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/repo/test_phase11_ingestion_source_lineage.py -p no:cacheprovider
```

## Boundary

PHASE11 completed 鍙〃绀哄畬鏁?Phase Scope 鍐?implementation available锛涗笉琛ㄧず production ready銆乹uality proven銆丳HASE12 Knowledge completed 鎴栧閮?RabbitMQ/OCR/VLM 鐢熶骇渚濊禆宸插湪鏈湴鐜鍙敤銆傚閮ㄤ緷璧栦笉鍙敤鏃跺繀椤讳繚鐣?target-blocked diagnostics锛屼笉鑳界敤 mock 鍐掑厖鐢熶骇鑳藉姏銆?
## 2026-07-20 Goal01 Reopen Audit

本文证据保留为 PHASE11 的部分实现线索，但不再证明完整 Phase completed。缺口包括真实 RabbitMQ 生产默认 dispatch/ACK/retry/DLQ/replay、可执行 OCR/VLM adapter boundary、Human Review task/decision/receipt 状态机、完整 delete/legal hold/restore fault coverage、以及 legacy upload/parser 默认路径 cutover inventory。
