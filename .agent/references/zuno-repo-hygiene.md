# Zuno Repo Hygiene Skill

## When To Use

当任务涉及目录移动、兼容壳退休、runtime 一等目录增减、生成物清理、`.gitignore`、repo verifier 或 Program 3 directory surface alignment 时使用。

## Mental Model

目录树是架构表达，不是历史 import path 的展示柜。`src/backend/zuno` 顶层应优先表达 `api / agent / memory / capability / knowledge / platform` 六层；旧实现目录只能作为受控 migration source、facade 或 compatibility surface 存在。

## Current Truth

历史 Program 3 final alias surface closure 已完成。当前目标态要求 `src/backend/zuno` 顶层只保留 `api / agent / memory / capability / knowledge / platform` 六个目录和 `__init__.py`、`main.py` 两个文件；旧 runtime import path 通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

## Target Direction

最终目标是让 `src/backend/zuno` 一等目录只剩六层目标目录，顶层文件只保留 `__init__.py` 和 `main.py`。旧 `core/`、`services/`、`database/`、`schema/`、`tools/`、`utils/`、`config/`、`resources/`、`compatibility/` 不能再作为顶层目录或根级 alias 文件存在。

## Must Preserve

- 旧 public import path 必须有测试保护。
- Runtime 主线仍是 Single GeneralAgent。
- Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档；`zuno-eight-deliverables-full-realization-v1` 也已完成并归档。runtime architecture upgrade 的近期 foundation slice 已在 PHASE09 收口，剩余成熟化仍不是当前独立 queued program。
- Current 文档只能写已实现事实，不能把目标目录写成成熟 runtime。

## Before Editing

1. 读 `.agent/references/code-map.md` 的后端包根规则。
2. 读 `docs/architecture/architecture.md` 和 `docs/architecture/production-readiness.md`。
3. 搜索待移动路径的 imports、tests、scripts 和 docs references。
4. 先加 focused guard，再移动或退休目录。

## Allowed Changes

- 小范围 legacy alias registry、facade re-export、README、目录地图、verifier 和 repo tests。
- 低风险小模块迁移，例如清楚的 contracts、registry、selector、BM25 helper。
- 只读审计和迁移计划。

## Forbidden Changes

- 重写 `services` 或 `core` 内部主循环行为。
- 改 public API、DB schema、eval baseline 或 frontend 行为。
- 恢复 `mcp_servers/`、`middleware/`、`evals/` 顶层目录。
- 新增未经 verifier 登记的 runtime 一等目录或非 alias 顶层文件。

## Common Failure Patterns

- 把“建了六层目录”误写成“目录整理完成”。
- 为了视觉清爽直接删除兼容 import。
- 新代码继续写进泛 `services/`、`utils/`。
- verifier 只检查存在，不检查新增旧式目录。

## Debug Playbooks

- 旧 import 失败：先查 `platform/compatibility/legacy_aliases.py`，再查 `tests/legacy_guards/test_zuno_alias_imports.py`。
- 目录 verifier 失败：先查 `BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS`、`BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES`、`BACKEND_LEGACY_IMPORT_ALIASES` 和 `BACKEND_RETIRED_TOP_LEVEL_PATHS`。
- 不知道目录归属：先查 `.agent/references/code-map.md`，再查 `.agent/references/runtime-call-chain.md`。

## Focused Tests

```powershell
pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
pytest -q tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
```

## Docs Sync

目录边界变化至少检查：

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/references/current-program.md`
- `.agent/references/code-map.md`
- `.agent/references/zuno-repo-hygiene.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture.md`

## Lessons Learned

- Program 3 的完成标准不能停在 facade 起步。
- 目录迁移必须小步、可回滚、有旧 import guard。
- 后端包根不再放 README / DIRECTORY_MAP；目录规则进入 `.agent/references/code-map.md` 和 verifier。
