# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法说明见 `docs/red-blue/README.md`；本目录只负责运行状态、上下文防火墙和机器可执行约束。

## 目标

Red / Blue 验证两件事：

1. Zuno 的 Project / Architecture / Module Part A 是否能够在真实业务与大厂面试式追问下保持完整因果；
2. 当前设计是否存在真正会改变 Architecture、Evidence、Ownership、Build/Buy 或 Simplification 决策的缺口。

它不负责把架构“辩得更复杂”。如果简单方案已经足够，Blue 应明确保留简单方案。

## 角色

### Controller

Controller 固定 Round manifest、切换上下文、推进批次状态、检查 source policy、保存 transcript/findings 和执行停止条件。Controller 不替 Red 设计答案，也不替 Blue 搜外部材料。

### Red

Red 从业务场景、简历 Claim、替代方案和故障窗口施压。**正式 Round 以 batch 为基本交互单位**：每个 batch 生成一组高信息量问题，默认 `batch_size: 100`；下一批问题必须根据上一批 Blue 回答与 Verifier 结果重新分配攻击权重，而不是机械复制题库。

优先验证：

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

同一批次可以覆盖多个高风险 Claim，但每道问题必须能回到简历 Claim、岗位要求、真实业务场景或上一批暴露出的风险。Red 不以内部对象名、字段数量或状态机复杂度衡量攻击深度。

### Blue

Blue closed-book。使用与 Red 相同的精确简历快照，只读取 manifest allowlist 内的 Zuno 文档。

Blue 对整个 batch 逐题作答，每道题都必须保留独立 source trace；不能用后一题答案覆盖前一题，也不能把一批问题压成一个泛化总结。Blue 优先从 Part A 的自然故事回答；被追到 Contract、State、Recovery、Security、Persistence 或 Evidence 后再进入 Part B / Part C / ADR / Evidence。

Blue 可以回答：简单方案足够、平台能力应复用、某机制应删除、需要 Architecture Revision、当前只有 Target、或证据不足。禁止用模型常识补齐 Zuno 未记录事实。

### Verifier

Verifier 是审计角色，不是第三个辩论方。它对 batch 内每道题逐题检查：

- Blue 的关键事实是否有允许来源；
- 回答是否混淆 Current / Target / History / Unknown；
- Finding 是否真的会改变决策；
- Gap classification 是否合理；
- 下一批是否应继续同一风险、换攻击角度或停止该链。

Verifier 不生成“正确答案”，也不向 Blue 回流诊断。

## Context Firewall

```text
RED CONTEXT
  exact resume snapshot
  role / JD / interview stage
  attack-model.md
  approved interview calibration
  prior batch Blue answers + verifier results
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
  Red batch questions + explicit attack metadata
  Blue batch answers + source traces
  same canonical sources required to verify claims
  judge.md / verification rules
```

禁止：

