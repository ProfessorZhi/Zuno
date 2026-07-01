# 当前程序

state: active
active_program: zuno-production-document-ingestion-and-thread-foundation-v1
current_phase: PHASE08_verification-doc-sync-and-closure.md
latest_completed_program: zuno-production-architecture-and-deliverables-completion-v1

## 当前状态

`.agent/programs/` 当前已从 no-active 等待态切换为 active program。当前 program 是：

- `zuno-production-document-ingestion-and-thread-foundation-v1`

这个 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1，目标是先把企业知识库的文档解析与索引交接地基写清、做实，并为后续多线程施工准备正式线程提示词、分支边界和验收闸门。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。最近完成的 `zuno-production-architecture-and-deliverables-completion-v1` 仍是一次性交付型成熟化 program，已把 Zuno 推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline；本轮不能改写它的历史 closure evidence。

## 为什么先做 Program 1

Zuno 的最终产品目标不是三个并列产品模式，而是一个企业内部知识库 Agentic GraphRAG 问答系统。Basic RAG 和静态 GraphRAG 只作为 Program 4 的评测对照组，不作为最终用户主模式。

文档解析层是企业知识库系统的入口。如果 PDF、Office、表格、代码、网页、扫描件等资料不能稳定进入统一 Document IR，后续 Memory、Tool、Planning、GraphRAG、Evidence、Citation 和 Eval 都会建立在不可靠输入上。因此本轮先固定解析层和索引交接，再进入并行子系统和规划层。

## Program Suite 排队顺序

1. **Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`**
   - 当前 active program。
   - 负责文档解析、Document IR、parser worker/job lifecycle、索引交接、golden fixtures、Program 2 线程提示词和分支计划。
2. **Program 2：`zuno-runtime-subsystems-parallel-v1`**
   - 后续 queued program。
   - 负责 Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四条独立线程并行。
3. **Program 3：`zuno-agent-planning-integration-v1`**
   - 后续 queued program。
   - 负责合并 Program 2 成果，并把真实 `plan -> ReAct -> observe -> reflect -> replan` 接入 Single Controller / `GeneralAgent` 主线。
4. **Program 4：`zuno-enterprise-knowledge-eval-benchmark-v1`**
   - 后续 queued program。
   - 负责企业知识库问答评测系统、Basic RAG / GraphRAG baseline / Agentic GraphRAG target 对比、LangSmith / OTel trace bridge、release gate。

## 最近完成归档

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：完成 PHASE01-PHASE12 的生产成熟化 program、四大总交付物、八类 runtime-first deliverables、release closure、full verification 和 no-active closure。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。

## 当前执行规则

- 当前 active program 必须从 PHASE01 顺序推进到 PHASE08。当前已关闭 PHASE01-PHASE07；当前进入 PHASE08。
- 每个 phase 只有在代码、测试、trace、eval、verifier 或明确 blocked evidence 支撑后才能关闭。
- 只写 contract、schema、README 或计划不能关闭 runtime phase。
- 外部生产 parser、OCR、LangGraph DB persistence、真实 sandbox、外部 vault、真实网络代理、外部 trace/eval 平台不可用时，只能写 adapter、local fallback、target-blocked evidence 和 Remaining Target。
- Program 2 的多线程提示词只写入 `.agent/programs/thread-prompts/`；提示词目标模式不等于 Codex UI 目标模式。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
