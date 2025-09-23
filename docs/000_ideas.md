# Evolutions
Avec Priorités

## Fonctionnalité de backup (Priority 1)
A Spécifier
Menu Fichier --> Bacup et me nu Restore

## Ajouts d'un panneau Préferences dans BlueNotebook (Priority 2)



Menu Fichier --> Préférences
Affichage d'un panneau avec Trois Tabs

1 Général (Journal, répertoire sauvegarde,)
2 Affichages couleurs, police
3 Intégration externes/Plugins (Citation du Jour, Météo , News)

## Ajout d'un menu Statistiques (Priority 3)

Sur les notes, le mots les tags



## Ajouter une barre d'icones à BlueNotebook (Priority 3)
New + <  + Today + > + Archive + Recherche (par mots, par tags)+ export PDF + + Aide + Préferences

## Recherche tags/mots 
Panneau Navigation Champ  de recherche avec complétion pour les tags (comme Rednotebook)
affichage dans  Panneau Navigation Liste 2 colonnes (Date) : Libelle 40 Chars form JSON)
kes libelles sont cliquable --> Ouverture dans éditeur Synchro Calendier

## nuage de tags (Priority 3)

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

 