# Zuno 架构文档

`docs/architecture/` 只负责一件事：说明 Zuno 理想状态下应该怎样设计。

这套总体架构不从九个模块开始，也不从 LangGraph、RAG 或数据库开始。它围绕一条更稳定的主线展开：**一个法律任务会同时产生材料与知识事实、机器候选、正式法律事实、运行控制事实和现实副作用；每一种事实都需要自己的权威来源，跨越边界时要留下可用于恢复和审计的因果凭据。** 九个责任域是这些约束长期稳定以后形成的 Ownership 结果。

这里不证明今天已经实现了什么，也不展开数据库字段、ORM、API 枚举和逐模块状态机。总体架构先把业务约束、事实权威、跨边界转换、故障恢复、安全和演进关系讲清楚；实施时再进入模块文档、ADR 和 Evidence。

## 文档结构

`docs/architecture/` 只保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

- [`architecture.md`](architecture.md)：Zuno 唯一的总体 Target Architecture 正文。用一项持续演进的法律任务解释事实、边界、Owner 和恢复。
- [`architecture-views.md`](architecture-views.md)：与正文配套的 Mermaid 图源。图帮助理解，不维护第二套架构事实。
- [`architecture.html`](architecture.html)：图形阅读入口，直接加载同一份 Mermaid 图源。
- `README.md`：说明文档边界和阅读顺序。

总体架构之外的精度分别放在其他知识面：

- [`../project/project.md`](../project/project.md)：项目为什么存在、历史背景和业务约束。
- [`../modules/`](../modules/README.md)：九个责任域内部的 Contract、State、Failure、Recovery 和实施设计。
- [`../decisions/`](../decisions/README.md)：已经接受的重要架构决策及其理由。
- [`../research/`](../research/README.md)：论文、框架和外部研究如何影响设计方向。
- [`../evidence/`](../evidence/README.md)：代码、测试、Eval、性能和生产资格等 Current 证据。

## 总体架构在设计阶段回答什么

总体架构关注的是一项法律工作怎样在时间中保持可信。

一份新材料进入以后，系统要知道它是哪一版；OCR、索引和图结构完成以后，还要判断当前任务是否真的拥有足够材料。检索和模型产生的内容先是候选，只有经过领域规则和必要的人审以后才成为正式业务事实。任务崩溃时，Runtime Checkpoint 不能推翻已经提交的 Domain fact；外部请求超时时，系统也不能把“没有收到响应”直接解释成“现实动作没有发生”。

这些关系确定以后，FastAPI、LangGraph、PostgreSQL、模型 Provider、向量数据库和消息队列才成为实现选择。

## 九个责任域

Target Architecture 使用九个逻辑责任域：

1. Application & Integration
2. Legal Domain & Work Product
3. Knowledge & Evidence
4. Agent Runtime & Control
5. Capability & Skill
6. Tool Runtime & Effects
7. Model Gateway
8. Security & Governance
9. Observability & Evaluation

它们是一张事实 Ownership 地图，不是九个微服务。默认物理形态可以是模块化 Python 后端和若干独立 Worker；只有吞吐、安全隔离、故障半径、网络出口或部署生命周期形成真实需求时，才把某个逻辑边界升级成独立网络服务。

Platform / Infrastructure 作为底层责任层提供数据库、对象存储、Queue、Checkpointer、CAS、Lease、Clock、Backup/Restore、Network 和 Secret Delivery 等技术原语，不拥有 Domain、Runtime、Knowledge 或 Effect 的业务成功。

## 推荐阅读顺序

理解 Zuno 时，先从项目问题进入，再沿着事实权威和故障恢复读总体架构：

```text
../project/project.md
→ architecture.md
→ architecture-views.md
→ ../modules/README.md
→ 目标模块文档
```

开始实施某一部分时：

```text
目标模块
→ 相关 ADR
→ 数据模型 / API / Migration / Worker 设计
→ 测试与故障注入
→ docs/evidence/
```

Research 用来提出和校准方案，Evidence 用来决定方案是否真的成立。论文、框架或设计文档本身都不能证明 Zuno 已经具备对应能力。

## 维护原则

总体架构只在跨模块语义发生变化时修改，例如：

- 某类正式事实更换 Owner；
- 完成证明发生变化；
- Runtime 与 Domain 的恢复顺序改变；
- 外部 Effect 的 Unknown / Reconcile 语义改变；
- Security Authority 改变；
- 九模块责任划分发生变化。

Provider、SDK、ORM 字段、Queue、Cache、索引实现和部署参数变化，如果没有改变上述语义，就属于模块或实现层调整。

目标是让 `architecture.md` 始终像一篇能够连续阅读的系统设计文档：读者先理解一个事实为什么可信，再理解哪个模块负责它；而不是从模块名称倒推系统的问题。
