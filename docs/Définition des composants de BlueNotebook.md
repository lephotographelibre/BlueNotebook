## Définition des composants de BlueNotebook

**Journal BlueNotebook**: C'est l'ensemble des outils de gestion et d'édition des documents sous le contrôle de BlueNotebook

**Répertoire du Journal**: Contient l'ensemble des éléments gérés par BlueNotebook (Notes Journalière, Attachements, Images, Notes, Index de tags). C'est ce répertoire qui est Sauvegardé/Restauré par les outils intégrés de BlueNotebook.

**Note Journalière**: Entrée du journal sous la forma d'un fichier Markdown qui est stocké dans le répertoire du `Journal`

**Notes**: Un document au format Makdown, généralement créé par l'Editeur Markdown intégré, qui peut contenir des images, des liens, des attachements et qui sera sauvegardé dans un sous-répertoire du dossier  
`Journal/notes`. Peut utiliser des modèles de document spécifiques créé par BlueNotebook ou l'utilisateur.

**Inages du Journal**: ce sont les images qui on été insérées au format Markdown dans les pasges du Journal, Notes ou attachements. Elles sont stockées automatiquement au moment de l'inssertion dans le répertoire `Journal/images`.

**Attachement**: ce sont des documents locaux en piece jointe qui sont rattachés aus notes journalières ou notes et qui sont accessibles via un lien Markdown. Au moment de l'insertion du lien de type Attachement le document local ou distants est copié dans le répertoire du journal `Journal/attachments`. Ils sont identifiables dans le document Markdown par l'icone 📎.

**Tag**: Un tag Bluenotebook est un mot clé spécifique qui est précédé de deux @ dans les Notes Journalières au format Markdown gérées par le journal. Ces tags sont automatiquement indexés et on peut les retouver dans les documents via l'interface de recherche du volet Navigation. Un tag spécifficque @@TODO est utilisé pour élaborer une liste des "tâches à faire" visible par défaut dans l'ongle Navigation.

**Sauvegarde du Journal**: Bluenotebook permet de Sauvegarder/Récupérer l'ensemble du journal (Notes Journalieres, Notes, Attachemenst, Images) dans un fichier archive .zip. Ce fichier est horodaté. Il est conseiller de sauvegarder ces fichiers sauvegarde dans un répertoire autre que le répertoire du `Journal`. Cette sauvegarde permettra de récuperer ou transferer l'ensemble du journal à partir de ce fichier (dans un autre réertoire, une autre machine, un autre OS).

**Export du Journal**: On peux exporter la totalité des notes journalières du Journal ou seulement une partie dans un fichier EPUB ou PDF. Les critères de filtrage de l'exportation peuvent être:

- Un plage de dates (début, fin ou toutes les dates)
- Un critère de sélecion basé sur un Tag spécifique en plus de la plage de date

L'export du journal pourra être personnalisé avec in Titre, Un Auteur, une image de couverture.

**Modèle/Templates**: Les modèles sont des structures de notes pré-remplies qui vous permettent de démarrer rapidement votre travail. BlueNotebook vous offre une gestion complète des modèles pour créer, utiliser et insérer des structures récurrentes. Il est possible de créer ses propre modèles. On peut à tout instant insérer un modèle dans un fichier Markdown en cours d'édition. Pour rendre vos modèles encore plus puissants, vous pouvez utiliser des "placeholders" qui seront automatiquement remplacés lors de l'utilisation du modèle :

- {{date}} : Sera remplacé par la date complète du jour (ex: "Lundi 28 Octobre 2025").
- {{horodatage}} : Sera remplacé par l'heure actuelle (ex: "14:32").

**Intégrations**: BlueNotebook peut interagir avec des services externes pour enrichir vos notes. Ces fonctionnalités se trouvent dans le menu Intégrations. Ces services externes sont appelés de manière transparentes et vienne inserer du code Markdown spécifique contenant des informations spécifique à l'intégration choisie (météo, Vido YT, Carte à partir des coordonnées GPS ou fichier de trace GPX). Ceratines Intégrations nécessitent un paramètrage spécifique qui sera fourni dans le menu Préférences6> Intégrations" (User key, localisation, etc)

**Préférences Utilisateur**: Les préférences utilisateurs (thèmes couleurs, polices, répertoires,...) osnt persisté dans un fichier `settings.json` à la racine du répertoire utilisateur ( `~/.config/BlueNotebook/settings.json` sur Linux, `C:\Users\nom_utilisateur\BlueNotebook\settings.json` sous Windows)