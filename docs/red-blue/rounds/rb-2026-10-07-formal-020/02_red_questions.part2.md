# Red Wave 1 — Questions Q51–Q100

```text
round: rb-2026-10-07-formal-020
role: Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师
stage: 技术一面 / 项目深挖
threads: T06 Project History · T07 Pilot/法院 · T08 系统简化 · T09 Knowledge/Retrieval · T10 工程基础
blind: true（仅读 frozen resume + attack-model）
```

## T06 — Project History

**Q51.** 你加入 Zuno 的第一天，仓库里已经有什么东西是能跑起来的？——请说一个你当时能亲眼看到它跑通的入口，而不是文档里写的东西。
> `intent`: 建立入职时的系统存量基线，后面所有 Ownership 判断都以这一答为参照 ｜ `callback`: — ｜ `depth`: L1

**Q52.** 你在这条链路里提交的第一笔改动是什么？改的是哪个文件、哪个函数？
> `intent`: 定位第一笔个人改动，作为「个人贡献时间轴」的起点 ｜ `callback`: — ｜ `depth`: L1

**Q53.** 简历这五条 bullet，逐条说：哪一条是你从零写的，哪一条是你接手别人已有的东西再改的？
> `intent`: 把五条 Claim 逐条切开归属，防止「我们」覆盖个人 ｜ `callback`: — ｜ `depth`: L1

**Q54.** 你说重构了「MCP Tool 经子 Agent 转发」这套 —— 那套转发是谁写的？当时是出于什么考虑才让子 Agent 中转的？
> `intent`: 重构对象的前史与原始动机，验证是否真的理解被重构的东西 ｜ `callback`: Q53 ｜ `depth`: L2

**Q55.** 从你第一笔改动，到「把 MCP Tools 直接绑定主 Agent」这件事落地，中间隔了多长时间？那段时间你主要在做什么？
> `intent`: 时间线与工作密度的交叉校验，检验重构是否突兀出现 ｜ `callback`: Q52 ｜ `depth`: L2

**Q56.** GraphRAG 排序回退这个方向，是你提出来的，还是方向已经定了、交给你执行？你做到哪一层：定位问题、定方案、还是只写实现？
> `intent`: 区分「提出方向 / 设计方案 / 仅实现」，定位该 Claim 的真实 Ownership 层级 ｜ `callback`: Q54 ｜ `depth`: L2

**Q57.** 你今天讲的 typed contract、版本、receipt 这一类机制，在你加入的第一个月存在吗？如果当时没有，那当时靠什么保证同一件事？
> `intent`: 区分「当年具备的能力」与「今天的机制」，追问演进前靠什么兜底 ｜ `callback`: Q51 ｜ `depth`: L2

**Q58.** 你描述的系统分成九个模块 —— 这九个里，哪一个在你加入之前接口就已经定型、你从头到尾没有改过它？
> `intent`: 找出「零改动模块」，作为个人覆盖面的边界证据 ｜ `callback`: Q53 ｜ `depth`: L2

**Q59.** 你在 Q53 说某条 bullet 是你写的、Q56 又说某条是已有方向 —— 如果我现在逐行看 blame，这几条 bullet 的主要贡献者分别是谁？
> `intent`: 用 blame 视角交叉验证 Ownership 归属，逼出团队/学长/框架的三方拆分 ｜ `callback`: Q53, Q56 ｜ `depth`: L3

**Q60.** 如果只允许你留一条 bullet，且必须删掉你个人没有实际做过的部分 —— 你留哪一条，删掉哪四条？为什么是这条？
> `intent`: 收口，逼出「个人净贡献」的自我判断 ｜ `callback`: Q53 ｜ `depth`: L3

## T07 — Pilot / 法院

**Q61.** 「法院侧测试」这件事是谁发起的？当时在场的有哪些角色？
> `intent`: 确认这件事的组织主体和参与方，判断是正式测试还是临时演示 ｜ `callback`: — ｜ `depth`: L1

**Q62.** 你本人当面跑过 demo 吗？那次是现场真跑，还是提前把输入固定好、只走一遍成功路径？
> `intent`: 区分「现场演示」与「预置输入的演出」，直接指向 demo 的真实性 ｜ `callback`: — ｜ `depth`: L1

**Q63.** 法院那边实际使用这个系统持续了多久？是每天用、隔几天用一次，还是只在一个时间窗口内测了一轮？
> `intent`: 用使用时长与频次界定测试的真实规模，不索取百分比 ｜ `callback`: — ｜ `depth`: L1

**Q64.** 「Pilot Validation」这个定性是谁给的？是法院/甲方那边给出的结论，还是你自己在简历里这样写的？
> `intent`: 追「Pilot Validation」这个词的出处与授权方 ｜ `callback`: Q63 ｜ `depth`: L2

**Q65.** 在那段使用期里，有没有收到过真实使用者报回来的具体 bad case？请说一条，以及当时怎么处理的。
> `intent`: 用真实 bad case 的存在与否，检验是否真的有使用闭环 ｜ `callback`: Q63 ｜ `depth`: L2

