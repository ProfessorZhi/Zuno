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

    assert result.returncode == 0
    args = json.loads(json.loads(record.read_text(encoding="utf-8-sig"))["ClaudeArgsJson"])
    assert args[:2] == ["-p", body]
    assert "--output-format" in args
    assert payload["prompt"]["length_chars"] == len(body)
    assert payload["prompt"]["sha256"]
    assert payload["worker_completion"]["status"] == "COMPLETED"


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

    assert result.returncode == 0
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

    assert result.returncode == 0
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

    assert result.returncode == 0
    assert payload["controller_token_status"] == "NOT_AVAILABLE_INTERACTIVE_SESSION"


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

    assert result.returncode == 0
    assert payload["provider_availability"]["execution_available"] == "AVAILABLE"
    assert payload["provider_availability"]["quota_snapshot_available"] == "CONFIG_REQUIRED"


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

    assert result.returncode == 0
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

    assert result.returncode == 0
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

    assert result.returncode == 0
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

    assert result.returncode == 0
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

    assert result.returncode == 0
    assert payload["worker_completion"]["status"] == "FAILED_WORKER_COMPLETION"


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

    assert first.returncode == 0
    assert second.returncode == 0
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

    assert result.returncode == 0
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
