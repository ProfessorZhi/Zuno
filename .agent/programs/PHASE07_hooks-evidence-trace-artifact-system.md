# PHASE07 Hooks Evidence Trace Artifact System

Program: `zuno-eight-deliverables-full-realization-v1`
status: planned

## 为什么

增强模式必须能回答“做了什么、为什么这么做、证据够不够、哪里 fallback、产物怎么复现”。Hooks、Evidence、Trace 和 Artifact 是把 Agent 行为从黑箱变成可审计系统的关键。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- pre-retrieval / post-retrieval / pre-tool / post-tool / post-answer hooks。
- Evidence Check、Citation Coverage、fallback reason。
- Trace event schema 和 artifact manifest。

## 执行步骤

1. 审计现有 observability、trace、citation、evidence 入口。
2. 定义事件 schema 和 artifact manifest。
3. 实现 hooks policy 与 runtime event emission 的 focused path。
4. 将 evidence coverage 与 citation check 接入 enhanced mode。
5. 增加 focused tests 和一份可复现 evidence report。

## 验收

- 每次增强路径能产生可读 trace。
- evidence check 不通过时有 fallback 或低置信说明。
- artifact manifest 能关联输入、检索、工具、证据和输出。
- docs/evals 能解释 trace 字段。

## PR 边界

建议拆成 schema PR、runtime hooks PR、evidence/artifact PR。
