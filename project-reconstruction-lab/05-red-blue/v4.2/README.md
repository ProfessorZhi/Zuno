# V4.2 Adaptive Dual-Thread Pack

本目录是 `ZUNO-RED-BLUE-WORKFLOW-V4.2` 的 Prompt、Context 和外部审查模板。
它只描述工作流契约，不创建线程、不启动 Round-006，也不拥有 Canonical Architecture。

## 角色边界

- `red-thread-prompt.md`：Red 每次只提出一个问题；下一题必须读取上一条冻结 Answer 后动态决定。
- `blue-thread-prompt.md`：Blue 在 Live Attack 中只回答，不修改 Canonical，不读取 interview calibration、Candidate 或业务代码。
- `main-orchestrator-prompt.md`：Main 负责 Snapshot、逐 Turn 冻结、append-only ledger、hash、状态和 merge gate。
- `red-judge-prompt.md`：Live Attack 完成后执行 Part-A-first Judge 和 Counter-Retest。
- `chatgpt-review-template.md`：外部审查使用的 Review Package，不等同于 Verifier。

## 关键差异

V4.2 禁止 `red-questions.md`、`questions_frozen_sha` 和任何预生成 Q001–Q100 题单。
唯一有效的对攻证据是 `question-answer-ledger.jsonl` 与其人类可读投影
`live-interrogation.md`。

## 运行入口

```powershell
python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v42.py --round project-reconstruction-lab/sessions/<round-id>
```

V4.2 Bootstrap 只证明 `WORKFLOW_CONTRACT_AVAILABLE`；Round-006 的真实 Session、Context
Isolation、Calibration boundary 和 Main Merge Gate 仍须由 Operational Pilot 提供证据。
