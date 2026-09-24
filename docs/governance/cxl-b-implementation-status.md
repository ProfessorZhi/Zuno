# CXL-B Cancel Orchestration Implementation Status

status: `READY_FOR_IMPLEMENTATION_AFTER_PRD_A2 / IMPLEMENTATION_NOT_STARTED`
source_freeze: [`cxl-b-cancel-orchestration-freeze-candidate.md`](cxl-b-cancel-orchestration-freeze-candidate.md)
current_upstream_evidence: `main@5eaeaf563d6c6ad8f7990a1b7c44d45b1804a660 / run 35516807526`
production_readiness: `NOT_ESTABLISHED`

CXL-B freeze 把取消语义压缩到一个小边界：04 持久化 run / plan / step cancellation intent，06 持有 Tool AsyncJob / CancellationReceipt / final Effect truth，Provider cancel 只是 optional capability。此前 B1 被 Product RuntimeRequest 无法稳定定位同一 canonical task/run 阻塞；PRD-A2 已经关闭这个上游缺口。

这次状态变化只表示 **CXL-B 可以重新进入实现**。Product cancel command 还没有被接到同一个 canonical AgentRun，cancel-in-flight 也没有闭环。

## Current source evidence

### Product surface 已经有取消命令入口

当前前端 workspace 走 Product command surface，`ProductService.submit_runtime_request()` 为 accepted RuntimeRequest 签发：

```text
command_kind = CANCEL_RUNTIME_REQUEST
target_ref = runtime_request_ref
```

`consume_action_token()` / `consume_action_token_as_command()` 已负责 tenant / principal / expiry / single-use token 校验。这里已经有取消命令的安全和幂等外壳，不需要再设计第二套 HTTP token 或 idempotency namespace。

### PRD-A1 / A2 已经提供稳定 runtime 定位

PRD-A1 把执行输入收敛为 Product-owned durable `RuntimeExecutionSpec`。PRD-A2 又让 dispatch consumer在 owner transaction中耐久记录：

```text
runtime_request_ref
canonical_task_id
canonical_run_id
runtime_execution_spec_ref
runtime_execution_spec_hash
```

同一 Product RuntimeRequest跨 restart / redelivery 继续命中同一 canonical task/run；selected PostgreSQL probes已经覆盖 owner commit response loss、runtime start response loss和 duplicate delivery。CXL-B 因而不再需要从字符串猜 task id，也不再需要恢复旧 workspace task owner。

### 取消链本身仍然没有接通

`AgentRunApplicationService.cancel_task()` / `AgentRuntimeService.cancel()` 已经提供 Runtime cancellation primitive，Tool 侧也已有 AsyncJob / CancellationReceipt primitive。当前缺口是 Product `CANCEL_RUNTIME_REQUEST` command 还没有通过 PRD-A2 binding定位同一个 canonical AgentRun，并把 cancel intent交给 04。

因此 Current 边界是：

```text
PRODUCT_CANCEL_COMMAND_TOKEN = CURRENT / IMPLEMENTED
PRD_A1_DURABLE_EXECUTION_SPEC = CURRENT / SELECTED VERIFIED
PRD_A2_CANONICAL_RUNTIME_BINDING = CURRENT / SELECTED VERIFIED
RUNTIME_CANCELLATION_PRIMITIVE = CURRENT / IMPLEMENTED
TOOL_CANCELLATION_PRIMITIVE = CURRENT / IMPLEMENTED
PRODUCT_CANCEL -> SAME CANONICAL RUN = NOT IMPLEMENTED
IN_FLIGHT TOOL PROVIDER CANCEL = OPTIONAL / NOT IMPLEMENTED
```

## CXL-B1 implementation boundary

B1 现在可以按照已经冻结的 Owner 边界继续：

```text
consume Product cancel command
→ load matching PRD-A2 canonical task/run binding
→ record durable 04 Runtime cancellation intent
→ stop future plan/step work
→ inspect current Tool observation / AsyncJob identity
→ let 06 preserve final Effect truth
```

B1 不能直接在 Product action consumer里写 ToolCancellationReceipt，也不能把“收到 cancel”解释成已经撤销外部现实 Effect。已经完成或可能已经发生的 Effect继续由 06 处理。

进入 Current 前至少需要 scoped PostgreSQL evidence覆盖：same cancel replay幂等、wrong tenant / wrong runtime binding fail closed、terminal run cancel语义、cancel intent后 restart恢复，以及存在 in-flight Tool时不会因为取消重放制造第二个外部动作。

CXL-B2 的 provider cancel capability继续保持 optional。只有具体 Provider真的支持稳定 cancel locator / semantics，并且业务收益值得增加这条恢复面时再接入。

## What remains independent

CXL-B 不阻止 06 / 08 独立收敛其他事实闭环，例如 provider remote-query reconciliation、manual reviewer Authority、Audit class / AUD-L2、Tool Provider capability conformance。它们继续使用各自的 scoped freeze 和 Evidence。

## Non-claims

本状态不表示：

- Product cancel 已经能停止 canonical AgentRun；
- Tool provider cancel 已实现；
- cancel-in-flight orchestration 已闭环；
- PRD-A2 证明了完整 Product Runtime；
- Full CI、真实 Provider E2E 或 Production Readiness 已建立。

它只说明 PRD-A2 已经提供 CXL-B 所需的稳定 runtime identity，上游 blocker 已关闭，CXL-B1 可以继续实现。
