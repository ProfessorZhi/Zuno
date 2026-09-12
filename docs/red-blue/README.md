# Zuno Red / Blue Architecture Review

`docs/red-blue/` 保存 Zuno 的对抗性评审方法和已经结束的 Round。它的目的不是生成更多架构术语，也不是让两个 AI 互相证明当前设计正确，而是发现 Project、Architecture 和 Module Part A 在正常写作与普通 Review 中没有暴露出来的缺口。

Red / Blue 不拥有 Project History、Target Architecture、Module Truth 或 Current Evidence。它只能提出问题、反例和 Findings；正式修改仍要回到对应 Owner。

## 为什么独立成一级目录

Red / Blue 已经有自己的输入、角色、上下文边界、Round 生命周期、批次策略、停止条件和归档结果。把它塞进 `maintenance/` 会让读者误以为它只是仓库维护说明。

它与主文档的关系是：

```text
Project / Architecture / Modules Part A
        ↓
先达到独立可读、完整、自洽
        ↓
Red / Blue adversarial review
        ↓
Narrative / Architecture / Evidence / Ownership / Simplification Findings
        ↓
独立修复任务
        ↓
回到对应 Canonical Owner
        ↓
换场景重新测试
```

第一次阅读 Zuno 时不需要读这里。

## 批量交互是默认模式

新的正式 Round 以 **batch** 为基本交互单位，默认 `batch_size: 100`。

一批问题不是把题库随机切 100 条。Red 先从简历 Claim、真实业务场景、已知故障窗口和面经 pressure distribution 分配问题预算；同一批可以同时覆盖 Ownership、Project Reality、Agent/RAG、架构、恢复、安全、Build/Buy、Eval 和基础原理。问题在 Red 输出时冻结，随后 Blue 对整批逐题作答，Verifier 再逐题核对。基于回答形成的新追问进入下一批。

```text
Batch N
  Red 生成并冻结问题
  → 立即归档 Red batch
  → Blue 逐题回答
  → 立即归档 Blue batch
  → Verifier 逐题审计
  → 立即归档 verifier results
  → 重新分配下一批攻击权重
  → Batch N+1 | Close
```

这样既保留一次 100 问的广度压力，也避免把后续追问提前假装成已经知道 Blue 会怎样回答。

## 两种正式模式

只保留两种执行模式：

### CHATGPT_AUTO

适合在一个 ChatGPT 对话中快速批量压力测试。

```text
Controller
→ Red 生成一个 batch（默认 100 问）
→ Blue closed-book 逐题回答完整 batch
→ Verifier 逐题检查来源与 decision impact
→ Controller 根据结果重分配下一批攻击预算
→ ...
→ Round close
```

同一对话只能做到程序性上下文隔离。Red 的 external interview calibration 和显式 hidden attack metadata 不得作为 Blue 的回答依据；严重 Architecture / Evidence Finding 不因两个角色达成一致就自动成立。

CHATGPT_AUTO 从 Round 启动开始就必须把每个 batch 的可观察过程写入 GitHub transcript，不能只在结束时保留一个聊天摘要。

### AGENT_AUTO

适合正式 Closed-book 验收。Controller 为 Red、Blue 和 Verifier 建立独立上下文。

```text
Red context
  resume / role / JD
  business scenarios
  approved interview calibration
  prior batch results
  current public platform facts when testing Build/Buy

Blue context
  same resume snapshot
  Project / Architecture / Modules
  Decisions / Evidence
  allowed Governance facts

Verifier
  full batch questions + answers + source traces
  accepted canonical docs
```

AGENT_AUTO 同样必须把每个 Agent 的可观察输入输出、显式协议元数据、Controller transition 和用户 intervention 按时间顺序归档。Agent 使用独立 context 不意味着过程可以只留最后 verdict。

这里的“完整过程”指**可观察 role I/O 和控制事件**。模型私有 chain-of-thought 不属于可观察归档内容，不要求、也不得伪造；协议显式生成的 `red_hidden_intent`、`expected_evidence`、`source_trace` 和 `verifier_result` 则属于必须归档的 Round 数据。

用户可以随时打断、修改范围或亲自回答，但这属于 intervention，不构成第三种 `human-candidate` 模式；intervention 本身也进入 transcript。

## Red 的工作：用问题预算攻击业务假设

Red 每个 batch 应覆盖当前最高风险的若干 Claim，而不是追求平均覆盖模块。

优先场景包括：

- 100 份材料中关键扫描件仍未 OCR，但系统已经可以生成流畅答案；
- 两个 Provider 都能返回相同 JSON，但专业语义、案件范围或资格不同；
- 专业人员修改机器结果后，新证据又进入；
- 新 Plan 已产生，旧分支随后返回高质量结果；
- 外围法院系统 POST timeout，不知道现实动作是否发生；
- 长任务开始时有权限，执行外发时权限已经撤销；
- GraphRAG / Reflection / Multi-Agent / Native Runtime 可以加入，但没有 baseline 或 ablation 证明收益；
- WorkBuddy / Dify / LangGraph 已经能承担通用能力，Zuno 是否仍在重复造基础设施；
- 简历中的“主导、从零、自研、生产级、提升 X%”是否有真实个人证据。

