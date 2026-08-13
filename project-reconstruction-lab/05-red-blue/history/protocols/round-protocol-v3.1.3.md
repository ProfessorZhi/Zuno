# ZUNO-RED-BLUE-WORKFLOW-V3.1.3

## 本轮目的

V3.1.3 延续 V3.1.2 的 100Q、场景化 Red/Blue、Delta、Canonical Sync 和 Human Writing Contract，
但把审查重点推进到系统真实运行时的失败闭环：并发、崩溃、恢复、重放、撤权、旧版本、未知副作用、
滚动升级和部分失败。它不证明 Runtime 已实现，也不把 Round 分数当作法院质量、安全资格或生产证据。

```text
Deep Failure / Recovery / Concurrency
→ Red 100Q
→ Blue direct answer + structured record
→ Severity / Closure Class independent review
→ Distribution Audit
→ Root-cause Delta Set
→ Canonical SECTION_REWRITE / FULL_PART_REWRITE / NO_CHANGE
→ Human Continuity Review
→ Immutable Round Archive
```

## V3.1.3 Closure Classification Integrity

每题必须分别判断 `Severity` 与 `Primary Closure Class`。二者正交，不能因为当前没有代码就自动填 `I`。

| Class | 含义 | 首要判断 |
|---|---|---|
| `A` | `ARCHITECTURE_BLOCKING` | Target 仍有 Owner、State、Retry/Replan、Security 或 Recovery Authority 矛盾 |
| `I` | `IMPLEMENTATION_BLOCKING` | Contract 已清楚，主要缺实现、接线、测试或运行恢复 |
| `E` | `EVIDENCE_MEASUREMENT_BLOCKING` | 设计与实现路径清楚，但收益、覆盖率或因果归因尚未测量 |
| `X` | `EXTERNAL_QUALIFICATION_BLOCKING` | 需要真实 Sandbox、Provider、HA、Load、Production 或外部资格证据 |

判断顺序固定为：先问是否存在未解决的架构矛盾；若没有，再问是否只是实现缺口；若仍不是，再问是否主要缺
Benchmark/Measurement；最后才判断是否主要依赖外部环境资格。一个问题可以有多个 `secondary_gaps`，
但只能有一个 `primary_closure_class`。每题必须写一句 `closure_class_rationale`，说明为什么不是另外三类。

`I` 不能成为“未实现”的默认桶。若 Sandbox 闭环已经设计清楚但需要真实逃逸测试，Primary 应为 `X`，
可以同时记录 `I` 为 secondary gap；若 Graph 与 Hybrid 的选择路径清楚但收益未知，Primary 应为 `E`。
历史 P0 的 Severity 和 Closure 不因本轮自动重分类；只有明确的 Historical Correction 或 Gate Reclassification
才能改变历史记录。

## Closure Distribution Audit

每个 Round 必须生成 `closure-class-audit.md`，记录 A/I/E/X 数量、每类五个样本、边界题、重分类和潜在默认偏差。
任一类别超过 80% 时必须做至少 20 题人工抽查；即使没有超过 80%，也建议抽查四类样本。Audit 是分类完整性检查，
不是 Runtime 或 Production 证明。

## Human Narrative Continuity

V3.1.2 的 Human Writing Contract 继续有效。每次修改 Canonical Part A，都必须从第一段读到最后一段，再检查场景、
问题、决策、代价和反转是否连贯。禁止在结尾追加四个孤立的“此外/Runtime 仍然/这项约束”式补丁段；同一思想要合并
成完整收束段。必要的英文 Contract 名称保留精度，但 Part A 先讲事情，再引出术语；Part B 继续 precision first。
目标场景可以自然写成“考虑下面这个目标场景”，但必须注明它不代表 Historical Current。

确定性 Verifier 只报告结构、分布和密度信号，不能自动宣称 Human Writing PASS。`PASS/WARNING/FAIL` 仍由 Blue self-review、
Red documentation review 和 ChatGPT review package 共同形成。

## Round-005 Contract

Round-005 必须恰好 100 题，11+1 配额为：

