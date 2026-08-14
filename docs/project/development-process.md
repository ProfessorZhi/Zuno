# Zuno 开发过程

status: canonical-development-process
canonical_question: 项目如何从已有产品发展到 Agent、Memory/Context、工具调用、演示、法院测试和 Pilot？
owner: Project Documentation Owner
source_boundary: 用户回忆、项目阶段事实和当前仓库证据；不是 Git Commit Log，也不把当前代码反写成历史个人贡献

本文讲“项目怎样发展”和“用户实际参与到什么程度”。精确日期、提交、文件、Bug 和指标没有证据时保留 UNKNOWN。当前仓库事实与历史项目事实分开描述。

## 项目开始时已经存在

用户加入时，项目已经有代码和一个比较简易的自研前端，不是从零立项开发。历史最早的提交、第一版产品名称、第一条需求和当时完整技术栈尚未恢复；当前 GitHub 仓库只能证明今天的实现，不能替代历史项目档案。

用户确认，核心研发规模约 7–8 人；一名学硕学长承担主要技术负责人角色并把用户带入项目。这里不把该学长写成 CTO、总架构师或合同负责人，也不把用户写成整个项目负责人、总架构负责人或 Production Owner。

## 用户加入与实际参与方向

用户约在 2026 年 3 月加入，身份是研究生工程参与者。用户确认参与过以下方向：

- 部分 Agent 开发；
- Memory 相关的第一批重要工作；
- OpenViking 在 Memory / Context 区域的接入；
- Tool Calling Strategy 相关开发；
- 进入数据库查看或调试数据。

用户在开发期间学习或接触过 LangGraph 和 GraphRAG，但 `LEARNED_ONLY` 不等于 `PRODUCT_IMPLEMENTED`，更不等于用户实现了完整 Runtime、全部 GraphRAG、全部 RAG、全部 Backend、数据库、法律算法、前端、部署或整体架构。

目前能够诚实说明的是“参与过哪些方向”，还不能恢复任务级 Ownership：第一项任务、输入输出、修改过的逻辑、真实 Tool、OpenViking 的 SDK/API/Adapter 形态、Memory 写入/召回时机、具体 SQL、Bug、定位、修复和验证方式都为 UNKNOWN。当前代码中能找到的实现也不能自动证明是用户当时写的。

## 工程工作如何展开

在已有产品基础上，项目继续围绕 Agent、Context/Memory 和 Tool Calling 做开发与联调；团队还涉及法律智能能力、Knowledge / Retrieval、后端、前端、测试和部署等方向，但每个方向的正式人数、姓名、Title、Owner 和协作流程没有可靠记录。

一个与已确认经历相容的阶段叙事是：先在已有 Agent 产品上继续补充上下文组织和工具调用，再把团队已有的检索或法律智能能力接入更完整的任务流程，经过内部 Demo 和客户侧 Demo 获取反馈，随后继续迭代并接受法院侧人员测试，最后进入 Pilot Validation。这个顺序是当前可恢复的项目阶段故事，不是逐提交的 Git 时间线。

分支策略、Code Review、周会、Issue / Task 管理、接口协作、测试协议和部署流程仍然 UNKNOWN。不得把常见的 GitHub PR、双周 Sprint 或标准 Scrum 当作历史事实。

## 演示、反馈与测试

已确认的交付链是：

```text
已有代码和产品
  → Internal Demo
  → Customer / Smart Court Project Demo
  → 客户反馈：回答质量需要提高
  → Further Iteration
  → Court-side Testing
  → Pilot Validation
  → Production：NO
```

这个链条是项目开发过程中的事实锚点。客户反馈目前只能记录为 `INC-HIST-001`：

| 字段 | 当前状态 |
| --- | --- |
| Symptom | 回答质量需要提高 |
| Root Cause | UNKNOWN |
| Investigation | UNKNOWN |
| Change | UNKNOWN |
| Result / Metric | UNKNOWN |

不得自行把根因归为 Prompt、RAG、Memory、Model、Tool 或 Context，也不能把当前架构建议写成当时已经完成的修复。Demo 时间、地点、操作者、法院、测试题、参考答案、Reviewer、Pilot 用户数、环境、时长、验收、SLA、QPS、Latency、Token、Cost、HA 和 DR 均未恢复。

## 当前仓库能证明什么

当前 main 可以单独证明仓库中存在相应的 Python 后端、Web/API、Agent、Knowledge/Retrieval、Memory、Capability/Tool、数据库和测试入口；`docs/evidence/` 负责记录可复现的当前代码、测试、运行与评测证据。目录、类名、依赖声明、Mock Test 或 Target 文档都不能证明这些组件在历史项目的哪个版本中由谁使用，也不能证明它们曾经在 Pilot 或 Production 中运行。

历史技术矩阵应保持保守：Agent development、OpenViking、Tool Calling Strategy 和数据库访问属于用户确认的参与方向；LangGraph、GraphRAG 属于学习/接触事实；Python、FastAPI、PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、Elasticsearch、MCP、Pytest、Docker、历史 LLM、Embedding 和 Reranker 等是否在历史项目中使用，逐项 UNKNOWN，除非有新的用户回忆或历史证据。

## 开发过程的事实边界

项目故事可以说明“已有研究与工程背景 → 已有产品 → Agent/Memory/Tool 方向开发 → Demo → 质量反馈 → 法院测试 → Pilot”，但不能把缺失的过程细节补成完整 SOP。后续用户确认应直接更新本文和[项目背景](./project-background.md)，不再恢复一个平行的 Fact Ledger。

总体架构只回答跨层 Target 为什么这样设计；模块目录目前只保留边界占位；Evidence 只记录当前可复现证据。三者都不能替代本文件中的历史事实。
