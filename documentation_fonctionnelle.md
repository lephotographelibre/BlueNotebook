## BlueNotebook : Analyse Fonctionnelle par Niveaux

### Introduction

BlueNotebook est une application de journalisation et de prise de notes conçue pour les utilisateurs qui apprécient la puissance et la portabilité du Markdown, tout en bénéficiant d'une interface graphique riche et d'outils d'organisation avancés. Ce document analyse ses fonctionnalités en quatre couches superposées, de l'outil d'écriture de base à la plateforme de gestion de la connaissance.

---

### Niveau 1 : L'Éditeur - Le Cœur de l'Expérience d'Écriture

Ce niveau concerne l'environnement d'écriture immédiat : la capacité à saisir et formater du texte de manière efficace.

#### Fonctionnalités Actuelles

*   **Éditeur Markdown Complet** : Le cœur de l'application est un éditeur de texte avec une coloration syntaxique en temps réel pour tous les éléments Markdown (titres, listes, gras, italique, code, liens, etc.).
*   **Aperçu HTML Instantané** : Un panneau d'aperçu (`F5`) affiche le rendu final de votre document, se mettant à jour quasi instantanément pendant que vous tapez.
*   **Personnalisation Visuelle Poussée** : L'utilisateur peut personnaliser entièrement l'apparence de l'éditeur via les Préférences, incluant la police, la taille, et la couleur de chaque élément syntaxique (texte, fond, titres, listes, code, tags, etc.).
*   **Gestion de Thèmes** : Possibilité de sauvegarder et de charger des thèmes de couleurs complets pour l'éditeur, permettant de basculer rapidement entre des environnements de travail (ex: "Classic Light", "Classic Dark").
*   **Menus de Formatage Accessibles** : Un menu "Formater" complet et un menu contextuel (clic droit) permettent d'appliquer rapidement des styles sans mémoriser toute la syntaxe Markdown.
*   **Aides à l'Édition** :
    *   **Numérotation des lignes** : Optionnelle, pour se repérer dans les longs documents.
    *   **Zoom dynamique** : `Ctrl + Molette` pour ajuster la taille du texte à la volée.
    *   **Nettoyage de paragraphe** : Une fonction pour fusionner les lignes et supprimer les espaces superflus, très utile après un copier-coller.

#### Pistes d'Amélioration (Ce qui pourrait être ajouté)

*   **Correcteur Orthographique** : Intégration d'un correcteur orthographique en temps réel pour souligner les fautes de frappe.
*   **Autocomplétion** : Saisie semi-automatique pour les tags (`@@...`) ou même pour des blocs de texte récurrents (snippets).
*   **Édition de Tableaux Améliorée** : Un assistant visuel pour créer et modifier des tableaux Markdown, qui peuvent être fastidieux à gérer manuellement.
*   **Modes d'Écriture** :
    *   **Mode Focus** : Estompe le texte qui n'est pas dans le paragraphe ou la phrase en cours d'édition.
    *   **Mode Machine à écrire** : Maintient la ligne active toujours au centre de l'écran.

---

### Niveau 2 : Le Journal - La Dimension Temporelle

Ce niveau se concentre sur la fonctionnalité principale de BlueNotebook : la tenue d'un journal chronologique.

#### Fonctionnalités Actuelles

*   **Une Note par Jour** : Le concept central est un fichier par jour, nommé `AAAAMMJJ.md`. Cela garantit la simplicité et la portabilité des données.
*   **Navigation Temporelle** : Le panneau de navigation (`F6`) contient un calendrier où les jours avec une note sont mis en évidence. Un clic ouvre la note correspondante. Des boutons "Précédent", "Suivant" et "Aujourd'hui" facilitent la navigation séquentielle.
*   **Gestion Intelligente de la Sauvegarde** : Lors de la sauvegarde (`Ctrl+S`), si la note du jour existe déjà, l'application propose d'ajouter le nouveau contenu à la suite, ce qui est idéal pour compléter ses pensées au fil de la journée.
*   **Sauvegarde et Restauration Complètes** : Des outils intégrés permettent de créer une archive `.zip` de l'intégralité du journal (notes, images, pièces jointes) et de la restaurer de manière sécurisée (le journal actuel est sauvegardé avant d'être remplacé).
*   **Export du Journal** : Possibilité d'exporter une sélection de notes (par plage de dates et/ou par tag) dans des formats professionnels comme le **PDF** (paginé, avec couverture) et l'**EPUB** (avec table des matières, couverture et images intégrées).

#### Pistes d'Amélioration (Ce qui pourrait être ajouté)

