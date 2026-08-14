---
name: jd-enterprise-project
description: Design a realistic, interviewable, and implementable enterprise project from a job description, target role, engineering constraints, and optional repository. Use when translating a JD into a minimal product and evidence-backed architecture without blindly adding advertised technologies or claiming unimplemented production capabilities.
---

# JD Enterprise Project

## Purpose

从岗位要求推导一个“企业级但不过度设计”的项目，再用 Red/Blue 和事实边界验证它能否真实实现、
解释和维护。

## Inputs

- JD、Target Role、Target Seniority；
- 技术约束、时间和范围；
- 现有 Repository、Architecture、Tests、Evidence（可选）；
- 真实用户、业务域或交付限制（可选）。

## Workflow

1. 从 JD 提取 Business Requirement、核心能力、可靠性、数据、安全、部署和评测期待；
2. 先写 Problem、User 和 Business Workflow；
3. 设计 Minimal Product，不先列技术名词；
4. 依次推导 Overall Architecture、端到端链路、责任边界、状态 Owner、失败/恢复、安全和 Eval；
5. 再决定 Build / Buy / Reuse / Externalize、Scale、Module、Contract、Database 和 Code；
6. 若已有代码，逐项标记 `CURRENT / TARGET / GAP`；
7. 运行 Red Interview → Blue Defense → Red Review → Gap Clustering → Repair → Retest；
8. 输出实现路线、Codex Task 候选、面试防守包、Fact Gap 和 Measurement Gap。

## Outputs

- Product 和 End-to-End Runtime 叙事；
- Current / Target / Gap 矩阵；
- Architecture、State、Failure、Security、Eval 和 Build/Buy 决策；
- Implementation Roadmap、Codex Task 候选和 Interview Defense Package；
- 剩余事实、测量和外部资格缺口。

## Boundaries

- JD 写了 Kafka 不等于必须使用 Kafka；写了 Agent 不等于必须 Multi-Agent；写了 RAG 不等于
  必须 GraphRAG；写了高并发不等于必须微服务；
- 先证明用户问题和工作流，再选择技术；
- 不把设计出来的能力写成已实现、上线、生产或性能提升；
- 不虚构用户数、QPS、SLA、准确率、客户、个人贡献或部署环境；
- 不替代正式 Facts、Architecture、ADR、Evidence 或用户的事实确认。

## Failure / Stop Conditions

- JD 或用户问题不足以决定产品边界时停在假设清单；
- Existing Repository 与 Target 混淆时先建立 Current/Target/GAP；
- 关键需求只能由技术名词猜出时返回 `FACT_GAP`；
- 无法为复杂度定义验证指标时选择更简单设计或 `MEASUREMENT_BLOCKED`；
- 需要修改业务 Runtime、API、Schema、Dependency 或生产 Infra 时停止并单独授权。

## Evidence Rules

每个项目主张都必须注明来源和状态。论文、JD、目录、依赖、Mock 和架构草图只能支持候选或
背景，不能证明历史实现或生产成果。面试准备与 Production Readiness 是两条独立轨道。

## Example Invocation

```text
请使用 jd-enterprise-project，根据这份 Backend/AI Platform JD 和已有仓库，设计一个最小案件
分析产品。先写用户工作流，再判断是否需要 Agent、Graph、Queue 和微服务；所有未实现内容标为 TARGET。
```
