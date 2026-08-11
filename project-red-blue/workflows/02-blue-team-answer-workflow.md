# 02 Blue Team Answer Workflow

## 定位

本工作流是**受事实源约束的答辩（Source-Constrained Defender）**。它的目标不是让回答听起来完整，而是暴露当前材料实际上能不能回答红队问题。

该工作流不修改架构、不临时增加 Target、不编造项目背景、不把公开研究结果塞回 Current，也不把 `BLUE_PROPOSAL` 当成现有答案。

## Source Boundary

每个 Answer Session 开始前必须 Pin：

```text
source_commit
architecture_version
resume_version
project_fact_version
```

允许读取的事实源由 Session manifest 指定，通常包括：

- `docs/architecture/`；
- `docs/modules/`；
- `docs/decisions/`；
- `docs/status/`；
- `docs/evidence/`；
- `project-red-blue/01-project-facts.md`；
- 已确认 Project Facts、Resume / Project Material。

如果问题涉及外部项目，但当前正式材料没有最终 Build-vs-Buy 结论，不能在回答过程中临时研究并伪造一个已存在的项目决策。应记录“当前正式材料尚未形成最终决策”，把研究交给 Workflow 03。

## Answer Status

| 状态 | 含义 |
|---|---|
| `SUPPORTED` | Pin 的事实源直接支持完整回答 |
| `PARTIALLY_SUPPORTED` | 只有部分陈述可被支持，其余必须收缩 |
| `UNSUPPORTED` | 当前来源无法支持该陈述 |
| `UNKNOWN` | 现有来源不能判断，且没有足够重建证据 |
| `CURRENT_EVIDENCE_MISSING` | Target 或文档有描述，但 Current 缺实现/测试/Trace/Eval 证据 |
| `TARGET_NOT_DEFINED` | 当前 Target 没有定义该机制或边界 |

## 执行步骤

1. 读取 Red Question 和 `Claim Under Test`，不提前读取未经授权的研究材料；
2. 只在已 Pin 的 Source Boundary 内查找支持、冲突和缺失信息；
3. 分开回答事实、Target、Current、Future、个人贡献和公开背景；
4. 对无法支持的部分直接降级为相应 Answer Status；
5. 记录 Sources Used、Unsupported Portion、Confidence 和需要后续研究的 Gap；
6. 将 Blue Answer 返回给 Red Judge 或 Workflow 03，不在现场修改文件。

每条回答至少记录：

```text
Question ID
Claim Under Test
Answer
Answer Status
Sources Used
Unsupported Portion
Current / Target Boundary
Confidence
```

## 禁止的补全方式

以下内容不得出现在 Source-Constrained Answer 中：

- “如果重新设计，我们可以……”被说成当前已经实现；
- 从南京大学、法院、开源项目或公开资料推断 Zuno 的历史事实；
- 用最新 Web Research 覆盖 Pin 版本中没有的决策；
- 把目标文档、类名、Mock Test 或目录结构当成生产证据；
- 为了提高分数替用户补出团队人数、用户规模、QPS、上线状态或个人代码贡献。

## 输出

输出逐题 Blue Answer Record。回答失败不是流程异常，而是有效发现：它说明当前事实、架构文档、简历或证据边界存在 Gap，应由 Workflow 03 聚类和修复。
