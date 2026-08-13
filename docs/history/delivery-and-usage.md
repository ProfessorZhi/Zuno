# 交付与使用阶段

status: canonical-history
canonical_question: 历史项目实际验证和交付到了什么阶段？
owner: Project History Owner
replaces: 旧 delivery-and-usage 表格式入口

## 一条保守的交付叙事

当前可以确认的阶段顺序不是精确日期，而是：项目存在内部 Demo，也面向智慧法院项目组 / 客户侧做过 Demo；客户反馈回答质量仍需提高；随后团队继续迭代，并有法院侧真实人员参与测试；项目进入 Pilot Validation，但尚未正式生产部署。

```text
Internal Demo
  → Customer / Smart Court Project Demo
  → 回答质量反馈
  → Further Iteration
  → Court-side Testing
  → Pilot Validation
  → Production = NO
```

## 状态表

| 阶段 | 历史状态 | 边界 |
|---|---|---|
| Internal Demo | `USER_CONFIRMED` | 有内部演示，时间、内容和参与者未知 |
| Customer-side Demo | `USER_CONFIRMED` | 有项目组 / 客户侧演示，不等于正式验收 |
| Court-side Testing | `USER_CONFIRMED` | 有法院侧人员参与，身份、人数和题目未知 |
| Pilot Validation | `USER_CONFIRMED` | 进入试点验证阶段，不等于生产 |
| Production | `USER_CONFIRMED: NO` | 尚未正式生产部署 |

Pilot 与 Production 必须分开：Pilot 只能说明在有限范围内进行验证或试用，不能推出正式全量部署、稳定 SLA、正式用户规模、QPS 或长期运维承诺。

## 客户质量反馈

客户 Demo 后明确提出回答质量需要继续提高，这是目前最可靠的业务反馈锚点。我们还不知道它具体对应事实错误、漏召回、引用不准、上下文不足、答案不完整，还是其他问题；也没有恢复出 Cause → Fix → Metric 的闭环。因此：

- `客户提出质量问题`：`USER_CONFIRMED`；
- `问题根因`：`UNKNOWN`；
- `团队修改带来质量提升`：`UNKNOWN`；
- `已经达到 Production Ready`：`CONTRADICTED` / 不允许使用。

## 仍然未知

- Pilot 部署位置、Endpoint 和环境归属；
- 具体试点法院、测试人员人数和职位；
- 是否有固定 Court QA、参考答案和评分人；
- 正式验收、用户规模、SLA、QPS、延迟、Token、成本和灾备；
- 质量改进前后的可复现指标。

当前仓库的测试和运行证据进入 [`../evidence/README.md`](../evidence/README.md)；当前生产状态由 [`../facts/current-state.md`](../facts/current-state.md) 维护。本文件不把 Compose、Target 部署图或代码目录当成历史客户部署证明。
