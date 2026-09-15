# Red Interview Behavior Evidence — 2026-09

status: workflow-research-input
owner: Red/Blue Harness Maintainer
purpose: calibrate interviewer behavior; not a per-round Red question source

这份材料记录 AI Agent / LLM 应用研发面经的定性抽样。它不拥有 Zuno 项目事实，也不作为每轮 Red 的直接题库。Red Skill 只吸收稳定的 interviewer behavior；具体公司原题不直接复制进正式 Round。

公开面经属于候选人回忆和社区材料，不是公司官方面试规范。它适合判断“面试官通常怎么问”，不适合声称“字节一定这样问”。

## 已经反复出现的模式

### 先让候选人自己把主线暴露出来

多份一面从自我介绍、项目介绍或“挑一个最复杂 / 最熟的项目”开始。面试官先听候选人怎样组织问题、技术、结果和个人贡献，再决定从哪里下钻。

这比一上来问十个内部架构概念更接近真人。

### 后一问通常吃上一答

淘天的一条多 Agent 线是连续的：为什么拆子 Agent → skill 能不能替 → 不能替的局限在哪 → 改变前提后本质区别还剩什么 → 什么时候会出错 → 真遇到过吗。

去哪儿的一份记录也明确描述，面试官会根据候选人说出的关键词继续提问。字节 AI 应用一面记录同样是前面了解经历和项目，后面根据项目细节持续追问。

真正应该沉淀的是这种“听完再追”的行为，不是原题。

### 真人问题往往很短

常见表面问题只是：

```text
为什么这么做？
具体怎么实现？
这个数怎么来的？
你自己做哪段？
真遇到过吗？
如果失败呢？
```

深度来自连续追问，不来自一个问题里同时塞背景、算法、测试、故障和 Trade-off。

### 一场面试不会平均覆盖所有 Claim

很多 45–65 分钟一面会围绕一个主要项目追很久，再切第二项目、基础知识、算法或场景题。某条线回答很有信息量，就继续；很快证明候选人不熟，就换。

完整覆盖是 Pressure Suite 的目标，不是 Live Interview 的目标。

### 基础题可以从项目长出来，也可以直接切

Agent / AI 应用面经里常见项目后继续问并发、网络、数据库、TCP、协程、TopK 或算法题。它们不一定每一道都严格由上一句话推导。

Red 不应为了形式统一，把普通基础题包装成长篇项目场景。

## 字节样本补充：短问题，但会把一条线压得很深

2026 年 8–9 月几份公开字节 AI 应用 / AI Agent 面经给出了更明确的“深挖”样式。

### 项目先讲起来，再不断问具体

一份 2026-08 的 AI 应用开发一面记录描述：前半段主要了解个人经历和项目，后半段“根据项目细节不断追问”。题目覆盖 Agent 核心模块、Tool 设计、参数 Schema、Memory、ReAct / Plan-Execute 等，但整体体验并不是强压迫式审讯。

这说明“问得深”和“说话像人”可以同时成立。

### 同一回答可以连续追 3–5 层

一份 2026-09 的 AI Agent 社招一面回忆直接写到：每个回答会继续往下挖 3–5 层，并且会共享屏幕看代码。

记录中的追问形态包括：

```text
为什么这里用异步？
→ 为什么不用同步？
→ 异步任务状态怎么持久化？
```

Tool 场景还会从大结果 / 上下文问题继续追具体工程处理，从 timeout 追 retry 策略和失败后的处理，从评测体系继续追构建方式。

关键不是“3–5”这个数字本身，而是：如果候选人把某块说成强项，面试官愿意一直追到代码、状态、参数、异常和证据。

### Evaluation 会被当成完整工程问题追

一份 2026-07 的 AI Agent 开发岗记录从 RAG Agent 项目继续问：评测集怎么构建、观察哪些指标、是否研究行业 benchmark；然后把前提改成“线上 log 是海量的，怎么变成有限的线下评测集”。

这说明 Red 不应满足于“我们有 Recall / MRR”。如果数字是简历卖点，可以继续追数据从哪来、怎么更新、怎么从线上 failure 形成 regression set。

### 项目深挖会自然切到底层与安全

