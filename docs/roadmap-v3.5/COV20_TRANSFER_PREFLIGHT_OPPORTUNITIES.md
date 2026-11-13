# V35-COV-20 — Contrat transversal de transfert et prévol (O-001/O-002/O-004/O-028/O-032)

**13 novembre 2026 — CANDIDAT / NON NORMATIF.** Ce document affine COV-19 sans créer d'exporteur, de pilote Cricut, de ticket V34 ou de modification du projet V1. Sources vérifiées : V3.4 OPPORTUNITIES.md (descriptions intégrales O-001/002/004/028/032), COV18B2 (C07–C12), #142, contrat des 25 contrôles et PROGRESS. Les commentaires historiques Smart Delivery V1/V2 et les DoD complets des lots 14–17 ne sont **pas requalifiés ici comme relus** ; le rapprochement final reste ouvert. Aucun résultat de test n'est revendiqué.

## 1. Décisions et héritage traçable

| ID | Source historique et liens explicités dans OPPORTUNITIES | Décision V3.5 | Limite et alternative contradictoire |
|---|---|---|---|
| O-001 | S-010, S-084, R33-022, R33-034, V34-010 | RACCORDER au journal **post-export**, P1 | Une checklist manuelle sans journal est plus simple ; conserver le journal seulement s'il apporte diagnostic et reprise sans fuite de données |
| O-002 | S-029, R33-022, V34-007/009, T-V34-02-05/06 | AMÉLIORER le contrôle PTC A4/orientation/échelle, P1 | Ne pas afficher de dimensions maximales non sourcées ; mesure imprimée et calibration externe restent UNKNOWN |
| O-004 | S-085, R33-022/023, V34-012, T-V34-03-08/09/15 | RACCORDER à la prévisualisation par opérations, P1 | La séquence est indicative ; aucune commande machine ni promesse d'ordre réel |
| O-028 | S-030/034/056, V34-101/103 | AMÉLIORER le diagnostic budget de chemins, P1 | La source historique mentionne 5 000 paths ; traiter ce chiffre comme **hypothèse historique non certifiée/versionnée**, pas comme plafond universel actuel |
| O-032 | S-012/084, R33-022/034, V34-111/114 | FUSIONNER la surface avec O-001, conserver deux critères distincts, P1 | Le guide après import vérifie Attach, dimensions et opérations par déclaration utilisateur, jamais par interrogation de Design Space |

**UX connexes :** C07 prévol, C08 profils, C10 quatre exports, C11 transfert. **COV18B2** reste une revue candidate, pas une certification de DoD. O-012 et O-031 sont consommateurs transversaux (double codage accessible et conflits de segments), sans doublon d'outil.

## 2. Jobs to be done et UX

**Novice :** après création d'un sticker PTC ou d'une boîte CUT/SCORE, comprendre quel fichier ouvrir, quelles dimensions contrôler, quel réglage vérifier dans Design Space et quelles étapes restent incertaines. Une action « Préparer le transfert » ouvre un panneau contextuel non bloquant : (a) rôle de l'artefact et dimensions, (b) problèmes bloquants du prévol local, (c) checklist DS adaptée au rôle, (d) déclarations facultatives et effaçables. L'utilisateur peut revenir au canevas sans modifier son projet.

**Expert :** inspecter chaque path, son opération et son identifiant, la géométrie et les unités mm, la version du profil et du guide, les avertissements de complexité et le hash de l'export. Exporter le diagnostic expurgé sans le confondre avec une certification matérielle.

**États UX :** EMPTY (aucun export réel : ne pas proposer un faux ZIP) → LOCAL_PREFLIGHT_PENDING → LOCAL_PREFLIGHT_READY/WARN/BLOCKED → EXPORTED (artefact réellement existant) → GUIDE_OPEN → USER_DECLARED_CHECKED/UNCHECKED → EXTERNAL_UNVERIFIED ; ERROR et CANCELLED sont réessayables. Une nouvelle révision d'artefact rend les déclarations précédentes STALE, sans les reporter. Le panneau affiche texte + motif + couleur, navigation clavier/focus, ordre de tabulation et messages lisibles à 1366×768 / DPI 200 %, contraste élevé et animation réduite. Aucun « succès » vert pour une étape seulement cochée.

