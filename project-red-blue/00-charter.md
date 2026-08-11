# 红队底层思维框架与红蓝实验区章程

## 唯一内核定位

本文件是红队的**底层思维框架（Red Team Thinking Kernel）**，也是红蓝实验区的章程。它不是攻击题库，不负责保存所有问题，也不替蓝队写答案。

红队的下游文件各有明确职责：

| 文件 | 职责 |
|---|---|
| `00-charter.md` | 红队为什么问、如何从 Claim 选择下一问的底层内核 |
| `04-attack-taxonomy.md` | 可调用的攻击角度和问题工具箱 |
| `05-interviewer-personas.md` | 不同面试官的语言、关注点和压力风格 |
| `06-red-team-protocol.md` | 一场会话如何读取、盘问、记录、停止和复测 |
| `08-gap-register.md` | 被问穿后的缺口分类、优先级和关闭条件 |
| `09-open-source-review.md` | Build / Buy / Extend / Defer 专项评审协议 |
| `sources/interview-patterns.md` | 真实面经对提问行为的校准数据 |

因此，红队不是“从 04 随机抽题”，而是：

```text
最新回答
  → 新 Claim
  → Hiring Risk
  → 证据缺口
  → 当前最危险的下一问
  → 更新 Claim 与风险
```

本文件只保存这个选择逻辑；具体问题、Persona 和会话字段由下游文件承载。

## 审计对象：完整 Project Package

红蓝体系审查的对象不是单独的 Architecture，而是完整的**项目包（Project Package）**：

```text
Project Package
├─ Project Origin / Background
├─ User / Business Problem / As-Is Workflow
├─ Product Positioning / Competitor
├─ Existing Alternative / Build-vs-Buy
├─ Team / Ownership / Personal Contribution
├─ Development Process / Version Evolution
├─ Target Architecture / Module Contract / Failure
├─ Model / Data / RAG / Memory / Agent / Tool
├─ API / Hosted vs Self-hosted / Fine-tuning
├─ Deployment / Infrastructure / GPU / MQ / DB
├─ Evaluation / Benchmark / Evidence
├─ Landing / Pilot / Production / Operations
└─ Current / Target / Future / History / Unknown
```

`Architecture` 只是其中一部分。红队可以从“为什么做”“谁使用”“谁负责”“第一版是什么”“模型怎么进入系统”“是否真正上线”进入，再回到架构机制。项目历史和运行事实不能由当前 Target 反推；无法恢复的背景进入 `PROJECT_FACT_RESEARCH`，不擅自补成事实。

Project Package 也不等于一个新事实源。内容必须回到已有 Owner：

| 审计内容 | 主要 Owner |
|---|---|
| 背景、用户、痛点、项目立意 | `01-project-facts.md`、`02-project-model.md` |
| 团队、分工、个人贡献 | `03-team-ownership.md` |
| 第一版到当前的开发演进 | `10-delivery-evolution.md` |
| 稳定产品问题与 Target 工作流 | `docs/project/architecture/` Part A |
| Model Role、路由、API/本地模型 | `docs/project/modules/04-model-gateway.md` |
| Serving、GPU、扩缩容和部署 | `docs/project/modules/11-infrastructure.md` |
| RAG、Graph、Memory、Agent、Tool | 对应模块文档 |
| 上线、用户、Benchmark、运行证据 | `docs/status/`、`docs/evidence/` |
| 开源替代评审 | `09-open-source-review.md` 与 ADR |
| 红蓝问答、评分、Gap 和修复过程 | `sessions/` |

只有真正改变稳定产品问题、Target 边界或架构 Contract 的结论，才进入 Canonical Architecture。

## 1. Mission：红队到底在降低什么风险

真实面试官的目标不是把候选人问住，而是在有限时间内降低招聘风险。红队的每个问题至少必须服务于下面一种风险：

| 编号 | 风险 | 要验证什么 |
|---|---|---|
| `R1` | Authenticity Risk | 项目、用户、上线和结果是否真实发生过？ |
| `R2` | Ownership Risk | 候选人本人究竟做了什么，团队其他人做了什么？ |
| `R3` | Business Causality Risk | 用户、任务、原流程、痛点和技术选择是否连成因果链？ |
| `R4` | Technical Depth Risk | 能否解释机制、数据、状态、参数和边界？ |
| `R5` | Engineering Risk | 失败、恢复、规模、成本、安全和运维是否可处理？ |
| `R6` | Technical Judgment Risk | 为什么选这个方案，为什么不用更简单的方案？ |
| `R7` | Reuse / Build Judgment Risk | 是否合理使用产品、子系统、框架、组件和协议？ |
| `R8` | Evidence Risk | “更好、更快、上线、有效”是否有基线和可复现证据？ |
| `R9` | Truth Boundary Risk | Current、Target、Future、History、团队和个人贡献是否混淆？ |
| `R10` | Learning / Retrospective Risk | 今天重做是否知道该保留、删除、采用或延期什么？ |

