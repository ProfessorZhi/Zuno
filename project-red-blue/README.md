# Zuno Project Red-Blue Lab

## 这是什么

`project-red-blue/` 是 Zuno 的项目级红蓝对抗实验区。它不是新的架构事实源，也不是把面试题堆在一起的题库，而是用来攻击并修复项目叙事、落地可信度、团队协作、技术取舍、架构边界和实施可行性的工作流。

- **红队（Red Team）**：像大厂面试官、架构评审人、开源方案质疑者、投资人或业务负责人一样，从最新陈述和正式文档出发连续追问。
- **蓝队（Blue Team）**：基于事实回应；用户记忆不完整时先做证据搜索和候选重建；对目标态、方案和修复路径给出明确标注的提案。
- **裁判（Referee）**：区分已确认事实、仓库证据、公开背景、目标设计、蓝队提案和未知状态，决定哪些事实需要用户确认、哪些 Target 设计可以进入正式架构评审。

红蓝队的目标不是证明 Zuno “什么都有”，而是找出以下问题：

1. 项目为什么存在，真实用户和痛点是什么；
2. 当前团队是否真的能维护所声称的复杂度；
3. 逻辑模块、部署服务、团队职责和个人贡献是否被混为一谈；
4. 每个技术选择是否有替代方案、成本边界和失败处理；
5. 项目背景、领域模型和目标架构是否属于同一条因果链；
6. 哪些能力必须由 Zuno 拥有，哪些应该 Adopt / Extend / Replace / Defer；
7. 哪些内容是 Current，哪些只是 Target、Proposal、Reconstruction 或 Unknown。

## 输入优先级

项目红蓝队不是封闭题库。每轮开始前先刷新输入，优先级如下：

```text
REAL_SELF_INTERVIEW
    用户自己的真实面试原始记录 / QA / 复盘，最高权重。

PROJECT_REPO_EVIDENCE
    Zuno 最新 main 的代码、测试、Migration、Trace、Eval、Status 和正式架构。

TARGET_ROLE_JD
    目标岗位真实 JD，决定本轮必须覆盖的能力面。

HIGH_SIGNAL_PUBLIC_INTERVIEW
    真实公开面经，用于学习追问行为，不用于证明 Zuno 事实。

PUBLIC_CONTEXT
    学校、教师、法院、开源项目、竞品等可核验公开资料，只证明其自身事实；除非存在直接项目链接，不能自动升级成 Zuno 历史事实。
```

当前面试模式研究入口来自 `ProfessorZhi/internship-work` 的 `interview/00_面试文案仓库/red-team/`。最新刷新快照见 `sources/interview-patterns.md`：`internship-work` 为 `1831f7be`，面经子仓库为 `b623c99`，当前总览为 1,770 条记录；旧的 300 份内容级深读仍只代表旧样本基线，不代表新增记录已经深读。每次用户提示面经有更新时，先读取最新 `main`、面经子仓库指针、总览和来源审计，不得沿用未核验的旧计数。

## 来源和状态标签

正式架构事实仍以 `docs/` 为准，项目红蓝材料不覆盖它们。项目陈述使用以下状态标签：

| 标签 | 含义 |
|---|---|
| `[USER_CONFIRMED]` | 用户明确提供或确认的真实事实 |
| `[REPO_EVIDENCE]` | 能在仓库代码、测试、文档或证据中复核的事实 |
| `[TARGET_ACCEPTED]` | 已确认的目标架构或目标规则 |
| `[BLUE_PROPOSAL]` | Agent 提出的方案、叙事、重建候选或假设，尚未成为历史事实 |
| `[UNKNOWN]` | 当前不能从证据推出，必须保留未知 |

状态和“重建置信度”分开维护。公开资料可以高置信地证明“南京大学软件学院长期参与某类司法信息化工作”，但它不能单独证明“Zuno 就是该公开项目的直接延续”。详细规则见 `01-project-facts.md`。

## 标准工作闭环

```text
0. EVIDENCE REFRESH
   读取最新 Zuno main、个人真实面试、目标 JD、更新后的面经研究与必要公开资料
        ↓
1. RECONSTRUCTION
   先由蓝队搜索证据并提出 A/B/C 候选，只把真正无法恢复的现实事实交给用户确认
        ↓
2. PROJECT MODEL + CLAIM INVENTORY
   建立背景、用户、问题、团队、架构、取舍、交付、落地和证据模型
        ↓
3. RED ATTACK
   从高风险 Claim 开始，连续攻击真实性、Ownership、架构、开源替代、实现和证据
        ↓
4. GAP ROUTING
   区分背景、叙事、架构、Build/Buy、实现、证据、测量、安全或简历风险
        ↓
5. BLUE REPAIR
   可以缩 Scope、重建项目故事、采用现成方案或重新设计 Target；不得为了保住旧架构而强行辩护
        ↓
6. CANONICAL SYNC
   只有确认后的事实或 Target 设计进入正确的 docs / ADR / status / evidence Owner
        ↓
7. RED RETEST
   换一种问法再次攻击；没有关闭证据就保持 OPEN
        ↓
8. SKILL EXTRACTION
   多次真实运行稳定后再提炼正式 Skill，不以一版规则直接冻结自动化行为
```