**Q66.** 你简历里那些效果相关的说法，分别来自哪里 —— 你自己跑的、团队给你的、还是某份文档里写的？说清来源而不是数值。
> `intent`: 为每个数字建立来源归属，不诱导编造数值 ｜ `callback`: Q63 ｜ `depth`: L2

**Q67.** 如果这个系统明天关掉，法院那边会有人发现并来问吗？
> `intent`: 用「依赖是否真实存在」检验它离 production 的距离 ｜ `callback`: Q63 ｜ `depth`: L2

**Q68.** 法院侧测试的用例和验收标准是谁写的？法院有没有出自己的题，还是你们自己出题自己验收？
> `intent`: 检验测试是否存在独立第三方标准，还是自证 ｜ `callback`: Q61 ｜ `depth`: L2

**Q69.** 你在 Q64 说 Pilot 这个定性来自某一方 —— 那按你今天的判断，阻止你把它叫做 Production 的第一位原因是什么？
> `intent`: 收口到「为什么不是生产」，检验候选人的自我诚实度 ｜ `callback`: Q64 ｜ `depth`: L3

**Q70.** 如果面试官直接问你「这个系统在生产环境跑过吗」，你最诚实的一句话回答是什么？那你为什么仍在简历上保留 Pilot Validation？
> `intent`: 收口，检验候选人能否在压力下保持表述一致性 ｜ `callback`: Q64, Q67 ｜ `depth`: L3

## T08 — 系统简化 / Delete

**Q71.** 你那九个模块里，哪些模块的调用方只有一到两个？
> `intent`: 用调用方数量找抽象的可疑层，为后续减法建立清单 ｜ `callback`: — ｜ `depth`: L1

**Q72.** 如果今天从零重做，你第一个删掉的模块是哪个？
> `intent`: 直接执行 Subtraction Test，取候选人的第一直觉 ｜ `callback`: — ｜ `depth`: L1

**Q73.** 九个模块里，哪一个删掉之后主流程仍然能跑完？
> `intent`: 找出「删除无损」的模块，检验复杂度是否真的有支撑 ｜ `callback`: — ｜ `depth`: L1

**Q74.** 这些抽象里，哪一个是你为了架构完整性加的，而不是某个具体 bad case 逼出来的？
> `intent`: 逼出「架构自嗨」的自认，检验复杂度举证责任 ｜ `callback`: Q72 ｜ `depth`: L2

**Q75.** 你说要删 X —— 但 X 当初是为解决什么问题建的？那个问题今天真的不存在了，还是只是你换了个方式绕过去？
> `intent`: 校验删除判断是否建立在问题消失的证据上 ｜ `callback`: Q72 ｜ `depth`: L2

**Q76.** 如果强行把九个模块压成五个，你会怎么合并？合并之后哪一个具体 failure 会回来？
> `intent`: 用合并代价检验模块边界的必要性 ｜ `callback`: Q71 ｜ `depth`: L2

**Q77.** 你自研的这些层里，哪一层其实 LangGraph 或某个成熟框架已经覆盖了，你们只是包了一层？
> `intent`: Build/Buy/Extend 追问，找自研的真实 Delta ｜ `callback`: Q71 ｜ `depth`: L2

**Q78.** Memory V2 的 typed contract 加 scope 约束 —— 如果只允许保留一个 scope 维度，你留哪一个，另一个靠什么替代？
> `intent`: 用「只留一个」压缩 scope 抽象，检验它是否真被需要 ｜ `callback`: — ｜ `depth`: L2

**Q79.** 你在 Q75 说 X 的问题已经不存在了 —— 那今天的判断是「当时该做但做错了」，还是「当时就不该做」？两个结论对应的架构责任完全不同。
> `intent`: 区分「实现错误」与「设计不该存在」，检验反思粒度 ｜ `callback`: Q75 ｜ `depth`: L3

**Q80.** 请给九个模块各写一个删除/合并条件 —— 哪个模块你写不出来？写不出来的那个为什么该继续留着？
> `intent`: 收口，逼出退出条件；写不出条件的模块即复杂度未举证 ｜ `callback`: Q72, Q76 ｜ `depth`: L3

## T09 — Knowledge / Retrieval 基础

**Q81.** 从一份文档进入系统，到用户点得到引用 —— 这中间经过了哪几个状态对象，分别由谁改变？
> `intent`: 建立文档到引用的状态链，检验是否真理解流转而非名词堆叠 ｜ `callback`: — ｜ `depth`: L1

**Q82.** 「Ready」这个状态是给谁看的？谁有权把它从没准备好改成准备好？
> `intent`: 追问 Readiness 的消费方与写权限归属 ｜ `callback`: — ｜ `depth`: L1

**Q83.** 一条引用（Citation）里到底存了什么？是文档 ID、chunk ID，还是字符区间？点进去靠什么定位？
> `intent`: 追引用的数据结构，检验可点击性是真实实现还是说法 ｜ `callback`: — ｜ `depth`: L1

**Q84.** 文档被更新之后，指向旧版本的引用会怎样？是失效、重定向到新版本，还是仍然可以点开旧内容？
> `intent`: 追版本与引用的耦合语义，检验更新是否被认真处理 ｜ `callback`: — ｜ `depth`: L2

