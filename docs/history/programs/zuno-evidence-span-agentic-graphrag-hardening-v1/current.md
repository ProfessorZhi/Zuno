# 当前程序

state: completed
program: zuno-evidence-span-agentic-graphrag-hardening-v1
active_program: none
current_phase: none
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## 当前状态

本文是 evidence-span hardening program 的完成归档快照：

- Program：`zuno-evidence-span-agentic-graphrag-hardening-v1`
- 中文名：Zuno evidence-span Agentic GraphRAG 质量加固 Program
- 当前 Phase：none
- 状态：completed / archived

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
- Current：PHASE01 focused tests 和 workflow verifier 已通过，当前 active phase 已推进到 PHASE02 source span provenance contract。
- Current：PHASE02 已完成 source span provenance contract，本地 IR -> handoff -> index metadata / citation_lineage -> EvidenceItem / Citation / trace 能保留 document、source object、document version、block、chunk、span、source URI、content hash 和 parser 字段；缺失 page / char offset 时保持 `null`，不 fake span。
- Current：local citation-sized chunk handoff 已进入 BM25 / vector / GraphRAG / evidence / citation handoff，citation chunks 保留 parent context、neighbor chunks、source span provenance 和 runtime chunking config；这不是 Evidence Text Available@5 达标证明。
- Current：local lexical / phrase evidence path 已进入 retrieval ranking 和 trace metadata，输出 retriever source、raw / normalized score、rank、matched terms / phrase 和 candidate reason；该路径不读取 benchmark gold labels。
- Current：local deterministic graph evidence lineage 已进入 trace：entity / relation / community report 能回源到 supporting chunks 和 source spans；external graph DB 仍是 Target。
- Current：local deterministic evidence-aware reranker 已进入 Agentic retrieval，trace 输出 feature scores、pre/post rank、rank delta 和 selected reason；external reranker provider 仍是 Target。
- Current：local deterministic claim-level citation binder 已进入 Agentic retrieval，trace 和 task event 输出 claim -> evidence binding、support / contradict / insufficient verdict、citation label、chunk、block、source span 和 action；只有带 source span 的 evidence 能成为 strict claim citation，doc-level citation 不算 strict citation。
- Current：PHASE08 已完成 `hard_negative_coverage` 与 `release_gate` 输出面；两次本地真实 paired eval 尝试未完成 agentic profile，因此 release gate 没有 measured pass，当前结论是 `blocked_not_measured_due_to_agentic_profile_incomplete`。
- Target：修复或拆分 agentic profile runner 后，重新运行 fixed paired benchmark，把 `Evidence Text Available@5` 提高到可作为 release gate 的水平，并让 citation accuracy 进入可解释增长区间。
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

归档时，本 program 的完成文件包括：

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

## 完成边界

- 已完成 eval truth source / gap buckets、source span provenance、citation-sized chunking、lexical / phrase retrieval、local graph evidence lineage、evidence-aware reranker、claim-level citation binder、hard negative coverage 与 release gate 输出面。
- Runtime 行为修改仍必须由 focused tests、E2E、trace/eval 或 verifier 证明后才能写成 Current。
- 不得把 doc-level retrieval 增益写成 evidence-span citation 已完成。
- 不得把 `deep_graphrag` 冒充为完整产品 Agentic Runtime；当前主线仍是 Single Controller / Single `GeneralAgent`。
- PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index、external observability sink 和 CI release gate operations 仍是 Production Scale Target，除非未来 phase 接入真实 provider 并通过验证。
