# Red / Blue / Counter Attack

## 角色

- Red Team：杀死没有必要的复杂度，攻击事实、架构、成本和替代方案。
- Blue Team：基于证据给出最小可行回应，不以“企业级”“最佳实践”代替证明。
- Counter Attack：攻击 Blue 的隐含假设、失败语义、运营成本、规模和安全声明。

## 生命周期

```text
Claim
→ Red Attack
→ Blue Response
→ Counter Attack
→ Closure Class
→ User Architecture Gate
→ Decision
→ Canonical Sync / Gap
```

Blue 回答不会自动通过。只有反击后仍成立，Architecture 才能进入 `SURVIVED`。

Round 结束后不直接进入下一 Round。若存在大量 P0/P1，先执行：

```text
Discovery
→ Root-Cause Clustering
→ Blue Repair
→ Severity Reclassification
→ Closure Class
→ A-P0 Burn-down
→ User Architecture Gate
→ Canonical Sync
→ Implementation / Evidence / External Tracks
→ Counter Retest
→ Round Closure
→ Next Round
```

具体规则见 [Blue Repair Protocol](blue-repair-protocol.md)。Severity Burn-down 只减少严重度
饱和，不能把没有证据的 P0 宣称为已关闭。若 P0 只是实现、测量或外部资格阻塞，不得因此
把已经设计清楚的 Target 锁死在 User Architecture Gate 之前；具体规则见
[Architecture Gate Policy](../../docs/governance/architecture-gate-policy.md) 和
`sessions/RB-GATE-REALIGNMENT-001/`。

## 输出

每项设计必须得到：`KEEP`、`SIMPLIFY`、`ADOPT`、`EXTEND`、`BUILD`、`DEFER` 或 `DELETE`，并附原因、替代方案、证据和回滚条件。

## V3 百问协议

`ZUNO-RED-BLUE-WORKFLOW-V3` 将一次完整架构攻击固定为一个可回放、可同步 Round：

```text
Fact Baseline
  → Red 100Q Attack
  → Blue 100Q Response
  → Red Scoring
  → Blue Architecture Decision
  → Architecture Delta Consolidation
  → Automatic Canonical Sync（只限 AUTO_APPLY）
  → Completeness / Governance Verification
  → Immutable Round Archive
  → ChatGPT Review Package
```

事实结构仍然冻结为十类 Canonical Facts 和 E0–E5 Evidence Strength；Red 发现的历史事实
缺口必须进入 Fact Recovery Queue，不能由 Blue 为了维护架构叙事自行填空。

### 11+1 固定配额

每轮恰好 100 个问题：00 Overall 12；01 Product 6；02 Ingestion 7；03 Knowledge/GraphRAG 11；
04 Model Gateway 6；05 Memory 8；06 Agent Core 14；07 Capability/Skill 6；08 Tool Runtime 10；
09 Security 8；10 Observability/Eval 6；11 Infrastructure 6。

问题必须独立、具体、可回答，并能改变设计决策；至少 70% 标记 `NOVEL`，最多 30% 标记
`REGRESSION`。完整映射见 [`11-plus-1-canonical-coverage-map.md`](11-plus-1-canonical-coverage-map.md)。

### 逐题记录契约

```text
Question ID / Round ID / Category / Question
Attack Intent / Target Component / Assumption Being Attacked
Severity / Expected Answer Depth / Evidence Required / Kill Condition
Blue Answer / Current-Historical-Target Boundary / Problem / Decision / Why
Ownership / State Transition / Failure / Retry / Recovery / Idempotency
Security / Observability / Alternative / Tradeoff / Test-Benchmark / Evidence
Remaining Gap / Red Critique / Blue Revision / Final Red Assessment / Score
```

字段不能使用 `N/A` 逃避边界；不适用时也要写清楚“不适用原因和替代验证”。不得保存隐藏思维链；
只保存用户可见的问题、回答、批评、修订、评分和决策摘要。

V3 额外要求：每道题进入独立 `questions.md`、`blue-answers.md`、`red-scores.md` 和
`blue-decisions.md`；Delta 必须回链 Question IDs，Canonical Sync 必须回链 Delta IDs。

