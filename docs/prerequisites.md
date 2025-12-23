# Installation Prerequisites for BlueNotebook

This document lists all the system dependencies (for Ubuntu/Debian) and Python packages required to run the BlueNotebook application and all its features.

## 1. System Prerequisites (Ubuntu/Debian)

### pyenv install

Install pyenv using <https://github.com/pyenv/pyenv-installer>

```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

add these lines to .bash_profile

```bash
# User specific environment and startup programs
#
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

add this line to .bashrc

```bash
eval "$(pyenv virtualenv-init -)"
```

These packages provide the base libraries required for certain graphical and export features.

### Essential Dependencies

These packages are required for map generation (GPS, GPX) and PDF/EPUB export.

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv libcairo2-dev libpango-1.0-0 libgdk-pixbuf2.0-0
# When running into a VM/Container You may have to install sound packages for QWebEngineView
sudo apt-get install libasound2t64
# if emojis not installed
sudo apt install fonts-noto-color-emoji
```

*   `python3-pip`: For installing Python packages.
*   `python3-venv`: For creating isolated virtual environments.
*   `libcairo2-dev`: Required by `py-staticmaps` and `cairosvg` for drawing and image manipulation.
*   `libpango-1.0-0` and `libgdk-pixbuf2.0-0`: Required by `WeasyPrint` for PDF export.

### Development Dependencies (Optional)

If you wish to contribute to the development, especially for translating the interface, install the Qt tools.

```bash
sudo apt-get install qttools5-dev pyqt5-dev-tools
```

*   `qttools5-dev`: Provides the **Qt Linguist** graphical application.
*   `pyqt5-dev-tools`: Provides the command-line tools `pylupdate5` and `lrelease`.

## 2. Python Prerequisites

It is strongly recommended to install these packages in a virtual environment.

```bash
# 1. Create a virtual environment
python3 -m venv .venv_3.11.13

# 2. Activate it
source .venv_3.11.13/bin/activate

# 3. Install all required packages
# Linux
pip install -r requirements.txt
```

### List of Python Packages (`requirements.txt`)

Here is the list of Python dependencies used by the project:

*   **Core application:**
    *   `PyQt5`: The framework for the graphical interface.
    *   `PyQtWebEngine`: For the HTML preview panel.
    *   `markdown`, `Pygments`, `pymdown-extensions`: For Markdown conversion and highlighting.
    *   `requests`: For network requests (weather, quote, YouTube).
    *   `beautifulsoup4`, `lxml`: For parsing HTML content.
    *   `appdirs`: For finding system configuration directories.

*   **Optional features (included in `requirements.txt`):**
    *   `gpxpy`, `py-staticmaps[cairo]`, `geopy`: For GPS and GPX map integration.
    *   `Pillow`, `EbookLib`, `cairosvg`: For exporting to EPUB format.
    *   `WeasyPrint`: For exporting to PDF format.

## 3. System Prerequisites (Windows)

### pyenv

++++ Powershell Admin system: Windows-X Terminal (Administrator)
https://github.com/pyenv-win/pyenv-win

PS C:\Users\jmdig> Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Reopen PowerShell
PS C:\Users\jmdig> pyenv --version
pyenv 3.1.1

Add the following to your PATH variable
Instructions for those who are unsure about how to add PATH, search in Windows for Advanced system settings
"search System".--> "Show advanced system settings"
Click Environment Variables. In the section System Variables, add a new PATH environment variable
"Environment Variables". --> PATH Edit

C:\Users\jmdig\.pyenv\pyenv-win\bin
C:\Users\jmdig\.pyenv\pyenv-win\shims

C:\Users\jmdig>pyenv local 3.11.9

C:\Users\jmdig>python -V
Python 3.11.9

On Windows, virtual environment management is not a core feature of pyenv-win.
It is provided by a separate plugin called pyenv-virtualenv.

C:\Users\jmdig>git clone https://github.com/pyenv/pyenv-virtualenv.git "$(pyenv root)\plugins\pyenv-virtualenv"

### Cairo

how to install libcairo-2.dll on windows 11

https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

Add PATH --> C:\Program Files\GTK3-Runtime Win64\bin

where libcairo-2.dll
