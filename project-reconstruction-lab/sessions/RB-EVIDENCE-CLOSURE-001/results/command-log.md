# Executed Command Log

执行日期：2026-08-12。以下是本会话实际运行的命令及原始摘要。完整测试输出以终端退出码和
本文保存的结果为准；没有运行完整 CI。

## Import / entrypoint probe

### 裸 Agent batch verifier

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src\backend'
python tools/scripts/verify_agent_runtime_batch.py
```

结果：`FAIL`，`ModuleNotFoundError: No module named 'zuno'`。

进一步探测显示解释器 `sys.path` 没有采纳该环境变量，但源码文件存在。该结果标记为验证入口
环境问题，不作为 Agent Runtime 产品失败。

### 显式导入路径后的 Agent batch verifier

```powershell
python -c "import sys,runpy; sys.path.insert(0, r'F:\agent_project\Zuno\src\backend'); runpy.run_path(r'tools\scripts\verify_agent_runtime_batch.py', run_name='__main__')"
```

结果：`PASS`。

```text
Agent runtime batch verification passed: 80 requirements, 10 runtime nodes, 4 step runs, 8 reconcilers.
```

## Batch verifiers

四个命令均使用显式 `sys.path.insert(0, F:\agent_project\Zuno\src\backend)` 的 `runpy` 入口。

| Verifier | Result | Raw result |
|---|---|---|
| `verify_memory_runtime_batch.py` | PASS | `Memory runtime batch verifier passed for ARCH-MEM-001..060` |
| `verify_tool_runtime_batch.py` | PASS | `Tool runtime batch verifier passed for ARCH-TOOL-001..080` |
| `verify_security_runtime_batch.py` | PASS | `Security runtime batch verifier passed for ARCH-SEC-001..060` |
| `verify_observability_runtime_batch.py` | PASS | `Observability runtime batch verification passed for ARCH-OBS-001..024 and ARCH-OBS-RAG-001..020` |

这些 batch verifier 是当前仓库的协议/模型检查；它们不是多服务集成、真实网络、Provider、
Sandbox 或法院质量 benchmark。

## Focused pytest

```powershell
pytest -q tests/agent/runtime/test_runtime_state_contract.py tests/agent/runtime/test_runtime_tool_idempotency.py tests/agent/runtime/test_runtime_restart_persistence.py tests/agent/runtime/test_runtime_interrupt_resume.py tests/security/test_security_runtime_batch.py -p no:cacheprovider
```

结果：`PASS`。

```text
................                                                         [100%]
16 passed in 22.40s
```

覆盖的当前测试包括：Runtime state serialization/version/payload reference、Tool execution
idempotency、approval interrupt restart persistence、resume boundary 和 security runtime batch。

## 未运行

- 完整 CI；
- 多服务 Docker/Compose 集成；
- RabbitMQ/MinIO/Milvus/Neo4j/Elasticsearch 实例联调；
- 真实 MCP/API Provider；
- Sandbox escape/egress/secret fault injection；
- 法院 QA、A/B/C、Citation correctness 或 representative legal benchmark；
- 生产、Pilot 或 DR 证据。
