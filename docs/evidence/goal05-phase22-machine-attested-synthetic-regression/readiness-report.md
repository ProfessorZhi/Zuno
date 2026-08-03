# PHASE22 Machine-attested Synthetic Regression Readiness

status: BLOCKED_WITH_EXACT_GAPS
track: machine_attested_synthetic_regression
date: 2026-08-03

## 当前结论

本报告建立 Synthetic Regression Track 的当前事实边界和人工分工入口，不声明 track ready。

当前可证明事实：

- `origin/main`：`c9d099d64a1af28102231751ce55df8217173e89`
- PR #106：Open，head `95e17fc522591e7ee543b40b5b568d71963b6aa0`，GitHub checks passed
- Stacked branch：`codex/phase22-real-synthetic-benchmark-readiness`
- PHASE22：`in_progress`
- Program：`active`
- Production Readiness：not established
- Public Benchmark：`reviewer_approved_count=0`，`benchmark_eligible_count=0`

Synthetic Track 当前仍为 `BLOCKED_WITH_EXACT_GAPS`，原因是完整 Corpus 真实 Canonical Ingestion、三索引 Visibility Receipt、Snapshot Activation、同 Snapshot 四 Profile Runtime、Profile Trace Gold 隔离、真实 runtime metrics、Fault/Security/Resume/Idempotency 矩阵均未执行完成。

## CC-A 当前进度

已建立当前 schema 的 seed dataset scaffold，用于证明字段、hash、source span、gold 隔离和 validator 机制可执行。

- seed case count：7
- seed case distribution：每个目标 bucket 各 1 个
- seed dataset hash：`00064456daf21942b2739a9151d6bb86c84ffda7e946cece4b4b548c9f7c9e6a`
- seed corpus hash：`749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4`
- world model hash：`f3078e20b11feb468285fcca07fa09a920a5be4f280841957dc447938dc76242`
- runtime eligible：false
- synthetic regression eligible：false

seed dataset 只是 7-case scaffold，不是完整 Track 证据；完整 Track 仍需要真实 canonical ingestion 和 runtime profile。

## CC-A Candidate 80 当前进度

已生成当前 schema 的 80-case candidate dataset，分布满足目标 bucket，并通过当前机器校验范围：

- case count：80
- distribution：20 single_doc_fact / 20 multi_hop / 15 graph_reasoning / 10 temporal_version / 5 abstain_no_answer / 5 security_scope / 5 fault_recovery
- dataset hash：`b7832e537dbaab14a7d664f334676120f10b86aa8b7efddfc7220bc7bc915f0c`
- corpus hash：`749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4`
- world model hash：`f3078e20b11feb468285fcca07fa09a920a5be4f280841957dc447938dc76242`
- validation scope：schema、source_document_refs、source_span_refs、input_hash、case_hash、duplicate_question、duplicate_case_id、runtime_forbidden_gold_fields、gold_leakage、hard_negative_no_answer_scan、seed_hash_stability
- derivation validator v1：80/80 derivation valid；80/80 answer derivation valid from World Model；80/80 source evidence valid；0 unsupported answer；0 duplicate question；0 gold leakage；5/5 hard negative valid；80/80 hash valid；report hash `7c0a118e77b6d2c49a9b4086b853d3eaf4ddf5a56236bda64cd8644e07e5d834`
- runtime eligible：false
- synthetic regression eligible：false

当前 80-case candidate 已具备当前 schema、World Model answer derivation、source span、hash、duplicate、gold-field 隔离、hard negative scan 和 derivation validator v1 证据。它仍没有经过完整 Canonical Ingestion、三索引、Snapshot Activation 或四 Profile Runtime，因此不能声明 `SYNTHETIC_REGRESSION_TRACK_READY`。

## WP5 Release Gate 当前进度

已冻结 machine-attested synthetic regression 专属非零阈值集合，并生成当前 `BLOCKED` release decision evidence。该 decision 只表示缺 runtime metrics / 四 Profile / Snapshot activation，不能写成 `PASSED`。

