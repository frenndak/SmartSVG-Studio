# État observé et corrections de pilotage

Lecture ciblée de `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, le 13 novembre 2026. Il s'agit d'un audit de sources, pas d'une exécution de l'application complète. L'inventaire des fichiers n'est pas un graphe exhaustif des imports.

## Ce qui existe réellement

| Surface | Constat de source | Limite / action |
|---|---|---|
| Bureau | `engine/standalone_desktop_v34.py` construit Accueil, Projet, Fabrique, Apparence et Atelier ; création, notes et récupération raccordées | Installation finale et recette Windows actuelle à vérifier |
| Projet V1 | Création PNG et notes, inspection de révision, SHA avant/après lecture | Ne pas ajouter un deuxième writer ni déclarer le format V2 livré |
| Retouche | `native_atelier_tk_v34.py` ouvre le panneau pinceau pour un sujet prouvé ; `native_brush_draft_tk_v34.py` importe et appelle `save_native_subject_stroke` | L'en-tête « read-only » du panneau et celui du bridge de sauvegarde sont antérieurs au raccordement ; suivre les appels effectifs |
| Sauvegarde des retouches | `smartsvg_core/native_subject_save_v34.py` appelle `ManagedWorkspace.save_subject_brush`, vérifie le reçu et renvoie le SHA de projet | Présence du code et des tests, pas une qualification fraîche CPU/Windows dans cette session |
| Synchronisation | Après sauvegarde, le bureau réexamine le projet et vérifie le reçu ; rebasing explicite des notes locales | Conflits, résultats tardifs et panne après commit à tester dans les parcours complets |
| Historique | `subject_brush_history_g33e.py` fournit le plan ; `project_workspace_g22.py` expose `subject_brush_history` et `change_subject_brush_history` | Ces services ne prouvent pas la présence de boutons de mutation natifs ; #139 porte la disponibilité en lecture seule |
| Affichage | Viewport avec pan, zoom, Home et 0 ; dernier commit de main = PR #137 | #140 traite séparément le canevas temporairement nul |
| Fabrique | Présence des gabarits natifs et tests de géométrie/prévol | Aperçu géométrique ne prouve pas export, sauvegarde ou montage physique |
| Sorties | Modules et tests PNG density, SVG publication et guide de transfert présents | Aucun parcours d'export dans le shell lu ; ne pas confondre moteur testé et bouton livré |
| Calques / texte / lots | Exigences et moteurs historiques à réconcilier | Pas de complétion déduite d'un nom de module ou d'une ancienne PR |

## Écarts documentaires identifiés

Les résumés du 6 novembre dans `docs/ETAT_ACTUEL_SMARTSVG.md` et le README V3.4 annoncent encore des projets existants en lecture seule et recovery/retouches non raccordés. Le point d'exécution du même dossier annonce encore recovery comme prochaine action. Ces résumés ne décrivent donc plus complètement le shell lu aujourd'hui. Les tableaux historiques restent datés ; cette proposition ne les réécrit pas et ne présente pas les anciennes preuves comme des tests du HEAD actuel.

Le premier correctif de suivi à intégrer sera un résumé courant adossé au SHA et aux tests des fonctions effectivement raccordées, en laissant les photographies historiques explicitement datées. Il devra remplacer les trois points d'entrée contradictoires ensemble, sans modifier les critères hérités. Cette réconciliation fait partie de V35-01 et ne constitue pas une promotion automatique en V3.5.

## Travail déjà ouvert à préserver

| PR ouverte lors de la lecture | HEAD observé | Périmètre | Conséquence |
|---|---|---|---|
| [#138](https://github.com/frenndak/SmartSVG-Studio/pull/138) | `dd76533696deeefcaea65328b4cda6326d5df9b9` | Reçus de récupération inattendus | Relire diff, tests, reviews et CI exacts avant intégration ; ne pas dupliquer |
| [#139](https://github.com/frenndak/SmartSVG-Studio/pull/139) | `409dd41b676cd5be8a92e60a4ff7ebb365c15cca` | Disponibilité Undo/Redo native en lecture seule | Point de départ de l'historique ; la mutation reste une étape distincte |
| [#140](https://github.com/frenndak/SmartSVG-Studio/pull/140) | `e3a072f6f0e5735bf7d9a567e89a536048810ae0` | Viewport Tk de taille nulle | Vérifier puis réutiliser ; aucun travail concurrent sur le même helper |

Les trois PR étaient DRAFT et non fusionnées dans la base examinée. Ces SHA sont des observations, jamais une réservation : les relire au prochain cycle. Aucun verdict d'approbation ni preuve de réussite n'est attribué ici à ces candidats.

## Sources et profondeur de la vérification

Lecture : AGENTS ; les 25 documents numérotés du dossier V3.4 (24 lots et une annexe), HERITAGE_INDEX, PROGRESS, README, matrice d'exécution ; maîtres/traçabilité V3.3 ; shell natif, Atelier, pinceau, bridge de sauvegarde, workspace et historique ; tests de sauvegarde et intégrité V3.4 ; inventaires `engine`, `smartsvg_core`, `tests` et `tools` ; listes des PR ouvertes et commit main. Les fichiers lus pour l'état sont distingués des simples inventaires ci-dessus.

La réponse du contrôle des statuts combinés du commit était vide (`statuses: []`). Ce résultat ne prouve ni succès ni échec des check runs Actions. Les jobs Actions n'ont pas été qualifiés ici. La copie complète par git n'était pas disponible par les routes réseau essayées ; les fichiers utiles ont été lus par leur révision exacte. Les tests produit complets n'ont donc pas été exécutés. La validation de la nouvelle roadmap se fait sur les documents récupérés et les nouveaux fichiers.

## Décisions et risques à conserver

- **Bloquant pour écrire un projet :** identité/révision prouvées, contrat admissible, confirmation explicite, contrôle du résultat et récupération en cas d'incertitude.
- **Bloquant pour promettre un usage Cricut :** qualification du format et preuves Design Space / mesures physiques appropriées ; pas seulement un SVG qui se parse.
- **Non bloquant pour développer :** absence de photo personnelle, de GPU, d'assistant ou de format V2 si le lot peut utiliser une fixture V1 synthétique.
- **Risque de dispersion :** traiter un raccordement observable à la fois ; les 15 tranches ne sont pas 15 chantiers simultanés.
- **Risque de faux avancement :** aucun ticket entier déclaré terminé sur le seul motif qu'une partie de son code existe.
