# PRD-A Product Runtime Durable Handoff Freeze Candidate

status: `READY_FOR_REVIEW / IMPLEMENTATION_NOT_AUTHORIZED`
base_main: `7c1df7abca6e918a04b1fc9c65b34234b342bf95`
scope: `01 Product command / Agent Core owner receipt / 04 canonical Runtime execution handoff`
production_readiness: `NOT_ESTABLISHED`

CXL-B 的 source review 暴露了一个更上游的问题：Product 已经能够接受 `RuntimeRequest` command、提交 outbox、签发 cancel action token，也已经有 consumer 能为该 command 写 Agent Core 的 GoalVersion / TaskContract / AgentRun owner facts；但生产路径还没有证明同一个请求会启动 canonical `WorkspaceAgentRuntime / AgentRuntimeService`。

继续追代码以后，问题进一步收窄。今天缺的不只是一个 queue worker。Product command 本身没有耐久保存足够的 canonical execution input，outbox 也只携带请求 hash 与少量 identity。重启后的 worker即使存在，也无法从 Owner facts重建一次等价的 RuntimeStartRequest。

PRD-A 先解决这个 handoff，再重新打开 CXL-B。

## Current failure shape

### Product command 已耐久，但 execution input 没有耐久

`ProductService.submit_runtime_request()` 接收：

```text
tenant_id
workspace_id
conversation_id
principal_id
active_agent_version_id
client_request_id
runtime_request_ref
raw_intent_ref
payload
```

`ProductRepository.submit_command()` 会把 request hash写入：

```text
product_submissions.request_hash
product_commands.payload_hash
product_messages.message_hash
```

随后创建 `product.runtime_request.dispatch` outbox event。

Current outbox payload包含：

```text
tenant_id
workspace_id
conversation_id
submission_id
message_id
command_id
command_kind
runtime_request_ref
active_agent_version_id
principal_id
payload_hash
```

它不包含原始 `payload`、`goal_ref` 或任何可在重启后解引用的 typed execution spec。

`raw_intent_ref` 目前也是 identity / provenance reference；repo-wide review没有找到 Current store可以用它重新读取原始 intent。

因此：

```text
PRODUCT_COMMAND_DURABLE = YES
EXECUTION_REQUEST_RESTART_SAFE = NO
```

### 不同 Product surface 的 payload 也不是一个稳定 Contract

Web runtime 当前会把：

```text
payload.goal = query
```

放进 submit 请求，但 Backend API 将 `payload` 定义成自由 dict。

Completion surface 更严格地只把：

```text
runtime_surface
dialog_id
user_input_hash
product_mode
query_method
```

交给 Product command；它没有把原始 user goal放进 outbox或可解引用 Owner store。

所以不能根据“Web 当前恰好有 goal”设计 production worker。相同 `RuntimeRequest` topic必须有跨 surface稳定的 typed handoff。

### Agent Core owner row 与 canonical runtime run 不是同一事实

`consume_runtime_request_dispatch()` 当前会创建：

```text
agent_run_id = agent-run:{runtime_request_ref}
task_contract_id = task-contract:{runtime_request_ref}
goal_version_id = goal:{runtime_request_ref}
```

并在 Product receipt里记录 `agent_run_ref`。

这证明 Agent Core owner fact存在，不证明 canonical graph已经执行。

另一方面，`WorkspaceAgentRuntime._to_runtime_request()` 固定构造：

```text
RuntimeStartRequest.task_id = WorkspaceRunRequest.task_id
RuntimeStartRequest.run_id  = run:{WorkspaceRunRequest.task_id}
```

`PostgresAgentRunStore` 又以 `task_id` 作为 durable runtime主键。

今天没有 durable contract说明：

```text
runtime_request_ref
↔ Agent Core agent_run_ref
↔ canonical runtime task_id
↔ canonical runtime run_id
```

如何一一对应。

如果现在直接在 dispatch consumer末尾调用 `start()`，可能得到两套同名为 AgentRun 的事实体系，也无法证明 response-loss replay不会启动第二次 graph。

## Design objective

PRD-A 不建立新 Runtime Service。它把已经存在的 Product command、Agent Core owner receipt 和 server-owned `WorkspaceRuntimeComposition` 接成一条可恢复 handoff。

