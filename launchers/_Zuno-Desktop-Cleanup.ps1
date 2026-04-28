param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectRoot,

    [Parameter(Mandatory = $true)]
    [string]$FrontendRoot,

    [Parameter(Mandatory = $true)]
    [string]$DesktopRoot,

    [Parameter(Mandatory = $true)]
    [string]$FrontendPidFile,

    [Parameter(Mandatory = $true)]
    [string]$DesktopPidFile
)

$ErrorActionPreference = "SilentlyContinue"

function Get-AncestorProcessIds {
    param(
        [Parameter(Mandatory = $true)]
        [int]$StartPid
    )

    $ids = New-Object System.Collections.Generic.HashSet[int]
    $currentPid = $StartPid

    while ($currentPid -gt 0) {
        $null = $ids.Add($currentPid)
        $process = Get-CimInstance Win32_Process -Filter "ProcessId = $currentPid"
        if (-not $process) {
            break
        }

        $currentPid = [int]$process.ParentProcessId
        if ($ids.Contains($currentPid)) {
            break
        }
    }

    return $ids
}

$excludedPids = Get-AncestorProcessIds -StartPid $PID

function Stop-ProcessTree {
    param(
        [Parameter(Mandatory = $true)]
        [int]$TargetPid
    )

    if ($excludedPids.Contains($TargetPid)) {
        return
    }

    & taskkill /PID $TargetPid /T /F *> $null
    if ($LASTEXITCODE -ne 0) {
        Stop-Process -Id $TargetPid -Force -ErrorAction SilentlyContinue
    }
}

function Stop-TrackedPidFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PidFile
    )

    if (-not (Test-Path -LiteralPath $PidFile)) {
        return
    }

    $pidText = (Get-Content -LiteralPath $PidFile -TotalCount 1).Trim()
    if ($pidText -match '^\d+$') {
        Stop-ProcessTree -TargetPid ([int]$pidText)
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
}

function Stop-ListeningPorts {
    param(
        [Parameter(Mandatory = $true)]
        [int[]]$Ports
    )

    foreach ($port in $Ports) {
        $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($listener in $listeners) {
            Stop-ProcessTree -TargetPid $listener.OwningProcess
        }
    }
}

function Matches-AnyMarker {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [Parameter(Mandatory = $true)]
        [string[]]$Markers
    )

    foreach ($marker in $Markers) {
        if (-not [string]::IsNullOrWhiteSpace($marker) -and $Text -like ("*" + $marker + "*")) {
            return $true
        }
    }

    return $false
}

$launcherTargets = @(
    (Join-Path $ProjectRoot "launchers\Zuno-Desktop-Start.cmd"),
    (Join-Path $ProjectRoot "launchers\Zuno-Desktop-Stop.cmd"),
    (Join-Path $ProjectRoot "launchers\Zuno-Desktop-Rebuild.cmd"),
    (Join-Path $ProjectRoot "launchers\Zuno-Desktop-Full-Rebuild.cmd"),
    (Join-Path $ProjectRoot "launchers\_Zuno-Desktop-Common.cmd")
)

$runtimeTargets = @($FrontendRoot, $DesktopRoot) + $launcherTargets
$processes = Get-CimInstance Win32_Process | Where-Object {
    $cmd = $_.CommandLine
    if (-not $cmd) {
        return $false
    }

    $name = $_.Name.ToLowerInvariant()
    $isSupportedRuntime = $name -in @("electron.exe", "node.exe", "cmd.exe", "powershell.exe", "pwsh.exe", "timeout.exe")
    $isSupportedRuntime -and (Matches-AnyMarker -Text $cmd -Markers $runtimeTargets)
}

Stop-TrackedPidFile -PidFile $DesktopPidFile
Stop-TrackedPidFile -PidFile $FrontendPidFile
Stop-ListeningPorts -Ports @(8091, 8090)

foreach ($process in $processes) {
    Stop-ProcessTree -TargetPid $process.ProcessId
}
