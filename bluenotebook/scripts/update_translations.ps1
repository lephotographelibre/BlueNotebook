# update_translations.ps1
# À placer à la racine du projet BlueNotebook/bluenotebook
# A executer avec 
# powershell -ExecutionPolicy Bypass -File update_translations.ps1
# .venv_bluenotebook\Scripts\activate  NE PAS OUBLIER !!!!!!!!

$excludedDirs = "tests", "scripts", "__pycache__", ".git", ".venv", "venv", "build", "dist", "i18n", "resources"

$pythonFiles = Get-ChildItem -Path . -Recurse -Filter *.py |
    Where-Object {
        $file = $_
        -not ($excludedDirs | Where-Object { $file.FullName -like "*\$($_)*" })
    } |
    Select-Object -ExpandProperty FullName

if ($pythonFiles.Count -eq 0) {
    Write-Host "Aucun fichier .py trouvé." -ForegroundColor Red
    exit 1
}

Write-Host "Fichiers Python trouvés : $($pythonFiles.Count)" -ForegroundColor Green

# Construction de la commande
$args = $pythonFiles -join " "
$command = "pylupdate5 -verbose $args -ts i18n/bluenotebook_en.ts"

Write-Host "Exécution : $command" -ForegroundColor Cyan
Invoke-Expression $command

Write-Host "`nTerminé ! Fichier mis à jour : i18n/bluenotebook_en.ts" -ForegroundColor Green