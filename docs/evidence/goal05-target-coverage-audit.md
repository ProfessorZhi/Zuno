# Goal05 Target Coverage Audit

status: frozen-gap-ledger
audit_date: 2026-07-28
base_branch: main
base_sha: 5b6f880df88fd1d1f3efc782eedd8466aff45554
audit_scope: 11 modules mandatory target coverage

## 结论

本轮按最新 `origin/main` 执行一次性 Target Coverage Audit。结论是：PHASE20 不能启动，PHASE15 必须重新打开。主因不是缺少文档或 DTO，而是 Agent Sandbox 没有真实默认运行证据：

- WASM Python sandbox 要求 Deno + Pyodide/WASM；当前机器 `deno --version` 不存在。
- OCI Process sandbox 要求短生命周期容器执行；当前 Docker CLI 存在，但 daemon 未运行，`docker info` 不能连接。
- Postgres integration evidence 当前也被 `localhost:5432` 连接超时阻塞。

本轮已完成一项真实 repair：`ToolInvocationGateway` 默认路径新增 sandbox profile resolution、session isolation、limits/allowlist hash、`tool_sandbox_receipts` 持久化和 dispatch 前 fail-closed gate。该修复只证明 sandbox contract 已进入默认 gateway，不证明 Deno/Pyodide 或 OCI container 已真实执行。

## Frozen Gap Ledger

冻结文件：

```text
.agent/programs/work-products/goal05-target-gap-ledger.yaml
```

冻结后不得重复全仓扫描来改写本轮 ledger。后续修复必须按 Owner Phase 补 closure evidence，并只更新 `closure_evidence`。

## Module Matrix Summary

| Module | Verdict | Owner Phase | Gap |
| --- | --- | --- | --- |
| 01 Product Surface | GAP | PHASE21/22 | Web/Desktop E2E、撤权、Rollback rehearsal 和 Legacy-free 清理尚未完成。 |
| 02 Input / Document Ingestion | GAP | PHASE21 | Delete/Privacy/Restore E2E 与 full fault matrix 尚未完成。 |
| 03 Knowledge / Agentic GraphRAG | GAP | PHASE20/21/22 | GraphRAG metric、fixed benchmark、delete/restore 与 release gate 未完成。 |
| 04 Model Gateway | GAP | PHASE20/21/22 | Judge/embedding/model profile comparability 与 fixed benchmark 证据未完成。 |
| 05 Memory & Context | GAP | PHASE21 | Privacy delete、restore 后不回生和 memory negative-transfer E2E 未完成。 |
| 06 Agent Core | GAP | PHASE21 | Domain/checkpoint/queue crash matrix、full E2E 和 cutover 证据未完成。 |
| 07 Capability / Skill | GAP | PHASE21/22 | Capability/tool exposure 在 full attack/E2E 和 legacy-free cleanup 中尚未收口。 |
| 08 Tool Runtime | GAP | PHASE15/21/22 | Sandbox 真实执行、UNKNOWN E2E、legacy-free cleanup 未完成。 |
| 09 Security | GAP | PHASE15/21 | Sandbox enforcement、SSRF/DNS rebinding、approval replay、epoch revocation E2E 未完成。 |
| 10 Observability & Eval | GAP | PHASE20 | Eval runtime、Core Five、BenchmarkComparison、ReleaseGateEvaluation 未完成。 |
| 11 Infrastructure | GAP | PHASE15/21/22 | Deno/OCI/Postgres runtime evidence、backup/restore/load/soak/final tree cleanup 未完成。 |

## PHASE15 Repair Evidence

新增代码与迁移：

```text
src/backend/zuno/capability/tool_runtime/sandbox.py
src/backend/zuno/capability/tool_runtime/invocation_gateway.py
src/backend/zuno/platform/database/tool_runtime/domain.py
infra/db/alembic/versions/20260728_52_goal05_tool_sandbox_receipts.py
```

已通过：

```text
python -m py_compile src/backend/zuno/capability/tool_runtime/__init__.py src/backend/zuno/capability/tool_runtime/invocation_gateway.py src/backend/zuno/capability/tool_runtime/sandbox.py src/backend/zuno/platform/database/tool_runtime/domain.py
pytest -q tests/capability/test_phase15_agent_sandbox.py tests/capability/test_phase16_tool_effect_policy.py tests/capability/test_phase16_tool_bypass_guard.py tests/repo/test_goal03_wave_b_migration_contract.py -p no:cacheprovider
```

结果：`14 passed`。

Blocked：

```text
pytest -q tests/integration/test_goal03_wave_b_persistence.py::test_phase15_gateway_records_sandbox_receipt_before_readonly_dispatch -p no:cacheprovider
```

原因：PostgreSQL `localhost:5432` connection timeout。

## Stop Decision

PHASE20 保持 blocked，直到 PHASE15 Sandbox Closure 取得真实 Deno/Pyodide 和 OCI process sandbox runtime evidence，并完成 Postgres integration evidence。不得用当前 deterministic receipt contract 冒充完整 sandbox。
