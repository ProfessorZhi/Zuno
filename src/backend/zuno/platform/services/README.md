# Services 迁移源

分类：`migration-source`

## 当前角色

`src/backend/zuno/services/` 当前仍承载 application services、GraphRAG / retrieval、memory foundation、capability foundation、storage、queue、MCP、pipeline 和 workspace runtime 实现。它是最大旧 runtime 来源，不能用一次性目录移动替代架构切片。

PHASE02 的当前 owner 入口是 `docs/architecture/repo-ownership-matrix.md`。新增 `platform/services/*` 子目录前，必须先在 `PLATFORM_SERVICES_TARGET_OWNERS` 和 ownership matrix 中声明 target owner、compat path、测试和 verifier；否则 repo structure verifier 会失败。

## Target role

目标状态下，services 内部实现应按职责分流到 `agent/`、`memory/`、`capability/`、`knowledge/` 和 `platform/`。迁移顺序必须按 vertical slice 推进：先 contract/facade，再小型实现，再高风险 runtime。

当前 target owner 概览：

- `application` -> `api / knowledge / workspace`
- `convert_files`、`pipeline` -> `knowledge/ingestion`
- `graphrag` -> `knowledge/graphrag`
- `rag`、`retrieval`、`deepsearch`、`rewrite` -> `knowledge/retrieval`
- `memory` -> `memory`
- `mcp`、`mcp_openai` -> `capability/mcp`
- `sandbox` -> `platform/security`
- `storage` -> `platform/storage`
- `llm`、`embedding` -> `platform/model_gateway` 或 retrieval 相关 owner
- `queue` -> future `platform/jobs`
- `workspace` -> `agent / platform/workspace`

## 允许新增内容

- 允许保留旧 `zuno.services.*` import path 作为当前 runtime 兼容面。
- 允许把小型 contract、selector、retrieval helper 或 platform helper 迁到目标层，并保留旧路径 re-export。

## 禁止事项

- 禁止 bulk move `services/`。
- 禁止改变 API response、GraphRAG retrieval、queue/storage、MCP 或 memory runtime 行为。
- 禁止把 Target 能力写成 Current，除非有代码、测试和 trace/eval 证据。

## Focused tests

- `tests/agent/`
- `tests/retrieval/`
- `tests/storage/`
- `tests/tools/`
- `tests/legacy_guards/test_zuno_alias_imports.py`
