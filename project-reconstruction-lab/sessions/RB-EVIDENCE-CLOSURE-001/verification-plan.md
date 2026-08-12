# Verification Plan

## 目标

在不修改产品 Runtime 行为的前提下，优先复用当前仓库已有的 verifier 和 focused tests，
为 Final P0 提供可复现的窄命题证据。没有现成证据的跨服务并发、真实 Provider、Sandbox、
法院 QA 和 A/B/C Eval 不通过写 prose 假装完成，而是登记为下一步证据要求。

## 执行分层

| 组别 | 覆盖 | 本轮动作 | 结论边界 |
|---|---|---|---|
| Agent state | Q016、Q033、Q097 | 运行 state contract、restart、interrupt/resume、idempotency tests 与 Agent batch verifier | V3 focused；不证明跨服务恢复 |
| Tool effect | Q061、Q063、Q064、Q070 | 运行 Tool/Security batch verifier 与 idempotency test | V3 contract/model；不证明真实 Provider |
| Security boundary | Q066、Q067、Q070 | 运行 security batch verifier 与相关 payload/approval tests | V3 contract/model；不证明 sandbox escape/egress |
| Observability/Citation | Q039 | 运行 observability batch verifier | 只证明观测协议模型；不证明 Citation quality |
| Domain ownership | Q005 | 设计 mutation/concurrency spike | 本轮未执行，等待最小 Owner contract |
| Plan concurrency | Q053 | 设计 version-conflict fault test | 本轮未执行，等待 Domain/Plan fixture |

## 通过与失败

每个命令的退出码为 0 且输出包含预期 verifier/test 结果时，记录为 `EXECUTED_PASS` 的窄证据。
以下任一情况记录为失败或阻塞：

- 命令不能在干净工作树和声明环境中复现；
- 测试通过但没有覆盖该 P0 的 Closure Condition；
- 证据只存在于计划或静态目标文档；
- 环境缺少真实外部服务、Provider、Sandbox、法院 QA 或代表性数据；
- Red Review 发现 Claim 超出了 Artifact 的实际范围。

## 环境前提

```text
OS: Windows PowerShell
Python: E:\develop\Python312\python.exe
Repository: F:\agent_project\Zuno
Backend import: explicit sys.path insertion of F:\agent_project\Zuno\src\backend
External services: not started for this campaign
Production/court environment: unavailable
```

解释器没有把 `PYTHONPATH` 环境变量自动放入 `sys.path`；因此 Agent batch verifier 的裸命令
失败属于执行入口环境问题。使用显式 `sys.path.insert` 的同一 verifier 成功，二者都保留在命令日志中。

## 尚未执行的 V4/V5

- Domain Owner 并发写入和跨服务 mutation；
- Plan/Domain version conflict 与 replan；
- Provider timeout、unknown effect 和重复 side effect；
- Sandbox escape、egress、secret 和资源隔离；
- Citation sufficiency、unsupported claim、Fact–Article 与 A/B/C；
- 多服务 crash matrix、outbox/inbox、reconciliation；
- 真实法院 QA、Pilot trace 和生产运行验证。

这些缺口阻止 P0 进入 `CLOSED`，也阻止 Production Readiness 上升。
