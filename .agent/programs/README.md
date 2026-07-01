# Agent 执行计划

`.agent/programs/` 当前处于 active program 状态。

## 当前 Active Program

- State: active
- Active program: `zuno-production-document-ingestion-and-thread-foundation-v1`
- Current phase: `PHASE08_verification-doc-sync-and-closure.md`
- Latest completed program: `zuno-production-architecture-and-deliverables-completion-v1`

当前 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的第一段。它先把企业知识库文档解析与索引交接地基做扎实，并为后续 Program 2 多线程施工准备可直接投递的目标模式提示词、分支边界和验收闸门。

## 当前文件

- `current.md`：当前 active program 状态、suite 顺序和执行规则。
- `implementation-roadmap.md`：Program 1-4 总路线、依赖关系、验收和验证命令。
- `closure-checklist.md`：Program 1 收口清单、证据要求和归档规则。
- `PHASE01_program-truth-source-and-parser-current-audit.md`：已完成打开 program、确认边界、审计解析层 Current。
- `PHASE02_document-ir-and-parser-contract-freeze.md`：已完成 Document IR、parser adapter contract 和 parser capability matrix 冻结。
- `PHASE03_parser-worker-runtime-and-job-lifecycle.md`：已完成本地 parser worker / job lifecycle / retry / metrics。
- `PHASE04_native-text-and-structured-file-parsers.md`：已关闭 native 文本、Markdown、CSV、JSON、HTML、代码 parser 与 fixtures。
- `PHASE05_pdf-office-ocr-adapter-boundaries.md`：已关闭 PDF / Office / OCR adapter、fallback、依赖探测和 target-blocked 边界。
- `PHASE06_index-handoff-provenance-and-fixtures.md`：已关闭解析到索引 manifest、provenance、ACL 和 citation lineage。
- `PHASE07_program2-thread-prompts-and-branch-plan.md`：已关闭 Program 2 多线程目标模式提示词、分支边界和合并计划。
- `PHASE08_verification-doc-sync-and-closure.md`：当前 phase，验证、文档同步、自维护审查、归档和 no-active / next-program 交接。
- `queued-programs/`：Program 2-4 的后续计划，不是当前 active phase。

## 使用规则

- `.agent/programs/` 根目录只保存当前 active program 的 phase 文件。
- 后续 queued program 可以先放在 `queued-programs/`，但不得被写成 active program。
- completed program 必须整体归档到 `docs/history/programs/`。
- 新 program 必须从 PHASE01 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须先由当前主线程生成提示词和分支边界；子线程必须由用户在 Codex UI 中确认真实目标模式。
