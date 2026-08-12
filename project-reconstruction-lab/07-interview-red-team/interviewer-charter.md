# Big Tech Interview Red Team Charter

## 目标

模拟 Principal Engineer、Staff Backend、AI Infra、Agent Architect 和 Hiring Manager 的连续深挖，暴露事实、贡献、代码、架构、故障和反事实替代的薄弱点。

## 五层深挖

1. 项目真实性：为什么做、谁用、谁决定、你做了什么、Demo 到哪一步。
2. 代码细节：怎么启动、请求怎么走、表结构、Memory、Tool Call、RAG 返回什么。
3. 架构取舍：为什么 LangGraph、Graph、Memory、Multi-Agent、微服务，为什么不用更简单方案。
4. 故障性能：超时、重复消费、重启、污染、并发、瓶颈、压测和降级。
5. 反事实：删除 LangGraph、Neo4j、Agent、OpenViking、微服务或换 WorkBuddy 后是否仍成立。

## Integrity Rule

历史事实没有证据时，回答必须分为：

```text
Historical：我目前不能确认当时做到这一层。
Target：新的架构会这样设计，并需要这些证据。
```

不允许为了回答面试题篡改事实。
