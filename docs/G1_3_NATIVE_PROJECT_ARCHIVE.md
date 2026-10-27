# SmartSVG G1.3 — Sauvegarde native .smartsvg (PR empilée sur G1.2)

**Périmètre :** format d'archive non exécutable, portable, réouvrable et vérifié. Le code de V21.15.2, l'archive source figée, les IDs de nœuds et la roadmap V3.2 ne changent pas.

## Utilisation (Python)

Importer depuis engine/ :

    from smartsvg_core.project_archive import LoadedProject, save_project, load_project

Construire un LoadedProject à partir des enregistrements G1.2 :
- project_id et app_version ;
- sources, masks, subjects, artifacts, qa_results ;
- document (objet JSON), operations (liste de révisions/annulations) ;
- resources : dictionnaire chemin relatif → octets ;
- source_paths et mask_paths : identifiants stables → chemins relatifs.

Puis appeler :

    save_project("mon_projet.smartsvg", project)
    restored = load_project("mon_projet.smartsvg")
    save_project("mon_projet.smartsvg", edited, overwrite=True)

**Attention :** l'API de bas niveau est destinée à une intégration future. Elle ne crée pas encore de boutons dans l'interface Express/ComfyUI.

## Structure v1

- manifest.json : version de schéma, ID projet, version application, chemins et hash SHA-256 + taille de chaque entrée ;
- document.json : éléments et transformation de scène (JSON non exécutable) ;
- operations.json : historique des révisions et corrections ;
- sources.json, masks.json, subjects.json, artifacts.json : métadonnées G1.2 ;
- proofs/qa_results.json : déclarations de preuve et statut, **non certifiés automatiquement** ;
- sources/*, masks/*, chemins de fichiers d'artefacts : octets conservés à l'identique.

Le ZIP est lu en mémoire avec des budgets définis, **jamais extrait**. Les chemins absolus, les .., les fichiers doublons (y compris collision de casse), les symlinks, le chiffrement, les types ZIP non admis et les membres non déclarés sont refusés.

**Compatibilité G1.2 :** les noms portables contenant des espaces et des caractères Unicode visibles sont admis, par exemple `exports/étiquette 01.svg`, et conservés octet par octet lors d’un aller-retour ZIP. Restent interdits les chemins traversants ou absolus, caractères de contrôle et de direction invisibles, noms réservés Windows, séparateurs interdits, composants dépassant 255 octets UTF-8, et alias après normalisation NFC + repli de casse. Les vérifications sont réalisées **en écriture et en lecture** ; aucun chemin n'est extrait vers le système de fichiers.

## Propriétés de sûreté

- Contrôle des références et bounding-box G1.2 avant sauvegarde/après restauration ;
- Après alignement sur G1.2, contrôle **acyclique des relations d'accessoires** à la sauvegarde et au rechargement ; une archive contenant des sujets cycliques est rejetée même lorsque ses entrées et son manifeste SHA-256 sont cohérents. Test d'intégration négatif dédié, sans extraction ou écriture lors du chargement ;
- Rejet explicite des cartes source/masque/ressources malformées (objet obligatoire), avant toute écriture ; deux identifiants de source ne peuvent pas référencer le même membre ZIP, même si leurs empreintes et dimensions sont identiques (prévention des alias de ressources) ;
- contrôle SHA-256 **réel sur les octets**, manifestes, dimensions déclarées et en-têtes d'images (PNG/JPEG/WebP) ;
- Les PNG source déclarés `L`, `RGB` ou `RGBA` sont vérifiés contre le type couleur réel du PNG avant admission et après réouverture. Une déclaration trompeuse de transparence est refusée (`SOURCE_COLOR_MODE_MISMATCH`) ; les types sans équivalent G1.2 (`UNSUPPORTED_SOURCE_PNG_COLOR_TYPE`), les profondeurs autres que 8 bits et les images entrelacées (`UNSUPPORTED_SOURCE_PNG_LAYOUT`) nécessitent une conversion explicite. Le ZIP ne peut conserver un PNG source dont les CRC de chunks, les données IDAT décompressées, les filtres de lignes ou le chunk final IEND sont invalides, même si son SHA-256 déclaré est cohérent ;
- masques obligatoirement en PNG L8 sujet blanc, CRC des chunks et décompression vérifiée sans dépasser le budget ;
- les PNG source `L/RGB/RGBA` et les masques L8 refusent tout chunk de transparence `tRNS` (`PNG_UNDECLARED_TRANSPARENCY`) : ce chunk peut rendre transparents des pixels annoncés opaques et contredire les contrats G1.2. Conversion explicite vers un format alpha compatible requise ; jamais de suppression silencieuse. Le rejet intervient avant l'écriture et protège le dernier projet valide ;
- limite d'entrées, taille membre, taille décompressée globale, profondeur JSON (32) et nombre d'éléments ;
- Dans `document` et `operations`, seules les structures JSON natives sont acceptées (`dict`, `list`, scalaires) : les tuples Python sont rejetés (`INVALID_JSON_TYPE`) au lieu d'être transformés silencieusement en listes. Une tentative de sauvegarde rejetée ne remplace jamais l'ancienne version valide. **Exception explicite et bornée :** les champs typés G1.2 `Subject.bbox_px`, `Subject.accessory_ids` et `Artifact.subject_ids`, immuables dans le moteur, sont volontairement encodés comme tableaux JSON à l'export ; les autres tuples arbitraires de la scène restent refusés.
- fichier temporaire dans le même dossier, fsync, réouverture avant publication puis remplacement atomique ;
- création par lien dur sans écrasement lorsque overwrite=False sur les systèmes où ce mécanisme est pris en charge.

**Limites connues :**
- Les en-têtes JPEG/WebP/Png source ne remplacent pas une validation complète de décodage visuel ou de profil ICC ; l'ouverture fiable des pixels est à tester dans le moteur image et dans l'UI.
- Les SVG conservés comme ressources ne sont PAS exécutés, interprétés ou certifiés à cette étape : les soumettre au préflight SVG avant tout rendu/export.
- La sauvegarde ne reconstitue pas encore automatiquement une scène native ComfyUI ; la couche de liaison Express et ses migrations sont des lots suivants.
- La présence de champs real et de références de preuves ne démontre pas l'authenticité d'un essai physique.
- Format de schéma smartsvg-project/1 fermé par défaut : versions nouvelles refusées jusqu'à ajout d'un migrateur explicite. Pas de migration silencieuse.
- Un système de fichiers incapable de garantir la création de lien dur peut refuser la première sauvegarde. Il faut alors une méthode alternative sûre avant prise en charge générale Windows.


- Les PNG sources et masques refusent désormais les chunks critiques inconnus, un deuxième `IHDR`, et les segments `IDAT` non contigus, même si les CRC et empreintes SHA-256 sont cohérents. Les chunks auxiliaires sûrs comme `tEXt` avant ou après la séquence IDAT restent admis ; les tests vérifient aussi la préservation de la dernière sauvegarde valide.

## Tests et acceptation

- tests engine/tests/test_project_archive_g13.py : scénarios synthétiques de sauvegarde et attaques (sans œuvres utilisateur), y compris alias de source, cartes malformées, rejet des incohérences PNG `L/RGB/RGBA`, round-trip conforme pour les trois types, CRC IDAT corrompu, PNG source sans IEND, filtres invalides malgré CRC correct et profondeur 16 bits non déclarable ;
- tests racine tests/test_g13_project_archive.py exécutés automatiquement par la CI privée d'admission ;
- tests des 8 contrats G1.2 conservés dans la branche parente ;
- ne pas confondre ces tests avec une exécution GPU RTX 3070, Design Space ou coupe Explore 5.

Décision à prendre après publication des logs CI exact-HEAD. Cette PR cible la branche G1.2 pour respecter WIP 1+1 et éviter toute fusion prématurée.

## Lot suivant après G1.3

G1.4 : reprise après crash, sauvegardes versionnées/rollback et gestion des erreurs présentée à l'utilisateur. G2.1 : relier ensuite le même état de projet à Express et réduire la dépendance au graphe.
