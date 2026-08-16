# 项目事实来源说明

本文是 Zuno **项目事实层的来源登记和表述边界**。`docs/project/` 负责用自然语言讲项目为什么存在、怎样发展和怎样定位；本文回答更严格的问题：某句话从哪里来、今天能说到什么程度、哪些说法会越过证据，以及以后拿到什么材料才能把一个 Unknown 升级成可确认事实。

它不是另一份项目故事，也不拥有 Target Architecture。当前代码、Migration、Test、Trace、Eval 和运行结果仍由 `docs/evidence/` 证明；架构设计由 `docs/architecture/` 和 `docs/modules/` 拥有。

## 1. 五类信息必须分开

### 已确认历史事实

来自用户明确回忆、仍可核对项目材料或双方一致确认的历史事实。可以进入 `docs/project/` 正文，但仍要保留适当范围。例如“项目经历过 Pilot Validation”不等于“项目已经正式生产上线”。

### 公开背景佐证

来自学校、实验室、论文、专利或其他公开材料，只能说明研究和合作背景。公开论文证明团队做过某项研究，不自动证明历史 Zuno 某个版本已经接入该论文模型。

### 当前工程证据

来自今天 `main` 的代码、Migration、测试、Trace、Eval 和真实运行证据。这些材料只能证明 **Current**，不能自动解释历史上 Pilot 用了什么版本、谁写了哪段代码。

### Target / 产品价值假设

来自已经接受的总体架构、模块设计和 ADR。例如“复杂法律工作需要长期材料版本、正式证据和失效传播”是当前产品 / 架构判断；它可以解释今天为什么这样设计，但不能冒充“历史客户当时明确提出了这句话”。

### Unknown / 未恢复

缺少可靠材料时直接保留未知。不能用行业常识、现在的代码、论文或 Target 设计把历史空白补完整。

## 2. 项目事实台账