*   **Gestion de Plusieurs Journaux** : Permettre à l'utilisateur de définir et de basculer facilement entre plusieurs répertoires de journal (ex: "Journal Personnel", "Journal de Projet").
*   **Chiffrement** : Option pour chiffrer des notes spécifiques ou l'ensemble du journal avec un mot de passe pour une confidentialité accrue.
*   **Statistiques du Journal** : Un tableau de bord affichant des statistiques sur l'activité d'écriture (nombre de mots par jour, jours consécutifs d'écriture, tags les plus utilisés sur une période, etc.).
*   **Vue "Ce jour-là"** : Une fonctionnalité qui affiche les notes écrites à la même date les années précédentes.

---

### Niveau 3 : La Prise de Notes - Enrichir le Contenu

Ce niveau couvre les outils qui permettent de créer des notes riches et structurées, au-delà du simple texte.

#### Fonctionnalités Actuelles

*   **Système de Modèles (Templates)** :
    *   Créer des notes à partir de modèles prédéfinis (`Fichier > Nouveau...`).
    *   Sauvegarder une note actuelle comme un nouveau modèle (`Fichier > Sauvegarder comme Modèle...`).
    *   Insérer le contenu d'un modèle à n'importe quel endroit dans une note existante.
    *   Utilisation de placeholders dynamiques comme `{{date}}` et `{{horodatage}}`.
*   **Gestion des Pièces Jointes** : Une fonction "Attachement" copie n'importe quel fichier (PDF, document, etc.) dans un dossier `attachments/` du journal et insère un lien Markdown, garantissant la portabilité.
*   **Intégrations Externes Riches** : Le menu "Intégrations" permet d'enrichir les notes avec du contenu dynamique :
    *   **Cartes** : Insertion de cartes statiques à partir de coordonnées GPS ou d'une trace GPX.
    *   **Contenu Multimédia** : Intégration de vidéos YouTube (avec récupération optionnelle de la transcription).
    *   **Données contextuelles** : Ajout de la météo du jour, des données astronomiques (lever/coucher du soleil, phase de lune) ou des informations sur un livre via son ISBN.
    *   **Données EXIF** : Extraction et affichage des métadonnées d'une photo (lieu, date, appareil).
*   **Conversion PDF vers Markdown** : Outil intégré pour convertir un document PDF en texte Markdown éditable.

#### Pistes d'Amélioration (Ce qui pourrait être ajouté)

*   **Web Clipper** : Une extension de navigateur ou une fonction "Importer depuis une URL" qui capturerait le contenu d'une page web et le convertirait en Markdown propre.
*   **Enregistrement Audio** : Possibilité d'enregistrer de courtes notes vocales et de les intégrer dans une note sous forme de fichier audio cliquable.
*   **Dessin et Schémas** : Intégration d'un petit canevas de dessin pour créer des schémas simples à la main et les insérer comme des images.

---

### Niveau 4 : La Gestion de la Connaissance - Connecter les Idées

Ce niveau représente la capacité de l'application à aider l'utilisateur à organiser, retrouver et créer des liens entre ses informations.

#### Fonctionnalités Actuelles

*   **Système de Tags** : Utilisation d'une syntaxe simple (`@@tag`) pour catégoriser l'information. Les tags sont normalisés (insensibles à la casse et aux accents) pour une meilleure cohérence.
*   **Indexation Asynchrone** : Au démarrage, un processus en arrière-plan scanne tout le journal pour créer un index des tags, ce qui permet des recherches quasi-instantanées sans bloquer l'interface.
*   **Recherche par Tag** : Le panneau de navigation permet de rechercher un tag spécifique. Les résultats affichent la date et le contexte de chaque occurrence.
*   **Navigation par Clic** : Un clic sur un résultat de recherche ouvre la note correspondante et positionne le curseur **directement à la ligne où le tag a été trouvé**.
*   **Découverte Visuelle** :
    *   **Nuage de Tags** : Affiche les tags les plus utilisés, offrant une vue d'ensemble des thèmes principaux du journal. Un clic sur un tag lance une recherche.
    *   **Plan du document** (`F7`) : Affiche une vue hiérarchique des titres du document actuel, permettant de naviguer rapidement dans les notes longues et structurées.
*   **Lecteur de Documents Intégré** : Le panneau lecteur (`F8`) permet d'afficher des documents EPUB et PDF à côté de l'éditeur, facilitant la prise de notes à partir de sources externes.

#### Pistes d'Amélioration (Ce qui pourrait être ajouté)

*   **Liens Bidirectionnels (Backlinks)** : La fonctionnalité phare des outils de "second cerveau" comme Obsidian ou Roam. Pour chaque note, afficher une section listant toutes les autres notes qui pointent vers elle.
*   **Vue Graphique (Graph View)** : Une représentation visuelle du journal sous forme de réseau de nœuds (les notes) et de liens, permettant de découvrir des connexions inattendues entre les idées.
*   **Recherche Avancée** : Un moteur de recherche plus puissant avec des opérateurs booléens (`tag:projet AND NOT tag:archive`), la recherche par plage de dates, ou la recherche dans le contenu des pièces jointes (PDF, etc.).
*   **Transclusion (Inclusion de Blocs)** : La capacité d'intégrer (et d'afficher) un bloc de texte d'une autre note directement dans la note actuelle, tout en gardant le contenu synchronisé.