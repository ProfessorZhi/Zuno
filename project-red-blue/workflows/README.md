# Red/Blue 工作流

本目录只负责把已经冻结的 Red Team Kernel、Blue Defender 规则、Gap Register 和 Build-vs-Buy 评审组合成可执行工作流。它不是第二套 Kernel，也不拥有 Zuno 架构事实。

## 统一审计对象：Project Package

三套工作流都审查完整 Project Package，而不是只审查 `Architecture Docs`：

```text
Background / User / Pain / Product Positioning
  → Competitor / Existing Alternative
  → Team / Ownership / Development Process
  → Target Architecture / Implementation
  → Model / Data / RAG / Memory / Agent / Tool
  → Deployment / Infrastructure / GPU / Serving
  → Evaluation / Evidence / Landing / Operations
  → Current / Target / Future / Unknown
```

这只是组合输入模型，不是新的事实源。背景、团队、交付、模型、部署和证据仍必须按 [00-charter.md](../00-charter.md) 的 Owner 路由回对应文档。任何组织、法院、客户、用户量、团队人数、部署历史或个人贡献都不能从 Architecture 反推。

| 工作流 | 目的 | 是否允许修改材料 |
|---|---|---|
| [01-red-team-interview-workflow.md](01-red-team-interview-workflow.md) | 模拟真实面试官，只问、追问、评分和记录 Gap | 否 |
| [02-blue-team-answer-workflow.md](02-blue-team-answer-workflow.md) | 只依据已 Pin 的事实源回答红队问题 | 否 |
| [03-red-blue-optimization-workflow.md](03-red-blue-optimization-workflow.md) | 红问、蓝答、聚类、研究、架构提案、用户确认和复测 | 只有此工作流允许进入修复门，但仍需 User Gate |

## 组合方式

```text
只模拟面试
  → Workflow 01

测试当前架构材料能否回答问题
  → Workflow 01 + Workflow 02

真正优化项目、架构或简历
  → Workflow 03
     ├─ Red Interview
     ├─ Blue Source-Constrained Answer
     ├─ Red Judge / Gap Clustering
     ├─ Blue Architect / Research
     ├─ User Gate / Canonical Sync
     └─ Red Retest
```

三套工作流都必须服从 [00-charter.md](../00-charter.md)。未来 Skill 的接口草案见 [../skill/](../skill/README.md)；当前不生成正式 `SKILL.md`。
