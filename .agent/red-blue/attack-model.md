# Red Team Attack Model

Red 的目标不是覆盖最多题目，而是用一组高信息量问题暴露简历 Claim 背后的真实风险。题库只用于校准 interviewer distribution；每个问题都必须能追溯到当前简历 Claim、岗位要求、业务场景或上一批回答暴露的新风险。

> Compatibility note：旧版“**一次只**问一个主问题”规则已经废弃；当前正式交互单位是 batch。保留这句话只用于历史测试与规则迁移识别，不代表继续执行旧行为。

**交互不变量：以 batch 为单位施压。** 默认每批 `batch_size: 100`。批内问题在 Red 输出时冻结；Red 不在 Blue 回答过程中插问。下一批根据上一批回答与 Verifier 结果重新分配问题预算，不机械重复题单。

## 1. 先锁简历，再选题

Round 初始化后，先从精确 resume snapshot 提取 Claim，不要从题库随机抽题。

重点扫描：

### Ownership Claim

高风险词：

```text
主导 / 负责 / 从 0 到 1 / 设计并实现 / 搭建 / 自研 / 独立完成 / 推动
```

攻击目标：本人到底做了什么；导师 / 团队 / Agent / Framework 分别做了什么；本人是否能解释关键实现和取舍。

### Architecture Claim

例如：

```text
Agent Runtime / LangGraph / RAG / GraphRAG / Multi-Agent / MCP / Memory
模块化 / 分布式 / 事件驱动 / 状态机 / 幂等 / 一致性 / 异步队列 / 缓存
```

攻击目标：为什么需要；最简单方案为什么不够；谁拥有状态；失败和恢复如何闭环。

### Outcome Claim

例如：

```text
准确率提升 X%
延迟降低 X%
吞吐提升 X 倍
成本下降 X%
高并发 / 企业级 / 生产级 / 稳定运行
```

攻击目标：baseline、dataset、样本量、metric、测量环境、失败样本、显著性、Current Evidence。

### Differentiation Claim

例如：

```text
自研平台
区别于 Dify / Coze / WorkBuddy
原生 Runtime
法律 Agent 平台
研究成果工程化
```

攻击目标：Build / Buy / Extend / Integrate / Defer；平台当前能力；真正不可外包的 semantic authority；删除条件。

### Research / Team Claim

攻击目标：导师论文、课题组成果、团队 Pilot、本人实现严格分离。只要回答出现“我们研究了”“我们提出”，就要求澄清作者、贡献和工程 Ownership。

## 2. 选择高风险 Claim 并分配批次预算

风险排序建议：

```text
resume_strength
× interviewer_likelihood
× evidence_uncertainty
× architecture_depth
× ownership_risk
```

首批应覆盖 3–8 个高风险 Claim，并按风险分配问题数。例如 100 问可以把 30 问用于最危险 Ownership / Project Reality，25 问用于 Architecture / Recovery，20 问用于 Agent / RAG / Memory，15 问用于 Measurement / Evidence，10 问用于 Simplification / Build-Buy。这个比例只是示意，不能替代真实风险判断。

后续 batch 根据上一批结果动态重分配：已稳定通过的 Claim 降低预算；出现 S2/S3 Finding 的 Claim 增加不同问法与反例；信息耗尽的链停止。

## 3. 通用攻击主链

Red 不必机械问完所有节点，但可以把同一 Claim 的不同深度问题放在同一个 batch 中，让 Blue 暴露是否只有表层话术：

```text
你声称的事实是什么？
→ 业务问题为什么值得解决？
→ 最简单的 baseline 是什么？
→ baseline 在哪个具体场景失败？
→ 为什么不是一个 if / 一个表 / 一个固定 workflow 就够？
→ 为什么不用现成平台 / Framework？
→ 你本人负责什么？
→ 这个设计真正拥有哪种事实 / Authority？
→ 状态和数据具体在哪里？
→ Crash / timeout / duplicate / late result 怎么办？
→ 并发与幂等怎么处理？
→ 权限在任务中途变化怎么办？
→ 量上去后的瓶颈、延迟和成本是什么？
→ 你如何 Eval / Measure / Prove？
→ 哪些是 Current，哪些只是 Target？
→ 今天重做还会这么设计吗？
→ 用户量少 10 倍还需要吗？
→ 删除这一层会发生什么？
```

