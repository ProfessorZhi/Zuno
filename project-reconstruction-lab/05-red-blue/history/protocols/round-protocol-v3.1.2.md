# ZUNO-RED-BLUE-WORKFLOW-V3.1.2

## 目的

V3.1.2 在 V3.1.1 的同文件 Part A / Part B、逐题 Red/Blue、Delta 和 Canonical Sync 契约上，
增加 Human Writing Review，并执行 Round-004。它审查的不是架构名词数量，而是设计在具体时序、
部分失败和组件替换下是否仍然自洽。

```text
Human Writing Audit
→ scenario-based Red 100Q
→ Blue Answer
→ Red Score + Writing Note
→ Blue Decision
→ Architecture Delta
→ SECTION_REWRITE / FULL_PART_REWRITE / NO_CHANGE
→ Canonical Sync
→ Human Continuity Check
→ Immutable Round Archive
```

## Human Writing Contract

Part A 必须 technically precise、prose-led、scenario-driven、non-template、human-reviewable。
先说明业务场景和风险，再引出 DomainVersion、PlanVersion、Checkpoint、EffectReceipt 等术语；
每篇至少包含一条可复述的正常路径、一条具体失败路径、设计代价和真实替代方案。Target Scenario
必须明确不是历史事实，Facts、Current、Target、Future、History 和 Hypothesis 不得混写。

“人味”不等于虚构经历，也不等于降低规格精度。不得添加未被 Facts 支持的客户会议、线上事故、
性能数字或个人贡献。Part B 继续以 Contract、State、Failure、Retry、Recovery、Idempotency、
Security、Audit 和 Test 为准。

## Human Writing Review Gate

`HUMAN_WRITING_REVIEW` 与 Part A 数值分数分开，取值为 `PASS`、`WARNING` 或 `FAIL`。确定性
Verifier 只能检查并报告：重复模板短语、标题密度、列表/表格占比、英文术语密度、场景/失败/取舍
标记和 Current/Target 边界；它不能自动宣称 Human Writing PASS。最终结论必须由 Blue self-review、
Red documentation review 和 ChatGPT review 共同形成。

审查记录至少包含：每篇文档的 Template Phrase Density、Heading Density、English Term Density、
Scenario Quality、Failure Story Quality、Tradeoff Quality、Narrative Flow、Human Review Result
和 Rewrite Required。

## Round-004 Contract

Round-004 固定 100 道问题，保持 11+1 配额：12、6、7、11、6、8、14、6、10、8、6、6。问题至少
80% 为 `NOVEL`，最多 20% 为 `REGRESSION`，且每道问题都必须包含具体场景、时序或失败条件。
主题固定为：

```text
Architecture Consistency
Failure Semantics
Component Survival
```

重点覆盖 Product workflow、Domain concurrency、stale propagation、PlanVersion/DomainVersion、
parallel branch、Reducer/Join、Replan Barrier、Memory contamination/promotion、Graph stale
projection、Citation lineage、Tool unknown outcome、Approval race、duplicate side effect、Queue
duplicate/cancellation、service partial failure、rolling upgrade、Checkpoint compatibility、
provider substitution 和 A/B/C measurability。

每题的 Blue Answer 先直接回答，再说明 Owner、State、Failure、Recovery、Tradeoff、Evidence 和
Reversal。每题的 Decision 必须记录 `document_impact`、Part A/Part B change required、Canonical
Owner、`sync_mode` 和 Delta Ref。`Writing / Explainability Note` 只记录 `CLEAR`、`DENSE`、
`TEMPLATE-LIKE` 或 `AMBIGUOUS`，不进入 Architecture Score。

## Canonical Sync

Round-004 不允许 APPEND。若 Red 攻击只澄清已有设计，使用 `SECTION_REWRITE`；若改变一整个叙事
或 Contract，使用 `FULL_PART_REWRITE`；没有稳定影响时使用 `NO_CHANGE`。同步前必须从 Part A
第一段通读到最后一段，检查术语、因果、失败路径和 Target 边界；同步后 Part B 与其 Contract
必须重新通过现有 verifier。

## Gate 与边界

Round-005 只有在 New A-P0 = 0、Architecture Integrity PASS、Part A/Part B >=85、Human
Writing != FAIL 且 Canonical Sync 完成时，才标记 `READY_NOT_STARTED`。本轮默认
`facts_changed = NONE`，不得修改 Runtime、UI、Schema、Migration、Dependencies 或 Production
Infrastructure。Historical Gap 进入 Fact Recovery Queue；架构目标没有运行证据时仍是 Target、
Hypothesis 或 Gap。

Round-004 Session 必须 immutable，位置为：
`project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-004/`。
