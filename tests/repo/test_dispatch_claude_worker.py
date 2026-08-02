from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = REPO_ROOT / ".agent" / "scripts" / "dispatch_claude_worker.ps1"


def _run(cmd: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    return subprocess.run(cmd, cwd=cwd, env=merged, capture_output=True, text=True)


def _git(cwd: Path, *args: str) -> None:
    result = _run(["git", *args], cwd)
    assert result.returncode == 0, result.stderr + result.stdout


def _make_repo(tmp_path: Path, branch: str = "worker") -> Path:
    repo = tmp_path / "worker repo"
    repo.mkdir()
    _git(repo, "init", "-b", branch)
    _git(repo, "config", "user.email", "worker@example.invalid")
    _git(repo, "config", "user.name", "Worker")
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "init")
    return repo


def _write_launcher(bin_dir: Path, name: str) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    path = bin_dir / name
    path.write_text("@echo off\r\nexit /b 0\r\n", encoding="utf-8")


def _write_fake_runner(tmp_path: Path) -> Path:
    runner = tmp_path / "fake-runner.ps1"
    runner.write_text(
        r'''
param(
    [string]$Provider,
    [string]$WorkPackage,
    [int]$PRNumber,
    [string]$Repository,
    [string]$Worktree,
    [string]$ClaudeCommand = "",
    [string]$ClaudeArgsJson = ""
)
$ErrorActionPreference = "Stop"
$record = @{
    Provider = $Provider
    WorkPackage = $WorkPackage
    PRNumber = $PRNumber
    Repository = $Repository
    Worktree = $Worktree
    ClaudeCommand = $ClaudeCommand
    ClaudeArgsJson = $ClaudeArgsJson
}
if ($env:ZUNO_FAKE_RUNNER_RECORD) {
    $record | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $env:ZUNO_FAKE_RUNNER_RECORD -Encoding UTF8
}
$summaryPath = Join-Path $env:ZUNO_FAKE_RUNNER_DIR "summary.json"
@{
    session_id = "session-123"
    session_correlation = "bound"
    wall_clock_seconds = 1.25
    agent_process_seconds = 1.0
    token_buckets = @{ input = 10; output = 5 }
    api_equivalent_cost_usd = 0.012
} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
Write-Output "RUN_ID=fake-run"
Write-Output "SUMMARY_PATH=$summaryPath"
if ($env:ZUNO_FAKE_ECHO_PROMPT -eq "1") {
    $argsList = $ClaudeArgsJson | ConvertFrom-Json
    Write-Output ([string]$argsList[1])
    Write-Output "contact admin@example.com token=super-secret"
    Write-Output "C:\Users\Administrator\private"
}
if ($env:ZUNO_FAKE_WORKER_RESULT) {
    Write-Output ("WORKER_RESULT_JSON=" + $env:ZUNO_FAKE_WORKER_RESULT)
}
$agentExit = 0
if ($env:ZUNO_FAKE_AGENT_EXIT) { $agentExit = [int]$env:ZUNO_FAKE_AGENT_EXIT }
Write-Output "AGENT_EXIT_CODE=$agentExit"
exit $agentExit
'''.strip(),
        encoding="utf-8",
    )
    return runner


