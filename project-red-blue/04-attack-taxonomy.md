# 红队攻击分类

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

## 十五个攻击角度

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

## 典型 Claim 的攻击链

| Claim | 优先追问 |
|---|---|
| “企业 Agent 平台” | A01/A02/A03：谁的企业问题，真实用户和落地证据是什么？ |
| “11 个模块” | A05/A14：逻辑模块如何落到少量服务，谁维护，哪些先不做？ |
| “自研 Memory” | A06/A07/A09：为什么不采用现有方案，写入、冲突、失效和回滚如何做？ |
| “GraphRAG” | A05/A08/A12：Graph 补足了什么，何时不用，如何证明提升？ |
| “效果提升” | A08/A12：基线、数据集、指标、置信区间和反例是什么？ |
| “已经落地” | A03/A13：当前运行证据、用户反馈、运维责任和边界是什么？ |
| “微服务架构” | A05/A10/A14：拆分解决了什么，通信和运维成本是否值得？ |

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
