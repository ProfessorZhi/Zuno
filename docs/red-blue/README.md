# Zuno Red / Blue Interview Review

`docs/red-blue/` 用来验证三件彼此不同的事：当前 Zuno 文档能否压缩成可信简历；一个只看到简历的大厂面试官会怎样追问；候选人的回答最终暴露的是项目事实、实现证据、简历、架构，还是 Red 自己的问题。

Red / Blue 不拥有 Project History、Target Architecture、Current Evidence 或个人 Ownership。它只产生压力、回答、评价和改进建议，正式事实仍回到各自 Canonical Owner。

## Resume-first

真实面试官先看到简历，而不是 `docs/architecture/`。正式 Round 先由 Resume Builder 读取固定 `zuno_base_sha` 的 Project、Architecture、Modules、Evidence、选定 provenance 和已有简历风格，生成 `01_simulated_resume.md`。模拟简历冻结以后，Red 的正式输入只剩模拟简历、岗位 / JD、Red Interview Skill 和模型通用知识。

## GitHub 在流程中间

```text
main@固定 SHA
→ red-blue/<round-id>
→ docs/red-blue/workspace/<round-id>/
→ stage 读取 live branch HEAD
→ artifact + manifest + transcript
→ commit
→ 下一 stage 重新读取新 HEAD
```

GitHub commit 是阶段边界。聊天里未提交的摘要、上一角色临时输出和 Controller 草稿不能直接跨阶段成为正式输入。Round 启动前已经知道的用户约束进入第一笔 transaction；中途新反馈也先提交，再影响后续阶段。

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED`，不能证明同一聊天已经物理遗忘项目资料。需要严格 blind Red 验收时使用拥有独立 Red context 的 `AGENT_AUTO / PHYSICAL_CONTEXT_ISOLATION`。

## Red 不再预写一场 30 问面试

Round 仍然可以保存 100 个高质量问题，但它们现在只叫 **Pressure Suite**：用于离线覆盖、漏项检查和 Workflow Retrospective。

真实 45–60 分钟一面由另一套机制执行：

```text
6–10 个 Spoken Seeds
→ 候选人回答
→ Red 抽取刚刚出现的技术、数字、选择、困难、Ownership 或 bad case
→ 只选一个最高信息增益 handle 继续问
→ 根据新回答继续或换 thread
```

近期公开 Agent / LLM 应用面经反复出现这种行为。字节的一面记录是前段了解个人经历和项目，后段根据项目细节不断追问；淘天的一组记录里，面试官沿着“为什么拆子 Agent → skill 能不能替 → 你说不能替，那局限在哪 → 改变前提后本质区别是什么 → 什么时候会出错 → 你真遇到过吗”连续走同一条线；另有面经直接描述面试官会根据候选人说出的关键词继续追问。抽样与边界见 [`interview-behavior-evidence-2026-09.md`](interview-behavior-evidence-2026-09.md)。

这个变化修正了之前的根本问题：旧 Red 虽然每道题技术上合理，却仍然像把 Reviewer checklist 改写成问句。

## 一个问题只承担一个主要意图

真人深挖通常靠连续短问，而不是一题同时要求背景、机制、代码、测试、故障和 Trade-off。

更自然的表面是：

```text
你刚才说这里做了 GraphRAG，最开始到底哪里出了问题？
为什么当时这么改？
这个数怎么测出来的？
这块是你自己负责的吗？
那如果请求其实已经成功了呢？
```

Red 内部仍然维护 Claim、risk、Ownership confidence、Evidence gap、Kill Switch 等 Controller state，但这些元数据不作为面试官话术展示。

## 面试按时间和信息增益走，不按覆盖矩阵走

默认节奏更接近：

```text
3–5 min   自我介绍 / 项目选择
20–30 min 一条主线程深挖
10–15 min 第二线程或基础知识
5–10 min  场景 / 故障 / Build-Buy
3–5 min   收尾 / 反问
```

第一条线程很有信息量，可以追很久；Ownership 很快断掉，就自然换题。真实面试不要求平均覆盖四条 Resume bullet。

### Ownership Kill Switch

Kill Switch 仍然保留，但只属于 Controller。候选人连续两轮只能讲团队概念、无法说明本人改动时，Red 记录该 Claim 暂时无法建立，然后像真人一样说“行，那我们再看一下你另一块工作”，而不是继续十几道源码同义追问。

## Build / Buy、故障和基础仍然重要

新框架没有降低技术深度。Red 仍会追成熟方案已经解决什么、为什么仍需要自己的 Delta、框架补齐以后是否删除；也会从真实项目自然进入 timeout、幂等、并发、DB isolation、Recall/MRR、TCP 或算法基础。

变化在于**何时问**。候选人刚讲 Tool timeout，再追 HTTP/TCP 和 retry 很自然；候选人还没有讲过任何外部调用时突然抛 unknown outcome，会更像架构 Reviewer。

真实面试也可能直接切到 Redis、数据库、网络或算法，所以不强制每道基础题都伪装成 Resume Claim 的延伸。

## USER_RED_REVIEW：先审 Red，再运行 Blue

工作流校准期默认：

```text
red_review_gate: REQUIRED
```

Red 第一次提交 `02_red_questions.md` 后进入 `USER_RED_REVIEW`。用户检查的重点现在是：Seed 是否像真人会问；Branch Example 里下一问是否真的从上一答长出来；有没有复合长问；有没有无信息增益的原子化追问。

用户结果：`APPROVE / REQUEST_REVISION / ABORT`。只有 APPROVE 后 Red plan 才能 `FROZEN`，Blue 才允许执行。

如果用户判断问题不是局部措辞缺陷，而是 Red Skill 本身有结构问题，可以把当前 Round 标记 `SUPERSEDED`，先独立更新 Skill，再用新 Skill 开新 Round。失败的题单和批评继续保留，不做漂亮化重写。

## 一轮后续阶段

```text
Frozen Red Interview Plan
→ Live Interview / Blue answers
→ Red Evaluation
→ Blue Architecture Reflection
→ Workflow Retrospective
→ Archive / CI / Merge
```

Red Evaluation 评价实际发生的问答分支，而不是检查 100 问是否逐题完成。

## Blue Architecture Reflection：面试断点怎样路由

Blue Reflection 把问题重新分类：

```text
SIMULATED_RESUME_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_ZUNO_CHANGE
```

面试官追到历史实现细节，而 Project documentation 没恢复，不意味着 Target Architecture 需要新增对象。只有 Owner、Authority、State、Recovery、Security、Contract 或 Build/Buy 因果本身不成立，才进入 Architecture Revision。

## 固定九份 artifact

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

活动 Round 位于 `docs/red-blue/workspace/<round-id>/`。关闭前在同一 branch 上归档到 `docs/red-blue/rounds/<round-id>/`，required CI 通过后 merge。

Round 的成功标准不是题量或 PASS 率，而是持续提高：**简历 Claim 的可信度、项目文档对个人实现的工程解释力、以及 Red 是否真的像一个会听人说话的面试官。**
