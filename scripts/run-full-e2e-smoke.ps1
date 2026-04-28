$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$qaRoot = Join-Path $repoRoot 'tmp-qa-playwright'
$frontendRoot = Join-Path $repoRoot 'src\frontend'
$authPath = Join-Path $qaRoot 'auth.json'
$qaApiScript = Join-Path $qaRoot 'qa_echo_api.py'
$frontendOut = Join-Path $repoRoot 'tmp\frontend-dev.out.log'
$frontendErr = Join-Path $repoRoot 'tmp\frontend-dev.err.log'
$qaApiOut = Join-Path $repoRoot 'tmp\qa-echo-api.out.log'
$qaApiErr = Join-Path $repoRoot 'tmp\qa-echo-api.err.log'
$tmpRoot = Join-Path $repoRoot 'tmp'

function Test-Http {
    param(
        [Parameter(Mandatory = $true)][string]$Url
    )
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

function Ensure-Auth {
    if (-not (Test-Path $authPath)) {
        throw "Missing auth state: $authPath. Log in once in the browser and export storage state first."
    }

    $raw = Get-Content $authPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $token = $raw.origins.localStorage | Where-Object { $_.name -eq 'token' } | Select-Object -First 1
    if (-not $token -or [string]::IsNullOrWhiteSpace($token.value)) {
        throw "auth.json exists but does not contain a token."
    }
}

function Ensure-Frontend {
    if (Test-Http -Url 'http://127.0.0.1:8090/login') {
        return
    }

    Write-Host 'Starting frontend dev server on 8090...'
    if (-not (Test-Path $tmpRoot)) {
        New-Item -ItemType Directory -Path $tmpRoot | Out-Null
    }
    Start-Process -FilePath 'E:\develop\nodejs\npm.cmd' `
        -ArgumentList 'run', 'dev', '--', '--host', '127.0.0.1', '--port', '8090' `
        -WorkingDirectory $frontendRoot `
        -RedirectStandardOutput $frontendOut `
        -RedirectStandardError $frontendErr | Out-Null

    Wait-Http -Url 'http://127.0.0.1:8090/login' -TimeoutSeconds 60
}

function Ensure-QaApi {
    if (Test-Http -Url 'http://127.0.0.1:9101/health') {
        return
    }

    Write-Host 'Starting local QA echo API on 9101...'
    if (-not (Test-Path $tmpRoot)) {
        New-Item -ItemType Directory -Path $tmpRoot | Out-Null
    }
    Start-Process -FilePath 'python' `
        -ArgumentList $qaApiScript `
        -WorkingDirectory $qaRoot `
        -RedirectStandardOutput $qaApiOut `
        -RedirectStandardError $qaApiErr | Out-Null

    Wait-Http -Url 'http://127.0.0.1:9101/health' -TimeoutSeconds 20
}

function Ensure-Backend {
    Wait-Http -Url 'http://127.0.0.1:7860/health' -TimeoutSeconds 20
}

Write-Host 'Checking login state, backend, frontend, and QA API...'
Ensure-Auth
Ensure-Backend
Ensure-Frontend
Ensure-QaApi

Write-Host 'Running full end-to-end smoke validation...'
Push-Location $qaRoot
try {
    & 'E:\develop\nodejs\npm.cmd' run full-e2e
}
finally {
    Pop-Location
}
