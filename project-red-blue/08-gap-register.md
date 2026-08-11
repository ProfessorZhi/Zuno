# Gap Register

## 缺口类型

| 类型 | 含义 |
|---|---|
| `BACKGROUND_GAP` | 项目来源、约束或时间线不清 |
| `PROJECT_REALITY_GAP` | 用户、上线、规模或真实流程无法证明 |
| `OWNERSHIP_GAP` | 团队或个人责任边界不清 |
| `NARRATIVE_GAP` | 项目说法与事实、证据或范围不一致 |
| `PRODUCT_POSITIONING_GAP` | 用户价值、差异化或非目标不清 |
| `BUILD_BUY_GAP` | 自建、复用、扩展、延期没有比较 |
| `OVERENGINEERING_GAP` | 复杂度与团队、规模或阶段不匹配 |
| `ARCHITECTURE_GAP` | 模块边界、Owner、状态或契约不完整 |
| `IMPLEMENTATION_GAP` | 关键路径、异常或数据细节无法说明 |
| `DELIVERY_PROCESS_GAP` | 开发、评审、发布、回滚或协作过程不清 |
| `CURRENT_EVIDENCE_GAP` | Current 结论缺代码、测试、Trace 或运行证据 |
| `MEASUREMENT_GAP` | 指标、基线、数据集或成本无法复现 |
| `SECURITY_GAP` | 权限、租户、隐私、外部副作用或合规不清 |
| `FUNDAMENTAL_GAP` | 依赖的基础原理不能解释 |
| `RESUME_CLAIM_RISK` | 简历或面试陈述超出本人真实贡献 |

## 记录模板

```text
RB-XXX [OPEN]
类型：
严重度：P0 / P1 / P2
触发 Claim：
红队问题：
已知事实：
缺少什么：
蓝队回应：
候选修复：
需要用户确认：
正式去向：
关闭证据：
复测结果：
```

## 关闭条件

- 事实缺口：用户确认并记录来源；
- 证据缺口：补充可复现代码、测试、Trace、指标或引用；
- 架构缺口：更新唯一正式文档和必要 Contract，并通过验证；
- 过度设计：缩小范围或明确 Defer，不以增加文档解释代替；
- 叙事风险：改成与事实一致的说法，并重新进行 Forensic 追问。

没有关闭证据时保持 `OPEN`，不能因为有一个漂亮的回答就关闭。
