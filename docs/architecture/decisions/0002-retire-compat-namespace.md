# ADR 0002：退休 Compat Namespace

## 状态

Accepted

## 决策

兼容命名空间的退休应放在能力主线稳定之后执行，不能抢在 Memory、Capability、GraphRAG 和 Evidence 主线前面。

## 原因

- 兼容层退休的主要收益是边界清晰和 runtime truth 统一，不直接增加用户能力。
- 退休会影响 import、Docker、launcher、配置路径、测试和文档。
- 过早收口会放大风险，并拖慢核心能力落地。

## 结果

- 先推进 Single GeneralAgent、Context / Memory、ToolCard、GraphRAG、retrieval fusion 和 eval / trace 闭环。
- 等能力稳定后，再删除兼容命名空间并统一到 `zuno` 主线。
