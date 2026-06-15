param(
  [Parameter(Mandatory = $true)]
  [string]$FrontendDir,
  [Parameter(Mandatory = $true)]
  [string]$ViteEntry,
  [Parameter(Mandatory = $true)]
  [string]$FrontendPort,
  [Parameter(Mandatory = $true)]
  [string]$FrontendLog,
  [Parameter(Mandatory = $true)]
  [string]$FrontendErrLog,
  [Parameter(Mandatory = $true)]
  [string]$FrontendPidFile
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $FrontendDir)) {
  throw "Frontend directory not found: $FrontendDir"
}

if (-not (Test-Path -LiteralPath $ViteEntry)) {
  throw "Vite entry not found: $ViteEntry"
}

[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($FrontendLog)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($FrontendErrLog)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($FrontendPidFile)) | Out-Null

$env:VITE_API_BASE_URL = 'http://127.0.0.1:7860'
$quotedViteEntry = '"{0}"' -f $ViteEntry

$process = Start-Process `
  -FilePath 'node' `
  -ArgumentList @($quotedViteEntry, '--host', '127.0.0.1', '--port', $FrontendPort, '--strictPort') `
  -WorkingDirectory $FrontendDir `
  -WindowStyle Hidden `
  -RedirectStandardOutput $FrontendLog `
  -RedirectStandardError $FrontendErrLog `
  -PassThru

Set-Content -Path $FrontendPidFile -Value $process.Id -Encoding UTF8
