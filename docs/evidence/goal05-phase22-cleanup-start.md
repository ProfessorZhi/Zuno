# Goal05 PHASE22 Cleanup Start Evidence

status: in_progress
date: 2026-07-30
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据记录 PHASE22 的第一个 cleanup 切口：冻结 PHASE21 removal candidates 输入，并将 Product Runtime 默认路径中的两个 legacy alias import 改为 canonical import。

本证据不声明 PHASE22 completed，不声明 legacy-free tree，不声明 fixed benchmark completed，不声明 production ready。

## Implemented

- 新增 `.agent/programs/work-products/phase22-removal-candidates.yaml`，把 PHASE21/PHASE22 startup 发现的 mandatory cleanup 输入冻结为 PHASE22 删除候选。
- `src/backend/zuno/product/runtime_batch.py` 从 `zuno.schema.workspace` 改为 `zuno.api.dto.workspace`。
- `src/backend/zuno/api/services/product/command_service.py` 从 `zuno.database import engine` 改为 `zuno.platform.database import engine`。
- `tools/scripts/verify_repo_structure.py` 的 active program 结构断言推进到 `current_phase: PHASE22`。
- 新增 `tools/scripts/verify_phase22_cleanup_boundary.py` 和 `tests/repo/test_phase22_cleanup_boundary.py`，防止 Product Runtime 重新引入这两个 legacy alias import，并确保 removal candidates 文件存在。

## Verification

```text
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_phase22_cleanup_boundary.py tests/repo/test_repo_structure_consistency.py tests/api/test_product_runtime_batch.py tests/api/test_goal03_product_route.py -p no:cacheprovider
rg -n "from zuno\.schema\.workspace|from zuno\.database import engine" src/backend/zuno/product src/backend/zuno/api/services/product
```

## Result

```text
PHASE22 cleanup boundary verification passed.
Repository structure verification passed.
27 passed, 1 warning in 69.58s
rg returned no matches
```

## Remaining

- `src/backend/zuno/platform/compatibility/legacy_aliases.py` 仍存在，不能在大量生产 import 仍依赖 `zuno.core` / `zuno.services` / `zuno.schema` / `zuno.database` / `zuno.tools` / `zuno.resources` 时直接删除。
- `tests/legacy_guards/` 仍存在，后续必须迁移为 `tests/repo` canonical boundary guards。
- `legacy_general_agent_completion_rollback` 仍是 PHASE22 cleanup candidate。
- Fixed benchmark、full final verification、production readiness truth 和 Program archive 仍未完成。
