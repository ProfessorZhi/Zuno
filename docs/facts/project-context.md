# Zuno 项目上下文

status: `current-context`
owner: Project Context Owner

## 这是什么

Zuno 是智慧司法研发背景下形成的一个法律知识与 Agent 产品仓库。项目与南京大学软件学院葛季栋 / LIPLAB 的智慧司法研发背景有关，合作侧日常称为“智慧法院项目组”。Zuno 是该体系中的一个产品名称，不等于整个智慧法院项目。

当前仓库和项目资料共同表明，Zuno 关注法律材料、知识检索、Agent 工作流、Memory / Context、工具调用和可审计的结果交付。当前代码能证明相关工程表面存在；它不能单独证明历史客户环境、完整历史技术主链路或全部能力已经生产运行。

## 为什么这些背景今天仍然有效

这些背景决定了 Zuno 不是一个脱离业务的通用 Chat Demo：

- 结果需要面向法律或司法专业场景进行解释和复核；
- 知识检索、文档证据、Agent 执行和领域状态不能互相冒充；
- 真实交付关注回答质量、来源可追溯、权限和失败后的恢复；
- 当前 Target Architecture 因此强调 Domain Owner、Evidence、Security、Budget、Review、Idempotency 和 Eval。

最后一项是架构约束的背景解释，具体 Target Contract 以 [`../architecture/architecture.md`](../architecture/architecture.md) 和有效 ADR 为准。

## 已知边界

- 项目历史上经历过内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation；尚未建立正式 Production 证据。
- 用户约于 2026 年 3 月作为研究生工程参与者加入已有代码和简易前端的项目，参与 Agent、Memory、OpenViking Memory / Context 接入和 Tool Calling Strategy；详细历史归档见 [`../history/team-and-ownership-history.md`](../history/team-and-ownership-history.md)。
- 具体合同主体、正式产品名、直接客户、试点法院、历史完整技术栈和生产规模仍是 `UNKNOWN`。

## 不应从本文件推出的内容

公开研究背景不等于 Zuno 已实现对应论文算法；当前仓库的目录、依赖、Compose、类名或 Target 文档也不等于历史客户部署或 Production Readiness。历史开发过程见 [`../history/`](../history/README.md)，当前实现状态见 [`current-state.md`](current-state.md)。
