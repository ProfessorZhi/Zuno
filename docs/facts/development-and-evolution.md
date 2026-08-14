# 开发演进史

status: current-fact
canonical_question: 用户加入后，项目如何从已有产品走向 Demo、反馈、测试和 Pilot？
owner: Project Facts Owner
source_boundary: 用户回忆和项目史锚点；不是 Git Commit Log

> 本文恢复的是工程演进故事，不是 Git Commit Log。已确认事实、用户部分回忆和候选顺序必须分开；没有 Artifact 支持时不创造精确日期。

## 1. 加入之前：项目已经存在

用户加入时，项目已经有代码和一个比较简易的自研前端，因此不是从零搭建产品。项目的最早立项时间、历史正式产品名、第一条需求和第一条提交目前都没有恢复。当前 GitHub 仓库也不能替代完整历史项目档案。

## 2. 约 2026 年 3 月：加入并进入 Agent 方向

用户大约在 2026 年 3 月由一名承担主要技术负责人角色的学硕学长带入项目，身份是研究生工程参与者。加入后参与 Agent 开发，Memory 是第一批重要工作之一；同时在开发过程中学习 LangGraph 和 GraphRAG。

这里的“学习”与“实现”必须分开：用户确认学习过 LangGraph / GraphRAG，但这不能推出历史产品完整采用了 LangGraph Runtime，也不能推出 GraphRAG 已经是正式生产主链路。

## 3. Agent、Memory 和工具调用的阶段性工作

用户参与了 OpenViking 在 Memory / Context 区域的接入，也参与了 Tool Calling Strategy。可以确认这些是用户实际参与过的方向，但还不能恢复出精确的 Adapter、接口、表结构、调用链或第一次提交。

比较可靠的阶段性叙事是：项目在已有 Agent 产品基础上继续处理上下文组织和工具调用问题，用户在其中承担了部分工程开发和联调工作。至于某一次回答质量问题是否直接导致 OpenViking 接入，或某个具体改动是否带来指标提升，目前都没有证据，继续保持 `UNKNOWN`。

## 4. Demo、反馈和进一步迭代

项目做过内部 Demo，也做过面向智慧法院项目组 / 客户侧的 Demo。用户确认客户明确反馈过“回答质量还需要提高”。在此之后团队继续开发和优化，随后有法院侧真实人员参与测试，并进入 Pilot Validation。

目前只能恢复这条阶段性关系：

```text
已有代码与前端
  → 用户加入并参与 Agent / Memory
  → OpenViking Memory / Context 接入与 Tool Calling Strategy（具体顺序 UNKNOWN）
  → 内部 Demo / 客户 Demo（具体顺序 UNKNOWN）
  → 客户反馈回答质量仍需提升
  → 团队继续迭代
  → 法院侧人员测试
  → Pilot Validation
```

早期 Demo 是否展示检索过程只有 `USER_PARTIAL_RECALL`：用户隐约记得可能展示过检索，但页面、Trace、Citation 和呈现方式没有可靠恢复。

## 5. 目前不能恢复的开发细节

以下内容继续保持 `UNKNOWN`：

- 第一条具体任务、第一次提交和第一次 Review；
- 本地启动方式、联调 Endpoint、发布和回滚方式；
- 用户实际改动的文件、API Contract 和测试用例；
- 客户回答质量问题的具体 Bad Case；
- 团队采取的具体 Cause → Fix → Metric；
- 法院侧测试的人员、题目、参考答案和评价协议；
- Pilot 的部署环境、用户规模、SLA、QPS、成本和正式验收结果。

## 6. 历史与 Target 的边界

当前仓库和新的 Target Architecture 可以帮助规划下一步重构，但不能反推历史项目已经是 Python-only 微服务、完整 Multi-Agent、Agentic GraphRAG 或 Domain-aware Runtime。历史技术矩阵见 [`technology-reality.md`](technology-reality.md)；新的产品问题与架构假设见 [`../architecture/architecture.md`](../architecture/architecture.md)。
