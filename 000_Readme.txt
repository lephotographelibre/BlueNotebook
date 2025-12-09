V4.0.1-beta - Windows C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1
=================================================

Modification de requirements.txt


V4.0.1_requirements_windows3.11.9.txt --> requirements.txt

la version windows des requirements était mauvaise V3.5.2
V4.0.1_requirements_windows3.11.9.txt a été refabriqué à partir de la version 3.3.1 du portage Windows initial.
V4.0.1_requirements_windows3.11.9.txt a été testée dans le projet testappqt5

J'ai écrasé le .venv de la V5.5.2 Windows pour en recréer un propre.

-------  Test1 -------------------------------
on reprend le .bat de la V3.5.2 on est dans bluenotebook\run_bluenotebook.bat

CD C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1\bluenotebook

on modifie le script pour copier requirements_windows3.11.9.txt --> requirements.txt

COPY C:\source\test.bin D:\backup\test.bin /B /V /Y

COPY ..\requirements_windows3.11.9.txt ..\requirements.txt /A /V /Y

------

On reprend la version V3.5.2 --> bluenotebook\run_bluenotebook.batbluenotebook\run_bluenotebook.bat

Modifications

REM --- Positionnement du repertoire du journal et locale---
REM set "JOURNAL_DIRECTORY=E:\Dropbox\BlueNotebookJournal"
REM set "BLUENOTEBOOK_LOCALE=fr_FR"

REM Transmet tous les arguments (%*) au script python
REM call "%VENV_PYTHON%" main.py %*
REM  %errorlevel% neq 0 ( echo "ERREUR: Le lancement de main.py a echoue." & pause & exit /b 1 )

--- Lancement réel

Il manque des libs dans le requirements.txt

--- erreur 1 ----------- 

ModuleNotFoundError: No module named 'geopy'

===> pip install geopy

"%VENV_PYTHON%" -m pip install geopy

"%VENV_PYTHON%" -m pip install ebooklib
"%VENV_PYTHON%" -m pip install appdirs


--- ??
résolu en recupérant requirements.txt via pip freeze d'une instance windows V3.5.2 qui fonctinnait


--------------------------

-
 
pour Bluenotebook : Python 3.11.9 .venv_bluenotebook

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
"%VENV_PYTHON%" -m pip -V
"%VENV_PYTHON%" -m pip install --upgrade pip

---------------

settings.py


        # Définir les paramètres par défaut
        self.defaults = {
            "app": {
                "language": "fr_FR",   ---> "language": "",
            },
			
			
			et
			
    locale_to_set = "en_US"  # Fallback de sécurité

    if settings_language:
        locale_to_set = settings_language
        print(f"🌍 Locale depuis settings.json : '{locale_to_set}'")
    elif forced_locale_str:
        locale_to_set = forced_locale_str
        print(f"🌍 Locale depuis variable d'environnement : '{locale_to_set}'")
    else:
        #locale_to_set = QLocale.system().name()    ==================== supresseion
        locale_to_set = "en_US" ====== NEW
        print(f"🌍 Locale système : '{locale_to_set}'")


___________________________________________________________________________
Fichers a reinjecter


main.py
main_windows.py
setup_python.bat
fichiers i18n traduits

----------------

. J'ai remplacé toutes les occurrences de print() pour utiliser MainWindowContext.tr("...").format(...), ce qui permettra une internationalisation correcte de ces messages affichés en console.

-------------------
Activer l'environnement virtuel
Ouvrez un terminal (Command Prompt ou PowerShell) dans le répertoire racine de votre projet. Le plus simple est de faire un clic droit dans le dossier BlueNotebookV4.0.1-beta1 dans l'explorateur de fichiers et de choisir "Ouvrir dans le terminal".

Activez l'environnement virtuel. Tapez la commande suivante et appuyez sur Entrée. Cette commande exécute le script d'activation qui se trouve dans votre venv :

shell
.\bluenotebook\.venv_bluenotebook\Scripts\activate
Vous saurez que cela a fonctionné car le nom de l'environnement virtuel (.venv_bluenotebook) apparaîtra au début de votre invite de commande.
-------------------------------------------
Vérifiez l'installation (si nécessaire). pylupdate5 fait partie de pyqt5-tools. Assurez-vous qu'il est bien installé en tapant :

shell
pip show pyqt5-tools

---------------------------------------------
++++ modification MANUELLE de @default par MainContext 
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en">
<context>
    <name>MainContext</name>
    <message>
        <location filename="../main.py" line="87"/>
        <source>🌍 Locale depuis settings.json : &apos;{0}&apos;</source>
        <translation>🌍 Locale from settings.json: &apos;{0}&apos;</translation>

-----------------------
Dans VScode

pylupdate5 main.py gui/main_window.py -ts i18n/bluenotebook_en.ts
pylupdate5 main.py gui/main_window.py -ts i18n/bluenotebook_fr.ts


dans le repertoire C:\Program Files (x86)\Qt Linguist\bin
C:\Program Files (x86)\Qt Linguist\bin>lrelease C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1\bluenotebook\i18n\bluenotebook_en.ts C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1\bluenotebook\i18n\bluenotebook_en.qm
Updating 'C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1\bluenotebook\i18n\bluenotebook_en.qm'...
    Generated 41 translation(s) (41 finished and 0 unfinished)
Updating 'C:\Users\jmdig\github\BlueNotebookV4.0.1-beta1\bluenotebook\i18n\bluenotebook_en.qm'...
    Generated 41 translation(s) (41 finished and 0 unfinished)