# 红队攻击分类

本文件是攻击工具箱，不是红队决策大脑。下一问的选择必须服从 `00-charter.md` 的 Claim、Risk、Remaining Risk 和 Transition；这里的 D/A 只提供可调用的攻击角度，不能驱动随机平铺题目。

红队沿两个正交维度组织问题：**问题域（D）**决定问哪一类内容；**攻击角度（A）**决定如何把一个陈述问深。

## 七个问题域

| 编号 | 问题域 |
|---|---|
| D1 | 基础原理与通用工程知识 |
| D2 | 项目现实、背景、用户和落地 |
| D3 | 架构设计、边界和技术取舍 |
| D4 | 实现细节、数据流和接口行为 |
| D5 | 工程质量、性能、成本、安全和运维 |
| D6 | 判断力、范围控制和复盘演进 |
| D7 | 沟通、协作、岗位匹配和个人贡献 |

## 十六个攻击角度

| 编号 | 角度 | 核心问题 |
|---|---|---|
| A01 | Business Need | 为什么值得做，谁会付出或受益？ |
| A02 | Project Origin | 项目从哪里来，是真需求还是事后包装？ |
| A03 | Landing Reality | 真的运行过吗，谁用，失败怎么办？ |
| A04 | Team Ownership | 谁决定、实现、评审、发布和背故障？ |
| A05 | Architecture Reasoning | 为什么这样拆，边界依据是什么？ |
| A06 | Build / Buy / Extend / Defer | 为什么不复用已有产品或开源方案？ |
| A07 | Implementation Depth | 关键路径具体怎样运行？ |
| A08 | Parameter Justification | 阈值、Top-K、超时、预算和版本为何这样定？ |
| A09 | Failure / Bad Case | 异常、脏数据、重复执行和部分成功怎么办？ |
| A10 | Scale / Performance / Cost | 规模上升后瓶颈、成本和隔离怎样变化？ |
| A11 | Security / Multi-tenancy | 权限、隐私、租户和外部副作用如何保护？ |
| A12 | Evaluation / Evidence | 凭什么说有效，指标如何采集和复现？ |
| A13 | Current / Target | 哪些已实现，哪些只是设计或未来？ |
| A14 | Over-engineering | 小团队和小规模是否真的需要这套复杂度？ |
| A15 | Evolution / Retrospective | 如果重来一次，什么会采用、延期或删除？ |
| A16 | Project–Architecture Alignment | 真实背景、用户、领域对象、技术复杂度和简历 Claim 是否属于同一条因果链？ |
| A17 | Development Process | 需求、设计、评审、实现、测试、发布和回滚是否真实经历过？ |
| A18 | Retrospective | 今天重做会保留、采用、延期或删除什么？是否理解长期代价？ |

## 攻击优先级

红队不平均覆盖所有角度。每轮按下列顺序挑最危险的 Claim：

```text
P0：真实性 / Ownership / Current-Target 冲突 / 安全越权
P1：业务价值 / Project-Architecture Alignment / Build-vs-Buy / 核心实现 / Failure
P2：参数依据 / 成本 / Eval / 演进 / 非核心基础
```

如果一个 P0 Claim 被击穿，不要为了“覆盖更多题目”立即换题；先把同一 Claim 的来源、Owner、边界和证据问清。

## 典型 Claim 的攻击链

| Claim | 优先追问 |
|---|---|
| “企业 Agent 平台” | A01/A02/A03/A13：谁的企业问题，真实用户、落地证据和 Current 是什么？ |
| “法院/司法项目” | A02/A03/A16：合作关系是什么，实际用户是谁，为什么领域模型和旗舰场景匹配？ |
| “逻辑专题与服务数量” | A05/A14/A16：逻辑能力如何落到少量服务，谁维护，哪些先不做？ |
| “自研 Memory” | A06/A07/A09：为什么不采用现有方案，写入、冲突、失效和回滚如何做？ |
| “GraphRAG” | A05/A08/A12：Graph 补足了什么，何时不用，如何证明提升？ |
| “效果提升” | A08/A12：基线、数据集、指标、置信区间和反例是什么？ |
| “已经落地” | A03/A13：当前运行证据、用户反馈、运维责任和边界是什么？ |
| “微服务架构” | A05/A10/A14：拆分解决了什么，通信和运维成本是否值得？ |
| “比 WorkBuddy / Dify 更适合” | A01/A06/A12/A16：不可替代 Delta 是什么，是否可以只做 Extension，证据在哪里？ |
| “我主要负责 Agent / Memory / RAG” | A04/A07/A13：本人具体链路、代码、决策和未负责范围分别是什么？ |
| “项目从一开始就是现在这样” | A02/A17：第一版是什么，为什么演进，谁评审和推动了变化？ |
| “现在这样设计没有问题” | A14/A15/A18：删掉一半会删什么，今天重做还会这样选吗？ |

## A16：Project–Architecture Alignment 固定攻击

出现下面任一情况必须触发 A16：

- 项目背景说的是法院/司法，但领域对象和旗舰故事只剩企业合同；
- 用户规模较小，却直接宣称大规模分布式或微服务是必要条件；
- 团队只有少数人，却声称同时建设大量生产级平台能力；
- 简历写“已实现”，仓库只有 Target 文档；
- 竞品已经覆盖通用 Agent Runtime，但差异化仍只说“我们也有 Memory / RAG / Tool”。

固定追问顺序：

```text
真实背景是什么？
→ 这个背景对应哪个用户任务？
→ 该任务要求哪些领域事实和不可接受风险？
→ 当前领域对象是否真的表达这些事实？
→ 当前架构复杂度是否由规模/风险/团队约束推出？
→ 哪些能力其实可以被通用平台替换？
→ 剩下的 Zuno Delta 是否足够支撑项目存在？
→ Current 和 Resume 是否只声称已经证明的部分？
```

如果这条链断裂，优先记录 `PROJECT_ARCHITECTURE_ALIGNMENT_GAP`，而不是先扩写话术。

## 项目相关与项目无关的切换

一场真实面试可以从项目突然切到基础题，再从基础题回到项目机制。红队要记录切换原因：

```text
项目 Claim 暴露基础原理风险
  → PROJECT_INDEPENDENT 基础追问
  → FUNDAMENTAL_GAP（不改写 Zuno 架构）

岗位要求基础能力
  → PROJECT_INDEPENDENT 独立题
  → 结束后再回到项目 Claim

项目回答出现具体机制
  → PROJECT_DEPENDENT 实现 / 参数 / Failure 追问
```

基础题的考点、项目题的事实和个人 Ownership 必须分开记录。

## 连续追问骨架

```text
Claim
  → Context
  → Ownership
  → Necessity
  → Alternative
  → Mechanism
  → Detail
  → Failure
  → Evidence
  → Boundary
  → Retrospective
```

不是每道题机械走完所有层。回答在哪一层出现断点，就沿该层继续下钻；只有证据已经稳定或事实明确 UNKNOWN 时才结束该链。

## 反题库原则

红队不是从题库随机抽题，而是根据最新回答生成下一问。`docs/verification/interview-qa/` 提供架构机制的已维护攻击素材，`ProfessorZhi/internship-work` 的面试红队研究提供真实面试行为模式；两者都不能替代当前 Claim 和当前证据。
