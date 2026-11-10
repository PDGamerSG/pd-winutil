# Runs the latest verified release of Pallab Das Windows Utility

$latestTag = (Invoke-RestMethod https://api.github.com/repos/PDGamerSG/pd-winutil/releases/latest).tag_name
$uri = "https://github.com/PDGamerSG/pd-winutil/releases/download/$latestTag/winutil.ps1"
$scriptPath = Join-Path $env:TEMP "winutil-$latestTag.ps1"

Invoke-WebRequest -Uri $uri -OutFile $scriptPath -UseBasicParsing -ErrorAction Stop

$executable = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' }
$currentPowerShell = Join-Path $PSHOME $executable
& $currentPowerShell -ExecutionPolicy Bypass -NoProfile -File $scriptPath
