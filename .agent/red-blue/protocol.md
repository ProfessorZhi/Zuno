# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法说明见 `docs/red-blue/README.md`；本目录只负责运行状态、上下文防火墙和机器可执行约束。

## 目标

Red / Blue 验证两件事：

1. Zuno 的 Project / Architecture / Module Part A 是否能够在真实业务与大厂面试式追问下保持完整因果；
2. 当前设计是否存在真正会改变 Architecture、Evidence、Ownership、Build/Buy 或 Simplification 决策的缺口。

它不负责把架构“辩得更复杂”。如果简单方案已经足够，Blue 应明确保留简单方案。

## 角色

### Controller

Controller 固定 Round manifest、切换上下文、推进状态、检查 source policy、保存 transcript/findings 和执行停止条件。Controller 不替 Red 设计答案，也不替 Blue 搜外部材料。

### Red

Red 从业务场景、简历 Claim、替代方案和故障窗口施压。一次只问一个主问题。优先验证：

- 业务目标与 baseline；
- Material / Knowledge readiness；
- Capability / Provider qualification；
- Candidate / Formal Business Fact；
- crash / late result / replan；
- timeout / external effect；
- continuous authorization；
- Build / Buy / Extend / Delete；
- Evidence / Measurement；
- Team / Personal Ownership。

Red 不以内部对象名、字段数量或状态机复杂度衡量攻击深度。如果追问不会改变任何决策，只会增加术语，结束该链。

### Blue

Blue closed-book。使用与 Red 相同的精确简历快照，只读取 manifest allowlist 内的 Zuno 文档。

Blue 优先从 Part A 的自然故事回答；被追到 Contract、State、Recovery、Security、Persistence 或 Evidence 后再进入 Part B / Part C / ADR / Evidence。

Blue 可以回答：简单方案足够、平台能力应复用、某机制应删除、需要 Architecture Revision、当前只有 Target、或证据不足。禁止用模型常识补齐 Zuno 未记录事实。

### Verifier

Verifier 是审计角色，不是第三个辩论方。它只检查：

- Blue 的关键事实是否有允许来源；
- 回答是否混淆 Current / Target / History / Unknown；
- Finding 是否真的会改变决策；
- Gap classification 是否合理；
- 是否应该继续同一攻击链。

Verifier 不生成“正确答案”，也不向 Blue 回流诊断。

## Context Firewall

```text
RED CONTEXT
  exact resume snapshot
  role / JD / interview stage
  attack-model.md
  approved interview calibration
  current public platform facts when Build/Buy is under test

BLUE CONTEXT
  exact same resume snapshot
  AGENTS.md
  docs/project/
  docs/architecture/
  docs/modules/
  docs/decisions/
  docs/evidence/
  allowed docs/governance/ facts

VERIFIER CONTEXT
  Red question + hidden intent
  Blue answer + source trace
  same canonical sources required to verify claims
  judge.md / verification rules
```

禁止：

```text
Red interview corpus ─X→ Blue
Red hidden intent     ─X→ Blue
Verifier diagnosis   ─X→ Blue during same chain
Blue external search ─X→ answer
Historical ideal QA  ─X→ Blue
Legacy Round answer  ─X→ Blue
```

## Round 启动

开始前固定：

1. Zuno base SHA；
2. exact resume snapshot：repository + commit SHA + path；
3. role / JD / interview stage；
4. mode；
5. Red calibration policy；
6. Blue allowlist；
7. scenario scope；
8. max turns / stop condition。

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

用户可以中途 intervention，但没有 `human-candidate` 执行模式。

## CHATGPT_AUTO

单一 ChatGPT conversation 内按程序性角色隔离运行：

```text
INIT
→ CLAIM_OR_SCENARIO_SELECTION
→ RED_ASK
→ BLUE_ANSWER
→ VERIFY_SOURCE_AND_DECISION_IMPACT
→ CONTINUE_CHAIN | NEXT_SCENARIO | CLOSE
```

同一 conversation 不是密码学隔离。CHATGPT_AUTO 适合快速发现 Gap；高严重度 Architecture / Evidence / Ownership Finding 不因 Red 与 Blue 同意就自动成立。

## AGENT_AUTO

Controller 为 Red、Blue 和 Verifier 创建独立 context。适合正式 Closed-book 验收与高严重度 Finding retest。

AGENT_AUTO 可以让 Red 在开始前读取批准的 interview corpus 或当前平台资料形成私有 pressure model。该内容不得进入 Blue。

两种模式都不得自动：

- 修改 Zuno Architecture；
- 修改简历；
- 创建业务实现；
- 用外部材料补齐 Blue；
- 把 Round Verdict 写成 Current Evidence。

## Turn 记录

每个 Turn 至少记录：

```text
turn_id
scenario_or_claim
attack_angle
red_question
red_hidden_intent
expected_evidence
blue_answer
blue_source_trace
verifier_result
finding_type
next_action
```

## 连续追问

Red 根据回答形状继续：

- 只有名词 → 回到实际输入、动作、Owner、失败结果；
- 有方案没有原因 → 追 baseline、约束、alternative、cost；
- 说“我们” → 追 Personal Ownership；
- 说“自研” → 追 Build / Buy / Extend；
- 说“恢复” → 注入 crash / duplicate / late result；
- 说“性能/高并发” → 追 workload、瓶颈和测量；
- 说“效果更好” → 追 baseline、dataset、metric、ablation、failure case；
- 说“权限” → 追长任务权限变化；
- 说“重试” → 追 idempotency 和 Unknown external outcome；
- Current / Target 混淆 → 要求重新分层；
- 已证明简单方案足够 → 停止增加复杂度。

## 停止条件

单链在以下情况结束：

- Blue 已覆盖事实、原因、机制、故障、Trade-off、Evidence 与 Ownership；
- 已形成明确 Finding，继续追问只重复同一缺口；
- 允许文档没有更多信息；
- 问题越出目标岗位或业务范围；
- 后续追问只会产生 trivia 而不改变决策。

## Round 产物

长期归档只要求：

```text
manifest.yaml
transcript.md
findings.md
```

`findings.md` 对重复问题去重，并记录 severity、decision impact、source support、evidence needed 和 retest scenario。

Finding 典型分类：

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

Round 完成后归档到 `docs/red-blue/rounds/<round-id>/`。旧手工/早期自动 Round 只在 `docs/red-blue/archive/legacy/` 保存。

Findings 必须通过独立任务写回 Project / Architecture / Modules / Decisions / Evidence / Resume；历史 Round 本身不拥有 Architecture Truth。