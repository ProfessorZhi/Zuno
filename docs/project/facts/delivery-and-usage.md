# Delivery and Usage

## 已确认的交付状态

| 事实 | 状态 | 当前表述 |
|---|---|---|
| 内部 Demo | `[USER_CONFIRMED]` | 存在内部 Demo |
| 面向智慧法院项目组/客户侧的 Demo | `[USER_CONFIRMED]` | 存在客户侧 Demo |
| 法院侧真实人员参与测试 | `[USER_CONFIRMED]` | 有法院侧人员参与测试；数量和身份未知 |
| 历史阶段 | `[USER_CONFIRMED]` | Pilot Validation / 试点验证 |
| 正式生产部署 | `[USER_CONFIRMED]` | 尚未正式生产部署 |
| 生产流量 | `[UNKNOWN]` | 未建立生产流量证据 |

## 交付状态边界

```text
Internal Demo       = YES
Customer Demo       = YES
Court-side Testing  = YES
Pilot Validation    = YES
Production          = NO
```

上述状态不代表已经有正式验收、稳定 SLA 或可公开的客户规模。

| 未知事实 | 状态 | 需要的直接证据 |
|---|---|---|
| 实际部署位置和 endpoint | `[UNKNOWN]` | 环境、部署记录或访问地址 |
| 真实用户数量和访问范围 | `[UNKNOWN]` | 用户清单、日志或客户确认 |
| 具体法院与试点法院 | `[UNKNOWN]` | 项目材料或客户反馈 |
| 正式验收结果 | `[UNKNOWN]` | 验收文档或明确用户确认 |
| 上线时间、QPS、延迟、Token 和成本 | `[UNKNOWN]` | Trace、指标、账单或 Benchmark |
| 运维责任、SLA、On-call 和灾备 | `[UNKNOWN]` | Runbook、告警和值班记录 |

## 质量反馈

| Claim | 状态 | 边界 |
|---|---|---|
| 客户 Demo 后提出回答质量需要进一步提高 | `[USER_CONFIRMED]` | 反馈已确认，具体问题归因和指标未知 |
| 已经证明回答质量提升 | `[UNKNOWN]` | 没有统一可复现的前后对照指标 |
| 已经达到 production ready | `[CONTRADICTED]` | 尚未正式生产部署，不能使用该表述 |

不能把“有 Demo”“有法院侧人员测试”写成生产上线，也不能把试点验证写成正式交付完成。

## 证据路由

当前仓库的运行和测试证据进入 [`../../evidence/`](../../evidence/README.md)；生产 readiness 进入 [`../../status/production-readiness.md`](../../status/production-readiness.md)。本文件只维护项目历史状态，不把当前 Compose 或目标部署拓扑当作历史交付证明。
