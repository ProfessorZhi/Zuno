# CXL-B Cancel Orchestration Implementation Status

status: `BLOCKED_BY_PRD_A2_CANONICAL_EXECUTION / IMPLEMENTATION_NOT_STARTED`
base_main: `0222269a34648774dc60197bcfd6beb6a8e09349`
source_freeze: [`cxl-b-cancel-orchestration-freeze-candidate.md`](cxl-b-cancel-orchestration-freeze-candidate.md)
production_readiness: `NOT_ESTABLISHED`

CXL-B freeze 已经把取消语义压缩到一个小边界：04 持久化 run / plan / step cancellation intent，06 持有 Tool AsyncJob / CancellationReceipt / final Effect truth，Provider cancel 只是 optional capability。进入实现前对当前 Product 调用链做 repo-wide review 后，发现 B1 还有一个更上游的前置条件没有成立：PRD-A1 已证明 Product RuntimeRequest execution material 可以作为 typed `RuntimeExecutionSpec` 耐久保存、跨 restart读取并由 dispatch consumer校验；当前仍未证明同一请求会启动同一条 canonical AgentRun execution。

这不是取消协议内部的缺口。PRD-A1 只解决“worker拿到什么”，没有解决“worker如何以 stable task/run identity启动 canonical runtime”。若忽略 PRD-A2 直接写 cancellation API，仍会得到一条“可以提交 cancel command，却没有对应 production canonical AgentRun / Tool execution可以取消”的假闭环。

## Current source evidence

### Web 已切到 Product command surface

当前前端 workspace 默认页使用：

```text
POST /api/v1/product/runtime-requests
POST /api/v1/product/actions/consume
```

frontend regression 同时明确禁止回退到旧 `/workspace/simple/chat`。

因此 CXL-B 不能通过恢复旧 workspace task owner 或旧 simple-agent route 来“完成”生产取消。

### Product RuntimeRequest 已有 cancel action token

`ProductService.submit_runtime_request()` 会为 accepted RuntimeRequest 发出：

```text
command_kind = CANCEL_RUNTIME_REQUEST
target_ref = runtime_request_ref
```

`consume_action_token()` / `consume_action_token_as_command()` 负责 tenant / principal / expiry / single-use token 校验，并把 cancel action 变成新的 Product command。

这层已经提供了 Product cancel 命令的安全、幂等外壳，不需要再设计第二套 HTTP token 或取消 idempotency namespace。

### PRD-A1 已建立 durable dispatch input；production canonical start仍缺失

PRD-A1 后，`ProductService.submit_runtime_request()` 会在同一 Product UoW中写 typed/versioned `RuntimeExecutionSpec`，outbox只携带 matching spec ref/hash；`consume_runtime_request_dispatch()` 会按 tenant/ref/hash重新读取并校验 scope，再在 Agent Core owner transaction 中创建 GoalVersion、TaskContract 和 AgentRun owner fact。它还会把：

```text
runtime_request_ref
agent_run_ref
task_contract_ref
```

写入 Product owner receipt。

Current PostgreSQL evidence已经证明 dispatch consumer可从 durable spec恢复 owner input，但 repo-wide call-site review仍没有建立 production Worker / startup / queue consumer调用它并继续进入 canonical runtime。PRD-A1 没有因此升级成 PRD-A2。

因此：

```text
PRODUCT_RUNTIME_EXECUTION_SPEC = CURRENT / SELECTED VERIFIED
PRODUCT_RUNTIME_DISPATCH_TO_CANONICAL_START = NOT IMPLEMENTATION-PROVEN
```

### 当前 dispatch consumer 也没有启动 canonical AgentRuntimeService

即使直接调用 `consume_runtime_request_dispatch()`，当前实现做的是 Agent Core owner-fact creation；source review 没有看到它继续构造 `RuntimeStartRequest` 并调用 `AgentRuntimeService.start()`。

这意味着 Product command 的 `agent_run_ref` 当前可以证明 Owner record存在，但不能自动扩写成“canonical graph正在执行”。

### AgentRunApplicationService 有 cancel primitive，但 production route/binding 未证明

`AgentRunApplicationService.cancel_task()` 已经调用 `AgentRuntimeService.cancel()`，后者通过 canonical checkpointer 写入 terminal cancellation。

但 repo-wide call-site review 对 `AgentRunApplicationService.create_task / approve_task / cancel_task / get_task_snapshot` 的命中集中在测试；没有建立 production HTTP route / worker binding。

Current Runtime Baseline 把 `AgentRunApplicationService` 定义为 Agent Run submit/query/resume/cancel 的 Application Owner。Source evidence 说明这个 Owner contract 与 production routing之间仍有实现缺口。

## CXL-B1 readiness decision

CXL-B1 暂不进入代码实现。

准确状态是：

```text
PRODUCT_CANCEL_COMMAND_TOKEN = CURRENT / IMPLEMENTED
RUNTIME_CANCELLATION_PRIMITIVE = CURRENT / IMPLEMENTED
TOOL_CANCELLATION_PRIMITIVE = CURRENT / IMPLEMENTED
PRODUCT_RUNTIME_EXECUTION_SPEC = CURRENT / SELECTED VERIFIED
PRODUCT_RUNTIME_REQUEST -> CANONICAL AGENT EXECUTION = NOT IMPLEMENTATION-PROVEN
PRODUCTION CANCEL -> SAME AGENT RUN -> IN-FLIGHT TOOL = BLOCKED_UPSTREAM
```

这里不能用以下方式绕开：

- 根据 `runtime_request_ref` 字符串直接伪造一个 Runtime task id；
- 看到 Agent Core owner `AgentRun` row 就假设 graph 已经启动；
- 恢复已从 production cutover 移除的旧 workspace task owner；
- 在 Product action consume 里直接写 ToolCancellationReceipt，跳过 04 Runtime cancellation intent；
- 因为 `ProductRuntimeMechanics.cancel_task()` 存在就重新把它升级成 HTTP owner。Current Runtime Baseline 已明确它只是 mechanics/state component。

## Upstream exit condition

重新打开 CXL-B1 前，PRD-A1 已满足 durable execution input；还需要 PRD-A2 证明后半条正式生产链：

```text
durable Product RuntimeExecutionSpec
→ Agent Core owner receipt
→ stable runtime_request_ref ↔ canonical task/run identity
→ canonical AgentRuntimeService / AgentRunStore start-or-recover
```

证据可以来自最小 integration implementation + PostgreSQL probe，不要求引入新服务。

只有这个 binding成立以后，CXL-B1 才把已有 Product cancel token消费映射到：

```text
same canonical AgentRun
→ durable Runtime cancellation intent
→ current Tool observation / execution identity
→ 06 AsyncJob locator
```

CXL-B2 的 optional provider cancel capability继续依赖 B1，不独立提前实现。

## What remains safe to implement independently

CXL-B blocked 不阻止 06 内部继续修复与 Product cutover无关的事实闭环，例如：

- provider remote-query reconciliation；
- manual reviewer Authority binding；
- Audit class / cancellation-independent Effect recovery；
- Tool Provider capability conformance。

这些工作必须拥有自己的 scoped freeze/evidence，不能借 CXL-B 改 Product runtime topology。

## Non-claims

本状态文档不表示：

- Product runtime request 已经执行；
- cancel action token 已经能停止 canonical AgentRun；
- Tool provider cancel 已实现；
- cancel-in-flight orchestration 已闭环；
- CXL-B 被取消或永久 Defer。

它只说明当前实现顺序必须先修正 Product runtime dispatch到 canonical execution 的 owner binding，再继续 CXL-B1。
