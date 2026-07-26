# Goal03 Wave A Product Projection Stream Action Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE09 中默认 Product API 在提交 `RuntimeRequest` 后必须进入 Product-owned read model 的最小纵切：

- 同一 Product Unit of Work 内提交 `ProductCommand`、`CommandReceipt`、`ProjectionEvent`、`StreamCursor` 和服务端 `ActionToken`。
- `CommandReceipt` 仍只表示 Product 接受或重复，不冒充 Agent Core 领域成功。
- `GET /api/v1/product/stream` 使用 `text/event-stream` 输出 Product Projection Delta / Resync 事件。
- `GET /api/v1/product/stream-events` 提供同一事件源的 JSON 查询面，支持 `Last-Event-ID`，并在未知或过期 cursor 时返回 `RESYNC_REQUIRED` 语义。
- `Last-Event-ID` 绑定 principal；其他 principal 复用 cursor 时按未知 cursor 处理并返回 `RESYNC_REQUIRED`，不泄露增量事件。
- AvailableAction 由服务端签发 action token，不由前端按状态字符串推断。
- `product_action_tokens` 支持一次性消费和撤销；重复消费或撤销后消费 fail closed。

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
```

## 代码证据

- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/v1/product.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `tests/api/test_goal03_product_route.py`
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

## 边界

本证据只证明 PHASE09 默认入口已经接入 Product projection、stream cursor 和 AvailableAction token 的真实持久化路径。

本证据不单独证明完整 PHASE09 completed；Agent Catalog / Publication / Installation 的全量后端、完整 SSE backpressure、全旧 API cutover、跨 Owner Projection rebuild 和完整浏览器 E2E client reconnect 仍需要 Closure Gate 汇总证明。
