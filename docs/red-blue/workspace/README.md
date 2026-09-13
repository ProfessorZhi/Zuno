# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 面试模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

## Active Round 不在聊天里运行

正式 Round 以 GitHub branch / Draft PR 为运行容器。用户启动一轮以后，先从固定 `main` SHA 创建：

```text
red-blue/<round-id>
```

然后在这个 branch 上创建：

```text
docs/red-blue/workspace/<round-id>/
```

一轮固定九个文件：

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

Draft PR 是活动 Round 的 GitHub 入口。`main` 不需要保存半完成的 workspace。

## GitHub 是阶段交接面

每个阶段都执行同一套动作：

```text
读取 Round branch HEAD
→ 核对 manifest 当前 stage 和输入 allowlist
→ 从该 HEAD 读取允许输入
→ 生成本阶段 artifact
→ 同步更新 manifest / transcript
→ commit
→ 下一阶段重新读取新的 HEAD
```

未提交的聊天摘要、上一角色临时文本和 Controller 草稿都不能直接成为下一阶段输入。GitHub 在这里承担的是**状态总线和 write barrier**，不只是最后存一份日志。

用户在中途提出会影响当前 Round 的评价或约束时，同样先写入并提交：

```text
07_user_feedback.md
08_session_transcript.md
```

提交完成后再继续运行。

## 为什么先生成模拟简历

真实面试官通常看不到 Zuno 的 Project、Architecture、Module 和 Evidence 文档。他看到的是候选人的简历，然后依据自己的工程经验、岗位要求和面试风格追问。

因此每轮先由 Resume Builder 从固定 `zuno_base_sha` 读取当前文档与已有简历风格，生成一份**当前文档能够负责的模拟简历**。它既不能把 Target 写成实现，也不能为了安全把所有技术成果删成“参与项目”。

`01_simulated_resume.md` 必须先冻结并提交。Red 随后从新的 GitHub HEAD 重新读取模拟简历、岗位信息与 Red Interview Skill，再生成 `02_red_questions.md`。

## 两种模式的隔离强度不同

`CHATGPT_AUTO` 与 `AGENT_AUTO` 使用相同的 GitHub state machine 和文件结构，但不能声称相同的 context firewall。

`CHATGPT_AUTO` 在一个 ChatGPT 对话中执行。全过程可通过 GitHub 恢复和审计，但同一对话不能证明模型已经物理遗忘 Resume Builder 先前看到的 Zuno 文档，所以标记为：

```text
LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

它适合快速测试模拟简历、Red Skill、问题质量和 Blue 文档支撑能力。

`AGENT_AUTO` 为 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective 建立独立 context，同时仍然要求所有 handoff 经过 GitHub commit。需要正式证明 Red 只看到简历时，使用：

```text
PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

## 一轮的阶段

```text
模拟简历
→ Red 批量提问（默认 100）
→ Blue 根据 Zuno docs 逐题回答
→ Red 只根据简历和回答做面试官评价
→ Blue 根据 docs 反思真正的架构 / 文档 / 证据问题
→ Workflow Retrospective 反过来审 Red 问题质量和 Harness
→ 保存用户反馈
→ 归档整轮
```

每个箭头都对应一次 GitHub commit barrier。需要再次攻击时，新建下一轮，不在同一文件夹继续追加第二批题。

## 关闭一轮

完成全部阶段以后，在 Round branch 上把：

```text
docs/red-blue/workspace/<round-id>/
```

原样移动到：

```text
docs/red-blue/rounds/<round-id>/
```

然后把 Draft PR 转为 ready，跑 required CI，merge 后重新读取精确 `main` HEAD。

Round 里的坏问题、弱回答、用户批评和失败尝试不做“漂亮化重写”。它们是后续改进 Red Skill、文档和简历的证据。