## 三类修复必须分开

```text
Story Repair
    恢复项目背景、用户、团队、时间线和个人贡献；事实不够时只生成候选。

Architecture Repair
    红队证明 Target 的边界、领域模型、Owner、状态或故障语义不成立时，重新设计正式架构。

Implementation / Evidence Repair
    Target 合理但 Current 没有实现、测试、Trace、Eval 或运行证据时，交给工程任务，不用修改叙事伪装完成。
```

红队可以证明原架构是错的。蓝队没有义务“守住原方案”；真正的目标是让项目事实、产品定位、Target Architecture 和 Current Evidence 相互一致。

## 文件地图

| 文件 | 职责 |
|---|---|
| `00-charter.md` | Red Team Thinking Kernel、红队风险模型、Claim 取证漏斗、动态追问和红蓝边界 |
| `01-project-facts.md` | 项目事实、重建置信度和 Claim 清单 |
| `02-project-model.md` | 背景、用户、问题、团队、架构、落地、证据及跨层 Alignment Gate |
| `03-team-ownership.md` | 真实团队职责与目标 Ownership 的分离 |
| `04-attack-taxonomy.md` | 问题域、攻击角度和连续追问链 |
| `05-interviewer-personas.md` | 红队面试官/评审人角色 |
| `06-red-team-protocol.md` | 红队读取、攻击、记录和报告流程 |
| `07-blue-team-protocol.md` | 蓝队重建、回应、提案、修复和同步流程 |
| `08-gap-register.md` | 缺口分类、生命周期、优先级和关闭条件 |
| `09-open-source-review.md` | Adopt / Extend / Build / Defer 评估协议 |
| `10-delivery-evolution.md` | 从最小落地到生产治理的演进假设 |
| `workflows/` | 三套可组合工作流：Red Interview、Blue Answer、Red-Blue Optimization |
| `sources/` | 外部面经模式和仓库证据入口，不拥有 Zuno 新事实 |
| `sessions/` | 可审计的公开 Session 记录和 TEMPLATE，不保存隐藏思维链 |
| `tools/scripts/verify_red_blue_session.py` | Campaign Session 的 YAML/Markdown 一致性验证器；不运行红队或修改正式架构 |
| `skill/` | 两个 Future Skill Design Spec；多次实跑前不生成 `SKILL.md` |

`00-charter.md` 是红队的唯一底层思维框架。`04` 提供攻击工具，`05` 提供面试官视角，`06` 规定会话运行方式，`sources/` 负责用真实面经校准问法；这些文件不能反过来各自维护一套互相冲突的红队决策逻辑。

## Kernel 冻结后的 Architecture Loop

`Red Team Thinking Kernel v1` 冻结后，主工作转入架构红蓝循环，不再无限扩张红队制度：

```text
Project / Domain Alignment
  → Product / Domain Fit Analysis
  → Knowledge / Evidence Fit Analysis
  → Agent / Multi-Agent Runtime Fit Analysis
  → Service / Data Ownership Fit Analysis
  → Tool / Capability / Security
  → Deployment / Eval
  → Cross-service Architecture Review
```

每个 Canonical Question 专题统一执行：

```text
Read Current + Target + Evidence + OSS Candidate
  → Red Attack
  → Gap Report
  → Blue Review
  → KEEP / SIMPLIFY / ADOPT / EXTEND / BUILD / DEFER / DELETE
  → Architecture Change Set
  → User Architecture Gate
  → Canonical Docs Update
  → Red Retest
```

蓝队可以推翻旧 Target；未经过用户架构确认，不把红蓝提案写入正式 `docs/project/architecture/` 或 `docs/project/modules/`。

## 第一次真正运行时怎么问用户

不要先把十个 P0 问题逐项丢给用户。先由蓝队读仓库、历史面试和可核验外部资料，输出：

```text
已直接确认的事实
仓库可证明的事实
公开背景但尚未与 Zuno 建立直接链接的事实
2–3 个最可能的背景 / 团队 / 交付候选模型
仍然会改变项目真实性的关键 Unknown
```

只有最后一类才问用户，并尽量使用 A/B/C、区间或“更接近哪个候选”的低负担确认方式。用户回答“记不清”是允许状态，不得强迫其为项目补造细节。