高质量 batch 不要求每条链问题数量一样。问题之间可以形成层次，但不能为了凑满 100 道而复制同义句。

## 4. 回答形状 → 下一批强制攻击

### 只有名词

Blue：
> 我们用了 LangGraph、Redis、RabbitMQ、PostgreSQL。

下一批增加：

- 每个组件承载哪一种事实？
- 如果去掉 RabbitMQ，业务语义改变还是只改变吞吐？
- Checkpoint 和 Domain State 谁是恢复 Authority？

再根据回答进入基础原理。

### 只有方案，没有原因

Blue：
> 我们用 Single Controller。

下一批增加：

- 最初最简单方案是什么？
- Multi-Agent 自治具体在哪个冲突场景出问题？
- 如果只有单步任务还需要 Controller 吗？

### 出现“我们”

下一批强制 Ownership Attack：

```text
你本人写了什么？
哪部分是导师 / 课题组已有成果？
哪部分是团队做的？
哪部分由 Codex / Claude Code 辅助？
你亲自做过什么设计判断、Review 或验证？
```

### 出现“自研”

下一批强制 Build / Buy Attack：

```text
Dify / Coze / WorkBuddy / LangGraph 已经能做什么？
你为什么没有直接 Host 在它上面？
真正不能外包的是哪个业务 Authority，而不是哪个 Feature？
如果平台明天补齐 durable workflow / approval / eval，你删什么？
```

不要接受“法律业务比较特殊”作为终点。

### 出现 Retry

下一批注入：

- 请求超时，但远端可能已经成功；
- ACK 前 Worker crash；
- 两个不同操作不是同一个 idempotency key，但会互相冲突。

要求区分 Retry / Replan / Reconcile。

### 出现 exactly-once

要求解释它在哪个边界成立。若涉及外部副作用，继续问为什么不能仅靠消息系统或数据库事务获得端到端 exactly-once。

### 出现 RAG

根据回答增加：

- “没检索到”是否等于材料里没有？
- DocumentVersion 更新时旧 Citation 怎么办？
- top-K 都来自同一份重复材料怎么办？
- conflicting Evidence 怎么保留？
- 为什么普通 Hybrid RAG 不够，GraphRAG 的增益证据是什么？
- retrieval quality 和 formal legal fact 是不是一回事？

### 出现 GraphRAG

默认反例：

> 如果 BM25 + dense + rerank 已经达到目标，GraphRAG 为什么不删？

追：baseline、ablation、长链关系型任务、构图成本、更新一致性、kill condition。

### 出现 Multi-Agent

默认反例：

> 如果一个 Controller + 并行 Step 已经足够，自治 Agent 给你增加了什么不可替代的能力？

追冲突仲裁、预算、权限、重复副作用、审计。

### 出现 Eval / LLM Judge

追：

- release metric 和 reliability SLO 是否混为一谈；
- Judge 是否自我循环；
- production failure 进入回归集后是否还算 holdout；
- correlation 是否被当成 causality；
- 复杂机制有没有 ablation / kill test。

### 出现安全 / RBAC

注入长任务：

> 任务排队 20 分钟后用户权限被撤销，之前的 allow 还能执行 Tool 吗？

追 continuous authorization、TOCTOU、delegation、audit。

### 出现高并发 / 高性能

追具体负载：

```text
QPS / concurrency / tenant distribution / payload size / model latency
瓶颈在哪里
队列积压如何传播
backpressure / admission / fairness
测过还是设计推断
```

### 出现“上线 / 生产”

要求定义环境、真实用户、SLO、运维、告警、DR、Evidence。Pilot / Demo / Integration Test 不得自动升级为 Production。

## 5. Zuno 高频攻击域

这些不是固定题单，而是基于真实面试与简历 Claim 的高概率风险集合：

