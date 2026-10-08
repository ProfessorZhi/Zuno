# Session Transcript — rb-2026-10-08-formal-021

```text
transcript_policy: full-observable-role-io
note: 本轮为 AGENT_AUTO；角色 IO 的完整文本即为 workspace 内各 artifact 本身，
      本文件记录阶段序列、执行者、commit 与隔离状态，不重复粘贴正文。
```

## 阶段序列

| # | Stage | 执行者 | 产物 | Commit |
| --- | --- | --- | --- | --- |
| 0 | `ROUND_INIT` | Controller | `00_manifest.yaml`, `00_artifact_links.md` | `d8f8d7a8` |
| 0b | （PR 登记） | Controller | manifest `round_pr: 282` | `eb8163fb` |
| 1 | `BUILD_SIMULATED_RESUME` | Controller + 隔离核验 subagent | `01_simulated_resume.md`（FROZEN，4 处措辞修正） | `bcd00a61` |
| 2 | `USER_RESUME_REVIEW` | Controller（用户委托） | manifest 记 `DELEGATED_APPROVED` | `bcd00a61` |
| 3 | `RED_WAVE_1` | Red ×2（互不可见实例，blind） | `02_red_questions.md` | `97bdd0db` |
| 4 | `BATCH_CHECKPOINT_RED_1` | Controller | 链接已发布 | — |
| 5 | `BLUE_WAVE_1` | Blue 候选人 ×2（A1–A50 / A51–A100）、Blue 架构 ×1 | `03_blue_answers.md`, `03_blue_architecture_notes.md`（SEALED，15 findings） | `28e4661e` |
| 6 | `BATCH_CHECKPOINT_BLUE_1` | Controller | 链接已发布 | — |
| 7 | `RED_WAVE_2` | Red ×1（盲） | `04_red_wave2_review_and_questions.md`（Part A + Q101–Q200） | `718c8524` |
| 8 | `BLUE_WAVE_2` | Blue 候选人 ×2（A101–A150 / A151–A200）、Blue 架构 ×1 | `04_blue_wave2_answers.md`, `04_blue_wave2_architecture_notes.md`（SEALED，差分） | `957e8114`, `b95e00fc` |
| 9 | `RED_EVALUATION` | Red ×1（盲） | `04_red_evaluation.md`（PARTIAL，15 findings） | `144ba412` |
| 10 | `BLUE_ARCHITECTURE_REFLECTION` | Blue 架构 ×1 | `05_blue_architecture_reflection.md`（ARCHITECTURE_GAP = 1） | `52eac169` |
| 11 | `WORKFLOW_RETROSPECTIVE` | Controller | `06_workflow_retrospective.md` | `52eac169` |
| 12 | `IMPROVEMENT_SYNTHESIS` + `ROUND_REPORT` | Controller | `09_improvement_ledger.md`, `09_round_report.md` | `0a451ab5` |
| 13 | `USER_IMPROVEMENT_REVIEW` | **待用户** | — | — |
| 14 | `BUILD_NEXT_RESUME_CANDIDATE` | Controller | `10_next_resume_candidate.md`（待闸口后） | — |
| 15 | `CLOSE` | Controller | 归档 + PR #282 | — |

`batch_checkpoint_policy: LINK_ONLY_PAUSE`。阶段 4 与 6 均按链接暂停点发布；
用户在阶段 1 的「照 020 一样委托」被解释为 Resume Gate 代行 + 全跑授权，故未阻塞。

## 执行者实例

| 阶段 | 实例数 | 隔离方式 | 可见性 |
| --- | --- | --- | --- |
| `BUILD_SIMULATED_RESUME` 核验 | 1 | 独立 context | 只读 canonical 源 |
| `RED_WAVE_1` | 2 | `PHYSICAL_CONTEXT_ISOLATION` | 互不可见；只读 frozen resume + attack-model |
| `BLUE_WAVE_1` | 候选人 2 + 架构 1 | 同 Skill、同 register；架构实例只读 canonical 源 | 后半批候选人**可读**前半批成品以对齐口径 |
| `RED_WAVE_2` | 1 | 盲 | **不得**读两份封存架构笔记与 canonical 源 |
| `BLUE_WAVE_2` | 候选人 2 + 架构 1 | 同 Wave 1 | 候选人**可读** Red 2 的公开盲评，**不得**读封存笔记 |
| `RED_EVALUATION` | 1 | 盲 | **不得**读封存笔记与 canonical 源 |
| `BLUE_ARCHITECTURE_REFLECTION` | 1 | 判决性质 | 可读全部产物 + 两份封存笔记 + canonical 源 |

## 隔离状态

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

- **上下文隔离是物理的**（独立 context、无共享记忆）；**文件系统是共享的**。
- 允许读哪些文件靠**指令约束 + 事后自报审计**，**不是沙箱**。本轮所有隔离声明**均为自我申报**。
- 本轮观测到 **3 次**泄漏向量，全部自报、无一由沙箱发现，详见 `06_workflow_retrospective.md §4.2`。
  `IMP-020-14` 尚未生效，本轮按原样带病运行，**不当作已解决**。

## 阶段依赖违规（Controller 自身）

| 事项 | 说明 | 处置 |
| --- | --- | --- |
| Resume Gate 措辞方向错误 | Controller 把第 1 条改成「复杂请求进入 ReAct 路径」，实际是准入 fail closed | **不回写 frozen resume**；进 `IMP-021-08` / `G-08` |
| manifest 非法 YAML | 自 `red_wave_1` 起跨多个 stage commit 无校验 | 已修复；进 `IMP-021-14` |
| 等待循环命中占位 blob | 以「文件存在」为条件，误判 336/341 字节占位符为产物 | 已改为尺寸阈值 + mtime；进 `IMP-021-17` |
| 对缺陷的转述本身不准 | Arch §14 的「写错目录」经复核不成立 | 已按源码更正（`00_artifact_links.md`）；进 `IMP-021-13` |

**本轮未复现** round 020 的 `F-20`（Red Final 与 Blue Reflection 并行完成导致 Reflection 重写）：
Red Final 先冻结提交（`144ba412`），Blue Reflection 才开工。**顺序被强制。**

## 冻结 Resume 的处理

`01_simulated_resume.md` 在 `bcd00a61` 冻结，**全程未改**。
Blue Wave 1 的 `A56` 暴露第 1 条措辞方向错误后，Controller 的处置是：

```text
verdict immutable —— 不回写 frozen resume；
错误进入 09_improvement_ledger.md（IMP-021-08 / G-08），
并由 10_next_resume_candidate.md 在下一轮改成可复核措辞。
```

本轮 Red 全程只读冻结版；Resume Gate 的处置记录写在 `00_artifact_links.md`（Red 不可读），
**不进入 resume 文件本身**（否则等于给 Red 发路标）。
