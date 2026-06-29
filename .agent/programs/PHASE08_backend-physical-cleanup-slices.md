# PHASE08：Backend Physical Cleanup Slices

> 状态：pending。目标是把 PHASE06 / PHASE07 的结论拆成可执行小切片。

## 目标

把 `src/backend/zuno` 的拥挤目录逐步变清楚，但每次只做一种低风险动作：

- 增加或修正目录 README。
- 建立 facade re-export。
- 迁移小型 contract / model / helper 文件。
- 删除已证明无引用的 legacy alias。
- 把 generated/local 产物纳入 ignore/verifier。

## 候选切片

| 切片 | 范围 | 目标 | 验证 |
| --- | --- | --- | --- |
| Slice A | `config/`、`settings.py`、`platform/` | 明确配置归属，避免 platform/config 双头叙事。 | settings / repo tests |
| Slice B | `schema/`、`api/` | 判断 DTO 是否逐步迁入 `api/dto`，或保留 `schema` 为 compatibility source。 | API contract tests |
| Slice C | `services/application/*` 到六层 facade | 优先迁移小型 capability/context/knowledge contracts。 | agent / retrieval focused tests |
| Slice D | `tools/`、`system_skills/` | 区分 runtime tools、local skills、system resources。 | tool tests / repo structure |
| Slice E | `legacy/`、retired aliases | 只删除有 grep 和 tests 证明的 legacy。 | legacy guard tests |

## 第一批落地：中层目录分类 README + verifier

> 状态：in progress。本批只做低风险 clarity，不做 runtime 物理移动。

### 变更文件列表

- `src/backend/zuno/README.md`
- `src/backend/zuno/config/README.md`
- `src/backend/zuno/database/README.md`
- `src/backend/zuno/schema/README.md`
- `src/backend/zuno/tools/README.md`
- `src/backend/zuno/system_skills/README.md`
- `src/backend/zuno/prompts/README.md`
- `src/backend/zuno/fixtures/README.md`
- `src/backend/zuno/api/README.md`
- `src/backend/zuno/agent/README.md`
- `src/backend/zuno/memory/README.md`
- `src/backend/zuno/capability/README.md`
- `src/backend/zuno/knowledge/README.md`
- `src/backend/zuno/platform/README.md`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_repo_structure_consistency.py`

### 旧路径和新路径

本批没有物理移动文件，因此没有新 runtime path。旧路径继续保留：

| 旧路径 | 本批分类 | 为什么不移动 |
| --- | --- | --- |
| `src/backend/zuno/config/` | infrastructure | 配置资源和 `settings.py`、`platform/` 叙事重叠；移动前必须证明资源加载路径、settings defaults 和旧 `zuno.config.*` import 不漂移。 |
| `src/backend/zuno/database/` | infrastructure | DB session、metadata、DAO、models 属于持久化底座；移动会触碰 DB schema / session lifecycle 风险，本批只记录边界。 |
| `src/backend/zuno/schema/` | migration-source | 当前仍是 API DTO / Pydantic schema 来源；迁入 `api/dto` 前必须有 API contract tests 证明 public field / response envelope 不变。 |
| `src/backend/zuno/tools/` | migration-source | 当前包含 runtime tools 和 helper；迁入 Capability 层前必须证明 tool registry、permission、execution trace 和旧 `zuno.tools.*` import 不变。 |
| `src/backend/zuno/system_skills/` | app-resource | 当前是 runtime skill resource；移动前必须证明 skill loading、系统 prompt 和 tool injection 行为不变。 |
| `src/backend/zuno/prompts/` | app-resource | 当前是 runtime prompt resource；移动前必须证明 prompt id、加载路径和默认模型行为不变。 |
| `src/backend/zuno/fixtures/` | app-resource | 当前可能混合 runtime / test 资源；拆分到 `tests/`、`examples/` 或 runtime resources 前必须先完成 consumer grep 和 focused tests。 |

### focused tests

```powershell
pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```

最终收口还必须运行本 Thread B 验收命令：

```powershell
git diff --check
pytest -q tests/repo/test_backend_facade_layers.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
```

### rollback plan

如果 README 分类或 verifier 规则误伤现有目录，回滚本批新增 README、恢复六层 README 的分类行、移除 `BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS` 和对应 repo tests。因为本批不移动 runtime 文件、不改 import、不改 schema，rollback 不需要数据迁移。

### docs / verifier 同步判断

本批同步了 README、PHASE08、`verify_repo_structure.py` 和 `test_repo_structure_consistency.py`。暂不更新 `docs/architecture/current-architecture.md` 或 `target-architecture.md`，因为这批只把既有边界讲清并加入机器检查，没有把 Target 能力提升为 Current。

## 禁止

- 不一次性移动 `services/`。
- 不在一个切片里同时改 API、DB、GraphRAG 和 Agent runtime。
- 不为了视觉清爽牺牲 import compatibility。

## 完成标准

每个切片必须有：

- 变更文件列表。
- 旧路径和新路径。
- focused tests。
- rollback plan。
- docs / verifier 是否同步的判断。
