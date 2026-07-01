# PHASE09 OCR / VLM Worker Boundary

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE09_ocr-vlm-worker-boundary
mode: tdd-implementation

## 目标

定义 OCR / VLM worker boundary，使扫描件、图片、图表、公式等输入可以进入 queued / blocked / succeeded / failed 语义。默认无 provider 时必须返回 target-blocked diagnostics，不能 fake success，也不能覆盖 deterministic parser source truth。

## 范围

- OCR / VLM request contract：source object、page image ref、budget、privacy gate、network policy。
- OCR / VLM result contract：ocr_text_block、caption、chart_summary、confidence、derived_from、review_required。
- Worker boundary：queued、running、blocked、succeeded、failed。
- blocked diagnostics 持久化并可被 ingest status 查询。
- OCR / VLM output 作为 derived enrichment，不覆盖原始 block lineage。

## 禁止范围

- 不要求真实 OCR / VLM provider。
- 不让 VLM 输出成为默认 source truth。
- 不绕过 privacy / network / budget gate。
- 不把扫描件解析能力写成完整 Current，除非真实 provider 和 tests 证明。

## 验收闸门

- focused test：无 provider 时 OCR / VLM request 进入 blocked diagnostics。
- focused test：blocked OCR / VLM 不创建 fake index。
- focused test：derived enrichment result 保留 `derived_from` 和 `review_required`。
- diagnostics 可从 durable store 和 status query 读回。

## 验证命令

```powershell
pytest -q tests/knowledge/test_ingestion_async_infrastructure.py -p no:cacheprovider
pytest -q tests/knowledge/test_parse_gateway_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/ingestion/router.py`
- `src/backend/zuno/knowledge/ingestion/adapters.py`
- `src/backend/zuno/knowledge/ingestion/gateway.py`
- `docs/architecture/document-ingestion-foundation.md`

## 需要修改的文件

- `src/backend/zuno/knowledge/workers/`
- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/ingestion/gateway.py`
- focused tests

## 执行拆解

1. 写 failing test：OCR / VLM worker no-provider blocked。
2. 实现 boundary contracts。
3. 写 failing test：derived enrichment metadata。
4. 实现 metadata propagation。
5. 跑 parse gateway 和 async infra tests。

## 多 agent 分工

- OCR Boundary Agent：审 provider-free blocked semantics。
- Security Agent：审 privacy / network / budget gates。
- Verification Agent：跑 parse / durable ingest tests。

## 需要返回的证据

- blocked diagnostics 示例。
- derived enrichment payload 示例。
- no-fake-index evidence。

## 停止条件

- 需要真实 OCR / VLM token 或服务才能通过 tests。
- VLM 输出会覆盖 deterministic source block。
- Privacy / network / budget gate 无法表达。
