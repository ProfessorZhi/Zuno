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

## V3.1 百问与文档质量协议

`ZUNO-RED-BLUE-WORKFLOW-V3.1` 是历史 Round-003 的 Part A Narrative / Part B Specification 质量门；
Round-001 至 Round-005 的 Human Writing、Closure Classification 与历史执行契约见
[`round-protocol-v3.1.3.md`](round-protocol-v3.1.3.md)。Round-006 以后使用
[`round-protocol-v4.md`](round-protocol-v4.md)，重新建立 Fresh Context、Dual Thread、Artifact
Handoff 和 ChatGPT External Audit。

V4 Bootstrap 位于 `sessions/RB-WORKFLOW-V4-BOOTSTRAP/`，只验证工作流，不启动 Round-006。

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
  → Part-A / Part-B Quality Gate
  → ChatGPT Review Package
```

事实结构仍然冻结为十类 Canonical Facts 和 E0–E5 Evidence Strength；Red 发现的历史事实
缺口必须进入 Fact Recovery Queue，不能由 Blue 为了维护架构叙事自行填空。

### 11+1 固定配额

历史 V3/V3.1 Round 使用过：00 Overall 12；01 Product 6；02 Ingestion 7；03 Knowledge/GraphRAG 11；
04 Model Gateway 6；05 Memory 8；06 Agent Core 14；07 Capability/Skill 6；08 Tool Runtime 10；
09 Security 8；10 Observability/Eval 6；11 Infrastructure 6。Round-005 按 V3.1.3 将配额调整为
12、6、7、10、5、8、15、6、10、8、6、7，仍然恰好 100 题。

问题必须独立、具体、可回答，并能改变设计决策；历史 Round 的 novelty 门槛由各自协议负责，Round-005
要求至少 80% 标记 `NOVEL`、最多 20% 标记 `REGRESSION`。完整映射见 Session 内的 coverage map。

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

V3.1 额外要求：每道题进入独立 `questions.md`、`blue-answers.md`、`red-scores.md` 和
`blue-decisions.md`；每个 Blue Decision 必须记录 `document_impact`、Part A/Part B change
required 和 Canonical Owner；Delta 必须回链 Question IDs，Canonical Sync 必须回链 Delta IDs。

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

V3.1 Round-003 在同一套 `sessions/` 记录中增加 `baseline-audit.md`、Part A/Part B 文档质量
Scorecard、`document_impact`、12 个 Delta、Review Package 和专用 verifier；Round-specific
changelog 只留在 Session，不写回 Canonical 文档。

V3.1.1 进一步要求 Canonical Sync 使用 `SECTION_REWRITE` 或 `FULL_PART_REWRITE`，禁止通过
`APPEND` 在旧正文后累积架构修订；Part A 目标为 85，90 以上标记为 STRONG。结构归一化可以
独立于新的 100Q Round 执行。

V3.1.2 在此基础上加入 Human Writing Contract：Part A 必须 prose-led、scenario-driven、
technically precise、non-template、human-reviewable；确定性 verifier 只能输出 warning，不能
把机器检查冒充人工审查。Round-004 使用具体时序和失败场景审查 Architecture Consistency、
Failure Semantics 与 Component Survival，并保持 immutable。

V3.1.3 Round-005 把重点推进到 Deep Failure、Recovery、Concurrency 和 Architecture Survival。每题
必须独立记录 Severity、Primary Closure Class 和 `closure_class_rationale`；A/I/E/X 的含义和判断顺序
见 [`round-protocol-v3.1.3.md`](round-protocol-v3.1.3.md)。任一分类超过 80% 时必须做 20 题 Distribution
Audit；本轮即使没有超阈值也保留了 20 题人工抽查。Part A 修改必须从第一段读到最后一段，禁止补丁式尾巴。

Round-005 关闭后另有 `RB-CLOSURE-SEMANTIC-AUDIT-V3.1.3.1`，专门从零复核 Closure Class。它不生成新百问，
不修改 Round-005 原件，而是记录 `attack_time_closure_class`、`post_round_closure_class`、`finding_state`、
逐题理由、Lens/Class Matrix 和原始文件 hash。Derived Audit 才表示当前分类视图；历史 Round 仍保持 immutable。

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
python tools/scripts/verify_red_blue_round_v313.py
python tools/scripts/verify_closure_semantic_audit_v3131.py
python tools/scripts/verify_red_blue_workflow_v4.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP
```

V2 Round-001 的历史 Gate 规则继续约束其自身记录；V3 Round 的 AUTO_APPLY 只允许协议定义的
Target refinement，并由 V3 verifier 和 Canonical Diff Validator 证明。它不能修改 Runtime、
Facts、Schema/Migration 或激活 implementation Program。
