# PHASE22 PR #100 Codex Review

## 摘要

PR #100 (`claude-minimax/phase22-synthetic-benchmark` @ `d7566624b702b74ebf6a89db2f916b9ea19b310c`) 只能作为 Claude Code Worker 候选结果，不能整体合并。

当前 `origin/main` 为 `c9d099d64a1af28102231751ce55df8217173e89`。PR #100 的 base 为 `1c7c524d6e87db4b321dcc5782646915866d0378`，已经落后最新 main，并会覆盖 PR #103 的 worker workflow 文档更新。

结论：

```text
worker_decision=BLOCKED
integration_policy=selective_restore_only
accepted_paths=tools/evals/zuno/rag_eval/metrics.py
phase22_status=in_progress
production_readiness=not_established
public_reviewer_approved_count=0
benchmark_eligible_count=0
```

## 阻断原因

PR #100 的 synthetic track 不是正式 Canonical Benchmark：

- `release_decision.json` 写入 `verdict=PASSED`。
- `core_five_metrics.json` 将四个 profile 全部标记为 `MEASURED`。
- `release_decision.json` 使用 `retrieval_recall_at_k=0.0`、`context_precision_at_k=0.0`、`citation_accuracy=0.0` 作为 release threshold。
- `ingest_and_run.py` 使用端口探测作为 runtime dependency 判断，没有通过 Zuno 正式 Owner 产生 KnowledgeVersion、Snapshot、Index activation、Trace、RunOutcome、BudgetSettlement、ArtifactReceipt 或 MeasurementAttestation。
- profile runner 使用 in-memory substring retrieval，不是 ES BM25、Milvus vector、Neo4j graph traversal 或 Agentic GraphRAG runtime。
- `answer` 直接来自 `expected_answer`，citation 直接来自 `gold_document_refs` / `gold_source_spans`。
- `runtime_ingestion.json` 把 `ingestion_status=submitted` 和端口 reachable 写成 index construction evidence，缺少真实 write/read-back、visibility、idempotency 和 activation receipt。
- `validation_report.json` 的 `machine_validated_count=80` 只证明作者生成的数据满足作者写的校验器，不能替代 human reviewer approval。

这些问题命中 PHASE22 completion blocker：Benchmark 仍是 `blocked_not_measured`，PHASE22 必须保持 `in_progress`，Program 必须保持 `active`，Production Readiness 仍未建立。

## ACCEPT / REWORK / DROP

| 路径或文件组 | verdict | Codex 处理 |
| --- | --- | --- |
| `tools/evals/zuno/rag_eval/metrics.py` | ACCEPT | 只吸收 `import math` 修复。该修复独立、低风险、属于真实 metrics bug fix。 |
| `docs/evidence/goal05-phase22-synthetic-benchmark/world_model.json` | REWORK | 可作为 synthetic dataset 候选输入；必须移出 evidence-as-source 模式，并由独立 validator 重新证明 hash、版本、关系和 source span。 |
| `docs/evidence/goal05-phase22-synthetic-benchmark/corpus/**` | REWORK | 可作为 fictional corpus 候选；需要移入正式 dataset 工具路径并补齐授权 principal、role、scope、epoch 与 hash-stable regeneration。 |
| `docs/evidence/goal05-phase22-synthetic-benchmark/synthetic_cases.jsonl` | REWORK | 80 case 可作为候选；必须增加声明式 DerivationSpec，由 validator 从 world model / corpus 独立推导答案，不得把 `expected_answer` 当执行答案。 |
| `build_world_model.py` / `build_cases.py` / `validate_cases.py` | REWORK | 可作为初稿；执行代码不得放在 `docs/evidence`，validator 必须校验 relation kind/from/to/direction、temporal version、source span support、no-answer corpus scan 和 security caller principal。 |
| `case_set_manifest.json` / `corpus_manifest.json` / `graph_manifest.json` / `derived/**` | REWORK | 结构有参考价值；必须由新 generator / validator 重新生成并绑定 source tree、seed、hash 和 schema。 |
| `architecture-change-proposal.md` | REWORK | 保留“synthetic track 不能替代 human review”的边界思想；删除或改写与 canonical profile measured、receipt/attestation capture 不符的声明。 |
| `canonical_ir.json` | DROP | 这是候选脚本生成的静态 IR，不是 Zuno 正式 Ingestion Application Service 产生的 KnowledgeVersion / Snapshot / Owner receipt。 |
| `ingest_and_run.py` | DROP | 使用端口探测、in-memory substring retrieval、expected answer 和自造 receipts/attestations；不得进入主线。 |
| `runtime_ingestion.json` | DROP | `submitted` 和 `reachable` 不能证明 canonical ingestion、三索引 write/read-back、visibility、activation 或 idempotency。 |
| `profile_results/*.json` | DROP | 四 profile 的 `MEASURED` 来自 substring baseline，不是真实 Standard / Local / Deep / Agentic RAG。 |
| `core_five_metrics.json` | DROP | 指标来自无 token、无真实 runtime、无真实 retrieval adapter 的 synthetic run。 |
| `release_decision.json` | DROP | `PASSED` 加零阈值直接违反 PHASE22 release gate。 |
| `failure_buckets.json` | DROP | 基于无效 profile_results 聚合，不能作为 release evidence。 |
| `validation_report.json` | DROP | `80/80 machine_validated` 不能作为 reviewer approval 或 benchmark measurement。 |
| `reproduction.md` / `license_report.md` | REWORK | 可参考格式；必须指向重构后的 dataset tooling 和 truthful blocked/measured boundary。 |
| `.agent/**` / `README.md` stale workflow changes from PR #100 base drift | DROP | PR #103 已在 `main` 建立最新 worker workflow；PR #100 旧基线不得覆盖。 |

## Codex 亲自完成的复杂修复

Codex 新增 `tools/scripts/verify_phase22_synthetic_truth_boundary.py` 并接入 PHASE22 validation。该 verifier 防止 PR #100 类 synthetic 目录进入主线后声明：

- synthetic release `PASSED`；
- profile `MEASURED`；
- 零阈值 release gate；
- `submitted` index job 冒充 canonical write/read-back proof。

## 下一步 Worker Wave

第一轮 worker 只处理可隔离的重复性工作：

- `CC-MM-1`：重构 synthetic dataset / validator 候选，不运行真实 benchmark，不修改 PHASE22 状态。
- `CC-DS-1`：调查 canonical ingestion 正式入口和 owner gaps，缺口精确返回 `BLOCKED_WITH_EXACT_GAP`。
- `CC-MM-2`：探测本地依赖环境与 write/read-back/fault matrix，不把环境健康写成 benchmark pass。

合并规则：worker branch 不整体 merge；只允许 Codex 审查后 `git restore --source=<WORKER_SHA> -- <EXACT_ACCEPTED_PATHS>`。
