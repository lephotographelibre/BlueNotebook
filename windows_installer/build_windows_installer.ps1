# Build script for BlueNotebook Windows Installer
# PowerShell version

# Move to the script directory to ensure relative paths work
Set-Location $PSScriptRoot
Set-Location ..

# Configuration
# Note: no version 3.11.13 available on pyenv-win Windows
$PYTHON_VERSION = "3.11.9"
$VENV_NAME = ".venv_3.11.9"
$VENV_DIR = "bluenotebook\$VENV_NAME"

Write-Host "--- BlueNotebook Build Script ---" -ForegroundColor Cyan

# --- Environment Verification ---

# 1. Check if pyenv-win is installed
$pyenvPath = "$env:USERPROFILE\.pyenv\pyenv-win\bin\pyenv.bat"
if (-not (Test-Path $pyenvPath)) {
    Write-Host "ERROR: pyenv-win is not detected." -ForegroundColor Red
    Write-Host "Please install it to manage Python versions: https://github.com/pyenv-win/pyenv-win#installation"
    Write-Host "PowerShell Admin command:"
    Write-Host 'Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"'
    Read-Host "Press Enter to exit"
    exit 1
}

# Add pyenv to PATH for this session
$env:PATH = "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:PATH"

# 2. Check if the Python version is installed (check executable directly)
$pythonExe = "$env:USERPROFILE\.pyenv\pyenv-win\versions\$PYTHON_VERSION\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Python $PYTHON_VERSION is not installed via pyenv." -ForegroundColor Yellow
    Write-Host "Attempting to install..."
    & pyenv install $PYTHON_VERSION
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: The installation of Python $PYTHON_VERSION failed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Python $PYTHON_VERSION found." -ForegroundColor Green
}

# 3. Create the virtual environment if it doesn't exist
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating the virtual environment '$VENV_DIR'..."
    & "$env:USERPROFILE\.pyenv\pyenv-win\versions\$PYTHON_VERSION\python.exe" -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: The creation of the virtual environment failed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Store absolute paths for later use
$PROJECT_ROOT = Get-Location
$VENV_PYTHON = Join-Path $PROJECT_ROOT "$VENV_DIR\Scripts\python.exe"
$VENV_PIP = Join-Path $PROJECT_ROOT "$VENV_DIR\Scripts\pip.exe"
$VENV_PYINSTALLER = Join-Path $PROJECT_ROOT "$VENV_DIR\Scripts\pyinstaller.exe"

# 4. Install/Verify dependencies
Write-Host "Verification and installation of dependencies from requirements.txt..."
& $VENV_PYTHON -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: The pip update failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Uses requirements.txt located at the root of the BlueNotebook folder
& $VENV_PYTHON -m pip install -r "requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: The dependency installation failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Dependencies up to date." -ForegroundColor Green

# --- PATH Configuration for Cairo library (required for WeasyPrint/CairoSVG) ---
$CAIRO_PATH = $null
$cairoPaths = @(
    "C:\Program Files\GTK3-Runtime Win64\bin",
    "C:\msys64\mingw64\bin",
    "$env:USERPROFILE\msys64\mingw64\bin"
)

foreach ($path in $cairoPaths) {
    if (Test-Path $path) {
        $CAIRO_PATH = $path
        break
    }
}

if ($CAIRO_PATH) {
    Write-Host "Added '$CAIRO_PATH' to the PATH for Cairo." -ForegroundColor Green
    $env:PATH = "$CAIRO_PATH;$env:PATH"
} else {
    Write-Host "WARNING: Unable to find the Cairo library (GTK3 or msys64). PDF/SVG export may fail." -ForegroundColor Yellow
}

# Display Python info
& $VENV_PYTHON -V
& $VENV_PYTHON -m pip -V

# --- STEP 1: PyInstaller Build ---
Write-Host "`n--- STEP 1: PyInstaller Build ---" -ForegroundColor Cyan

Set-Location bluenotebook

# Install PyInstaller
& $VENV_PIP install pyinstaller pyinstaller-hooks-contrib
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller installation failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run PyInstaller
& $VENV_PYINSTALLER main.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "PyInstaller build completed." -ForegroundColor Green

# --- STEP 2: Test the built application (optional) ---
# Uncomment the following line to test the built exe
# & ".\dist\BlueNotebook\BlueNotebook.exe"

# --- STEP 3: InstallForge Generation ---
Write-Host "`n--- STEP 2: InstallForge Installer Generation ---" -ForegroundColor Cyan

Set-Location ..
Set-Location windows_installer

$ifpFile = "C:\Users\jmdig\github\BlueNotebook\windows_installer\BlueNotebook.ifp"
$installForge = "C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe"

if (-not (Test-Path $installForge)) {
    Write-Host "ERROR: InstallForge not found at $installForge" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process -FilePath $installForge -ArgumentList "-i", "`"$ifpFile`"" -NoNewWindow -Wait

Write-Host "`n--- Build Complete ---" -ForegroundColor Green
 
