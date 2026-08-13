# Attack-time vs Post-round

## Distribution

| Class | Attack-time findings | Post-round open gaps |
|---|---:|---:|
| A | 6 | 0 |
| I | 71 | 75 |
| E | 12 | 13 |
| X | 11 | 11 |

## A semantics

A found: 6。A resolved in Round-005 after Canonical Sync: 1。A remaining: 0。

这些 A 不是“本轮结束仍有十个 A”。它们分别暴露了版本/Host/文档/Review/发布/Candidate authority 的攻击时刻问题；同步后没有留下核心架构矛盾，残余只进入 I 或 E。

## Finding states

- `DEFERRED`: 11
- `EVIDENCE_PENDING`: 13
- `REMAINS_OPEN`: 75
- `RESOLVED_IN_ROUND`: 1
