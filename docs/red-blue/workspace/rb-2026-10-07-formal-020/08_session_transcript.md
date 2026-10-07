# Session Transcript — rb-2026-10-07-formal-020

```text
transcript_policy: full-observable-role-io
note: 本轮为 AGENT_AUTO；角色 IO 的完整文本即为 workspace 内各 artifact 本身，
      本文件记录阶段序列、执行者、commit 与隔离状态，不重复粘贴正文。
```

## 阶段序列

| # | Stage | 执行者 | 产物 | Commit |
| --- | --- | --- | --- | --- |
| 0 | `ROUND_INIT` | Controller | `00_manifest.yaml`, `00_artifact_links.md` | `1edd052b` |
| 1 | `BUILD_SIMULATED_RESUME` | Controller | `01_simulated_resume.md`（FROZEN） | `1edd052b` |
| 2 | `USER_RESUME_REVIEW` | Controller（用户委托） | manifest 记 `DELEGATED` | `1edd052b` |
| 3 | `RED_WAVE_1` | Red ×2（隔离实例） | `02_red_questions.md` + `.part1/.part2` | `4d9bf767` |
| 4 | `BATCH_CHECKPOINT_RED_1` | Controller | 聊天内发布链接 + 代表题样本 | — |
| 5 | `BLUE_WAVE_1` | Blue 候选人 ×1、Blue 架构 ×1（互不可见） | `03_blue_answers.md`, `03_blue_architecture_notes.md`（SEALED） | `2c13a079` |
| 6 | `BATCH_CHECKPOINT_BLUE_1` | Controller | 聊天内发布链接 | — |
| 7 | `RED_WAVE_2` | Red ×1（盲） | `04_red_wave2_review_and_questions.md` | `9d728c41` |
| 8 | `BLUE_WAVE_2` | Blue 候选人 ×1、Blue 架构 ×1 | `04_blue_wave2_answers.md`, `04_blue_wave2_architecture_notes.md`（SEALED） | `9845b07e` |
| 9 | `RED_EVALUATION` | Red ×1（盲） | `04_red_evaluation.md` | `0c9e2d82` |
| 10 | `BLUE_ARCHITECTURE_REFLECTION` | Blue 架构 ×1 | `05_blue_architecture_reflection.md` | `0c9e2d82` |
| 11 | `WORKFLOW_RETROSPECTIVE` | Controller | `06_workflow_retrospective.md` | 见收口 commit |
| 12 | `IMPROVEMENT_SYNTHESIS` | Controller | `09_improvement_ledger.md`, `09_round_report.md` | 见收口 commit |
| 13 | `BUILD_NEXT_RESUME_CANDIDATE` | Controller | `10_next_resume_candidate.md` | 见收口 commit |
| 14 | `USER_IMPROVEMENT_REVIEW` | **待用户** | — | — |

`batch_checkpoint_policy: LINK_ONLY_PAUSE`。阶段 4 与 6 均已按链接暂停点发布；用户在阶段 1 的委托被解释为全跑授权，故未阻塞。

## 执行者实例

```text
Red Wave 1 A        threads T01–T05 → Q1–Q50        isolated
Red Wave 1 B        threads T06–T10 → Q51–Q100      isolated（与 A 互不可见）
Blue 候选人 (W1)     A1–A100                         isolated（未见 architecture notes）
Blue 架构 (W1)       S01–S18 初诊                    isolated（未见候选人答案）
Red Wave 2          Part A 盲评 + Q101–Q200          blind
Blue 候选人 (W2)     A101–A200                       isolated（未见任何 architecture notes）
Blue 架构 (W2)       复核 + N01–N04                  sealed
Red Final           最终盲评                          blind
Blue 架构 Reflection 架构审判                         full
```

## 隔离状态

- **上下文隔离：物理的。** 各角色运行在独立上下文；Red 的上下文里从未出现过 `src/` 的内容。
- **文件系统隔离：指令约束 + 事后审计，非沙箱。** 从阶段 7 起，盲角色的产物末尾必须附「本次实际打开的文件」清单。已收到的三份审计附录均只列出授权输入。
- **已记录的泄漏向量**（见 `06_workflow_retrospective.md` §4.2）：
  1. Red Final 的一次 `ls -la` 回显了两份封存件的**文件名与大小**（未读内容，主动披露）。
  2. 并行写文件使候选人实例察觉到另一实例的**存在**（未读其内容，主动报告）。
  3. `interview-acceptance-standard.md` 同时充当攻击标准与答题模板（A183）。

## 阶段依赖违规（Controller 自身）

`BLUE_ARCHITECTURE_REFLECTION` 与 `RED_EVALUATION` 被并行启动。协议规定前者必须读取后者的产物。后果：架构审判第 1–8 节在 Red Final 到位前写成，第 9.3 节在到位后整体重写。执行者已主动披露该过程（其 §0.1），未做掩盖。已立为 `IMP-020-13`。

## 冻结 Resume 的处理

`01_simulated_resume.md` 全程冻结未改。候选人在 A200 当场改写了第 1 条 bullet 的措辞 —— 该改写**不**回写本轮 frozen resume（否则后续所有 Red 评价失效），只进入 `10_next_resume_candidate.md`。
