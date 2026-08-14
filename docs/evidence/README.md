# 当前证据入口

`docs/evidence/` 只记录今天可以由代码、Migration、Test、Trace、Eval 或真实运行结果复核的
Current 结论。它不承载历史项目叙事，也不把 Target 文档、目录存在、Mock 或设计计划写成实现
或生产证据。

## 当前保留的证据

| Evidence | 保留理由 |
| --- | --- |
| [Current Runtime Baseline](current-runtime-baseline.md) | 当前 Runtime owner、状态和失败语义的证据入口 |
| [Current Test Baseline](current-test-baseline.md) | 当前测试范围、未运行项和质量边界 |
| [Current Eval Baseline](current-eval-baseline.md) | 当前评测与 Measurement Blocked 状态 |
| [Implementation Wave-001](implementation-wave-001.md) | TASK-001 / TASK-003 的有限代码、测试和窄验证证据；不是 Program closure |

已删除的 `local-workspace-closure.md` 和 `repository-closure.md` 只是已完成 Program / 工作区
收口材料，不是今天需要维护的运行证据；其提交和原始材料仍由 Git 历史保留。

## 当前边界

```text
PRODUCTION_READINESS: NOT_ESTABLISHED
QUALITY: not_yet_proven
FULL CI: NOT RUN
COURT QA: UNKNOWN / NOT AVAILABLE
```

当前仓库可以证明有限实现和验证范围，不能证明完整历史技术栈、真实法院质量、生产部署、用户规模、
SLA、QPS、HA、No-egress、Sandbox 资格或正式外部验收。历史 Pilot 不等于 Production。

## 读取规则

- 先看对应 Evidence 的 scope、command、result 和 known gaps；
- 只把明确覆盖的结论称为 Current；
- 外部数据、客户材料和历史记忆必须回到 `docs/project/`；Red / Blue 讨论只回到 `docs/history/red-blue/`，不作为 Evidence；
- Architecture Target 和 ADR 的语义不由本目录拥有。