```text
Red interview corpus ─X→ Blue
Red explicit hidden intent ─X→ Blue before answering
Verifier diagnosis   ─X→ Blue during same batch
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
8. `batch_size`，默认 100；
9. `max_batches` / stop condition；
10. transcript policy，默认 `full-observable-role-io`。

只允许：

```text
CHATGPT_AUTO
AGENT_AUTO
```

用户可以中途 intervention，但没有 `human-candidate` 执行模式。

## Batch 执行模型

正式交互顺序为：

```text
INIT
→ CLAIM_OR_SCENARIO_SELECTION
→ RED_BATCH_GENERATE (default 100 questions)
→ ARCHIVE_RED_BATCH
→ BLUE_BATCH_ANSWER
→ ARCHIVE_BLUE_BATCH
→ VERIFY_EACH_QUESTION
→ ARCHIVE_VERIFIER_RESULTS
→ REWEIGHT_ATTACKS
→ NEXT_BATCH | CLOSE
```

一个 batch 内的问题在 Red 输出时冻结。Blue 回答期间不得由 Red 插入新的追问；基于回答产生的新问题进入下一批。这样既保留批量压力测试，又能让后续批次真正根据上一批暴露的风险演进。

## CHATGPT_AUTO

单一 ChatGPT conversation 内按程序性角色隔离运行。每个 batch 的 Red 输出、Blue 输出、Verifier 输出、Controller transition 和用户 intervention 都必须同步写入 Round `transcript.md`，不能等 Round 结束后凭摘要重建。

同一 conversation 不是密码学隔离。CHATGPT_AUTO 适合快速发现 Gap；高严重度 Architecture / Evidence / Ownership Finding 不因 Red 与 Blue 同意就自动成立。

## AGENT_AUTO

Controller 为 Red、Blue 和 Verifier 创建独立 context。适合正式 Closed-book 验收与高严重度 Finding retest。

AGENT_AUTO 可以让 Red 在开始前读取批准的 interview corpus 或当前平台资料形成私有 pressure model。该内容不得进入 Blue。Controller 必须把每个 Agent 的**可观察输入输出、显式攻击元数据、source trace、verdict、工具/控制事件摘要和用户 intervention**按发生顺序写入 `transcript.md`。

所谓“完整过程归档”指可观察的角色 I/O 与控制事件，不要求也不得伪造或导出模型私有 chain-of-thought。Red 的 `red_hidden_intent` 是协议要求显式生成并归档的攻击元数据，不等同于模型内部推理轨迹。

两种模式都不得自动：

- 修改 Zuno Architecture；
- 修改简历；
- 创建业务实现；
- 用外部材料补齐 Blue；
- 把 Round Verdict 写成 Current Evidence。

## Transcript：必须 append-only 保留完整可观察过程

每个 Round 从启动开始就创建 `transcript.md`，并采用 append-only 方式记录。至少包含：

```text
round init / manifest snapshot
calibration source inventory (Red only, 不向 Blue 暴露正文)
controller transitions
user interventions
batch_id / question_count
for each question:
  question_id
  scenario_or_claim
  attack_angle
  red_question
  red_hidden_intent (explicit attack metadata)
  expected_evidence
  blue_answer
  blue_source_trace
  verifier_result
  finding_type
  next_action
batch summary / attack reweighting
round close event
```

禁止只保存：最终问题清单、Blue 总结、Verifier 汇总、findings 或聊天摘要。`findings.md` 可以去重，但 `transcript.md` 不得因为去重而删除原始问答。

如果 GitHub 单文件大小成为实际限制，可以把 transcript 按 batch 分片：

```text
transcript.md              # chronological index + controller/user events
transcript-batch-001.md
transcript-batch-002.md
...
```

但 manifest 必须列出全部分片，且任何模式都不能只保存最终 Findings。

## Batch 记录

每个 batch 至少记录：

```text
batch_id
question_count
questions[]
answers[]
source_traces[]
verifier_results[]
attack_reweighting
next_batch_focus
```

每道题的最小字段沿用：

```text
question_id
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

## 批次间连续追问

Red 根据上一批回答形状调整下一批：

- 只有名词 → 下一批增加实际输入、动作、Owner、失败结果；
- 有方案没有原因 → 增加 baseline、约束、alternative、cost；
- 说“我们” → 增加 Personal Ownership；
- 说“自研” → 增加 Build / Buy / Extend；
- 说“恢复” → 注入 crash / duplicate / late result；
- 说“性能/高并发” → 追 workload、瓶颈和测量；
- 说“效果更好” → 追 baseline、dataset、metric、ablation、failure case；
- 说“权限” → 追长任务权限变化；
- 说“重试” → 追 idempotency 和 Unknown external outcome；
- Current / Target 混淆 → 要求重新分层；
- 已证明简单方案足够 → 降低该链权重，把问题预算转给其他未验证 Claim。

## 停止条件

Round 在以下条件之一满足时结束：

- 达到 `max_batches`；
- 目标 Claim / scenario 已被足够覆盖；
- 已形成稳定高严重度 Finding，继续批量追问只会重复；
- 允许文档没有更多信息；
- 后续问题越出目标岗位或业务范围；
- 下一批只会产生 trivia 而不改变决策；
- 用户 intervention 要求结束。

## Round 产物

长期归档至少要求：

```text
manifest.yaml
transcript.md              # 完整可观察过程；必要时索引分片
transcript-batch-*.md      # 可选分片；使用时必须全部列入 manifest
findings.md
```

`findings.md` 对重复问题去重，并记录 severity、decision impact、source support、evidence needed 和 retest scenario；它不能替代 transcript。

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