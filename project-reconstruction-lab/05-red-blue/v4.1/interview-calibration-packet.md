# V4.1 Interview Calibration Packet

status: `WORKFLOW_CALIBRATION_INPUT`
audience: `RED_THREAD_ONLY`
answer_content_included: `NO`
candidate_script_included: `NO`

## 用途

本文件只把外部面试材料中的“提问行为”压缩成 Red Team 可使用的攻击方法。它不是 Zuno 的架构答案、候选人的面试话术、事实证明，也不是 Blue 的上下文。Main Thread 在每轮开始时复制并按本轮新证据更新一份会话级 packet；不得把整个 `interview-work` 目录注入 Red Context。

## 来源与权重

本基线 packet 于 2026-08-13 读取以下来源。路径是外部工作区，不属于 Zuno Canonical Truth；SHA 用于说明本次提炼所依据的文件版本。

| 权重 | 来源 | 读取范围 | SHA256 / 状态 |
|---|---|---|---|
| `REAL_SELF_INTERVIEW` | `F:\internship-work\interview\02_则知科技_Agent开发实习\01_面试_QA整理.md`、`01_面试_复盘.md` | 用户真实项目深挖与复盘 | `5A3EEB3C07D4CAF422C78DE0143E12EED53CE419D6DEF5B318E067B226D9749A` / `BF8A0CBE9BEFCC22718532661F0268998402F18EAE1E2B0FB663869F97909E86` |
| `REAL_SELF_INTERVIEW` | `F:\internship-work\interview\04_丰疆智能_架构培训生(AI工程师)\01_面试_QA整理.md`、`01_面试_复盘.md` | 用户真实项目深挖与复盘 | `3FB5FA8D341E67B0E92171952F66C45C919B4F8EA3F58C20AC6E8DBCD82951BA` / `2BC3E29788818C500FE37774F5CE4AB19BBD37C9843963CDBEDB04CBFFF7B87B` |
| `REAL_SELF_INTERVIEW` | `F:\internship-work\interview\05_杭州泛讯信息科技_AI应用工程师\01_面试_QA整理.md`、`01_面试_复盘.md` | 用户真实 Agent / Tool / Memory 深挖与复盘 | `A0FE64A53636029F0A13AF66C5FD12376FCE033368770ECE5B179932953BE46D` / `DD5C046878ED4EB6B81940001C8347D7DDDD755D1F17036145777A64D7D87E7C` |
| `REAL_SELF_INTERVIEW` | `F:\internship-work\interview\07_水滴集团_Agent应用工程师\01_面试_QA整理.md`、`01_面试_复盘.md` | 用户真实权限、Memory、检索与恢复深挖 | `86018F484D3F6A152A17A12B33FD60E624E08A9C0EE6BDA19E4400C34D4BF079` / `08464B5ADEB59328D61FF55857A35E03F208D164C9071BA3461F2C53E47279AF` |
| `HIGH_SIGNAL_PUBLIC_INTERVIEW` | `F:\internship-work\interview\00_面试文案仓库\red-team\01_面试官关注点与底层原则.md` | 取证、Why、反例、证据和停止条件 | `0A650611979F516245B727E57CCDBE6D0B6DA065C03129D1298A1C2705242A23` |
| `HIGH_SIGNAL_PUBLIC_INTERVIEW` | `...\02_攻击角度分类.md`、`03_面试官画像与提问风格.md`、`04_红蓝对抗工作流.md`、`06_来源审计.md` | 攻击角度、画像、复测和来源边界 | `FAB39BE98FD3B95B1E4D6CCFFB5CF4C102BD8394B0F912724A223B51A3643A47`、`3647758233DB6ACC1309A6CF4BDB49E747B3D161196E0330992FF258ACF0C099`、`589693496EF283486DC887068228EDFF95AF8FDF0C5E6516700C0E19D1FD8ABD`、`F28F85CA4BBB1AC5D2B2D909D99FCCB50F11CCD84A011914EC2AD539C54F8352` |
| `GENERAL_PUBLIC_INTERVIEW` | `F:\internship-work\interview\面经\` | 只作为方向补充，不按公司推断固定风格 | `READ_ONLY_DIRECTORY` |

若本轮要复现来源，应重新计算 SHA；本表不替代外部来源的完整 Artifact Ledger。

## 提炼出的 Red 行为

### 1. 以 Claim 为入口

先抓住一个架构 Claim，再沿着问题、必要性、设计理由、边界、Owner、失败、成本、替代方案和反转条件连续下钻。不要把 100 个随机关键词问题当作深度。

### 2. 使用 Deep-Dive Attack Chain

Round-006 以后默认生成 12–18 条 Chain，总题数仍恰好 100。每条 Chain 必须有：

- `chain_id`、`root_claim`、`question_ids`、`primary_concept`；
- 至少一个 `counterfactual`、`alternative`、`failure` 或 `reversal` 压力；
- 至少一个约束变化，例如成本减半、权限撤销、版本变化、Provider 不可用、任务取消、并发写入或副作用未知；
- `questioning_pattern_source`，只能描述提问方式来源，不是答案来源。

每条 Chain 通常包含 5–10 个真正相互触发的问题。前一问的设计概念应成为后一问的上下文，不得用同主题的同义句凑链。

### 3. 让问题像工程讨论

优先使用“为什么这里需要……？”、“如果换一种情况呢？”、“为什么不能只用……？”、“听起来它和……有什么区别？”、“今天重做还会这么选吗？”等自然追问。避免把问题写成 API 文档、合同清单或预先泄露答案的教学题。

### 4. 先拆名词，再谈术语

如果 Canonical Part A 写了 `Replan Barrier`、`DomainVersion` 或 `EffectReceipt`，Red 先问它在普通工程语言中实际解决什么问题。若 Blue 只能依赖 Zuno-specific 术语，记录 `CONCEPT_NOT_CLEAR` 或 `TERM_DEPENDENT`。

### 5. 强制替代、反事实和取舍

核心设计至少经历一次 `Why Not`：只用 Hybrid、PostgreSQL、一个 Agent、普通 DAG、WorkBuddy、现有 OSS 或 OpenViking 是否已经足够。再改变用户规模、成本、时延、权限、数据版本、Provider 健康度或任务可取消性，检查架构是否仍然闭合。复杂度没有相应收益或反转条件时，优先要求 `SIMPLIFY`、`EXTERNALIZE`、`DEFER` 或 `DELETE`。

### 6. 攻击 Ownership 与未知副作用

Red 追问“谁说了算”：谁接受 Evidence、谁让 Finding stale、谁激活 Plan、谁决定 Tool 可执行、谁使 Approval 失效、谁提交 Run 完成、谁允许 Memory 晋升。外部 Tool 已执行但响应丢失时，必须继续追问是否敢重试、如何知道结果、Provider 无查询接口时如何降级。

### 7. 人工评分维度

每条 Chain 额外记录 `INTERVIEW_DEPTH` 0–5，只衡量问题是否连续打穿必要性、边界、失败、替代、成本和反转，不进入 Architecture Defense Score。Red Judge 另记录 `INTERVIEW_EXPLAINABILITY: CLEAR | DENSE | TERM_DEPENDENT | MISSING`，判断 Fresh Blue 是否能仅凭 Part A 用 30–90 秒自然解释概念。

## 明确不注入的内容

- “更稳回答方向”、候选人的标准答案和项目包装话术；
- 任何由面经推导出的 Zuno 历史事实、Current 证据或个人贡献；
- Implementation Interviewer 的 class、method、SQL、字段和具体代码问题，除非本轮显式声明 `IMPLEMENTATION-FEEDBACK-ROUND`；
- 上一轮 Blue reasoning、完整聊天记录或未审核的面经结论。

Blue Thread 不读取本文件。Blue 只能从 Canonical Part A、必要 Facts、Active ADR、Governance 和自身通用架构知识完成 Cold-Start Defense；否则无法判断 Part A 是否真的可解释。
