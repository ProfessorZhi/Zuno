# Archived Calibration — rb-2026-09-14-iterative-018

status: `INVALID_WORKFLOW_CALIBRATION`
counts_as_formal_round: `false`
source_pr: `#236`

这次运行不计入正式 Red / Blue Round。

原因不是候选人表现，而是 Harness 在运行过程中仍同时混用了 turn-by-turn、batch override、Pressure Suite 与自动连续 stage，导致用户无法在清晰的 Wave 边界看到：

```text
Red 1
→ Blue 1
→ Red 2 对 Blue 1 的评价 + 追问
→ Blue 2
→ 最终 Red / Blue / Harness / Architecture Reflection
```

其中产生的 Resume、问题和回答可以作为 Workflow 设计样本，但不得把其 PASS/FAIL、Architecture finding 或 Improvement Ledger 当成正式下一轮输入。

本次校准直接推动的新正式协议：

- 自动 Round 默认 `BATCH_DUEL`；
- Red Wave 1 固定 100 题；
- Blue Wave 1 固定 100 答，同时生成对 Red 封存的架构初诊；
- Red Wave 2 必须先盲评 Blue 1，再生成新的 100 个针对性追问；
- Blue Wave 2 固定 100 答，同时生成第二次封存架构诊断；
- Red Final 继续 blind；
- Blue Final 才读取 canonical sources 做最终 Architecture Reflection；
- Controller 再审 Resume Builder、Red Thinking Framework、Blue Candidate Framework、Blue Architecture Framework 与 Harness；
- 用户批准缺陷清单后，才真正修改架构 / 文档 / Skill / Implementation plan；
- 每个 Batch Checkpoint 默认只向用户发送对应 GitHub 文档链接。

后续正式 Round 必须从新协议已经 merge 的 main HEAD 重新开始，不继承本轮 verdict。