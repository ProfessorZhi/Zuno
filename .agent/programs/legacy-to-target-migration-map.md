# Legacy → Canonical Target 迁移地图

status: program-control-document
verification_owner: PHASE01 / PHASE02

本文给 Codex 提供初始导航，减少重复搜索。所有 Current Anchor 必须在 PHASE01 以最新 `main` 再验证；路径存在不等于行为已经符合 Target。

## 1. 物理根目录约束

后端继续使用六个根：

```text
src/backend/zuno/api
src/backend/zuno/agent
src/backend/zuno/memory
src/backend/zuno/capability
src/backend/zuno/knowledge
src/backend/zuno/platform
```

不得为逻辑模块新增顶层 `product`、`tool_runtime`、`security` 或 `observability` 根。逻辑模块映射：

| 模块 | Target 物理位置 |
| --- | --- |
| 01 Product Surface | `api/product/**`、`api/services/product/**`、`api/projection/**`、`platform/database/product/**`、`apps/web/src/product/**`、`apps/desktop/src/product/**` |
| 02 Ingestion | `knowledge/ingestion/**`、`knowledge/storage/**`、`platform/database/ingestion/**`、Worker/Adapter |
| 03 Knowledge | `knowledge/domain/**`、`knowledge/application/**`、`knowledge/retrieval/**`、`knowledge/index/**`、`platform/database/knowledge/**` |
| 04 Model Gateway | `platform/model_gateway/**` |
| 05 Memory | `memory/**`、`platform/database/memory/**` |
| 06 Agent Core | `agent/domain/**`、`agent/application/**`、`agent/runtime/**`、`platform/database/agent/**` |
| 07 Capability / Skill | `capability/domain/**`、`capability/application/**`、`capability/registry/**` |
| 08 Tool Runtime | `capability/tool_runtime/**`、`platform/database/tool_runtime/**` |
| 09 Security | `platform/security/**`、`platform/database/security/**` |
| 10 Observability & Eval | `platform/observability/**`、`tools/evals/zuno/**`、`platform/database/observability/**` |
| 11 Infrastructure | `platform/database/**`、`platform/storage/**`、`platform/queue/**`、`platform/checkpoint/**`、`infra/**` |

## 2. 主要迁移面

| Current / Legacy Anchor（PHASE01 验证） | Canonical Owner | 迁移方式 | Cutover Gate | Contract 后处理 |
| --- | --- | --- | --- | --- |
| `agent/runtime/service.py` 的局部 Unified Runtime | 06 | 扩展为正式 Domain/Persistence/Graph，不在旧 Snapshot 上堆全部语义 | AgentRun/Plan/Step/Action 状态与恢复测试通过 | 删除 PHASE 注释和临时 Store 语义 |
| `agent/durable_runtime.py` 本地 durable surface | 06/11 | 先 Adapter，后 PostgreSQL Domain + LangGraph Checkpointer 对账 | 进程重启、Interrupt、Generation Reconcile 通过 | 本地实现仅保留 CI Adapter |
| GeneralAgent / LangChain Tool Loop | 06/08 | Feature Flag 双路径；先只读，再副作用，最后主路径切换 | 新路径 E2E、Rollback、无旁路验证通过 | Legacy Flag 限时保留后删除 |
| `api/services/completion.py` 和 workspace runtime | 01/06 | Route 变薄，调用 Product Command/Query Port 与 Agent Core | Contract Test、SSE Resume、Approval Signal 通过 | 旧 DTO 只作为版本化 Adapter |
| SQLite/SQLModel 本地 Store | 11 + 各 Owner | PostgreSQL Expand、Backfill、Dual Read/Write、Cutover | Migration、并发、恢复和回滚通过 | SQLite 仅 Developer/CI Adapter |
| 本地文件 Object Store | 11/02 | S3-compatible ObjectRef + Hash + Manifest | Commit/visibility/delete/restore 测试通过 | 本地文件仅 CI Adapter |
| in-process/local Queue | 11 | RabbitMQ Outbox/Inbox、Lease、Fencing | Duplicate/Redelivery/DLQ/Crash 通过 | 进程内 Queue 仅 CI Adapter |
| 自定义 Runtime Checkpoint Bridge | 06/11 | LangGraph-compatible PostgreSQL Checkpointer + Domain Generation 对账 | native interrupt/resume、restart、orphan reconcile 通过 | 旧 Bridge 退为兼容 Adapter 或删除 |
| 直接 OpenAI/Anthropic/DashScope/Embedding 调用 | 04 | Provider Adapter 全部进入 Model Gateway | Bypass Guard 归零、Usage/Cancel/Fallback 通过 | 禁止业务层 Provider SDK Import |
| `knowledge/**` 局部 Retrieval/GraphRAG | 03 | 先 Standard Hybrid，再 KnowledgeVersion，再 Agentic 内层循环 | Evidence/Citation、Snapshot、Corrective Retrieval 测试通过 | 旧 Query Service 变 Adapter 后删除 |
| `memory/**` 本地 Memory Engine/Store | 05 | 版本化 ContextPack、Candidate、Governance、Activation | Privacy Delete、Revocation、Reuse Trace 通过 | 旧四层命名仅兼容读取 |
| `capability/**` Registry/Selector | 07 | Definition/Version/Availability/Feasibility/Progressive Loading | Planner Contract 和 Tool Projection 通过 | 07 不再拥有 Tool Effect 事实 |
| Tool handler、MCP coroutine、CLI/OpenAPI 直接 execute | 08 | Invocation Gateway + Adapter SPI；Read-only→Side-effect→UNKNOWN | Boundary Allowlist 归零、Effect Fault Test 通过 | 所有直接执行入口删除或 Adapter 化 |
| local trace/eval helper | 10 | Envelope→Append-only Ingest→Projection/Audit→Eval | Dedup/Gap/Rebuild/Core Five/Gate 通过 | 外部 Sink 不成为内部 Owner |
| 旧 Web API/store/page 直接消费 Runtime 状态 | 01 | `apps/web/src/product/**` Contract/Store/Projection/SSE | Multi Interrupt、Resync、Revocation、UNKNOWN UI E2E | 删除字符串推断和旧 DTO 泄漏 |
| Desktop 直接复用旧 API/Bridge | 01 | `apps/desktop/src/product/**` 版本化 Bridge/Authorization/Delivery | Desktop Smoke + Contract Test | 旧 Bridge 仅兼容旧客户端版本 |
| `platform/compatibility/legacy_aliases.py` | Governance | Allowlist + Owner + Removal Phase | 新 Import 路径稳定、测试无旧 Import | PHASE22 删除无必要 Alias |

