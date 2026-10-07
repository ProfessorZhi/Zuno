# Interview Acceptance Standard

```text
status: governing-standard
applies_to: Project / Architecture / Modules Human Narrative, Red / Blue workflow, Resume
owner: Cross-cutting Architecture Owner
introduced: 2026-10-07
scope: 后续每一轮自主治理的主指令
```

这份标准规定：Zuno 作为面试材料，什么算「通过」。它不拥有业务 Target，也不替代 [`architecture-narrative-quality-standard.md`](architecture-narrative-quality-standard.md)；它决定**如何验收**，以及**哪些改动允许自主发生**。

## 0. 唯一目标

不要优化「看起来真实」，而要优化：

> 任何强 Claim 都能被追到 History、个人 Ownership、代码、失败窗口、Evidence 和 Unknown。
> 面试官越追，项目边界应该越清楚，而不是越追越像后来补出来的架构。

**最终验收标准**：一个不了解 Zuno 的大厂资深工程师，从简历或 Project 进入后，可以连续追问 30–60 分钟；候选人的回答能稳定区分 Historical / Personal Ownership / Current / Target / Evidence / Unknown；所有强 Claim 都能落到真实代码、测试、故障、数据或明确 Unknown；继续追问不会暴露时间线冲突、Ownership 漂移、或「架构为面试临时补出」的痕迹。

## 1. 事实层永远高于面试效果

真实性来自证据链，不来自细节丰富度。以下升级**一律禁止**，无论面试效果多好：

```text
Pilot → Production
selected verification → Full CI
5-query smoke → GraphRAG superiority
Target → Implemented
team work → personal ownership
Framework capability → Zuno self-built
possible → proven
```

反向表述通常**提高**可信度：

```text
「这个当时没做到。」
「这部分是团队后续实现。」
「这里只有 selected PostgreSQL test。」
「holdout 现在是 measurement blocked。」
「这个 Target 我认可，但 code 还没有。」
```

一个大厂面试官发现一处这样的扩大，前面大量正确回答会一起失去可信度。

## 2. 六层事实分类

任何一句话都必须能归入其中一层，且不允许跨层漂移：

| 层 | 含义 | 谁能改 |
| --- | --- | --- |
| Historical | 当时真实存在/发生过的 | 只有真实证据 |
| Personal Ownership | 本人实际做的 | 只有本人做过的 |
| Current | 今天代码/文档真实做到的 | Evidence |
| Target | 被接受的架构方向 | Architecture / accepted ADR |
| Evidence | 已记录的可复现测量 | Evidence 文档 |
| Unknown | 明确承认不知道 | 任何人，且必须承认 |

History 不允许用今天的 Target 回填。

## 3. Interview Threads：不要 100 个独立知识点

`100 / 100 / 100 / 100` 的 harness 规模不变，但 Red 内部必须组织成**约 8–12 条高价值 Thread**。每条 Thread 逐层收紧：

```text
Resume Claim
→ 真实性
→ Personal Ownership
→ before / after
→ 真实问题
→ 最简单 baseline
→ 为什么 baseline 不够
→ 当前实现
→ 数据 / 状态 / 函数 / Contract
→ concurrency / timeout / crash / stale result
→ Evidence
→ Fundamentals
→ Build / Buy / Extend / Defer
→ cost / complexity
→ delete condition
```

**Red 必须跨题保持状态**：记住候选人前面说过的数字、函数、状态、Ownership 和 Unknown，并在后续问题里回钩。回钩优先于新增架构题。

示例回钩链：

```text
「threshold=6 是 heuristic」
→ 谁定的？
→ 为什么不是 5？
→ holdout 呢？
→ 没有 holdout，为什么简历还写 GraphRAG？
→ 你实际做的是 regression fix 还是 GraphRAG architecture？
→ 今天删掉 seed expansion 会发生什么？
→ 没证据时是否应该删？
```

## 4. 四类优先攻击面

每轮必须覆盖。

### Ownership consistency

你加入时系统已经有什么？这是你提出的还是已有方向？你本人第一笔修改是什么？哪个 commit / function / schema 最能代表你的贡献？哪部分是团队后续实现？今天 Target 里哪些当时根本不存在？哪些不能写成「我设计/实现」？

