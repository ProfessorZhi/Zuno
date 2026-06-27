# 模板

这里存放 skill 执行模板和报告骨架。模板只回答“输出成什么样”，不沉淀项目知识；项目知识和可复用经验放 `.agent/references/`。

## 当前模板

这里放开发 Agent 常用模板，例如：

- 架构评审模板
- 重构任务拆解模板
- 验收检查清单
- 目标模式提示词
- Debug 记录模板

正式面向团队的模板，仍应迁移到仓库正式文档区。

## 边界

- `references/`：本地项目 skills、lessons、playbooks。
- `templates/`：执行提示、phase 计划、closure report、审计报告等固定格式。
- `programs/`：当前 phase 执行计划。

新增模板必须能被 `.agent/system.yaml` 或 phase 文件引用。
