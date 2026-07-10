# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-evidence-span-agentic-graphrag-hardening-v1
current_phase: PHASE02_source-span-provenance-contract.md
latest_completed_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1

`.agent/programs/` 当前打开新的 evidence-span hardening program。

当前 program：

- Program：`zuno-evidence-span-agentic-graphrag-hardening-v1`
- 中文名：Zuno evidence-span Agentic GraphRAG 质量加固 Program
- 当前 Phase：`PHASE02_source-span-provenance-contract.md`
- 状态：active

最近完成并归档的 program 仍是：

- Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- 状态：completed / archived
- 归档：`docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
- Suite：`zuno-enterprise-agentic-graphrag-production-suite-v1`
- 合并关系：原 Program 3 `zuno-enterprise-ingestion-async-infrastructure-v1`、Program 4 `zuno-runtime-subsystems-parallel-v1`、Program 5 `zuno-agent-planning-integration-v1` 和 Program 6 `zuno-enterprise-knowledge-eval-benchmark-v1` 已合并进 Program 3 Mega 并完成，不再作为 queued pipeline 执行。

完成结论：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

Program 3 Mega 已完成 PHASE01-PHASE15，把输入层、Knowledge / Retrieval / GraphRAG、Memory & Context、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、Product API / Frontend、E2E、文档和归档统一收口为本地可验证的 launchable product baseline。

目标产品口径固定为 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。Agent Core 公式是 `Model Gateway + Memory & Context Engine + Planning & Control Runtime + Capability Layer + Governance / Trace / Eval Envelope`。用户在聊天里提出目标，并在勾选知识库时选择标准检索 / 深度检索；GraphRAG、BM25、vector、re-query、rerank、Skill、MCP 和工具调用由 Single Controller Agent 内部自动规划。Skill 是 Capability Layer 里的任务方法包，不是 Tool、不是 Knowledge、也不是产品级多 Agent runtime。Basic RAG 和 Static GraphRAG 只作为 eval baseline，不是最终产品模式。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。真实 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index、external observability sink 和 CI release gate operations 未接入并测试前，仍只能写作 Production Scale Target / target-blocked evidence。

## 本轮 Hardening 目标

本轮不再泛泛讨论 GraphRAG 是否有效，而是用 fixed paired benchmark 判断 evidence-span quality：

```text
Evidence Text Available@5 >= 0.60
Source Doc Citation >= 0.85
Citation Accuracy >= 0.30 first hardening target
Answer Correctness >= standard_rag baseline
```

核心 failure buckets：

- `doc_miss`
- `doc_hit_text_miss`
- `text_hit_citation_miss`
- `citation_hit_answer_wrong`

## 当前 Front Path 文件

active 状态下，`.agent/programs/` 保留：

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

completed program 的 phase、closure evidence 和 merged queued inputs 保存在 `docs/history/programs/`。

## Program Suite 顺序

1. Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
2. Program 2：`zuno-enterprise-document-ingestion-platform-v2`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
3. Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
4. Program 4：`zuno-evidence-span-agentic-graphrag-hardening-v1`
   - 状态：active。
   - 当前 Phase：`PHASE02_source-span-provenance-contract.md`

## 最近完成归档

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`：完成 PHASE01-PHASE15、full verification、docs / architecture expansion、closure summary、no-active closure 和本地提交。
- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`：Product V1 local durable ingestion baseline，完成 PHASE01-PHASE08、durable ingestion、restart recovery、验证和 no-active closure。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 Program 1 的 Document IR、parser worker、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 闭环、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first / vertical-slice-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成 PHASE01-PHASE10 的上一轮八大治理交付物闭环。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：历史 Program 4 / `zuno-six-layer-internalization-v1` 的六层内部入口、README、focused tests 和 verifier guard 完成事实。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成 repo layout cleanup、backend alias surface 收口、root hygiene guard 和 final closure。
- 历史 Program 3 final alias surface closure 已完成；旧 public import path 只通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容，不恢复根级 alias 文件。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- active program 必须从当前 phase 文件出发；PHASE01 已完成，当前从 PHASE02 source span provenance contract 开始，不得跳到后续 phase。
- 新 runtime 行为继续遵守 TDD；只写 contract、schema 或 README 不能关闭 runtime phase。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是评测对照组，不是最终产品模式。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
