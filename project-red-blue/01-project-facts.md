# PROJECT-FACTS-RECONSTRUCTION-V2

本文件是 Project Facts 的红蓝工作材料。它维护候选、攻击、未知和下一轮回忆问题；正式事实以 [`docs/project/facts/`](../docs/project/facts/README.md) 为准。

## 一、证据标签

| 标签 | 含义 |
|---|---|
| `[USER_CONFIRMED]` | 用户明确确认 |
| `[USER_PARTIAL_RECALL]` | 用户记得大致发生过，细节模糊 |
| `[PARTIAL_REPOSITORY_EVIDENCE]` | 当前/历史 Git、代码、配置、测试或 Migration 的部分支持 |
| `[ARTIFACT_EVIDENCE]` | 简历、截图、PPT、聊天、任务或旧文档直接支持 |
| `[PUBLIC_CONTEXT]` | 学校、实验室、法院或公开项目外围资料 |
| `[RECONSTRUCTED_CANDIDATE]` | 多线索形成但尚未确认的历史候选 |
| `[UNKNOWN]` | 当前无法恢复 |
| `[TARGET_ONLY]` | 新架构目标，不是历史事实 |
| `[CONTRADICTED]` | 证据冲突或被直接事实否定 |

## 二、V2 User Gate：已确认事实

### 项目与客户

- `[USER_CONFIRMED]` 项目属于南京大学软件学院葛季栋 / LIPLAB 侧长期智慧司法相关研发背景。
- `[USER_CONFIRMED]` 合作侧日常称谓是“智慧法院项目组”。
- `[USER_CONFIRMED]` Zuno 是该项目体系中的一个产品，不是整个智慧法院项目。
- `[USER_CONFIRMED]` 历史正式产品名称不叫 Zuno。
- `[USER_PARTIAL_RECALL]` 正式名称偏企业化/项目化风格，但已遗忘。
- `[USER_CONFIRMED]` 项目涉及天津智慧法院体系，Zuno 覆盖 22 家法院体系中的部分法院。
- `[UNKNOWN]` 合同甲方、正式机构、正式项目名、具体法院名单和是否属于某个正式合同子项目。

### 时间、团队与加入过程

- `[USER_CONFIRMED]` 用户约在 2026 年 3 月加入，2026 年期间项目持续推进，是长期持续型研发。
- `[USER_CONFIRMED]` 核心研发约 7–8 人。
- `[USER_CONFIRMED]` 一名学硕学长承担主要技术负责人角色，并由其带用户进入项目。
- `[USER_CONFIRMED]` 用户加入时 clone 了已有项目代码，并已有简易自研前端页面。
- `[USER_CONFIRMED]` 用户加入后参与开发，同时学习 LangGraph / GraphRAG。

### 交付与个人参与

- `[USER_CONFIRMED]` 存在内部 Demo、客户侧 Demo、法院侧人员测试和 Pilot Validation。
- `[USER_CONFIRMED]` 尚未正式生产部署。
- `[USER_CONFIRMED]` 客户 Demo 后的重要反馈之一是回答质量需要进一步提高。
- `[USER_CONFIRMED]` 用户参与 Agent 开发，第一批重要任务之一是 Memory。
- `[USER_CONFIRMED]` 用户参与 OpenViking 在 Memory / Context 区域的接入。
- `[USER_CONFIRMED]` 用户参与 Tool Calling Strategy 相关开发。
- `[USER_CONFIRMED]` 用户亲自进入数据库查看或调试过数据，但具体数据库产品未知。

## 三、V2 历史技术矩阵裁判

| 技术/能力 | 当前裁判 | 不能推出的内容 |
|---|---|---|
| OpenViking | `[USER_CONFIRMED]`：Memory/Context 接入 | 不等于所有 Memory、法律事实存储或生产关键路径 |
| LangGraph | `[USER_CONFIRMED]`：学习/参与上下文 | 不等于完整 Runtime 或历史生产主链路 |
| GraphRAG | `[USER_CONFIRMED]`：学习 | 不等于 Experiment、Demo 或 Product Main Path 已确认 |
| Agent | `[USER_CONFIRMED]`：参与部分开发 | 不等于整个 Agent Runtime Owner |
| Tool Calling Strategy | `[USER_CONFIRMED]`：参与开发 | 具体工具选择、参数、失败、Retry、Approval 和 MCP 仍 UNKNOWN |
| 数据库 | `[USER_CONFIRMED]`：查看/调试过 | 不知道具体产品、表、SQL、客户端 |
| Python/FastAPI/PostgreSQL/RabbitMQ/MinIO/Milvus/Neo4j/Elasticsearch/Redis/MCP/Pytest/Compose | `[UNKNOWN]` + 当前仓库 `[PARTIAL_REPOSITORY_EVIDENCE]` | 当前代码/配置不能证明历史使用或用户本人负责 |
| Hybrid Retrieval/BM25/Vector/Reranker | `[UNKNOWN]` | 不从简历候选或 Target 推导历史主链路 |

