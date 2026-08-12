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

## 用户确认的交付边界

| 事实 | 状态 | 边界 |
|---|---|---|
| 正式生产部署 | `[USER_CONFIRMED]` | 用户明确表示尚未正式生产部署；实际是否有内部环境、客户 Demo 或试点环境仍需分别确认 |
| 内部 Demo、客户 Demo、法院侧人员测试和 Pilot | `[UNKNOWN]` | 附件中的 V1 方案将其列为候选叙事，但本轮尚未获得逐项直接确认 |

## 本轮事实 Gate 的明确保留项

以下均继续保持 `[UNKNOWN]`：

```text
实际部署位置
真实用户数量和访问范围
团队内部试点 / Pilot 状态、正式生产部署的时间和可复核证据
上线时间、验收结果、QPS、延迟和成本
运维责任、SLA、On-call、Backup / Restore / 灾备演练
```

旧模块、架构图、Provider 名称、目录存在或目标部署拓扑，都不能把这些状态提升为 Current。

学校、导师、法院或合作对象的公开规模只能用于 Target Capacity Planning，不能推出 Zuno 的实际用户量、部署规模或生产状态。

## 证据路由

当前状态和运行指标进入 [`../../status/production-readiness.md`](../../status/production-readiness.md)；可复现代码、测试、Trace、Eval 和部署证据进入 [`../../evidence/`](../../evidence/README.md)。本文件只维护项目层的事实摘要和缺口，不复制证据正文。
