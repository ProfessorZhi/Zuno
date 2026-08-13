# RED-KERNEL-V3 仓库 Current 侦察记录

base_sha: `0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
access_date: 2026-08-12
evidence_class: CURRENT_REPOSITORY_OBSERVATION
scope: `src/backend/zuno`, `tests`, `tools/evals/zuno`, `pyproject.toml`, formal status/evidence docs

## 观察

- `src/backend/zuno` 存在通用 `agent`、`knowledge`、`memory`、`capability`、`platform` 和 `product` 包；代码规模不能证明这些复杂度必要。
- Knowledge storage 已有 `DocumentVersion`、parse/index/quality/review/task/artifact 等通用记录；retrieval 代码有 Claim/Evidence 相关结构。
- 在 `src/backend/zuno` 中，本轮针对 `Matter`、`Case`、`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase`、`HumanDecision`、`WorkProduct` 的类/表/Owner 闭环未找到可证明完整实现。
- Agent Core 有通用 AgentRun、Plan/Step、checkpoint/控制语义的 Target 与实现表面；没有法律 Domain State 与其 Runtime 对账的 E2E Trace。
- `docs/project/status/production-readiness.md` 为 `NOT_ESTABLISHED`；当前 Eval 文档保持 `MEASUREMENT_BLOCKED`/未证明边界。

## 可复现检索

以下检索用于侦察，不把“未匹配”解释为数学意义上的不存在：

```powershell
rg -n "Matter|Case|Party|Fact|Event|Conflict|Dispute|LegalIssue|StatuteVersion|LegalElement|ApplicableLaw|SimilarCase|HumanDecision|WorkProduct" src/backend/zuno
rg -n "DocumentVersion|Claim|Evidence|AgentRun|Checkpoint|ReviewTask|ReviewDecision" src/backend/zuno
```

第二条命令可以定位通用 Document/Claim/Evidence/Agent 结构；第一条命令没有形成法律 Domain Kernel 的可运行 schema、mutation authority、staleness/dependency 和 review/audit 闭环证据。正式状态仍以代码、Migration、测试、Trace、Eval 和 `docs/project/status/` 为准。
