# PROGRAM01 Real Unified Runtime Cutover

```yaml
program: zuno-real-unified-runtime-cutover-v1
state: activated_from_queue
active_program: zuno-real-unified-runtime-cutover-v1
baseline_commit: 2bcba3fd0a6391b1718b291d54560e292c9ebfbd
program_type: implementation_and_product_cutover
```

## 适用性判断

这个 program 已在 `d90dc0013c1721a56828a6dc6f889e209454b346` 之后由用户授权激活。当前 active truth source 是 `.agent/programs/current.md` 和平铺 PHASE 文件；本文件只保留 queued candidate 的来源设计，不再作为执行状态事实源。

原因：

1. 它没有继续增加新的架构层，而是针对当前最大缺口：产品主路径、LangGraph 执行引擎、真实 Model / Memory / Knowledge / Tool 数据面仍未完全统一。
2. 它把 PHASE01 定义为事实冻结和 guardrail verifier，适合作为进入高风险 runtime cutover 前的最短安全入口。
3. 它明确禁止 fake evidence、fake citation、canned answer、缺失依赖仍标 completed，以及 benchmark blocked 被写成 measured。
4. 它承认质量门需要真实 paired benchmark 证明，不把 implementation tests 通过等同 quality pass。

需要收缩的边界：

0. 不得把 activated_from_queue 设计稿写成 Completed 或 measured。
1. `.agent/programs/current.md`、`implementation-roadmap.md`、`closure-checklist.md` 和 PHASE 文件才是 active program truth source。
2. PHASE02-PHASE06 会修改核心 runtime、API 和产品默认路径；执行时必须逐 phase 小步提交，不能一次性大切。
3. PHASE07 benchmark 可以关闭为 `measurement_blocked`，但必须给出 `blocked_reason`、`measured_case_count=0` 和可复现配置缺口。
4. GeneralAgent 只能作为 rollback adapter 的目标状态，不能在文档中写成已经退出默认产品路径，除非代码和测试证明。

## Program 目标

把当前并存的两条路径：

```text
GeneralAgent
-> LangChain create_agent
-> model / tool / knowledge / memory

UnifiedAgentRuntimeService
-> runtime contracts
-> 手写节点循环
-> deterministic observation
-> SQLite checkpoint
```

收敛为：

```text
Completion / Workspace API
-> UnifiedAgentRuntimeService
-> compiled LangGraph
-> RuntimeDependencyFactory
   -> Model Gateway
   -> Memory Engine
   -> Corrective Agentic GraphRAG
   -> Tool Control Plane
-> Plan-and-Execute
-> ReAct step
-> Observation
-> Reflection
-> Replan
-> Reflexion
-> GroundedAnswer
-> Product SSE / Artifact
```

最终目标是一个产品主 Controller：

```text
UnifiedAgentRuntimeService
```

`GeneralAgent` 可作为短期 rollback adapter；`SingleControllerDurableRuntime` 只能保留为 deprecated compatibility facade 或旧测试迁移入口。

## 不可违反原则

1. LangGraph 必须成为 Agent Core 的唯一执行引擎。
2. 缺少 dependency 时必须输出 blocked observation，不能伪造 success、evidence、citation 或 completed step。
3. Planner、Executor、ReAct、Critic 和 Synthesis 必须统一经过 Model Gateway。
4. Completion / Workspace 最终答案必须来自 `AgentRuntimeState.final_answer` 或等价 runtime state 字段，不能返回 canned text。
5. Legacy path 必须在显式 rollback flag 后面。
6. `blocked`、`prepared`、`runtime observed`、`partial profile` 不能写成 measured。

## PHASE01：Program 激活与事实冻结

执行时新增 active program 文件：

```text
.agent/programs/current.md
.agent/programs/implementation-roadmap.md
.agent/programs/closure-checklist.md
.agent/programs/PHASE01_real-runtime-baseline.md
.agent/programs/PHASE02_langgraph-execution-cutover.md
.agent/programs/PHASE03_runtime-dependency-factory.md
.agent/programs/PHASE04_real-agent-execution.md
.agent/programs/PHASE05_product-runtime-integration.md
.agent/programs/PHASE06_product-cutover.md
.agent/programs/PHASE07_benchmark-and-closure.md
```