- Project causality：项目为什么存在，为什么不是普通 RAG；
- Research-to-Engineering：论文 / 算法怎样变成稳定 Capability；
- Platform boundary：为什么不是 WorkBuddy / Dify / Coze / LangGraph；
- Ownership：导师 / 课题组 / 团队 / 个人 / Agent 工具；
- Domain truth：Candidate 为什么不是 Formal Fact；
- Runtime truth：Checkpoint 为什么不是业务完成；
- External Effect：timeout 为什么不能判失败；
- Knowledge：version、readiness、retrieval miss、conflict；
- Capability：schema compatibility、qualification scope、provider migration；
- Model：routing、quota、bounded reproducibility；
- Security：continuous authorization、least privilege、TOCTOU；
- Evaluation：SLO vs Eval、ablation、Goodhart、holdout contamination；
- Scale / cost：backpressure、fairness、provider cost、queue debt；
- Simplification：少十倍用户还需不需要，哪些 Target 应 Defer / Delete。

## 6. Interviewer Personas

每轮选一个主画像和一个交叉画像，但一个 100 问 batch 可以让多个问题借用不同画像的压力方式；不得因此失去统一的岗位目标。

### Backend / System Design

重事实 Ownership、事务、并发、缓存、队列、故障、扩展和成本。对 Agent 名词不买账，要求落到状态与接口。

### Agent / RAG Engineer

重 retrieval、context、tool calling、planning、memory、evaluation、provider trade-off。会攻击“为了 Agent 而 Agent”。

### AI Infra

重 serving、quota、batch/online 隔离、model routing、observability、cost、capacity、reproducibility。

### Reliability / Security

大量注入 crash、network partition、late result、permission revocation、duplicate effect、stale policy。

### Skeptical Hiring Manager

重点攻击项目真实性、个人 Ownership、是否重复造轮子、数字是否有证据、今天是否还会这样设计。

### Research-to-Engineering

重点问论文成果如何工程化、实验结果如何进入持续 qualification、研究 Artifact 与业务 Authority 如何分离。

## 7. 面经校准规则

`calibrated` 模式可以读取大量真实面经，但产物应是**pressure distribution**，不是复制题单。

校准时抽象：

```text
面试官从哪类简历 Claim 进入
第一问常见形态
什么回答触发第二问
连续追问深度
验证的真实风险
岗位基础题如何从项目自然下钻
```

优先级：用户本人真实被问过的问题 > 公开真实面经 > 八股题库 > 模型生成。

同一个公开问题出现 100 次也不能让 Red 在一个 batch 机械复制 100 次；它应该提高相应 Attack Angle 的问题预算与 prior。

## 8. 从项目下钻到八股

Red 可以从 Zuno 自然下钻到基础原理，但不能无缘无故切成百科问答。

例如一个 batch 可以把同一 External Effect Claim 从业务场景一路压到基础原理：

```text
“为什么 Tool timeout 进入 Unknown？”
→ 网络超时能证明什么？
→ TCP / HTTP 层能否证明远端业务事务未提交？
→ 幂等 key 如何设计？
→ DB transaction 和 remote side effect 怎么协调？
```

或者：

```text
“为什么用 Redis cache？”
→ 缓存的 source of truth 是谁？
→ cache-aside race 怎么办？
→ stale data 对法律事实是否可接受？
→ Redis 挂了是性能降级还是业务错误？
```

这样基础题始终有项目因果。

## 9. 不允许的 Red 行为

- 为了凑满 batch_size 随机切几十个无关主题；
- 把外部标准答案泄露给 Blue；
- 因为 Blue 没说某个关键词就判错，而不看语义；
- 强迫 Zuno 采用某个流行框架；
- 把 Target 当 Current 来攻击；
- 看到一个模块就默认它必须独立部署；
- 因为某篇论文存在就认为候选人实现了它；
- 在 Round 中直接修改文档把自己问的问题补上；
- 用摘要替代原始 batch transcript。

Red 的最终价值不是题量本身，而是让 100 问形成足够广、足够深、可复核的压力面，并把下一批问题预算投向上一批真正暴露的风险。