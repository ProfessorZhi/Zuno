# Zuno Target Architecture Refresh V1

## 状态

已完成并归档。它不再是 active executable program。

## 目标

把 Zuno 近期目标架构从恢复期叙事继续升版为成熟 Agent / RAG / GraphRAG 工程底座表达，重点是：

- API / Agent / Memory / Capability / Knowledge / Platform / Trace 边界。
- GraphRAG 实体和关系抽取默认采用 LLM extraction。
- 规则、正则、词典只作为确定格式辅助、fallback 或 baseline test。
- 知识库支持多套 extractor / config 选择。
- Memory approval、Capability policy / execution、Evidence / Trace / Eval 是目标架构一等边界。

## 归档文件

- `implementation-roadmap.md`
- `PHASE01_current-target-roadmap-audit.md`
- `PHASE02_target-layer-model-refresh.md`
- `PHASE03_graphrag-llm-entity-knowledge-config.md`
- `PHASE04_memory-capability-trace-boundaries.md`
- `PHASE05_docs-consistency-closure.md`

## 验证边界

本 program 只修改文档、工作流状态面、verifier 和 repo tests。它不实现 runtime，不移动业务目录，不修改 API / DB / frontend / eval baseline。