其他 2026-08 AI Agent 面经包括：多 Tool 连续触发如何避免混乱、RAG 召回差怎么排查、TopK；以及 PDF / 复杂表格解析、Query Rewriting、混合检索 / GraphRAG、状态机扩展，随后直接切 SSRF / CSRF 等基础与安全问题。

这支持一个更自然的面试模型：项目聊到足够深以后，可以直接切岗位基础，不必强行把所有底层题包装成项目追问。

## 用户本人真实面试记录：Ownership、减法与企业化追问

2026-08 的 Shopee、水滴集团、杭州泛讯三场用户本人面试记录提供了比公开面经更高优先级的行为证据。这里仍然只抽取 interviewer behavior，不把其中理想回答或后来形成的 Zuno Target Architecture 当作当时项目事实。

### Shopee：先问谁做的，再从 Tool 权限追到存储选择

Shopee MP 后端片段先问项目人数、谁主导架构、候选人具体负责哪些模块；随后连续追 Tool 权限到底由谁分配、用户权限和工具权限按什么维度判断，再问为什么使用多个数据库、一个数据库是否足够。

这说明真实 interviewer 很自然地使用下面的顺序：

```text
项目 Claim
→ Ownership
→ 具体机制
→ 最简单替代是否足够
```

Red 不应等一条技术线讲完才校验 Ownership。候选人从“我”滑向“我们”时，可以直接插入“这个决定是谁定的”“你自己写哪一段”。

### 水滴：Build / Buy 与方案来源本身就是真实性问题

水滴 Agent 应用工程师面试从“从头搭还是基于开源”“为什么不用开源”开始，又追模型和团队分工、两名 Agent 同学如何拆分工作。进入 Memory 后继续追 Working / Session / Long-term 分层、OpenViking 是否调研、方案来自导师还是团队、企业使用时分布式部署和并发怎么办、知识库和 Memory 边界、错误/过期记忆如何删除和冲突处理。

这里最稳定的 interviewer behavior 不是“喜欢问 Memory”，而是：

```text
自研 Claim
→ 开源替代
→ 方案来源
→ 个人 Ownership
→ 企业约束变化
→ 并发 / 状态 / 恢复
```

因此 Red 对复杂机制应主动做 Subtraction Test：如果数据库条件查询、框架能力、固定 Workflow 或普通 Subgraph 已经够用，候选人需要说明额外抽象解决了哪个真实 failure。

### 泛讯：项目机制可以自然桥接到运行时基础

泛讯 AI 应用工程师面试围绕 Agent / Skill / Tool、权限、MCP Schema / Provider 变化、Memory 写入纠错、Context Pack、Hybrid / GraphRAG 与多数据库展开。其问题形态说明 Agent 项目并不会与传统后端基础隔离：权限变化会进入 TOCTOU，Provider timeout 会进入 retry / idempotency，Memory 并发会进入数据库隔离和冲突，GraphRAG 并行检索会进入 async / cancellation。

这支持 Red 增加显式 `Project → Fundamental Bridge`：

```text
remote Tool timeout → HTTP 语义 → retry → idempotency
per-user config → 并发隔离 → ContextVar / request-local state
Graph retrieval → asyncio → timeout / cancellation
Memory write → lost update → isolation / optimistic lock / CAS
shared Agent state → stale result → versioning / coordination
```

桥接的目标是验证候选人的工程判断是否有底层知识支撑，不是把随机八股硬套进项目故事。

### 强结果必须触发 Evidence Escalation

三场本人记录也反复出现“到底谁做的、当前做到什么程度、一个数据库能否完成、企业并发是否真的处理”等问题。它们共同说明：Claim 越强，面试官越可能要求更具体的交叉验证。

```text
“优化了” → 给一个失败样本和 before/after
“稳定” → 哪类运行证据支持
“我做的” → 入口、函数、数据结构或 commit 在哪里
“企业可用” → 并发、隔离、部署、审计做到什么程度
```

这类 Evidence Escalation 比机械追问“有测试吗”更接近真实面试。

## 对 Red Skill 的直接约束

