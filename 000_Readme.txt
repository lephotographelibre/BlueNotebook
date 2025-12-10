Readme.txt windows 4.0.x
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


====  Powershell translate tous les fichier *.py d'un répertoire (marche moyennement mais a garder)
PS C:\Users\jmdig> cd .\github\
PS C:\Users\jmdig\github> cd .\BlueNotebook\
PS C:\Users\jmdig\github\BlueNotebook> cd .\bluenotebook\
PS C:\Users\jmdig\github\BlueNotebook\bluenotebook> .venv_bluenotebook\Scripts\activate

(.venv_bluenotebook) PS C:\Users\jmdig\github\BlueNotebook\bluenotebook> pylupdate5 -verbose (Get-ChildItem core/*.py).FullName -ts i18n/bluenotebook_en.ts

Updating 'i18n/bluenotebook_en.ts'...
    Found 8 source texts (8 new and 0 already existing)
    Kept 0 obsolete translations
    Removed 41 obsolete untranslated entries
(.venv_bluenotebook) PS C:\Users\jmdig\github\BlueNotebook\bluenotebook>