# V4 Fresh Context / Dual Thread 工具包

本目录保存 V4 的可复用 Prompt、Context Packet 约束和人工 Orchestrator 操作说明。它不是
Canonical Architecture，也不是 Codex Thread API 的替身。

## 文件

| 文件 | 用途 |
| --- | --- |
| `red-thread-prompt.md` | 独立 Red Challenger/Judge 的启动契约 |
| `blue-thread-prompt.md` | 独立 Blue Canonical Writer 的启动契约 |
| `red-judge-prompt.md` | Blue Sync 后的 Red Counter Review 契约 |
| `chatgpt-review-template.md` | External Architecture Auditor 输入模板 |
| [`../round-protocol-v4.md`](../round-protocol-v4.md) | V4 状态、权限和 Artifact 正式协议 |

## 人工 Orchestrator 顺序

1. 在 `main` 上生成 Snapshot，并冻结其 SHA。
2. 生成 Red/Blue 两份 Context Packet；只引用 Snapshot、路径和 SHA。
3. 在隔离 Session 中启动 Red；Red 只写 `red-questions.md` 和攻击 Artifact。
4. 通过 verifier 后记录 `questions_frozen_sha`，再生成 Blue Packet。
5. 在新的隔离 Session 启动 Blue；Blue 只通过 Artifact 读取 Red Questions，并拥有唯一
   Canonical 写权限。
6. 生成 Judge Packet；重新启动或唤醒 Red Judge Phase，只读取 Judge Packet。
7. 生成 Review Package，状态停在 `WAITING_FOR_CHATGPT_REVIEW`。
8. 用户提供 Verdict 后再运行 verifier；只有允许的 Verdict 才能关闭 Round。

当前环境不能证明 Codex Thread API 已可被脚本可靠创建，因此不自动 launch、不伪造 Session
或 Telemetry。人工操作材料见 [`../../sessions/RB-WORKFLOW-V4-BOOTSTRAP/manual-launch-instructions.md`](../../sessions/RB-WORKFLOW-V4-BOOTSTRAP/manual-launch-instructions.md)。
