# Development Evolution

本文件记录可恢复的历史过程。时间顺序不确定的内容明确标注，不把当前 Target 或仓库结构倒灌到历史。

## 已确认的时间与加入事实

| Claim | 状态 | 边界 |
|---|---|---|
| 用户约在 2026 年 3 月加入该产品研发 | `[USER_CONFIRMED]`（近似） | 这是用户加入时间，不是项目立项时间 |
| 2026 年期间项目持续推进 | `[USER_CONFIRMED]` | 不能推出正式结束时间或生产部署 |
| 该研发是长期持续型项目 | `[USER_CONFIRMED]` | 不等于持续提供生产 SLA |
| 用户加入时项目已经存在代码 | `[USER_CONFIRMED]` | 用户加入后 clone 了已有项目代码并参与开发 |
| 用户加入时已有简易自研前端页面 | `[USER_CONFIRMED]` | 页面具体功能和版本未知 |
| 加入后同时开发并学习 LangGraph / GraphRAG | `[USER_CONFIRMED]` | 学习不等于产品主链路已采用 |

项目最早立项时间、历史正式产品名第一次出现时间、第一次提交和第一次任务仍为 `[UNKNOWN]`。当前 GitHub 的创建时间不能代替横向项目立项时间。

## 已确认里程碑

| 里程碑 | 状态 | 说明 |
|---|---|---|
| 内部 Demo | `[USER_CONFIRMED]` | 存在，但具体时间和内容未知 |
| 面向智慧法院项目组/客户侧 Demo | `[USER_CONFIRMED]` | 存在，但具体展示路径未知 |
| 客户反馈回答质量需要继续提高 | `[USER_CONFIRMED]` | 这是重要反馈锚点；问题根因尚未确定 |
| 法院侧真实人员参与测试 | `[USER_CONFIRMED]` | 人员身份、数量和测试任务未知 |
| 试点验证 | `[USER_CONFIRMED]` | 只能说明阶段，不等于生产部署 |
| 正式生产部署 | `[USER_CONFIRMED]` | 尚未发生 |

## 保守时间线

下列顺序中，加入、已有代码/前端、客户反馈和未生产是明确事实；技术任务与各类 Demo 的精确相对顺序仍需恢复：

```text
约 2026-03 加入
  ↓
clone 已有代码，并开始参与 Agent 开发与 LangGraph / GraphRAG 学习
  ↓
参与 Memory / OpenViking 接入
  ↓
参与 Tool Calling Strategy
  ↓
内部 Demo / 客户 Demo（精确先后 UNKNOWN）
  ↓
客户反馈：回答质量需要进一步提高
  ↓
继续开发和优化
  ↓
法院侧人员测试与 Pilot Validation（精确先后 UNKNOWN）
  ↓
截至当前尚未正式生产部署
```

早期 Demo 是否展示检索过程目前只有 `[USER_PARTIAL_RECALL]`：用户隐约记得可能展示过检索，但具体页面、Trace、引用和呈现方式未知。

## 尚未恢复的开发过程

以下均为 `[UNKNOWN]`：第一条任务、第一次提交、第一次联调 endpoint、本地启动命令、代码 Review 方式、发布/回滚流程、客户反馈的具体根因，以及回答质量改进究竟归因于 Prompt、Retrieval、Rerank、Context、Memory、Tool、Citation 还是其他因素。

## 历史架构边界

Python-only Microservice Architecture、新服务边界、Domain Kernel、Domain-aware Runtime 和新 Multi-Agent 设计均为 `[TARGET_ONLY]`。不能用当前 Target 反推历史项目已经是微服务，也不能把当前仓库的逻辑包直接当作历史服务。

## 事实 Owner

本文件负责时间、加入、里程碑和反馈演进；交付状态进入 [`delivery-and-usage.md`](delivery-and-usage.md)，技术矩阵进入 [`technology-reality.md`](technology-reality.md)。