任何一次「我 / 我们 / 系统后来」的切换都可以触发 Ownership Interrupt。

### Implementation reality

强 Claim 必须能指出真实工程落点：先看哪个入口？哪个 class / function / table / migration？状态存哪里？transaction boundary 在哪？crash 在 commit 前后分别怎样？replay 怎样避免重复？test 怎样构造这个 failure？

不要求背 SHA，但必须指得出落点。

### Evidence escalation

Claim 越强，Evidence 要求越具体：

```text
「修过」      → regression
「效果提升」  → baseline + sample + metric
「稳定提升」  → holdout + repeatability
「生产稳定」  → deployment / incident / SLA / operation evidence
「法院验证」  → Task Class / reviewer / acceptance procedure / environment
```

没有对应证据时，主动降低 Claim。

### Build / Buy / Delete

任何自研层必须回答：框架已经提供什么？Zuno 新增的业务 Authority 是什么？wrapper / policy layer 是否足够？为什么需要新的 service / state / receipt？今天重做还会 Build 吗？什么 Evidence 出现时应该删除？

## 5. Blue Candidate 第一层必须像真实面试

默认 **20–60 秒**完成第一层：

```text
结论 → 我本人做了什么 → 一个最关键机制 → 一个 Evidence 或边界
```

不要一题直接讲完 architecture、failure matrix、trade-off 和未来规划。Red 追问后再展开第二、第三层。

这不是「技术不够深」，而是大厂一面里「先用 30 秒讲明白，再被追到底」比第一答讲五分钟更可信。

## 6. Architecture Interview Acceptance（closed-book 循环）

架构改动后，开启**独立 Red context**，与普通 Red/Blue 分开：

```text
Canonical Part A
→ Closed-book Red 只读 Project + Resume
→ Red 重建 Zuno mental model
→ Red 选 8–12 个高风险 claim
→ 连续盘问
→ Blue Candidate 只用 20–60 秒口语回答第一层
→ Red 继续追 implementation / failure / evidence
→ 最后才由 Architecture Reviewer 读取 canonical docs
→ 分类问题根因
→ 只修真正 Owner 文档
→ 再跑 closed-book
```

**Closed-book reconstruction 是本循环的核心。** Red 只能读：

```text
Frozen Resume
docs/project/README.md
docs/architecture/architecture.md
docs/modules/README.md
```

**禁止读**：Engineering Reference、Source、Evidence、ADR、Blue notes。

Red 至少必须能从 Human Narrative 理解：Zuno 为什么存在；什么任务普通 RAG / Workflow 就够；什么现实约束开始要求更强设计；九个责任域为什么存在；谁拥有正式业务事实；Runtime 为什么不能代表业务成功；Domain 已提交但 Checkpoint 未写时怎样恢复；timeout 后为什么不能 blind retry；authorization 为什么要重新检查；Memory 为什么不能覆盖 Domain；version drift 为什么需要重新验收；哪些复杂机制是 optional；什么情况下应该删除这些复杂度。

> **如果必须背 `AdmissionReceipt`、`SecurityEpoch`、`PlanVersion` 才能解释系统，Human Narrative 就没完成。**

## 7. Finding 必须严格路由

Blue Candidate 答不好 ≠ 架构有问题。每个 Finding 先分类：

```text
BLUE_SKILL_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_CHANGE
```

只有 **Owner / Authority / State semantics / Contract / Recovery semantics / Security Authority / Build-Buy causality** 本身错误，才允许 Architecture Revision。

```text
「Part A 没解释」        → Narrative / Doc
「Target 正确但没实现」  → Implementation
「代码有，但没有 holdout」→ Evidence
「候选人不会讲」          → Blue Skill
「简历写太强」            → Resume
```

**不允许用 Architecture change 修 Candidate 的表达失败。**

## 8. Interview Traceability（内部表）

维护一份内部对照，用于防止面试回答、简历和架构相互漂移。它**不进 Human Narrative**：

```text
Architecture Claim
→ 现实 failure
→ Owner
→ Target mechanism
→ Current status
→ code location
→ selected test / Evidence
→ personal ownership status
→ resume eligibility
→ interview questions
→ known Unknown
```

