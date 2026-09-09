# Findings — rb-2026-09-09-resume-v4-005

Round result: `PASS_WITH_S3_NARRATIVE_CLARIFICATION`  
Resume claim verdict: `PASS`  
Highest severity: `S3`

v4 已通过 Resume Truthfulness、Ownership、Measurement 和 Current / Target 复测。没有新的 S0 / S1 / S2 Claim 风险；只保留一个可以通过一句话修复的 Narrative Finding。

## F1 — Tool Calling bullet 应显式区分 GeneralAgent 与 Workspace 调用层

Severity: `S3`  
Type: `NARRATIVE_GAP`

### Current wording

v4 将两段真实历史放在同一 bullet：

- 2026-04-15 `GeneralAgent` Tool/MCP strategy：MCPAgent-as-Tool -> concrete MCP Tools，调用期注入用户配置；
- 2026-04-28 `WorkSpaceSimpleAgent` route hardening：deterministic direct route / ReAct fallback、custom MCP recursion、天气参数解析。

两段都由 PF-032 支持，当前文字没有声称 direct route 位于 `GeneralAgent`。但连续书写容易让读者把后半句继续归到 `GeneralAgent` 类内。

### Decision

不削弱 Claim。最小修复是在后半句明确写：

```text
并在 Workspace 调用层保留 deterministic direct route 与 ReAct fallback
```

这样可以在不增加字数级别复杂度的前提下，把 Agent 内部 Tool binding 与产品调用层 routing 分开。

### Still-valid boundaries

以下 v4 边界已经通过，不需要重写：

- “新增对应回归用例”只表示 test artifact，不表示历史 CI pass；
- 主动语态只覆盖 exact diff-supported task，不扩张到整个 Tool Runtime；
- later PreparedAction / Approval / Idempotency / EffectReceipt / Reconcile 不属于 4 月实现；
- 没有 latency / token / success-rate / customer result Claim；
- Context / Memory PR #8 的 `32 passed` 与 Tool Calling 的 test artifact 证据等级保持分开。

### Next step

创建一个只做该层次澄清的后继 Resume 候选，保留 v4 作为 Round #005 固定输入。随后 targeted retest 新 Tool Calling 句子即可；无需重新审计 Coding Agent、SFT/DPO 或其他 Zuno bullet。