```text
00 Overall Architecture                    12
01 Product Surface                          6
02 Input / Document Ingestion               7
03 Knowledge / Agentic GraphRAG            10
04 Model Gateway                            5
05 Memory & Context                         8
06 Agent Core / Planning & Control         15
07 Capability / Skill                        6
08 Tool Runtime                             10
09 Security                                  8
10 Observability & Eval                      6
11 Infrastructure                            7
```

至少 80% 为 `NOVEL`，最多 20% 为 `REGRESSION`。问题优先使用 Scenario + State + Timing + Failure + Ownership Conflict，
覆盖 Domain/Runtime/Projection 版本屏障、Document 发布、Graph/Citation stale、Model fallback、Memory promotion、
Plan/Join/Reducer/Replan、Capability version、EffectReceipt、authorization race、queue duplicate、checkpoint compatibility、
fault injection 和 A/B/C attribution。

Blue Answer 先直接回答核心问题，再保存结构化的 Owner、State、Failure、Retry、Recovery、Idempotency、Security、
Observability、Alternative、Tradeoff、Evidence 和 Gap。Red Score 为 0–5；新增的 `Explanation Quality`
（`CLEAR/DENSE/AMBIGUOUS/TEMPLATE_LIKE`）不进入 500 分，只用于文档复核。

## Delta 与 Canonical Sync

100 题必须先聚类 Root Cause，再生成 Delta Set。每个 Delta 要声明 Owner、`document_impact` 和 `sync_mode`。只允许
`SECTION_REWRITE`、`FULL_PART_REWRITE`、`NO_CHANGE` 或升级；`APPEND` 禁止。Part A 改写必须执行 Human Continuity Pass，
Part B 补足版本、状态转换、失败矩阵、恢复矩阵、并发、安全 Gate、对账和 Fault Injection Requirement。

## Gate

Round-006 只有在以下条件满足时标记 `READY_NOT_STARTED`：

```text
New A-P0 = 0
Architecture Integrity = PASS
Part A >= 85
Part B >= 85
Human Writing != FAIL
Closure Classification Audit = PASS
Canonical Sync = COMPLETE
```

新 A-P0 必须阻塞受影响决策的自动接受；E-P0 只阻塞 Measured，X-P0 只阻塞 External Qualification/Production。
`ACCEPTED_TARGET` 仍不等于 `IMPLEMENTED`、`VERIFIED`、`MEASURED` 或 `PRODUCTION_PROVEN`。

本轮默认 `facts_changed = NONE`，不得修改 Runtime、UI、Schema、Migration、Dependencies 或 Production Infrastructure。
Round-004 目录保持 immutable，原始 P0 继续由 Evidence Closure Track 管理。

## V3.1.3.1 Semantic Closure Audit

Round 关闭后，如果 A/I/E/X 的序列或理由显示可能存在分类偏差，必须建立独立的 Semantic Closure Audit；
它不是新的 100Q，也不能修改原始 Question、Answer、Score、Decision、Delta 或 Scorecard。审计必须重新
读取每题的完整链路和同步后的 Canonical Owner 文档，从零判断：

```text
attack_time_closure_class
→ post_round_closure_class
→ finding_state
```

`A` 只有在 Target Contract 仍无法给出唯一 Owner、State、Retry/Replan、安全或 Recovery Authority 时成立。
如果 Round 内已通过 Blue Repair/Canonical Sync 消除矛盾，必须把“攻击时发现 A”和“Round 结束仍有 A”分开。
`A-P1/P2` 是可被接受 Target 包含的架构债务，但若涉及 Domain Owner、Security Trust Boundary、Recovery Authority
或 Plan/Domain Truth 等核心不变量，必须重新判断是否应升级为 A-P0。

Semantic Audit 必须生成逐题 rationale、Attack-vs-Post 分布、Lens/Class Matrix、重复理由审计和 immutable source
hash。不得设置类别配额；题号和 Lens 只能用于索引，不能用于分类。Derived Audit 是当前分类视图，Round 原件仍是
可回放的历史记录。
