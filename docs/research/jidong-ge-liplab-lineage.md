# 葛季栋 / LIPLAB Research Lineage

> status: research-reference
> last_verified: 2026-08-27
> current_implementation_evidence: not-implied

本文件记录与 Zuno 项目起源相关的**研究谱系**，不把论文、导师项目或课题组能力自动转换为 Zuno Current。

## 身份消歧

目标研究者：葛季栋 / Jidong Ge，南京大学软件学院相关研究团队。

后续论文进入 VERIFIED SET 时优先使用：

- 南京大学官方教师/团队页面；
- 明确的 Nanjing University / Software Institute affiliation；
- DBLP PID `128/5781`；
- ORCID `0000-0003-1773-0942`；
- 已核验 co-author network；
- 官方项目/论文列表。

只有姓名匹配不足以确认作者身份；不确定时标 `UNVERIFIED`。

## 研究谱系

### 1. Software Process / Workflow / Collaboration

早期研究覆盖工作流、软件过程、协同与调度问题。这一脉络可以帮助解释为什么“过程状态、协同、失败和恢复”长期是研究背景，但没有证据证明当前 Zuno Runtime 的 PlanVersion、Single Controller 或 Replan Barrier 直接来自某一篇论文。

**Relation:** `CONCEPTUAL_LINEAGE`

### 2. Intelligent Judiciary / Legal NLP

与 Zuno 项目问题最直接相关的脉络包括智慧司法、法律信息处理、多源证据链、裁判说理、法条推荐、案件事实与法律条文关系等。

这类工作说明课题组并不是从“做一个法律 Chatbot”开始，而是在长期司法信息化与法律智能问题中积累了多个独立 Research Artifacts。

**Relation:** 项目/问题层 `DIRECT_LINEAGE`；具体算法进入某版本需另证。

### 3. Legal Capability Artifacts

代表性 Research Artifact 类型包括：

- 法条推荐；
- 事件 / 争议 / 案件事实抽取；
- Fine-grained Fact–Article correspondence；
- 法律模型；
- 法律问答 / 判决相关方法；
- 专业 Evaluation Dataset / Benchmark。

这些成果最自然的工程化形态通常是稳定的专业 Capability，而不是让 Runtime 永久依赖某个论文模型名字。

**Relation:** `CAPABILITY_LINEAGE`

### 4. Intelligent Software Engineering / Testing

课题组在 Program Repair、Code Completion、Testing 等方向的积累可以提供“质量不能只看单个 headline metric、实现需要可替换、复杂机制要接受测试”的工程思想背景。

除非有更直接证据，不应把这些研究硬接成某个 Zuno Module 的来源。

**Relation:** `BACKGROUND_ONLY` 或 `CONCEPTUAL_LINEAGE`

### 5. Legal LLM / Evaluation

LawBench、LJPCheck、法律模型等工作最重要的工程启示不是某个具体模型分数，而是：法律 AI 的“可用”需要按任务、失败模式和质量条件拆开评估。

进入工程系统后，这种思想进一步转化为：

```text
benchmark result
→ scoped provider qualification
→ task-class eligibility
→ regression / failure taxonomy
→ release evidence
→ ablation / kill test
```

**Relation:** `CAPABILITY_LINEAGE` / `CONCEPTUAL_LINEAGE`

## 研究成果不能怎样使用

禁止从本文件推导：

- “导师做过 X，所以 Zuno 已经实现 X”；
- “论文 A 就是 Module 03/05/09 的直接代码来源”；
- “课题组发表的论文属于用户本人 Ownership”；
- “某篇论文效果好，所以对应 Zuno Capability 已经 qualified”；
- “研究原型存在，所以 Production Readiness 已建立”。

## 推荐 Traceability

后续真正要建立的是：

```text
Research Problem
→ Research Artifact
→ Artifact 的输入 / 输出 / 适用范围 / Evaluation
→ 进入真实系统后的 Engineering Gap
→ Stable Capability Semantics
→ Provider / Qualification
→ Zuno responsibility
→ Current / Target / Unknown
→ Evidence
```

如果中间任何一跳没有证据，保持 `UNVERIFIED`，不要用故事完整性替代事实。
