$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$frontendRoot = Join-Path $repoRoot 'apps\web'
$desktopRoot = Join-Path $repoRoot 'apps\desktop'
$tmpRoot = Join-Path $repoRoot 'tmp'
$resultPath = Join-Path $tmpRoot 'desktop-smoke-result.json'
$frontendOut = Join-Path $tmpRoot 'desktop-smoke-frontend.out.log'
$frontendErr = Join-Path $tmpRoot 'desktop-smoke-frontend.err.log'
$desktopOut = Join-Path $tmpRoot 'desktop-smoke.out.log'
$desktopErr = Join-Path $tmpRoot 'desktop-smoke.err.log'

function Test-Http {
    param([Parameter(Mandatory = $true)][string]$Url)
    try {
        $response = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 $Url
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 500
    }
    catch {
        return $false
    }
}

function Wait-Http {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$TimeoutSeconds = 30
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Http -Url $Url) {
            return
        }
        Start-Sleep -Seconds 1
    }
    throw "Timed out waiting for $Url"
}

function New-SmokeToken {
    Push-Location $repoRoot
    try {
        $token = @'
import json
from zuno.compatibility.vendor.fastapi_jwt_auth import AuthJWT
from zuno.api.JWT import Settings

@AuthJWT.load_config
def get_config():
    return Settings()

payload = {"user_name": "Admin", "user_id": "1", "role": "admin"}
print(AuthJWT().create_access_token(subject=json.dumps(payload)))
'@ | python -
        return ($token | Select-Object -First 1).Trim()
    }
    finally {
        Pop-Location
    }
}

function Ensure-Backend {
    Wait-Http -Url 'http://127.0.0.1:7860/health' -TimeoutSeconds 30
}

function Ensure-Frontend {
    if (Test-Http -Url 'http://127.0.0.1:8091') {
        return
    }

    Write-Host 'Starting desktop smoke frontend dev server on 8091...'
    Start-Process -FilePath 'E:\develop\nodejs\npm.cmd' `
        -ArgumentList 'run', 'dev', '--', '--host', '127.0.0.1', '--port', '8091' `
        -WorkingDirectory $frontendRoot `
        -RedirectStandardOutput $frontendOut `
        -RedirectStandardError $frontendErr | Out-Null
    Wait-Http -Url 'http://127.0.0.1:8091' -TimeoutSeconds 60
}

if (-not (Test-Path $tmpRoot)) {
    New-Item -ItemType Directory -Path $tmpRoot | Out-Null
}
Remove-Item -Path $resultPath, $desktopOut, $desktopErr -ErrorAction SilentlyContinue

Ensure-Backend
Ensure-Frontend

$electronCandidates = @(
    (Join-Path $repoRoot 'node_modules\electron\dist\electron.exe'),
    (Join-Path $desktopRoot 'node_modules\electron\dist\electron.exe')
)
$electronExe = $electronCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $electronExe) {
    throw 'Electron runtime not found.'
}

$oldFrontendUrl = $env:DESKTOP_FRONTEND_URL
$oldApiBaseUrl = $env:DESKTOP_API_BASE_URL
$oldResult = $env:DESKTOP_SMOKE_RESULT
$oldToken = $env:DESKTOP_SMOKE_TOKEN
$oldRunAsNode = $env:ELECTRON_RUN_AS_NODE

$env:DESKTOP_FRONTEND_URL = 'http://127.0.0.1:8091'
$env:DESKTOP_API_BASE_URL = 'http://127.0.0.1:7860'
$env:DESKTOP_SMOKE_RESULT = $resultPath
$env:DESKTOP_SMOKE_TOKEN = New-SmokeToken
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue

try {
    $process = Start-Process `
        -FilePath $electronExe `
        -ArgumentList '.' `
        -WorkingDirectory $desktopRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $desktopOut `
        -RedirectStandardError $desktopErr `
        -PassThru

    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline -and -not (Test-Path $resultPath)) {
        if ($process.HasExited) {
            break
        }
        Start-Sleep -Milliseconds 500
    }

    if (-not (Test-Path $resultPath)) {
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        throw "Desktop smoke result was not written: $resultPath"
    }

    $result = Get-Content -Path $resultPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (-not $result.ok) {
        throw "Desktop smoke failed: $($result.failures -join '; ')"
    }
    Write-Host 'Desktop smoke passed.'
}
finally {
    $env:DESKTOP_FRONTEND_URL = $oldFrontendUrl
    $env:DESKTOP_API_BASE_URL = $oldApiBaseUrl
    $env:DESKTOP_SMOKE_RESULT = $oldResult
    $env:DESKTOP_SMOKE_TOKEN = $oldToken
    if ($oldRunAsNode) {
        $env:ELECTRON_RUN_AS_NODE = $oldRunAsNode
    } else {
        Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
    }
}