最小链路：

```text
Product RuntimeRequest
→ durable Product command
→ durable typed RuntimeExecutionSpec
→ outbox / inbox delivery
→ Agent Core owner admission
→ stable canonical runtime identity binding
→ canonical WorkspaceAgentRuntime / AgentRuntimeService
```

每个箭头必须可以在进程重启以后从 durable fact恢复。

## PRD-A1 — Durable RuntimeExecutionSpec

A1 只解决“worker拿到什么”。

增加一个最小、版本化、非 Secret 的 Product-owned execution handoff。实现可以复用现有 Product command表，也可以新增最小 companion table；不得为了一个 payload增加新 network service。

建议逻辑 Contract：

```text
RuntimeExecutionSpec
  runtime_request_ref
  tenant_id
  workspace_id
  conversation_id
  principal_id
  submission_id
  client_request_id
  active_agent_version_id
  goal_ref / durable goal material ref
  plan_kind
  tool_id? / tool_arguments_ref?
  knowledge_space_refs?
  budget_limits?
  content_fingerprint
  spec_version
  spec_hash
```

A1 的核心约束不是字段数量，而是：

- Product command exact replay必须得到同一 spec；
- same `client_request_id` / `runtime_request_ref` + changed spec 必须 conflict；
- spec必须 tenant / workspace / principal scoped；
- Secret material不得进入 spec；
- arbitrary frontend dict不能直接成为 canonical RuntimeStartRequest；
- Completion / Web / future Host必须先归一化成同一 typed spec。

若 goal 本身需要持久化，优先复用 Product-owned message/intent durable surface；如果当前 surface只有 hash，则允许增加最小的受控 goal material字段或对象引用，但必须明确 retention / classification。不要通过日志、Trace 或前端内存恢复 goal。

### A1 outbox payload

`product.runtime_request.dispatch` 不需要复制整份任意 payload。

最小 outbox只携带：

```text
runtime_request_ref
runtime_execution_spec_ref
runtime_execution_spec_hash
tenant / workspace / principal identities
active_agent_version_id
command / submission identities
```

consumer 按 ref从 Product Owner store读取 spec并校验 hash。

这样 response loss / queue redelivery / worker restart都不会依赖旧进程内存。

## PRD-A2 — Canonical execution binding

A2 只有在 A1 durable spec成立以后启动 canonical runtime。

### Stable identity

冻结一个 deterministic mapping，不能让各 adapter自己猜：

```text
canonical_task_id = deterministic(runtime_request_ref, tenant_id, workspace_id)
canonical_run_id  = run:{canonical_task_id}
```

具体编码可以使用 namespaced hash或稳定 escaped ref；关键是同一个 Product RuntimeRequest永远映射到同一 canonical task/run，跨 tenant不能碰撞。

Agent Core owner receipt必须显式记录：

```text
runtime_request_ref
agent_run_ref
canonical_task_id
canonical_run_id
runtime_execution_spec_ref
runtime_execution_spec_hash
```

恢复时任何 identity/hash不匹配都 fail closed。

### Owner row 与 runtime store的关系

Product dispatch consumer创建的 Agent Core owner fact继续是 owner admission / durable business-control fact。

`PostgresAgentRunStore` 是 canonical runtime execution/checkpoint store。

两者可以互相引用，但不能互相冒充。

A2 不允许：

- 因为 `agent_run_ref` row存在就宣布 graph已启动；
- 因为 runtime checkpoint存在就回写 Product “owner admitted”而没有 matching owner receipt；
- 使用两个互不绑定的随机 run id。

### Start ordering

禁止在持有 Product/Agent owner transaction时执行 graph、模型或 Tool。

最小顺序：

```text
claim Product dispatch event
→ load + validate durable RuntimeExecutionSpec
→ idempotently establish Agent Core owner facts + canonical identity binding
→ COMMIT
→ start/recover canonical runtime using server WorkspaceRuntimeComposition
→ persist runtime start/result observation
→ update Product projection/owner receipt
```

如果 crash发生在 owner commit以后、runtime start以前，redelivery必须读到相同 canonical identity并继续 start。

如果 crash发生在 runtime store已创建以后、Product projection更新以前，redelivery必须读取已有 runtime task，而不是再次创建不同 run。

