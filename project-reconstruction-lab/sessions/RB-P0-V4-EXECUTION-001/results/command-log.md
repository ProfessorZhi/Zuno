# V4 Execution Command Log

执行日期：2026-08-12。所有路径均为当前 `F:\agent_project\Zuno`，未修改产品 Runtime。

## Baseline

执行 `git fetch origin`、`git checkout main`、`git pull --ff-only origin main`、`git rev-parse HEAD`、`git status --short`。

结果：`HEAD=71630f16edf027b610e9b0ca7f17a6a4c0fc9080`，branch 与 origin/main 同步，工作树干净。

## Environment entry audit

当前解释器 `isolated=1`、`ignore_environment=1`、`safe_path=True`。裸运行
`python tools/scripts/verify_agent_runtime_batch.py` 结果为
`FAIL / ModuleNotFoundError: No module named 'zuno'`。

`pyproject.toml` 声明了 Poetry package `{ include = "zuno", from = "src/backend" }`，但当前
解释器的 editable metadata 指向另一个 worktree，且隔离模式不加载 `zuno.pth`。`pytest`
通过 `tests/conftest.py` 注入 `src/backend`，所以 pytest 入口可用；batch verifier 使用显式
源码路径的临时验证入口。记录为：

```text
VERIFICATION_ENVIRONMENT_GAP
不是 Runtime Product P0；不改变产品代码。
```

显式路径入口的 Agent batch 结果：PASS，80 requirements、10 runtime nodes、4 step runs、8 reconcilers。

## New V4 focused harness

命令：`pytest -q tests/architecture/test_p0_v4_execution.py -p no:cacheprovider`

结果：`10 passed, 1 xfailed in 60.42s`。

`xfailed` 是 Q039 wrong-span 负例：当前实现按位置绑定 Citation，测试有意记录该缺口；
它不能被解释成 Q039 已通过。

覆盖：Q005/Q053/Q097 verification-only concurrency/recovery spike、Q063/Q064 loopback HTTP
provider emulator、Q016 restart path、Q033 approval gate、Q039 citation fixture、Q067
untrusted flow、Q070 read-only audit correlation。

## Related existing tests

命令：`pytest -q tests/agent/test_tool_control_plane_runtime.py tests/capability/test_tool_runtime_batch.py tests/security/test_security_runtime_batch.py tests/agent/runtime/test_runtime_restart_persistence.py tests/agent/runtime/test_runtime_interrupt_resume.py tests/agent/runtime/test_runtime_grounded_synthesis.py tests/platform/test_observability_runtime_batch.py -p no:cacheprovider`

结果：`18 passed in 42.85s`。

## Existing batch verifiers

使用显式 `sys.path.insert(0, F:\agent_project\Zuno\src\backend)` 的 runpy 入口：

| Verifier | Result |
|---|---|
| Agent runtime batch | PASS — 80 requirements / 10 nodes / 4 steps / 8 reconcilers |
| Capability runtime batch | PASS — ARCH-CAP-001..080 |
| Tool runtime batch | PASS — ARCH-TOOL-001..080 |
| Security runtime batch | PASS — ARCH-SEC-001..060 |
| Observability runtime batch | PASS — ARCH-OBS-001..024 / RAG-001..020 |

这些结果是现有 contract/model verifier，不自动升级为 V4 integrated evidence。

## Sandbox probe

执行 `docker version --format '{{.Server.Version}}'` 与 `deno --version`，结果均不可用。
Q066 记为 `BLOCKED_EXTERNAL`，没有执行伪 Sandbox 测试。

## Not run

- Full CI；
- ephemeral PostgreSQL concurrency；
- Domain Owner / PlanVersion / DomainVersion current persistence；
- 三方 Tool Gateway UOW 的完整 side-effect chain；
- 真实 Provider、Docker/Deno Sandbox；
- Court QA、A/B/C、Citation quality、Evidence sufficiency、Unsupported Claim benchmark；
- production/Pilot/DR execution。
