# Réflexions sur une Architecture de Plugins pour BlueNotebook

Ce document a pour but d'explorer les concepts et les approches pour créer un système de plugins (ou "intégrations") générique, robuste et évolutif pour BlueNotebook.

## 1. Objectifs et Principes Fondamentaux

Un bon système de plugins doit respecter plusieurs principes clés :

1.  **Découplage Fort** : Le code de l'application principale ne doit jamais dépendre directement d'un plugin spécifique. Les plugins sont des "invités" qui s'enregistrent auprès de l'application.
2.  **Découverte Automatique** : L'application doit être capable de détecter, charger et lister les plugins disponibles sans modification de son propre code. Un simple ajout de dossier dans un répertoire `plugins/` devrait suffire.
3.  **API Claire et Stable** : Les plugins interagissent avec BlueNotebook via une "Interface de Programmation d'Application" (API) bien définie. Cette API est un contrat : elle définit ce que le plugin peut demander à l'application (ex: "ajoute cet item au menu") et ce que l'application attend du plugin.
4.  **Gestion du Cycle de Vie** : L'application doit gérer le chargement, l'initialisation, l'activation/désactivation et le déchargement propre des plugins.
5.  **Extensibilité des Préférences** : Les plugins doivent pouvoir ajouter leurs propres options de configuration dans la fenêtre des Préférences de manière automatique.

---

## 2. Proposition d'Architecture pour BlueNotebook

Voici une approche concrète, inspirée des systèmes de plugins de nombreux éditeurs de texte et IDE.

### a. La Structure d'un Plugin

Chaque plugin serait un simple dossier placé dans un nouveau répertoire `bluenotebook/plugins/`.

**Exemple avec un plugin "Météo" :**

```
bluenotebook/
├── plugins/
│   └── meteo/
│       ├── __init__.py         # Fichier principal du plugin
│       ├── plugin.json         # Métadonnées (nom, auteur, version...)
│       └── preferences_widget.py # Widget pour les préférences (optionnel)
│
└── core/
    ├── plugin_manager.py     # Le gestionnaire qui charge les plugins
    └── plugin_api.py         # L'API et la classe de base des plugins
```

#### Le fichier de métadonnées `plugin.json`

Ce fichier simple décrit le plugin. Il est essentiel pour la découverte.

```json
{
    "name": "Météo du Jour",
    "version": "0.1.0",
    "author": "Jean-Marc DIGNE",
    "description": "Insère la météo actuelle pour une ville donnée.",
    "entry_point": "meteo:MeteoPlugin" 
}
```
*   `entry_point`: Indique au gestionnaire de plugins où trouver la classe principale (`MeteoPlugin` dans le fichier `meteo/__init__.py`).

### b. L'API du Plugin (`plugin_api.py`)

On définit une classe de base que tous les plugins devront hériter. C'est le "contrat" à respecter.

```python
# bluenotebook/core/plugin_api.py

class BlueNotebookPlugin:
    """Classe de base pour tous les plugins de BlueNotebook."""

    def __init__(self, main_window):
        self.main_window = main_window

    def get_metadata(self):
        """Retourne les métadonnées du plugin (chargées depuis plugin.json)."""
        # Cette méthode sera gérée par le PluginManager
        pass

    def register_actions(self):
        """
        Doit retourner une liste d'objets QAction à ajouter au menu 'Intégrations'.
        Exemple: return [self.my_action]
        """
        return []

    def register_preferences_widget(self):
        """
        Doit retourner un tuple (nom_onglet, QWidget) pour les Préférences.
        Exemple: return ("Météo", MeteoPreferencesWidget())
        """
        return None

    def shutdown(self):
        """Appelé lorsque le plugin est désactivé ou que l'application se ferme."""
        pass
```

### c. Le Gestionnaire de Plugins (`plugin_manager.py`)

C'est le chef d'orchestre. Il est responsable du chargement dynamique.

