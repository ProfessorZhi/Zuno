# Project Background

## 当前事实状态

| Claim | 状态 | 说明 |
|---|---|---|
| Zuno 在基线仓库中维护过 11 个逻辑模块 | `[REPO_EVIDENCE]` | 见 [`../modules/`](../modules/README.md)；这是上一阶段文档结构，不证明新 Target 永久保留该拆分 |
| 项目最初由什么真实需求启动 | `[UNKNOWN]` | 需要历史材料、用户确认或直接项目证据 |
| 历史客户的日常称谓 | `[USER_CONFIRMED]` | 用户记得项目侧称为“智慧法院项目组”；正式机构、合同主体和业务决策人仍未知 |
| 真实用户和业务决策人 | `[UNKNOWN]` | 不得从学校、导师或法院线索自动推出 |
| 原工作流、痛点和为什么值得做 | `[UNKNOWN]` | 需要建立 As-Is Workflow、Pain 和人工基线 |
| 合作方、学校、导师或法院与 Zuno 的直接关系 | `[UNKNOWN]` | 公开背景只能形成周边 Context |
| 企业法律 / 合同审查是否是历史原始场景 | `[UNKNOWN]` | 需要与原始项目材料和用户记忆核对 |
| 当前 Legal Agent Platform 定位 | `[TARGET_ACCEPTED]` 或 `[BLUE_PROPOSAL]` | 以正式 Architecture 的当前状态为准，不反推历史 |

## 用户确认的最小历史事实

以下事实由本轮 User Gate 明确确认，只用于限制历史叙事，不代表客户、上线或商业结果已经被证明：

| Claim | 状态 | 边界 |
|---|---|---|
| 用户是南京大学软件学院葛季栋老师的学生 | `[USER_CONFIRMED]` | 只证明师生关系，不证明具体项目客户或部署方 |
| 用户在研究生阶段参与过葛季栋老师侧组织的一个横向项目 | `[USER_CONFIRMED]` | 只证明参与过横向项目，不证明项目就是 Zuno 当前 Target、天津智慧法院或合同审查 |
| 项目侧客户称谓为“智慧法院项目组” | `[USER_CONFIRMED]` | 这是用户记忆中的日常称谓，不等于正式机构名称或合同甲方 |
| Zuno 是该项目组中的一个产品/产品线 | `[USER_CONFIRMED]` | 不等于 Zuno 覆盖整个智慧法院项目 |
| 覆盖天津 22 家法院体系中的部分法院 | `[USER_CONFIRMED]` | 用户记忆认为是其中一部分；具体法院清单和公开 22 家系统的直接关联仍未知 |
| 历史项目的正式名称、合同主体和原始需求 | `[UNKNOWN]` | 继续等待原始材料、项目记录或用户进一步确认 |
| Zuno 与公开天津智慧法院系统的直接项目关系 | `[UNKNOWN]` | 公开资料只能证明周边背景，不能单独证明该产品的合同或交付关系 |

因此，合同审查可以继续作为 Zuno 的 Target 旗舰场景，但不能反向写成历史项目起点。公开的导师、实验室、智慧司法或法律 NLP 背景只能作为 `PUBLIC_CONTEXT`，不能升级为本项目客户、用户或采购事实。

## 公开背景校准

下列资料可以证明周边背景，但不能替代 Zuno 的项目材料：

- 南京大学软件学院公开介绍称，学院主持完成天津智慧法院大型软件系统研发，服务天津市辖区高级、中级、基层等 22 家法院：[`南京大学软件学院`](https://software.nju.edu.cn/xygk/index.html)。
- LIPLAB 公开介绍称，研究组长期参与天津法院信息化建设，负责部分信息系统研发，特别涉及智能司法判决辅助技术成果落地：[`LIPLAB 介绍`](https://software.nju.edu.cn/szll/yjsds/index.html)。
- 最高人民法院公开报道记载，天津市高级人民法院召开全市法院智慧法院建设推动会，天津法院信息化 3.0 在全市法院应用：[`最高人民法院报道`](https://www.court.gov.cn/zixun/xiangqing/74412.html)。

以上属于 `PUBLIC_CONTEXT / R1_PUBLIC_CONTEXT`。它们支持“智慧法院项目组”这一历史背景的合理性，但不支持“Zuno 的直接合同客户是天津市高级人民法院”这一更强主张。

## 背景重建规则

```text
Repo / Git History / Status / Evidence
  → 用户真实面试、历史简历和原始材料
  → 必要公开背景
  → 2–3 个候选解释
  → 用户确认或保持 UNKNOWN
```

可提出研究候选，但不得编造客户、法院采购、上线用户、收入、用户数量或项目需求来源。项目定位只有在“用户—任务—As-Is Workflow—Pain—Required Capability”因果链成立后，才能进入 Product / Domain Target。

## 事实 Owner

本文件负责项目起点、背景、用户、痛点和产品立意的历史事实；稳定 Target 产品问题进入 [`../architecture/`](../architecture/README.md)，红蓝候选和攻击记录进入 [`../../../project-red-blue/`](../../../project-red-blue/README.md)。
