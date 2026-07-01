# Program Roadmap

state: active
active_program: `zuno-production-document-ingestion-and-thread-foundation-v1`
current_phase: `PHASE02_document-ir-and-parser-contract-freeze.md`
latest_completed_program: `zuno-production-architecture-and-deliverables-completion-v1`

## 总套件

本轮套件名：

`zuno-enterprise-agentic-graphrag-production-suite-v1`

核心目标：

```text
企业内部资料
  -> 多格式解析
  -> Document IR
  -> index / graph handoff
  -> Single Controller Agentic GraphRAG
  -> plan / react / observe / reflect / replan
  -> cited answer / artifact / trace
  -> automated enterprise KB eval
```

Zuno 最终产品不是 Basic RAG、GraphRAG、Agentic GraphRAG 三个并列模式。最终产品是企业知识库 Agentic GraphRAG Agent。Basic RAG 与静态 GraphRAG 是 Program 4 的评测 baseline，用来证明 Agentic GraphRAG 是否真的在多跳、跨文档、引用和低幻觉方面更强。

## Program 1：Document Ingestion 与线程地基

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：active。

目标：把文档解析层从本地 deterministic baseline 推进到可继续 productionize 的 parser worker / Document IR / index handoff 基线，并准备 Program 2 多线程执行资产。

正式架构契约：

- `docs/architecture/document-ingestion-foundation.md`

Program 1 不是只做 parser adapter 清单；它要把企业知识库文档入口的 local runtime slice 和 production Target 边界讲清楚。近期闭环是 `workspace file -> ParseGateway -> CanonicalDocumentIR -> index handoff -> IndexJobManifest -> retrieval / citation provenance`。生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index 和 reconciler 只写为 Target，不能写成 Current。

### Phase 顺序

1. `PHASE01_program-truth-source-and-parser-current-audit.md`
   - 已完成：确认 worktree、branch、status、Current / Target 边界。
   - 已完成：审计当前 parser registry、Document IR、fixtures、index handoff 和 tests。
   - 已完成：确认 workspace ingest 仍绕过 `ParseGateway`，并记录 `_document_from_file()` / `workspace_text_runtime` gap。
2. `PHASE02_document-ir-and-parser-contract-freeze.md`
   - 当前 phase。
   - 冻结 parser capability matrix、adapter contract、Document IR 字段、document version、source hash、parser config hash、schema version 和 target-blocked 表达。
3. `PHASE03_parser-worker-runtime-and-job-lifecycle.md`
   - 实现本地 parser worker 抽象、job state、retry、metrics、snapshot、idempotency、blocked / failed / dead-letter 语义，并把 outbox / lease / reconciler 保留为 Target。
4. `PHASE04_native-text-and-structured-file-parsers.md`
   - 强化 `txt/md/csv/json/html/code` 等 native parser，让 heading、table cell、JSON pointer、HTML table、code line range 等结构化输出可测试。
5. `PHASE05_pdf-office-ocr-adapter-boundaries.md`
   - 处理 PDF / Office / OCR / VLM enrichment adapter、local fallback、依赖探测、network / privacy / budget gate 和 Remaining Target。
6. `PHASE06_index-handoff-provenance-and-fixtures.md`
   - 证明解析结果能进入 index manifest，并保留 source span、ACL、parser version、document_version_id、parse_job_id、parse_attempt_id、source_sha256、parser_config_hash 和 citation lineage。
7. `PHASE07_program2-thread-prompts-and-branch-plan.md`
   - 生成 Program 2 四条子线程目标模式提示词：Memory / Tool / Security / GraphRAG。
8. `PHASE08_verification-doc-sync-and-closure.md`
   - 运行验证、更新文档、归档 program，并把下一轮切到 Program 2 或 no-active。

### Program 1 验收

