# V4 手工启动指引

当前环境没有被证明可靠的 Codex Thread 创建 API，因此只能按下列方式人工操作。任何一步
未产生真实 Session 或 Artifact，都必须记录 `NOT_RUN`，不得用 UI 截图或模型文本伪造。

## Round N 启动

1. 在 `main` 上记录 `base_sha`，生成 `canonical-snapshot.yaml` 及其 SHA。
2. 为 Red 和 Blue 创建两个不同的、全新的逻辑 Session：`RB-R<NNN>-RED`、`RB-R<NNN>-BLUE`。
3. Red 使用只读 checkout，读取 `red-context.md` 和 Red Prompt；输出只进入 Red Artifact。
4. 运行 V4 verifier，确认 Questions 恰好 100 个并记录 `questions_frozen_sha`。
5. 生成 Blue Packet，包含本轮 Red Questions 的 SHA；Blue 使用可写分支并同步 Canonical。
6. 生成 Judge Packet；让 Red 重新读取 Judge Packet，输出 Counter Review 和 Scorecard。
7. 生成 `chatgpt-review-package.md`，把 Round 状态设置为 `WAITING_FOR_CHATGPT_REVIEW`。
8. 将 Package 交给外部 ChatGPT；只有用户提供完整 Verdict 后，才能再次运行 verifier 并关闭。

## 不能做的事

- 不要 continue 上一轮 Session；
- 不要把完整历史聊天复制进 Context Packet；
- 不要让 Red 写 Canonical；
- 不要让 Blue 改题或事实；
- 不要把 Wave-001 的实现证据作为 Architecture Round 的 Gate；
- 不要在没有外部 Verdict 时写 `ACCEPT` 或 `CLOSED`。