一个高价值 Red 问题应尽量包含：

```text
stakeholder goal
→ concrete stimulus
→ current environment
→ expected response
→ unacceptable failure consequence
→ substitute / simpler baseline
→ evidence needed
```

100 问不意味着 100 个互不相关主题。同一 Claim 可以从业务因果一路压到状态、故障、基础原理、Evidence 和个人 Ownership。上一批已经稳定通过的链应降权，问题预算转向仍不确定的地方。

## Blue 的工作：逐题保护事实，不保护现有架构

Blue 只能使用 Round manifest 允许的 Zuno 文档和同一份简历快照。它必须对 batch 中每道问题独立作答并保留 source trace，不能把 100 问合成一段泛化项目介绍。

Blue 优先从 Part A 的因果故事回答；被追到 Contract、State、Recovery、Security、Persistence 或 Evidence 时才进入 Part B / Part C / ADR / Evidence。

Blue 可以明确回答：

- 简单 RAG 已经足够，不需要新增机制；
- 某个 Framework Capability 应直接复用；
- 当前 Target 能处理该场景；
- 当前文档解释不清，属于 Narrative Gap；
- 当前 Architecture 对反例没有闭环，需要 Architecture Revision；
- 当前只有 Target，没有 Current Evidence；
- 某个复杂机制应被关闭或删除；
- 个人 Ownership 没有证据支持该说法。

Blue 不应为了“赢”而使用模型常识补齐 Zuno 未记录的事实。

## Transcript 是一等 Round 产物

Round 不是只保存最终 findings。无论 CHATGPT_AUTO 还是 AGENT_AUTO，都必须从启动起 append-only 保存完整可观察过程。

至少保存：

```text
manifest snapshot
calibration source inventory
controller transitions
user interventions
每个 batch 的 question_count 与问题全文
每题 red_hidden_intent / expected_evidence
每题 Blue answer / source trace
每题 verifier verdict / severity / gap / next_action
batch reweighting
round close event
```

如果一个 transcript 过大，可以按 batch 分片：

```text
transcript.md              chronological index + controller/user events
transcript-batch-001.md    Red / Blue / Verifier full batch record
transcript-batch-002.md
...
```

manifest 必须列出所有分片。任何摘要、最终题单或 `findings.md` 都不能替代这些原始可观察记录。

## Round 输出

新的 Round 至少固定：

```text
round_id
zuno_base_sha
resume_snapshot
role / JD / interview stage
mode: CHATGPT_AUTO | AGENT_AUTO
scenario_scope
blue_allowlist
batch_size: 100
max_batches / stop condition
transcript_policy: full-observable-role-io
archive_live: true
```

长期产物至少包括：

```text
manifest.yaml
transcript.md
transcript-batch-*.md   optional shards when needed
findings.md
```

`findings.md` 只保存去重后的 Findings、severity、decision impact、证据需求和 retest scenario。它故意比 transcript 短，但不能删除 transcript 里的失败尝试、重复问法或用户 intervention。

Finding 分类优先使用：

```text
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
TRADEOFF_GAP
EVIDENCE_GAP
IMPLEMENTATION_GAP
OWNERSHIP_GAP
MEASUREMENT_GAP
PROJECT_REALITY_GAP
RESUME_CLAIM_RISK
SIMPLIFICATION_OPPORTUNITY
```

Red / Blue Round 本身不是 Current Evidence，也不是 Architecture Decision。

## 防止两个 AI 自嗨

同一模型模拟 Red 和 Blue 存在共享偏差，所以采用五个约束：

1. **Scenario-first**：问题必须绑定业务场景、简历 Claim 或具体失败，不以名词深度衡量质量。
2. **Source trace**：Blue 的关键事实必须能回到允许来源；模型共识不能替代证据。
3. **Decision impact**：Finding 必须说明它会改变什么决策；不会改变任何设计的 trivia 不进入修复队列。
4. **Independent acceptance**：Architecture / Evidence / Ownership 的重大结论必须进入独立任务，必要时用 AGENT_AUTO、代码、测试或外部事实复核。
5. **Full transcript**：不能只保存“两个 AI 最后同意了什么”；完整可观察问答过程必须留在 GitHub，便于以后独立重审。

Round 的成功标准不是 FAIL 越多、题量越大越好，而是批量压力能够发现真正改变项目可信度、可读性、架构闭环或复杂度决策的问题。

## 目录

```text
docs/red-blue/
├── README.md
├── rounds/          新式 CHATGPT_AUTO / AGENT_AUTO Round
│   ├── README.md
│   └── <round-id>/
│       ├── manifest.yaml
│       ├── transcript.md
│       ├── transcript-batch-001.md   # optional when sharded
│       ├── transcript-batch-002.md
│       └── findings.md
└── archive/
    └── legacy/      旧的 manual / early automated Round，只供历史复盘
```

正式机器运行协议和临时 active state 仍由 `.agent/red-blue/` 管理。新 Round 的长期归档位于 [`rounds/`](./rounds/README.md)。

`archive/legacy/` 中的手工 Round 已退出正式模式。它们可以解释过去如何审查，但不能作为今天的 Architecture Truth 或面试标准答案。