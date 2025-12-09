REM ===========  Windows Python 3.11.9  ============  
REM pour Bluenotebook : Python 3.11.9 .venv_bluenotebook

cd bluenotebook
set PYTHON_VERSION=3.11.9
set VENV_NAME=.venv_bluenotebook
REM ajoute pyenv au PATH
set "PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%USERPROFILE%\.pyenv\pyenv-win\shims;%PATH%"
dir %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat
pyenv install %PYTHON_VERSION%
pyenv versions
pyenv local 3.11.9
REM  Creation de l'environnement virtuel '%VENV_NAME%'..."
"%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\python.exe" -m venv %VENV_NAME%
dir .venv_bluenotebook
set "VENV_PYTHON=%CD%\%VENV_NAME%\Scripts\python.exe"
"%VENV_PYTHON%" -m pip -V
"%VENV_PYTHON%" -m pip install --upgrade pip
"%VENV_PYTHON%" -m pip install -r "..\requirements.txt" 
"%VENV_PYTHON%" -m pip freeze  

REM # A chaque fois

REM cd bluenotebook
REM COPY ..\requirements_windows3.11.9.txt ..\requirements.txt /A /V /Y
REM set PYTHON_VERSION=3.11.9
REM set VENV_NAME=.venv_bluenotebook
REM set "PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%USERPROFILE%\.pyenv\pyenv-win\shims;%PATH%"
REM "%VENV_PYTHON%" -m pip install --upgrade pip
REM "%VENV_PYTHON%" -m pip install -r "..\requirements.txt"
REM "%VENV_PYTHON%" -m pip install  pyqt5-tools


=== activer l'environnement virtuel ====================  
Activez l'environnement virtuel. Tapez la commande suivante et appuyez sur Entrée. Cette commande exécute le script d'activation qui se trouve dans votre venv :


.\bluenotebook\.venv_bluenotebook\Scripts\activate

Vous saurez que cela a fonctionné car le nom de l'environnement virtuel 
(.venv_bluenotebook) apparaîtra au début de votre invite de commande.