## 3. Contrats de données proposés, **non implémentés**

`TransferContextV1` : `artifact_role` enum {PNG_PTC, SVG_BASIC_CUT, SVG_MULTILAYER_CUT, SVG_EDITABLE}, `artifact_sha256` hex 64, `artifact_size_bytes` entier, `dimensions_mm` deux décimaux finis strictement positifs, `export_revision` opaque, `machine_profile_id/version/status` (KNOWN/UNKNOWN), `ds_version` chaîne optionnelle ou UNKNOWN, `created_at_utc`. Source de vérité : **artefact produit par l'exporteur existant**, non le journal.

`OperationFindingV1` : `path_id`, `operation` enum CUT/SCORE/DRAW/PRINT/FOIL/UNKNOWN, `severity` BLOCK/WARN/INFO/UNKNOWN, `geometry_revision`, `message_code`, `source_provenance`. Les conflits sur un même segment sont BLOCK tant que l'utilisateur ne les résout pas ; un path SVG d'édition n'acquiert jamais automatiquement une opération.

`TransferJournalV1` : identifiant aléatoire local, `artifact_sha256`, `guide_version`, `check_id`, `declared_by_user`, `declared_at`, note facultative et chemin photo facultatif **hors ZIP par défaut**. Aucune élévation de preuve depuis ce journal. Stockage séparé du .smartsvg V1 ; export du journal seulement sur consentement explicite. Ne pas ajouter de champ au schéma V1.

`DeliveryInputV1` : liste non vide d'artefacts **existants et qualifiés**, chacun avec rôle/hash/chemin canonique contrôlé, et `qa_status` PASS/FAIL/UNKNOWN par axe. Un ZIP peut être construit avec un seul artefact sain ; il ne crée pas les trois autres exports manquants. Packaging en staging privé, vérification des hashes avant/pendant/après copie, manifeste et relecture du ZIP, publication atomique no-clobber. Pas de lien réseau, pas d'EXIF ou note privée par défaut, pas de HTML actif. Les erreurs (STALE_REVISION, MISSING_ARTIFACT, HASH_MISMATCH, UNSAFE_PATH, QUOTA, DISK_FULL, EXISTS, CANCELLED, PROFILE_UNKNOWN) doivent être typées et réparables.

**Frontière transactionnelle :** les prévols, previews et journaux ne mutent pas le projet ; toute correction de géométrie suit le writer/CAS et Undo existants. Un export externe déjà publié n'est pas « annulé » par Undo ; le guide est lié à son hash exact. Aucun nouveau writer, store, exporteur, ni modèle IA requis. Le fonctionnement CPU/manuel est complet ; GPU et réseau NON APPLICABLES à ce lot.

## 4. Protocoles de tests à écrire avant implémentation (tous NOT_RUN)

**Positifs :** (P1) un PNG PTC réel qualifié produit un guide PTC et un ZIP à un fichier sans fausse sortie SVG ; (P2) une boîte CUT/SCORE affiche opérations distinctes et avertissement Attach ; (P3) réouverture du journal avec hash identique restaure seulement les déclarations ; (P4) guide accessible au clavier à 1366×768/DPI 200 %.

