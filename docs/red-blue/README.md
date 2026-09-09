# Zuno Red / Blue Architecture Review

`docs/red-blue/` 保存 Zuno 的对抗性评审方法和已经结束的 Round。它的目的不是生成更多架构术语，也不是让两个 AI 互相证明当前设计正确，而是发现 Project、Architecture 和 Module Part A 在正常写作与普通 Review 中没有暴露出来的缺口。

Red / Blue 不拥有 Project History、Target Architecture、Module Truth 或 Current Evidence。它只能提出问题、反例和 Findings；正式修改仍要回到对应 Owner。

## 为什么独立成一级目录

Red / Blue 已经有自己的输入、角色、上下文边界、Round 生命周期、停止条件和归档结果。把它塞进 `maintenance/` 会让读者误以为它只是仓库维护说明。

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

## 两种正式模式

只保留两种执行模式：

### CHATGPT_AUTO

适合在一个 ChatGPT 对话中快速连续压力测试。

```text
Controller
→ Red 根据业务场景提出一个主问题
→ Blue closed-book 回答
→ Controller 检查来源和是否出现新信息
→ Red 沿同一风险继续追问或换场景
→ ...
→ Round close
```

同一对话只能做到程序性上下文隔离。Red 的 hidden attack intent、外部面经和校准材料不得作为 Blue 的回答依据；严重 Architecture / Evidence Finding 不因两个角色达成一致就自动成立。

### AGENT_AUTO

适合正式 Closed-book 验收。Controller 为 Red 和 Blue 建立独立上下文，必要时使用独立 verifier/auditor 检查来源和 verdict，但 verifier 不参与架构辩论，也不为 Blue 补答案。

```text
Red context
  resume / role / JD
  business scenarios
  approved interview calibration
  current public platform facts when testing Build/Buy

Blue context
  same resume snapshot
  Project / Architecture / Modules
  Decisions / Evidence
  allowed Governance facts

Verifier
  question + answer + source trace
  accepted canonical docs
```

AGENT_AUTO 适合复测 CHATGPT_AUTO 发现的高严重度问题，或做正式文档验收。

用户可以随时打断、修改范围或亲自回答，但这属于 intervention，不构成第三种 `human-candidate` 模式。

## Red 的工作：攻击业务假设，不攻击名词

Red 一次只验证一个主要风险。问题应该来自真实任务或替代方案，而不是对象名词表。

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

如果追问只会增加字段、对象或状态名称，却不会改变任何设计决策，Red 应停止该链。

## Blue 的工作：保护项目目标，不保护现有架构

Blue 只能使用 Round manifest 允许的 Zuno 文档和同一份简历快照。它必须优先从 Part A 的因果故事回答；被追到 Contract、State、Recovery、Security、Persistence 或 Evidence 时才进入 Part B / Part C / ADR / Evidence。

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

## Round 输出

新的 Round 不再保存三角色长篇自我辩论。每轮至少固定：

```text
round_id
zuno_base_sha
resume_snapshot
role / JD / interview stage
mode: CHATGPT_AUTO | AGENT_AUTO
scenario_scope
blue_allowlist
max_turns / stop condition
```

结束后只保留两个主要产物：

```text
transcript.md   实际问题与回答，保留 source trace
findings.md     去重后的 Findings、severity、decision impact、证据需求和 retest scenario
```

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

同一模型模拟 Red 和 Blue 存在共享偏差，所以采用四个约束：

1. **Scenario-first**：问题必须绑定业务场景或具体失败，不以名词深度衡量质量。
2. **Source trace**：Blue 的关键事实必须能回到允许来源；模型共识不能替代证据。
3. **Decision impact**：Finding 必须说明它会改变什么决策；不会改变任何设计的 trivia 不进入修复队列。
4. **Independent acceptance**：Architecture / Evidence / Ownership 的重大结论必须进入独立任务，必要时用 AGENT_AUTO、代码、测试或外部事实复核。

Round 的成功标准不是 FAIL 越多越好，而是发现少量真正改变项目可信度、可读性、架构闭环或复杂度决策的问题。

## 目录

```text
docs/red-blue/
├── README.md
├── rounds/          新式 CHATGPT_AUTO / AGENT_AUTO Round
│   ├── README.md
│   └── <round-id>/
│       ├── manifest.yaml
│       ├── transcript.md
│       └── findings.md
└── archive/
    └── legacy/      旧的 manual / early automated Round，只供历史复盘
```

正式机器运行协议和临时 active state 仍由 `.agent/red-blue/` 管理。新 Round 的长期归档位于 [`rounds/`](./rounds/README.md)。

`archive/legacy/` 中的手工 Round 已退出正式模式。它们可以解释过去如何审查，但不能作为今天的 Architecture Truth 或面试标准答案。