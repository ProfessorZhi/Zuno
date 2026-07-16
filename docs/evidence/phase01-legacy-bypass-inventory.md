# PHASE01 P01-T05 Legacy / Bypass Inventory Evidence

phase_id: PHASE01
task_id: P01-T05
status: partial implementation available
start_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
working_branch: codex/P01-T05-legacy-bypass-inventory

## Scope

本证据只证明 P01-T05 的 Legacy / Alias / Bypass inventory 结构和静态扫描输入被补齐；不证明 PHASE01 完整关闭，也不证明 PHASE02 Guard、PHASE07 Model Gateway、PHASE15 Tool Runtime 或 PHASE22 Legacy 删除已经完成。

## Environment

```text
OS: Windows
Shell: powershell without login profile for repository commands
Repository: F:\internship-work\resume&resume project\02_projects\Zuno
```

## Commands And Results

```powershell
rg -n "\b(OpenAI|AsyncOpenAI|ChatOpenAI|Anthropic|AsyncAnthropic|dashscope|aiohttp|httpx|requests\.|subprocess|call_tool|\.execute\(|legacy|legacy_alias|importlib|__import__|getattr\(|setattr\(|monkeypatch|entry_points|click\.command|typer\.|argparse|uvicorn|Celery|RabbitMQ|QueueBackend)" src apps tests tools infra -S
```

Result: static scan completed and produced provider SDK, HTTP side effect, subprocess, MCP direct call, dynamic import, legacy path, CLI and worker/runtime candidates. The scan is intentionally broad and includes tests/tools false positives; inventory entries remain focused on production or migration-relevant paths.

## Updated Artifacts

```text
.agent/programs/work-products/legacy-bypass-inventory.yaml
tools/scripts/verify_phase01_complete_baseline.py
docs/evidence/phase01-legacy-bypass-inventory.md
```

Changes:

- Restored readable Chinese status boundary for P01-T05.
- Added `current_callers`, `deadline`, `guard` and `test` to each registered bypass entry.
- Reused PHASE02 `temporary-allowlist.yaml` test/deadline data where available.
- Strengthened the PHASE01 verifier so P01-T05 checks are per-entry instead of keyword-only.

## Artifact Hash

To reproduce the artifact hash after checkout:

```powershell
Get-FileHash -Algorithm SHA256 .agent/programs/work-products/legacy-bypass-inventory.yaml
Get-FileHash -Algorithm SHA256 docs/evidence/phase01-legacy-bypass-inventory.md
```

## Remaining Gap

P01-T05 is not a completed closure candidate yet. Remaining work:

- Owner review of `current_callers` placeholders.
- Dynamic registry / factory / monkey-patch runtime enumeration.
- Guard tests proving new direct Provider SDK, Tool execute, MCP direct call, subprocess and legacy directory additions fail closed.
- Coordinator merge review after other PHASE01 work packages complete.
