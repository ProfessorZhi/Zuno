# Blue Fix Routing：蓝队修复与回写

红队发现问题后，不能直接在 QA 里把答案写长来“关闭”。先分类，再决定由谁修复、写到哪里、需要什么证据。

## Gap 分类

| Gap | 典型表现 | 修复去向 |
|---|---|---|
| `FACT_MISSING` | 用户数、团队、部署、当前状态未知 | 用户补充；进入事实台账 |
| `PROJECT_REALITY_GAP` | 背景、用户、上线、试点说不清 | 项目背景/README；必要时补 Evidence |
| `OWNERSHIP_GAP` | “我们做了”但个人边界模糊 | 团队协作说明、简历、项目 QA |
| `PRODUCT_POSITIONING_GAP` | WorkBuddy/开源替代下价值不成立 | 架构 Part A、产品定位、验证实验 |
| `SCOPE_GAP` | 小团队/小规模却承诺过大 | Product Scope、Program、Architecture ADR |
| `ARCHITECTURE_GAP` | Owner、状态、版本、Failure 或边界未冻结 | `docs/architecture/`、`docs/modules/`、ADR |
| `IMPLEMENTATION_GAP` | Target 有设计但代码/测试没有 | 代码、Migration、Test、Program |
| `MEASUREMENT_GAP` | 效果、延迟、成本没有证明 | `docs/evidence/`、Eval、Benchmark |
| `SECURITY_GAP` | 权限、租户、审批、审计不足 | 09 Security、ADR、安全测试 |
| `DELIVERY_PROCESS_GAP` | 需求、评审、发布、反馈流程混乱 | `docs/governance/` 或项目流程文档 |
| `NARRATIVE_GAP` | 事实存在，但人话讲不清 | 对应 Part A、README、面试材料 |
| `DECISION_PENDING` | 多个方案都合理，尚未选择 | ADR 或保持待决，不得假装已定 |

## 回写目标矩阵

| 内容 | 正式 Owner |
|---|---|
| 产品定位、用户任务、非目标 | `docs/architecture/architecture.md` Part A、01 Product |
| 领域对象、模块 Contract、状态、Failure | 对应 `docs/modules/` Owner 文档 |
| 重大取舍、WorkBuddy/开源替代、自研边界 | `docs/decisions/` ADR |
| 当前用户/规模/部署/质量证据 | `docs/status/` 与 `docs/evidence/` |
| 团队实际协作和开发过程 | 用户事实台账；确认后进入适合的 governance/project 文档，不塞进 Runtime Contract |
| 面试表达与追问 | `docs/verification/interview-qa/` 或外部 interview-workspace，不改成架构事实 |

## 蓝队修复顺序

```text
1. 先确认事实：用户 / 代码 / 测试 / Trace / Eval
2. 判断是缺信息、表达差、范围过大还是架构真的不成立
3. 生成修复 Proposal，标注目标文件和状态
4. 用户确认 Proposal 或补充事实
5. 修改唯一 Canonical Owner
6. 同步架构图、Coverage、Status/Evidence（如适用）
7. 运行验证器
8. 用不同问法 Red Retest
```

设计含义变化时，至少检查：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_architecture_interview_qa.py
```

## Agent Proposal 的写法

Agent 不应直接写：

> Zuno 已经有 300 个企业用户，团队 5 人，采用微服务部署。

应写成：

```text
PROPOSAL_AGENT：如果目标是企业法律试点，建议先选择 1 个 Matter/合同审查场景，
以模块化单体或少量运行域交付；用户数量、团队人数和部署状态仍需用户确认。
```

## Gap 关闭标准

- `FACT_MISSING`：用户给出事实或明确 UNKNOWN，并更新台账；
- `PROJECT_REALITY_GAP`：背景、用户、当前状态和边界可被复述且不夸大；
- `ARCHITECTURE_GAP`：Owner/Contract/Failure 通过架构评审并完成验证；
- `IMPLEMENTATION_GAP`：代码、测试或运行证据补齐，不能只改文档；
- `MEASUREMENT_GAP`：有固定数据集、基线、指标和可复现结果；
- `NARRATIVE_GAP`：30 秒、90 秒和 3 分钟版本都能被换问法验证；
- 其他 Gap：裁判确认修复范围后重新红队盘问。
