# Script pour uploader les fichiers d'installation sur GitHub Release
# Usage: .\Upload_to_GitHub.ps1 -Version "4.2.7"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

# Configuration
$RepoOwner = "lephotographelibre"
$RepoName = "BlueNotebook"
$ExeFileName = "BlueNotebook-Setup-$Version.exe"
$HashFileName = "$ExeFileName.hash"
$ReleaseTag = "v$Version"

# Verification du token GitHub
if (-not $env:GITHUB_TOKEN) {
    Write-Error "La variable d'environnement GITHUB_TOKEN n'est pas definie."
    Write-Host "Ajoutez dans votre profil PowerShell ($PROFILE) :"
    Write-Host '$env:GITHUB_TOKEN = "votre_token"'
    exit 1
}

# Verification de l'existence du fichier .exe
if (-not (Test-Path $ExeFileName)) {
    Write-Error "Le fichier $ExeFileName n'existe pas dans le repertoire courant."
    exit 1
}

Write-Host "=== Upload vers GitHub Release ===" -ForegroundColor Cyan
Write-Host "Version: $Version"
Write-Host "Release: $ReleaseTag"
Write-Host "Fichier: $ExeFileName"
Write-Host ""

# Etape 1: Calcul du hash SHA256
Write-Host "[1/3] Calcul du hash SHA256..." -ForegroundColor Yellow
$Hash = (Get-FileHash -Path $ExeFileName -Algorithm SHA256).Hash
Write-Host "Hash: $Hash" -ForegroundColor Green

# Etape 2: Creation du fichier .hash
Write-Host "[2/3] Creation du fichier $HashFileName..." -ForegroundColor Yellow
@"
Algorithm : SHA256
Hash      : $Hash
Path      : $ExeFileName
"@ | Out-File -FilePath $HashFileName -Encoding UTF8

Write-Host "Fichier $HashFileName cree." -ForegroundColor Green

# Etape 3: Upload vers GitHub
Write-Host "[3/3] Upload vers GitHub Release $ReleaseTag..." -ForegroundColor Yellow

# Verification si gh CLI est installe
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    # Utilisation de gh CLI (methode recommandee)
    Write-Host "Utilisation de GitHub CLI (gh)..." -ForegroundColor Cyan

    # Configuration du token pour gh
    $env:GH_TOKEN = $env:GITHUB_TOKEN

    # Upload du fichier .exe
    Write-Host "  - Upload de $ExeFileName..."
    gh release upload $ReleaseTag $ExeFileName --repo "$RepoOwner/$RepoName" --clobber

    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK $ExeFileName uploade" -ForegroundColor Green
    } else {
        Write-Error "Echec de l'upload de $ExeFileName"
        exit 1
    }

    # Upload du fichier .hash
    Write-Host "  - Upload de $HashFileName..."
    gh release upload $ReleaseTag $HashFileName --repo "$RepoOwner/$RepoName" --clobber

    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK $HashFileName uploade" -ForegroundColor Green
    } else {
        Write-Error "Echec de l'upload de $HashFileName"
        exit 1
    }

} else {
    # Utilisation de l'API REST GitHub
    Write-Host "GitHub CLI non trouve, utilisation de l'API REST..." -ForegroundColor Cyan

    # Recuperation des informations de la release
    $headers = @{
        "Authorization" = "Bearer $env:GITHUB_TOKEN"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $releaseUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/tags/$ReleaseTag"

    try {
        $release = Invoke-RestMethod -Uri $releaseUrl -Headers $headers -Method Get
        Write-Host "  Upload URL brute: $($release.upload_url)" -ForegroundColor Gray
        $idx = $release.upload_url.IndexOf([char]123)
        if ($idx -gt 0) {
            $uploadUrl = $release.upload_url.Substring(0, $idx)
        } else {
            $uploadUrl = $release.upload_url
        }
        Write-Host "  Upload URL finale: $uploadUrl" -ForegroundColor Gray

        $uploadHeaders = @{
            "Authorization" = "Bearer $env:GITHUB_TOKEN"
            "Content-Type" = "application/octet-stream"
            "Accept" = "application/vnd.github+json"
        }

        # Upload du fichier .exe
        $exeFullPath = (Resolve-Path $ExeFileName).Path
        $exeBytes = [System.IO.File]::ReadAllBytes($exeFullPath)
        $exeUri = $uploadUrl + "?name=" + $ExeFileName
        Write-Host "  - Upload de $ExeFileName..."
        Write-Host "    URI: $exeUri" -ForegroundColor Gray
        Invoke-RestMethod -Uri $exeUri -Headers $uploadHeaders -Method Post -Body $exeBytes | Out-Null
        Write-Host "    OK $ExeFileName uploade" -ForegroundColor Green

        # Upload du fichier .hash
        $hashFullPath = (Resolve-Path $HashFileName).Path
        $hashBytes = [System.IO.File]::ReadAllBytes($hashFullPath)
        $hashUri = $uploadUrl + "?name=" + $HashFileName
        Write-Host "  - Upload de $HashFileName..."
        Write-Host "    URI: $hashUri" -ForegroundColor Gray
        Invoke-RestMethod -Uri $hashUri -Headers $uploadHeaders -Method Post -Body $hashBytes | Out-Null
        Write-Host "    OK $HashFileName uploade" -ForegroundColor Green

    } catch {
        Write-Error "Erreur lors de l upload: $_"
        Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Upload termine avec succes ===" -ForegroundColor Green
$finalUrl = "https://github.com/$RepoOwner/$RepoName/releases/tag/$ReleaseTag"
Write-Host "Les fichiers sont disponibles sur: $finalUrl"
