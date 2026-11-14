#requires -Version 5.1
<#
SmartSVG Studio V3.4 - paquet Windows portable experimental (pas un installateur).
Execution Windows x64, depuis la racine du depot :
    pwsh -NoProfile -File tools/build_portable_windows.ps1
L'environnement doit deja contenir Python 3.11, PyInstaller 6.16.0,
NumPy 2.4.6 et Pillow 13.0.0 (voir le workflow GitHub associe).
#>
[CmdletBinding()]
param(
    [string]$RepositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not [Environment]::Is64BitProcess -or -not $IsWindows) {
    # Windows PowerShell 5.1 ne definit pas $IsWindows.
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT -or -not [Environment]::Is64BitProcess) {
        throw 'Ce packaging exige Windows x64.'
    }
}

$repo = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$entryPoint = Join-Path $repo 'engine/standalone_desktop_v34.py'
$guide = Join-Path $repo 'docs/PORTABLE_ALPHA_WINDOWS.md'
if (-not (Test-Path -LiteralPath $entryPoint -PathType Leaf)) { throw 'Point entree natif introuvable.' }
if (-not (Test-Path -LiteralPath $guide -PathType Leaf)) { throw 'Guide Alpha introuvable.' }

$work = Join-Path $repo 'build/portable-alpha'
$dist = Join-Path $work 'pyinstaller-dist'
$spec = Join-Path $work 'spec'
$build = Join-Path $work 'pyinstaller-work'
$artifacts = Join-Path $work 'artifacts'
$stage = Join-Path $work 'staging'
foreach ($folder in @($dist, $spec, $build, $artifacts, $stage)) {
    if (Test-Path -LiteralPath $folder) { Remove-Item -LiteralPath $folder -Recurse -Force }
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
}

& python -m PyInstaller --noconfirm --clean --onedir --windowed --name SmartSVG-Studio --paths (Join-Path $repo 'engine') --distpath $dist --workpath $build --specpath $spec $entryPoint
if ($LASTEXITCODE -ne 0) { throw "PyInstaller a echoue (code $LASTEXITCODE)." }

$builtApp = Join-Path $dist 'SmartSVG-Studio'
$builtExe = Join-Path $builtApp 'SmartSVG-Studio.exe'
if (-not (Test-Path -LiteralPath $builtExe -PathType Leaf)) { throw 'Executable manquant apres packaging.' }

$packageDir = Join-Path $stage 'SmartSVG-Studio'
Copy-Item -LiteralPath $builtApp -Destination $packageDir -Recurse
Copy-Item -LiteralPath $guide -Destination (Join-Path $packageDir 'LIRE_AVANT_TEST.md')
$versionFile = Join-Path $packageDir 'VERSION_ALPHA.txt'
$commit = (& git -C $repo rev-parse HEAD).Trim()
@(
    'SmartSVG Studio V3.4 - ALPHA PORTABLE WINDOWS x64'
    "Git commit : $commit"
    'Nature : version experimentale non certifiee pour Cricut'
    'Entree : SmartSVG-Studio.exe'
    'Dossier portable : conserver tous les fichiers ensemble'
) | Set-Content -LiteralPath $versionFile -Encoding UTF8

# Ne tester que le dossier livre, avec un chemin contenant espace et accents,
# et non la copie de developpement.
$testRoot = Join-Path $work 'test packagé évaluation'
if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
New-Item -ItemType Directory -Path $testRoot | Out-Null
$testDir = Join-Path $testRoot 'SmartSVG-Studio'
Copy-Item -LiteralPath $packageDir -Destination $testDir -Recurse
$testExe = Join-Path $testDir 'SmartSVG-Studio.exe'

# --probe charge le noyau sans ouvrir Tk et doit sortir avec le code zero.
$probe = Start-Process -FilePath $testExe -ArgumentList @('--probe') -PassThru -Wait
if ($probe.ExitCode -ne 0) { throw "Le probe de l'executable emballe a echoue: $($probe.ExitCode)." }

# Verifie que l'executable GUI reste vivant apres demarrage reel.
$gui = Start-Process -FilePath $testExe -PassThru
try {
    Start-Sleep -Seconds 5
    $gui.Refresh()
    if ($gui.HasExited) { throw "Le GUI s'est termine prematur ement, code $($gui.ExitCode)." }
}
finally {
    $gui.Refresh()
    if (-not $gui.HasExited) { Stop-Process -Id $gui.Id -Force }
}

$zipName = 'SmartSVG-Studio-V3.4-Alpha-Windows-x64.zip'
$zipPath = Join-Path $artifacts $zipName
Compress-Archive -LiteralPath $packageDir -DestinationPath $zipPath -CompressionLevel Optimal -Force
if ((Get-Item -LiteralPath $zipPath).Length -lt 1048576) { throw 'Archive anormalement petite.' }
$sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
"$sha  $zipName" | Set-Content -LiteralPath (Join-Path $artifacts 'SHA256SUMS.txt') -Encoding ascii
Write-Output "PORTABLE_ALPHA_BUILD_OK"
Write-Output "ZIP=$zipPath"
Write-Output "SHA256=$sha"
