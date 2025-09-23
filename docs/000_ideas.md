# Evolutions
Avec Priorités

## Fonctionnalité de backup (Priority 1)

"Backup" in the "Fichier" menu saves all your entered data in a zip file.
A Spécifier
Menu Fichier --> Backup et  Restore

### Rednotebook ---> Backup
fichier -> Backup Select backupfilename dans file Manager RedNotebook-Backup-RedNotebookDropbox-2025-09-23.zip

## Ajouts d'un panneau Préferences dans BlueNotebook (Priority 2)



Menu Fichier --> Préférences
Affichage d'un panneau avec Trois Tabs

1 Général (Journal, répertoire sauvegarde,)
2 Affichages couleurs, police
3 Intégration externes/Plugins (Citation du Jour, Météo , News)

## Ajout d'un menu Statistiques (Priority 3)

Sur les notes, le mots les tags

## Report a problem (Priority 3)

add menu Aide --> Signaler un problème
--> envoi vers Github comme rednotebook  https://github.com/jendrikseipp/rednotebook/issues
--> https://github.com/lephotographelibre/BlueNotebook/issues

## Spell check for editor (Priority 3)

## Ajouter une barre d'icones à BlueNotebook (Priority 3)
New + <  + Today + > + Archive + Recherche (par mots, par tags)+ export PDF + + Aide + Préferences

## Recherche tags/mots 
Panneau Navigation Champ  de recherche avec complétion pour les tags (comme Rednotebook)
affichage dans  Panneau Navigation Liste 2 colonnes (Date) : Libelle 40 Chars form JSON)
kes libelles sont cliquable --> Ouverture dans éditeur Synchro Calendier

## nuage de tags as Rednotebook (Priority 3)
comme dans rednotebook

## Gestion de templates (Priority 2)

Template par defaut
Rendez-vous téléphonique

save as ... templates dans répertoires bluenotebook/resources/templates/ au format .md

## Export Wizard as Rednotebook (Priority 3)

--> PLain texte
--> HTML
--> Word
--> ODT

## Template HTML (priority 3)

A la fois pour l'apercu et pour l'export 
CSS ?

## Storageformat for perf (Priority 4)

### Rednotebook
```
24: {text: "This is a normal text entry."}
25:
  Ideas: {"Invent Anti-Hangover machine": null}
  text: "This is another text entry, shown in the main text area."

  ```
As you can see, the data format uses a dictionary (hashmap) for storing the information. The outer dictionary has the day numbers as keys and the day content as values. The day values consist of another dictionary. It can have a key "text" whose value will be inserted in the main content area. Additionally there can be multiple other keys that stand for the categories that belong to that day. Each category contains a dictionary mapping category entries to the null value.

## Command line options (Priority 3)
### Rednotebook
usage: rednotebook [-h] [--version] [--date START_DATE] [journal]

RedNotebook is a modern desktop journal. It lets you format, tag and
search your entries. You can also add pictures, links and customizable
templates, spell check your notes, and export to plain text, HTML or
Latex.

positional arguments:
  journal            (optional) Specify the directory storing the journal data.
                     The journal argument can be one of the following:
                      - An absolute path (e.g. /home/username/myjournal)
                      - A relative path (e.g. ../dir/myjournal)
                      - The name of a directory under $HOME/.rednotebook/ (e.g. myjournal)
                     
                     If the journal argument is omitted then the last session's journal
                     path will be used. At the first program start, this defaults to
                     "$HOME/.rednotebook/data".

options:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  --date START_DATE  load specified date (format: YYYY-MM-DD)
## Windows specifics  (Priority 2)
.bat , launch, Python env, 

### Rednotebook doc
You can use a GTK3 compatible theme to change the appearance of your RedNotebook installation. Once you find a GTK3 compatible theme, copy the theme into <RedNotebook Dir>\share\themes, e.g., C:\Program Files (x86)\RedNotebook\share\themes and then edit C:\Program Files (x86)\RedNotebook\etc\gtk-3.0\settings.ini to comment out the current theme setting and add your own.

For example, for using the FlatStudio theme, download the *.tar.gz file and extract it. Out of the four themes -- FlatStudio, FlatStudioDark, FlatStudioLight, FlatStudioGray -- pick one of the folders (e.g., FlatStudioDark) and copy it into <RedNotebook Dir>\share\themes. Then edit etc\gtk-3.0\settings.ini so it looks similar to this:

```
[Settings]
# gtk-theme-name=win32
gtk-theme-name=FlatStudioDark

```
Finally, relaunch RedNotebook.

Alternative 1: set GTK_THEME=FlatStudioDark in user environment variables. This overrides the theme set in settings.ini and persists even after reinstalling RedNotebook. However, this might change the theme of every GTK application on Windows.

Alternative 2: set GTK_THEME=FlatStudioDark in the application shortcut as follows:

