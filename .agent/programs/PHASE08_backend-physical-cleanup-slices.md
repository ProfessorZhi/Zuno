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
| Slice F | root local artifacts、generated cache、`data/`、`reports/` | 根目录不保留 `.agents`、`.local`、`.test-tmp`、`node_modules`、`__pycache__` 等本地产物；`data/` / `reports/` 继续使用白名单语义。 | repo structure / repo hygiene tests |

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

## Thread C：Root / Local Artifact Cleanup

> 状态：已执行。本轮只处理根目录和本地产物可见噪音，不移动 runtime 源码，不删除 tracked 数据。

### 审计结论

| path | tracked / untracked 判断 | 处理动作 | 保留或清理原因 |
| --- | --- | --- | --- |
| `.agents/` | 未发现 tracked 或 untracked 实体。 | 不创建、不 ignore 成长期入口；由 structure verifier 禁止回潮。 | 旧点号 Agent 入口会和 `AGENTS.md` 并行，属于前台噪音。 |
| `.test-tmp/` | 未发现 tracked 或 untracked 实体；`.gitignore` 已覆盖。 | 保留 ignore 规则，并由 structure verifier 禁止根目录实体残留。 | 测试 scratch 可再生成，不应出现在第一次打开的根目录。 |
| `.local/` | 未发现 tracked 或 untracked 实体；`.gitignore` 已覆盖。 | 保留 ignore 规则，并由 structure verifier 禁止根目录实体残留。 | 本地配置、eval 和运行态产物可以在本机生成，但不应挡住仓库结构。 |
| `data/` | 未发现当前实体；hygiene verifier 已禁止 broad `data/` ignore。 | 不删除、不新增 broad ignore。 | 正式样例或证据必须显式归属；生成物只能用白名单子路径 ignored。 |
| `reports/` | 未发现当前实体；hygiene verifier 已禁止 broad `reports/` ignore。 | 不删除、不新增 broad ignore。 | 正式报告应提升到 `docs/evidence/` 或明确 allowlist；运行报告保持 local/ignored。 |
| `node_modules/` | 未发现根目录实体；未发现 tracked 命中。 | 不删除用户依赖安装；由 verifier 禁止根目录实体残留。 | 依赖安装产物不属于仓库结构，也不作为项目封面展示。 |
| `__pycache__/`、`.pytest_cache/` | 未发现根目录或全仓实体。 | 无需删除；由 `.gitignore` 和 structure verifier 防回潮。 | Python / pytest 缓存可再生成。 |

### 变更文件

- `tools/scripts/verify_repo_structure.py`：新增 `ROOT_LOCAL_ARTIFACT_DIRECTORIES` 和 `verify_root_local_artifacts_are_absent()`，把根目录本地产物可见噪音纳入结构验证。
- `tests/repo/test_repo_structure_consistency.py`：新增测试 pin 常量和 `run_verification()` 调用链，防止规则漂移。
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`：记录 Slice F 的审计结论和验收边界。

### 验收与回滚

- focused tests：`pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`。
- program gate：`git diff --check`、`python tools/scripts/verify_repo_structure.py`、`python .agent/scripts/verify_agent_system.py`。
- rollback plan：如 verifier 误伤正式样例或正式证据，先把该路径分类为 Current / History / Generated / Local，再调整 allowlist；不要直接放宽为 broad `data/`、`reports/` 或 `node_modules/` 规则。
