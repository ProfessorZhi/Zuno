# V4.2 Adaptive Dual-Thread Pack

本目录是 `ZUNO-RED-BLUE-WORKFLOW-V4.2` 的 Prompt、Context 和外部审查模板。
它只描述工作流契约，不创建线程、不启动 Round-007，也不拥有 Canonical Architecture。

V4.2 的默认执行 Profile 是 `BATCH_ADVERSARIAL`；`LIVE_ADAPTIVE` 是实验性 Profile。Round-006
的 Live Pilot 已因 `WF-API-001` 中止，不能作为架构评分；下一轮只具备
`READY_FOR_BATCH_ADVERSARIAL_PILOT / NOT_STARTED` 状态。

## 角色边界

- `red-thread-prompt.md`：Red 每次只提出一个问题；下一题必须读取上一条冻结 Answer 后动态决定。
- `blue-thread-prompt.md`：Blue 在 Live Attack 中只回答，不修改 Canonical，不读取 interview calibration、Candidate 或业务代码。
- `main-orchestrator-prompt.md`：Main 负责 Snapshot、逐 Turn 冻结、append-only ledger、hash、状态和 merge gate。
- `red-judge-prompt.md`：Live Attack 完成后执行 Part-A-first Judge 和 Counter-Retest。
- `chatgpt-review-template.md`：外部审查使用的 Review Package，不等同于 Verifier。

## Profile 差异

`BATCH_ADVERSARIAL` 允许 Fresh Red Attack 一次生成完整 100Q 和 12–18 条 Deep-Dive Chain；
它必须保留 Why、Why Not、Counterexample、Failure、Alternative、Tradeoff 和 Reversal 攻击维度，
并由 `RED_COUNTER` 读取 Blue Answers 后进行动态追击。Batch 不得简化成 100 个独立 checklist 问题。

`LIVE_ADAPTIVE` 禁止 `red-questions.md`、`questions_frozen_sha` 和任何预生成 Q001–Q100 题单；
其唯一有效的逐题对攻证据是 `question-answer-ledger.jsonl` 与人类可读投影
`live-interrogation.md`。这些禁止项不适用于 Batch Attack Artifact。

## 运行入口

```powershell
python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v42.py --round project-reconstruction-lab/sessions/<round-id>
python tools/scripts/verify_red_blue_workflow_v42.py --profile batch_adversarial --round project-reconstruction-lab/sessions/<batch-round-id>
```

V4.2 Bootstrap 只证明 `WORKFLOW_CONTRACT_AVAILABLE`；Round-006 的真实 Session、Context
Isolation、Calibration boundary 和 Main Merge Gate 只取得部分/未证明的 Operational Evidence，
并已因 `WF-API-001` 中止。下一次运行必须使用默认 Batch Profile；Round-007 尚未启动。
