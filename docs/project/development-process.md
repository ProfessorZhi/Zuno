<!--
status: canonical-development-process
canonical_question: 项目如何在既定法律智能 Agent 平台方向下发展、交付并接受法院侧验证？
owner: Project Documentation Owner
source_boundary: 用户回忆、项目阶段事实和当前仓库证据；不是 Git Commit Log，也不把当前代码反写成历史个人贡献
-->

# Zuno 开发过程

## 1. 我加入时项目已经有什么

项目在用户加入前已经存在代码和一个比较简单的自研前端，因此不是 Greenfield 项目。用户约在 2026 年 3 月加入，由一名学硕学长带入；当时项目已经处在继续开发和产品迭代阶段，而不是从零开始立项。

这一点对理解后续贡献很重要。用户面对的是一个已经有历史、已有产品形态、同时还在快速变化的工程系统，因此很多工作天然属于“在现有边界上继续接入、调试和迭代”，而不是从第一天就拥有全部架构和代码。面试里如果被问“你是不是从零搭的”，准确答案应该先说明这个起点，再讲自己实际接手了哪些方向。

历史最早的提交、第一版产品名称、第一条需求和当时完整技术栈尚未恢复。当前 GitHub 仓库只能说明今天的实现，不能替代历史项目档案，也不能自动说明某段当前代码是谁在历史项目中编写的。

## 2. 在已有产品上继续开发

在已有产品基础上，团队继续围绕 Agent、Memory / Context、Tool Calling，以及法律智能能力和 Knowledge / Retrieval 做开发与联调。用户实际参与的方向单独记录在[团队与开发分工](./team-and-contributions.md)，这里不重复扩展个人职责。

从产品演进角度，这类工作不是几个互不相关的技术实验。Agent 需要能够使用知识和专业能力，Memory / Context 影响跨轮次或跨步骤输入，Tool Calling 把模型建议连接到外部能力；任何一个环节发生变化，都可能改变回答质量、恢复路径或安全边界。今天的九模块 Target Architecture 正是在后续架构整理中把这些过去容易纠缠的问题重新按事实 Owner 拆开；这不能反过来证明历史团队当时已经用同一套九模块方式组织开发。

项目整体还涉及后端、前端、测试和部署等工作方向，但正式人员分工、人数、Title、Owner、会议方式、分支策略、Code Review、Issue / Task 管理和部署流程都没有可靠历史记录。因此，不能把常见的 Scrum、双周 Sprint、PR Review 或 CI/CD 自动写成当时的开发方法。

## 3. Internal Demo

Internal Demo 是目前能够恢复的第一个重要阶段。它说明已有产品和相关能力曾经被项目组用于内部演示和迭代验证，但具体日期、参与者、环境、演示材料和每项能力的完成程度还没有恢复。

内部 Demo 的价值可以理解为“先把一条产品链路跑起来并暴露问题”，而不能被写成正式质量验收。今天如果要进一步恢复这一阶段，最有价值的材料是当时的截图、演示脚本、输入样例、环境配置和内部反馈，而不是用当前代码重新运行一遍再假设结果与历史相同。

## 4. 客户侧 Demo 与反馈

之后项目进行过客户侧或智慧法院项目组 Demo。已经能够确认的反馈是“回答质量还需要提高”。目前没有足够资料判断当时具体问题来自 Prompt、检索、模型、Memory、Tool、引用、数据处理还是其他环节，因此开发历史只保留反馈本身，不替它补写根因或修复故事。

从工程复盘角度，这恰好是目前最值得继续恢复的一段。如果未来找到当时 Bad Case、排查记录或版本提交，理想的记录方式应是：客户看到了什么问题 → 团队怎样复现 → 根因属于哪一层 → 为什么选择某个修复 → 修复后用什么题或指标验证。只有形成这条 Cause → Decision → Implementation → Metric 链，才能把“做过优化”升级成经得起技术面试继续追问的工程案例。

在这些材料恢复以前，不能为了让故事完整而写“我们后来通过 GraphRAG / Prompt 优化 / Memory 把准确率提升了多少”。这些都可能是合理方法，但合理不等于历史事实。

