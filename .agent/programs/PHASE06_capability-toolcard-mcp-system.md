# PHASE06 Capability ToolCard MCP System

Program: `zuno-eight-deliverables-full-realization-v1`
status: planned

## 为什么

工具层如果只是一堆函数注册，Agent 无法解释为什么选择某个工具、是否允许调用、成本如何、失败如何回退。ToolCard 和检索式 capability selection 是 Agentic RAG 的动作边界。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- ToolCard registry。
- Native BM25 capability/tool search。
- MCP adapters 和 tool policy。
- 权限、成本、health、fallback trace。

## 执行步骤

1. 审计 `src/backend/zuno/capability` 和 MCP server 目录。
2. 固定 ToolCard schema：name、description、input contract、owner、permissions、cost、health、evidence。
3. 实现 capability retrieval / selector / policy 的 focused path。
4. 将 tool selection result 写入 trace。
5. 增加 tests，证明工具选择可解释、权限可拦截、旧入口兼容。

## 验收

- ToolCard 不只是文档，有代码 contract 和测试。
- Native BM25 search 能返回可解释候选。
- MCP / local tools 共享 policy 和 trace 边界。
- 旧 public import path 继续通过 compatibility 保护。

## PR 边界

建议拆成 ToolCard contract PR、selector/search PR、MCP policy/trace PR。
