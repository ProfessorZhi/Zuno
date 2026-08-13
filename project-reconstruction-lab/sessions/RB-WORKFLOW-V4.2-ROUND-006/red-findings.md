# Red Findings

## WF-API-001 — P1 / OPEN

在完成 Session 后，直接 `send_input` 可能先返回上一条 completed response；即使执行
`resume → send_input → wait`，进入新 Root 时仍需验证返回内容是否对应当前 Question。若没有
submission/cursor 级别的身份校验，Main 不能安全冻结下一条 Answer。

## Architecture Findings

本 Round 未生成有效 Architecture Score。Q001–Q003 的内容只是 Live Defense 样本，不足以支持
KEEP、DELETE、REPLACE 或 Canonical Rewrite。