| ID | 主题 | 来源状态 | 当前可以采用的表述 | 明确不能扩大成 | 未来可升级证据 |
| --- | --- | --- | --- | --- | --- |
| PF-001 | 项目主体 | USER_CONFIRMED | Zuno 是南京大学软件学院 LIPLAB 智慧司法研究与工程化背景下的法律智能 Agent 平台 | 南京大学或 LIPLAB 的全部智慧法院项目都叫 Zuno | 历史产品说明、立项书、需求文档 |
| PF-002 | 天津法院背景 | USER_CONFIRMED + PUBLIC_CORROBORATED | 项目与天津法院智慧平台相关场景存在合作背景 | 已恢复直接合同甲方、合同金额、完整部署拓扑 | 合同、项目编号、招投标 / 验收材料 |
| PF-003 | 研究成果工程化 | USER_CONFIRMED + PUBLIC_RESEARCH_CONTEXT | 项目有意将团队长期智慧司法研究成果继续工程化、产品化 | 每篇论文、专利、算法都已经进入同一个 Zuno 版本 | Capability 映射、版本记录、历史代码 / 演示材料 |
| PF-004 | 原始产品方向 | USER_CONFIRMED | 立项方向包含法律智能平台、多专业 Agent 和可组合专业能力 | 历史每个版本都已经拥有完整 Agent Catalog / Studio / 协作 Runtime | 早期产品方案、需求原文、演示文档 |
| PF-005 | 22 家法院体系 | USER_CONFIRMED | 产品涉及 22 家法院体系中的部分法院 | 全部 22 家均正式部署、日常使用或验收 | 法院名单、环境清单、Pilot / 验收记录 |
| PF-006 | 核心研发规模 | USER_PARTIAL_RECALL | 可恢复的核心研发规模约 7–8 人 | 完整组织图、正式职位和每个模块 Owner 已确认 | 人员名单、项目通讯录、任务 / PR 记录 |
| PF-007 | 用户加入时间 | USER_CONFIRMED | 用户约 2026 年 3 月加入项目 | 从立项开始就是项目 Owner | 历史任务 / 入组记录 |
| PF-008 | 加入时已有产品 | USER_CONFIRMED | 用户加入时项目已经有代码和一个比较简单的自研前端 | 用户从零完成产品立项和第一版系统 | 历史仓库、截图、早期 Release / Demo |
| PF-009 | 用户参与 Agent | USER_CONFIRMED | 用户参与过部分 Agent 开发 | 完整 Agent Runtime / 全部 Agent 由用户独立实现 | 任务、PR、Commit、代码 Review |
| PF-010 | 用户参与 Memory | USER_CONFIRMED | 用户参与过 Memory 相关第一批重要工作 | 用户拥有整个 Memory 架构 / 所有长期记忆实现 | 任务级提交、设计记录、测试 |
| PF-011 | OpenViking | USER_CONFIRMED | 用户参与 OpenViking 在 Memory / Context 区域的接入 | 已恢复具体 SDK / Adapter / 数据结构和生产使用方式 | 代码提交、配置、运行记录 |
| PF-012 | Tool Calling Strategy | USER_CONFIRMED | 用户参与过 Tool Calling Strategy 相关开发 | 用户拥有全部 Tool Runtime / 外部副作用体系 | 任务、PR、故障测试、调用记录 |
| PF-013 | 数据库参与 | USER_CONFIRMED | 用户进入数据库查看或调试过数据 | 用户负责数据库总体设计、Schema 或 Migration Owner | SQL / Issue / Migration / Review 记录 |
| PF-014 | LangGraph / GraphRAG | USER_CONFIRMED_AS_LEARNING_CONTEXT | 开发期间学习和接触过 LangGraph、GraphRAG | 用户完整实现当前 Target Runtime 或 GraphRAG | 任务级实现证据 |
| PF-015 | Internal Demo | USER_CONFIRMED | 项目经历过内部 Demo | 已恢复正式验收或性能结果 | Demo 材料、日期、参与人、环境 |
| PF-016 | 客户侧 Demo | USER_CONFIRMED | 项目进行过客户侧或智慧法院项目组 Demo | 已恢复完整客户名单和正式验收结论 | 会议纪要、反馈单、演示材料 |
| PF-017 | 回答质量反馈 | USER_CONFIRMED | 客户曾反馈回答质量还需要提高 | 已知根因一定是 RAG / Prompt / Memory / Model 中某一项 | Bad Case、Issue、调试记录、前后指标 |
| PF-018 | Court-side Testing | USER_CONFIRMED | 项目进入过法院侧人员测试 | 已恢复测试规模、题集、参考答案和 Reviewer 协议 | 测试题、记录、评价表 |
| PF-019 | Pilot Validation | USER_CONFIRMED | 项目进入过 Pilot Validation | 正式 Production、SLA 或全面法院部署 | Pilot 环境、用户、时长、验收材料 |
| PF-020 | Production | NO EVIDENCE / NOT ESTABLISHED | 当前不能把历史项目描述成正式生产系统 | “已经生产上线”“稳定服务多少用户” | 生产 Endpoint、部署证明、SLA、运维 / 监控、正式验收 |
| PF-021 | 历史技术栈 | PARTIAL / NOT_RECOVERED | 只能逐项说已经确认参与或当前代码存在的技术 | 直接把今天依赖列表写成当时 Pilot 技术栈 | 历史 requirements / lock、部署文件、提交、截图 |
| PF-022 | 历史性能指标 | UNKNOWN | QPS、Latency、Token、Cost、HA、DR 等目前未恢复 | 根据今天测试或本机运行反推历史 Pilot 指标 | Benchmark、监控、压测、法院侧运行记录 |
| PF-023 | 当前总体架构 | TARGET / ACCEPTED | Round 02 已冻结九个 Target 逻辑责任域和跨模块 Owner | 历史 Pilot 当时已经按今天九模块实现 | `docs/architecture/`、ADR、模块设计 |
| PF-024 | 通用平台差异化 | TARGET / PRODUCT_HYPOTHESIS | Zuno 目标上拥有法律领域状态、证据 / 版本、正式准入、失效、Effect Recovery 和法律 Eval 等专业后端语义 | 已经通过正式实验全面优于 Dify / Coze / 其他通用平台 | A/B/C benchmark、真实案例质量 / 成本 / 恢复数据 |
| PF-025 | Native Runtime 必要性 | TARGET / MEASUREMENT_GATED | 复杂任务可以使用 Zuno 原生 Runtime；简单问答可留在通用宿主 | 自研 Runtime 已证明对所有任务更好 | Generic Host vs Legal Backend vs Native Runtime 对照 |
| PF-026 | GraphRAG / Memory / Multi-Agent | TARGET_OPTIONAL / MEASUREMENT_GATED | 这些复杂能力按任务和测量决定是否启用 | 已证明必须默认开启 | 消融实验、query-class benchmark、长期运行数据 |
| PF-027 | Current 工程实现 | CURRENT_EVIDENCE_ONLY | 当前仓库存在有限 Runtime、Knowledge、Tool、Model、Security、Observability 等实现 / 测试基础 | 模块文档写得完整就等于全部实现 | `docs/evidence/`、代码、Migration、Test、Trace / Eval |
| PF-028 | 当前质量 / Production Readiness | NOT_ESTABLISHED | 正式 benchmark / 生产资格尚未建立 | “架构完整所以 production ready” | 正式 runtime、credentials、数据集、load / DR / security qualification |

