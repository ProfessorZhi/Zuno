# Goal03 Wave B 启动冻结 Gap List

status: frozen
wave: B
branch: goal03-repair/wave-b-memory-readonly-tool
scope: PHASE13, PHASE15
starting_main_sha: a6cd00b182cfc46be883fecfa3e214cede5b07f2
pr_a_merge_sha: a6cd00b182cfc46be883fecfa3e214cede5b07f2
alembic_head_at_start: 20260726_40

## 启动审计结论

Wave B 基于 PR A 合并后的 `origin/main` 启动，工作树在启动时 clean，Alembic 为单一 head `20260726_40`。

冻结 Gap：

- PHASE13：`platform.database.memory.MemoryRepository` 已存在，但默认 Agent post-turn 路径仍主要依赖旧 `MemoryEngine`，新 Repository 仅被局部持久化测试证明。
- PHASE13：ContextPack 选择、压缩和 Memory Use Trace 未由 Agent Core 默认路径固定写入新持久领域事实。
- PHASE15：`platform.database.tool_runtime.ToolRepository` 已存在，但默认 Tool Runtime 仍可通过 LangChain tool、OpenAPI adapter、CLI adapter 等路径直接执行。
- PHASE15：缺少默认生产路径旁路 guard，无法证明 `tool.ainvoke`、`tool.coroutine`、`httpx`、`subprocess` 等入口已收口到唯一 Gateway。
- PHASE15：有副作用 Tool 在 PHASE15 范围内不得返回虚构成功，例如 `mail.send` 不能生成假的 `message_id`。

## 冻结决策

- 只新增 Alembic revision，不回滚 PR A 或既有有效实现。
- PHASE13 以 Application Service 接入默认 Agent post-turn，旧 store 只作为期限 adapter。
- PHASE15 建立唯一 `ToolInvocationGateway`，默认只读路径进入 Gateway；有副作用路径 fail-closed，等待 PHASE16。
- 验证失败按失败指纹处理；PostgreSQL/Docker 连接失败归类为环境恢复，不触发业务代码修改。
