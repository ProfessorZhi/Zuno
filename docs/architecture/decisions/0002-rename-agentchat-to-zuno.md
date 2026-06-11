# ADR 0002: Rename agentchat to zuno

## 状态

Accepted

## 决策

把 `agentchat -> zuno` 作为最终收口步骤，而不是本轮第一步。

## 原因

- 改名收益主要是平台表达，不直接增加能力
- 改名会影响 import、Docker、launchers、配置路径、测试和文档
- 提前改名会放大风险并拖慢核心能力落地

## 结果

- 本轮先完成 Domain Pack、LangGraph、GraphRAG、eval 主线
- 等能力稳定后再进行兼容式迁移
