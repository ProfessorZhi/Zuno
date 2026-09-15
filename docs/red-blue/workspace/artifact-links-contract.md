# Red / Blue Stable Artifact Link Contract

本文件是 Red / Blue 的用户可见链接契约。它只规定 artifact 的稳定路径和聊天 handoff，不改变 Red / Blue 的输入 firewall、Skill pinning 或 Evaluation 语义。

## Round Init

每个正式 Round 初始化时必须创建：

```text
docs/red-blue/workspace/<round-id>/00_artifact_links.md
```

并预创建所有正式 stage artifact。尚未执行的 artifact 内容只包含：

```text
status: NOT_STARTED
```

以及必要的 visibility / stage 说明。不得预生成未来问题、答案、评价或架构结论。

预创建的目的只有一个：从 Round Init 起，每个用户可见 artifact 都拥有永久稳定的 GitHub URL，不出现阶段完成后才知道链接或用户点击 404 的情况。

## Stable paths

至少预创建：

```text
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
09_improvement_ledger.md
09_round_report.md
10_next_resume_candidate.md
```

Stage 执行时必须在原路径原地更新，不为了新版本换文件名或另建临时正式文件。

## Artifact index

`00_artifact_links.md` 继续作为内部稳定导航页，包含本轮全部 artifact 的可点击 GitHub 链接。它不要求在每个聊天 checkpoint 都发送给用户。

用户可以查看 sealed Blue notes；`SEALED_FROM_RED` 只约束 Red actor 的输入 allowlist，不约束项目 Owner 查看。

## Chat checkpoint：默认只发当前产物

聊天输出保持简洁。每个用户可见 checkpoint 默认只提供**本阶段刚生成的正式 artifact 直链**，不同时铺开整轮所有链接，也不默认发送 PR、总入口、manifest 或未开始阶段的 placeholder。

### Resume Gate

模拟简历体量小且需要人工审核：

```text
完整贴出模拟简历正文
+
01_simulated_resume.md 直接 GitHub 链接
```

### Red / Blue Batch

100 题或 100 答体量较大：

```text
3–8 个最有代表性、信息量最高的精辟片段
+
当前完整文档直接 GitHub 链接
```

Red checkpoint 摘出代表性攻击问题；Blue checkpoint 摘出代表性回答或关键暴露点。不得把 100 题 / 100 答全文重新贴进聊天。

### Final / Reflection / Report

默认给 3–8 条最关键结论或 finding，再给当前正式文档直链。

只有用户显式要求“全部链接 / 总入口 / PR / sealed notes”时，才额外发送对应链接。

不得只发送：

```text
文件名
仓库相对路径
commit SHA
“已完成”
```

## Stage mapping

```text
USER_RESUME_REVIEW
→ 01_simulated_resume.md

BATCH_CHECKPOINT_RED_1
→ 02_red_questions.md

BATCH_CHECKPOINT_BLUE_1
→ 03_blue_answers.md

BATCH_CHECKPOINT_RED_2
→ 04_red_wave2_review_and_questions.md

BATCH_CHECKPOINT_BLUE_2
→ 04_blue_wave2_answers.md

RED_EVALUATION
→ 04_red_evaluation.md

BLUE_ARCHITECTURE_REFLECTION
→ 05_blue_architecture_reflection.md

WORKFLOW_RETROSPECTIVE
→ 06_workflow_retrospective.md

USER_IMPROVEMENT_REVIEW
→ 09_round_report.md
→ 09_improvement_ledger.md

BUILD_NEXT_RESUME_CANDIDATE
→ 10_next_resume_candidate.md
```

Sealed architecture notes 仍在 Round 中保存，但默认不作为 Candidate checkpoint 的聊天链接；用户要求查看时再提供。

## Firewall invariants remain unchanged

稳定链接不能成为越权输入。

Red Wave 2 / Red Final 即使知道 sealed architecture notes 的 URL，也不得读取其内容。Blue Wave 2 Candidate 也不能使用 Wave 1 sealed notes coaching。角色输入仍以 manifest / protocol allowlist 为准。
