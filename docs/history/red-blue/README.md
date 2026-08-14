# Red / Blue Architecture Round Archive

这里是正式 Red / Blue 对抗 Round 的唯一历史 Owner。每个文件是一个压缩后的单 Round 记录，保留
核心 Questions、Answers、Review/Score、Decision、BASE SHA 和最终状态；它们不拥有 Current Facts、
Canonical Target Architecture 或实现授权。

## Manual Round

- [Manual Round 01 — Overall Architecture](manual-round-01-overall-architecture.md)

## Automated Rounds

- [Automated Round 001 — Project Architecture V2](automated-round-001-project-architecture-v2.md)
- [Automated Round 002 — Architecture V3](automated-round-002-architecture-v3.md)
- [Automated Round 003 — Document Quality V3.1](automated-round-003-document-quality-v31.md)
- [Automated Round 004 — Human Writing V3.1.2](automated-round-004-human-writing-v312.md)
- [Automated Round 005 — Failure / Recovery V3.1.3](automated-round-005-failure-recovery-v313.md)
- [Automated Round 006 — Operational Pilot](automated-round-006-operational-pilot.md) — `ABORTED`
- [Architecture Baseline 001](automated-architecture-baseline-001.md)
- [Domain Kernel V3](automated-domain-kernel-v3.md)
- [Architecture Reframe V1](automated-architecture-reframe-v1.md)

## Metadata contract

每个归档顶部都有：

```text
series
round_id
execution_mode: MANUAL | AUTOMATED
status
base_sha
archive_commit
architecture_revision_commit
```

Round-006 的 `ABORTED_OPERATIONAL_PILOT` 是真实工作流中止记录，不是完成的架构结果。
Bootstrap、Reset、Repair、Evidence Closure、P0 Execution、Gate Realignment、Normalization、
Semantic Audit 和 Workflow Test 不属于正式 Round，不在这里伪装成 Round。

Blue Proposal 不等于 Architecture Decision，Red Finding 不等于已证实事实。正式事实回到
[`../../facts/`](../../facts/README.md)，正式 Target 回到 [`../../architecture/`](../../architecture/README.md)，
正式长期架构决定回到 [`../../decisions/`](../../decisions/README.md)。当前工作流和归档导航见
[`../../../project-reconstruction-lab/WORKFLOW.md`](../../../project-reconstruction-lab/WORKFLOW.md)。