- threshold hash：`e301259d8b9fdfe854b750e0c1d18c068241df7f8799cfcfdceb06fc54a08b76`
- blocked decision hash：`5e800cb28da3bb1cd6c216b1001754366117645c37a0808d44702ed2c7b90223`
- required metrics：answer_exact_match、answer_semantic_score、recall_at_5、context_precision_at_5、hit_at_5、citation_accuracy、citation_completeness、abstention_accuracy、security_violation_rate、unsupported_claim_rate、profile_failure_rate、resume_success_rate、p50_latency、p95_latency、cost_per_case、budget_overrun_rate
- runtime metrics ref：null
- public benchmark claim：false
- production release claim：false

## Gold / Runtime 隔离当前进度

已生成 80 case x 4 profile 的 runtime request manifest，用于证明运行入口不会携带 `expected_answer`、gold span、derivation spec 或 World Model。该 evidence 只证明 request 输入隔离，不证明四 Profile 已真实运行。

- runtime request count：320
- runtime request hash：`1f8f3bf936d4e48412f1738e6f653ec702e6a0a21c4dd37253490a96db6c788d`
- forbidden field count：0
- runtime may read case file：false
- runtime may read gold：false
- runtime may read world model：false
- knowledge version id：null
- snapshot id：null

## WP2 Source Upload 当前进度

已将完整 candidate corpus 转成 Source Upload manifest，包含每个 corpus document 的 `source_id`、`document_id`、tenant/workspace、security scope、source hash、content type、corpus-relative path 和幂等 key。该 evidence 只证明上传输入已准备，不证明 MinIO、PostgreSQL 或 Canonical Ingestion 已执行。

- source count：8
- source manifest hash：`0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a`
- duplicate source count：0
- initial state：accepted
- runtime ingested：false
- object store verified：false
- postgres facts verified：false

## WP2 Canonical IR 当前进度

已从完整 candidate corpus 生成 Canonical Document IR manifest candidate，包含 document version、chunks、entities 和 directed relations。该 evidence 只证明 IR 输入候选可机器复现，不证明正式 Parser / Canonicalization Runtime、PostgreSQL facts 或 KnowledgeVersion 已执行。

- document count：8
- chunk count：24
- entity count：15
- directed relation count：5
- canonical IR hash：`43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6`
- parser runtime executed：false
- postgres facts verified：false
- knowledge version created：false

## WP3 Index Job 当前进度

已从 Canonical IR manifest 生成三索引 Index Job manifest candidate，覆盖 Elasticsearch BM25、Milvus Vector 和 Neo4j Graph。该 evidence 只证明 index jobs 输入和 fail-closed activation gate 可机器复现，不证明任何 adapter 已写入、回读或生成 Visibility Receipt。

- index job count：3
- Elasticsearch job count：1
- Milvus job count：1
- Neo4j job count：1
- index job manifest hash：`bdc2401a5c58a94fa330c4d4048d08e3320107516a9d3d981599d4207e80d5d3`
- indexes visible：false
- visibility receipt refs：[]
- snapshot activation allowed：false
- snapshot activation block reason：index_visibility_receipts_missing

## Snapshot Activation Gate 当前进度

已生成 Snapshot Activation manifest，用机器证据固定当前 fail-closed 边界：缺任一三索引 Visibility Receipt 时不得激活 Snapshot。本证据不证明真实 Snapshot 已创建，只证明当前候选链路不能越过 activation gate。

- required receipt count：3
- provided receipt count：0
- missing receipt count：3
- missing receipt kinds：Elasticsearch BM25 / Milvus Vector / Neo4j Graph
- activation allowed：false
- snapshot id：null
- activation receipt ref：null
- snapshot activation manifest hash：`8fcc6e3c2d5756f700ccab0168716926760f336e7497531ab634e5c324493c6b`

## Neo4j Path Visibility Receipt 当前进度

已在 Knowledge Indexing owner 边界定义最小 Neo4j Path Visibility Receipt Contract，并接到 `Neo4jGraphIndexClient` 的 owner runtime 方法。Focused unit test 使用 fake driver 证明 adapter 会写入 Entity / Directed Relation，随后通过两跳 path read-back 生成 receipt；read-back 缺失时返回 `None`，不得生成有效 Visibility Receipt。该 evidence 不证明真实 Neo4j 服务已执行。

