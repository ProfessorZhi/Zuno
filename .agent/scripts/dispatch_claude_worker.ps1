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

    [string]$MetricsRunner = "F:\funny_project\agent-metrics-workspace\agent-metrics-collector\scripts\run-claude-with-metrics.ps1",

    [string]$SchemaPath = ".agent\programs\worker-result.schema.json",

    [string]$WorkerResultSchemaName = "Zuno PHASE22 Claude Worker Result",

    [string]$CommitAttributionMarker = "Agent: Claude Code"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# Ensure the legacy JavaScriptSerializer is available for atomic JSON
# writes. PowerShell 5.1 ships on .NET Framework 4.x, which does not
# have System.Text.Json. We use JavaScriptSerializer because:
#   * it ships in-box via System.Web.Extensions
#   * it does not have the depth-truncation bug that ConvertTo-Json
#     has when a string value contains JSON-like text
#   * it produces a single-line UTF-16 string we can write atomically
try { Add-Type -AssemblyName System.Web.Extensions } catch { }
$__zunoJsonSerializer = $null
function Get-JsonSerializer {
    if ($null -eq $__zunoJsonSerializer) {
        $script:__zunoJsonSerializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
    }
    return $__zunoJsonSerializer
}

# Distinct exit codes (callers must read the contract, not guess).
# 0  : DISPATCH_OK and worker_completion.status == COMPLETED.
# 2  : PRECHECK_FAILED (gate rejected before metrics wrapper ran).
# 3  : RUNNER_FAILED (metrics wrapper itself failed; worker_completion
#      status will be FAILED_WORKER_COMPLETION or NOT_RUN).
# 10 : DISPATCH_OK with worker_completion.status == COMPLETION_CANDIDATE
#      (a Worker Result was reported; the Controller must review Diff,
#      Branch, Forbidden Paths and tests before accepting the candidate
#      as COMPLETED). This is the default successful exit when Worker
#      Result is a candidate, not an approval.
# 20 : DISPATCH_OK with worker_completion.status == FAILED_WORKER_COMPLETION.
# 30 : DISPATCH_OK with worker_completion.status starting with BLOCKED_.

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
    $exit = $LASTEXITCODE
    return @{
        exit_code = $exit
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

function ConvertTo-RedactedPath([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { return $null }
    $redacted = [string]$Path
    if (-not [string]::IsNullOrWhiteSpace($HOME)) {
        $redacted = $redacted.Replace($HOME, "%USERPROFILE%")
    }
    return $redacted
}

# Atomic JSON writer. Uses ConvertTo-Json with a high depth limit
# (PowerShell 5.1 compatible) and forces deterministic field ordering
# by converting the hashtable to PSCustomObject members. Writes
# UTF-8 with no BOM.
function Write-JsonAtomic([string]$Path, [hashtable]$Object) {
    $tempPath = "$Path.tmp"
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    $json = $Object | ConvertTo-Json -Depth 32 -Compress
    # PowerShell's ConvertTo-Json on hashtables preserves insertion
    # order; PSCustomObject fields are also iterated in declaration
    # order. The dispatcher builds the result hashtable in a stable
    # order, so this is sufficient for the contract.
    [System.IO.File]::WriteAllText($tempPath, $json, $utf8)
    Move-Item -LiteralPath $tempPath -Destination $Path -Force
}

# Lightweight JSON Schema validator (subset, sufficient for our schema).
# Supports: type, properties, required, additionalProperties, items,
# pattern, enum, allOf, if/then, minLength, minItems, maxItems.
function Test-JsonSchema {
    param(
        [Parameter(Mandatory = $true)] $Instance,
        [Parameter(Mandatory = $true)] $Schema,
        [string]$RootName = "root"
    )
    $errors = New-Object System.Collections.Generic.List[string]

    $refValue = $null
    if ($Schema.PSObject.Properties.Name -contains '$ref') {
        $refValue = $Schema.'$ref'
    }
    if ($null -ne $refValue) {
        $errors.Add("$RootName : `$ref is not supported by inline validator")
        return ,$errors
    }

    if ($Schema.PSObject.Properties.Name -contains 'type') {
        $expected = [string]$Schema.type
        $actualType = "unknown"
        if ($null -eq $Instance) {
            $actualType = "null"
        } elseif ($Instance -is [bool]) {
            $actualType = "boolean"
        } elseif ($Instance -is [int] -or $Instance -is [long] -or $Instance -is [double]) {
            $actualType = "number"
        } elseif ($Instance -is [string]) {
            $actualType = "string"
        } elseif ($Instance -is [System.Array] -or $Instance -is [System.Collections.IList]) {
            $actualType = "array"
        } elseif ($Instance -is [System.Collections.IDictionary]) {
            $actualType = "object"
        } else {
            $actualType = "object"
        }
        if ($expected -eq "integer" -and $actualType -ne "integer" -and $actualType -ne "number") {
            $errors.Add("$RootName : expected integer, got $actualType")
            return ,$errors
        }
        if ($expected -ne "integer" -and $expected -ne $actualType) {
            $errors.Add("$RootName : expected $expected, got $actualType")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'enum') {
        $match = $false
        foreach ($opt in $Schema.enum) {
            if ($Instance -eq $opt) { $match = $true; break }
        }
        if (-not $match) {
            $errors.Add("$RootName : value not in enum")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'pattern' -and $Instance -is [string]) {
        if (-not ([regex]::IsMatch($Instance, [string]$Schema.pattern))) {
            $errors.Add("$RootName : does not match pattern")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'minLength' -and $Instance -is [string]) {
        if ($Instance.Length -lt [int]$Schema.minLength) {
            $errors.Add("$RootName : shorter than minLength")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'minItems' -and ($Instance -is [System.Array] -or $Instance -is [System.Collections.IList])) {
        if (@($Instance).Count -lt [int]$Schema.minItems) {
            $errors.Add("$RootName : fewer than minItems")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'maxItems' -and ($Instance -is [System.Array] -or $Instance -is [System.Collections.IList])) {
        if (@($Instance).Count -gt [int]$Schema.maxItems) {
            $errors.Add("$RootName : more than maxItems")
            return ,$errors
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'required' -and ($Instance -is [System.Collections.IDictionary] -or $Instance.PSObject)) {
        foreach ($key in $Schema.required) {
            $hasIt = $false
            if ($Instance.PSObject.Properties.Name -contains $key) { $hasIt = $true }
            if (-not $hasIt) {
                $errors.Add("$RootName : missing required property '$key'")
            }
        }
        if ($errors.Count -gt 0) { return ,$errors }
    }

    if ($Schema.PSObject.Properties.Name -contains 'additionalProperties' -and ($Instance -is [System.Collections.IDictionary] -or $Instance.PSObject)) {
        if ($Schema.additionalProperties -eq $false) {
            $allowed = @()
            if ($Schema.PSObject.Properties.Name -contains 'properties') {
                $allowed = @($Schema.properties.PSObject.Properties.Name)
            }
            foreach ($prop in $Instance.PSObject.Properties.Name) {
                if ($allowed -notcontains $prop) {
                    $errors.Add("$RootName : unknown property '$prop'")
                }
            }
            if ($errors.Count -gt 0) { return ,$errors }
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'properties' -and ($Instance -is [System.Collections.IDictionary] -or $Instance.PSObject)) {
        foreach ($propName in $Schema.properties.PSObject.Properties.Name) {
            $propSchema = $Schema.properties.$propName
            if ($Instance.PSObject.Properties.Name -contains $propName) {
                $childErrors = Test-JsonSchema -Instance $Instance.$propName -Schema $propSchema -RootName "$RootName.$propName"
                foreach ($e in $childErrors) { $errors.Add($e) }
            }
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'items' -and ($Instance -is [System.Array] -or $Instance -is [System.Collections.IList])) {
        $idx = 0
        foreach ($item in $Instance) {
            $childErrors = Test-JsonSchema -Instance $item -Schema $Schema.items -RootName "$RootName[$idx]"
            foreach ($e in $childErrors) { $errors.Add($e) }
            $idx += 1
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'allOf') {
        foreach ($sub in $Schema.allOf) {
            $childErrors = Test-JsonSchema -Instance $Instance -Schema $sub -RootName $RootName
            foreach ($e in $childErrors) { $errors.Add($e) }
        }
    }

    if ($Schema.PSObject.Properties.Name -contains 'if') {
        # Evaluate the if branch: every key/value pair in 'properties' of
        # 'if' must match for the 'if' to be considered active.
        $ifActive = $true
        if ($Schema.if.PSObject.Properties.Name -contains 'properties') {
            foreach ($key in $Schema.if.properties.PSObject.Properties.Name) {
                $expected = $Schema.if.properties.$key
                $hasKey = $Instance.PSObject.Properties.Name -contains $key
                if ($expected.PSObject.Properties.Name -contains 'const') {
                    if (-not $hasKey -or $Instance.$key -ne $expected.const) {
                        $ifActive = $false
                        break
                    }
                } elseif ($expected.PSObject.Properties.Name -contains 'pattern') {
                    if ($hasKey -and $Instance.$key -is [string]) {
                        if (-not ([regex]::IsMatch($Instance.$key, [string]$expected.pattern))) {
                            $ifActive = $false
                            break
                        }
                    }
                }
            }
        }
        if ($ifActive -and $Schema.PSObject.Properties.Name -contains 'then') {
            $childErrors = Test-JsonSchema -Instance $Instance -Schema $Schema.then -RootName $RootName
            foreach ($e in $childErrors) { $errors.Add($e) }
        }
    }

    return ,$errors
}

function Get-WorkerResultRaw([string]$RawStdout) {
    foreach ($line in ($RawStdout -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith("WORKER_RESULT_JSON=")) {
            $payload = $trimmed.Substring("WORKER_RESULT_JSON=".Length)
            try { return ($payload | ConvertFrom-Json -ErrorAction Stop) } catch { return $null }
        }
    }
    return $null
}

# Decide the worker_completion status. This is the only place that
# produces the COMPLETED / COMPLETION_CANDIDATE / BLOCKED_* /
# FAILED_WORKER_COMPLETION decision. It is intentionally conservative:
# the Worker Result is never promoted to COMPLETED; the Controller
# performs the manual diff/branch/forbidden-paths review and emits
# COMPLETED via the dispatch-result.json contract.
function Get-WorkerCompletion {
    param(
        [object]$WorkerResult,
        [bool]$WorktreeCleanAfter,
        [string]$Worktree,
        [bool]$RunnerOk,
        [string]$ExpectedTaskId,
        [string]$CommitAttributionMarker
    )

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

    # BLOCKED_* must never be promoted.
    if ($status.StartsWith("BLOCKED_")) {
        if ($hasBlocker) {
            return @{ status = $status; reason = "worker reported exact blocker and clean worktree" }
        }
        return @{
            status = "BLOCKED_INVALID"
            reason = "status starts with BLOCKED_ but no blocker description"
        }
    }

    if ($status -ne "COMPLETED") {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker status '$status' is not a recognised completion marker"
        }
    }

    # Worker reports COMPLETED. Validate the data and produce a
    # COMPLETION_CANDIDATE; only the Controller's manual review of
    # diff / branch / forbidden-paths / test results can promote this
    # to COMPLETED in the final dispatch-result.json.
    $hasCommit = ($WorkerResult.PSObject.Properties.Name -contains "commit_sha") -and ([string]$WorkerResult.commit_sha -match '^[0-9a-f]{7,40}$')
    $hasChanged = ($WorkerResult.PSObject.Properties.Name -contains "changed_files") -and (@($WorkerResult.changed_files).Count -gt 0)
    $hasCommands = ($WorkerResult.PSObject.Properties.Name -contains "test_commands") -and (@($WorkerResult.test_commands).Count -gt 0)
    $hasResults = ($WorkerResult.PSObject.Properties.Name -contains "test_results") -and (@($WorkerResult.test_results).Count -gt 0)
    $hasTaskId = ($WorkerResult.PSObject.Properties.Name -contains "worker_task_id") -and (-not [string]::IsNullOrWhiteSpace([string]$WorkerResult.worker_task_id))

    if (-not $hasTaskId) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker result missing worker_task_id"
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($ExpectedTaskId) -and $WorkerResult.worker_task_id -ne $ExpectedTaskId) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker_task_id '$($WorkerResult.worker_task_id)' does not match expected '$ExpectedTaskId'"
        }
    }

    if (-not ($hasCommit -and $hasChanged -and $hasCommands -and $hasResults)) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "worker result missing commit_sha/changed_files/test_commands/test_results"
        }
    }

    if (-not $RunnerOk) {
        return @{
            status = "FAILED_WORKER_COMPLETION"
            reason = "metrics runner exited nonzero"
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($Worktree)) {
        try {
            $gitLogOutput = & git -C $Worktree log -1 --format=%B $WorkerResult.commit_sha 2>&1
        } catch {
            $gitLogOutput = @($_.Exception.Message)
        }
        $gitLogExit = $LASTEXITCODE
        $commitBodyText = (($gitLogOutput | Out-String).Trim())
        if ($gitLogExit -ne 0 -or [string]::IsNullOrWhiteSpace($commitBodyText)) {
            return @{
                status = "FAILED_WORKER_COMPLETION"
                reason = "commit_sha not found in worktree git log"
            }
        }
        if ($commitBodyText -notmatch [regex]::Escape($CommitAttributionMarker)) {
            return @{
                status = "FAILED_WORKER_COMPLETION"
                reason = "commit body missing required $CommitAttributionMarker attribution"
            }
        }
    }

    return @{
        status = "COMPLETION_CANDIDATE"
        reason = "worker reported COMPLETED; controller must review diff, branch, forbidden paths, and test results before promotion"
        candidate_diff_paths = @($WorkerResult.changed_files)
        candidate_commit_sha = [string]$WorkerResult.commit_sha
    }
}

function New-ResultBase([string]$SegmentDir, [string]$TaskId) {
    return @{
        schema_version = "1.1"
        dispatcher = "dispatch_claude_worker.ps1"
        schema_validation = $null
        dispatch_status = "INITIALIZED"
        task_id = $TaskId
        expected_task_id = $null
        worker_task_id_match = $null
        provider = $Provider
        parent_pr = $ParentPR
        repository = $Repository
        work_package = $WorkPackage
        expected_branch = $ExpectedBranch
        segment_dir = (ConvertTo-RedactedPath $SegmentDir)
        controller_token_status = "NOT_AVAILABLE_INTERACTIVE_SESSION"
        prompt = @{
            sha256 = $null
            length_chars = 0
        }
        gates = @{}
        provider_availability = @{
            execution_available = "UNKNOWN"
            quota_snapshot_available = "NOT_QUERIED"
            quota_snapshot_reason = $null
            launcher_command = $null
            launcher_resolved = $null
            explicit_command_override = $false
        }
        metrics = @{
            run_id = $null
            summary_path = $null
            summary_sha256 = $null
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
        worker_result_validation = @{
            schema_path = $null
            schema_title = $null
            errors = @()
        }
        logs = @{
            stdout = "worker-stdout.log"
            stderr = "worker-stderr.log"
        }
        errors = @()
        worktree_lock = @{
            lock_path = $null
            pid = $null
            created_at = $null
            recovered_from_stale = $false
        }
    }
}

function Test-PidAlive {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return $false }
    try {
        $proc = Get-Process -Id $ProcessId -ErrorAction Stop
        if ($null -eq $proc) { return $false }
        return -not $proc.HasExited
    } catch {
        return $false
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
$schemaAbsPath = $null
if (-not [IO.Path]::IsPathRooted($SchemaPath)) {
    $schemaAbsPath = Join-Path (Get-Location) $SchemaPath
} else {
    $schemaAbsPath = $SchemaPath
}
$schemaObj = $null
$schemaTitle = $null
$schemaErrors = New-Object System.Collections.Generic.List[string]
$result = New-ResultBase -SegmentDir $segmentDir -TaskId "UNKNOWN"
$result.worker_result_validation.schema_path = (ConvertTo-RedactedPath $schemaAbsPath)
$lockStream = $null
$lockPath = $null
$lockRecovered = $false
$prompt = ""
$promptNormalized = ""
$taskCardResolved = ""
$exitCode = 0
$expectedTaskId = $null

try {
    if ($MaxTurns -lt 1) { throw "MaxTurns must be greater than zero." }
    if (-not (Test-Path -LiteralPath $TaskCard -PathType Leaf)) { throw "Task Card does not exist." }
    $taskCardResolved = (Resolve-Path -LiteralPath $TaskCard).Path
    $prompt = Read-Utf8Strict $taskCardResolved
    $promptNormalized = $prompt -replace "`r`n", "`n" -replace "`r", "`n"
    $result.prompt.length_chars = $promptNormalized.Length
    $result.prompt.sha256 = Get-Sha256Hex $promptNormalized
    if ($prompt.Length -lt 800) { throw "Task Card prompt is shorter than 800 characters." }

    if (-not (Test-Path -LiteralPath $schemaAbsPath -PathType Leaf)) {
        throw "Worker result schema not found: $schemaAbsPath"
    }
    $schemaText = Read-Utf8Strict $schemaAbsPath
    $schemaObj = $schemaText | ConvertFrom-Json -ErrorAction Stop
    $schemaTitle = [string]$schemaObj.title
    if ($schemaTitle -ne $WorkerResultSchemaName) {
        $schemaErrors.Add("schema title '$schemaTitle' does not match expected '$WorkerResultSchemaName'")
    }
    $result.worker_result_validation.schema_title = $schemaTitle

    $taskIdMatch = [regex]::Match($prompt, '(?im)^\s*WORKER_TASK_ID\s*:\s*([A-Za-z0-9._-]+)\s*$')
    if (-not $taskIdMatch.Success) { throw "Task Card is missing WORKER_TASK_ID." }
    $expectedTaskId = $taskIdMatch.Groups[1].Value
    $result.task_id = $expectedTaskId
    $result.expected_task_id = $expectedTaskId

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
    $lockContent = "pid=$PID;created_at=$((Get-Date).ToString('o'));segment=$segmentName"
    $lockRecovered = $false
    if (Test-Path -LiteralPath $lockPath) {
        $existing = (Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8).Trim()
        $existingPid = $null
        if ($existing -match 'pid=(\d+)') { $existingPid = [int]$Matches[1] }
        if ($existingPid -ne $null -and (Test-PidAlive $existingPid)) {
            throw "Another worker dispatch (pid=$existingPid) is using this worktree."
        }
        # Stale lock; take it over.
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
        $lockRecovered = $true
    }
    $lockStream = [IO.File]::Open($lockPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $lockBytes = [Text.Encoding]::UTF8.GetBytes($lockContent)
    $lockStream.Write($lockBytes, 0, $lockBytes.Length)
    $lockStream.Flush()
    $result.worktree_lock.lock_path = (ConvertTo-RedactedPath $lockPath)
    $result.worktree_lock.pid = $PID
    $result.worktree_lock.created_at = (Get-Date).ToString('o')
    $result.worktree_lock.recovered_from_stale = $lockRecovered
    $result.gates.worktree = "PASS"

    $launcher = Find-ProviderLauncher $Provider
    $result.provider_availability.launcher_command = $launcher.command
    $result.provider_availability.launcher_resolved = (ConvertTo-RedactedPath $launcher.resolved)
    if ($launcher.command) {
        $result.provider_availability.execution_available = "AVAILABLE"
    } else {
        throw ("No Claude launcher found for provider " + $Provider + ".")
    }
    # Default to NOT_QUERIED. Only CONFIG_REQUIRED when a real snapshot
    # was returned by the metrics runner. Recorded as a separate state
    # so callers can distinguish "not measured yet" from "measured and
    # marked CONFIG_REQUIRED".
    $result.provider_availability.quota_snapshot_available = "NOT_QUERIED"
    $result.provider_availability.quota_snapshot_reason = "not queried in precheck"

    $maxTurnsStr = [string]$MaxTurns
    # Build the Claude args array via ConvertTo-Json with a high depth
    # limit. The prompt is normalised so its content does not contain
    # JSON-like substrings that would re-trigger the depth bug.
    $argList = @("-p", $promptNormalized, "--output-format", "stream-json", "--verbose", "--max-turns", $maxTurnsStr)
    $ClaudeArgsJson = ConvertTo-Json -InputObject $argList -Depth 16 -Compress
    if (-not [string]::IsNullOrWhiteSpace($ResumeSessionId)) {
        $argList = @("-p", $promptNormalized, "--output-format", "stream-json", "--verbose", "--max-turns", $maxTurnsStr, "--resume", $ResumeSessionId)
        $ClaudeArgsJson = ConvertTo-Json -InputObject $argList -Depth 16 -Compress
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

    # Run the metrics wrapper. If it itself fails, the dispatch is a
    # runner failure, not a worker completion.
    $runnerOk = $true
    $rawStdout = ""
    $runnerExit = 0
    try {
        $rawStdout = (& $MetricsRunner @runnerArgs 2> $stderrPath) | Out-String
        $runnerExit = $LASTEXITCODE
    } catch {
        $runnerOk = $false
        $runnerExit = -1
        $result.errors += "metrics wrapper threw: $($_.Exception.Message)"
    }
    $result.dispatch_status = "DISPATCHED"
    $result.metrics.agent_exit_code = $runnerExit

    # Read the real SUMMARY_PATH from RAW stdout (before redaction).
    $rawSummaryPath = $null
    foreach ($line in ($rawStdout -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.StartsWith("SUMMARY_PATH=")) { $rawSummaryPath = $trimmed.Substring("SUMMARY_PATH=".Length) }
        if ($trimmed.StartsWith("RUN_ID=")) { $result.metrics.run_id = $trimmed.Substring("RUN_ID=".Length) }
        if ($trimmed.StartsWith("AGENT_EXIT_CODE=")) {
            $agentExitText = $trimmed.Substring("AGENT_EXIT_CODE=".Length)
            $parsedAgentExit = 0
            if ([int]::TryParse($agentExitText, [ref]$parsedAgentExit)) { $result.metrics.agent_exit_code = $parsedAgentExit }
        }
    }

    if ($rawSummaryPath -and (Test-Path -LiteralPath $rawSummaryPath -PathType Leaf)) {
        $rawSummaryText = Read-Utf8Strict $rawSummaryPath
        $result.metrics.summary_sha256 = Get-Sha256Hex $rawSummaryText
        # Sanitize the persisted path AFTER reading the file content.
        $result.metrics.summary_path = (ConvertTo-RedactedPath $rawSummaryPath)
        try {
            $summary = $rawSummaryText | ConvertFrom-Json -ErrorAction Stop
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
            # If the summary reports an explicit quota snapshot state, adopt it.
            foreach ($name in @("quota_snapshot_available", "quota_state")) {
                if ($summary.PSObject.Properties.Name -contains $name) {
                    $value = [string]$summary.$name
                    if ($value -eq "CONFIG_REQUIRED" -or $value -eq "AVAILABLE" -or $value -eq "NOT_QUERIED" -or $value -eq "BLOCKED") {
                        $result.provider_availability.quota_snapshot_available = $value
                        $result.provider_availability.quota_snapshot_reason = "summary.$name"
                    }
                }
            }
        } catch {
            $result.errors += "metrics summary could not be parsed"
        }
    }

    # Parse the Worker Result from RAW stdout (still un-redacted) so we
    # can later decide whether the Worker Result schema is satisfied.
    $rawWorkerResult = Get-WorkerResultRaw $rawStdout
    if ($null -ne $rawWorkerResult) {
        $result.worker_task_id_match = ([string]$rawWorkerResult.worker_task_id -eq $expectedTaskId)
        # Validate the Worker Result against the loaded schema.
        if ($null -ne $schemaObj) {
            $validation = Test-JsonSchema -Instance $rawWorkerResult -Schema $schemaObj -RootName "WorkerResult"
            $result.schema_validation = @{
                valid = ($validation.Count -eq 0)
                error_count = $validation.Count
                errors = @($validation)
            }
            $result.worker_result_validation.errors = @($validation)
        }
    } else {
        $result.schema_validation = @{ valid = $false; error_count = 1; errors = @("worker result not present in raw stdout") }
        $result.worker_result_validation.errors = @("worker result not present in raw stdout")
    }

    # Redact the stdout/stderr for the persistent logs.
    $sanitizedStdout = Redact-Text $rawStdout $promptNormalized $taskCardResolved
    $rawStderr = ""
    if (Test-Path -LiteralPath $stderrPath) { $rawStderr = Get-Content -LiteralPath $stderrPath -Raw -Encoding UTF8 }
    $sanitizedStderr = Redact-Text $rawStderr $promptNormalized $taskCardResolved
    Set-Content -LiteralPath $stdoutPath -Value $sanitizedStdout -Encoding UTF8
    Set-Content -LiteralPath $stderrPath -Value $sanitizedStderr -Encoding UTF8

    $afterDirty = Invoke-Git $worktreeResolved @("status", "--porcelain")
    $cleanAfter = ($afterDirty.exit_code -eq 0 -and [string]::IsNullOrWhiteSpace($afterDirty.output))

    $completion = Get-WorkerCompletion -WorkerResult $rawWorkerResult -WorktreeCleanAfter $cleanAfter -Worktree $worktreeResolved -RunnerOk $runnerOk -ExpectedTaskId $expectedTaskId -CommitAttributionMarker $CommitAttributionMarker
    $result.worker_completion = $completion

    if (-not $runnerOk) {
        $exitCode = 3
    } elseif ($completion.status -eq "COMPLETION_CANDIDATE") {
        $exitCode = 10
    } elseif ($completion.status -eq "FAILED_WORKER_COMPLETION") {
        $exitCode = 20
    } elseif ($completion.status.StartsWith("BLOCKED_")) {
        $exitCode = 30
    } else {
        $exitCode = 0
    }

    Write-JsonAtomic $resultPath $result
    Write-Output $resultPath
    exit $exitCode
} catch {
    $result.dispatch_status = "PRECHECK_FAILED"
    $result.errors += $_.Exception.Message
    if (-not (Test-Path -LiteralPath $stdoutPath)) { Set-Content -LiteralPath $stdoutPath -Value "" -Encoding UTF8 }
    if (-not (Test-Path -LiteralPath $stderrPath)) { Set-Content -LiteralPath $stderrPath -Value "" -Encoding UTF8 }
    if ($schemaErrors.Count -gt 0) {
        $result.worker_result_validation.errors = @($schemaErrors)
    }
    Write-JsonAtomic $resultPath $result
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
