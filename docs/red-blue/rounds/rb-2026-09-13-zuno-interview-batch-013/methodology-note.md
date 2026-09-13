# Round #013 Methodology Note

status: `SUPERSEDED_INPUT_BOUNDARY`

Round #013 保留完整历史，但**不再作为合格 Interview Red Team 的验收结果**。

后续 Review 发现，该轮 Red 直接读取了 Zuno Project / Architecture / Modules / Evidence，并据此设计问题。这更接近 Architecture Reviewer：Red 已经知道项目内部如何分层、哪些地方有证据、哪些地方是 Target，再把这些信息反向写成面试问题。

真实面试官通常只拿到简历。新的 resume-first protocol 因此改为：

```text
Zuno docs / Evidence
→ Resume Builder 生成并冻结模拟简历
→ Red 只看模拟简历 + JD + Red Interview Skill + 通用知识
→ Blue 才读取 Zuno docs 回答
→ Red 只根据简历和回答评价
→ Blue 再做 Architecture Reflection
→ Workflow Retrospective 评价 Red 本身
```

Round #013 仍然可以用于两件事：

1. 保存当时 200 问 / 答 / 评价的完整历史；
2. 作为 workflow retrospective 的反例，说明“Red 预读项目文档”会让问题变成 Reviewer-style、答案导向式攻击。

它不能用于证明：

- 当前 Red Skill 已经达到真实大厂面试质量；
- 140 个 PASS 表示模拟面试通过；
- 该轮问题分布代表真实面试官只看简历时会提出的问题。

新的正式 Round 必须遵循 `.agent/red-blue/protocol.md` 的 resume-first source firewall。