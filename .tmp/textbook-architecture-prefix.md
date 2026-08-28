# Zuno 总体 Target 架构

Zuno 的总体架构围绕一个问题展开：当法律工作从一次问答变成持续数十分钟甚至更久的专业任务时，系统怎样保证材料、分析、人工判断、正式成果和外部动作始终有清楚的来源与恢复依据。

简单问题不需要复杂架构。用户只想查询一条合同原文时，受控检索和一次模型生成通常已经足够。只有当同一事项包含多版材料、长期业务状态、人工复核、权限变化、系统崩溃或现实副作用时，Zuno 才逐步引入更强的领域和运行机制。架构复杂度来自这些具体约束，而不是来自框图本身。

本文描述 Target（目标架构）。对象、Contract（契约）和状态出现在文档中，不代表它们已经全部成为 Current（当前实现）；历史 Pilot 也不等于 Production。项目背景与真实经历见 [`docs/project/project.md`](../project/project.md)，Current 证据见 [`docs/evidence/`](../evidence/)，模块内部设计见 [`docs/modules/`](../modules/README.md)，历史架构审查见 [`docs/maintenance/history/red-blue/`](../maintenance/history/red-blue/README.md)。
