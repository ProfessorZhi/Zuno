# V4.1 手工 Orchestrator 指引

当前环境没有被证明可靠的 Codex Thread create/close API，因此只生成 Artifact，不伪造 Session。

1. 从最新 `main` 记录 `base_sha`，生成 Canonical Snapshot；列出 Part A/Part B 文件与 SHA；复制并按本轮来源更新 `interview-calibration-packet.md`，只提炼提问行为。
2. 创建全新的 `RB-R<NNN>-RED` 和 `RB-R<NNN>-BLUE` Session；两者不得复用旧聊天。
3. Red 使用只读 worktree，只读取 Part A、必要 Facts/ADR/Governance 和采访校准 packet，不读取业务实现代码。
4. Red 生成 12–18 条 Deep-Dive Chain，总计 100Q；Main 冻结 `questions_frozen_sha`，通过 verifier 后再创建 Blue。
5. Blue 使用非 `main` Candidate Branch；先做概念防守，标记 `part_a_support`，再改 Part A/Part B。
6. Red Judge 先看 Final Part A，生成 `part-a-explainability.md`，再读 Part B 做一致性核验。
7. Main 生成 Review Package，状态保持 `WAITING_FOR_CHATGPT_REVIEW`。
8. 只有用户提供 `ACCEPT` / `ACCEPT_WITH_DEBT`，Main 才能 merge Candidate 到 `main`。Blue Context 必须标记 `interview_calibration: PROHIBITED`。

任何未实际执行的 Session、代码读取、Telemetry、Commit、Merge 或 Verdict 都必须标记
`NOT_RUN`，不能用 Prompt、截图或模型回答替代。