- contract status：`OWNER_RUNTIME_IMPLEMENTED_LIVE_SERVICE_NOT_EXECUTED`
- owner：Knowledge / Neo4j Graph Index Adapter 或正式 Graph Read-back Runtime
- required fields：receipt_id、tenant_id、workspace_id、knowledge_version_id、snapshot_id、query_kind、start_entity_ref、end_entity_ref、relation_kinds、path_length、matched_node_refs、matched_relation_refs、adapter_execution_ref、visibility_status、observed_at、config_hash
- runtime receipt count：0
- fake-driver two-hop owner read-back：PASSED
- live Neo4j two-hop read-back：NOT_RUN

## 历史 PR 分类

本轮历史审查范围：PR #100、PR #104、PR #105。

| PR | 分类 | 结论 |
| --- | --- | --- |
| #100 | ACCEPT_AFTER_REWORK / DROP mixed | Corpus 和 80 case 资产可选择性参考；`ingest_and_run.py`、profile result、release decision、runtime ingestion 产物必须 DROP，因为使用 in-memory substring / expected answer 注入 / TCP probe 冒充 runtime。 |
| #104 | ACCEPT_AFTER_REWORK / SUPERSEDED_BY_MAIN mixed | Truth boundary、execution candidate gate、task prompt 思路可参考；已关闭未合并，不是 Current。PR #106 已正式吸收 synthetic invalidation guard 的核心边界。 |
| #105 | ACCEPT_AFTER_REWORK | `CanonicalIngestionSliceRuntime`、状态机测试、Package A upload helper 可逐文件审查后迁移；不得整体合并，且必须适配最新 main owner boundary。Alembic env import fix需重新验证是否仍必要。 |

## 当前 Blocker

- Dataset：当前分支已有 80/80 schema、World Model answer derivation、source evidence、duplicate/gold leakage/hard-negative/hash 机器校验证据；仍缺人工 reviewer approval，且不得把该机器证据冒充 Public Benchmark。
- Ingestion：已有完整 Corpus 的 Source Upload input manifest 和 Canonical IR manifest candidate；仍没有 Source Upload 到 Snapshot Activation 的真实 runtime ID 链。
- Index：已有三索引 Index Job manifest candidate 和缺 receipt 时禁止 Snapshot Activation 的 blocked manifest；仍没有 ES/Milvus/Neo4j 真实写入、回读或 visibility receipt。
- Embedding：没有 formal Embedding Gateway provider/model/dimension/config hash。
- Graph：最小 Neo4j Path Visibility Receipt Contract 已定义并接入 `Neo4jGraphIndexClient` owner 方法；仍缺真实 Neo4j 服务两跳 read-back 和 receipt evidence。
- Profiles：四 Profile 仍没有同 Snapshot、不同正式路径的 run ids。
- Evaluation：已有非零阈值集合、当前 `BLOCKED` synthetic release decision 和 request-level Gold 隔离证明；仍缺四 Profile Trace Gold 隔离证明、runtime metrics 和真实阈值评估结果。
- Fault：Fault/Security/Resume/Idempotency matrix 未执行。

## 人工分工入口

四张人工 Claude Code 任务卡已写入：

- `.agent/programs/thread-prompts/CC-A-phase22-dataset-corpus-derivation-validator.md`
- `.agent/programs/thread-prompts/CC-B-phase22-canonical-ingestion-three-indexes.md`
- `.agent/programs/thread-prompts/CC-C-phase22-four-profile-runtime-benchmark.md`
- `.agent/programs/thread-prompts/CC-D-phase22-integration-fault-security-evidence.md`

这些任务卡只是人工分派材料，不启动 Worker，不改变 Codex 当前工作流。

## 验证入口

```powershell
python tools/scripts/verify_phase22_synthetic_regression_track.py
```

该 verifier 只证明当前 blocked truth boundary 和任务卡完整性，不证明 Synthetic Track Ready。