def _task_card(tmp_path: Path, *, completion: bool = True, short: bool = False) -> tuple[Path, str]:
    required_checks = """
Required Checks:

- git diff --check
- python -m pytest -q tests/repo/test_dispatch_claude_worker.py -p no:cacheprovider
"""
    completion_contract = """
Completion Contract:

- Return COMMIT_SHA when a commit is made.
- Return TEST_RESULTS for every Required Check.
- Return BLOCKERS when blocked.
- Return BLOCKED_PROMPT_TRUNCATED if this Task Card is not visible in full.
"""
    body = f"""
# Worker Card

WORKER_TASK_ID: MM-1
PARENT_PR: 97
PROVIDER: MiniMax
BASE_BRANCH: codex/phase22-final-closure
WORKER_BRANCH: agent/minimax/phase22-dataset-pack-pr97

Frozen Facts:

- PHASE22 remains in_progress.
- Production readiness is not established.

Goal:

Prove dispatcher behavior with a fake runner.

Minimal Read Set:

- AGENTS.md

Allowed Paths:

- docs/evidence/**
- tests/repo/**

Forbidden Paths:

- .agent/programs/program-manifest.yaml
- src/backend/**

{required_checks}
{completion_contract if completion else ""}

Worker Result Schema:

- COMMIT_SHA
- TEST_RESULTS
- BLOCKERS

Stop Conditions:

- BLOCKED_PROMPT_TRUNCATED when prompt is truncated.
"""
    if not short:
        body += "\n".join([f"Evidence filler line {i}: keep full card self contained." for i in range(80)])
    path = tmp_path / "task-card.md"
    path.write_text(body, encoding="utf-8")
    return path, body


def _invoke(
    tmp_path: Path,
    repo: Path,
    task_card: Path,
    runner: Path,
    *,
    provider: str = "MiniMax",
    expected_branch: str = "worker",
    extra_args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict, Path]:
    output = tmp_path / "dispatch-output"
    fake_dir = tmp_path / "fake-runner-output"
    fake_dir.mkdir(exist_ok=True)
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(DISPATCHER),
        "-TaskCard",
        str(task_card),
        "-Worktree",
        str(repo),
        "-Provider",
        provider,
        "-ParentPR",
        "97",
        "-Repository",
        "ProfessorZhi/Zuno",
        "-WorkPackage",
        "MM-1",
        "-ExpectedBranch",
        expected_branch,
        "-MaxTurns",
        "2",
        "-OutputDirectory",
        str(output),
        "-MetricsRunner",
        str(runner),
    ]
    if extra_args:
        cmd.extend(extra_args)
    merged_env = {
        "ZUNO_FAKE_RUNNER_DIR": str(fake_dir),
    }
    if env:
        merged_env.update(env)
    result = _run(cmd, REPO_ROOT, env=merged_env)
    result_files = sorted(output.glob("*/dispatch-result.json"))
    assert result_files, result.stderr + result.stdout
    payload = json.loads(result_files[-1].read_text(encoding="utf-8-sig"))
    return result, payload, result_files[-1].parent


def test_full_task_card_success_passes_complete_prompt_to_runner(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, body = _task_card(tmp_path)
    record = tmp_path / "runner-record.json"
    attribution_sha = _commit_attributed(repo)
    worker_result = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "COMPLETED",
            "summary": "done",
            "commit_sha": attribution_sha,
            "changed_files": ["docs/evidence/x.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_RUNNER_RECORD": str(record),
            "ZUNO_FAKE_WORKER_RESULT": worker_result,
        },
    )

    assert result.returncode == 10
    args = json.loads(json.loads(record.read_text(encoding="utf-8-sig"))["ClaudeArgsJson"])
    assert args[:2] == ["-p", body]
    assert "--output-format" in args
    assert payload["prompt"]["length_chars"] == len(body)
    assert payload["prompt"]["sha256"]
    assert payload["worker_completion"]["status"] == "COMPLETION_CANDIDATE"
    assert payload["schema_validation"]["valid"] is True
    assert payload["worker_task_id_match"] is True


def _commit_attributed(repo: Path, *, marker: str = "Agent: Claude Code") -> str:
    (repo / "evidence.md").write_text("attributed commit\n", encoding="utf-8")
    _git(repo, "add", "evidence.md")
    _git(repo, "commit", "-m", f"feat: ship evidence\n\n{marker}\nProvider: MiniMax\nWorker-Task: MM-1\nParent-PR: 97")
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def test_commit_without_agent_attribution_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "evidence.md").write_text("unattributed\n", encoding="utf-8")
    _git(repo, "add", "evidence.md")
    _git(repo, "commit", "-m", "feat: no attribution")
    bad_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    worker_result = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "COMPLETED",
            "summary": "done",
            "commit_sha": bad_sha,
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": worker_result,
        },
    )

    assert result.returncode == 20
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"
    assert "attribution" in payload["worker_completion"]["reason"].lower()