- parser matrix 明确支持、fallback、target-blocked 三种状态。
- 所有 golden fixtures 可复现解析为 Document IR。
- parser worker / job lifecycle 有状态、失败原因、重试、metrics 和 snapshot。
- workspace ingest 通过 `ParseGateway.submit_parse_job()` 进入 `CanonicalDocumentIR` 和 `KnowledgeIndexRuntime.index_document()`，不再依赖 `workspace_text_runtime` 单 block stub 作为产品闭环。
- index handoff 能追踪 source file、block id、page / section、parser version、ACL、document version、parse job / attempt 和 manifest provenance。
- `docs/architecture/document-ingestion-foundation.md` 明确 Current local runtime slice、Remaining Target infrastructure、target-blocked parser / OCR / VLM evidence。
- Program 2 的线程提示词写入 `.agent/programs/thread-prompts/`，并给出独立 branch / worktree / allowed paths / forbidden paths / verification gates。

## Program 2：Runtime Subsystems Parallel

Program ID：`zuno-runtime-subsystems-parallel-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`。

目标：在 Program 1 的解析和索引地基稳定后，使用多线程模式并行推进四个低耦合子系统。

线程：

1. Memory / Context：分层记忆、上下文压缩、semantic fallback、privacy delete、sensitive exclusion、memory eval。
2. Tool / Sandbox：Tool Control Plane、approval ledger、network policy、credential-ref-only、sandbox adapter。
3. Security / Governance：prompt injection、retrieval gate、tool gate、output DLP、cross-workspace leakage tests。
4. GraphRAG / Index：enterprise knowledge schema、RRF/rerank trace、GraphRAG baseline runner、external index adapter boundary。

Program 2 不直接重写 `GeneralAgent` 主循环；它只产出可被 Program 3 合并的模块能力、tests 和 evidence。

## Program 3：Planning Integration

Program ID：`zuno-agent-planning-integration-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM03_agent-planning-integration.md`。

目标：把 Program 2 的 Memory、Tool、安全、GraphRAG 能力合并进 Single Controller Agent，并实现真实 `plan -> ReAct -> observe -> reflect -> replan` 闭环。

Program 3 是高冲突 program，默认由主线程集中执行，必要时只用 subagent 做只读审计。它不得把 Zuno 产品 runtime 改成多 Agent。

## Program 4：Enterprise Knowledge Eval Benchmark

Program ID：`zuno-enterprise-knowledge-eval-benchmark-v1`

状态：queued。计划文件：`.agent/programs/queued-programs/PROGRAM04_enterprise-knowledge-eval-benchmark.md`。

目标：建设企业知识库问答自动化评测系统，对同一 corpus 和 question set 比较 Basic RAG baseline、Static GraphRAG baseline 和 Agentic GraphRAG target。

Program 4 指标：

- Retrieval：`recall@k`、`precision@k`、MRR、NDCG、hit rate、context precision / recall。
- Answer：correctness、faithfulness、citation coverage、source-span accuracy、unsupported claim rate、refusal correctness。
- Agent：plan step success、replan usefulness、tool trajectory correctness、reflection decision accuracy。
- Ops：latency、cost、trace completeness、redaction correctness、LangSmith / OTel export coverage。

## 验证基线

Program 1 文档与 workflow 基线：

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

Program 1 runtime focused tests 会按 phase 增加，默认从 `tests/knowledge/`、`tests/repo/` 和 parser / index 相关 tests 中选择最小可失败集合。

## 停止条件

- 工作树出现用户未说明的冲突修改。
- 需要真实外部 parser、OCR、vault、sandbox、network proxy、LangSmith token 或生产 DB，且无法用 adapter / local fallback / target-blocked evidence 推进。
- 验证要求修改 runtime 公共 API、数据库 schema 或兼容路径，但当前 phase 未授权。
- Program 2 子线程需要真实 Codex UI 目标模式，但当前工具不能创建或确认；此时只能输出提示词文件路径，等待用户手动创建或改为挂机模式。
