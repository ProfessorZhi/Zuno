# PHASE04 从架构图反推执行计划

status: pending

## 目标

根据细化架构图，生成后续产品化执行顺序：文档解析、企业知识库场景、安全闸门、LangSmith eval、前端 trace / artifact 闭环。

## 范围

只写计划，不实施功能。

## 需要修改的文件

- `.agent/programs/implementation-roadmap.md`
- `docs/architecture/roadmap.md`
- `README.md`

## 禁止修改的文件

- `src/backend/zuno/**`
- `apps/web/**`
- DB schema 或依赖版本。

## 验收闸门

- 执行顺序明确写成 `architecture detail -> Document Ingestion -> Enterprise Knowledge Base -> Security -> LangSmith eval -> frontend trace/artifact product loop`。
- README 只给精简入口，不堆完整执行细节。
- roadmap 明确当前 program active，且不把后续实现写成 Current。

## 验证命令

```powershell
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_docs_entrypoints.py
```

## 需要返回的证据

- program roadmap summary
- formal roadmap active state

## 历史影响

本阶段不移动历史材料。