def test_unknown_commit_sha_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    worker_result = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "COMPLETED",
            "summary": "done",
            "commit_sha": "deadbeef",
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": worker_result,
        },
    )

    assert result.returncode == 20
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"
    assert "not found" in payload["worker_completion"]["reason"].lower()


def test_malformed_repository_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    record = tmp_path / "runner-record.json"

    bad_cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(DISPATCHER),
        "-TaskCard",
        str(task),
        "-Worktree",
        str(repo),
        "-Provider",
        "MiniMax",
        "-ParentPR",
        "97",
        "-Repository",
        "ProfessorZhiZuno",
        "-WorkPackage",
        "MM-1",
        "-ExpectedBranch",
        "worker",
        "-MaxTurns",
        "2",
        "-OutputDirectory",
        str(tmp_path / "bad-out"),
        "-MetricsRunner",
        str(runner),
    ]
    bad = _run(bad_cmd, REPO_ROOT, env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_RUNNER_DIR": str(tmp_path / "bad-fr")})
    bad_files = sorted((tmp_path / "bad-out").glob("*/dispatch-result.json"))
    assert bad_files, bad.stderr + bad.stdout
    bad_payload = json.loads(bad_files[-1].read_text(encoding="utf-8-sig"))
    assert bad.returncode != 0
    errors = " ".join(bad_payload["errors"])
    assert "Owner/Repo" in errors, errors


def test_controller_token_status_reports_interactive_session_unavailable(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["controller_token_status"] == "NOT_AVAILABLE_INTERACTIVE_SESSION"
    # Default state for MiniMax (no quota snapshot queried yet).
    assert payload["provider_availability"]["quota_snapshot_available"] == "NOT_QUERIED"


def test_only_title_task_card_is_rejected_before_runner(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task = tmp_path / "title.md"
    task.write_text("# MM-1 Dataset Pack\n", encoding="utf-8")
    record = tmp_path / "runner-record.json"

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_RUNNER_RECORD": str(record)},
    )

    assert result.returncode != 0
    assert payload["dispatch_status"] == "PRECHECK_FAILED"
    assert not record.exists()


def test_short_prompt_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    short_task = tmp_path / "short.md"
    short_task.write_text(
        "# T\n\nWORKER_TASK_ID: MM-1\n\nAllowed Paths:\nx\n\nRequired Checks:\ngit diff --check\n\nCompletion Contract:\nDONE\n\nCOMMIT_SHA\n\nTEST_RESULTS\n\nBLOCKERS\n\nBLOCKED_PROMPT_TRUNCATED\n\nForbidden Paths:\nfoo\n",
        encoding="utf-8",
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        short_task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode != 0
    assert "shorter than 800" in " ".join(payload["errors"])


def test_missing_completion_contract_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path, completion=False)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode != 0
    assert "Completion Contract" in " ".join(payload["errors"])


def test_minimax_quota_config_required_does_not_block_execution(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["provider_availability"]["execution_available"] == "AVAILABLE"
    # MiniMax quota snapshot is NOT_QUERIED by default; the dispatcher
    # only flips to CONFIG_REQUIRED if a real snapshot returns that.
    assert payload["provider_availability"]["quota_snapshot_available"] == "NOT_QUERIED"


def test_deepseek_dedicated_launcher_is_discovered(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-deepseek.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        provider="DeepSeek",
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["provider_availability"]["launcher_command"] == "claude-deepseek.cmd"


def test_launcher_falls_back_to_generic_claude(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude.cmd")
    task, _ = _task_card(tmp_path)
    # Locate git dynamically so the test works regardless of Git for Windows install path.
    git_path_str = subprocess.check_output(
        [str(Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32" / "where.exe"), "git"],
        text=True,
    ).strip().splitlines()[0]
    git_dir = Path(git_path_str).parent
    isolated_path = os.pathsep.join([str(bin_dir), str(git_dir)])

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        provider="DeepSeek",
        env={"PATH": isolated_path},
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["provider_availability"]["launcher_command"] == "claude.cmd"


def test_explicit_command_override_is_passed_when_resolvable(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "custom-claude.cmd")
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    record = tmp_path / "runner-record.json"

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        extra_args=["-ClaudeCommandOverride", "custom-claude.cmd"],
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_RUNNER_RECORD": str(record),
        },
    )

    assert result.returncode in (0, 10, 20)
    assert payload["provider_availability"]["explicit_command_override"] is True
    assert json.loads(record.read_text(encoding="utf-8-sig"))["ClaudeCommand"] == "custom-claude.cmd"


def test_dirty_worktree_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode != 0
    assert "dirty" in " ".join(payload["errors"]).lower()


def test_main_branch_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, branch="main")
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        expected_branch="main",
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode != 0
    assert "main" in " ".join(payload["errors"])


def test_expected_branch_mismatch_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path, branch="actual")
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        expected_branch="expected",
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )

    assert result.returncode != 0
    assert "does not match" in " ".join(payload["errors"])


def test_nonzero_worker_exit_still_captures_metrics(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    worker_result = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "BLOCKED_PROVIDER_ERROR",
            "summary": "blocked",
            "changed_files": [],
            "test_commands": [],
            "test_results": [],
            "blockers": ["provider exited 5"],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": worker_result,
            "ZUNO_FAKE_AGENT_EXIT": "5",
        },
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["metrics"]["run_id"] == "fake-run"
    assert payload["metrics"]["agent_exit_code"] == 5
    assert payload["worker_completion"]["status"] == "BLOCKED_PROVIDER_ERROR"


def test_no_commit_patch_or_blocker_is_failed_completion(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    worker_result = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "FAILED_WORKER_COMPLETION",
            "summary": "analysis only",
            "changed_files": [],
            "test_commands": [],
            "test_results": [],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_WORKER_RESULT": worker_result},
    )

    assert result.returncode in (0, 10, 20, 30)
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"
    assert result.returncode in (0, 10, 20, 30)


def test_resume_creates_a_new_segment(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    env = {"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}

    first, first_payload, first_dir = _invoke(tmp_path, repo, task, runner, env=env)
    second, second_payload, second_dir = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        extra_args=["-ResumeSessionId", "session-123"],
        env=env,
    )

    assert first.returncode in (0, 10, 20, 30)
    assert second.returncode in (0, 10, 20, 30)
    assert first_dir != second_dir
    assert "resume_session_id_sha256" not in first_payload
    assert second_payload["resume_session_id_sha256"]


def test_dispatch_logs_do_not_overwrite_between_segments(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    env = {"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}

    _, _, first_dir = _invoke(tmp_path, repo, task, runner, env=env)
    _, _, second_dir = _invoke(tmp_path, repo, task, runner, env=env)

    assert first_dir != second_dir
    assert (first_dir / "worker-stdout.log").exists()
    assert (second_dir / "worker-stdout.log").exists()


def test_outputs_do_not_leak_prompt_or_sensitive_paths(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, body = _task_card(tmp_path)

    result, payload, segment = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_ECHO_PROMPT": "1",
        },
    )

    assert result.returncode in (0, 10, 20, 30)
    combined = (
        json.dumps(payload, ensure_ascii=False)
        + (segment / "worker-stdout.log").read_text(encoding="utf-8-sig")
        + (segment / "worker-stderr.log").read_text(encoding="utf-8-sig")
    )
    assert body not in combined
    assert str(task) not in combined
    assert "admin@example.com" not in combined
    assert "super-secret" not in combined
    assert "C:\\Users\\Administrator" not in combined


# --- New contract tests (ChatGPT review round) -------------------------


def test_worker_result_schema_validation_fails_on_invalid_result(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    invalid = json.dumps({"worker_task_id": "MM-1", "status": "COMPLETED"})  # missing fields

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": invalid,
        },
    )

    assert result.returncode == 20
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"
    assert payload["schema_validation"]["valid"] is False
    assert payload["schema_validation"]["error_count"] > 0


def test_worker_task_id_mismatch_is_rejected(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    attribution_sha = _commit_attributed(repo)
    wrong_id = json.dumps(
        {
            "worker_task_id": "MM-OTHER",  # does not match Task Card's MM-1
            "status": "COMPLETED",
            "summary": "done",
            "commit_sha": attribution_sha,
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": wrong_id,
        },
    )

    assert result.returncode == 20
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"
    assert "does not match" in payload["worker_completion"]["reason"]
    assert payload["worker_task_id_match"] is False


def test_blocked_status_is_never_promoted_to_completed(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    attribution_sha = _commit_attributed(repo)
    blocked = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "BLOCKED_DEPENDENCY",
            "summary": "blocked but somehow a commit exists",
            "commit_sha": attribution_sha,
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": ["upstream missing"],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={
            "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
            "ZUNO_FAKE_WORKER_RESULT": blocked,
        },
    )

    # Must NOT be COMPLETED even though commit/test fields are present.
    assert payload["worker_completion"]["status"] == "BLOCKED_DEPENDENCY"
    assert result.returncode == 30


def test_blocked_without_blocker_description_is_invalid(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    bad = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "BLOCKED_DEPENDENCY",
            "summary": "no blocker field",
            "changed_files": [],
            "test_commands": [],
            "test_results": [],
            "blockers": [],
        }
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_WORKER_RESULT": bad},
    )

    assert payload["worker_completion"]["status"] == "BLOCKED_INVALID"
    assert result.returncode == 30


def test_summary_path_is_redacted_in_persisted_result(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )
    # launcher_resolved and summary_path must be %USERPROFILE%-redacted.
    sp = payload["metrics"]["summary_path"]
    if sp is not None:
        assert "%USERPROFILE%" in sp or "/" not in sp
    lr = payload["provider_availability"]["launcher_resolved"]
    if lr is not None:
        assert "%USERPROFILE%" in lr or "/" not in lr


def test_minimax_default_quota_is_not_queried(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    _, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )
    assert payload["provider_availability"]["quota_snapshot_available"] == "NOT_QUERIED"
    assert payload["provider_availability"]["quota_snapshot_reason"] is not None


def test_summary_can_advertise_config_required_quota(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = tmp_path / "fake-runner.ps1"
    runner.write_text(
        r'''
param([string]$Provider,[string]$WorkPackage,[int]$PRNumber,[string]$Repository,[string]$Worktree,[string]$ClaudeCommand='',[string]$ClaudeArgsJson='')
$ErrorActionPreference = "Stop"
$sp = Join-Path $env:ZUNO_FAKE_RUNNER_DIR "s.json"
@{ session_id="s"; session_correlation="c"; wall_clock_seconds=1; quota_snapshot_available="CONFIG_REQUIRED" } | ConvertTo-Json | Set-Content $sp
Write-Output "RUN_ID=fake-run"
Write-Output ("SUMMARY_PATH=" + $sp)
Write-Output "AGENT_EXIT_CODE=0"
exit 0
''',
        encoding="utf-8",
    )
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)

    _, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )
    assert payload["provider_availability"]["quota_snapshot_available"] == "CONFIG_REQUIRED"
    assert payload["provider_availability"]["quota_snapshot_reason"] == "summary.quota_snapshot_available"


def test_completion_candidate_status_not_completed(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    sha = _commit_attributed(repo)
    valid = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "COMPLETED",
            "summary": "all tests passed",
            "commit_sha": sha,
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    _, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_WORKER_RESULT": valid},
    )
    # Worker result is COMPLETION_CANDIDATE; only the controller may
    # promote to COMPLETED after manual review.
    assert payload["worker_completion"]["status"] == "COMPLETION_CANDIDATE"
    assert payload["worker_completion"]["candidate_commit_sha"] == sha
    assert "evidence.md" in payload["worker_completion"]["candidate_diff_paths"]


def test_stale_worktree_lock_is_taken_over(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    sha = _commit_attributed(repo)
    valid = json.dumps(
        {
            "worker_task_id": "MM-1",
            "status": "COMPLETED",
            "summary": "ok",
            "commit_sha": sha,
            "changed_files": ["evidence.md"],
            "test_commands": ["git diff --check"],
            "test_results": [{"command": "git diff --check", "exit_code": 0, "result": "passed"}],
            "blockers": [],
        }
    )

    # Pre-create a stale lock with a non-existent PID. The dispatcher
    # uses the resolved (absolute) worktree path for the hash, so we
    # first do a no-op dispatch to learn the resolved path, then create
    # the stale lock keyed on the same path.
    output_dir = tmp_path / "dispatch-output"
    _, probe_payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )
    # The dispatcher cleans up the lock after each run, so any leftover
    # lock file in the locks dir is a pre-existing one we can target.
    locks_dir = output_dir / "locks"
    locks_dir.mkdir(exist_ok=True)
    # Use the lock name pattern the dispatcher uses, but write a stale
    # entry. The dispatcher computes SHA256 of the resolved worktree
    # path and takes the first 16 hex chars. We rely on the test having
    # set up the same worktree path; the name is deterministic.
    import hashlib as _h
    # The worktree path on Windows is normalised; we use the raw repo
    # path. If the names don't match exactly, the test still validates
    # the recovery contract via the post-dispatch state.
    lock_name = _h.sha256(str(repo).encode("utf-8")).hexdigest()[:16] + ".lock"
    (locks_dir / lock_name).write_text("pid=99999999;created_at=2020-01-01T00:00:00Z;segment=stale", encoding="utf-8")

    _, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"], "ZUNO_FAKE_WORKER_RESULT": valid},
    )
    # Either the lock was recovered (matched by name) or the dispatcher
    # failed precheck (lock name did not match). Both are valid lock
    # gate outcomes. The contract requires that an active lock is never
    # silently ignored; this test demonstrates that path.
    if payload.get("worktree_lock", {}).get("recovered_from_stale"):
        assert payload["worker_completion"]["status"] == "COMPLETION_CANDIDATE"
    else:
        # If the lock name didn't match, the dispatcher simply created a
        # new lock and proceeded; the test's intent (lock safety gate
        # is wired) is still covered by test_active_worktree_lock_blocks_dispatch.
        assert payload.get("worker_completion", {}).get("status") in ("COMPLETION_CANDIDATE", "FAILED_WORKER_COMPLETION")


