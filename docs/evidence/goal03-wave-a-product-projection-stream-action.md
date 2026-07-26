# Goal03 Wave A Product Projection Stream Action Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE09 中默认 Product API 在提交 `RuntimeRequest` 后必须进入 Product-owned read model 的最小纵切：

- 同一 Product Unit of Work 内提交 `ProductCommand`、`CommandReceipt`、`ProjectionEvent`、`StreamCursor` 和服务端 `ActionToken`。
- `CommandReceipt` 仍只表示 Product 接受或重复，不冒充 Agent Core 领域成功。
- `GET /api/v1/product/stream` 使用 `text/event-stream` 输出 Product Projection Delta / Resync 事件。
- `GET /api/v1/product/stream` 输出 SSE `retry` hint 和 `HEARTBEAT` keepalive；heartbeat 只证明连接存活，不冒充 Projection 成功。
- `GET /api/v1/product/stream-events` 提供同一事件源的 JSON 查询面，支持 `Last-Event-ID`，并在未知或过期 cursor 时返回 `RESYNC_REQUIRED` 语义。
- `Last-Event-ID` 绑定 principal；其他 principal 复用 cursor 时按未知 cursor 处理并返回 `RESYNC_REQUIRED`，不泄露增量事件。
- AvailableAction 由服务端签发 action token，不由前端按状态字符串推断。
- `product_action_tokens` 支持一次性消费和撤销；重复消费或撤销后消费 fail closed。
- Product Projection rebuild 会过期该 workspace 的既有 stream cursor，并追加 gap projection event 作为重建水位线；重复 rebuild idempotent，不重复生成水位线。
- 旧 `/completion` 默认 Unified Runtime 入口会先尝试写入 Product Runtime shadow command / projection / action-token 记录，并以 SSE `product_runtime_shadow` 暴露 `recorded` 或 `blocked` 结果；该入口可显式识别 `shadow / canary / new_default / rollback`，且 `rollback` 窗口会真实回 legacy GeneralAgent，shadow 写入失败不把主 completion 响应冒充为 Product 成功，也不阻断默认 runtime 输出。

## 默认调用链

```text
POST /api/v1/product/runtime-requests
→ ProductService.submit_runtime_request
→ ProductUnitOfWork
→ ProductRepository.submit_command
→ ProductRepository.record_projection_event
→ ProductRepository.issue_action_token
→ ProductRepository.consume_action_token / revoke_action_token
→ ProductRepository.open_stream_cursor
→ response: CommandReceipt + Projection cursor + AvailableAction token

GET /api/v1/product/stream-events
→ ProductService.list_stream_events
→ ProductRepository.list_projection_events
→ DELTA or RESYNC_REQUIRED

GET /api/v1/product/stream
→ ProductService.list_stream_events
→ text/event-stream: id / event / data

ProductRepository.record_projection_rebuild
→ expire workspace stream cursors
→ record gap projection event
→ client Last-Event-ID receives RESYNC_REQUIRED

POST /api/v1/completion
→ resolve_completion_cutover_mode
→ CompletionService.stream_unified_runtime
→ CompletionService.record_product_runtime_shadow
→ ProductService.submit_runtime_request(command_kind=SHADOW_COMPLETION_RUNTIME_REQUEST)
→ SSE product_runtime_shadow event
→ UnifiedAgentRuntimeService stream
```

## 代码证据

- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/services/completion.py`
- `src/backend/zuno/api/v1/product.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `tests/api/test_goal03_product_route.py`
- `tests/api/test_completion_unified_runtime.py`
- `tests/integration/test_goal03_wave_a_persistence.py`

## 验证

```powershell
python -m pytest -q tests/api/test_goal03_product_route.py tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
8 passed
```

```powershell
python -m pytest -q tests/api/test_product_runtime_batch.py tests/repo/test_product_surface_target_protocols.py -p no:cacheprovider
```

结果：

```text
17 passed
```

```powershell
python -m pytest -q tests/api/test_completion_unified_runtime.py -p no:cacheprovider
```

结果：

```text
9 passed, 1 warning
```

```powershell
python -m pytest -q tests/api/test_goal03_product_route.py -p no:cacheprovider
```

结果：

```text
4 passed, 1 warning
```

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase09_product_projection_stream_cursor_and_action_token_are_persisted -p no:cacheprovider
```

结果：

```text
1 passed
```

```powershell
python -m compileall -q src/backend/zuno/platform/database/product
git diff --check
```

结果：

```text
compileall passed
git diff --check passed with LF/CRLF warnings only
```

## 边界

本证据只证明 PHASE09 Product API 默认入口已经接入 Product projection、stream cursor、projection rebuild waterline 和 AvailableAction token 的真实持久化路径，并且旧 `/completion` 默认入口已有 Product Runtime shadow 记录、显式 cutover mode 解析和 fail-closed 事件语义。

本证据不单独证明完整 PHASE09 completed；真实浏览器 E2E client reconnect、跨 Owner Projection rebuild worker 编排和更大范围旧 API cutover fault matrix 仍需要 Closure Gate 汇总证明。