```python
# bluenotebook/core/plugin_manager.py
import os
import json
import importlib

class PluginManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugins = []
        self.plugins_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')

    def discover_and_load_plugins(self):
        """Scanne le dossier des plugins et charge chaque plugin valide."""
        for plugin_name in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            if not os.path.isdir(plugin_path):
                continue

            # 1. Lire les métadonnées
            try:
                with open(os.path.join(plugin_path, 'plugin.json'), 'r') as f:
                    metadata = json.load(f)
                module_name, class_name = metadata['entry_point'].split(':')
            except (FileNotFoundError, KeyError):
                print(f"⚠️ Plugin '{plugin_name}' ignoré: plugin.json invalide.")
                continue

            # 2. Charger dynamiquement le module et la classe
            try:
                # Ajoute temporairement le dossier du plugin au path
                sys.path.insert(0, plugin_path)
                plugin_module = importlib.import_module(module_name)
                plugin_class = getattr(plugin_module, class_name)
                
                # 3. Instancier le plugin
                plugin_instance = plugin_class(self.main_window)
                plugin_instance._metadata = metadata # Attacher les métadonnées
                self.plugins.append(plugin_instance)
                print(f"✅ Plugin '{metadata['name']}' chargé.")

            except Exception as e:
                print(f"❌ Erreur lors du chargement du plugin '{plugin_name}': {e}")
            finally:
                sys.path.pop(0) # Nettoyer le path

    def register_all_plugins(self):
        """Appelle les méthodes d'enregistrement de chaque plugin chargé."""
        for plugin in self.plugins:
            # Enregistrer les actions de menu
            for action in plugin.register_actions():
                self.main_window.integrations_menu.addAction(action)

            # Enregistrer le widget de préférences
            pref_widget_info = plugin.register_preferences_widget()
            if pref_widget_info:
                tab_name, widget = pref_widget_info
                # Ici, il faudrait une méthode dans PreferencesDialog pour ajouter un onglet
                # self.main_window.preferences_dialog.add_plugin_tab(tab_name, widget)
```

### d. Intégration dans `main_window.py`

Au démarrage, il suffirait d'appeler le `PluginManager`.

```python
# Dans MainWindow.__init__()
from core.plugin_manager import PluginManager

# ... après la création des menus ...
self.plugin_manager = PluginManager(self)
self.plugin_manager.discover_and_load_plugins()
self.plugin_manager.register_all_plugins()
```

---

## 3. Questions à se poser pour aller plus loin

1.  **Gestion des dépendances** : Que se passe-t-il si un plugin a besoin d'une bibliothèque externe (ex: `requests`) ?
    *   *Approche simple* : Le documenter et demander à l'utilisateur de l'installer (`pip install -r plugins/meteo/requirements.txt`).
    *   *Approche avancée* : Le `PluginManager` pourrait lire un `requirements.txt` et tenter d'installer les dépendances.

2.  **API de l'Éditeur** : Comment un plugin peut-il interagir avec le texte ?
    *   L'API doit exposer des méthodes sûres. Au lieu de donner un accès direct au widget `QTextEdit`, on pourrait fournir des méthodes sur `main_window.editor` comme :
        *   `editor.get_selected_text()`
        *   `editor.insert_text_at_cursor(text)`
        *   `editor.replace_selection(text)`

3.  **Activation / Désactivation** : Comment permettre à l'utilisateur d'activer ou de désactiver un plugin sans le supprimer ?
    *   Il faudrait un onglet "Plugins" dans les Préférences, listant les plugins découverts avec une case à cocher "Activé".
    *   Le `PluginManager` ne chargerait que les plugins marqués comme actifs dans `settings.json`.

4.  **Communication Plugin -> Application** : Comment un plugin notifie-t-il l'application d'un événement ?
    *   Le système de signaux et slots de Qt est parfait pour cela. Le plugin peut définir ses propres signaux (`pyqtSignal`) et l'application peut s'y connecter.

5.  **Sécurité** : Un plugin est du code Python qui s'exécute avec les mêmes droits que l'application.
    *   Pour une première version, on peut faire confiance aux plugins.
    *   Pour un système public, il faudrait réfléchir à des mécanismes de "sandboxing" (bac à sable), mais c'est très complexe.

Cette architecture modulaire est un excellent point de départ. Elle sépare clairement les responsabilités et rend l'ajout de nouvelles intégrations (comme "Carte GPS" ou "Vidéo YouTube") beaucoup plus simple et propre : il suffirait de les transformer en plugins respectant ce format.

