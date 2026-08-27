# Zuno Red / Blue Interview Harness

`.agent/red-blue/` 是 Zuno 的 **Interview / Architecture Stress-Test 运行中心**。它只拥有“怎么运行 Red / Blue”，不拥有 Zuno 的项目事实、Target Architecture、Module Truth、Current Evidence，也不保存候选人的长期简历正文。

一句话定义：

> Red 从简历 Claim 出发，用真实大厂面试的追问方式持续施压；Blue 只能依赖同一份简历快照和 Zuno Canonical Docs 回答；Judge 只判断回答是否经得住追问并记录 Gap，不能替 Blue 补答案。

## 目录

```text
.agent/red-blue/
├── README.md
├── current.md             当前 Round 指针；main 默认 no-active
├── protocol.md            Red / Blue / Judge 与两种运行模式
├── attack-model.md        Claim-driven 攻击逻辑与面试官追问内核
├── judge.md               判定规则、Gap taxonomy、通过条件
└── templates/
    ├── round.md           Round manifest 模板
    └── turn.md            单轮问答 / 裁决模板
```

历史记录不放这里。Round 完成后，原始 Transcript、Judgment 和 Gap Snapshot 进入 `docs/maintenance/history/red-blue/`；人类可读流程见 `docs/maintenance/red-blue/README.md`。

## 两种正式运行模式

### ChatGPT Duel

适合聊天中直接跑 Red / Blue 对攻。Controller 按 `Red → Blue → Judge → Red follow-up` 推进，一次只暴露一个主问题。Blue 不得读取 Red 的面经语料、攻击意图、标准答案或 Judge 内部评语。

单一聊天模型里的隔离属于**程序性隔离**，不是密码学隔离；高保真验收时优先使用独立上下文 / 子 Agent。

### Autonomous Agent

适合 Agent 自主完成一整轮压力测试。Controller 为 Red、Blue、Judge 创建独立 context manifest：

```text
Red context   = resume snapshot + target role/JD + Red kernel + optional interview calibration sources
Blue context  = same resume snapshot + allowed Zuno canonical docs only
Judge context = question + answer + resume snapshot + allowed canonical docs + Red attack intent
```

Controller 负责状态推进和归档，角色之间禁止共享未授权上下文。

另外可以运行 `human-candidate`：Red 直接问用户，用户本人作答，Judge 只在用户要求复盘时介入。

## Resume-first，而不是题库-first

Red 不维护一个固定 500 题列表。每一轮先锁定**精确简历快照**，再从简历抽取高风险 Claim，例如：

- “从 0 到 1”“负责架构”“自研”“主导”；
- “高并发”“生产级”“企业级”“准确率提升”“成本下降”等强 Claim；
- RAG、GraphRAG、Multi-Agent、LangGraph、MCP、Tool Calling、Memory、Eval；
- Retry、幂等、事务、缓存、队列、权限、恢复、部署、性能等工程 Claim；
- 团队 / 导师成果与个人 Ownership 可能混淆的表述。

然后 Red 用 `attack-model.md` 把这些 Claim 展开成连续攻击链，而不是随机抽题。

## Red 的“内核”和面经语料是什么关系

默认 Round 可以只依赖：

```text
Red interviewer kernel
+ exact resume snapshot
+ target role / interview stage
```

为了让这个 kernel 保持接近真实市场问题，可以在 Round 前做 `calibrated` 预热。校准优先级：

1. `ProfessorZhi/internship-work` 中用户本人真实面试记录、复盘和简历定制材料；
2. `ProfessorZhi/interview-notes` 中同岗位真实公开面经；
3. `ProfessorZhi/onboard-anything` 中真实面经、八股和高质量工程材料；
4. `ProfessorZhi/xiaolin-interview-notes` 作为结构化补充并去重；
5. 模型自身的 interviewer knowledge。

这些外部材料只用来**校准面试官会验证什么风险、怎样连续追问**，不是让 Red 机械背题，也绝不能进入 Blue 上下文。

## Blue 的 Closed-book Source Profile

Blue 默认只允许：

```text
exact resume snapshot
AGENTS.md

docs/project/
docs/architecture/
docs/modules/
docs/decisions/
docs/evidence/
docs/governance/project-fact-provenance.md
```

Blue 应优先从 Project / Architecture / Module 的 **Part A 故事**组织回答；当 Red 继续追 Contract、State、Crash、Concurrency、Security、Persistence 时才下钻 Part B / Part C / ADR / Evidence。

Blue 不允许临时读取：

- `internship-work` 的 QA / 标准答案 / 复盘；
- `interview-notes`；
- `onboard-anything`；
- `xiaolin-interview-notes`；
- 外部博客、论文、搜索结果；
- Red 的 hidden intent、counterexample 或 Judge 评语。

如果 Canonical Docs 和简历不足以回答，正确结果是 Gap，不是偷偷补知识。

## 角色边界

Red 只负责攻击，不负责修文档；Blue 只负责在允许语料内回答，不负责搜索外部答案；Judge 只负责判定，不负责把一个失败答案润色成通过答案。

正式修复必须另开动作：

```text
Round Gap
→ classify Writing / Architecture / Evidence / Ownership / Measurement
→ independent fix
→ merge
→ 用不同问法 Red Retest
```

## Skill 导出边界

未来最适合导成 Skill 的内容是：`protocol.md`、`attack-model.md`、`judge.md` 和 templates。不要把以下内容打包进通用 Skill：

- `current.md`；
- Zuno 当前 Architecture Truth；
- 具体简历正文；
- `docs/maintenance/history/red-blue/` 历史记录；
- 某一轮临时问题和标准答案。

Skill 应封装方法，运行时再读取目标仓库和候选人输入。