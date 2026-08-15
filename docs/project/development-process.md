<!--
status: canonical-development-process
canonical_question: 项目如何在既定法律智能 Agent 平台方向下发展、交付并接受法院侧验证？
owner: Project Documentation Owner
source_boundary: 用户回忆、项目阶段事实和当前仓库证据；不是 Git Commit Log，也不把当前代码反写成历史个人贡献
-->

# Zuno 开发过程

## 1. 我加入时项目已经有什么

项目在用户加入前已经存在代码和一个比较简单的自研前端，因此不是 Greenfield 项目。用户约在 2026 年 3 月加入，由一名学硕学长带入；当时项目已经处在继续开发和产品迭代阶段，而不是从零开始立项。

历史最早的提交、第一版产品名称、第一条需求和当时完整技术栈尚未恢复。当前 GitHub 仓库只能说明今天的实现，不能替代历史项目档案，也不能自动说明某段当前代码是谁在历史项目中编写的。

## 2. 在已有产品上继续开发

在已有产品基础上，团队继续围绕 Agent、Memory / Context、Tool Calling，以及法律智能能力和 Knowledge / Retrieval 做开发与联调。用户实际参与的方向单独记录在[团队与开发分工](./team-and-contributions.md)，这里不重复扩展个人职责。

项目整体还涉及后端、前端、测试和部署等工作方向，但正式人员分工、人数、Title、Owner、会议方式、分支策略、Code Review、Issue / Task 管理和部署流程都没有可靠历史记录。因此，不能把常见的 Scrum、双周 Sprint、PR Review 或 CI/CD 自动写成当时的开发方法。

## 3. Internal Demo

Internal Demo 是目前能够恢复的第一个重要阶段。它说明已有产品和相关能力曾经被项目组用于内部演示和迭代验证，但具体日期、参与者、环境、演示材料和每项能力的完成程度还没有恢复。

## 4. 客户侧 Demo 与反馈

之后项目进行过客户侧或智慧法院项目组 Demo。已经能够确认的反馈是“回答质量还需要提高”。目前没有足够资料判断当时具体问题来自 Prompt、检索、模型、Memory、Tool、引用、数据处理还是其他环节，因此开发历史只保留反馈本身，不替它补写根因或修复故事。

## 5. 后续迭代与法院侧测试

在客户反馈之后，项目继续迭代，随后进入法院侧人员测试。这个阶段说明产品曾经被放到真实业务侧进行验证，但测试题数量、参与法院、参与人员职位、参考答案、Reviewer、评价协议、运行环境和性能数据都没有恢复。

## 6. Pilot Validation

项目后来进入 Pilot Validation。这里的 Pilot 是阶段性验证，不等于正式 Production；目前也没有资料支持用户规模、运行时长、部署 Endpoint、正式验收、SLA、QPS、Latency、Token、Cost、HA 或 DR。

## 7. 一条目前能够恢复的开发主线

```text
已有产品
  → Agent / Memory / Tool 等方向继续开发
  → Internal Demo
  → Customer / Smart Court Project Demo
  → 回答质量反馈
  → 继续迭代
  → Court-side Testing
  → Pilot Validation
```

这条主线是目前可恢复的项目阶段故事，不是逐提交的 Git 时间线，也不代表每个目标能力在每个阶段都已经完整实现。更细的 Git Timeline、PR、Sprint、Task Ownership、Bug、测试题和性能数据，需要以后从历史材料或用户回忆中逐项补充。

## 8. 历史技术信息与当前仓库

目前可以确认用户参与过 Agent development、OpenViking、Tool Calling Strategy 和数据库访问；LangGraph、GraphRAG 属于开发期间学习和接触过的方向。历史技术栈尚未逐项确认：Python、FastAPI、PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、Elasticsearch、MCP、Pytest、Docker、历史 LLM、Embedding Model 和 Reranker 是否在历史项目中使用，都需要单独证据。

当前 main 可以证明仓库中存在 Python 后端、Web/API、Agent、Knowledge / Retrieval、Memory、Capability / Tool、数据库和测试入口。这些是当前工程事实；目录、类名、依赖、Mock Test 或 Target 文档都不能反推出历史项目在哪个版本由谁使用过这些组件，也不能证明它们曾经运行在 Pilot 或 Production 环境。具体当前实现请阅读[Evidence](../evidence/README.md)。