**Q85.** 你如何证明「全案里没有这个信息」？是检索不到就断定不存在，还是有一层覆盖度判断？
> `intent`: 追问「否定性结论」的证据来源，检验是否用检索结果冒充全集判断 ｜ `callback`: Q83 ｜ `depth`: L2

**Q86.** Vector、BM25、Graph 三路结果怎么融合、怎么调权？权重是固定常量，还是随 query 变化？
> `intent`: 追融合与调权的真实机制 ｜ `callback`: — ｜ `depth`: L2

**Q87.** baseline-preserving fusion 保留了 baseline 的原始 rank —— 那被挤出 Top-K 的那条图候选，它的证据强度算到哪里去了？
> `intent`: 追晋升/挤出规则的分数去向，检验融合是否只是加权拼接 ｜ `callback`: Q86 ｜ `depth`: L2

**Q88.** 如果 chunk 切在了句子中间，用户点进引用看到的是完整那句，还是一个残句？你们怎么切、怎么补？
> `intent`: 追切分与引用展示的一致性，检验可点击性的表层之下 ｜ `callback`: Q83 ｜ `depth`: L2

**Q89.** 你在 Q85 说检索不到时会如何如何 —— 但如果引用指向的那一段恰好被删掉了，你 Q84 讲的「旧引用仍可用」还成立吗？
> `intent`: 收口，把否定判断与引用时效两条线交叉，逼出自洽性 ｜ `callback`: Q84, Q85 ｜ `depth`: L3

**Q90.** 这条链上的状态对象，你觉得哪一个是可以删掉的？删掉它之后哪一步会变得不可判定？
> `intent`: 收口，把删除思维施加到知识链上，检验状态对象的必要性 ｜ `callback`: Q81 ｜ `depth`: L3

## T10 — 工程基础

**Q91.** GIL 存在的情况下，为什么用线程跑多个 `requests` 请求仍然能提速，而 CPU 密集型任务用线程基本不加速？
> `intent`: GIL 的真实语义与释放时机 ｜ `callback`: — ｜ `depth`: L1

**Q92.** PostgreSQL READ COMMITTED 下，两个事务同时执行 `UPDATE t SET c = c + 1 WHERE id = 1`，会不会丢更新？为什么？
> `intent`: 隔离级别与丢失更新的成因 ｜ `callback`: — ｜ `depth`: L1

**Q93.** 一次 Tool 调用的 HTTP 请求超时了 —— 你能据此断定远端没有执行吗？请举一个不能断定的情况。
> `intent`: 超时的语义边界，检验是否把「本地超时」当「远端未发生」 ｜ `callback`: — ｜ `depth`: L1

**Q94.** 你在 Q86 说三路检索并行、超时就返回 —— `asyncio.gather` 到点取消，被取消的是本地 coroutine，远端那次检索请求真的停了吗？
> `intent`: 从项目机制桥接到 cancellation 语义，追取消是否等于终止 ｜ `callback`: Q86 ｜ `depth`: L2

**Q95.** 简历说 per-user config 在调用时注入 —— 如果用 ContextVar 存这个配置，`asyncio.create_task` 里读得到吗？丢进 `run_in_executor` 里呢？各为什么？
> `intent`: coroutine 上下文传播，检验并发下用户配置会不会串 ｜ `callback`: Q54 ｜ `depth`: L2

**Q96.** 如果失败重试三次的那个 Tool 是写操作，最坏的事态是什么？你靠什么让这次重试是安全的？
> `intent`: 重试放大与幂等语义 ｜ `callback`: Q93 ｜ `depth`: L2

**Q97.** `asyncio.CancelledError` 在 Python 3.8+ 继承自 `BaseException` 而不是 `Exception` —— 这对你写 `except Exception` 的清理逻辑意味着什么？
> `intent`: 异常层级语义，检验是否写过真正的取消安全清理 ｜ `callback`: — ｜ `depth`: L2

**Q98.** 查询条件固定为 `user_id = ? AND project_id = ?` 再按 `created_at DESC` 排前 20 条 —— 复合索引的列顺序你怎么定？为什么反过来会变差？
> `intent`: 复合索引的最左前缀与排序利用 ｜ `callback`: — ｜ `depth`: L2

**Q99.** Memory 是「调用前读取、回合后写入」—— 请描述一个多轮并发下能产生丢失更新的时序，并说明为什么 READ COMMITTED 挡不住它。
> `intent`: 收口，把并发基础落到候选人自己声称做过的 Memory 写入路径 ｜ `callback`: Q92, Q95 ｜ `depth`: L3

**Q100.** 你在 Q53 说路由这条 bullet 是你写的、并用回归测试固定了路由边界 —— 那个回归集里，「该 direct 却走了 ReAct」和「该 ReAct 却走了 direct」会被算成同一个错误吗？哪一个方向对你更致命，为什么？
> `intent`: 收口，把评测指标设计打穿到错误代价不对称性 ｜ `callback`: Q53 ｜ `depth`: L3