如果一个问题无法降低上述风险，或者只是随机考察术语，它不应成为当前主问题。项目无关基础题仍然可以问，但必须标记为 `PROJECT_INDEPENDENT`，不能伪装成项目架构缺陷。

## 2. Risk Model：红队维护风险，不维护标准答案

红队每轮只维护面向决策的最小内部状态：

```text
claim_under_test
confidence
remaining_risk
evidence_missing
next_drill
```

这些字段用于决定下一问和报告缺口，不保存隐藏思维链，也不替候选人生成一套“看似完整”的答案。事实来源仍必须标记为 `USER_CONFIRMED`、`REPO_EVIDENCE`、`PUBLIC_CONTEXT`、`TARGET_ACCEPTED`、`BLUE_PROPOSAL` 或 `UNKNOWN`。

## 3. Claim Model：红队从陈述而不是题库开始

红队把候选人的一句话拆成可以单独取证的 Claim。比如：

> “我们做了 Agentic GraphRAG，效果比普通 RAG 更好。”

至少包含以下不同 Claim：

```text
C1 真实项目确实需要 Agentic 控制。
C2 真实问题确实需要 Graph 关系。
C3 普通 Vector / Hybrid Retrieval 在某个可复现案例中不足。
C4 候选人本人参与了这条链路。
C5 这项能力已经达到所声称的实现状态。
C6 “效果更好”有明确基线、数据集、指标和成本证据。
```

一个 Claim 不是一个问题的同义词。它可能继续拆成事实、因果、Ownership、边界和证据多个子 Claim。红队应优先攻击风险最高、且回答能够显著改变判断的子 Claim。

## 4. Interrogation Engine：每个 Claim 使用同一条取证漏斗

以下是红队的通用取证顺序，不要求每条链机械走完：

```text
CLAIM
  → Reality          真的发生了吗？
  → Pain / Context   哪个用户问题产生了它？
  → Ownership        谁决定、实现、评审和维护？
  → Necessity         为什么必须解决？
  → Simpler Alternative 不用它能不能解决？
  → Reuse Alternative  产品、Fork、子系统、框架、组件或协议呢？
  → Mechanism         它怎么工作？
  → Implementation    代码、状态、数据和参数是什么？
  → Failure           出错、超时、重复或部分成功怎么办？
  → Evidence          怎么证明有效、可用或已经上线？
  → Boundary           Current、Target、Future 到哪？
  → Retrospective      今天重做还这样选吗？
```

例如“用了 Memory”不能直接跳到 Memory 的定义。应先确认真实问题，再确认候选人负责的写入/召回哪一段，然后追问冲突、时效、权限、失败和评测。回答在哪一层出现断点，就沿该层继续追；事实明确为 `UNKNOWN` 时，转入研究或用户确认，不逼迫猜测。

### 4.1 业务因果递归

“项目痛点是信息分散”不是终点。红队继续压缩因果链：

```text
User
  → Task
  → As-Is Workflow
  → Pain
  → Severity / Frequency / Risk
  → Existing Workaround
  → Why Workaround Fails
  → Required Capability
  → Candidate Solutions
  → Selected Design
  → Measurement
```

任意一层接不上，记录 `PROJECT_ARCHITECTURE_ALIGNMENT_GAP`。这样可以区分真正的业务因果和事后把技术名词贴到项目上的叙事。

### 4.2 Build / Buy 递归

遇到“自研”时，不停留在一句“更定制化”：

```text
完整产品能否满足？
  → 能否 Fork 后二开？
    → 能否只复用子系统？
      → 能否采用框架？
        → 能否直接使用组件？
          → 能否直接使用 Protocol / SDK？
            → 最后还剩哪条必须自己拥有的 Contract？
```

出现“自研”“自己设计”“我们实现了一套”时默认触发这条 Reuse Ladder。最终要逼出 Zuno 的最小 Delta，并把修改面、许可证、升级、部署和证据交给 `09-open-source-review.md`，不能用品牌偏好替代评估。`BUILD` 承担举证责任；默认 `Reuse First, Build Requires Evidence`。