PHASE01 只做事实冻结和 guardrail，不修改生产 runtime。

必须冻结的当前事实：

```text
compiled StateGraph exists
UnifiedAgentRuntimeService does not yet prove compiled graph is the only execution engine
ReActStepExecutor / ModelStepExecutor must not use deterministic completion as product success
Completion unified mode must not return fixed canned completion text
Workspace unified runtime must be proven as product main path before marked current
EnterpriseRAG paired benchmark remains blocked_not_measured unless real fixed run proves otherwise
```

建议新增 verifier：

```text
tools/scripts/verify_real_runtime_cutover.py
```

最低检查项：

```text
UnifiedAgentRuntimeService references build_agent_graph or compiled graph entrypoint
UnifiedAgentRuntimeService does not contain manual product runtime while loop
ModelStepExecutor calls Model Gateway
ReActStepExecutor calls a real ReAct runner or returns blocked_not_available
Completion unified path does not contain "Unified runtime completed." as product answer
KnowledgeStepExecutor does not fabricate evidence when runtime is missing
default product path resolves to unified runtime after PHASE06
legacy path is behind explicit rollback flag after PHASE06
```

## PHASE02：LangGraph 执行切换

范围：

```text
src/backend/zuno/agent/runtime/service.py
src/backend/zuno/agent/runtime/graph.py
src/backend/zuno/agent/runtime/checkpointer.py
src/backend/zuno/agent/runtime/routing.py
src/backend/zuno/agent/runtime/state.py
tests/agent/runtime/
```

目标：

1. `UnifiedAgentRuntimeService` 通过 compiled LangGraph 的 `ainvoke` / `astream_events` / resume contract 执行。
2. 手写 `_run_from`、`_next_node` 或主运行 `while current_node != END` 退出产品主路径。
3. Approval / ASK_USER 使用 interrupt / resume，而不是直接把恢复状态改成 PASS。
4. LangGraph checkpoint 和领域 run store 分清职责。
5. restart 后用新的 service/store instance 恢复同一 task。

验收测试：

```text
test_service_executes_compiled_langgraph.py
test_service_has_no_manual_runtime_loop.py
test_langgraph_interrupt_resume.py
test_langgraph_restart_with_new_service_instance.py
test_langgraph_stream_is_live_not_replay_only.py
```

## PHASE03：RuntimeDependencyFactory

范围：

```text
src/backend/zuno/agent/runtime/factory.py
src/backend/zuno/agent/runtime/configuration.py
src/backend/zuno/agent/runtime/protocols.py
tests/agent/runtime/
tests/api/
```

目标：

1. 建立唯一依赖装配入口。
2. `RuntimeDependencies` 使用 typed protocols，不再让核心依赖默认为 `Any | None`。
3. Completion 从 dialog / workspace / user scope 解析模型、知识库、工具、记忆和审批策略。
4. Workspace 复用统一 runtime，不先走旧 retrieval 再旁路 unified runtime。
5. 知识库、模型、工具缺失时输出 blocked observation 和 failure reason。

最低依赖：

```text
model_gateway
memory_engine
knowledge_runtime when knowledge selected
tool_control_plane
trace_sink
```

## PHASE04：真实 Agent 执行数据面

范围：

```text
src/backend/zuno/agent/runtime/execution/model_step.py
src/backend/zuno/agent/runtime/execution/react_runner.py
src/backend/zuno/agent/runtime/synthesis/
tests/agent/runtime/
```

目标：

1. `ModelStepExecutor` 调用 Model Gateway，并记录 provider、model、role、latency、token usage、cost、fallback 和 trace event。
2. Planner 对复杂任务使用 structured model output，并经过 PlanValidator；无效时 blocked 或 abstain。
3. ReAct 只执行当前 PlanStep，不接管全局 finalize、replan 或 memory commit。
4. Grounded Synthesis 从 EvidenceLedger 生成 answer、claims、citations、unsupported_claims 和 evidence refs。
5. Reflection 先走 deterministic gate，高风险或模糊场景再走可选 critic；critic 也必须经过 Model Gateway。

验收至少覆盖：

```text
direct answer
plan-and-execute multi-step
ReAct tool step
model gateway call count > 0
non-canned final answer
final_answer equals streamed product answer
```

