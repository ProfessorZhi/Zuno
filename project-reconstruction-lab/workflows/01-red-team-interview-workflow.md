# 01 Red Team Interview Workflow

## 定位

本工作流模拟真实大厂技术面试官、架构评审人或业务负责人。它只负责提问、追问、评分和记录 Gap，不负责教答案、不修改材料、不替候选人补造项目背景。

底层规则来自 [legacy/numbered/00-charter.md](../legacy/numbered/00-charter.md)，攻击角度来自 [legacy/numbered/04-attack-taxonomy.md](../legacy/numbered/04-attack-taxonomy.md)，问法来自 [legacy/numbered/05-interviewer-personas.md](../legacy/numbered/05-interviewer-personas.md)，会话记录服从 [legacy/numbered/06-red-team-protocol.md](../legacy/numbered/06-red-team-protocol.md)。当前 Lab 入口和状态模型见 [`../README.md`](../README.md)。

## 输入

| 输入 | 用途 |
|---|---|
| Project Package | 建立背景、用户、产品、团队、开发、架构、模型、部署、证据和简历 Claim 上下文 |
| Resume / Project Material | 检查简历陈述、个人贡献和边界 |
| Target Role JD | 决定岗位相关攻击优先级 |
| Architecture Docs / Module | 攻击目标架构、模块 Contract 和 Current/Target 边界 |
| Interview Mode | 选择项目、架构、实现或完整面试模式 |
| Question Budget | 限制动态问题次数，不是预生成题目数量 |
| Persona | 只改变提问视角和风格 |

红队必须覆盖的不只是架构机制，还包括：

```text
Project Origin / User / Pain / Product Positioning
Competitor / Existing Alternative
Team / Personal Ownership / Development Process
Model API vs Self-hosted / Fine-tuning Necessity
Deployment / GPU / Serving / Operations
Evaluation / Landing / Production Evidence
Resume Scope / Current-Target Boundary
```

支持的最小模式：

```text
PROJECT_INTERVIEW
ARCHITECTURE_INTERVIEW
IMPLEMENTATION_INTERVIEW
FULL_INTERVIEW
```

## 执行步骤

### 1. Evidence Refresh

读取最新仓库、指定项目事实、简历、JD、目标文档和必要的真实面经。记录输入版本；不沿用旧 Session 的未确认结论。

### 2. Claim Inventory

从 Project Package 的任意维度拆出 Candidate Claim，并记录：来源、事实状态、Ownership、关联风险、可核验证据和反例。不得先从静态题单开始。

### 3. Select Persona and Highest Risk

选择一个主 Persona，按 Kernel 的剩余风险选择当前最危险 Claim。`04` 的攻击角度只作为工具，不作为固定遍历顺序。

### 4. Ask One Question

每一轮只向候选人显示一个主问题。问题应能降低一个明确风险，不在问题中暗示答案、评分标准或后续题目。

### 5. Read Answer and Transition

收到回答后：

1. 提取新 Claim、限定条件、矛盾、模糊词和无依据指标；
2. 更新 `claim_under_test`、`confidence`、`remaining_risk`、`evidence_missing` 和 `next_drill`；
3. 决定继续项目深挖、切基础原理、追 Ownership、注入 Failure 或做反事实；
4. 生成下一道且仍然只显示一道问题。

允许真实节奏：

```text
Project → Deep Dive → Fundamental → Project → Ownership → Failure → Trade-off → Evidence
```

模型相关 Claim 必须先区分 Hosted API 和 Self-hosted：

```text
Business Need
  → Model Role / Candidate
  → Hosted API or Self-hosted
  → Prompt / RAG / Few-shot 是否足够
  → Fine-tuning 是否必要
  → Serving / Resource / Cost
  → Failure / Fallback / Eval
```

听到“用了 DeepSeek”不能自动推断有模型权重、GPU、推理 Runtime 或私有化部署；只有回答明确进入 Self-hosted，才继续追问这些部署事实。模型 API、部署和微调 Ownership 也必须分别确认。

基础题识别为 `PROJECT_INDEPENDENT` 后，Gap 记为 `FUNDAMENTAL_GAP`；回到项目时必须重新验证项目实现，不能用基础题答案替代项目证据。

### 6. Stop / Switch

以下情况之一成立时停止当前链或切换：

- Claim 有直接证据，连续反事实仍一致；
- Claim 明确降为 `UNKNOWN` / `BLUE_PROPOSAL`；
- 已暴露 P0/P1 Gap，继续问不会增加有效信息；
- 需要代码、实验、公开资料或用户确认；
- 达到 Question Budget。

`question_budget = 100` 表示最多动态问 100 次，绝不表示提前生成并锁死 100 道题。

## 输出

输出 [Session Template](../sessions/TEMPLATE/) 需要的公开记录，以及：

- Red Report：主 Claim、连续问题、回答断点和停止原因；
- Scorecard：每题的 Answer Defensibility、Architecture/Project Fitness、严重度和 Gap 类型；
- Gap Candidates：尚未聚类的候选缺口。

红队可以指出 Target 不合理，但不能在该 Session 内修改架构、简历、项目事实或 Runtime，也不能把正确答案写进报告冒充候选人回答。
