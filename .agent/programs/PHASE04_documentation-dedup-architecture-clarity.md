# PHASE04 Documentation Dedup Architecture Clarity

status: completed
completed_at: 2026-07-01
next_phase: PHASE05_repo-ownership-and-compatibility-retirement

## 目标

让文档系统清晰无冗余：`architecture.md` 讲目标架构，`production-readiness.md` 讲成熟度和交付物，program 文件讲执行，History 保存旧证据。

## 范围

- 检查 README、AGENTS、docs/architecture、.agent/architecture、.agent/references、docs/history 的重复和漂移。
- 保持 `docs/architecture/architecture.md` 与 `.agent/architecture/architecture.md` 镜像一致。
- 保持 HTML 由 Markdown 生成，不承载唯一事实。

## 禁止范围

- 不恢复 `current-architecture.md`、`target-architecture.md`、`roadmap.md`、`deliverables.md` 为当前前台。
- 不在 README / AGENTS 重复 phase 目录或 Production Target 细节。

## 验收闸门

- 前台文档入口少而精。
- 架构描述和生产成熟度边界清楚。
- 文档去冗余规则进入 verifier / tests。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
```

## 需要先读取

- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `.agent/architecture/README.md`
- `.agent/architecture/architecture.md`
- `.agent/references/docs-map.md`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/documentation-governance.md`
- `tools/scripts/verify_docs_entrypoints.py`

## 需要修改的文件

- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/README.md`
- `.agent/architecture/README.md`
- generated: `docs/architecture/architecture.html`、`.agent/architecture/architecture.md`、`.agent/architecture/architecture.html`
- `tools/scripts/verify_docs_entrypoints.py`
- `tests/repo/test_docs_entrypoints.py`

## 执行拆解

1. 建立前台文档职责表：README 只导航，architecture 讲架构，production-readiness 讲成熟度，program 讲执行，history 留证据。
2. 搜索重复 Current / Target / phase / deliverables 展开，压缩到唯一事实源。
3. 更新 architecture.md 中当前 active program 和实施落点，但不把 Production Target 写成 Current。
4. 运行 render_architecture 同步 HTML 和 `.agent/architecture` 镜像。
5. 更新 docs verifier/test，阻止旧拆分文档回到前台。

## 多 agent 分工

- Thread A：审计 README / docs/architecture。
- Thread B：审计 `.agent/architecture` 和 references。
- Thread C：更新 verifier/test。
- 主线程：修改 architecture.md、运行 renderer、审查镜像 diff。

## 需要返回的证据

- 文档职责表。
- 重复内容删除或保留理由。
- architecture Markdown / HTML sync 结果。
- docs entrypoint verifier 结果。

## 停止条件

- 需要恢复已归档拆分文档作为当前入口。
- Markdown 和 HTML 生成结果不一致。
- Current / Target 边界因文档压缩变模糊。

## 完成证据

PHASE04 已把前台文档职责进一步压缩为“入口只导航、architecture 讲架构、production-readiness 讲成熟度、program 文件讲执行、history 留证据”。本 phase 没有恢复旧拆分架构文档，也没有把 Production Target 写成 Current。

### 文档职责表

| Surface | 职责 | PHASE04 处理 |
| --- | --- | --- |
| `README.md` | 仓库总览和首读路径 | 删除 runtime-full 闭环链路重复，保留归档指针和 production-readiness 指针。 |
| `AGENTS.md` | Agent boot entry 和工作流契约 | 删除 runtime-full 闭环链路重复，保留归档位置和闭环证据边界。 |
| `docs/architecture/README.md` | 架构目录入口 | 删除上一轮 program 的完整闭环链路，保留 architecture / production-readiness / history 路由。 |
| `.agent/programs/current.md` | active program 当前状态 | 删除闭环链路细节，保留当前 phase、归档位置和 phase gate。 |
| `.agent/references/current-program.md` | Agent 侧 program 状态索引 | 删除闭环链路细节，保留 active program、归档位置和 Current / Target 规则。 |
| `.agent/references/docs-map.md` | 文档同步 skill | 把 `docs/architecture/architecture.md` 从多角色重复入口压缩为单一总架构职责，并加入 `production-readiness.md` / `repo-ownership-matrix.md` 明确边界。 |

### 去冗余规则

- 前台摘要不得重复 phase 完成细节、Production Target 清单或 runtime-full 闭环链路。
- `docs-map.md` 的正式入口列表中 `docs/architecture/architecture.md` 只能出现一次；成熟度和 owner matrix 必须使用各自正式文件承载。
- `docs-map.md` 的 Docs Sync 列表不能重复同一路径。

### Verifier / Test 证据

- RED：新增 `test_docs_map_does_not_duplicate_architecture_source_roles` 后，`pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider` 失败，证明 `docs-map.md` 中 `docs/architecture/architecture.md` 出现 4 次且 verifier 缺少对应检查。
- GREEN：修正 `docs-map.md` 并新增 `verify_docs_map_has_unique_architecture_source_roles` 后，同一测试通过，`13 passed`。
- RED：把 runtime-full 闭环链路加入 forbidden summary details 后，docs verifier 指出 `README.md`、`AGENTS.md`、`docs/architecture/README.md`、`.agent/programs/current.md` 和 `.agent/references/current-program.md` 仍重复该链路。
- GREEN：瘦身上述 5 个摘要入口后，`python tools/scripts/verify_docs_entrypoints.py` 通过，`pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider` 通过。

### 最终收口验证

| Command | Result |
| --- | --- |
| `git diff --check` | exit 0，仅 Windows LF/CRLF 提示。 |
| `python tools/agent/render_architecture.py --check` | exit 0，architecture Markdown mirror 和 HTML outputs in sync。 |
| `python tools/scripts/verify_docs_entrypoints.py` | exit 0，documentation entrypoint verification passed。 |
| `python .agent/scripts/verify_doc_boundaries.py` | exit 0，Doc boundary verification passed。 |
| `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1` | exit 0，Docs verification passed。 |
| `python .agent/scripts/verify_agent_system.py` | exit 0，Agent system verification passed。 |
| `python tools/scripts/verify_repo_structure.py` | exit 0，Repository structure verification passed；PowerShell Terminal-Icons profile 输出为环境噪音。 |
| `pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider` | `13 passed`。 |
| `pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider` | `41 passed`。 |
