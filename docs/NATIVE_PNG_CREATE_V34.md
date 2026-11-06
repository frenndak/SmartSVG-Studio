# Création de projet PNG dans le logiciel autonome — V3.4

Ce lot raccorde la première création et sauvegarde V1 au bureau Python/Tk. Base de départ : `main@c9cececbc55a78ac37f9b62cf6a372e48f8fc66c`, après #121 ; les résultats d'intégration du candidat sont consignés dans sa PR. Rattachement partiel : V34-018/025/041/042/044/048, avec protection du writer V1 existant ; aucun ticket complet ni schéma V2 qualifié par ce seul parcours.

## Parcours réellement raccordé

Accueil ou Projet → **Créer depuis un PNG…** (Ctrl+N) → choisir le PNG et le dossier → nom/intention/largeur mm/DPI → **Créer et ouvrir**. Le fichier est placé dans `SmartSVG_Managed_Projects/<nom>.smartsvg` sous le dossier explicitement choisi.

Le dossier de travail n'est pas créé par la navigation ou par l'annulation du formulaire. Le port valide les paramètres et le PNG avant d'instancier le workspace. La création conserve les octets source et les paramètres ; elle ne produit pas de masque, de sujet détecté ou d'export. Le nom suit les contraintes historiques ASCII (1–48 caractères) et les noms réservés Windows sont refusés ; le dossier peut comporter des caractères Unicode.

La confirmation « Projet créé, enregistré et relu » suit le retour du writer, une relecture liée au SHA retourné et le contrôle de la source et des paramètres persistés. La fenêtre ouvre ensuite le fichier par le lecteur natif existant. Une vérification échouée après publication reste **non confirmée** : vérifier les fichiers, sans suppression ni retry automatique.

## Réemploi et frontière de mutation

- [Port natif](../engine/smartsvg_core/native_project_create_v34.py) : lecture bornée d'un fichier PNG ordinaire, validation par les fonctions existantes, création via `ManagedWorkspace.create`, relecture V1 et reçu SHA. La provenance native utilise le champ V1 existant ; l'origine navigateur reste la valeur par défaut pour les anciens consommateurs.
- [Formulaire Tk](../engine/native_create_tk_v34.py) : une seule création active, paramètres capturés avant le worker, statut sur le thread Tk, actions/diagnostic réservés en bas et chemins affichés de façon bornée sans changer les chemins utilisés, double activation ignorée et fermeture différée pendant l'écriture. Aucun usage de `LatestOnlyJob` pour une écriture.
- [Writer existant](../engine/smartsvg_core/project_recovery.py) : option `require_absent`, désactivée par défaut pour les sauvegardes existantes ; la création gérée l'active. Sous le verrou OS, présence d'un primaire ou d'un secours/pending interdit la création. La publication initiale existante par lien atomique reste sans écrasement.
- [Entrée bureau](../engine/standalone_desktop_v34.py) : création explicite depuis Accueil/Projet, fermeture et ouverture d'un autre projet différées pendant cette création ; réouverture du reçu vérifié. Les projets déjà existants restent en lecture seule dans cette version.

La correction du contrôle sous verrou ferme un cas reproduit : deux créateurs pouvaient passer le premier test d'absence, puis le second traiter le premier projet comme une mise à jour. Les sauvegardes ordinaires, CAS, recovery, float32 et anciens contrats restent en place.

## Bornes et erreurs visibles

PNG 8 bits L/RGB/RGBA non entrelacé, jusqu'à 12 Mio et 20 millions de pixels, largeur de 5 à 300 mm, résolution 300 ou 450 DPI. L'intention configure le projet initial ; elle n'exécute pas encore le traitement associé. Les formats non pris en charge sont refusés explicitement.

L'aperçu garde ses limites distinctes (8 Mio, 5 millions de pixels) : un projet valide peut être enregistré et ouvert avec « image trop grande pour l'aperçu sécurisé ». Les pixels source ne sont pas réduits pour contourner cette borne. Une miniature dérivée reste une amélioration ultérieure.

Doublon, nom réservé, PNG illisible/invalide, dossier indisponible, paramètres invalides et création non confirmée ont un retour FR ; aucune erreur de worker n'expose une trace Python ou un chemin privé dans les logs UI. Un projet existant n'est jamais remplacé par une création.

## Preuves à lire au SHA du candidat

- [Tests port/writer](../tests/test_v34_native_project_create.py) : vrai roundtrip V1, PNG et réglages conservés, doublon et course reproduite, secours orphelins préservés, erreurs d'écriture, résultat périmé refusé, grande source valide sans aperçu.
- [Tests du formulaire](../tests/test_v34_native_create_ui.py) : annulation sans écriture, paramètres capturés, double activation sans seconde soumission, fermeture différée, erreur puis possibilité de correction.
- [Tests d'intégration et Tk](../tests/test_v34_native_app_shell.py) : vrai bouton de l'accueil, vrai worker/writer/lecteur, reçu visible et source relue ; parcours graphique réel lorsque Tk et une session graphique sont disponibles. Un skip sans écran n'est pas une validation graphique.
- Probe isolé : expose la création disponible et la lecture seule des projets existants ; il ne lance ni fenêtre, ni écriture, ni serveur ComfyUI.

Prochain travail : session commune et commandes de sauvegarde/reprise des opérations existantes (étape 2 de la [roadmap d'exécution](roadmap-v3.4/EXECUTION_ET_INTEGRATION_2026_11_06.md)). Édition native, sauvegarde de retouches, recovery depuis le bureau, exports et installateur restent à raccorder/qualifier séparément. Les tests automatiques continuent sur fixtures autorisées sans solliciter un projet personnel.
