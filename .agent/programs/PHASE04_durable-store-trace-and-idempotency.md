# PHASE04_durable-store-trace-and-idempotency

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE04
    state: completed
    title: 持久化 Run Store、Trace 与幂等
    depends_on: PHASE03
    next_phase: PHASE05

    ## 目标

    把 in-memory durable semantics 迁移为 SQLite-backed runtime facts，使 run、checkpoint、plan、observation、interrupt、EvidenceLedger 和 tool execution 在重启后可恢复。

    ## 当前事实

    SingleControllerDurableRuntime 有 checkpoint/interrupt/resume contract，但 store 是内存；Memory 已有 SQLModel-backed store。

    ## 完成事实

    PHASE04 已新增 `AgentRunStore` protocol、`SQLiteAgentRunStore`、runtime SQL table definitions 和 `SQLiteLocalTraceStore`。SQLite store 兼容现有 `SingleControllerDurableRuntime` store 方法，并持久化 run、checkpoint、event、interrupt、plan version、observation 和 tool idempotency claim。测试已证明新 store 实例可从同一 SQLite db 读取 pending interrupt 并 resume 到 completed，重复 tool idempotency key 不会重复 claim，corrupt JSON snapshot 会显式失败。

    当前完成状态不表示 LangGraph 主图已经接入持久 store；完整 graph restart、产品 API 恢复和 UI recovery 仍归 PHASE05/PHASE11。

    ## 目标增量

    建立 AgentRunStore protocol 和 SQLite implementation。payload 用 versioned JSON，不用 pickle；所有查询带 workspace/user scope。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/{store,sqlite_store}.py
src/backend/zuno/platform/database/models/agent_runtime.py
src/backend/zuno/platform/observability/local_trace_store.py
tests/agent/runtime/test_runtime_store.py
tests/agent/runtime/test_runtime_restart_persistence.py
```

    ## 实施步骤

    1. Store protocol：create/load/save checkpoint/event/interrupt/plan/observation/tool claim。
2. 建 SQLModel tables 和索引。
3. event `(run_id, sequence)` 唯一。
4. tool idempotency key 唯一。
5. interrupt pending/approved/rejected/expired/consumed。
6. checkpoint 保存 node、route、state_version。
7. InMemory store 变测试实现。
8. restart test 用新 store 实例读取并 resume。
9. 大 payload 进入 object store。

    ## 关键代码草图

    ```python
class AgentRunStore(Protocol):
    def create_run(self, snapshot): ...
    def save_checkpoint(self, snapshot, *, node: str, route: str) -> str: ...
    def load_latest(self, *, run_id: str, workspace_id: str, user_id: str): ...
    def append_event(self, event): ...
    def save_interrupt(self, interrupt): ...
    def claim_tool_execution(self, *, idempotency_key: str): ...
```

    ## 测试

    store contract、scope isolation、sequence uniqueness、version、restart、pending interrupt、duplicate tool claim、corrupt snapshot。

    ## 验收标准

    新进程可读同一 run；不依赖对象引用；tool resume 不重复；trace/checkpoint 同 run/step 关联。

    ## Windows PowerShell 验证

    ```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath 'F:\internship-work\resume&resume project\02_projects\Zuno'
$VenvPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$Python = if (Test-Path -LiteralPath $VenvPython) { (Resolve-Path -LiteralPath $VenvPython).Path } else { 'python' }
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src\backend').Path
```
```powershell
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_store.py','tests\agent\runtime\test_runtime_restart_persistence.py','tests\agent\test_durable_runtime.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'durable store tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    保留 InMemory compatibility。DB 失败不能静默 fallback 内存，应返回 persistence_unavailable。

    ## 文档与状态同步

    可将 store baseline 写 Current，但 graph restart 要等 PHASE05/11。

    ## Phase 完成报告

    - 修改 owner：`src/backend/zuno/agent/runtime/store.py`、`src/backend/zuno/agent/runtime/sqlite_store.py`、`src/backend/zuno/platform/database/models/agent_runtime.py`、`src/backend/zuno/platform/observability/local_trace_store.py`、PHASE04 tests。
    - 新增 contract：`AgentRunStore`、`SQLiteAgentRunStore`、`RUNTIME_STORE_SCHEMA_VERSION`、`SQLiteLocalTraceStore`。
    - 真实调用链：`SingleControllerDurableRuntime(store=SQLiteAgentRunStore(db_path))` -> checkpoint/interrupt/event persisted -> new runtime/store instance -> `resume_task()`.
    - trace/restart/eval 证据：SQLite restart resume test 已覆盖 pending interrupt recovery；没有 benchmark measured 证据。
    - 下一 phase：PHASE05 可以开始 unified LangGraph runtime skeleton。

    Codex 必须报告：

    1. 修改文件和 owner。
    2. 新增或修改的 contract。
    3. 真实调用链。
    4. 测试命令与结果。
    5. trace、restart 或 eval 证据。
    6. 未完成和 blocked 项。
    7. commit SHA。
    8. 下一 Phase 是否满足依赖。