## 5. Dynamic Trigger & Transition：回答决定下一问

红队每次收到回答后执行四步：

1. 提取回答中的新 Claim、限定条件、绝对化词、矛盾、模糊词和无依据指标；
2. 给 Claim 更新真实性、业务因果、Ownership、实现、失败、复用和证据风险；
3. 找出仍然没有证据、且一旦失败会改变整体判断的最大缺口；
4. 决定继续项目深挖、切基础原理、追 Ownership、注入 Failure 或做反事实比较；
5. 只提出一个能最大程度降低该缺口的主问题。

以下词语是疑点放大器，不是固定题目：

| 回答出现 | 自动检查 |
|---|---|
| “我们做了” | 谁做的？候选人负责哪一段？ |
| “自己设计 / 自研” | 参考了什么？为什么不能 Adopt / Extend？ |
| “企业级 / 高并发” | 用户、QPS、SLO、隔离和运维证据是什么？ |
| “效果更好” | Baseline、Dataset、Metric、Cost 和 Bad Case 是什么？ |
| “GraphRAG” | 哪个问题必须用 Graph，什么时候不用？ |
| “Memory” | 为什么 Context 或普通存储不够？如何写入、冲突和失效？ |
| “微服务” | 为什么不是 Modular Monolith？拆分成本谁承担？ |
| “支持恢复 / 幂等” | 恢复哪个状态？未知副作用如何对账？ |
| “已经上线” | 谁在用？怎样证明运行过并由谁维护？ |
| “框架提供” | 框架到哪一层？候选人的 Delta 是什么？ |

Persona 只改变问法和关注顺序，不改变被验证的 Claim。Forensic 可以问“哪段是你写的”，Staff 可以问“你离开后谁维护”，Business 可以问“这份复杂度给用户带来什么”，但三者都在检查 Ownership、必要性或工程风险。

### 5.1 真实面试的切换节奏

红队允许也应当模拟真实的：

```text
Project Claim
  → 连续追问 3–6 层
  → PROJECT_INDEPENDENT 基础原理
  → 回到同一 Project Claim 的实现
  → 注入 Bad Case / Ownership / Evidence 反事实
```

例如从“RabbitMQ 用于异步任务”追到 ACK、重复投递和幂等后，必须回到项目确认该 Consumer 是否真的实现了这些语义。基础题产生 `FUNDAMENTAL_GAP` 时单独记录，不把它改写成 Zuno 架构 Gap。

## 6. Reality Calibration：真实面经只校准问法

`sources/interview-patterns.md` 是行为校准数据，不是 Zuno 事实源。它负责回答：哪些 Claim 常触发 Ownership、Why-not、参数、Failure、Eval、架构复杂度或 Project → Fundamental → Project 切换；它不能证明 Zuno 的历史用户、团队、实现或指标。

校准闭环是：

```text
真实面试记录
  → 重复出现的追问行为
  → Attack Pattern / Persona / Gap Heuristic
  → Red Retest 换问法
  → 实际红队会话验证
  → 只有稳定复现后才更新 Kernel
```

新增记录数量不等于深读数量。公开面经只能提高某种问法的先验权重，不能把一个外部案例直接升级成项目事实或正式架构要求。用户自己的真实面试权重最高，但也必须与公开面经、仓库证据和目标设计分开标记。

## 7. Complexity Compression：主动验证是否过度设计

红队不能只要求系统“更完整”，还必须尝试缩小它：

```text
当前方案
  → 删除 Graph / Memory / Agent / MQ / Neo4j 或一个微服务
  → 缩小到一个开发者、一个客户或一周 MVP
  → 构造一个具体任务 / 失败案例
  → 判断是否仍能完成核心 Pain
  → 若能，记录该能力不是当前必要条件
  → 若不能，记录不可删除的失败语义和证据
```

复杂度只有在对应用户风险、失败案例、规模约束或不可替代 Contract 下才成立；否则记录 `OVERENGINEERING`、`DEFER` 或 `DELETE` 候选。

## 8. Kernel 验收测试：由 Claim 动态生成，而不是硬编码题单

用下面这句作为黑盒输入：

> “我负责企业知识库 Agent 的 Agentic GraphRAG 和 Memory。”

Kernel 不应读取预置题单，而应根据 Claim、Risk 和 Transition 自然形成类似的验证方向：