**Négatifs :** (N1) dimensions mm nulles/NaN ou version DS UNKNOWN → blocage de garantie, guide de vérification manuelle ; (N2) deux segments superposés CUT/SCORE → diagnostic bloquant sans réécriture ; (N3) SVG avec XML hostile, chemins traversants/reparse/Unicode collision → refus avant ZIP ; (N4) artefact remplacé après SHA ou deux packagings concurrents → rejet STALE/HASH_MISMATCH, aucune publication partielle ; (N5) disque plein, annulation ou crash pendant staging → nettoyage/reprise contrôlée, ZIP final absent ou intact ; (N6) révision d'export changée → anciennes cases DS périmées ; (N7) photo/EXIF privé → non inclusion par défaut ; (N8) complexité supérieure au budget hypothétique → WARN avec version et source, pas de fausse certification DS.

**Preuves séparées :** unitaires CPU et ZIP, UI Windows, Design Space version/date avec mesures de taille et Attach, coupons physiques Explore 5 (matière/lame/tapis et photos/mesures) ; GPU = N/A car aucune IA. Toutes **NOT_RUN** ici. Mesurer p50/p95 prévol et ZIP sur fixtures synthétiques autorisées et volumes annoncés ; aucune latence chiffrée inventée.

## 5. Micro-lots TDD et DoD candidat

1. Contrat d'entrée et fixtures : validation rôles, dimensions, hash, tri-state ; refuser les entrées non fiables avant toute écriture.
2. Prévol opérations et budget chemins : tests de conflits, topologie et provenance ; aucune confusion CUT/SCORE ou SVG éditable/CUT.
3. Guide PTC et guide CUT/SCORE versionnés : checklist accessible, persistance locale liée au hash, STALE et effacement.
4. Assemblage Delivery via le producteur existant : ZIP à un export, manifeste et QA par axe, staging atomique/no-clobber, quotas et crash.
5. Qualification Windows/DS/physique séparée et revue hostile des preuves ; aucun statut PASS dérivé d'une déclaration.

**DoD de conception encore ouvert :** identifier les ports exacts sur HEAD main, relire les commentaires SD-V1/SD-V2 et les DoD locaux des lots 14–17, assigner les scénarios source exhaustifs, contrôler les 25 axes, puis revue indépendante. Aucune certification prête à coder attribuée.

## 6. Audit explicite des 25 axes (statuts de cette fiche)

01–05 inventaires **PRÉSERVÉS, couverture sémantique OUVERTE** ; 06 preuve d'implémentation **NOT_RUN** ; 07 CAS/writer **SPÉCIFIÉ sans validation HEAD** ; 08 quatre rôles **DISTINCTS** ; 09 machine **UNKNOWN sauf preuve** ; 10–12 parcours et accessibilité **SPÉCIFIÉS, tests NOT_RUN** ; 13 crash/concurrence **CAS DE TEST DÉFINIS** ; 14 IA **N/A : aucune inférence**, consentement externe maintenu ; 15 PNG/ICC/EXIF **PARTIEL, tests NOT_RUN** ; 16 topologie/XML/mm **PARTIEL, tests NOT_RUN** ; 17 Fabrique/batch **N/A comme fonctionnalité**, consommateurs conservés ; 18 Delivery **SPÉCIFIÉ, non testé** ; 19 propositions connexes **TRAÇABLES** ; 20 performance **PROTOCOLE seulement** ; 21 sécurité/licences **RISQUES recensés** ; 22 branche et gouvernance **RESPECTÉES** ; 23 anti-doublon **CONTRAT**, ports HEAD non vérifiés ; 24 adoption **NON AUTORISÉE** ; 25 aucune compression ni suppression d'obligation **REVU pour cette fiche**, audit de campagne toujours ouvert.

**État :** 5/5 opportunités approfondies au niveau contrat candidat, 0/5 certifiées. Inventaires historiques 24/141/140/80/437 inchangés, 431/437 liens historiques explicites et six exceptions, dix G6/G9 sans ticket direct encore ouverts. **Prochaine action unique COV-21 :** confrontation des cinq contrats ci-dessus aux DoD exacts des lots V3.4 14–17 et aux deux commentaires SD-V1/SD-V2, puis résolution des divergences avec ports HEAD main vérifiés.
