# PHASE22 Tools / Infra / Workflow Findings

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Scope: `tools/**`, `infra/**` (excluding `infra/db/alembic/**`),
`.github/workflows/**`

## Files inspected

### Tools scripts

- `tools/scripts/start.py`
- `tools/scripts/clean_workspace.py`
- `tools/scripts/run-full-e2e-smoke.ps1`
- `tools/scripts/run-desktop-smoke.ps1`
- `tools/scripts/zuno-start.bat`
- `tools/scripts/zuno-stop.bat`
- `tools/scripts/zuno-rebuild-start.bat`
- `tools/scripts/zuno-clean-rebuild-start.bat`
- `tools/scripts/zuno_mcp_smoke_server.py`
- All `tools/scripts/verify_*.py` (referenced by workflows)
- `tools/scripts/phase02_compatibility_runtime.py`

### Tools launchers

- `tools/launchers/windows/_Zuno-{Web,Desktop}-Common.cmd`
- `tools/launchers/windows/_Zuno-Desktop-{StartFrontend,StartElectron,Cleanup,BuildFrontend}.ps1`
- `tools/launchers/windows/Zuno-{Web,Desktop}{,-Phase0-Backend}-{Start,Stop,Rebuild,Full-Rebuild}.cmd`
- `tools/launchers/windows/README.md`

### Infra

- `infra/docker/docker-compose.yml`
- `infra/docker/docker-compose.dev.yml`
- `infra/docker/docker_config.example.yaml`
- `infra/docker/docker_config.local.yaml`
- `infra/docker/Dockerfile`
- `infra/docker/Dockerfile.frontend`
- `infra/docker/nginx.frontend.conf`

### Workflows (all 12)

- `agent-core-target-docs.yml`
- `architecture-document-set.yml`
- `finalize-wave1-governance.yml`
- `infrastructure-target-docs.yml`
- `memory-context-target-docs.yml`
- `model-gateway-target-docs.yml`
- `observability-eval-target-docs.yml`
- `phase22-contract-verification.yml`
- `product-surface-target-docs.yml`
- `security-target-docs.yml`
- `tool-runtime-target-docs.yml`
- `wave1-contract-freeze.yml`

## Classification table

| Surface           | Hit                                                                                       | Classification                                                                                                          |
| ----------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Workflows         | All 12 workflows reference only canonical `tools/scripts/verify_*` paths and `.agent/scripts/verify_*` paths that exist. | not legacy                                                                                                              |
| Workflow: phase22 | Calls into `phase02_compatibility_runtime.py`, `verify_phase22_cleanup_boundary.py`, `tools/scripts/generate_phase22_evidence.py`, `generate_phase22_archive_preflight.py`, `generate_phase22_closure_summary.py`, `generate_phase22_verification_report.py`. | not legacy                                                                                                              |
| Tool: scripts     | `zuno-*.bat` legacy forwarders (Start / Stop / Rebuild / Full Rebuild)                     | ALLOWED_HISTORY_REFERENCE (explicitly tested by `tests/tools/test_launcher_scripts.py::test_legacy_desktop_forwarders_target_current_launcher_names`) |
| Tool: scripts     | `start.py`, `clean_workspace.py`, `run-full-e2e-smoke.ps1`, `run-desktop-smoke.ps1`, `zuno_mcp_smoke_server.py` | not legacy                                                                                                              |
| Tool: scripts     | `verify_*` scripts referenced by workflows and `.agent/scripts/verify_agent_system.py`, `.agent/scripts/verify_doc_boundaries.py`, `.agent/scripts/verify_module_boundaries.py`, `.agent/scripts/verify_repo_hygiene.py` | not legacy                                                                                                              |
| Tool: evals       | `tools/evals/zuno/rag_eval/` and `tools/evals/zuno/multihop_eval/` and `tools/evals/zuno/contract_review_eval/` | not legacy (current evaluation harness; corpus and benchmark thresholds are part of `phase22-removal-candidates.yaml`'s frozen manifest) |
| Tool: migrations  | `tools/migrations/`                                                                       | out of scope (the directory contains one-off migration scripts; not modified by this worker)                            |
| Tool: README      | `tools/scripts/README.md` calls `zuno-*.bat` "legacy forwarders"                          | ALLOWED_HISTORY_REFERENCE (matches reality; preserved as authoritative docstring)                                       |
| Infra: compose    | `infra/docker/docker-compose.yml` retains `elasticsearch` under `profiles: [elasticsearch]` | not legacy (explicit opt-in profile; `enable_elasticsearch: false` in `docker_config.example.yaml`)                    |
| Infra: compose    | `infra/docker/docker-compose.dev.yml` mounts `apps/web`, `tools/cli`, `tools/scripts`, mounts `src/backend` (cached) | not legacy                                                                                                              |
| Infra: Dockerfile | Uses `${PYTHON_BASE_IMAGE}` build arg, `chromium`, `chromium-driver`, mirror-aware PIP     | not legacy                                                                                                              |
| Infra: frontend   | `infra/docker/Dockerfile.frontend` and `nginx.frontend.conf`                              | not legacy                                                                                                              |
| Infra: README     | `infra/docker/README.md`                                                                  | not legacy                                                                                                              |

## Old / retired scripts explicitly searched for and absent

Searches executed for the literal strings (with `rg`):

- `legacy_aliases` (non-file) → only present under `.claude/worktrees/` (isolated); canonical tree has none.
- `run-?desktop-smoke\.ps1` historical variants → only `tools/scripts/run-desktop-smoke.ps1` and the alias `run-full-e2e-smoke.ps1` exist.
- `start_legacy_server\.py`, `bootstrap_legacy_agents\.py`, `init_legacy_state\.py` → none.
- `verify_legacy_dual_write\.py` → not present; replaced by `verify_phase22_cleanup_boundary.py`.
- Workflow `uses:` argo/circle/etc. → only `actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `snok/install-poetry@v1`.

## Outcome

No 1:1 tools/infra/workflow replacement was appropriate. The four .bat legacy
forwarders are intentional and tested. All compose services are live and
referenced by launchers, tests, and the smoke scripts. No edits applied
inside `tools/` or `infra/`, and no `.github/workflows/*` was modified
(which preserves PR #119 evidence untouched, as required).
