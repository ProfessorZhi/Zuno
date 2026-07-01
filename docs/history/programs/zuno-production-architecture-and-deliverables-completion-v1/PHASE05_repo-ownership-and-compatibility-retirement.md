# PHASE05 Repo Ownership and Compatibility Retirement

status: completed
completed_at: 2026-07-01
next_phase: PHASE06_product-surface-desktop-recovery-loop

## 目标

让文件夹结构和代码 ownership 真正清晰，减少零碎和凑合的兼容层，把真实 runtime owner 收回六层目录。

## 范围

- 盘点 `src/backend/zuno/api`、`agent`、`memory`、`capability`、`knowledge`、`platform`。
- 盘点 `platform/services`、`platform/compatibility`、`platform/vendor`、provider tree、legacy alias。
- 设计 import matrix、迁移顺序、兼容桥保留条件和退休条件。

## 禁止范围

- 不无测试删除 public import path。
- 不把 compatibility 当成新功能 owner。
- 不进行无关大重构。

## 验收闸门

- owner map 与 repo-ownership matrix 更新。
- legacy / compatibility / vendor guard 有测试。
- 至少完成一批低风险物理迁移或明确 blocked evidence。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
```

## 需要先读取

- `docs/architecture/repo-ownership-matrix.md`
- `.agent/references/code-map.md`
- `.agent/references/runtime-call-chain.md`
- `.agent/references/zuno-repo-hygiene.md`
- `src/backend/zuno/*/README.md`
- `src/backend/zuno/platform/compatibility/legacy_aliases.py`

## 需要修改的文件

- `docs/architecture/repo-ownership-matrix.md`
- `src/backend/zuno/api/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/platform/**`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- `tests/repo/test_backend_facade_layers.py`
- `tests/repo/test_static_target_layer_imports.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`

## 执行拆解

1. 建立 import matrix：旧 public path、当前 owner、目标 owner、compat bridge、test coverage。
2. 先迁移低风险 alias / facade / README owner，不碰数据库 schema 和 public API field rename。
3. 将 `platform/services` 中真实 runtime owner 分类为保留、迁移、thin facade、blocked。
4. 对 compatibility / vendor / provider tree 写明退休条件和禁止承载新功能规则。
5. 更新 repo structure verifier，让零碎路径不能重新扩散。

## 多 agent 分工

- Thread A：api / agent / memory owner map。
- Thread B：capability / knowledge owner map。
- Thread C：platform/services / compatibility / vendor / provider tree。
- Thread D：verifier/test guard。
- 主线程：审查 import matrix，合并低风险迁移。

## 需要返回的证据

- import matrix。
- compatibility retirement table。
- owner migration diff。
- import smoke test 和 static target layer test 结果。

## 停止条件

- 删除或改名 public import path 会破坏 legacy guards。
- 需要 database schema 或 API field rename。
- 同一 runtime owner 被两个目录同时承载且无法安全拆分。

## 完成证据

PHASE05 已完成一批低风险 owner 收口：不删除 public alias，不迁移 DB / API schema，不移动重 runtime；先把已存在的六层 owner surface 固定进 repo verifier / tests，并退休两个过时物理路径说法。

### Import Matrix

| Legacy / old physical path | Current owner | Compat bridge | PHASE05 处理 |
| --- | --- | --- | --- |
| `zuno.schema.*` | `src/backend/zuno/api/dto/` | `platform/compatibility/legacy_aliases.py` | `api/README.md` 改为 api/dto owner，不再把 root-level schema 目录写成 Current。 |
| `src/backend/zuno/services/application/capabilities/` | `src/backend/zuno/platform/services/application/capabilities/` | `zuno.services.application.capabilities.*` | `runtime-call-chain.md` 改到当前 platform/services 物理路径。 |
| `agent/harness.py` / `agent/durable_runtime.py` | `src/backend/zuno/agent/` | `zuno.core.*` legacy aliases | 加入 `BACKEND_LAYER_INTERNAL_SURFACES`，防止 owner surface 漂移。 |
| `capability/control_plane.py` / `capability/retrieval.py` / `capability/runtime.py` | `src/backend/zuno/capability/` | `zuno.services.application.capabilities.*` | 加入 repo verifier 和 static target layer tests 覆盖。 |
| `knowledge/agentic_graphrag.py` / `knowledge/indexing/` | `src/backend/zuno/knowledge/` | `zuno.services.graphrag.*`、`zuno.services.retrieval.*`、`zuno.services.rag.*` | 加入 repo verifier surface pin。 |

### Compatibility Retirement Table

正式表已写入 `docs/architecture/repo-ownership-matrix.md` 的 `PHASE05 Owner Surface Pin` 与 `Compatibility Retirement Table`。本 phase 的结论：

- `zuno.schema.*` 保留，直到所有 public DTO consumer 有替代路径和 legacy guard 更新。
- `zuno.services.application.capabilities.*` 保留，直到 provider runtime 有独立 owner、import matrix 和 focused tests。
- `platform/compatibility/legacy_aliases.py` 保留为唯一 legacy import registry。
- `platform/compatibility/vendor/fastapi_jwt_auth` 保留，等待单独 vendor migration 计划。

### Owner Migration Diff

- 更新 `tools/scripts/verify_repo_structure.py` 的 `BACKEND_LAYER_INTERNAL_SURFACES`：补 `agent/harness.py`、`agent/durable_runtime.py`、`capability/control_plane.py`、`capability/retrieval.py`、`capability/runtime.py`、`knowledge/agentic_graphrag.py` 和 `knowledge/indexing/`。
- 新增 `verify_backend_owner_docs_do_not_reference_retired_physical_paths`，防止 retired physical path 回流。
- 更新 `tests/repo/test_repo_structure_consistency.py`，先 RED 后 GREEN 固定 owner surface 和 stale path guard。

### Blocked Physical Migration Evidence

本 phase 未执行物理迁移。原因：候选重 runtime 仍由 public alias、legacy guards 或后续 PHASE07-PHASE11 runtime target 保护；删除或改名会触发停止条件。当前安全收口是 owner pin、文档路径退休和 verifier/test 防漂移。

### 最终收口验证

| Command | Result |
| --- | --- |
| `git diff --check` | exit 0，仅 Windows LF/CRLF 提示。 |
| `python tools/scripts/verify_repo_structure.py` | exit 0，Repository structure verification passed。 |
| `python .agent/scripts/verify_repo_hygiene.py` | exit 0，Repo hygiene verification passed。 |
| `python .agent/scripts/verify_module_boundaries.py` | exit 0，Module boundary verification passed。 |
| `python tools/agent/render_architecture.py --check` | exit 0，architecture Markdown mirror 和 HTML outputs in sync。 |
| `python .agent/scripts/verify_agent_system.py` | exit 0，Agent system verification passed。 |
| `python tools/scripts/verify_docs_entrypoints.py` | exit 0，documentation entrypoint verification passed。 |
| `pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider` | `31 passed`。 |
| `pytest -q tests/repo/test_repo_structure_consistency.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider` | `48 passed`，9 个第三方 deprecation warnings。 |
| `pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider` | `13 passed`。 |
