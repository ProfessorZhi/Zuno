# Tool Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-TOOL-001` 到 `ARCH-TOOL-080`

范围说明：

- 已证明 08 Tool Runtime 是 ToolDefinition、PreparedToolAction、ToolAttempt、ToolObservation、ToolExecutionReceipt、EffectReceipt 和 EffectReconciliation 的 canonical owner。
- 已证明 07 Capability / Skill 只持有 planner projection，exposure 不等于 execute，ActionProposal 只能由 06 Agent Core 提供。
- 已证明 ToolVersion 不可变，Installation 与 Definition 分离，Activation 使用 generation/CAS。
- 已证明 PreparedToolAction 固定 canonical input hash、target resource set、effect profile、security epoch、audit requirement、idempotency key 和 deadline。
- 已证明 PreparedToolAction 不保存 secret material，Approval 绑定完整 hash，执行前必须重检 security epoch。
- 已证明 mandatory audit 先于 effect，claim 先于 dispatch，claim 不可冒充 effect。
- 已证明每次 dispatch 记录 Attempt，Attempt 状态转换受矩阵约束，dispatch certainty 和 execution receipt 显式记录。
- 已证明 effectful tool 需要 EffectReceipt，批量 effect 逐项表达，receipt append-only generation 不可覆盖。
- 已证明 UNKNOWN effect 禁止盲目 retry，只能进入 durable reconciliation；只有 `CONFIRMED_NOT_EXECUTED` 允许重试同一副作用。
- 已证明 Compensation 是新的受治理 action，不是隐藏数据库回滚；Cancellation 不冒充 provider 已停止。
- 已证明 ToolObservation 归 08，NormalizedObservation projection 归 06，Tool output 默认不可信，schema 强校验，不自动写 Memory 或 Knowledge Evidence。
- 已证明 CLI sandbox 使用 env allowlist、进程树终止和资源限制；OpenAPI endpoint、redirect 和 connectivity probe 有独立策略。
- 已证明 SDK adapter version pinned，隐藏 retry 受控，adapter conformance 可失效。
- 已证明 MCP 必须先协商 capability，schema 绑定 snapshot，listChanged 使旧 action obsolete，annotations 默认不可信，多模态输出保留结构。
- 已证明 MCP task 可恢复，redelivery 与 effect idempotency 分离，MCP Sampling 只能经 04 Model Gateway，MCP Elicitation 不能冒充 Security Approval。
- 已证明 async accepted 不等于 completion，callback 需要 signature 和 nonce，资源冲突键、replan epoch、timeout stages 和 deadline 显式记录。
- 已证明 Tool failure 保持 `TOOL` namespace，Outbox 与领域事实同事务，Secret 只以 lease 交付，隔离不足 fail closed。
- 已证明 capacity 不绕过 exposure、prepare、security、audit、claim、dispatch、receipt、effect gate。
- 已证明 canary 不复制真实 effect，drain 保持恢复，retired tool 历史 effect 可读，大 payload 使用 ObjectRef，legal hold 阻止删除。
- 已证明 SLO 关注 confirmed effect，当前 legacy allowlist 有收缩记录和最终归零 gate。
- 已证明 Target 转 Current 必须具备代码、测试、verifier 和 evidence 引用。

未覆盖：

- Tool Runtime 模块 `ARCH-TOOL-001` 到 `ARCH-TOOL-080` 已由本批 evidence 覆盖；其他模块仍需后续批次证明。
- 本证据不声明 PHASE15 或全 Program 关闭。

验证命令：

```powershell
python -m py_compile src/backend/zuno/capability/tool_runtime/runtime_batch.py tools/scripts/verify_tool_runtime_batch.py
pytest -q tests/capability/test_tool_runtime_batch.py tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
python tools/scripts/verify_tool_runtime_batch.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
pytest -q tests/capability/test_tool_runtime_batch.py tests/agent/test_capability_layer_surfaces.py tests/agent/runtime/test_runtime_tool_control_plane.py tests/agent/runtime/test_runtime_tool_idempotency.py tests/agent/test_tool_control_plane_runtime.py tests/agent/test_tool_control_plane_contract.py tests/tools/test_cli_tool_adapter.py tests/tools/test_openapi_tool_adapter.py tests/tools/test_user_defined_tool_runtime.py -p no:cacheprovider
```

结果：

```text
7 passed in 2.02s
Tool runtime batch verifier passed for ARCH-TOOL-001..080
Requirement ledger evidence gate passed.
documentation entrypoint verification passed.
28 passed in 37.15s
```