示例（GraphRAG）：

```text
Cross-document multi-hop retrieval failure
→ 03 / 09
→ optional Graph route
→ Current heuristic implementation
→ tiny regression evidence only
→ holdout BLOCKED
→ personal retrieval-quality commits exist
→ Resume 只能写 regression / retrieval work，不能写普遍提升
```

## 9. 「太像设计出来的项目」信号

Red 必须特别攻击以下信号。发现时**优先尝试删除、合并、Buy 或 Defer**，而不是继续补对象：

- Receipt 太多，但说不清哪个 failure 需要它；
- 每个概念都有一个 Service；
- 每个模块都拥有自己的数据库；
- 九模块被误讲成九个微服务；
- Target object 比真实 bad case 多；
- 没有真实 Evidence 却有极完整 state machine；
- 一切都有版本，但说不清什么时候版本漂移真的会错；
- Memory / GraphRAG / Multi-Agent 看起来像为了 Agent 技术完整性存在；
- 所有问题都用 retry / idempotency / event sourcing 回答；
- 所有设计都「未来可扩展」，却没有 delete condition。

## 10. 失败案例是架构教材主线

高价值 Part A 应能自然讲出至少这些具体失败：

```text
1. Domain transaction 成功，Checkpoint 未写就 crash
2. external POST 已执行，但 response 丢失
3. Plan 按 v1 解析，dispatch 时 Provider / Tool / Credential 已变 v2
4. 新证据进入，旧 Worker late result 返回
5. ContextPack 构建后权限被撤销
6. stale Memory 与新的正式 Domain fact 冲突
7. KnowledgeGeneration 构建了一半进程 crash
8. duplicate delivery / replay
9. Human Approval 等待期间 policy 变化
10. Evaluation sample 太小，却有人试图扩大结论
```

原则从 failure 自然产生。

## 11. 文档顺序：先现实问题，后术语

首次出现以下对象时，必须先出现 **现实场景 → failure → baseline 为什么失败 → 谁需要保存什么事实**，最后才给术语：

```text
AdmissionReceipt / KnowledgeGeneration / ReadinessDecision / PlanVersion / StepRun
PreparedAction / EffectReceipt / ReconciliationReceipt / SecurityEpoch
RuntimeExecutionSpec / ProviderBinding
```

术语只能压缩已经理解的概念。

## 12. 每轮结束的三个最终问题

1. 如果把 Agent、GraphRAG、Memory、Native Runtime 这些词全部删掉，Zuno 仍然有清楚的产品价值和工程问题吗？
2. 如果大厂面试官现在打开代码，他看到的东西会不会和候选人刚才说的一致？
3. 如果他抓住一个 Unknown 连续追十分钟，我们会越来越可信，还是必须开始编细节？

三个答案都健康，才结束本轮。

## 13. 自主修改权限

**可以自主迭代**：

```text
Project / Architecture / Module Human Narrative
Engineering Reference 的一致性
Cross-document redundancy
首次术语出现顺序
Failure / recovery explanation
Red / Blue workflow artifacts
narrative-quality rules
Evidence freshness 文档
测量协议与 Eval 设计
```

**不得因为 Red 问到了就擅自**：

```text
新增业务模块
新增状态机 / Receipt / Provider
改 Authority
改 Security Authority
改正式 Recovery semantics
把 Target 升级 Current
制造 Personal Ownership
制造测量数字
```

涉及这些内容时，必须先证明 root cause 真的是 Architecture Gap，并明确现实 failure、baseline failure、替代方案、成本和退出条件。

## 14. 最新 main HEAD 起步

每轮开始：

```text
1. fetch / pull 当前 main
2. 固定 exact SHA
3. 对上一轮 ledger 做 base-alignment
4. 已在 main 解决的 Finding 不得重新当成新 Architecture Gap
5. Current 变化通过 Evidence 读取
6. Target 只由 Architecture / Module / accepted ADR 决定
7. History 不允许用今天 Target 回填
```

禁止再次出现 base 较旧、导致 Red 重新发现已落地改动的问题。