## 3. 产品定位中的“优势”怎样说才不越界

当前文档可以明确说明 Zuno **设计上多解决了什么问题**，例如法律领域状态、材料版本和知识就绪、正式准入、历史引用、失效传播、外部效果恢复、Research-to-Capability 和法律质量评测。

但在正式对照数据不存在时，不应说：

- “Zuno 比通用平台准确率高”；
- “Zuno 一定比 Dify / Coze 更适合法院”；
- “GraphRAG 明显提升了效果”；
- “Multi-Agent 明显优于单 Agent”；
- “自研 Runtime 已经证明比通用 Host 更稳定”；
- “Pilot 说明系统已经可以生产使用”。

更准确的表述是：

> Zuno 的差异化设计把通用宿主通常需要项目自行补充的法律业务语义，提升为一等架构责任；这些差异是否形成实际质量、恢复性和成本优势，仍要通过正式 A/B、故障测试和真实任务测量证明。

这也是 [`docs/project/product-positioning-and-value.md`](../project/product-positioning-and-value.md) 使用的统一口径。

## 4. 历史、Current 和 Target 冲突时怎么处理

如果历史回忆说“当时用了某项技术”，而当前仓库已经改成别的实现，两者可以同时成立：一个是 History，一个是 Current。不要为了统一文档把其中一个删掉。

如果 Target Architecture 描述了一个历史材料没有证明的对象，例如 `AdmissionReceipt`、`KnowledgeGeneration` 或九模块责任域，也不构成历史冲突；它只说明今天的目标设计已经进一步明确。

真正需要处理的是**同一时间层的互斥事实**。例如两个当前文档同时声称不同模块拥有同一个 Authoritative Fact，就属于 Architecture Gap；两个历史来源对同一时间点给出相反结论，则属于 Fact Gap，需要更多材料而不是选一个听起来合理的版本。

## 5. 一个事实怎样从 Unknown 升级

优先证据顺序：

```text
原始项目材料 / 合同 / 需求 / 验收
→ 历史代码 / Commit / PR / Issue / 测试 / 配置
→ 会议纪要 / Demo 材料 / 截图 / 运行记录
→ 用户明确回忆
→ 公开背景资料
→ 合理推断（只能作为 inference，不能升级成事实）
```

不同问题的最佳证据不同。个人贡献优先找任务、PR、Commit 和 Review；Pilot 优先找环境、参与人、运行记录和验收；质量优化优先找 Bad Case、Cause → Fix → Metric；历史技术栈优先找依赖锁、部署文件和提交。

## 6. Reviewer / Agent 使用规则

1. 讲项目故事时优先读 `docs/project/`，不要把本台账直接念给用户。
2. 需要判断一句历史表述能否采用时，再回到本表检查允许范围。
3. 讨论“为什么这样设计”时进入 `docs/architecture/` 和 `docs/modules/`，不要把 Target 说成历史客户原话。
4. 讨论“现在实现了吗”时进入 `docs/evidence/`，不要用项目回忆或设计文档证明 Current。
5. 遇到 Unknown 时直接保留 Unknown，并记录下一步最有价值的取证材料。
6. 新证据到来后，优先更新对应事实行和项目正文，再同步入口 / Validator；不要在多个位置分别维护互相独立的版本。

## 7. 当前最值得继续恢复的事实

如果以后还要提高技术面试和项目复盘的可信度，最有价值的不是继续增加架构名词，而是恢复几条真正的 **Cause → Decision → Implementation → Metric** 链：

- 客户说“回答质量需要提高”以后，到底抽取了哪些 Bad Case，根因是什么，改了什么，指标怎样变化；
- 用户实际参与的一项 Agent / Memory / OpenViking / Tool Calling 任务，从需求、代码、故障到验证的完整链路；
- Court-side Testing / Pilot 到底有多少题、多少用户、什么环境、怎样验收；
- 历史 Knowledge / RAG 的真实技术栈、数据规模和检索策略；
- 一次真实故障或性能问题怎样定位、修复和验证；
- 一个研究成果究竟怎样进入 Zuno 的某个历史产品版本。

这些材料一旦恢复，应该优先进入 Project / Evidence，而不是继续美化 Target Architecture。
