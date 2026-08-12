# RB-BLUE-REPAIR-001 Counter Retest

## Retest 规则

本次 Counter Retest 攻击的是 Blue Repair 后的 Part A，而不是重复 Round-001 原题。每个
Cluster 至少改变一个变量：状态转换、失败点、权限、并发、规模、Provider 故障、证据缺失或
个人事实边界。由于本阶段没有修改 Runtime，也没有新增真实 Evidence，结果只能是 `REOPEN`
或 `WAITING_FOR_EVIDENCE`，不能是 `PASS`。

## RETEST-RC-001

- Source Cluster：`RC-001`
- Mutation：把真实法院 Workflow 替换为“上传材料→回答”以外的未知业务流程。
- Red Attack：如果 Part A 仍能宣称完整 Legal Domain，而没有用户/Artifact 证据，Domain Contract 过度冻结。
- Blue Response：保持最小 Matter/DocumentVersion/Evidence 边界，真实任务进入 Fact Recovery。
- Result：`REOPEN`
- Remaining Gap：真实法院任务、QA 协议和业务复核点未知。

## RETEST-RC-002

- Source Cluster：`RC-002`
- Mutation：两个 Provider 同时提交同一 Fact 的不同版本，且用户未通过 Architecture Gate。
- Red Attack：如果 Proposal 能直接变成 Canonical Fact，Owner/Version Gate 仍未闭合。
- Blue Response：只有 Domain Owner 接受带 Provenance、Permission、Version 和 Review 的 Proposal。
- Result：`REOPEN`
- Remaining Gap：需要 Domain Mutation/Review/Concurrent Owner Test。

## RETEST-RC-003

- Source Cluster：`RC-003`
- Mutation：Checkpoint 显示 Planner 完成，但 Domain Transaction 未提交；随后 Runtime 重启。
- Red Attack：如果恢复直接生成 Finding 或重复执行 Step，Runtime/Domain Boundary 失败。
- Blue Response：以 Domain Commit 和 generation 对账，Checkpoint 不能宣称业务完成。
- Result：`REOPEN`
- Remaining Gap：Crash Matrix、Checkpoint/Domain Reconciliation Trace 未执行。

## RETEST-RC-004

- Source Cluster：`RC-004`
- Mutation：Graph 错边、Memory Provider 不可用、Citation 缺证据，同时降低 Token Budget。
- Red Attack：如果系统仍强制 Graph/Memory，或把候选引用当事实，Conditional Provider 设计失败。
- Blue Response：回退 Hybrid/DB+Checkpoint，Evidence Gate 阻止 unsupported Finding。
- Result：`REOPEN`
- Remaining Gap：Graph Kill、Memory Ablation、Citation Sufficiency 尚无测量。

## RETEST-RC-005

- Source Cluster：`RC-005`
- Mutation：Vector/Graph/Redis 投影丢失、Raw Artifact 保留、Domain DB 正常。
- Red Attack：如果派生索引被当 SoR，恢复会产生事实损坏；如果 Cache 丢失无法重建，Owner 不清。
- Blue Response：PostgreSQL/Raw Artifact 保留，派生 Projection 可重建，Cache/Queue 不作为业务事实。
- Result：`REOPEN`
- Remaining Gap：Rebuild、Retention、Deletion 和 Cross-store consistency test 未执行。

## RETEST-RC-006

- Source Cluster：`RC-006`
- Mutation：外部写操作超时、Approval Epoch 变化、Secret 被撤销、Provider Operation ID 未返回。
- Red Attack：如果 timeout 被当 failed 或盲目重试，存在重复副作用和安全绕过。
- Blue Response：进入 `outcome_unknown`，先 Reconcile；旧 Approval 不适用于新参数/ToolVersion。
- Result：`REOPEN`
- Remaining Gap：Effect Receipt、Provider Reconcile、Revocation、Sandbox/Egress 测试未执行。

## RETEST-RC-007

- Source Cluster：`RC-007`
- Mutation：Worker 在 Domain Commit 前崩溃、Queue ACK 丢失、Cancellation 与 Retry 同时发生。
- Red Attack：如果通用 exponential backoff 造成重复 Job 或不可恢复状态，Failure Contract 不成立。
- Blue Response：错误分类、Attempt、Lease、Idempotency Key、Dead-letter/Review 和 Reconcile 分离。
- Result：`REOPEN`
- Remaining Gap：Fault Injection、Lease/Retry/Cancellation Matrix 未执行。

## RETEST-RC-008

- Source Cluster：`RC-008`
- Mutation：100 用户低负载、Knowledge GPU 峰值、长 Agent Run、Sandbox 高风险 Effect 同时出现。
- Red Attack：如果五个物理服务没有独立 scaling/failure/security/lifecycle 收益，必须合并；如果
  Sandbox 或 Knowledge 有强隔离需求，不能用统一服务掩盖。
- Blue Response：服务数量保持 Candidate，要求 workload/resource/failure/security evidence。
- Result：`REOPEN`
- Remaining Gap：Boundary Spike、容量和部署 Profile 证据未执行。

## RETEST-RC-009

- Source Cluster：`RC-009`
- Mutation：A/B/C 最终 Judge 分数相同，但 Citation Correctness、Unsupported Claim、Latency 和 Cost 不同。
- Red Attack：如果只看总 Judge Score 就保留复杂度，Eval 无法归因。
- Blue Response：使用质量、效率、调用和 State Reuse 多指标，并预注册删除条件。
- Result：`REOPEN`
- Remaining Gap：Court QA、A/B/C、Graph/Memory/Agent ablation 未执行。

## RETEST-RC-010

- Source Cluster：`RC-010`
- Mutation：面试问题要求提供个人文件、客户 SLA、生产指标和历史组件配置。
- Red Attack：如果 Target 或团队工作被说成个人 Current，事实边界失败。
- Blue Response：保持 Personal/Team/Framework/Unknown 分离，返回 Fact Recovery Queue。
- Result：`WAITING_FOR_EVIDENCE`
- Remaining Gap：个人 Commit/Task/API、旧 Artifact、客户交付和历史配置仍需用户或证据确认。

## Retest Summary

```text
Cluster retests              10
PASS                         0
REOPEN                       9
WAITING_FOR_EVIDENCE         1
Final P0 closed              0 / 12
Counter Retest               NOT CLOSED
Round-002                    BLOCKED
```