## PHASE05：Knowledge、Tool、Memory 真实接入

范围：

```text
src/backend/zuno/agent/runtime/execution/knowledge_step.py
src/backend/zuno/knowledge/
src/backend/zuno/capability/
src/backend/zuno/memory/
tests/agent/runtime/
tests/e2e/
```

目标：

1. KnowledgeStepExecutor 调用 Corrective Agentic GraphRAG，产出 EvidenceLedger ref。
2. Query Rewrite / Multi Query / HyDE / Step-back 不再只是固定字符串拼接。
3. 至少完成 `filesystem.read` 和 `filesystem.write` 两个真实工具，带路径约束、审批、幂等和审计 trace。
4. MemoryEngine 进入 pre-turn ContextPack、in-turn trace 和 post-turn raw event / summary / Reflexion candidate。
5. Reflexion lesson 进入 pending review，approved 后能影响后续相似任务。

最低纵向验收：

```text
PDF ingest
-> index
-> unified LangGraph runtime
-> first retrieval insufficient
-> query rewrite
-> second retrieval
-> EvidenceLedger
-> synthesis model
-> claim binding
-> page citation
-> final answer
-> memory summary
```

## PHASE06：产品默认切换与旧路径退出

范围：

```text
src/backend/zuno/api/
src/backend/zuno/agent/
apps/web/
tests/api/
tests/e2e/
```

目标：

1. `POST /completion` 默认走 unified runtime。
2. rollback 使用显式 flag，例如 `ZUNO_AGENT_RUNTIME=legacy_general_agent`。
3. SSE 实时输出 runtime_started、node_started、model_call、retrieval_round、tool_call、approval_required、reflection、replan、answer_chunk、citation、runtime_completed。
4. Workspace task 的 final answer / artifact 来自 unified runtime。
5. UI 最小展示执行阶段、当前 plan step、检索轮次、引用、approval 状态、最终回答、blocked/abstain 原因。

验收：

```text
普通 Completion 请求 -> unified runtime -> real model -> real answer
Workspace PDF task -> unified runtime -> cited artifact
approval tool -> interrupt -> page refresh -> approve -> resume -> execute once
server restart -> new service/store instance -> resume task
```

## PHASE07：Benchmark 与 Program 收口

目标：

1. 解决 sample-8 当前配置 blocker，配置 local embedding model / base_url，但不在代码中写死本机地址。
2. fixed paired set 如不存在，创建 tracked manifest，记录 dataset source、hash、selection policy、case IDs、exclusions。
3. standard_rag、deep_graphrag、agentic_graphrag 使用相同 case IDs、index version、model config 和 runtime config。
4. Release Gate 分开输出 implementation_status、measurement_status、quality_gate_status。

合法关闭结果：

```text
implementation_complete + measurement_pass + quality_pass
implementation_complete + measurement_pass + quality_fail
implementation_complete + measurement_blocked + quality_not_proven
```

禁止关闭结果：

```text
implementation tests passed => quality pass
partial profile output => fixed paired benchmark measured
prepared benchmark => measured
doc-level citation => strict citation pass
```

## 执行验证基线

每个 phase 至少运行：

```powershell
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_current_program.py
pytest -q tests/agent/runtime tests/api -p no:cacheprovider
git diff --check
```

涉及 repo guardrail 时追加：

```powershell
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_current_program_contract.py -p no:cacheprovider
```

涉及产品路径时追加真实 HTTP / browser / SSE 验证，并保存 trace、report 和 blocked reason。

## 启动前检查

真正激活本 program 前必须先完成：

1. 重新确认 branch、`git status --short --branch`、远端同步状态。
2. 读取 `AGENTS.md`、`.agent/programs/current.md`、本 queued program、上一轮归档 closure summary、runtime 相关代码和测试。
3. 把本 queued 文档拆成 active flat PHASE 文件。
4. 更新 `.agent/programs/current.md` 为 active program。
5. 更新 `.agent/programs/README.md`、`implementation-roadmap.md`、`closure-checklist.md`、`.agent/references/current-program.md`、`.agent/system.yaml`、verifier 和 repo tests。
6. PHASE01 先只落 facts 与 guardrail，guardrail 通过后再进入 runtime cutover。