### 评分和 Gate

Red Team 对每题给 `0–5` 分：0 是未回答或明显错误，1 是口号，2 是方向但缺关键边界，
3 是基本闭环，4 包含替代/失败/恢复/验证，5 具有 Contract、Evidence、反例、Kill
Condition 和可执行 Validation。Round Raw Score 最大 500，Normalized Score 为
`Raw Score / 5`。

分数只代表本轮防守质量，不自动证明架构正确。以下任一未关闭时，Round 必须保持
`NOT_PASSED`：Canonical State Ownership、不可逆副作用、安全或审批绕过、重复执行、
数据损坏、Plan Version 冲突、跨服务一致性、Evidence/Citation Integrity。

### Complexity Justification Card

重要组件必须填写 [Complexity Justification Card](complexity-justification-card.md)。
`KEEP` 不是默认状态；组件只有在 Capability Separation、State Ownership、Failure/Security
Isolation、Independent Scaling/Resource Profile/Deployment Lifecycle、Provider Replaceability、
Audit Governance 或 Measured Quality Improvement 至少一项成立，并且简单替代方案不足，
才可以进入 Blue Proposal。

### Round 记录位置

本仓库已有 `sessions/` 的机器校验契约，因此每个 Round 的物理记录位于：

```text
project-reconstruction-lab/sessions/<session-id>/
```

它等价于建议的 `05-red-blue/rounds/<round-id>/`，避免同时维护两套 QA 记录。V2 的历史 Round
使用 `transcript.md` 等旧契约；V3 使用 `questions.md`、`blue-answers.md`、`red-scores.md`、
`blue-decisions.md`、`architecture-deltas.md` 和 `canonical-sync-record.md`。不要修改
Round-001 的历史格式，也不要让 V2 与 V3 形成第二套当前协议。

Blue Repair 使用同一个 `sessions/` 根目录，Repair Session 以独立协议记录根因聚类、Part-A
修复、五指标、Counter Retest 和 Closure Report，例如：

```text
project-reconstruction-lab/sessions/RB-BLUE-REPAIR-001/
```

它不是新的 100Q Round，也不覆盖 Round-001 的原始分数和原始 Severity。

### Evidence Closure

Blue Repair 之后，如果 Final P0 仍未闭合，进入 [Evidence Closure Protocol](evidence-closure-protocol.md)。
Evidence Closure 是证据战役，不是新的百问 Round：它逐项要求执行验证、保存原始 Artifact、
接受 Red Evidence Review，并完成 Counter Retest。当前会话位于：

```text
project-reconstruction-lab/sessions/RB-EVIDENCE-CLOSURE-001/
```

没有 V3–V5 证据的设计只能保持 `TARGET_ONLY` 或 `COUNTER_RETEST_PENDING`；不得因为 Blue
Repair 已经写过状态模型，就把 P0 标成 `CLOSED`。`RB-GATE-REALIGNMENT-001` 只分离
Architecture、Implementation、Measurement 和 External Qualification 的阻塞面，不改变
原始 P0 Closure。

P0 V4 Execution 记录位于 `sessions/RB-P0-V4-EXECUTION-001/`。该会话允许 verification-only
spike、fault model、loopback Provider emulator 和 focused test，但必须区分 Current、Emulated
Boundary、Target 和 External Block；它不直接修改产品 Runtime。

验证：

```powershell
python tools/scripts/verify_red_blue_session.py
python tools/scripts/verify_red_blue_round_v2.py
python tools/scripts/verify_red_blue_round_v3.py
python tools/scripts/verify_red_blue_score_v3.py
python tools/scripts/verify_canonical_diff_v3.py
python tools/scripts/verify_red_blue_repair_v1.py
python tools/scripts/verify_red_blue_evidence_closure_v1.py
python tools/scripts/verify_red_blue_p0_v4_execution_v1.py
```

V2 Round-001 的历史 Gate 规则继续约束其自身记录；V3 Round 的 AUTO_APPLY 只允许协议定义的
Target refinement，并由 V3 verifier 和 Canonical Diff Validator 证明。它不能修改 Runtime、
Facts、Schema/Migration 或激活 implementation Program。
