# Goal05 PHASE22 Canonical Cleanup Wave 1 Evidence

status: BOUNDARY_ACCEPTED_NOT_MERGE_READY
date: 2026-08-01
branch: agent/minimax/phase22-canonical-cleanup-wave1
work_package: MM-PHASE22-CANONICAL-CLEANUP-WAVE1
base_branch: docs/phase22-agent-performance-governance
base_sha: 3fa2f4734c88f9e4510cf0c2f3a99d82b06226a1

## Scope

本证据记录 PHASE22 P22-T03 / P22-T04 第一波 cleanup：在 Wave 0 已完成 alias registry 退役、`tests/legacy_guards` 退场、绝大多数内部 legacy alias import 迁出之后，把仅剩的 `platform/compatibility/vendor/fastapi_jwt_auth` 第三方 vendor shim 物理迁移到其 canonical owner `platform/vendor/fastapi_jwt_auth`，并删除空壳 `platform/compatibility/` 目录；同步新增静态边界规则，防止生产源码重新引入 legacy 目录/文件、legacy_aliases、永久双读/双写或无 Owner compatibility alias、任何对 `zuno.platform.compatibility.*` 的旧内部 import。

本证据不声明 PHASE22 completed，不声明 legacy-free tree，不声明 fixed benchmark completed，不声明 production ready。

## Implemented

- 把 `src/backend/zuno/platform/compatibility/vendor/fastapi_jwt_auth/`（`__init__.py`、`auth_config.py`、`auth_jwt.py`、`config.py`、`exceptions.py`）物理迁移到 `src/backend/zuno/platform/vendor/fastapi_jwt_auth/`。
- `src/backend/zuno/api/services/user.py`、`src/backend/zuno/api/v1/user.py`、`src/backend/zuno/main.py`、`src/backend/zuno/platform/services/autobuild/build.py` 的 vendored AuthJWT import 由 `from zuno.platform.compatibility.vendor.fastapi_jwt_auth ...` 改为 canonical `from zuno.platform.vendor.fastapi_jwt_auth ...`。
- `tests/api/test_fastapi_jwt_auth_compat.py` 的 `VENDORED_ROOT` 与四个 module spec 全部指向 canonical `zuno.platform.vendor.fastapi_jwt_auth`；`test_fastapi_jwt_auth_runtime_imports_use_vendored_package` 断言 `AuthConfig` / `LoadConfig` / `AuthJWTException` 的 `__module__` 都以 `zuno.platform.vendor.fastapi_jwt_auth` 开头，`AuthJWT` 的 `__file__` 解析到 `platform/vendor/fastapi_jwt_auth/`。
- `src/backend/zuno/platform/compatibility/` 目录整体删除（包含 `__init__.py`、`README.md`、`vendor/` 子目录），不再有任何生产源码或测试再导入 `zuno.platform.compatibility.*`。
- `src/backend/zuno/platform/vendor/README.md` 升级到 `PHASE22 status: canonical-owner-active (P22-T03 Wave 1)`，声明 `fastapi_jwt_auth` 已迁入、禁止再恢复 `platform/compatibility/vendor/fastapi_jwt_auth/` 或 `src/backend/fastapi_jwt_auth/` 顶层 public shell。
- `src/backend/zuno/platform/vendor/__init__.py` 的 `__all__` 从空改为 `["fastapi_jwt_auth"]`，暴露 canonical subpackage。
- `tools/scripts/verify_phase22_cleanup_boundary.py` 新增三组硬边界：
  1. 静态扫描 `src/backend/zuno`、`apps/web/src`、`apps/desktop/src`，禁止任何 production 文件或目录名出现 `legacy`、`legacy_*`、`*_legacy` 段或文件名 `legacy_aliases.py`；已显式登记在 `.agent/programs/work-products/phase22-removal-candidates.yaml::mandatory_removal_candidates` 且 `current_status: active_candidate` 的路径会被 allowlist（如 `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 是 PHASE16 fixed blocker）。
  2. 禁止任何 production `.py` 文件 import `from zuno.platform.compatibility` 或 `import zuno.platform.compatibility`。
  3. 禁止任何 production `.py` 文件包含 `zuno.platform.compatibility.vendor.fastapi_jwt_auth` 或 `ZUNO_AGENT_RUNTIME=legacy_general_agent` 这类永久双读/双写或无 Owner compatibility alias 标记。
  4. canonical owner 要求：vendor shim 必须位于 `src/backend/zuno/platform/vendor/fastapi_jwt_auth/`，旧 `src/backend/zuno/platform/compatibility/vendor/fastapi_jwt_auth/` 任何回写都会失败。
- `.agent/programs/work-products/phase22-removal-candidates.yaml` 新增 `wave1_resolved` 段落与 `fixed_blockers` 段落，把 4 个 caller、1 个 vendor shim、1 个 compat test、1 个 compatibility 目录、1 个 `platform/vendor/README.md` 的 before/after 全部登记入 evidence，并显式记录 `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 作为 PHASE16 fixed blocker。
- `.agent/references/code-map.md` 的后端包根规则说明：移除 `platform/compatibility/legacy_aliases.py` 描述，把旧 public alias 列表与当前 canonical owner 暴露对应。
- `docs/governance/repo-ownership-matrix.md` 把 `platform/compatibility/legacy_aliases.py` 状态改为 `wave-1-retired`、`platform/vendor/fastapi_jwt_auth` 改为 `wave-1-canonical`、`platform/vendor` 改为 `canonical-owner-active`，并把 Compatibility Retirement Table 中两条 entry 替换为 Wave 1 结果，把 Guardrails 段两条规则改成 wave-1 wording。

