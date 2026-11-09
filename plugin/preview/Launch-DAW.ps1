param([Parameter(Mandatory = $true)][string]$Daw)
$ErrorActionPreference = 'Stop'
$pythonExe = Join-Path $PSScriptRoot 'runtime\Scripts\python.exe'
if (!(Test-Path $pythonExe -PathType Leaf)) { throw 'Run Setup.ps1 first.' }
$dawPath = (Resolve-Path -LiteralPath $Daw).Path
if ([IO.Path]::GetExtension($dawPath) -ine '.exe' -or !(Test-Path $dawPath -PathType Leaf)) {
    throw 'Supply the full path to your DAW executable.'
}
$previous = [Environment]::GetEnvironmentVariable('GROOVECLEAN_PYTHON', 'Process')
try {
    $env:GROOVECLEAN_PYTHON = $pythonExe
    Start-Process -FilePath $dawPath -WorkingDirectory (Split-Path $dawPath)
} finally {
    [Environment]::SetEnvironmentVariable('GROOVECLEAN_PYTHON', $previous, 'Process')
}
