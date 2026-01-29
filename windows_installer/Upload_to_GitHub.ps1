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

# Vérification du token GitHub
if (-not $env:GITHUB_TOKEN) {
    Write-Error "La variable d'environnement GITHUB_TOKEN n'est pas définie."
    Write-Host "Ajoutez dans votre profil PowerShell ($PROFILE) :"
    Write-Host '$env:GITHUB_TOKEN = "votre_token"'
    exit 1
}

# Vérification de l'existence du fichier .exe
if (-not (Test-Path $ExeFileName)) {
    Write-Error "Le fichier $ExeFileName n'existe pas dans le répertoire courant."
    exit 1
}

Write-Host "=== Upload vers GitHub Release ===" -ForegroundColor Cyan
Write-Host "Version: $Version"
Write-Host "Release: $ReleaseTag"
Write-Host "Fichier: $ExeFileName"
Write-Host ""

# Étape 1: Calcul du hash SHA256
Write-Host "[1/3] Calcul du hash SHA256..." -ForegroundColor Yellow
$Hash = (Get-FileHash -Path $ExeFileName -Algorithm SHA256).Hash
Write-Host "Hash: $Hash" -ForegroundColor Green

# Étape 2: Création du fichier .hash
Write-Host "[2/3] Création du fichier $HashFileName..." -ForegroundColor Yellow
@"
Algorithm : SHA256
Hash      : $Hash
Path      : $ExeFileName
"@ | Out-File -FilePath $HashFileName -Encoding UTF8

Write-Host "Fichier $HashFileName créé." -ForegroundColor Green

# Étape 3: Upload vers GitHub
Write-Host "[3/3] Upload vers GitHub Release $ReleaseTag..." -ForegroundColor Yellow

# Vérification si gh CLI est installé
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if ($ghInstalled) {
    # Utilisation de gh CLI (méthode recommandée)
    Write-Host "Utilisation de GitHub CLI (gh)..." -ForegroundColor Cyan

    # Configuration du token pour gh
    $env:GH_TOKEN = $env:GITHUB_TOKEN

    # Upload du fichier .exe
    Write-Host "  - Upload de $ExeFileName..."
    gh release upload $ReleaseTag $ExeFileName --repo "$RepoOwner/$RepoName" --clobber

    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ $ExeFileName uploadé" -ForegroundColor Green
    } else {
        Write-Error "Échec de l'upload de $ExeFileName"
        exit 1
    }

    # Upload du fichier .hash
    Write-Host "  - Upload de $HashFileName..."
    gh release upload $ReleaseTag $HashFileName --repo "$RepoOwner/$RepoName" --clobber

    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ $HashFileName uploadé" -ForegroundColor Green
    } else {
        Write-Error "Échec de l'upload de $HashFileName"
        exit 1
    }

} else {
    # Utilisation de l'API REST GitHub
    Write-Host "GitHub CLI non trouvé, utilisation de l'API REST..." -ForegroundColor Cyan

    # Récupération des informations de la release
    $headers = @{
        "Authorization" = "Bearer $env:GITHUB_TOKEN"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $releaseUrl = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/tags/$ReleaseTag"

    try {
        $release = Invoke-RestMethod -Uri $releaseUrl -Headers $headers -Method Get
        $uploadUrl = $release.upload_url -replace '\{\?name,label\}', ''

        # Fonction pour uploader un asset
        function Upload-Asset {
            param($FilePath, $UploadUrl)

            $fileName = Split-Path $FilePath -Leaf
            $fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
            $uploadUri = "$UploadUrl?name=$fileName"

            $uploadHeaders = @{
                "Authorization" = "Bearer $env:GITHUB_TOKEN"
                "Content-Type" = "application/octet-stream"
                "Accept" = "application/vnd.github+json"
            }

            Write-Host "  - Upload de $fileName..."
            Invoke-RestMethod -Uri $uploadUri -Headers $uploadHeaders -Method Post -Body $fileBytes | Out-Null
            Write-Host "    ✓ $fileName uploadé" -ForegroundColor Green
        }

        # Upload des fichiers
        Upload-Asset -FilePath $ExeFileName -UploadUrl $uploadUrl
        Upload-Asset -FilePath $HashFileName -UploadUrl $uploadUrl

    } catch {
        Write-Error "Erreur lors de l'upload: $_"
        Write-Host "Détails: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=== Upload terminé avec succès ===" -ForegroundColor Green
Write-Host "Les fichiers sont disponibles sur: https://github.com/$RepoOwner/$RepoName/releases/tag/$ReleaseTag"
