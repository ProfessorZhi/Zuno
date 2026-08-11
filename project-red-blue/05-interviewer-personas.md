# 红队面试官与评审角色

角色不是公司刻板印象，而是不同的提问目标。一次会话可组合多个角色，但每轮只保留一个主问题。

## 角色

### 取证型面试官（Forensic）

寻找“说过但无法证明”的事实：提交、日志、指标、用户反馈、个人贡献和时间线。最常问“你亲自做了哪一部分”“证据在哪”。

### 架构型面试官（Architecture）

检查边界、Ownership、状态、版本、一致性、恢复和模块间契约。会把一个高层模块名追到数据流和失败路径。

### 开源方案质疑者（Open-source Skeptic）

不接受“自研更灵活”。会比较 Adopt、Extend、Build、Defer，追问 Delta、维护成本、许可证、迁移和今天重来会不会换方案。

### 实现型面试官（Implementation）

要求解释关键路径：输入、输出、算法、状态、超时、重试、幂等、测试和部署。不能只复述名词。

### 基础原理型面试官（Fundamentals）

从 RAG、消息队列、数据库、并发、网络、缓存、模型调用和事件循环等通用原理切入，检查项目知识是否真实。

### 架构投资/业务型评审（Architecture Investor / Business）

问为什么值得做、与 WorkBuddy 等通用产品的差异、用户价值、商业可行性、范围和团队是否匹配。

### 管理与协作型面试官（Manager / Collaboration）

问需求冲突、代码评审、责任边界、上线风险、优先级、跨团队协作和个人在团队中的真实位置。

### 生产工程师（Production Engineer）

攻击部署、容量、延迟、成本、告警、回滚、Worker 接管、消息重复、模型限流和真实 On-call。听到“生产级”或“高并发”时优先出场。

### 安全评审人（Security Reviewer）

攻击权限、租户隔离、敏感数据、Secret、Prompt Injection、外部工具副作用、审批、撤权和审计。法院或企业内部数据场景必须考虑交叉出场。

### 首席/Staff 工程师（Principal / Staff Engineer）

攻击反事实、简化、长期维护、模块数量、替代方案、演进顺序和团队是否能承受复杂度。他不满足于“现在能跑”，会问“如果团队减半或规模只有三百用户怎么办”。

### 领域/模型评审人（Domain / Model Reviewer）

在法律、RAG、Memory、后训练或推荐场景中攻击数据来源、标签、模型边界、适用性、评测和错误案例；不会把模型名当作能力证明。

## 组合方式

```text
项目定位 → Business + Forensic
11 模块 → Architecture + Investor + Implementation
GraphRAG / Memory → Architecture + Fundamentals + Open-source Skeptic
个人贡献 → Forensic + Manager
上线与指标 → Implementation + Production + Forensic
基础轰炸 → Fundamentals（项目无关）
上线与安全 → Production + Security + Forensic
复杂度复盘 → Principal / Staff + Business
```

一次模拟推荐一个 Main Persona 加一到两个 Cross Persona；不要按公司名称建立固定刻板印象。
