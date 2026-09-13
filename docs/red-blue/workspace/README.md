# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 面试模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

默认 `main` 不保留 active round folder；只有用户明确启动一轮以后，才创建：

```text
docs/red-blue/workspace/<round-id>/
```

一轮一个文件夹，固定产物顺序如下：

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

## 为什么先生成模拟简历

真实面试官通常看不到 Zuno 的 Project、Architecture、Module 和 Evidence 文档。他看到的是候选人的简历，然后依据自己的工程经验、岗位要求和面试风格追问。

因此每轮先由 Controller / Resume Builder 阅读当前 Zuno 文档与已有简历风格，生成一份**当前文档能够负责的模拟简历**。它既不能把 Target 写成实现，也不能为了安全把所有技术成果删成“参与项目”。

模拟简历冻结后，Red 的输入被收窄为：

```text
模拟简历
岗位 / JD / 轮次
Red Interview Skill
模型通用知识
```

Red 不再读取 Zuno docs。这样得到的问题才是“面试官看到这份简历会怎么问”，而不是“Reviewer 看完架构以后知道哪里该问”。

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

需要再次攻击时，新建下一轮，不在同一文件夹继续追加第二批题。这样每轮都对应一版明确的 Zuno 文档和一份明确的模拟简历。

## 两种模式

`CHATGPT_AUTO` 与 `AGENT_AUTO` 使用完全相同的文件结构和 source policy。

- `CHATGPT_AUTO`：在一个 ChatGPT 对话中程序性隔离角色；每阶段完成立即写入 GitHub。
- `AGENT_AUTO`：为 Resume Builder、Red、Blue、Red Evaluation、Blue Reflection、Workflow Retrospective 建立独立 context；所有可观察输入输出仍归档到同一 Round 文件夹。

两种模式都保存 `08_session_transcript.md`，但都不保存或伪造模型私有 chain-of-thought。

## 关闭一轮

完成全部阶段以后，整个目录原样移动到：

```text
docs/red-blue/rounds/<round-id>/
```

Round 里的坏问题、弱回答、用户批评和失败尝试不做“漂亮化重写”。它们是后续改进 Red Skill、文档和简历的证据。