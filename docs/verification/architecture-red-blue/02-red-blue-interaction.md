# Red / Blue Interaction：红蓝队互动协议

## 角色分工

### 红队：挑刺和取证

红队一次只攻击一个 Claim，重点问：为什么做、谁需要、谁负责、为什么这样设计、是否过度、失败怎么办、怎么证明、现在做到哪。红队不负责替蓝队修复。

### 蓝队：事实、决策和修复

蓝队不是把每个问题都答成“可以实现”，而是做五种回应之一：

```text
ACCEPT_FACT       接受事实，并提供来源
REJECT_PREMISE    指出问题前提不成立
SCOPE_DOWN        缩小范围，降低当前承诺
PROPOSE_DESIGN    提出新的 Target 方案
REQUEST_EVIDENCE  承认需要代码、测试、用户或指标证明
```

### 裁判：决定是否写回

裁判确认：

- 这是事实、Proposal 还是未知；
- 是否同意改变架构语义；
- 应写到哪个 Canonical Owner；
- 是修复表达、补架构、补实现还是补评测。

## 一次互动的固定轮次

```text
Round 0 事实确认
  → 用户提供背景、规模、团队、当前状态和约束

Round 1 红队首问
  → 从一个最高风险 Claim 开始，不显示攻击意图

Round 2 蓝队回应
  → 用户确认事实；Agent 可提出方案，但标为 Proposal

Round 3 红队追击
  → 注入替代方案、规模、故障、竞品或团队约束

Round 4 裁判决定
  → 接受、缩小范围、补证据、改架构或继续盘问

Round 5 Agent 整理
  → 生成可审阅的变更提案，不自动写入正式文档

Round 6 Blue Fix / Red Retest
  → 获得确认后写回，再用不同问题复测
```

## 关键互动：如何补全团队合作关系

Agent 不应该直接写：“A 负责后端，B 负责模型，C 负责部署”。正确做法是两阶段：

### 阶段一：用户确认实际事实

```text
团队共有几人？
谁负责需求/业务？
谁负责 Agent / Knowledge / Backend / Frontend / Data / Deployment？
哪些决策由谁拍板？
你实际写过或维护过哪些部分？
哪些部分你只是参与、评审或学习？
```

### 阶段二：Agent 提出角色级 Proposal

Agent 生成一张不带虚构姓名的矩阵：

| 工作流 | 决策 Owner | 实现 Owner | Review/依赖 | 当前/目标 |
|---|---|---|---|---|
| 需求与场景 | 待确认 | 待确认 | 法务/业务 | Current/Target |
| Agent 控制 | 待确认 | 待确认 | Model/Tool | Current/Target |
| Knowledge/RAG | 待确认 | 待确认 | Ingestion/Eval | Current/Target |
| 后端与部署 | 待确认 | 待确认 | DB/Queue/Security | Current/Target |
| 评测与发布 | 待确认 | 待确认 | 业务验收 | Current/Target |

用户只需要逐格确认“事实 / 不对 / 未来计划”。确认后才可以把它写进项目背景或协作说明。

## 关键互动：Agent 如何补全开发过程

Agent 可以先提出目标流程：

```text
业务问题确认
→ 最小闭环 / Contract
→ 数据与权限确认
→ 单模块实现
→ 集成测试与 Eval
→ 内部试用
→ Bad Case / Feedback
→ 迭代或收缩范围
→ 发布与运行监控
```

然后必须问用户：实际过程是否如此、哪一步不存在、哪一步由谁完成、哪些只是现在希望建立的流程。最终分为：

```text
Observed Development Process：实际发生过的流程
Target Delivery Process：建议建立的流程
Process Gap：两者之间的差距
```

## 推荐的回应格式

### 红队对用户显示

```text
红队问题：团队只有 X 人，为什么设计这么多模块？当前是几个可部署服务？
```

### 用户/蓝队回答后，Agent 内部整理

```text
Claim：当前有 N 个模块
证据状态：FACT_USER / FACT_REPO / UNKNOWN
红灯：逻辑模块、物理服务和未来目标可能混淆
下一问：删掉一半模块后，最小可交付链路是什么？
```

### 复盘输出

```text
已确认事实：
Agent Proposal：
仍需用户确认：
正式文档回写目标：
Red Retest 问法：
```

## 交互原则

- 模拟面试时只显示问题，不显示 `red_risk` 和预设答案；
- 设计评审时可以显示攻击理由，但仍不把 Proposal 当事实；
- 用户说“不知道”时，Agent 进入补充问题或 Proposal 模式，不替用户编造；
- 架构问题和项目叙事问题分开记录，避免把“说不清”误判成“架构错误”。
