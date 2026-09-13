# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 面试模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

## Active Round 以 GitHub 为运行容器

正式 Round 从固定 `main` SHA 创建独立 branch：

```text
red-blue/<round-id>
```

并创建 `docs/red-blue/workspace/<round-id>/`。固定九个文件保持不变：

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

```text
读取 live Round branch HEAD
→ 核对 manifest stage / allowlist
→ 从该 HEAD 读取正式输入
→ 生成 artifact
→ 更新 manifest / transcript
→ commit
→ 下一阶段重新读取新的 HEAD
```

Round 启动前已经知道的用户约束进入第一笔 Round transaction；中途新反馈也先提交，再影响后续阶段。

## Resume-first

`01_simulated_resume.md` 冻结后，Red 只能读取冻结模拟简历、岗位 / JD / 面试轮次、Red Interview Skill 和模型通用知识。它不读 Zuno canonical docs、源码、PR 或 Blue answer key。

## `02_red_questions.md` 现在是 Interview Plan，不是固定问卷

默认保存：

```text
6–10 条 SPOKEN_SEEDS
DYNAMIC FOLLOWUP_POLICY
若干 BRANCH_EXAMPLES
100 问 PRESSURE_SUITE
```

`SPOKEN_SEEDS` 是面试官最初真正可能说出口的问题，只负责打开话题。候选人回答以后，Red 必须从上一答中抽取技术、数字、选择、困难、Ownership 或 bad case，再决定下一问。

Pressure Suite 负责离线覆盖，不在 45–60 分钟现场逐题朗读。

### 一个问题只问一件主要事情

旧版常把“机制、代码、测试、指标、Trade-off”塞在一个问题里。现在这些验证拆成连续对话。例如：

```text
你刚才说检索效果掉了，最开始怎么发现的？
→ 具体是哪里排错了？
→ 你最后改了哪一层？
→ 那个 Recall 是怎么测的？
```

深度来自每一答触发下一问，而不是问题本身越来越长。

### Kill Switch 是 Controller 元数据

如果候选人连续无法建立某个 Claim 的 Ownership / mechanism，Red 记录 credibility break 并自然换 thread。Kill Switch 不作为面试官口头话术展示。

## USER_RED_REVIEW

校准 Round 默认 `red_review_gate: REQUIRED`。Red 第一版 Interview Plan 提交后停止推进，用户检查：

- Seed 是否像真人会问；
- Branch Example 中下一问是否真的从上一答长出来；
- 是否还有 Reviewer checklist 味；
- 是否有复合长问；
- 是否无信息增益地拆原子细节。

用户结果：`APPROVE / REQUEST_REVISION / ABORT`。只有 APPROVE 后 `red_questions_status` 才能 `FROZEN`，Blue 才能开始。

如果用户认为是 Skill 结构问题，而不是局部措辞问题，可以把当前 Round `SUPERSEDED`，先更新 Skill，再用新 Skill 开新 Round。失败版本继续保留。

## 两种模式的隔离强度

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED`，不能证明物理遗忘；`AGENT_AUTO` 在 Red 使用独立 context 时可声明 `PHYSICAL_CONTEXT_ISOLATION`。两种模式仍使用同一 GitHub state machine。

## 关闭一轮

完成 Round 后把 workspace 原样移动到 `docs/red-blue/rounds/<round-id>/`，Draft PR 转 ready，required CI 通过后 merge。坏问题、弱回答、用户批评和修订历史都保留。
