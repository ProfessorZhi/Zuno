---
name: jd-enterprise-project
description: Design a realistic, interviewable, and implementable enterprise project from a job description, target role, constraints, and optional repository. Use only when the user or an upper Coordinator explicitly invokes jd-enterprise-project; do not invent production evidence or silently compose other Skills.
---

# JD Enterprise Project

## Purpose

从岗位要求推导一个真实、可实现、边界清楚、能深入讲并能产生工程证据的项目，不为了简历堆砌技术名词。

## Activation

```text
ACTIVATION: EXPLICIT_ONLY
COMPOSITION: EXPLICIT_ONLY
```

只有用户或上层 Coordinator 明确指定本 Skill 名称或路径时才读取。它可以建议后续调用其他 Skill，但不能隐式调用。

## Inputs

- JD、Target Role、Target Seniority；
- 时间、团队、技术和交付限制；
- Existing Repository、Architecture、Tests、Evidence，可选；
- 真实用户、业务域或部署边界，可选。

## Workflow

按以下顺序收敛，不从技术名词反推产品：

```text
JD Analysis
→ Competency Model
→ Business Problem
→ Minimal Product
→ Overall Architecture
→ Runtime Flow
→ State Ownership
→ Failure / Recovery
→ Security
→ Eval
→ Build / Buy
→ Complexity Kill
→ Module / Contract
→ Current / Target / Gap
→ Implementation Plan
→ Interview Red-Team
```

如果传入 Existing Repository，必须先分析 Current，再设计 Target。每个 Target 都要能回到用户问题、状态 Owner、失败语义、验证指标和实施范围。

## Outputs

- Product 和 End-to-End Runtime 叙事；
- `CURRENT`、`TARGET`、`GAP`、`EVIDENCE_REQUIRED` 矩阵；
- Architecture、State、Failure、Security、Eval 和 Build/Buy 决策；
- Implementation Roadmap、Codex Task 候选和 Interview Defense Package；
- Fact Gap、Measurement Gap 和外部资格缺口。

没有 Existing Repository 时，明确标记 `DESIGN_AVAILABLE` 和 `IMPLEMENTATION_NOT_PROVEN`。

## Boundaries

- JD 写 Kafka 不等于必须使用 Kafka，写 Agent 不等于必须 Multi-Agent，写 RAG 不等于必须 GraphRAG；
- 不替代正式 Facts、Architecture、ADR、Evidence 或用户事实确认；
- 不把设计出来的能力写成已实现、上线、生产或性能提升；
- 不虚构用户数、QPS、SLA、准确率、客户、个人贡献或部署环境；
- 不自动修改文件、调用 Codex、创建 Worktree、Branch、Commit 或 Push；
- 不拥有 Architecture Decision；最终裁决交给 ChatGPT Main 或用户。

## Failure / Stop Conditions

- JD 或用户问题不足以决定产品边界时停在假设清单；
- Existing Repository 与 Target 混淆时先建立 Current / Target / GAP；
- 关键需求只能由技术名词猜出时返回 FACT_GAP；
- 无法为复杂度定义验证指标时选择更简单设计或 MEASUREMENT_BLOCKED；
- 需要修改业务 Runtime、API、Schema、Dependency 或生产 Infra 时停止并单独授权。

## Evidence Rules

每个项目主张都注明来源和状态。论文、JD、目录、依赖、Mock 和架构草图只能支持候选或背景，不能证明历史实现或生产成果。面试准备与 Production Readiness 是两条独立轨道。

## Example Invocation

```text
请明确调用 jd-enterprise-project，根据这份 Backend/AI Platform JD 和已有仓库设计一个最小案件分析产品。
先分析 Current，再推导 Minimal Product、Architecture 和 Implementation Plan；所有未实现内容标为 TARGET。
```
