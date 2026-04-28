param(
  [Parameter(Mandatory = $true)]
  [string]$DesktopDir,
  [Parameter(Mandatory = $true)]
  [string]$DesktopFrontendPort,
  [Parameter(Mandatory = $true)]
  [string]$DesktopLog,
  [Parameter(Mandatory = $true)]
  [string]$DesktopErrLog,
  [Parameter(Mandatory = $true)]
  [string]$DesktopPidFile
)

$ErrorActionPreference = 'Stop'

Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:DESKTOP_FRONTEND_URL = "http://127.0.0.1:$DesktopFrontendPort"
$env:DESKTOP_API_BASE_URL = "http://127.0.0.1:7860"

$electronExe = Join-Path $DesktopDir 'node_modules\electron\dist\electron.exe'
if (-not (Test-Path -LiteralPath $electronExe)) {
  throw "Electron runtime not found: $electronExe"
}

[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($DesktopLog)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($DesktopErrLog)) | Out-Null
[System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($DesktopPidFile)) | Out-Null

$process = Start-Process `
  -FilePath $electronExe `
  -ArgumentList '.' `
  -WorkingDirectory $DesktopDir `
  -WindowStyle Normal `
  -RedirectStandardOutput $DesktopLog `
  -RedirectStandardError $DesktopErrLog `
  -PassThru

Set-Content -Path $DesktopPidFile -Value $process.Id -Encoding UTF8
