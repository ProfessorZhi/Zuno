# Project Facts

本目录是 Zuno 项目历史事实的正式入口，回答：**What actually happened?**

## Current GitHub 与完整历史的边界

```text
Current GitHub Repository
≠
Complete Historical Project Repository
```

当前仓库只能作为 `PARTIAL_REPOSITORY_EVIDENCE`：它可以证明某个阶段存在的代码、配置、测试、Migration 或设计表面，但不能自动证明原横向项目从一开始就使用这些内容，也不能证明用户本人负责、客户环境部署、历史 Demo 使用或历史技术栈完全一致。

## Canonical 文件

| 文件 | Canonical Question |
|---|---|
| [`project-background.md`](project-background.md) | 项目来自什么背景，客户和产品关系是什么？ |
| [`team-and-ownership.md`](team-and-ownership.md) | 谁参与，用户本人实际做了什么？ |
| [`development-evolution.md`](development-evolution.md) | 项目怎样开始、开发、演进和获得反馈？ |
| [`delivery-and-usage.md`](delivery-and-usage.md) | Demo、测试、试点和生产状态是什么？ |
| [`technology-reality.md`](technology-reality.md) | 哪些技术历史上真正使用，哪些只是当前仓库或 Target？ |

候选重建、攻击和下一轮回忆问题维护在 [`project-red-blue/01-project-facts.md`](../../../project-red-blue/01-project-facts.md)，不替代本目录的 Canonical Fact。

## 统一事实标签

- `[USER_CONFIRMED]`：用户明确确认的事实。
- `[USER_PARTIAL_RECALL]`：用户记得大致发生过，但细节仍模糊。
- `[PARTIAL_REPOSITORY_EVIDENCE]`：当前或历史 Git/代码/配置/测试/Migration 的部分支持，不代表完整历史。
- `[ARTIFACT_EVIDENCE]`：简历、旧截图、PPT、聊天、任务记录或旧文档直接支持。
- `[PUBLIC_CONTEXT]`：学校、实验室、法院或公开项目资料支持的外围背景。
- `[RECONSTRUCTED_CANDIDATE]`：多个线索形成的候选解释，尚未最终确认。
- `[UNKNOWN]`：目前无法恢复。
- `[TARGET_ONLY]`：当前重新设计的目标，不是历史事实。
- `[CONTRADICTED]`：证据之间存在冲突，等待裁判。

事实标签与 Current/Target/Future/History 是两条不同维度：用户确认“参与过 OpenViking Memory 接入”不等于证明当前仓库仍使用它，也不等于生产部署已经完成。

## 事实规则

- 当前 Target Architecture 不能证明历史实现、上线、用户量、团队分工或个人贡献。
- 公开背景只能证明公开背景自身；不能自动推出 Zuno 的合同甲方、具体法院或采购关系。
- 当前 GitHub 的依赖、目录、Docker 服务和类名不能单独证明历史产品使用。
- 团队工作、个人工作、框架提供和外部团队工作必须分开记录。
- 无法恢复时保留 `UNKNOWN`，不为了完整叙事创造产品名、法院名单、用户量、指标或 SLA。
- 只有事实证据进入本目录；`RECONSTRUCTED_CANDIDATE` 主要留在红蓝工作区。

## 事实 Owner

本目录负责历史事实摘要；可复现代码、测试、Trace、Eval 和当前运行证据进入 [`../../evidence/`](../../evidence/README.md)，生产状态进入 [`../../status/production-readiness.md`](../../status/production-readiness.md)，新架构进入 [`../architecture/`](../architecture/README.md) 和专题目录。
