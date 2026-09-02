# Zuno 架构文档

`docs/architecture/` 只负责一件事：说明 Zuno 理想状态下应该怎样设计。

这里不证明今天已经实现了什么，也不展开数据库字段、ORM、API 枚举和逐模块状态机。总体架构先把业务约束、责任边界、正常流程、故障恢复、安全和演进关系讲清楚；实施时再进入模块文档、ADR 和 Evidence。

## 文档结构

`docs/architecture/` 只保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

- [`architecture.md`](architecture.md)：Zuno 唯一的总体 Target Architecture 正文。只讲概念设计和整体关系。
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

总体架构不从技术栈开始。它先回答几个长期问题：

一项法律任务依赖哪一版材料；知识索引与正式法律事实怎样分开；机器候选怎样进入人工和领域判断；长任务崩溃以后从什么事实恢复；外部请求超时以后怎样确认现实动作；权限变化以后哪些未来动作仍然允许；研究算法和模型怎样在不改变业务语义的前提下替换。

这些问题确定以后，FastAPI、LangGraph、PostgreSQL、模型 Provider、向量数据库和消息队列才成为实现选择。

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

第一次理解 Zuno：

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

目标是让 `architecture.md` 始终像一篇能够连续阅读的系统设计文档，而不是随着实现细节增长成第二份代码规格。
