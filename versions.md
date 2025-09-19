## V1.1.3 Fix Bug #1 Cannot see HTML fragment pasted into the editor

       padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                color: #2c3e50;   ---> Ajouté
                selection-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }

## V1.1.2   Création d'en script de lancement

Je voudrais un script bash pour linix et un script pour windows pour lancer le programme bluenotebook. sur Linux bien vérifier que l'in est dasn un terminal bash ce script doit positionner l'environnement virtuel pyenv nommé .venv_bluenotebook avec Python 3.13.5, verifier le bon chargements des packages qui sont dans requirements.txt, puis lancer le programme main.py

1
bluenotebook$ ./run_bluenotebook.sh   --> Par defaut Journal dossier bluenotebook dans répertoire utilisateur
2
bluenotebook$ ./run_bluenotebook.sh --journal "/ssd/Dropbox/bluenotebook"
3
bluenotebook$ export JOURNAL_DIRECTORY="/home/jm/Work/BlueNotebook/"
bluenotebook$ ./run_bluenotebook.sh

et mettre a jour le dossier technique docs/V1.0 bluenotebook_technical_doc.md avec les nouvelles fonctionnalités décrites dans versions.md. 
Remettre à jour l'aborecence des fichiers

## V1.1.1   Fix gestion variable d'environnement JOURNAL_DIRECTORY

## V1.1.0   Gestion du répertoire Journal

### gestion du répertoire du journal DONE

Par défaut le répertoire de stockage du journal est créé dans le repertoire utilisateur et se nomme bluenotebook. 

Le répertoire du journal est positionné soit par une variable d'nvironnement JOURNAL_DIRECTORY sous Linix, soit passé comme paramètre optionnel sur la ligne de commande lors du lancement du journal -j ou --journal "répertoire du journal"

Au lancement de l'application on vérifira qu'un de ces cas est vrai
- il y   une variable d'environnement JOURNAL_DIRECTORY qui pointe vers un répertoire qui existe
- un paramtre de la ligne de commande au lancement est -j ou --journal "répertoire" qui pointe sur un répertoire qui existe
- un répertoire du journal existe  dans le repertoire utilisateur et se nomme bluenotebook
- si aucun de ces cas est vrai on crée un répertoire journal dans le répertoire utilisateur et se nomme bluenotebook

Le réperttoire du journal sera affiché dans la barre de texte tout en bas de l'application à coté du nom de fichier ouvert

un fichier journal contient des fichiers au format Markdown dont le nom de fichier est sous la forme YYYYMMJJ.md

Quand on sauvegarde un nouveau fichier par le Menu Fichier->Sauvergarde le fichier en cours sera sauvegardé dans le répertoire du journal automatiquement sous la le nom YYYYMMJJ.md 
Si un fichier existe déja sous ce nom là le contenu du fichier courant sera ajouté à la fin du fichier existant ou remplacera le fichier existant. Une boite de dialogue  permettra à l'utilisateur de sélectionner lors de la sauvegarde "Fichier Journal déja existant --> choix Remplacer ou Ajouter à la fin"

Dans le Menu Fichiers en dessous "Ouvrir" sera créé un  nouvel item qui est "Ouvrir Journal" qui permet de forcer le choix d'un répertoire comme répertoire Jource. Cette action prendra le pas sur toutes les autres possibilités. Le répertoire sélectionné sera affiché dans la barre de texte tout en bas de la fenetre de l'application à coté du nom de fichier ouvert

Lors du lancement de l'application vérifier s'il existe un fichier journal dans le répertoire du journal qui porte la date du jour c'est a dire dans le format YYYYMMJJ.md. Si c'est le cas ouvrir ce fichier

Au lancement de l'application afficher le répertoire journal dans le terminal

## V1.0    Première release avec Qt (editeur Markdown + Preview)