# Goal05 PHASE15 Sandbox Repair Evidence

status: repair_partial_wasm_runtime_blocked
date: 2026-07-29
branch: codex/goal05-phase15-sandbox-repair
base_pr: https://github.com/ProfessorZhi/Zuno/pull/52

## Repair Scope

本修复只针对 frozen gap ledger 中的 PHASE15 Agent Sandbox Gap。没有重复全仓审计，也没有启动 PHASE20。

已完成：

- `SandboxAdapterRegistry` 新增真实 `execute()` runner contract。
- `SandboxAdapterRegistry.execute()` 在 runner 启动前校验 Stateful Session 的 hash、版本、过期时间和大小上限。
- `SandboxAdapterRegistry.prepare()` 写入默认 session store；`execute()` 要求 session store 中存在匹配记录，防止只靠客户端 dispatch payload 自证。
- `ToolInvocationGateway` 默认使用 Tool Runtime DB-backed sandbox session store；migration `20260728_52` 新增 `tool_sandbox_sessions`，并用 FK 将 `tool_sandbox_receipts.session_ref` 绑定到 session。
- `InMemorySandboxSessionStore` roundtrip 保留 session metadata，用于验证 stateful session contract；DB-backed default store 由 `ToolInvocationGateway` 注入。
- integration 侧 PHASE15 用例已更新为同时断言 `tool_sandbox_sessions` 与 `tool_sandbox_receipts`，证明默认路径先写 session 再写 receipt。
- integration 侧还新增默认 gateway 用例：Deno 缺失时默认 DB-backed session store 会先写 `tool_sandbox_sessions`，再写入 blocked `tool_sandbox_receipts` 审计证据，然后 fail-closed。
- `SandboxAdapterRegistry.execute()` 还校验 runner 输出结构、session ref、adapter tier 与输出大小上限。
- WASM Python runner 使用 Deno 权限边界，并要求显式 Pyodide entrypoint；缺 Deno 或缺 Pyodide entrypoint fail-closed。
- WASM Python runner 将显式 file path allowlist 映射到 `--allow-read`，将显式 domain allowlist 映射到 `--allow-net`；无 domain allowlist 时保持 `--deny-net`。
- OCI Process runner 使用 Docker CLI 短生命周期容器命令边界：`--rm`、`--network none`、`--read-only`、`--cap-drop ALL`、`no-new-privileges`、non-root、tmpfs workspace、memory/cpu/pid/output/time limit。
- OCI Process runner 默认 `--network none`；存在显式 egress allowlist 时必须提供 proxy，否则 fail-closed；提供 proxy 时注入 `HTTP_PROXY`、`HTTPS_PROXY` 和 `ZUNO_EGRESS_ALLOWLIST`，且不允许宿主 volume/mount。
- Deno 和 Docker runner 调用外部进程时显式使用空环境变量，不继承宿主 env；容器内 proxy 只通过 Docker `--env` 显式注入。
- `ToolInvocationGateway` 对 Python、CLI、OpenAPI、Browser、Shell、Git 等 sandboxable adapter 在 provider executor 前执行 sandbox；sandbox 失败记录 `NOT_DISPATCHED`，不会调用 provider executor。
- `ToolInvocationGateway` 不再把 sandbox output 直接作为 readonly/domain result；sandbox output 只能进入 `ToolObservation` / receipt 边界，真实 result 必须来自 provider executor。
- Sandbox execute 失败后仍写入 `tool_sandbox_receipts`，记录 `sandbox_execution_status=BLOCKED` 和 blocked reason。
- Sandbox 输出在 gateway 进入 receipt/observation 边界前会做敏感信息脱敏。
- Python/CLI sandbox 成功时，sandbox output 形成 `ToolObservation` 输入，不直接成为领域成功。
- Approved side-effect 路径中 sandbox output 不会生成 confirmed `ToolEffectReceipt`；真实 effect receipt 只来自 provider executor 的 effect 结果。
- `zuno.platform.database` 初始化现在读取标准 `ZUNO_CONFIG` / `.local/config/zuno/config.local.yaml` 解析路径，防止迁移、测试 fixture 与默认 runtime security/infrastructure UoW 混用不同数据库。
- `ToolRepository.publish_provider()` 修复为按 `provider_id` upsert；`ToolRepository.record_attempt()` 修复为同一 attempt 可从 `STARTED` 推进到 `SUCCEEDED` / `FAILED` / `UNKNOWN`。

未完成：

- 当前机器没有 Deno，因此不能证明 Deno + Pyodide/WASM 真实执行。
- Docker daemon 已启动，Docker CLI 与 Zuno Postgres 可用；本轮已用隔离数据库 `zuno_goal05_phase15` 跑通 migration-backed integration。
- 本轮尚未新增真实 OCI container execution 集成证据，因此 PHASE15 仍不能关闭。

## Verification

```text
python -m py_compile src/backend/zuno/capability/tool_runtime/sandbox.py src/backend/zuno/capability/tool_runtime/invocation_gateway.py src/backend/zuno/capability/tool_runtime/__init__.py src/backend/zuno/platform/database/tool_runtime/domain.py src/backend/zuno/platform/database/tool_runtime/__init__.py tests/capability/test_phase15_agent_sandbox.py tests/integration/test_goal03_wave_b_persistence.py
pytest -q tests/capability/test_phase15_agent_sandbox.py tests/repo/test_goal03_wave_b_migration_contract.py tests/integration/test_goal03_wave_b_persistence.py -p no:cacheprovider
```

Result:

```text
49 passed
```

运行环境：

```text
ZUNO_CONFIG=.local/config/zuno/config.local.yaml
ZUNO_TEST_POSTGRES_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zuno_goal05_phase15?connect_timeout=5
```

Environment probes:

```text
deno --version
docker --version
docker info --format '{{.ServerVersion}}'
```

Result:

```text
Deno CommandNotFoundException
Docker CLI / daemon 29.4.0 available
zuno-postgres healthy on localhost:5432
```

## Closure Decision

PHASE15 remains `blocked`. 本 repair 证明 sandbox execution contract、DB-backed session/receipt、Postgres migration-backed default gateway 已恢复到真实默认路径；但 Deno + Pyodide/WASM 真实执行和 OCI container execution 仍缺少完整可复现证据。
