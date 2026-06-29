# Program Roadmap

## 当前状态

当前 active program：

```text
zuno-six-layer-internalization-v1
```

每次新 program 都从 `PHASE01` 开始编号；当前 program 也是从 `PHASE01` 重新开始，不沿用 Program 3 的 Phase 号。

目标：在 Program 3 已经完成 root / alias surface closure 的基础上，让 `api / agent / memory / capability / knowledge / platform` 六层内部逐步拥有清晰、可测试、无副作用的目标层入口。

## 总边界

允许：

- 增加薄 facade、contracts、policy、selector、retrieval、rendering、trace 等目标层入口。
- 保留旧 public import path，并证明新旧入口对象一致。
- 修正文档中 Current / Target 混淆。
- 增加 focused tests 和 verifier guard。

禁止：

- 改 API response shape。
- 改 DB schema。
- 改 frontend。
- 改 eval baseline。
- 重写 GeneralAgent 主循环。
- 删除 `zuno.services.*`、`zuno.core.*`、`zuno.database.*` 等旧 public import path。
- 把未完成的 production runtime 能力写成 Current。

## Phase Plan

1. `PHASE01_six-layer-current-inventory.md`：盘点六层内部成熟度，确认 Program 3 只完成顶层封口。
2. `PHASE02_memory-layer-foundation-surfaces.md`：让 `memory/` 从纯 facade 变成 contract / store / policy / review / retrieval / rendering / engine 薄入口。
3. `PHASE03_capability-layer-foundation-surfaces.md`：按 contracts / registry / selector / policy / execution / trace / mcp / tools 收口 capability 入口。
4. `PHASE04_knowledge-layer-foundation-surfaces.md`：按 query_service / contracts / evidence / citation / retrieval / fusion / graphrag 收口 knowledge 入口。
5. `PHASE05_agent-runtime-boundary-surfaces.md`：在不重写 GeneralAgent 的前提下，把 agent 层入口拆成 runtime / context / post_turn / state / tool_bridge。
6. `PHASE06_platform-boundary-hardening.md`：收紧 platform 的 config / database / security / observability / compatibility / common 边界。
7. `PHASE07_docs-verifier-and-closure.md`：同步 docs、AGENTS、verifier、tests，并归档当前 program。

## 当前 Phase 状态

- Phase 01：completed。
- Phase 02：in progress。
- Phase 03-07：pending。

## 最近完成历史

Program 3 已完成并归档：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 完成态中，`src/backend/zuno` 根目录只允许：

```text
__init__.py
main.py
api/
agent/
memory/
capability/
knowledge/
platform/
```

旧 import path 必须继续可用，并由 `platform/compatibility/legacy_aliases.py` 或后续明确 compatibility 机制保护。

## Queued / Not Active

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
