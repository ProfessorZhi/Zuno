# Workflow Retrospective — rb-2026-09-14-iterative-018

status: COMPLETE
change_effective_scope: NEXT_ROUND_ONLY

## Resume Builder Reflection

### Worked

- 简历从“模块/框架清单”变成了三个可深挖工程线程：Tool/MCP、GraphRAG、Context/Memory。
- GraphRAG 没再把 `0.80 → 1.00` 当 headline，而是写 regression → ranking fix → 5-query scope；Red 后续能自然追到 threshold / holdout / latency。
- Tool 不是只写“接入 MCP”，而是能沿 Agent-as-Tool → direct Tool binding → config injection → route hardening 深挖。
- Memory 两条分别覆盖 foundation 与 readback boundary，能够引出 scope / approval / provenance，而不是泛写“做了长期记忆”。

### Needs change

- 项目简介仍主要是历史参与面，尚未给“今天 Zuno 已演化成什么”留自然入口；导致 Blue 被追 current architecture 时有时仍停在个人历史实现。
- 以后 Resume Builder 可以在面试准备材料中额外生成 `history-current bridge`，但不把它塞进投递简历正文。

resume_builder_change: 为每个强 bullet 生成内部 interview handle：`historical_owned_delta / current_project_evolution / target_boundary`，供 Blue Skill 使用，不暴露给 blind Red。

## Red Skill Reflection

### Worked

- Wave 1 Pressure Suite 覆盖足够深，能把 Tool、retrieval、Memory、topology、evidence 和 fundamentals 打通。
- Wave 2 是真正从 Blue Wave 1 长出来的：并发隔离未证明 → 追 middleware state；threshold heuristic → 追 sweep/holdout；Memory APPROVED → 追 authority/TOCTOU；Single Agent → 追 Domain state / late result / Supervisor bottleneck。
- Multi-Agent 没被预设成正确答案，能够攻击 Tool / Subgraph / Specialist / Generic Host 的边界。

### Needs change

- 当前 `attack-model.md` 把 live turn-by-turn 当唯一正式执行方式，不适合自动 Round。
- `100-question Pressure Suite` 适合作为离线覆盖库，但本轮为了纠正执行模型让 Blue 全答了 100 问，信息利用率不够高。下一轮 Batch Duel 不应机械消费全部 Pressure Suite。
- Batch Red 需要专门的 wave selection policy：第一波按 Resume 选 20–40 个高信息量问题，第二波只从 Blue 缺口生成 10–30 个 follow-up；100 问继续只做 coverage audit。

red_skill_change: 增加 `BATCH_DUEL` conversation mode，与 `LIVE_INTERVIEW` 并存；Batch Wave 2 必须显式引用 Wave 1 observable answer handles。

## Blue Skill Reflection

### Worked

- Evidence discipline 很好：能主动说 5-query、无 holdout、无 ablation、Pilot ≠ Production、historical ≠ Target。
- 实现深度明显提高：能回答 candidate group、baseline rank、graph signal、MemoryScope 字段、review decision、ContextOrchestrator，而不是只讲框架。
- 第二波对架构开放：没有为了“赢 Red”硬说 Multi-Agent 已实现，而是区分 Tool / Subgraph / Specialist / controller+workers。

### Needs change

- Blue Wave 1 有明显“读 Evidence memo”的语言，例如频繁说 `canonical evidence / PF-xxx / current evidence`。Artifact 可以保留 source support，但 `spoken_answer` 应更像真实候选人口语。
- 更重要的是 **历史 Ownership 与当前项目架构的模式切换** 不够敏捷：当 Red 从“你 4 月做了什么”转向“今天这条链该怎么设计”时，Blue 有几处继续以历史 InMemory/Tool route 为中心，遗漏了 main 已存在的 `ToolInvocationGateway`、DatabaseMemoryStore 等 Current surface。
- Blue 需要先判断当前问题属于：`HISTORICAL_OWNERSHIP / CURRENT_ARCHITECTURE / TARGET_DESIGN / FUNDAMENTAL`，再选择允许的 source 和回答口径。

blue_skill_change: 新增 mode-switch policy；批量 artifact 将每题拆成 `spoken_answer` 与 `source_support/boundary`，禁止把 source trace 念进回答。

## Harness Reflection

### Major failure found

原协议把自动化 Round 设计成 `RED_TURN -> BLUE_TURN -> ...`，隐含要求用户在聊天里逐题参与。用户明确纠正：自动 Round 应由 Red/Blue 自己在 GitHub 批量对攻，不应把用户当候选人逐题等待回答。

classification: HARNESS_GAP

### Corrected execution shape

```text
Frozen Resume
→ Frozen Red Plan / Pressure Suite
→ RED_WAVE_1 batch
→ commit
→ BLUE_WAVE_1 batch
→ commit
→ RED_WAVE_2 reads Blue Wave 1 and generates targeted batch
→ commit
→ BLUE_WAVE_2 batch
→ commit
→ Red Evaluation
→ Blue Reflection
→ Retrospective / Improvement
```

适应性仍然存在，只是从 per-question adaptation 改成 per-wave adaptation。Red Wave 2 不能在 Blue Wave 1 之前预写。

### Future artifact shape

不要长期新增 `02b / 03b` 临时文件。下一轮固定：

- `02_red_questions.md` 内含 Plan + Pressure Suite + Red Wave 1 + Red Wave 2；
- `03_blue_answers.md` 内含 Blue Wave 1 + Blue Wave 2；
- transcript 记录每个 wave 的 input HEAD / output commit。

### Modes

- `BATCH_DUEL`：CHATGPT_AUTO 默认，用于自动架构压力测试和简历迭代；
- `LIVE_INTERVIEW`：只有用户明确要求真人逐题模拟时使用；
- AGENT_AUTO 可在两种 execution mode 下使用 physical context isolation。

harness_change: 正式修改 protocol/system/templates/tests，使 automated default = BATCH_DUEL，同时保留 LIVE_INTERVIEW optional。

## Architecture-learning Reflection

本轮证明 Red/Blue 的目的不能是“守住当前架构”。有效的压力应该允许三种结果：

1. Current / Target 已经解决问题，只需要 Narrative / Blue Skill 跟上；
2. Target 正确但 Current 没实现，进入 Implementation Gap；
3. Authority / State / Recovery 本身缺语义，才进入 Architecture Gap。

Multi-Agent 也按同样规则处理。它不是目标答案，而是 execution topology challenger。要进入默认路径，必须相对 Single Agent / Subgraph / controller+workers / Generic Host baseline 证明 Specialist autonomy 的质量、隔离、恢复或成本收益。

## Retest targets for next round

- Batch Wave 2 是否真正引用 Wave 1 缺口，而不是第二套预写题库；
- Blue 是否能在 Historical → Current → Target 之间自然切换；
- 当前 ToolInvocationGateway / Memory DatabaseStore 等 Current 能否在回答 current architecture 时出现，但不被冒充为历史个人贡献；
- Multi-Agent challenger 是否用 benchmark / failure scenario 推导，而不是架构偏好；
- Red 是否能把新的 Architecture Gap 与已经存在的 Current/Target 区分开。
