# Goal03 Wave B Gate Review

status: approved
wave: B
branch: goal03-repair/wave-b-memory-readonly-tool
scope: PHASE13, PHASE15
starting_main_sha: a6cd00b182cfc46be883fecfa3e214cede5b07f2
alembic_revision: 20260727_41
alembic_head_after: 20260727_41
coordinator_approval: approved
production_readiness: not_established

## 默认调用链

PHASE13 默认 Memory 调用链：

```text
UnifiedAgentRuntime factory
→ MemoryEngine(store=DatabaseMemoryStore)
→ governed_context_runtime
→ post_turn_commit
→ GovernedMemoryContextRuntime.commit_turn_outcome
→ MemoryUnitOfWork / MemoryRepository
→ CaptureIntent / Candidate / GovernanceDecision / MemoryRecord / MemoryVersion / ContextPack / CompressionTrace / MemoryUseTrace
```

PHASE15 默认 Tool 调用链：

```text
ToolControlPlaneRuntime / GeneralAgent LangChain middleware / user-defined CLI/OpenAPI runtime
→ ToolInvocationGateway
→ ToolUnitOfWork / ToolRepository
→ ToolProvider / Definition / Version / Operation / Installation / Activation / AdapterBinding
→ PreparedToolAction / ToolAttempt / ToolObservation / ToolExecutionReceipt / BypassGuardReceipt
```

Side-effect Tool 在 PHASE15 fail-closed，返回 `PHASE16_REQUIRED_FOR_SIDE_EFFECT_TOOL`，不生成虚构外部 Effect 成功。

## 验证命令

已运行并通过：

```powershell
alembic -c infra/db/alembic.ini heads
python -m py_compile src/backend/zuno/platform/database/memory/domain.py src/backend/zuno/memory/governed_runtime.py src/backend/zuno/capability/runtime.py src/backend/zuno/capability/tool_runtime/invocation_gateway.py src/backend/zuno/platform/services/user_defined_tool_runtime.py src/backend/zuno/agent/core/agents/general_agent.py src/backend/zuno/agent/runtime/factory.py src/backend/zuno/agent/runtime/nodes/core.py
python tools/scripts/verify_memory_context_target_protocols.py
python tools/scripts/verify_tool_runtime_target_protocols.py
python tools/scripts/verify_tool_execution_bypass.py
pytest -q tests/repo/test_goal03_wave_b_migration_contract.py -p no:cacheprovider
pytest -q tests/integration/test_goal03_wave_b_persistence.py -p no:cacheprovider
```

环境恢复记录：

- 初次运行 `pytest -q tests/integration/test_goal03_wave_b_persistence.py -p no:cacheprovider` 在 `migrated_postgres` fixture 连接 `localhost:5432` 超时。
- 失败指纹：`sqlalchemy.exc.OperationalError` / `psycopg.errors.ConnectionTimeout` / `infra/db/alembic/env.py` line 94 / Docker engine 未启动，PostgreSQL 未监听。
- 恢复动作：启动 `com.docker.service` 和 Docker Desktop engine，再通过 `docker compose -f infra/docker/docker-compose.yml up -d postgres` 启动 `zuno-postgres`，healthcheck 为 `healthy`。
- 环境恢复后复跑同一命令，发现并修复 `record_memory_use()` 中误用 `pack` 的代码缺陷；再次复跑通过。

## Gate 结论

- PHASE13 completed：默认 Agent post-turn 路径已进入 governed memory application service，并写入持久 Memory/Context/Use Trace 事实。
- PHASE15 completed：默认只读 Tool 路径进入唯一 Gateway，ToolRepository/UoW 被生产路径调用，有副作用 Tool fail-closed 到 PHASE16。
- PHASE10 ready：Product Backend Runtime 已在 Wave A 完成，前端适配可启动。
- PHASE16 ready：Tool read-only cutover 已完成，side-effect/reconciliation 可启动。
- Goal03 completed；production readiness not established。
