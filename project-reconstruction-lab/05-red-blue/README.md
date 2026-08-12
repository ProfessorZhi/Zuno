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
→ P0 Burn-down
→ Counter Retest
→ Round Closure
→ User Architecture Gate
→ Next Round
```

具体规则见 [Blue Repair Protocol](blue-repair-protocol.md)。Severity Burn-down 只减少严重度
饱和，不能把没有证据的 P0 宣称为已关闭。

## 输出

每项设计必须得到：`KEEP`、`SIMPLIFY`、`ADOPT`、`EXTEND`、`BUILD`、`DEFER` 或 `DELETE`，并附原因、替代方案、证据和回滚条件。

## V2 百问协议

`ZUNO-RED-BLUE-WORKFLOW-V2` 将一次完整架构攻击固定为一个可回放 Round：

```text
Fact Baseline
  → Red 100Q Attack
  → Blue 100Q Response
  → Red Scoring
  → Gap / Blocker Clustering
  → Blue Reconstruction Proposal
  → Counter Attack
  → Decision / User Gate
  → Canonical Sync（仅在通过 Gate 后）
```

事实结构仍然冻结为十类 Canonical Facts 和 E0–E5 Evidence Strength；Red 发现的历史事实
缺口必须进入 Fact Recovery Queue，不能由 Blue 为了维护架构叙事自行填空。

### 固定配额

每轮恰好 100 个问题：A Product/Domain/Requirement 10；B Conceptual Architecture/Necessity 10；
C Agent Runtime/Planning/Multi-Agent 15；D Knowledge/RAG/Graph/Memory 15；E Data/State/Database/Consistency 10；
F Tool Runtime/Sandbox/Security 10；G Failure/Retry/Recovery/Idempotency 10；H Microservice/Scale/Deployment 8；
I Observability/Eval/Benchmark 7；J Engineering Reality/Interview Attack 5。

问题必须独立、具体、可回答，并能改变设计决策；禁止用同一问题的同义改写凑数。

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

可以写 `N/A`，但不能省略真正适用的字段。不得保存隐藏思维链；只保存用户可见的问题、
回答、批评、修订、评分和决策摘要。

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

本仓库已有 `sessions/` 的机器校验契约，因此 V2 Round 的物理记录位于：

```text
project-reconstruction-lab/sessions/<session-id>/
```

它等价于建议的 `05-red-blue/rounds/<round-id>/`，避免同时维护两套 QA 记录。`manifest.yaml`
保存 Round 元数据；`transcript.md` 保存逐题辩论；`scorecard.md` 保存评分和类别汇总；
`gaps.md` 保存 Fact/Architecture/Blocker 聚类；`blue-change-set.md` 保存重构提案；
`retest.md` 保存 Counter Attack/回归结果。

Blue Repair 使用同一个 `sessions/` 根目录，Repair Session 以独立协议记录根因聚类、Part-A
修复、五指标、Counter Retest 和 Closure Report，例如：

```text
project-reconstruction-lab/sessions/RB-BLUE-REPAIR-001/
```

它不是新的 100Q Round，也不覆盖 Round-001 的原始分数和原始 Severity。

验证：

```powershell
python tools/scripts/verify_red_blue_session.py
python tools/scripts/verify_red_blue_round_v2.py
python tools/scripts/verify_red_blue_repair_v1.py
```

V2 Round 未通过 User Architecture Gate 前，不得把 Blue Proposal 写入 `docs/project/`，
也不得生成 Runtime implementation task。