## 不在范围内

- `tools/evals/zuno/**`、`tests/evals/**`、`.github/workflows/**` 未修改。
- 共享 `agent-performance-ledger.md` / `agent-performance-ledger.csv` 未修改（PR 自己的 record JSON 单独建）。
- `infra/db/alembic/env.py`、Migration、数据库模型和业务 Contract 未修改。
- `src/backend/zuno/knowledge/ingestion/legacy_cutover.py` 未删除；保留为 PHASE16 fixed blocker，由 cleanup boundary verifier 的 allowlist 显式保护。
- `tests/legacy_guards/` 已在 Wave 0 退场；本 PR 不再删除（已无目录）。
- 未运行 Docker、付费模型、完整前端 build、全量 pytest 与压测。

## Verification

```text
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_repo_structure.py
python -c "import sys; sys.path.insert(0,'src/backend'); from zuno.platform.vendor.fastapi_jwt_auth import AuthJWT; print(AuthJWT)"
python -m compileall -q src/backend/zuno/platform/vendor/fastapi_jwt_auth
git diff --check
```

预期结果：cleanup verifier 与 repo structure verifier 同时通过；canonical vendor shim import 正常解析；compileall 通过；diff --check 无 trailing whitespace / no newline 警告。

实际结果（执行时记录于本 PR 评论与 PR record 中）。

## Forbidden operations not used

- `git reset`：未使用。
- `git rebase`：未使用。
- `git commit --amend`：未使用。
- `git cherry-pick`：未使用。
- `git push --force`：未使用。

## Not Claimed

- 本 PR 不声明 PHASE22 整体完成、不声明 production ready、不声明 fixed benchmark 完成、不声明 Program 归档。
- 本 PR 不删除 `src/backend/zuno/knowledge/ingestion/legacy_cutover.py`；它仍是 PHASE16 fixed blocker。
- 本 PR 不删除 `src/backend/fastapi_jwt_auth/` 顶层 public shell 之外仍有第二份兼容拷贝的可能；只验证 vendor shim 已迁入 canonical owner。
- 本 PR 不修改 `tools/evals/zuno/**`、`tests/evals/**`、`.github/workflows/**`、Migration、数据库模型和业务 Contract。
- 本 PR 不修改共享 agent-performance ledger Markdown / CSV。