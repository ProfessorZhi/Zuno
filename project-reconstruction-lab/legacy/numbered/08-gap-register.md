# Gap Register

## 缺口类型

| 类型 | 含义 |
|---|---|
| `BACKGROUND_GAP` | 项目来源、约束或时间线不清 |
| `RECONSTRUCTION_CONFIDENCE_GAP` | 有候选解释，但证据不足以从重建升级为项目事实 |
| `PROJECT_REALITY_GAP` | 用户、上线、规模或真实流程无法证明 |
| `OWNERSHIP_GAP` | 团队或个人责任边界不清 |
| `NARRATIVE_GAP` | 项目说法与事实、证据或范围不一致 |
| `PRODUCT_POSITIONING_GAP` | 用户价值、差异化或非目标不清 |
| `PROJECT_ARCHITECTURE_ALIGNMENT_GAP` | 项目背景、用户任务、领域对象、架构复杂度或简历 Claim 不属于同一条因果链 |
| `BUILD_BUY_GAP` | 自建、复用、扩展、延期没有比较 |
| `OVERENGINEERING_GAP` | 复杂度与团队、规模或阶段不匹配 |
| `ARCHITECTURE_GAP` | 模块边界、Owner、状态、版本、Failure 或 Contract 不完整 |
| `IMPLEMENTATION_GAP` | 关键路径、异常、数据、Schema 或参数细节无法说明 |
| `IMPLEMENTATION_DEPTH_GAP` | 只能说出框架或算法名称，无法说明输入、输出、状态、参数、存储或调用位置 |
| `FAILURE_RECOVERY_GAP` | 无法说明超时、重复、部分成功、恢复、对账、降级或人工接管 |
| `DELIVERY_PROCESS_GAP` | 开发、评审、发布、回滚或协作过程不清 |
| `CURRENT_EVIDENCE_GAP` | Current 结论缺代码、测试、Trace 或运行证据 |
| `MEASUREMENT_GAP` | 指标、基线、数据集、成本或实验无法复现 |
| `SECURITY_GAP` | 权限、租户、隐私、外部副作用或合规不清 |
| `FUNDAMENTAL_GAP` | 依赖的基础原理不能解释 |
| `COMMUNICATION_GAP` | 能力存在但无法按 30 秒、90 秒或深挖节奏清晰表达；不等同于架构缺陷 |
| `RESUME_CLAIM_RISK` | 简历或面试陈述超出本人真实贡献 |

## Gap 生命周期

Gap 不使用简单 OPEN/CLOSED 二值。标准状态为：

```text
OPEN
  ↓
RESEARCHING
  ↓
BLUE_PROPOSED
  ↓
USER_CONFIRMATION_REQUIRED   # 只适用于现实事实或需要人类确认的 Target 决策
  ↓
ACCEPTED_FOR_FIX
  ↓
FIX_IN_PROGRESS
  ↓
RETEST_PENDING
  ↓
CLOSED
```

允许分支：

```text
OPEN → DEFERRED
    当前价值不足、缺外部条件或明确 Future。

OPEN / BLUE_PROPOSED → REJECTED
    红队前提不成立，或候选重建被证据否定。

RESEARCHING → UNKNOWN
    已做合理搜索但仍无法恢复；保留未知并缩小 Claim。
```

红队只能创建/复测 Gap，不得在同一 Session 直接把 Gap 改成 `CLOSED`。蓝队也不能因为写出一个更好的回答就进入 `RETEST_PENDING`；必须先有事实确认、正式架构修改、代码/测试/Eval 或明确范围收缩中的至少一种关闭证据。

## 严重度

```text
P0
    真实性冲突、个人 Ownership 冲突、Current/Target 混淆、越权安全风险、核心背景与架构明显不一致。

P1
    核心架构因果、Build/Buy、实现机制、失败恢复、项目价值或团队可行性无法成立。

P2
    参数依据、非核心成本、表达、扩展能力或暂不影响主线的测量缺口。
```

P0 Gap 未处理时，不应继续把相关 Claim 写进更强的简历、项目介绍或 Production Narrative。

## 记录模板

```text
RB-XXX [OPEN]
类型：
严重度：P0 / P1 / P2
触发 Claim：
truth_status：
reconstruction_confidence：R0 / R1 / R2 / R3 / R4
红队问题：
回答 / 文档断点：
已知事实：
缺少什么：
蓝队回应：
候选修复：
需要用户确认：
需要公开/仓库研究：
需要修改 Target Architecture：YES / NO
需要工程 / Eval：YES / NO
正式去向：
关闭证据：
复测换问法：
复测结果：
```

## 典型路由

| Gap | 首选处理 |
|---|---|
| `BACKGROUND_GAP` / `RECONSTRUCTION_CONFIDENCE_GAP` | Repo / 历史面试 / 公开资料研究 → A/B/C 候选 → 最小用户确认 |
| `OWNERSHIP_GAP` | Git/任务/代码证据 + 候选团队模型 → 用户确认现实分工 |
| `PROJECT_ARCHITECTURE_ALIGNMENT_GAP` | 蓝队重新检查产品定位、领域模型、复杂度和 Domain Profile；必要时正式改架构 |
| `BUILD_BUY_GAP` | `09-open-source-review.md`，输出 ADOPT / EXTEND / BUILD / DEFER |
| `OVERENGINEERING_GAP` | 缩 Scope、减少物理服务、延期能力；不能靠增加文档解释关闭 |
| `ARCHITECTURE_GAP` | 修改 canonical architecture / modules / ADR 后验证 |
| `IMPLEMENTATION_GAP` / `CURRENT_EVIDENCE_GAP` | Codex 工程实现、测试、Trace、Migration、运行证据 |
| `IMPLEMENTATION_DEPTH_GAP` / `FAILURE_RECOVERY_GAP` | 补关键路径、状态、参数、失败、幂等、恢复和人工接管；必要时拆工程任务 |
| `MEASUREMENT_GAP` | Eval / Benchmark / 压测 / Bad Case；没有实际数据就保持 Not Proven |
| `FUNDAMENTAL_GAP` | 独立基础知识复习或岗位相关练习，不回写 Zuno 架构 |
| `COMMUNICATION_GAP` | 单独做表达训练；不能用润色关闭事实、实现或证据 Gap |
| `RESUME_CLAIM_RISK` | 立即缩小叙事并重新做 Forensic 追问 |

## 关闭条件

- 事实缺口：用户确认或直接项目证据建立来源；强重建候选本身不能关闭真实性 Gap；
- 证据缺口：补充可复现代码、测试、Trace、指标或引用；
- 架构缺口：更新唯一正式文档和必要 Contract，并通过对应验证；
- Project–Architecture Alignment：背景、用户任务、领域对象、Target 和 Current Claim 重新形成一致因果链，并经 A16 换问法复测；
- Build/Buy：有明确 Adopt/Extend/Build/Defer 决策、Delta、成本和替换边界；
- 过度设计：缩小范围、简化部署或明确 Defer，不以增加文档解释代替；
- 叙事风险：改成与事实一致的说法，并重新进行 Forensic 追问；
- 面试表达问题：30 秒 / 90 秒 / 3 分钟可以稳定表达，但不能用表达训练关闭架构或实现 Gap。

没有关闭证据时保持未关闭状态。