## 3. 固定迁移模式

每个迁移面采用：

```text
Expand：增加新 Contract、表、Port、Adapter，不破坏旧调用
Migrate：真实请求按 Flag/Version/Shadow 进入新路径
Verify：Contract、Integration、Fault、E2E、Trace/Eval 证明
Contract：删除旧 Owner、旁路、Flag 或兼容写入
```

禁止一次性 Bulk Move。

## 4. Feature Flag 状态

所有切流 Flag 使用统一生命周期：

```text
DECLARED
→ SHADOW
→ CANARY
→ DEFAULT_NEW
→ ROLLBACK_WINDOW
→ RETIRED
```

每个 Flag 必须记录 Owner、默认值、Scope、观测指标、Rollback 命令、最大保留日期和删除任务。Feature Flag 不能永久成为双架构。

## 5. 数据迁移状态

```text
SCHEMA_EXPANDED
→ BACKFILLING
→ DUAL_READ
→ DUAL_WRITE（只有确需时）
→ READ_CUTOVER
→ WRITE_CUTOVER
→ VERIFIED
→ LEGACY_FROZEN
→ LEGACY_REMOVED
```

任何阶段失败必须能回到上一个安全读路径；跨模块删除不假装单事务原子完成。

## 6. Frontend 迁移原则

- 后端先提供版本化 Product DTO、Projection 和 AvailableAction。
- Web/Desktop 先增加新 Client 和 Store，不立即删除旧页面。
- Shadow 比较旧/新 Projection，记录不一致。
- SSE 使用 Opaque Cursor、去重、Gap、Resync 和重新授权。
- 多 Interrupt 不压缩为单个 `pendingApproval`。
- UNKNOWN Effect 只展示 Owner 提供的受控动作，不显示普通 Retry。
- Provisional Content 不写成正式 Assistant Publication。
- 新页面 E2E 通过后切默认路由，保留短期 Rollback，再删除旧 Store/API。

## 7. 完成判定

迁移完成不是“新目录存在”，而是：

- 新路径承接真实流量；
- 旧路径被 Guard 阻止新增调用；
- 数据和状态可恢复；
- Web/Desktop 使用新 Contract；
- Fault/E2E 和 Benchmark 证据可重现；
- Legacy Allowlist、Flag、Alias 和双写已删除或有正式保留 ADR。
