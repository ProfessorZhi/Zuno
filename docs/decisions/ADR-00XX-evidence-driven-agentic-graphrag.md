# ADR-00XX: Evidence-Driven Agentic GraphRAG

- Status: Proposed
- Date: 2026-08-04
- Scope: Knowledge / Agentic GraphRAG

## Context

企业知识库 Agent 面临的问题不是单纯提升检索数量，而是需要回答：

- 当前问题需要什么证据；
- 哪些检索路径具有必要性；
- 证据是否足够支撑 Claim；
- 证据冲突、缺失和过期时如何处理。

固定 Hybrid RAG 或固定 GraphRAG Pipeline 难以表达动态证据获取过程。

## Decision

Zuno 采用 Evidence-Driven Agentic GraphRAG 作为 Target 架构方向。

核心原则：

1. Agent Core 负责任务目标、计划、预算、Replan 和最终控制。
2. Knowledge 模块负责证据获取、检索路径选择、Evidence Ledger 和 Knowledge Control Proposal。
3. 模型只能产生 Proposal，不直接提交领域事实状态。
4. GraphRAG 是 Knowledge Capability，不是所有查询默认路径。
5. 检索循环必须具备停止条件、预算约束和证据质量判断。

## Retrieval Flow

```text
Question
  -> Evidence Goal
  -> Retrieval Plan
  -> Retrieve
  -> Evidence Assessment
  -> Corrective Probe / Stop
  -> Selected Evidence Bundle
```

## Non Goals

本 ADR 不引入：

- 产品级 Multi-Agent Runtime；
- 独立 Retrieval Agent 集群；
- 无审计的自动知识写入；
- 用模型替代确定性安全、权限和引用校验。

## Consequences

正面：

- 检索过程可解释；
- 证据质量可评测；
- 支持复杂企业知识场景。

成本：

- 增加 Evidence Contract；
- 增加 Trace 和 Eval 维度；
- 需要明确 Knowledge 与 Agent Core Ownership。

## Verification

Target 变为 Current 前必须具备：

- Contract 实现；
- Migration；
- Retrieval Trace；
- Eval 数据；
- Fault Test；
- 文档同步。