1. Live Interview 不使用固定 30 问线性脚本。
2. 先用少量 Seed 让候选人暴露主线，再按回答动态选 follow-up。
3. 一次只问一个主要意图。
4. Follow-up 优先复用候选人刚说过的名词、数字、选择、失败和不确定点。
5. 高价值 Thread 允许自然连续追 3–5 层甚至更深；深度可以进入代码、参数、状态、并发、网络、异常、评测和基础原理。
6. 深度必须由上一答解锁。不要在第一问把五层验证揉成复合长句。
7. Thread 没有新信息增益时及时换题；Kill Switch 属于 Controller，不作为面试官话术。
8. Pressure Suite 可以保持 100 问，但必须与 Live Interview 分离。
9. 人工 Review 既检查“像不像真人”，也检查“有没有真的追深”。
10. 字节面经只提供行为校准，不变成“字节原题库”。
11. 用户本人真实面试记录优先于公开社区样本，用于校准 Ownership Interrupt、Subtraction Test、Evidence Escalation 和 Project → Fundamental Bridge。
12. Project → Fundamental Bridge 优先从候选人自己声称做过的机制下沉，但岗位基础题也允许在项目段结束后直接切换。
13. Red 不预编排固定比例的“架构题”；题目分布跟随高价值 Claim、可信度变化和上一答暴露的新 handle。

## 本次抽样来源

### 用户本人面试记录

- `ProfessorZhi/internship-work`：2026-08-06 Shopee MP 后端开发 QA；项目人数 / 架构 Owner / 个人模块、Tool 权限、用户与工具权限、多数据库与检索/图谱。
- `ProfessorZhi/internship-work`：2026-08-11 水滴集团 Agent 应用工程师 QA；Build/Buy、团队分工、Memory 分层、OpenViking、企业并发、知识库边界、冲突和删除。
- `ProfessorZhi/internship-work`：2026-08-06 杭州泛讯 AI 应用工程师 QA；Agent/Skill/Tool、权限、MCP 变化、Memory、Context Pack、Hybrid/GraphRAG 与多数据库。

### 公开定性样本

- 牛客：字节跳动 AI 应用开发一面面经，2026-08；前段了解经历和项目，后段根据项目细节继续追问。
  https://www.nowcoder.com/feed/main/detail/15af3788a038477bba99f2f9d94b2cef
- 牛客：字节大模型应用开发一面，2026-08；项目深挖覆盖 AI Coding、执行安全、多轮修正等工程问题。
  https://api-cdn.nowcoder.com/discuss/916420927619928064
- 牛客：字节 AI Agent 开发岗社招一面，2026-09；候选人描述回答会被继续深挖 3–5 层，包含共享屏幕看代码、异步 / 状态、Tool 大结果、timeout / retry、评测体系等。
  https://www.nowcoder.com/discuss/926968209813639168
- 牛客：字节 AI Agent 开发岗面经-02，2026-06/07；包含 RAG Agent、评测集构建、指标、行业 benchmark、线上 log → 有限线下评测集等。
  https://www.nowcoder.com/discuss/922659486983036928
- 牛客：字节 AI Agent 开发岗面经-01，2026-08；包含多 Tool 调用、RAG 排查、TopK、复杂文档解析、Query Rewriting、混合检索 / GraphRAG、状态机和安全基础。
  https://www.nowcoder.com/discuss/922659050167226368
- 牛客：字节大模型算法岗面经汇总，2026-04–07；反复出现项目技术细节、代码实现、ablation、reward / RL 原理与工程问题的深入追问。
  https://www.nowcoder.com/discuss/921942397339082752
- 牛客：淘天 AI Agent 开发岗面经汇总，2026-04/05；包含 answer-dependent 多 Agent 深挖链。
  https://www.nowcoder.com/discuss/928330748212281344
- 牛客：去哪儿 AI 面，2026-08；作者明确描述提问会根据候选人说出的关键词继续追问。
  https://www.nowcoder.com/feed/main/detail/4ef227c6b7c74394b487fbfa37c0f941
- 牛客：经历多场 AI 面后的 AI 面试官复盘，2026-09；无信息增益的原子化追问会产生明显机器感。
  https://www.nowcoder.com/feed/main/detail/f984450bb2744b1d8df3581388c288fb

## Evidence boundary

这是定性样本，不代表所有字节团队、所有面试官或所有 Agent 岗位。用户本人面试记录也只代表其当场经历，不代表这些公司所有团队的固定面试法。Skill 只采用跨来源重复出现、且与用户实际反馈一致的行为模式。后续如果用户提供本人新的真实面试记录，继续优先更新。