# Phase 06：能力与工具检索

## 目标

引入可检索 ToolCard 层，减少一次性注入所有工具 schema 的做法。

## 范围

- ToolCard registry contract。
- Knowledge、Action Tool、MCP、Skill 的统一 capability metadata。
- capability selector 基于 task/context 做 keyword、permission、health、cost 过滤。
- GeneralAgent trace 记录 requested / selected / rejected capabilities。

## 不在范围内

- 新建 MCP server。
- 新增外部工具市场。
- 自动安装用户未授权工具。

## 退出标准

- Agent 可以按需选择 capability，而不是默认加载全部工具 schema。
- 工具选择结果进入 trace。
- 权限、健康状态和成本过滤有测试覆盖。

## 验证

- 聚焦 capability registry / selector 测试。
- 受影响 Agent runtime 测试。
- Agent/doc 边界验证。
