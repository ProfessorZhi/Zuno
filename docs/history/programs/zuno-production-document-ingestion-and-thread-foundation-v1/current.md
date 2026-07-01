# 归档时 Program 状态

> 归档说明：此文件是 `zuno-production-document-ingestion-and-thread-foundation-v1` 关闭时保存的历史状态面，不代表当前 active program。

state: completed / archived
active_program: none
archived_program: zuno-production-document-ingestion-and-thread-foundation-v1
current_phase: none

## 目标

本 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1，负责关闭企业知识库文档入口的本地可验证地基：

```text
workspace file
  -> ParseGateway
  -> CanonicalDocumentIR
  -> parser job snapshot
  -> KnowledgeIndexRuntime
  -> IndexJobManifest
  -> retrieval / citation provenance
```

Program 1 同时为 Program 2 准备 Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四条线程提示词、分支、worktree、允许范围、禁止范围和 focused tests。

## 完成阶段

- `PHASE01_program-truth-source-and-parser-current-audit.md`：completed。
- `PHASE02_document-ir-and-parser-contract-freeze.md`：completed。
- `PHASE03_parser-worker-runtime-and-job-lifecycle.md`：completed。
- `PHASE04_native-text-and-structured-file-parsers.md`：completed。
- `PHASE05_pdf-office-ocr-adapter-boundaries.md`：completed。
- `PHASE06_index-handoff-provenance-and-fixtures.md`：completed。
- `PHASE07_program2-thread-prompts-and-branch-plan.md`：completed。
- `PHASE08_verification-doc-sync-and-closure.md`：completed。

## Release Gate 结果

- `.agent/programs/` 已回到 no-active 等待态。
- Program 2-4 仍是 queued，不在本 program 中启动。
- Program 2 thread prompts 已归档到 `thread-prompts/`。
- full verification 结果见 `closure-summary.md`。
- 生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index、生产 sandbox、外部 vault、外部 trace / eval 和 online eval 仍是 Remaining Target，不写成 Current。