当前仓库未发现 OpenViking 实现或依赖。这个事实不推翻用户确认的历史接入；它证明的是 Current GitHub 与完整历史项目不能等同。

## 四、开发时间线

```text
约 2026-03 加入
  ↓
clone 已有代码；已有简易前端；学习 LangGraph / GraphRAG
  ↓
参与 Memory / OpenViking 接入
  ↓
参与 Tool Calling Strategy
  ↓
内部 Demo / 客户 Demo（技术任务与 Demo 精确顺序 UNKNOWN）
  ↓
客户反馈：回答质量需要进一步提高
  ↓
继续开发/优化
  ↓
法院侧人员测试与 Pilot Validation（精确相对顺序 UNKNOWN）
  ↓
尚未正式生产部署
```

早期 Demo 是否展示检索过程是 `[USER_PARTIAL_RECALL]`；第一次任务、第一次提交、第一次联调 endpoint、本地启动命令、反馈根因和质量指标均为 `[UNKNOWN]`。

## 五、历史与 Target 隔离

以下只能标为 `[TARGET_ONLY]`：Python-only、Microservices、Legal Domain Kernel、Domain-aware Runtime、新 Multi-Agent 服务、新 Legal Intelligence Engine、新 Service Boundary。当前仓库的目录、依赖或目标文档不能改写历史。

## 六、下一轮 Project Fact Recovery Questions

按回忆价值排序，只保留最能关闭事实缺口的问题：

1. 你第一次 clone 后，本地启动时最少需要启动哪些服务？是只启动后端/数据库，还是还要启动队列、对象存储、向量库或图数据库？
2. 上传 PDF 后页面是一直等待，还是立即显示“处理中”？是否能回忆出后台异步任务或进度状态？
3. 你是否见过 RabbitMQ 的管理页面（通常是 15672 端口）、exchange、queue、ack 或 retry？
4. 你是否在 MinIO 控制台见过 bucket/object，或亲自调试过对象路径？
5. 你是否打开过 Neo4j Browser 并执行过 Cypher，还是只学习过 GraphRAG 概念？
6. 你是否见过 Milvus collection/index，或只知道团队方案中提到向量库？
7. 你当时进入的数据库更像 PostgreSQL、SQLite、MySQL 还是其他？只需判断产品，不需要猜表名。
8. Memory 任务的输入和输出是什么？是 Session 对话、用户偏好、检索上下文、Agent 状态，还是其他内容？
9. OpenViking 接入时你改的是配置/Adapter、Memory API、召回逻辑，还是页面/接口？
10. Tool Calling Strategy 具体解决的是“何时调用、选哪个工具、参数构造、失败重试、观察结果回注”中的哪一项或哪几项？
11. 第一次客户 Demo 时，页面有没有显示检索命中文档、引用来源或原文片段？
12. 客户说“回答质量需要提高”时，最先被指出的是事实错误、引用不准、漏召回、答案不完整、响应慢，还是其他问题？
13. 法院侧人员测试是直接登录系统、远程演示，还是通过你们提供的样例任务反馈？
14. 你能回忆第一次实际提交或第一次被技术负责人 Review 的文件/功能吗？记不清文件名时，描述功能即可。
15. 你参与的 OpenViking、Tool Calling 和 Memory 工作是在客户 Demo 之前还是之后？如果只记得相对关系，也足够。

## 七、审计红线

- `Current GitHub Repository ≠ Complete Historical Project Repository`。
- 当前依赖或 Compose 服务不等于历史使用。
- 团队使用不等于用户本人实现。
- 学习 GraphRAG 不等于产品主链路 GraphRAG。
- 有 Demo/Pilot 不等于生产部署或 Production Ready。
- 不创造正式产品名、合同甲方、法院名单、用户量、准确率、SLA 或生产流量。
