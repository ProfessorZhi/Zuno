# External Qualification Track

## Q066 / X-P0

```text
Status: BLOCKED_EXTERNAL
Target Sandbox Boundary: DESIGNABLE
Security Qualified: NO
Production Proven: NO
```

所需资格证据：

- filesystem/path traversal、parent process、network egress、secret/environment、fork/process
  和 resource limit fault tests；
- allowlist、secret scope、audit receipt、image/dependency provenance；
- 可复现运行环境、命令日志和失败结果。

Docker/Deno 或等价隔离运行时不可用时，不执行伪造测试、不把 adapter/in-process contract
升级成真实隔离证明，也不把 `BLOCKED_EXTERNAL` 降级为 PASS。

## 外部资格不改变 Target Gate

Q066 不阻塞 `ACCEPTED_TARGET` 的用户审阅，但阻塞 `SECURITY_QUALIFIED`、`PRODUCTION_READY`
和 `PRODUCTION_PROVEN`。真实部署、第三方 Provider、负载环境和网络安全资格同样保持
未建立。
