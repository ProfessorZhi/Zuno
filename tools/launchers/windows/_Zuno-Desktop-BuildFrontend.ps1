param(
  [Parameter(Mandatory = $true)]
  [string]$FrontendDir,
  [Parameter(Mandatory = $true)]
  [string]$ViteEntry,
  [Parameter(Mandatory = $true)]
  [string]$FrontendLog,
  [Parameter(Mandatory = $true)]
  [string]$FrontendErrLog
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
$quotedViteEntry = '"{0}"' -f $ViteEntry

Push-Location $FrontendDir
try {
  $process = Start-Process `
    -FilePath 'node' `
    -ArgumentList @($quotedViteEntry, 'build') `
    -WorkingDirectory $FrontendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $FrontendLog `
    -RedirectStandardError $FrontendErrLog `
    -Wait `
    -PassThru

  if ($process.ExitCode -ne 0) {
    throw "Frontend build failed with exit code $($process.ExitCode)"
  }
} finally {
  Pop-Location
}
