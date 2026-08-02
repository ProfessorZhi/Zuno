[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TaskCard,

    [Parameter(Mandatory = $true)]
    [string]$Worktree,

    [Parameter(Mandatory = $true)]
    [ValidateSet("MiniMax", "DeepSeek")]
    [string]$Provider,

    [Parameter(Mandatory = $true)]
    [string]$ParentPR,

    [Parameter(Mandatory = $true)]
    [string]$Repository,

    [Parameter(Mandatory = $true)]
    [string]$WorkPackage,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedBranch,

    [Parameter(Mandatory = $true)]
    [int]$MaxTurns,

    [string]$ResumeSessionId = "",

    [string]$OutputDirectory = ".local\phase22-worker-dispatch",

    [string]$ClaudeCommandOverride = "",

    [string]$MetricsRunner = "F:\funny_project\agent-metrics-workspace\agent-metrics-collector\scripts\run-claude-with-metrics.ps1"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function ConvertTo-SafeName([string]$Value) {
    $safe = $Value -replace '[^A-Za-z0-9._-]', '-'
    if ([string]::IsNullOrWhiteSpace($safe)) { return "unknown" }
    return $safe
}

function Get-Sha256Hex([string]$Value) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Value)
    $hash = [Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
    return (($hash | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Read-Utf8Strict([string]$Path) {
    $encoding = [Text.UTF8Encoding]::new($false, $true)
    return [IO.File]::ReadAllText($Path, $encoding)
}

function Invoke-Git([string]$Repo, [string[]]$Arguments) {
    $output = & git -C $Repo @Arguments 2>&1
    return @{
        exit_code = $LASTEXITCODE
        output = (($output | Out-String).Trim())
    }
}

function Find-ProviderLauncher([string]$ProviderName) {
    if ($ProviderName -eq "DeepSeek") {
        $candidates = @("claude-deepseek.cmd", "claude-deepseek", "claude.cmd", "claude")
    } else {
        $candidates = @("claude-minimax.cmd", "claude-minimax", "claude.cmd", "claude")
    }
    foreach ($candidate in $candidates) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cmd) {
            $resolved = $candidate
            if ($cmd.Source) { $resolved = [string]$cmd.Source }
            elseif ($cmd.Definition) { $resolved = [string]$cmd.Definition }
            elseif ($cmd.Path) { $resolved = [string]$cmd.Path }
            return @{
                command = $candidate
                resolved = $resolved
                candidates = $candidates
            }
        }
    }
    return @{
        command = $null
        resolved = $null
        candidates = $candidates
    }
}

function Redact-Text([string]$Text, [string]$Prompt, [string]$TaskCardPath) {
    if ($null -eq $Text) { return "" }
    $redacted = [string]$Text
    if (-not [string]::IsNullOrEmpty($Prompt)) {
        $redacted = $redacted.Replace($Prompt, "[REDACTED_PROMPT]")
    }
    if (-not [string]::IsNullOrWhiteSpace($TaskCardPath)) {
        $redacted = $redacted.Replace($TaskCardPath, "[REDACTED_TASK_CARD_PATH]")
    }
    if (-not [string]::IsNullOrWhiteSpace($HOME)) {
        $redacted = $redacted.Replace($HOME, "%USERPROFILE%")
    }
    $redacted = $redacted -replace '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[REDACTED_EMAIL]'
    $secretPattern = "(?i)(api[_-]?key|token|secret|password)[`"']?\s*[:=]\s*[`"']?[^`"',\s}]+"
    $redacted = $redacted -replace $secretPattern, '$1=[REDACTED_SECRET]'
    return $redacted
}

function Write-DispatchResult([string]$Path, [hashtable]$Result) {
    $json = $Result | ConvertTo-Json -Depth 20
    Set-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function ConvertTo-ReportPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $Path }
    if (-not [string]::IsNullOrWhiteSpace($HOME)) {
        return ([string]$Path).Replace($HOME, "%USERPROFILE%")
    }
    return $Path
}

function Get-WorkerResult([string]$SanitizedStdout) {
    foreach ($line in ($SanitizedStdout -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith("WORKER_RESULT_JSON=")) {
            $payload = $trimmed.Substring("WORKER_RESULT_JSON=".Length)
            try { return ($payload | ConvertFrom-Json -ErrorAction Stop) } catch { return $null }
        }
    }
    return $null
}

function Test-WorkerCompletion([object]$WorkerResult, [bool]$WorktreeCleanAfter, [string]$Worktree, [string]$CommitAttributionMarker = "Agent: Claude Code") {
    if (-not $WorktreeCleanAfter) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker left uncommitted changes"
        }
    }
    if ($null -eq $WorkerResult) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "missing worker result"
        }
    }

    $status = ""
    if ($WorkerResult.PSObject.Properties.Name -contains "status") { $status = [string]$WorkerResult.status }
    $blockers = $null
    if ($WorkerResult.PSObject.Properties.Name -contains "blockers") { $blockers = $WorkerResult.blockers }
    $hasBlocker = $false
    if ($null -ne $blockers) {
        if ($blockers -is [array]) { $hasBlocker = @($blockers).Count -gt 0 }
        else { $hasBlocker = -not [string]::IsNullOrWhiteSpace([string]$blockers) }
    }

    $hasCommit = ($WorkerResult.PSObject.Properties.Name -contains "commit_sha") -and ([string]$WorkerResult.commit_sha -match '^[0-9a-f]{7,40}$')
    $hasChanged = ($WorkerResult.PSObject.Properties.Name -contains "changed_files") -and (@($WorkerResult.changed_files).Count -gt 0)
    $hasCommands = ($WorkerResult.PSObject.Properties.Name -contains "test_commands") -and (@($WorkerResult.test_commands).Count -gt 0)
    $hasResults = ($WorkerResult.PSObject.Properties.Name -contains "test_results") -and (@($WorkerResult.test_results).Count -gt 0)
    if ($hasCommit -and $hasChanged -and $hasCommands -and $hasResults) {
        if (-not [string]::IsNullOrWhiteSpace($Worktree)) {
            $commitBody = Invoke-Git $Worktree @("log", "-1", "--format=%B", $WorkerResult.commit_sha)
            if ($commitBody.exit_code -ne 0) {
                return @{
                    status = "FAILED_WORKER_COMPLETION"
                    reason = "commit_sha not found in worktree git log"
                }
            }
            if ($commitBody.output -notmatch [regex]::Escape($CommitAttributionMarker)) {
                return @{
                    status = "FAILED_WORKER_COMPLETION"
                    reason = "commit body missing required Agent: Claude Code attribution"
                }
            }
        }
        return @{
            status = "COMPLETED"
            reason = "commit, changed files, tests and clean worktree were reported"
        }
    }

    $hasPatch = ($WorkerResult.PSObject.Properties.Name -contains "patch") -and (-not [string]::IsNullOrWhiteSpace([string]$WorkerResult.patch))
    $hasEvidence = ($WorkerResult.PSObject.Properties.Name -contains "evidence") -and (@($WorkerResult.evidence).Count -gt 0)
    if (($hasPatch -or $hasEvidence) -and $hasBlocker) {
        return @{
            status = "REVIEWED_PARTIAL"
            reason = "patch/evidence with exact blocker requires Codex review"
        }
    }

    if ($status.StartsWith("BLOCKED_") -and $hasBlocker) {
        return @{
            status = $status
            reason = "worker reported exact blocker and clean worktree"
        }
    }

    return @{
        status = "FAILED_WORKER_COMPLETION"
        reason = "worker result did not contain commit, patch/evidence, or exact blocker"
    }
}

function New-ResultBase([string]$SegmentDir, [string]$TaskId) {
    return @{
        schema_version = "1.0"
        dispatcher = "dispatch_claude_worker.ps1"
        dispatch_status = "INITIALIZED"
        task_id = $TaskId
        provider = $Provider
        parent_pr = $ParentPR
        repository = $Repository
        work_package = $WorkPackage
        expected_branch = $ExpectedBranch
        segment_dir = (ConvertTo-ReportPath $SegmentDir)
        controller_token_status = "NOT_AVAILABLE_INTERACTIVE_SESSION"
        prompt = @{
            sha256 = $null
            length_chars = 0
        }
        gates = @{}
        provider_availability = @{
            execution_available = "UNKNOWN"
            quota_snapshot_available = "UNKNOWN"
            launcher_command = $null
            launcher_resolved = $null
            explicit_command_override = $false
        }
        metrics = @{
            run_id = $null
            summary_path = $null
            agent_exit_code = $null
            session_id = $null
            session_correlation = $null
            wall_clock = $null
            process_seconds = $null
            token_buckets = $null
            api_equivalent_cost = $null
        }
        worker_completion = @{
            status = "NOT_RUN"
            reason = $null
        }
        logs = @{
            stdout = "worker-stdout.log"
            stderr = "worker-stderr.log"
        }
        errors = @()
    }
}

$outputRoot = $OutputDirectory
if (-not [IO.Path]::IsPathRooted($outputRoot)) {
    $outputRoot = Join-Path (Get-Location) $outputRoot
}
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null
$segmentName = "{0}-{1}-{2}" -f (Get-Date -Format "yyyyMMddTHHmmssfff"), (ConvertTo-SafeName $WorkPackage), ([Guid]::NewGuid().ToString("N").Substring(0, 12))
$segmentDir = Join-Path $outputRoot $segmentName
New-Item -ItemType Directory -Force -Path $segmentDir | Out-Null
$resultPath = Join-Path $segmentDir "dispatch-result.json"
$stdoutPath = Join-Path $segmentDir "worker-stdout.log"
$stderrPath = Join-Path $segmentDir "worker-stderr.log"
$result = New-ResultBase -SegmentDir $segmentDir -TaskId "UNKNOWN"
$lockStream = $null
$lockPath = $null
$prompt = ""
$taskCardResolved = ""

try {
    if ($MaxTurns -lt 1) { throw "MaxTurns must be greater than zero." }
    if (-not (Test-Path -LiteralPath $TaskCard -PathType Leaf)) { throw "Task Card does not exist." }
    $taskCardResolved = (Resolve-Path -LiteralPath $TaskCard).Path
    $prompt = Read-Utf8Strict $taskCardResolved
    $result.prompt.length_chars = $prompt.Length
    $result.prompt.sha256 = Get-Sha256Hex $prompt
    if ($prompt.Length -lt 800) { throw "Task Card prompt is shorter than 800 characters." }

    $taskIdMatch = [regex]::Match($prompt, '(?im)^\s*WORKER_TASK_ID\s*:\s*([A-Za-z0-9._-]+)\s*$')
    if (-not $taskIdMatch.Success) { throw "Task Card is missing WORKER_TASK_ID." }
    $result.task_id = $taskIdMatch.Groups[1].Value

    $requiredPatterns = @(
        @{ name = "Allowed Paths"; pattern = '(?im)^\s*Allowed Paths\s*:' },
        @{ name = "Required Checks"; pattern = '(?im)^\s*Required Checks\s*:' },
        @{ name = "Completion Contract"; pattern = '(?im)^\s*Completion Contract\s*:' },
        @{ name = "COMMIT_SHA"; pattern = '(?i)COMMIT_SHA' },
        @{ name = "TEST_RESULTS"; pattern = '(?i)TEST_RESULTS' },
        @{ name = "BLOCKERS"; pattern = '(?i)BLOCKERS' },
        @{ name = "BLOCKED_PROMPT_TRUNCATED"; pattern = '(?i)BLOCKED_PROMPT_TRUNCATED' }
    )
    foreach ($item in $requiredPatterns) {
        if ($prompt -notmatch $item.pattern) { throw ("Task Card is missing " + $item.name + ".") }
    }
    if (($prompt -notmatch '(?im)^\s*Forbidden Paths\s*:') -and ($prompt -notmatch '(?i)no-governance-write')) {
        throw "Task Card is missing Forbidden Paths or no-governance-write."
    }
    $result.gates.task_card = "PASS"

    if (-not (Test-Path -LiteralPath $MetricsRunner -PathType Leaf)) { throw "Metrics runner does not exist." }
    if (-not (Test-Path -LiteralPath $Worktree -PathType Container)) { throw "Worktree does not exist." }
    $worktreeResolved = (Resolve-Path -LiteralPath $Worktree).Path
    $inside = Invoke-Git $worktreeResolved @("rev-parse", "--is-inside-work-tree")
    if ($inside.exit_code -ne 0 -or $inside.output -ne "true") { throw "Worktree is not a git repository." }
    $branch = Invoke-Git $worktreeResolved @("branch", "--show-current")
    if ($branch.exit_code -ne 0 -or [string]::IsNullOrWhiteSpace($branch.output)) { throw "Unable to parse worktree branch." }
    if ($branch.output -ne $ExpectedBranch) { throw "Worktree branch '$($branch.output)' does not match ExpectedBranch '$ExpectedBranch'." }
    if ($branch.output -eq "main") { throw "Worker dispatch is forbidden on main." }
    $head = Invoke-Git $worktreeResolved @("rev-parse", "HEAD")
    if ($head.exit_code -ne 0 -or $head.output -notmatch '^[0-9a-f]{40}$') { throw "Unable to parse worktree HEAD." }
    if ([string]::IsNullOrWhiteSpace($Repository)) { throw "Repository is required." }
    if ($Repository -notmatch '^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$') { throw "Repository must be in 'Owner/Repo' format." }
    if ($ParentPR -notmatch '^\d+$') { throw "ParentPR must be numeric." }
    $dirty = Invoke-Git $worktreeResolved @("status", "--porcelain")
    if ($dirty.exit_code -ne 0) { throw "Unable to inspect worktree status." }
    if (-not [string]::IsNullOrWhiteSpace($dirty.output)) { throw "Worktree is dirty; worker dispatch refused." }

    $locksDir = Join-Path $outputRoot "locks"
    New-Item -ItemType Directory -Force -Path $locksDir | Out-Null
    $lockName = (Get-Sha256Hex $worktreeResolved).Substring(0, 16) + ".lock"
    $lockPath = Join-Path $locksDir $lockName
    try {
        $lockStream = [IO.File]::Open($lockPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
        $lockBytes = [Text.Encoding]::UTF8.GetBytes(("pid={0};segment={1}" -f $PID, $segmentName))
        $lockStream.Write($lockBytes, 0, $lockBytes.Length)
        $lockStream.Flush()
    } catch {
        throw "Another worker dispatch is already using this worktree."
    }
    $result.gates.worktree = "PASS"

    $launcher = Find-ProviderLauncher $Provider
    $result.provider_availability.launcher_command = $launcher.command
    $result.provider_availability.launcher_resolved = $launcher.resolved
    if ($launcher.command) {
        $result.provider_availability.execution_available = "AVAILABLE"
    } else {
        throw ("No Claude launcher found for provider " + $Provider + ".")
    }
    if ($Provider -eq "MiniMax") {
        $result.provider_availability.quota_snapshot_available = "CONFIG_REQUIRED"
    } else {
        $result.provider_availability.quota_snapshot_available = "NOT_QUERIED"
    }

    $Prompt = Get-Content -LiteralPath $TaskCard -Raw
    $ClaudeArgsJson = ConvertTo-Json @(
      "-p",
      $Prompt,
      "--output-format",
      "stream-json",
      "--verbose",
      "--max-turns",
      "$MaxTurns"
    ) -Compress -Depth 8
    if (-not [string]::IsNullOrWhiteSpace($ResumeSessionId)) {
        $resumeArgs = @($ClaudeArgsJson | ConvertFrom-Json) + @("--resume", $ResumeSessionId)
        $ClaudeArgsJson = ConvertTo-Json $resumeArgs -Compress
        $result.resume_session_id_sha256 = Get-Sha256Hex $ResumeSessionId
    }

    $runnerArgs = @{
        Provider = $Provider
        WorkPackage = $WorkPackage
        PRNumber = $ParentPR
        Repository = $Repository
        Worktree = $worktreeResolved
        ClaudeArgsJson = $ClaudeArgsJson
    }
    if (-not [string]::IsNullOrWhiteSpace($ClaudeCommandOverride)) {
        $override = Get-Command $ClaudeCommandOverride -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $override) { throw "ClaudeCommandOverride was provided but could not be resolved by Get-Command." }
        $runnerArgs["ClaudeCommand"] = $ClaudeCommandOverride
        $result.provider_availability.explicit_command_override = $true
    }

    $rawStdout = (& $MetricsRunner @runnerArgs 2> $stderrPath) | Out-String
    $runnerExit = $LASTEXITCODE
    $sanitizedStdout = Redact-Text $rawStdout $prompt $taskCardResolved
    $rawStderr = ""
    if (Test-Path -LiteralPath $stderrPath) { $rawStderr = Get-Content -LiteralPath $stderrPath -Raw -Encoding UTF8 }
    $sanitizedStderr = Redact-Text $rawStderr $prompt $taskCardResolved
    Set-Content -LiteralPath $stdoutPath -Value $sanitizedStdout -Encoding UTF8
    Set-Content -LiteralPath $stderrPath -Value $sanitizedStderr -Encoding UTF8

    $result.dispatch_status = "DISPATCHED"
    $result.metrics.agent_exit_code = $runnerExit
    foreach ($line in ($sanitizedStdout -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith("RUN_ID=")) { $result.metrics.run_id = $trimmed.Substring("RUN_ID=".Length) }
        if ($trimmed.StartsWith("SUMMARY_PATH=")) { $result.metrics.summary_path = ConvertTo-ReportPath $trimmed.Substring("SUMMARY_PATH=".Length) }
        if ($trimmed.StartsWith("AGENT_EXIT_CODE=")) {
            $agentExitText = $trimmed.Substring("AGENT_EXIT_CODE=".Length)
            $parsedAgentExit = 0
            if ([int]::TryParse($agentExitText, [ref]$parsedAgentExit)) { $result.metrics.agent_exit_code = $parsedAgentExit }
        }
    }
    $rawSummaryPath = $null
    foreach ($line in ($sanitizedStdout -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith("SUMMARY_PATH=")) { $rawSummaryPath = $trimmed.Substring("SUMMARY_PATH=".Length) }
    }
    if ($rawSummaryPath -and (Test-Path -LiteralPath $rawSummaryPath -PathType Leaf)) {
        try {
            $summary = Get-Content -LiteralPath $rawSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop
            foreach ($name in @("session_id", "agent_session_id", "native_session_id")) {
                if (($summary.PSObject.Properties.Name -contains $name) -and $summary.$name) {
                    $result.metrics.session_id = [string]$summary.$name
                    break
                }
            }
            foreach ($name in @("session_correlation", "session_binding_status")) {
                if (($summary.PSObject.Properties.Name -contains $name) -and $summary.$name) {
                    $result.metrics.session_correlation = [string]$summary.$name
                    break
                }
            }
            foreach ($name in @("wall_clock", "wall_clock_seconds", "elapsed_seconds")) {
                if ($summary.PSObject.Properties.Name -contains $name) { $result.metrics.wall_clock = $summary.$name; break }
            }
            foreach ($name in @("process_seconds", "agent_process_seconds")) {
                if ($summary.PSObject.Properties.Name -contains $name) { $result.metrics.process_seconds = $summary.$name; break }
            }
            foreach ($name in @("token_buckets", "tokens")) {
                if ($summary.PSObject.Properties.Name -contains $name) { $result.metrics.token_buckets = $summary.$name; break }
            }
            foreach ($name in @("api_equivalent_cost", "api_equivalent_cost_usd", "cost")) {
                if ($summary.PSObject.Properties.Name -contains $name) { $result.metrics.api_equivalent_cost = $summary.$name; break }
            }
        } catch {
            $result.errors += "metrics summary could not be parsed"
        }
    }

    $afterDirty = Invoke-Git $worktreeResolved @("status", "--porcelain")
    $cleanAfter = ($afterDirty.exit_code -eq 0 -and [string]::IsNullOrWhiteSpace($afterDirty.output))
    $workerResult = Get-WorkerResult $sanitizedStdout
    $completion = Test-WorkerCompletion $workerResult $cleanAfter $worktreeResolved
    $result.worker_completion = $completion
    if ($runnerExit -ne 0 -and $completion.status -eq "COMPLETED") {
        $result.worker_completion = @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker process exited nonzero despite completed-looking result"
        }
    }
    Write-DispatchResult $resultPath $result
    Write-Output $resultPath
    exit 0
} catch {
    $result.dispatch_status = "PRECHECK_FAILED"
    $result.errors += $_.Exception.Message
    if (-not (Test-Path -LiteralPath $stdoutPath)) { Set-Content -LiteralPath $stdoutPath -Value "" -Encoding UTF8 }
    if (-not (Test-Path -LiteralPath $stderrPath)) { Set-Content -LiteralPath $stderrPath -Value "" -Encoding UTF8 }
    Write-DispatchResult $resultPath $result
    Write-Output $resultPath
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 2
} finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
        if ($lockPath -and (Test-Path -LiteralPath $lockPath)) {
            Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
        }
    }
}
