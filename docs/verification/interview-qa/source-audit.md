# Source Audit

## 审计边界

本次读取以可访问的最新来源为准：

- Zuno：main 基线为 4a6486edf4b27ad74ba99621de09ba83273b34fd。
- internship-work：浅克隆 commit f31d3fb，读取 interview/。
- interview-notes：本机可用独立仓库 F:/Onboard anything/05_TopDown_题库学习/面经，commit 7fc01bf；没有使用 README 中的总量直接推断。
- 本机没有可用的 internship-work/面经 Junction；没有把第三方面经原文复制进 Zuno。

## 实际计数

“parsed”定义为：文件可按 UTF-8 读取，且可以分离路径、文件体和（存在时）元信息；“question-bearing”使用问题标点、编号问题和中文疑问模式做确定性初筛；“sampled”表示本次实际读取并用于 pattern mining 的 question-bearing 文件，不代表只随机抽样。

| 来源 | discovered | readable | parsed | question-bearing | sampled |
| --- | ---: | ---: | ---: | ---: | ---: |
| internship-work/interview | 32 | 32 | 31 | 27 | 27 |
| interview-notes/Agent开发 | 1612 | 1612 | 1612 | 835 | 835 |
| interview-notes/RAG | 306 | 306 | 306 | 154 | 154 |
| interview-notes/Python工程 | 16 | 16 | 16 | 8 | 8 |
| interview-notes/AI产品 | 10 | 10 | 10 | 5 | 5 |
| 本次聚焦合计 | 1976 | 1976 | 1975 | 1029 | 1029 |

另外，面经独立仓库当前总 Markdown 文件数为 2333；本轮完整读取的是上表中与 Agent/RAG 及相邻 AI 应用方向相关的 1944 个文件，没有把未读取方向伪称为完整审计。

确定性扫描还提取到：

- 启发式问题行：12945；
- 显式包含 ? / ？ 的问题行：9059；
- 人工语义合并后的 question pattern family：64；
- 最终冻结并扩展为 Zuno QA：267 题；本轮新增 Memory & Information Extraction 35 题。

64 个 pattern family 是经过主题、触发条件和追问方向合并后的人工审计结果，不是把每一行标点变化都当作新问题。语义去重和来源归类仍属于 manual review；自动 verifier 只负责题库结构、引用和覆盖状态，不伪造语义质量。

## 个人真实面试

完整读取的正式面试场次：

1. 01 泛微网络 FDE 实施工程师：HR 面，作为岗位/问题风格对照。
2. 02 则知科技 Agent 开发实习：原始逐字稿、QA 整理、复盘、JD。
3. 03 遥望科技 通用 Agent 实习：原始逐字稿、QA 整理、复盘、JD。
4. 04 丰疆智能 架构培训生（AI 工程师）：原始逐字稿、QA 整理、复盘、JD。

05 杭州泛讯和 06 Shopee 在当前仓库只有 JD/README，没有正式 QA/逐字稿，因此不把它们计入正式个人面试问题统计。

高价值真实追问集中在：GraphRAG 为什么必要、Hybrid 是否足够、Agent 决策复杂在哪里、上下文压缩触发、架构边界、落地证据、状态持久化和如何证明有效。

## 面经公司与轮次标签

路径元信息不是统一 schema，因此只报告原始路径标签的统计：

- Agent开发：805 条记录、51 个公司/来源标签；主要标签包括字节、阿里、腾讯、小红书、快手、美团、百度、京东、蚂蚁、华为；轮次标签包括面试、一面、二面、三面、终面、笔试。
- RAG：153 条记录、32 个公司/来源标签；主要标签包括字节、腾讯、阿里、快手、百度、小红书、美团、蚂蚁、华为、滴滴、京东、科大讯飞；轮次标签包括面试、一面、二面、三面。
- Python工程：16 个文件；AI产品：10 个文件。
- 系统设计目录在本机独立仓库中不存在，未假称已读取。

## 题目来源分布

| source_type | 题数 |
| --- | ---: |
| REAL | 88 |
| DERIVED | 80 |
| ARCHITECTURE_STRESS | 99 |
| 合计 | 267 |

REAL 保留真实来源路径和必要的短问题摘要；DERIVED 明确指出派生来源；ARCHITECTURE_STRESS 只引用 Zuno Target，不把压力题伪装成真实面经。

## 限制

- 本轮没有运行完整外部 CI，也没有声称面经库 1100+ 全部被读取。
- 面经来源只用于 pattern mining，不是 Zuno 的架构事实源。
- 真实来源中的答案、项目规模和第三方 benchmark 没有复制进 QA，也没有被当作 Zuno Current 证据。
