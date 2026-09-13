# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 面试模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

## Active Round 以 GitHub 为运行容器

正式 Round 从固定 `main` SHA 创建独立 branch：

```text
red-blue/<round-id>
```

并在 branch 上创建：

```text
docs/red-blue/workspace/<round-id>/
```

固定九个文件：

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
```

Draft PR 是活动 Round 的 GitHub 入口。`main` 不保存半完成 workspace。

## GitHub 是阶段交接面

每个阶段都执行：

```text
读取 live Round branch HEAD
→ 核对 manifest stage / allowlist
→ 从该 HEAD 读取正式输入
→ 生成本阶段 artifact
→ 更新 manifest / transcript
→ commit
→ 下一阶段重新读取新的 HEAD
```

未提交聊天摘要、上一角色临时文本和 Controller 草稿不能跨阶段成为输入。Transcript 为每个事件记录 `input_head_sha`；manifest 的 `last_consumed_head_sha` 只记录最近完成阶段真正消费的输入 HEAD，不冒充当前 branch HEAD。

Round 启动前已经知道的用户约束必须在第一笔 Round transaction 中进入 `07_user_feedback.md` 与 transcript。中途新反馈也先提交，再影响后续阶段。

## Resume-first

每轮先由 Resume Builder 从固定 `zuno_base_sha` 读取当前 Project / Architecture / Modules / Evidence 与已有简历风格，生成本轮模拟简历。

`01_simulated_resume.md` 冻结并提交后，Red 只能从新的 GitHub HEAD 读取：

```text
冻结模拟简历
岗位 / JD / 面试轮次
Red Interview Skill
模型通用知识
```

Red 不读 Zuno canonical docs、源码、PR 或 Blue answer key。

## Red 第一轮不是 100 问逐题脚本

默认总压力集仍为 100 问，但题单拆成：

```text
PRIMARY_PATH: 默认 30，允许 25–40
RESERVE_FOLLOWUP: 其余问题
```

Primary Path 模拟真实 45–60 分钟技术一面。Reserve 只在主路径回答触发、用户要求继续深挖或后续复测时使用。

具体实现 Claim 要尽早经过 Ownership / mechanism probe。如果候选人无法说明自己改的真实实现对象和最小机制，Red 触发 Kill Switch，记录该 Claim 的 credibility break 后切到下一条 Claim，不再用十几道同义问题继续追。

## USER_RED_REVIEW

工作流校准 Round 默认：

```text
red_review_gate: REQUIRED
```

Red 提交第一版 `02_red_questions.md` 后进入 `USER_RED_REVIEW`，此时停止自动推进，把 Primary Path 与完整题单交给用户检查。

用户只能给三类结果：

```text
APPROVE
REQUEST_REVISION
ABORT
```

`APPROVE` 后通过单独 Controller commit 把 `red_questions_status` 冻结为 `FROZEN`，Blue 才能开始。

`REQUEST_REVISION` 时先把反馈写入 `07_user_feedback.md` / transcript 并提交；Red 再读取同一冻结简历、Attack Skill、当前题单和这条已提交质量反馈，修改同一个 `02_red_questions.md`，然后重新进入 `USER_RED_REVIEW`。旧版题单由 Git history 保留。

## 两种模式的隔离强度

`CHATGPT_AUTO`：

```text
LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

GitHub 可以约束 handoff，但单对话不能证明物理遗忘。

`AGENT_AUTO` 在 Red 确实使用独立 context 时可声明：

```text
PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

两种模式仍使用同一 GitHub state machine。

## 关闭一轮

完成全部阶段以后，在 Round branch 上把 workspace 原样移动到：

```text
docs/red-blue/rounds/<round-id>/
```

随后 Draft PR 转 ready、required CI 通过、merge，并重新读取 exact `main` HEAD。

坏问题、弱回答、用户批评和修订历史都保留。它们是后续改 Red Skill、Project documentation 和简历 Claim 的证据。
