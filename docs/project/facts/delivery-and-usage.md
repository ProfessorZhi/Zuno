# Delivery and Usage

## 交付状态

当前必须在以下状态中明确选择，不能统一写成“已经落地”：

```text
NOT_DEPLOYED
LOCAL_DEMO
TEAM_DEV
PILOT
INTERNAL_TEST
PRODUCTION
STOPPED
UNKNOWN
```

| 事实 | 当前状态 | 必需证据 |
|---|---|---|
| 实际部署位置 | `[UNKNOWN]` | 部署记录、环境、Endpoint |
| 实际访问者和用户量 | `[UNKNOWN]` | 访问日志、用户清单或用户确认 |
| QPS、延迟、Token 和成本 | `[UNKNOWN]` | Trace、指标、账单或 Benchmark |
| 运维责任、SLA 和 On-call | `[UNKNOWN]` | Runbook、告警、值班和事故记录 |
| Backup / Restore / 灾备 | `[UNKNOWN]` | 演练或运行证据 |
| 真实用户反馈和验收 | `[UNKNOWN]` | 反馈、验收记录或可复现任务 |

学校、导师、法院或合作对象的公开规模只能用于 Target Capacity Planning，不能推出 Zuno 的实际用户量、部署规模或生产状态。

## 证据路由

当前状态和运行指标进入 [`../../status/production-readiness.md`](../../status/production-readiness.md)；可复现代码、测试、Trace、Eval 和部署证据进入 [`../../evidence/`](../../evidence/README.md)。本文件只维护项目层的事实摘要和缺口，不复制证据正文。
