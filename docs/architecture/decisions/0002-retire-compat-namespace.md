# ADR 0002: Retire Compat Namespace

## 状态

Accepted

## 决策

把 legacy compat namespace 的退场放在能力主线稳定之后执行。

## 原因

- 兼容层退场收益主要是清晰边界与单一 runtime truth，不直接增加能力
- 退场会影响 import、Docker、launchers、配置路径、测试和文档
- 过早收口会放大风险并拖慢核心能力落地

## 结果

- 先完成 Domain Pack、LangGraph、GraphRAG、eval 主线
- 等能力稳定后再删除兼容命名空间并统一到 `zuno`
