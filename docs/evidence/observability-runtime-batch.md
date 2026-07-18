# Observability Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-OBS-001` 到 `ARCH-OBS-024`
- `ARCH-OBS-RAG-001` 到 `ARCH-OBS-RAG-020`

范围说明：

- 已证明 Trace Context 保留租户、工作区、correlation、causation 和 effective security epoch。
- 已证明 Trace Tree 具备 parent/link/causation reducer。
- 已证明 Telemetry Envelope 使用版本和 payload schema hash。
- 已证明 Inbox Dedup 按 payload hash 拒绝重复事件。
- 已证明 Ordering Watermark 检测 sequence gap。
- 已证明 Trace Lifecycle 状态转换受守卫约束。
- 已证明 Agent Core、Model、Retrieval 和 Tool Trace 需要 typed required fields。
- 已证明 Security Redaction 在进入 trace payload 前脱敏。
- 已证明 Audit Record 以 sequence、previous hash 和 payload hash 追加且不可变。
- 已证明 Sampling 支持 high-risk always keep 和 debug never sample。
- 已证明 External Sink Delivery 有 idempotency，且不代表 source-domain success。
- 已证明 Retention/Legal Hold 优先级阻止删除。
- 已证明 Eval Dataset/Case 使用不可变版本和 case hash。
- 已证明 Eval Run/Case Recovery 保留 attempt、lease 和 checkpoint。
- 已证明 Judge Policy 固定 version、timeout 和 output schema hash。
- 已证明 Failure Bucket 需要完整 trace fields。
- 已证明 Benchmark Comparison 需要 pinned input hash。
- 已证明 Profile Completeness 需要完整 case set。
- 已证明 Release Gate 在 completeness、comparability 和 threshold 全部满足后才 accepted。
- 已证明 Measurement Status 区分 measured、blocked 和 unavailable，不把 null 当 0。
- 已证明 Evidence Registry 记录 artifact hash、validation 和 supersession。
- 已证明 Projection Rebuild 来自 append-log replay 和 watermark，不替代 source fact。
- 已证明 Quality Proven 需要 measured、comparable、release gate 和 evidence。
- 已证明 RAG Core Five metric registry 覆盖 Context Precision、Context Recall、Faithfulness、Answer Relevancy 和 Answer Correctness。
- 已证明 RAG metric 保留 version、alias、calibration 和 metric hash。
- 已证明 Route Trace 记录 requested/resolved route。
- 已证明 Graph Traversal Trace 保留 entity、relation、path 和 community。
- 已证明 Source Grounding 绑定 graph ref 和 source span refs。
- 已证明 Fusion/Rerank Trace 保留 rank lineage 和 dropped reason。
- 已证明 Agentic Loop Trace 保留 trigger、outcome 和 replan ref。
- 已证明 RAG Failure Bucket required-field classifier 生效。
- 已证明 Evaluation Slice 完整性守卫生效。
- 已证明 Agent Efficiency Snapshot 记录 wall/active/queue/critical path/parallel branch/token/cost。
- 已证明 Quality-constrained Efficiency 受 quality-first gate 控制。
- 已证明 Cost/Latency Attribution 绑定 Usage Receipt 并完成 reconciliation。
- 已证明 Core Five Release Gate 需要五项 RAG 指标全部 measured。
- 已证明 Reproducible Evidence Bundle 保留 artifact hashes 和 result hash。

未覆盖：

- Observability / Eval 模块本批 44 条已覆盖；其他模块仍需后续批次证明。

验证命令：

```powershell
python tools/scripts/verify_observability_runtime_batch.py
pytest -q tests/platform/test_observability_runtime_batch.py tests/agent/test_platform_layer_surfaces.py -p no:cacheprovider
```

结果：

```text
Observability runtime batch verification passed for ARCH-OBS-001, ARCH-OBS-002, ARCH-OBS-003, ARCH-OBS-004, ARCH-OBS-005, ARCH-OBS-006, ARCH-OBS-007, ARCH-OBS-008, ARCH-OBS-009, ARCH-OBS-010, ARCH-OBS-011, ARCH-OBS-012, ARCH-OBS-013, ARCH-OBS-014, ARCH-OBS-015, ARCH-OBS-016, ARCH-OBS-017, ARCH-OBS-018, ARCH-OBS-019, ARCH-OBS-020, ARCH-OBS-021, ARCH-OBS-022, ARCH-OBS-023, ARCH-OBS-024, ARCH-OBS-RAG-001, ARCH-OBS-RAG-002, ARCH-OBS-RAG-003, ARCH-OBS-RAG-004, ARCH-OBS-RAG-005, ARCH-OBS-RAG-006, ARCH-OBS-RAG-007, ARCH-OBS-RAG-008, ARCH-OBS-RAG-009, ARCH-OBS-RAG-010, ARCH-OBS-RAG-011, ARCH-OBS-RAG-012, ARCH-OBS-RAG-013, ARCH-OBS-RAG-014, ARCH-OBS-RAG-015, ARCH-OBS-RAG-016, ARCH-OBS-RAG-017, ARCH-OBS-RAG-018, ARCH-OBS-RAG-019, ARCH-OBS-RAG-020.
14 passed in 74.27s
```