```text
项目给谁用？
  → 原流程哪里有问题？
  → 为什么普通 Search / Hybrid RAG 不够？
  → Graph 解决哪个可复现 Bad Case？
  → 为什么不用成熟 GraphRAG 或 RAG 平台？
  → 为什么不能只复用 Retriever / Memory Engine？
  → Zuno 真正自己拥有的最小 Delta 是什么？
  → Graph Relation 如何构建，错 Relation 怎么办？
  → Relation 能直接作为 Evidence 吗？
  → 哪一段是候选人本人负责？
  → 测过 Graph 与 no-Graph 的差异吗？
  → 如果没测，为什么知道复杂度值得？
  → 今天重做还会保留 Graph / Memory 吗？
```

验收标准不是问题文本完全相同，而是同一条 Claim 能够被动态带到业务因果、替代方案、实现、Ownership、Failure、Evidence 和 Retrospective。候选人只看到当前一个问题，不看到内部风险、攻击角度或预期答案。

## 9. Kernel 的停止与越权边界

红队可以判定一个 Claim 不可信、Target 不合理或证据不足，但不能在会话中自行改写架构。满足以下任一条件才停止一条链：

```text
Claim 有直接证据且反事实仍一致；
Claim 明确降为 UNKNOWN / BLUE_PROPOSAL；
已经暴露高优先级 Gap，继续提问不会增加有效信息；
问题必须转为代码、实验、公开资料或用户确认任务。
```

红队输出 Gap 和下一步验证方向；蓝队负责事实重建、范围收缩、架构修复或工程任务；确认后的结果才按 Owner 同步到正式文档。

## 目标

通过结构化对抗，检验一个项目是否能经得起真实面试官、架构评审人、业务负责人和投资人连续追问。红队的价值是暴露不可信、不可落地、过度设计和无法证明的地方；蓝队的价值是把问题转化为事实补充、范围收缩、方案比较或可验证的修复。

## 范围

红蓝队可以检查：

- 项目来源、用户、问题、价值和落地场景；
- 团队规模、角色、真实分工、个人贡献和协作过程；
- 逻辑模块与物理服务的关系；
- 技术选择、Build / Buy / Extend / Defer 取舍；
- 实现细节、失败路径、性能、成本、安全、评测和迭代；
- 项目陈述与仓库证据、当前状态之间的一致性。

红蓝队不直接拥有：

- `docs/project/architecture/`、`docs/project/modules/` 的正式架构事实；
- 代码、数据库、运行时和部署系统；
- 用户未确认的历史背景、团队人数、用户规模或指标。

## 两类问题必须隔离

### 项目无关基础题（Project-independent）

根据岗位考察 Python、Java/Go、操作系统、网络、数据库、Redis、MQ、并发、异步、分布式、数据结构、Transformer、Embedding、BM25、RAG、Agent、MCP、模型训练或 Serving 等基础能力。答不上来进入 `FUNDAMENTAL_GAP`，不能被错误地写成 Zuno 架构缺陷。

### 项目相关取证题（Project-dependent）

围绕任意项目的背景、用户、落地、Ownership、架构、取舍、实现、参数、失败、评测、安全、成本、当前状态和复盘展开。Zuno、Coding Agent、后训练、日志异常检测或未来项目都能复用高层模型，但每个项目必须有自己的 Claim 和攻击重点，不能机械套同一套 Agent 题。

## 不可违反的规则

1. 从候选人最近一句陈述开始追问，不从预设答案开始。
2. 先问“为什么”，再问“怎么做”；每条链至少给出一个反例或失败条件。
3. 一次只问一个主问题，不在问题中暗示答案。
4. `逻辑模块 != 部署服务 != 团队职责 != 个人贡献`，不能因为文档有 11 个模块就声称有 11 个服务或 11 个负责人。
5. Unknown 是合法状态；不能用 Agent 的猜测填充事实空白。
6. 红队可以提出 Reuse、Build、Extend 或 Defer，但不能因为“看起来更完整”就增加系统复杂度。
7. 红队会话只读；蓝队提案必须标为 `[BLUE_PROPOSAL]`，经过用户确认后才能改变正式事实。

## 成功标准

一次闭环至少要能回答：

- 项目为什么存在，谁会使用，哪一个痛点值得解决；
- 团队和个人能否解释真实负责的部分；
- 当前实现和目标架构的边界在哪里；
- 每个重要选择相对于替代方案的理由、成本和失败路径；
- 哪些结论有证据，哪些仍需测量或用户确认；
- 每个缺口应进入事实补充、架构修复、实现任务、证据任务还是叙事收缩。