## Server composition

A2 必须复用当前 production wiring：

```text
WorkspaceRuntimeComposition
PostgresAgentRunStore
SecurityDecision owner resolver
Tool / Security / Infrastructure UoW
```

不得调用旧 test-only `AgentRunApplicationService.configure_agent_run_store_for_tests()`，不得创建 per-request SQLite store，也不得恢复已退役的 `/workspace/simple/chat` owner path。

如果当前 Product composition因为 Budget / Approval等独立 owner gate而 fail closed，worker必须保存这个 canonical blocked结果。PRD-A 不允许 synthetic BudgetDecision或假 Approval绕过这些 gate。

换句话说，PRD-A 的验收可以是“正式 request确实到达 canonical runtime并在下一个真实 owner gate fail closed”，不要求把所有 Product功能一次跑通。

## Worker / deployment

A2 可以复用成熟的 outbox + RabbitMQ模式，但逻辑 consumer与物理 worker分开。

优先顺序：

1. 先实现可直接调用、幂等的 Product Runtime Dispatch application consumer；
2. 用 PostgreSQL integration证明 restart/replay；
3. 只有 production topology确实需要 RabbitMQ worker时，再复用 `PostgresOutboxRabbitMQPublisher` / transport pattern。

不为了架构图新建 Product Runtime microservice。

## Required PostgreSQL probes

### PRD-A1

1. **exact request replay**  
   同一 client/runtime identity + same spec只保留一个 durable spec。

2. **changed-content conflict**  
   同 identity + changed goal/spec fail closed，不覆盖旧 spec。

3. **restart-safe material**  
   销毁提交进程后，新 consumer只从 PostgreSQL能够恢复 canonical execution input。

4. **cross-tenant identity**  
   同 external request id跨 tenant不会互相读取 spec。

5. **secret rejection / redaction**  
   execution spec不允许 Secret material进入普通 payload。

6. **Completion surface**  
   Completion submit必须形成可恢复 goal/material，而不是只留下 `user_input_hash`。

### PRD-A2

1. **dispatch → canonical start**  
   fresh PostgreSQL上提交 RuntimeRequest，consumer建立 owner facts，再启动 server-owned canonical runtime。

2. **stable identity**  
   owner receipt与 runtime store使用固定 `runtime_request_ref ↔ task/run` mapping。

3. **response loss after owner commit**  
   owner row已提交但 runtime未启动，redelivery启动同一个 canonical task。

4. **response loss after runtime start**  
   runtime task/checkpoint已存在但 Product update丢失，redelivery不得建立第二个 runtime task。

5. **queue duplicate**  
   outbox/inbox redelivery只产生一个 canonical task。

6. **owner gate blocked**  
   Security / Budget / Approval未满足时，canonical runtime保存 blocked truth，不通过 fallback绕过。

7. **wrong tenant / spec hash**  
   fail closed；runtime start call count = 0。

## CXL-B relationship

CXL-B 只有在 PRD-A2 证明以下 binding以后重新打开：

```text
runtime_request_ref
→ canonical_task_id
→ active canonical runtime state
```

届时 Product cancel action token才能定位**同一个**运行实例，并把 cancel intent交给 04。

在 PRD-A 完成以前，不允许 Product action consumer直接写 ToolCancellationReceipt，也不允许从字符串猜 task id。

## Non-goals

PRD-A 不授权：

- CXL-B provider cancel；
- formal Budget owner service；
- 新 Product Approval flow；
- Formal Admission / AdmissionReceipt；
- provider remote-query reconciliation；
- AUD-L2 crash-repair；
- manual reviewer role system；
- Dynamic DAG扩张；
- 新独立 Runtime network service；
- GraphRAG / Memory / Multi-Agent扩张。

## Acceptance boundary

PRD-A1 完成后只允许写：

```text
Product RuntimeRequest execution material is durable and restart-safe
```

PRD-A2 完成后才允许写：

```text
Product RuntimeRequest dispatch reaches the server-owned canonical runtime
with one stable durable execution identity
```

仍不允许写：

```text
Product Runtime is fully executable
all owner gates are implemented
cancel-in-flight is closed
Production Ready
```

Current仍由 main PostgreSQL selected evidence证明。