## 5. 后续迭代与法院侧测试

在客户反馈之后，项目继续迭代，随后进入法院侧人员测试。这个阶段说明产品曾经被放到真实业务侧进行验证，但测试题数量、参与法院、参与人员职位、参考答案、Reviewer、评价协议、运行环境和性能数据都没有恢复。

“法院侧人员测试”比内部 Demo 更接近真实使用，但仍然不自动等于 Production。真实人员参与能够暴露材料表达、专业术语、引用习惯、权限和工作流程上的问题；要把它变成可比较的产品证据，还需要知道使用了什么任务集合、怎样判断回答可接受、失败案例如何记录，以及不同版本之间是否使用了同一评价口径。

因此当前文档只保留阶段事实，不给它附加一个不存在的准确率或满意度数字。

## 6. Pilot Validation

项目后来进入 Pilot Validation。这里的 Pilot 是阶段性验证，不等于正式 Production；目前也没有资料支持用户规模、运行时长、部署 Endpoint、正式验收、SLA、QPS、Latency、Token、Cost、HA 或 DR。

Pilot 最值得确认的也不只是“有没有部署过”，而是部署在哪里、谁实际使用、使用多久、处理什么材料、遇到过什么故障、怎样回滚、数据是否允许外发、有没有人工兜底和最终验收标准。今天的 Target Architecture 已经把这些问题分别放到 Security、Tool Effect、Observability、Domain 和 Operations 等责任边界，但历史 Pilot 是否真的具备对应机制仍然是事实问题。

这也是为什么当前项目可以说“走到过 Pilot Validation”，却不能说“已经生产化”。两个词对应的证据门完全不同。

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

### 为什么阶段故事和 Git 历史不能互相替代

Git 能很好地回答“某个仓库什么时候改过什么文件”，但未必能直接告诉我们一次客户 Demo 使用的是哪个部署环境、某个分支有没有真正交付，或者一次法院测试使用的是不是 main。反过来，用户记得“进入过 Pilot”也不能证明今天 Git 仓库里的某个类当时已经存在。

因此开发过程保留业务阶段，Current Evidence 保留今天可复现的代码与测试；如果以后取得历史 Commit、部署包、Demo 记录，再把两条时间线按证据关联起来。这样比强行把 Git Log 写成产品史更可靠。

## 8. 历史技术信息与当前仓库

目前可以确认用户参与过 Agent development、OpenViking、Tool Calling Strategy 和数据库访问；LangGraph、GraphRAG 属于开发期间学习和接触过的方向。历史技术栈尚未逐项确认：Python、FastAPI、PostgreSQL、Redis、RabbitMQ、MinIO、Milvus、Neo4j、Elasticsearch、MCP、Pytest、Docker、历史 LLM、Embedding Model 和 Reranker 是否在历史项目中使用，都需要单独证据。

当前 main 可以证明仓库中存在 Python 后端、Web/API、Agent、Knowledge / Retrieval、Memory、Capability / Tool、数据库和测试入口。这些是当前工程事实；目录、类名、依赖、Mock Test 或 Target 文档都不能反推出历史项目在哪个版本由谁使用过这些组件，也不能证明它们曾经运行在 Pilot 或 Production 环境。具体当前实现请阅读[Evidence](../evidence/README.md)。

## 9. 下一步最值得恢复的开发证据

如果目标是让整个项目能够经得起高级面试官连续追问，下一步最有价值的不是继续给阶段名称加形容词，而是恢复少量高质量的工程闭环。

第一类是质量闭环：找到一到两个真实 Bad Case，恢复输入、错误表现、根因、修改、回归测试和指标。第二类是个人任务闭环：从某一次 Agent、Memory、OpenViking 或 Tool Calling 工作里恢复需求、关键代码路径、接口、异常、测试和最终结果。第三类是 Pilot 闭环：确认环境、参与人、任务量、运行时长、评价方法和实际问题。

这些材料会分别回到 Project、Team / Contributions 和 Evidence。没有恢复之前继续保持 Unknown，比构造一个看起来完整但无法验证的开发故事更可靠。
