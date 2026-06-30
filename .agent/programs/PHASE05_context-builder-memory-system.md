# PHASE05 Context Builder Memory System

Program: `zuno-eight-deliverables-full-realization-v1`
status: active

## 为什么

Agentic RAG 的关键不是把更多文本塞进 prompt，而是建立可解释的 Context Pack 和记忆生命周期。没有 owner、source ids、压缩和抽取策略，增强模式会退化成不可验证的拼接。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- Context Pack contract。
- 短期状态、工作记忆、语义记忆、情节记忆、程序性记忆。
- Summary Compression、Structured Extraction、approval / review policy。

## 执行步骤

1. 审计 `src/backend/zuno/memory` 和现有 `platform/services/memory` owner。
2. 定义 Context Pack 数据边界、source ids、token budget 和 compression policy。
3. 实现 memory contracts、rendering、retrieval、review 的可测试路径。
4. 将 context builder 接入 Agent runtime 的准备阶段，但避免大规模重写主循环。
5. 增加 focused tests 和 docs/eval proof。

## 验收

- Context Pack 能说明每块上下文来源、类型、预算和使用方式。
- 五类记忆有边界和 owner，不混成单一 prompt 缓存。
- 记忆写入或抽取有 review / approval 规则。
- Current 文档只陈述已实现能力。

## PR 边界

建议拆成 contract PR、memory runtime PR、integration test PR。
