# Red Evidence Review

## Review 结论

Red Team 不接受任何 P0 的当前证据作为 `CLOSED`。原因不是命令没有通过，而是证据范围与
Closure Condition 不相等：现有结果主要是 V3 focused contract/model/recovery，缺少 V4/V5
集成、故障注入、真实 Provider、Sandbox 或法律 benchmark。

## 逐项复核

| P0 | 当前 Artifact | Red 判定 | 反驳理由 | 必须补的证据 |
|---|---|---|---|---|
| Q005 | 无执行结果 | REQUEST_MORE_EVIDENCE | Owner prose 不能证明并发 mutation | Domain Owner mutation/concurrency |
| Q016 | state/restart/interrupt tests | NARROW_CLAIM_ONLY | 证明 focused state behavior，不证明 cross-store recovery | Domain/Runtime crash matrix |
| Q033 | approval interrupt/security batch | NARROW_CLAIM_ONLY | 未覆盖真实 Tool effect 与旁路 API | approval bypass integration |
| Q039 | observability batch | REQUEST_MORE_EVIDENCE | 观测协议不是 Citation correctness 或 legal quality | Court QA/A-B/C citation eval |
| Q053 | 无执行结果 | REQUEST_MORE_EVIDENCE | 计划版本冲突尚未被触发 | concurrent Plan/Domain mutation |
| Q061 | tool/security batch | NARROW_CLAIM_ONLY | 没有执行侧撤权和多服务边界 | revoked permission integration |
| Q063 | local idempotency test | NARROW_CLAIM_ONLY | 本地去重不等于 Provider exactly-once 语义 | provider timeout/duplicate |
| Q064 | tool protocol batch | NARROW_CLAIM_ONLY | 没有真实 Unknown Provider result | provider query/reconcile |
| Q066 | security batch | REQUEST_MORE_EVIDENCE | 没有 Sandbox escape/egress/secret 实验 | isolated sandbox security test |
| Q067 | payload reference/security batch | NARROW_CLAIM_ONLY | 未从不可信 Context 走完整 Tool path | injection-to-tool integration |
| Q070 | tool/security batch | REQUEST_MORE_EVIDENCE | 没有跨服务 end-to-end audit trace | trace/receipt integration |
| Q097 | restart/interrupt tests | REQUEST_MORE_EVIDENCE | 没有 Domain/Checkpoint/Effect 三方 crash matrix | recovery fault injection |

## Red 的禁止升级

- `PASS` 不能改写为“安全”；
- V3 不能改写为 V4/V5；
- 模拟输入不能改写为 Court/Pilot 输入；
- 代码存在不能改写为历史项目使用；
- Target Contract 不能改写为 Current production behavior；
- `0 / 12` 不能因为“复杂度已经解释”而改变。

## Red Review 状态

```text
Accepted closure evidence: 0 / 12
Narrow-claim evidence: 7 / 12
Request-more-evidence: 5 / 12
Counter Retest: not run
```

其中 Q005、Q053 没有执行结果；矩阵中保留为 `READY_TO_EXECUTE`。
