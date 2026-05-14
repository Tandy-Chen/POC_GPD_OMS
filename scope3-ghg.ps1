param(
    [ValidateSet('process', 'validate')]
    [string]$Command = 'process',
    [string]$SourcePath,
    [string]$Sheet = 'sheet1',
    [string]$InputDir = (Join-Path $PSScriptRoot 'inputs'),
    [string]$OutputDir = (Join-Path $PSScriptRoot 'outputs')
)

$launcher = Join-Path $PSScriptRoot 'scope3-ghg.cmd'
$argsList = @()

if ($Command) {
    $argsList += $Command
}
if ($SourcePath) {
    $argsList += @('--input', $SourcePath)
}
if ($Sheet) {
    $argsList += @('--sheet', $Sheet)
}
if ($InputDir) {
    $argsList += @('--input-dir', $InputDir)
}
if ($Command -eq 'process' -and $OutputDir) {
    $argsList += @('--output-dir', $OutputDir)
}

& $launcher @argsList
exit $LASTEXITCODE