# 当前程序

state: active
active_program: zuno-evidence-span-agentic-graphrag-hardening-v1
current_phase: PHASE01_eval-truth-source-and-gap-buckets.md
latest_completed_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1

## 当前状态

`.agent/programs/` 当前打开新的 evidence-span hardening program：

- Program：`zuno-evidence-span-agentic-graphrag-hardening-v1`
- 中文名：Zuno evidence-span Agentic GraphRAG 质量加固 Program
- 当前 Phase：`PHASE01_eval-truth-source-and-gap-buckets.md`
- 状态：active

这个 program 的第一性目标不是继续堆 GraphRAG 名词，而是把已经出现的 doc-level Agentic Retrieval 增益，转成 evidence-span-level retrieval、claim-level citation 和 answer correctness 增益。

Program 3 Mega `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1` 已完成 PHASE01-PHASE15，并归档到：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

Program 3 Mega 的 Current 结论保持不变：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

成熟度和 runtime-first 交付物边界仍以 `docs/architecture/production-readiness.md` 为准。

本轮新增事实边界：

- Current：已有 EnterpriseRAG paired benchmark、standard / deep / agentic profile 对比、Evidence Text Available 指标、source doc citation 指标和 failure diagnostics 基础。
- Current：上一轮结果显示 agentic floor fusion 能提高 doc-level retrieval / source-doc citation，但 strict citation 与 evidence text availability 仍是主要短板。
- Current：PHASE01 已完成 EnterpriseRAG paired eval failure bucket 诊断面，`metrics.json`、`report.md` 和 `failure_cases.md` 能区分 `doc_miss`、`doc_hit_text_miss`、`text_hit_citation_miss`、`citation_hit_answer_wrong`；trace 字段不足时输出 `unavailable_due_to_missing_trace_fields`。
- Target：把 `Evidence Text Available@5` 从不可用水平提高到可作为 release gate 的水平，并让 citation accuracy 进入可解释增长区间。
- Future：生产级 external graph index、external vector DB、OCR / VLM、长期 metrics store 和在线 release gate 仍是 Production Scale Target。

## 本轮质量目标

先以 EnterpriseRAG paired benchmark 为主，不把其他数据集结论混入当前 release gate。

```text
Evidence Text Available@5 >= 0.60
Source Doc Citation >= 0.85
Citation Accuracy >= 0.30 first hardening target
Answer Correctness >= standard_rag baseline
```

这些指标必须来自 fixed paired benchmark。blocked、prepared、runtime observed 或缺失数据不能写成 measured。

## 当前 Front Path 文件

active 状态下，`.agent/programs/` 根目录保留：

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_eval-truth-source-and-gap-buckets.md`
- `.agent/programs/PHASE02_source-span-provenance-contract.md`
- `.agent/programs/PHASE03_citation-sized-chunk-index.md`
- `.agent/programs/PHASE04_lexical-phrase-evidence-retriever.md`
- `.agent/programs/PHASE05_entity-chunk-bidirectional-graph-index.md`
- `.agent/programs/PHASE06_evidence-aware-reranker.md`
- `.agent/programs/PHASE07_claim-level-citation-binder.md`
- `.agent/programs/PHASE08_hard-negative-eval-and-release-gate.md`
- `.agent/programs/queued-programs/README.md`

## 历史入口

- `zuno-production-document-ingestion-and-thread-foundation-v1`：Program 1，归档于 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`。
- `zuno-enterprise-document-ingestion-platform-v2`：Program 2 / Product V1 local durable ingestion baseline，归档于 `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`。
- `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`：Program 3 Mega，已吸收原 `zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1` 和 `zuno-enterprise-knowledge-eval-benchmark-v1`。
- `zuno-production-architecture-and-deliverables-completion-v1`：一次性交付型成熟化 program，归档于 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。
- `zuno-target-architecture-runtime-full-implementation-v1`：runtime-first / vertical-slice-first 闭环，归档于 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。
- `zuno-master-architecture-implementation-v1`：目标架构实现归档，归档于 `docs/history/programs/zuno-master-architecture-implementation-v1/`。

## 当前执行规则

- PHASE01 已完成 eval truth source 和 gap buckets 诊断面；下一步是 PHASE02 source span provenance contract，不直接改 citation builder 猜答案。
- Runtime 行为修改仍必须由 focused tests、E2E、trace/eval 或 verifier 证明后才能写成 Current。
- 不得把 doc-level retrieval 增益写成 evidence-span citation 已完成。
- 不得把 `deep_graphrag` 冒充为完整产品 Agentic Runtime；当前主线仍是 Single Controller / Single `GeneralAgent`。
- PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index、external observability sink 和 CI release gate operations 仍是 Production Scale Target，除非未来 phase 接入真实 provider 并通过验证。
