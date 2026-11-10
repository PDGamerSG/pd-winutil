param(
    [string]$ScriptPath = (Join-Path (Split-Path $PSScriptRoot -Parent) 'winutil.ps1'),
    [switch]$RenderLogo
)

$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$source = Get-Content -LiteralPath $ScriptPath -Raw -Encoding UTF8
$ast = [System.Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    $parseErrors | Format-List | Out-String | Write-Host
    throw 'The compiled PowerShell script contains syntax errors.'
}
if ($source.Contains('#{replaceme}') -or $source.Contains('#{islocalcompile}')) {
    throw 'The compiler left an unexpanded startup placeholder.'
}
foreach ($notice in 'MIT License', 'Copyright (c) 2022 CT Tech Group LLC',
    'Permission is hereby granted, free of charge',
    'The above copyright notice and this permission notice shall be included in all') {
    if (-not $source.Contains($notice)) {
        throw "The standalone script is missing its original license notice: $notice"
    }
}
$releaseUrl = 'https://github.com/PDGamerSG/pd-winutil/releases/latest/download/winutil.ps1'
if (-not $source.Contains($releaseUrl)) {
    throw 'The compiled utility does not contain the PD release URL.'
}
if ($source -match 'https://christitus\.com/win(?:[\s''"]|$)' -or
    $source -match '(?i)https://github\.com/ChrisTitusTech/winutil/releases/[^''"\s]*download/winutil\.ps1') {
    throw 'A compiled launch path still downloads the upstream product.'
}
foreach ($parameter in 'Config', 'Preset', 'Offline') {
    if ($parameter -notin $ast.ParamBlock.Parameters.Name.VariablePath.UserPath) {
        throw "The upstream launch parameter '$parameter' is missing."
    }
}

# Run only the banner and its console helper from the compiled artifact. Never run Windows tweaks.
$banner = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.CommandAst] -and
    $node.GetCommandName() -eq 'Write-WinUtilHost' -and
    $node.Extent.Text.Contains('Pallab Das Windows Utility') -and
    $node.Extent.Text.Contains('PP   PP')
}, $true)
if ($null -eq $banner) { throw 'The compiled artifact is missing its PD terminal banner.' }
$hostFunction = $ast.Find({
    param($node)
    $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Write-WinUtilHost'
}, $true)
if ($null -eq $hostFunction) { throw 'The upstream console helper is missing.' }
. ([scriptblock]::Create($hostFunction.Extent.Text))
& ([scriptblock]::Create($banner.Extent.Text))

if ($RenderLogo) {
    if ($env:OS -ne 'Windows_NT') { throw 'WPF logo rendering requires Windows.' }
    Add-Type -AssemblyName PresentationFramework
    $assetFunction = $ast.Find({
        param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -eq 'Invoke-WinUtilAssets'
    }, $true)
    if ($null -eq $assetFunction) { throw 'The upstream asset function is missing.' }
    . ([scriptblock]::Create($assetFunction.Extent.Text))
    $sync = [Hashtable]::Synchronized(@{})
    $logo = Invoke-WinUtilAssets -Type 'logo' -Size 90 -Render
    if ($null -eq $logo -or $logo.PixelWidth -le 0 -or $logo.PixelHeight -le 0) {
        throw 'The PD application and taskbar logo could not be rendered.'
    }
    $stride = $logo.PixelWidth * 4
    $pixels = New-Object byte[] ($stride * $logo.PixelHeight)
    $logo.CopyPixels($pixels, $stride, 0)
    if (-not ($pixels | Where-Object { $_ -ne 0 } | Select-Object -First 1)) {
        throw 'The PD logo rendered an empty image.'
    }
    Write-Host "PD WPF logo rendered: $($logo.PixelWidth)x$($logo.PixelHeight)"
}
Write-Host 'PD compiled artifact verification passed.'
