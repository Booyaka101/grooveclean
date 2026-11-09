param([string]$Python = 'py')
$ErrorActionPreference = 'Stop'
$runtime = Join-Path $PSScriptRoot 'runtime'
$pythonExe = Join-Path $runtime 'Scripts\python.exe'
function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    $null = Get-Command $Executable -CommandType Application -ErrorAction Stop
    # Windows PowerShell can treat harmless native stderr as a terminating error
    # when output is redirected. Native success is determined by the exit code.
    $ErrorActionPreference = 'Continue'
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed ($LASTEXITCODE): $Executable $Arguments" }
}
if (Test-Path $runtime) {
    throw 'runtime already exists. To retry, rename that folder first. No existing environment will be overwritten.'
}
if ($Python -eq 'py') {
    Invoke-Checked 'py' @('-3.11', '-c', "import struct, sys; assert sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8, 'Python 3.11 x64 required'")
} else {
    Invoke-Checked $Python @('-c', "import struct, sys; assert sys.version_info[:2] == (3, 11) and struct.calcsize('P') == 8, 'Python 3.11 x64 required'")
}
if ($Python -eq 'py') {
    Invoke-Checked 'py' @('-3.11', '-m', 'venv', $runtime)
} else { Invoke-Checked $Python @('-m', 'venv', $runtime) }
Invoke-Checked $pythonExe @('-m', 'pip', '--disable-pip-version-check', 'install', 'torch==2.6.0', '--index-url', 'https://download.pytorch.org/whl/cpu')
Invoke-Checked $pythonExe @('-m', 'pip', '--disable-pip-version-check', 'install', '-r', (Join-Path $PSScriptRoot 'requirements.txt'))
$wheels = @(Get-ChildItem (Join-Path $PSScriptRoot 'worker\*.whl'))
if ($wheels.Count -ne 1) { throw 'Expected exactly one bundled worker wheel.' }
Invoke-Checked $pythonExe @('-m', 'pip', '--disable-pip-version-check', 'install', '--no-deps', $wheels[0].FullName)
Invoke-Checked $pythonExe @((Join-Path $PSScriptRoot 'Check-Worker.py'))
Invoke-Checked $pythonExe @('-m', 'pip', 'freeze') | Set-Content (Join-Path $PSScriptRoot 'installed-runtime.txt')
Write-Host 'Setup passed. Read README.txt before installing the plugin and launching your DAW.'
