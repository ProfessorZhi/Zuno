# Program Roadmap

## 当前状态

Active program: `zuno-eight-deliverables-full-realization-v1`
state: active

每次新 program 都从 `PHASE01` 开始编号；已完成 program 必须归档到 `docs/history/programs/`，并从 `.agent/programs/` 前台移除 `PHASE*.md` 文件。

本轮 program 将五个 queued / not active 草案整合为一个完整落实八大交付物的大 program。`.agent/architecture/future/programs/` 只保留参考草案身份，不再作为当前执行入口。

## 总边界

允许：

- 完整落实八大交付物，而不是只做最小切片。
- 增加或重构 thin facade、contracts、policy、selector、retrieval、rendering、trace、eval 和 verifier。
- 将 Query Router、Context Pack、Memory、Capability ToolCard、GraphRAG、Hooks、Trace、Evidence、Artifact 进入可测试 runtime contract。
- 同步 `docs/architecture.md`、`docs/architecture.html`、`docs/architecture/*`、`.agent/references/*`、`.agent/templates/*`、README、verifier 和 repo tests。
- 按 phase / PR 递进推进，每个 PR 具备可复现验证。

禁止：

- 把未完成 runtime 能力写成 Current。
- 改 DB schema、API response shape、eval baseline 或 frontend 行为，除非对应 phase 明确列入验收并补齐测试。
- 删除旧 public import path 而没有 compatibility proof。
- 把 Codex 多 agent 执行方式误写成 Zuno runtime 多 Agent 架构。
- 把 `.agent/plans/` 写成当前启用入口。
- 把 Java、微服务、event worker 当作近期实现目标。

## Phase / PR 切分

| Phase | 主题 | 主要交付物 | PR 边界 |
| --- | --- | --- | --- |
| PHASE01 | Program boot baseline | 交付物 3、8 | active program、status surfaces、verifier/tests |
| PHASE02 | Workflow self-maintenance | 交付物 1、2、3、8 | AGENTS / references / templates / self-review guard |
| PHASE03 | Architecture docs + HTML | 交付物 4、5、6、8 | docs architecture、HTML render、visual/source sync |
| PHASE04 | Query router + mode policy | 交付物 6、7、8 | completed：mode contract、router policy、trace/eval |
| PHASE05 | Context builder + memory | 交付物 6、7、8 | completed：Context Pack、五类记忆、source ids、compression / extraction policy、review contract |
| PHASE06 | Capability + ToolCard + MCP | 交付物 6、7、8 | completed：ToolCard contract、Native BM25 ToolCard retrieval foundation、MCP/local policy trace |
| PHASE07 | Hooks + evidence + trace + artifact | 交付物 6、7、8 | completed：hook event schema、evidence verdict、artifact manifest、GeneralAgent additive trace event、eval diagnostics |
| PHASE08 | GraphRAG + knowledge runtime | 交付物 6、7、8 | active：extraction configs、retrieval fusion、drift/local/global |
| PHASE09 | Runtime upgrade integration | 交付物 6、7、8 | GeneralAgent path、six-layer ownership、integration tests |
| PHASE10 | Validation + release closure | 交付物 1-8 | full validation、docs sync、archive、commit/push |

## 已完成 Program

- `zuno-repo-layout-cleanup-v1`：完成 Program 3 root / alias surface closure。
- `zuno-six-layer-internalization-v1`：完成六层内部第一批 thin surfaces、README 边界、focused tests、repo verifier 和 Agent verifier 收口。

## 被本轮吸收的草案

- `zuno-query-router-and-mode-policy-v1`
- `zuno-context-builder-and-memory-v1`
- `zuno-hooks-evidence-trace-v1`
- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`

这些草案仍可作为参考材料，但本轮执行以 `.agent/programs/PHASE*.md` 为准。
