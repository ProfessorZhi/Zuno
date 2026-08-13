# V4.1 Conceptual Architecture Review Toolkit

V4.1 在 V4 的 Fresh Context / Dual Thread 基础上增加 Part-A Cold-Start、默认 No-Code Review、
Candidate Branch 和 Main Merge Gate。它是工作流材料，不是 Canonical Architecture。

| 文件 | 作用 |
| --- | --- |
| `red-thread-prompt.md` | Conceptual Red Challenger，默认不读业务代码 |
| `blue-thread-prompt.md` | Conceptual Blue Defense / Canonical Writer |
| `red-judge-prompt.md` | Part A first-pass + Part B consistency Judge |
| `main-orchestrator-prompt.md` | Main Thread / Coordinator 操作契约 |
| `chatgpt-review-template.md` | ChatGPT External Auditor 输入模板 |
| `interview-calibration-packet.md` | 只给 Red 的提问行为校准摘要，不含答案 |
| [`../round-protocol-v4.1.md`](../round-protocol-v4.1.md) | V4.1 正式状态与权限协议 |

当前不自动创建 Codex Thread。若没有可靠 Thread API，只生成 Manifest、Prompt、Context Packet、
Candidate Branch 记录和人工启动指引；不得伪造 Session、Merge 或 Verdict。

V4.1 Addendum 把 Red 从“100 个独立问题”校准为 12–18 条 Deep-Dive Attack Chain，总题数仍为
100。Manifest 同时记录 Novel/Regression 质量门和每条 Chain 的 `INTERVIEW_DEPTH: 0–5`。
`interview-calibration-packet.md` 只提炼真实面试中的提问方式；Blue 不读取它，且不把
面试答案、包装话术或外部面经事实注入任何 Canonical Context。