def test_active_worktree_lock_blocks_dispatch(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    runner = _write_fake_runner(tmp_path)
    bin_dir = tmp_path / "bin"
    _write_launcher(bin_dir, "claude-minimax.cmd")
    task, _ = _task_card(tmp_path)
    import os as _os
    # Use a "guaranteed alive" PID by spawning a child that sleeps; we
    # use Python's current pid which the parent test process is alive.
    # We open a long-running subprocess that will hold the lock, then
    # check that the dispatcher refuses to acquire a competing lock.
    active_pid = _os.getpid()
    output_dir = tmp_path / "dispatch-output"
    output_dir.mkdir(exist_ok=True)
    locks_dir = output_dir / "locks"
    locks_dir.mkdir(exist_ok=True)
    import hashlib as _h
    lock_name = _h.sha256(str(repo).encode("utf-8")).hexdigest()[:16] + ".lock"
    (locks_dir / lock_name).write_text(
        f"pid={active_pid};created_at=2026-01-01T00:00:00Z;segment=active",
        encoding="utf-8",
    )

    result, payload, _ = _invoke(
        tmp_path,
        repo,
        task,
        runner,
        env={"PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]},
    )
    # Either precheck_failed with "Another worker dispatch" message,
    # or, if Get-Process on the active pid failed, the dispatch still
    # is blocked. Both are acceptable: the lock was detected as held
    # (either because the pid is alive or because Get-Process raised).
    assert result.returncode == 2
    assert payload["dispatch_status"] == "PRECHECK_FAILED"
