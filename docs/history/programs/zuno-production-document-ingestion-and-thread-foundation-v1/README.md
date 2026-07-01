# Zuno Production Document Ingestion and Thread Foundation V1

> 状态：completed / archived。此目录是历史证据，不是当前 active program。

## 范围

本 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1，目标是把企业知识库文档入口地基做实，并为 Program 2 多线程施工准备提示词、分支边界和验收闸门。

## 完成内容

- PHASE01：parser current audit 与 workspace ingest gap evidence。
- PHASE02：Document IR、document version、source hash、parser config hash、schema version、parser adapter contract 和 parser capability matrix。
- PHASE03：本地 parser worker / job lifecycle / retry / metrics / snapshot / idempotency。
- PHASE04：native text / Markdown / CSV / JSON / HTML / code parser baseline 与 golden fixtures。
- PHASE05：PDF / Office / OCR / VLM adapter boundary、dependency probe、privacy / network / budget gate 和 target-blocked evidence。
- PHASE06：index manifest parse lineage、diagnostics digest、ACL、sensitivity 和 citation lineage handoff。
- PHASE07：Program 2 thread prompts、branch / worktree plan、allowed / forbidden paths、focused tests、stop conditions 和主线程合并顺序。
- PHASE08：workspace ingest -> ParseGateway runtime closure、验证、文档同步、自维护审查、归档和 no-active 状态交接。

## 归档文件

- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- `PHASE01_program-truth-source-and-parser-current-audit.md`
- `PHASE02_document-ir-and-parser-contract-freeze.md`
- `PHASE03_parser-worker-runtime-and-job-lifecycle.md`
- `PHASE04_native-text-and-structured-file-parsers.md`
- `PHASE05_pdf-office-ocr-adapter-boundaries.md`
- `PHASE06_index-handoff-provenance-and-fixtures.md`
- `PHASE07_program2-thread-prompts-and-branch-plan.md`
- `PHASE08_verification-doc-sync-and-closure.md`
- `thread-prompts/`

## 关键边界

Current 只包括本地可验证 ParseGateway、Document IR、parser snapshot、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 和 Program 2 prompt handoff。生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index、生产 sandbox、外部 vault 和外部 trace / eval 仍是 Remaining Target。