C:\Windows\System32\cmd.exe /c "SET GTK_THEME=FlatStudioDark&& ^
START /D ^"C:\Program Files (x86)\RedNotebook^" rednotebook.exe"
Then set application to Run: Minimized (in application shortcut properties). This also overrides the theme set in settings.ini. This won't affect any other app but it does change the shortcut icon to a cmd icon, as expected.



## Portable Mode as Rednotebook (Priority 3)

RedNotebook can be run in portable mode. In this mode, the template directory, the configuration and the log file are saved in the application directory instead of in the home directory. Additionally, the path to the last opened journal is remembered relatively to the application directory.

To use RedNotebook on a flash drive on Windows, run the installer and select a directory on your USB drive as the installation directory. You probably don't need the "Start Menu Group" and Desktop icons in portable mode.

To activate portable mode, change into the files/ directory and in the default.cfg file set portable=1.

## Encryption as Rednotebook (Priority 34)

You can use e.g. TrueCrypt to encrypt your journal. The general idea is to create and mount an encrypted folder with TrueCrypt and put your journal files in there.

In many Linux distributions it has become pretty easy to encrypt your entire home partition. I would recommend to do that to anyone who wishes to protect her/his diary and all other personal files. This method is especially useful for laptop users, because their computers are more likely to be stolen. If you encrypt your home partition all RedNotebook data will be encrypted, too.


## Complétion Automatique des Tags (Priority 4)

*   **Complétion Automatique** : Proposer une complétion automatique des tags existants lors de la saisie de `@@...` dans l'éditeur. ou dans la barre de recherche

##  Mode sombre / Thèmes personnalisables (Priority 4)
```python
class ThemeManager:
    themes = {
        'light': {...},
        'dark': {...},
        'high_contrast': {...}
    }
    
    def apply_theme(self, theme_name: str):
        # Application CSS dynamique
        # Mise à jour des couleurs de coloration syntaxique  
        # Persistance des préférences utilisateur
```



## Export Journal PDF natif (Priority 2)
```python
class PDFExporter:
    def export_to_pdf(self, html_content: str, output_path: str):
        # Utilisation de QWebEngine.printToPdf()
        # Styles CSS optimisés pour l'impression
        # Gestion des marges et en-têtes/pieds de page
```

  


#### 6. Plugin system pour extensions (Priority 3)
```python
class PluginManager:
    def load_plugin(self, plugin_path: str):
        # Chargement dynamique des modules Python
        # API standardisée pour extensions
        # Sandbox de sécurité
        
class PluginAPI:
    # Interface pour développeurs tiers
    def add_menu_item(self, name: str, callback: callable): ...
    def register_parser(self, extension: str, parser: callable): ...
    def add_export_format(self, format: str, exporter: callable): ...
```

 

**Technologies** : WebSocket, Operational Transform, serveur Node.js/Python.

#### 8. Mode présentation (reveal.js) (Priority 5)
```python
class PresentationMode:
    def export_slides(self, markdown_content: str):
        # Conversion Markdown → reveal.js
        # Thèmes de présentation
        # Export standalone HTML
        # Mode plein écran avec contrôles clavier
```

**Séparateurs de slides** :
```markdown
# Slide 1
Contenu...

---

# Slide 2  
Autre contenu...
```
 
 

## Intégration Git (Priority 3)
```python
class GitIntegration:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        
    def show_diff(self, file_path: str):
        # Affichage différences dans interface
        # Gutter avec ajouts/suppressions
        # Commit et push directement depuis l'éditeur
```

## Support cloud (GitHub, GitLab, Notion) (Priority 3)
```python
class CloudSync:
    def sync_with_github(self, repo_url: str):
        # API GitHub pour synchronisation
        # Gestion des conflits automatique
        # Publication GitHub Pages
        
    def export_to_notion(self, page_id: str):
        # Conversion Markdown → blocs Notion
        # Synchronisation bidirectionnelle
```


## Utilité et Évolutions Possibles des tags (Priority 2)

Ce système de tagging et d'indexation ouvre la porte à de nombreuses fonctionnalités puissantes :

*   **Recherche par Tag** : Créer une interface de recherche où l'utilisateur peut cliquer sur un tag pour voir instantanément toutes les notes et les contextes où il apparaît.
*   **Nuage de Tags (Tag Cloud)** : Visualiser les tags les plus utilisés dans le journal, avec une taille de police proportionnelle à leur fréquence.
*   **Navigation Thématique** : Permettre de filtrer le journal pour n'afficher que les entrées relatives à un `@@projet` spécifique.
*   **Rapports et Analyses** : Utiliser les fichiers `CSV` ou `JSON` pour générer des statistiques sur les thèmes abordés au fil du temps.
*   **Complétion Automatique** : Proposer une complétion automatique des tags existants lors de la saisie de `@@...` dans l'éditeur.

 