

# Verification Installer hash

Méthode la plus simple et gratuite : Fournir des hash (SHA256 le plus souvent)

**Étapes à suivre (côté développeur)** :

1. Calculer le hash :

```powershell
# PowerShell
Get-FileHash .\votreprogramme.exe -Algorithm SHA256 | Format-List

Get-FileHash .\BlueNotebook-Setup-4.2.7.exe.exe -Algorithm SHA256 | Out-File BlueNotebook-Setup-4.2.7.exe.hash

# ou avec certutil (présent sur tous les Windows)
certutil -hashfile votreprogramme.exe SHA256
```
```bash
#Linux 
$ sha256sum BlueNotebook-Setup-4.2.7.exe
78077d1c279d1f4b47a173f70c841229bb5a355391bb647d7df0d3603d492403  BlueNotebook-Setup-4.2.7.exe
$ sha256sum BlueNotebook-Setup-4.2.7.exe > BlueNotebook-Setup-4.2.7.exe.hash
```


2. Mettre le hash dans la description de la release GitHub (ou dans un fichier `checksums.txt` joint à la release)

Exemple classique :

```txt
SHA256 (monprog-v1.2.3.exe) = d8e8fca2dc0f896fd7cb4cb0031ba249
                               9b2e76fb4c2e0f4a8e7e8f8d8e8fca2d
```

**Vérification par l’utilisateur** (plusieurs façons) :

- PowerShell (recommandé) :

```powershell
Get-FileHash .\monprog-v1.2.3.exe -Algorithm SHA256
```

- Via l’interface graphique avec des outils comme :
  - HashCalc
  - WinMD5
  - 7-Zip (clic droit → CRC SHA → SHA-256)
 

## Github secrets

Sous Windows, voici les équivalents pour définir des variables d'environnement comme GITHUB_TOKEN :

1. Via le Profil PowerShell (équivalent de .bash_profile)
Éditer le profil PowerShell :

```powershell
notepad $PROFILE
```

Si le fichier n'existe pas, créez-le d'abord :

```powershell
New-Item -Path $PROFILE -Type File -Force
notepad $PROFILE
``` 
Ajoutez dans le fichier :

```txt
$env:GITHUB_TOKEN = "xxxxxxxxx"
```

Sauvegardez et redémarrez PowerShell. La variable sera disponible dans toutes vos sessions PowerShell.

## Upload GitHub

```powershell
.\Upload_to_GitHub.ps1 -Version "4.2.7"
```
Le script uploadera vers la release v4.2.7 du repository lephotographelibre/BlueNotebook.
