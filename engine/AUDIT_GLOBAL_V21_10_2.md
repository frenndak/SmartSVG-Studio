# SmartSVG Studio V21.10.2 — Contre-expertise globale et correctifs

**Date : 24 octobre 2026.** Base auditée : archive V21.10.1 livrée précédemment. Objectif : fiabiliser l'expérience *PNG transparent → Print Then Cut*, sans réécriture des moteurs historiques et avec cinq commandes Express inchangées.

## Synthèse et périmètre

**Verdict : passage à la suite possible sur le plan du code (GO conditionnel).** La fabrication historique est conservée. Trois défauts transversaux ont été corrigés dans la V21.10.2 ; le détourage IA sur RTX 3070, le vrai frontend ComfyUI et la découpe Cricut restent non validés physiquement.

| Axe contrôlé | Résultat | Réserve / action |
|---|---|---|
| Archive ZIP, extraction, SHA-256 | OK après extraction | Manifeste V21.10.2 distinct |
| Registre ComfyUI, ports, 3 workflows V21.10 | Contrats cohérents | Vérifier graphique sur Nodes 2.0 et extensions tierces |
| Moteurs PNG et SVG de fabrication | Sources inchangées | Sur la V21.10.1, non-régression d'exports vérifiée ; pas de preuve de découpe physique |
| Interface Express à cinq réglages | Identique | Nœud V21.8 conservé pour import Cricut |
| Correction manuelle | Corrections rejouées en Python à taille native | Un brouillon non enregistré restait vulnérable à une relance : corrigé en mémoire |
| Diagnostic des masques | Read-only, trous, îlots, chevauchements | Largeur physique 40 mm fixée dans l'inspection unifiée : alertes dimensionnelles indicatives |
| Fabrication HD automatique | Fonction auxiliaire présente | **Le dossier d'import Cricut reste basé sur le PNG de fabrication original**, pas le fichier HD distinct |
| Import Cricut PNG | RGBA, topologie et dimensions contrôlées localement | Les découpes de Design Space ne peuvent pas être simulées avec certitude |
| Validation des sept images | Dimensions/formats vérifiés | Aucune n'a de canal alpha exploitable ; sans détourage, coupe rectangulaire |
| Fichiers projet | Contrôle de confinement et de non-écrasement | Fichiers d'accompagnement du dossier Cricut également protégés en V21.10.2 |

## Correctifs effectifs V21.10.2

### P0 — Faux positifs de silhouette Print Then Cut

**Avant :** un PNG RGBA totalement opaque était classé `SILHOUETTE_ALPHA_UNE_ZONE` lorsque le rapport ne mentionnait pas explicitement le repli sans masque. Un rectangle opaque entouré de transparence pouvait aussi être annoncé comme une vraie silhouette. Ceci produisait un faux « prêt » pour une découpe de personnage alors que la Cricut découperait un rectangle.

**Après :** la forme alpha est analysée au seuil local de 128/255. Une unique composante qui remplit entièrement sa boîte englobante rectangulaire est classée `CADRE_RECTANGULAIRE_SANS_DETOURAGE` et `PRET_POUR_IMPORT_LOCAL_CADRE`. Cela **n'interdit pas** les cartes rectangulaires volontaires. Des contours courbes ou irréguliers restent classés `PRET_POUR_IMPORT_LOCAL` s'ils passent les autres tests. Une exception : certains détails anti-aliasés ou rectangles arrondis peuvent être visuellement rectangulaires sans correspondre exactement à la géométrie du détecteur.

### P1 — Protection des fichiers d'accompagnement

**Avant :** les PNG étaient protégés par création exclusive mais `LIRE_AVANT_IMPORT.txt` et `RAPPORT_IMPORT_CRICUT_V21_8.json` étaient écrasés avec `write_text`, même si l'utilisateur les avait modifiés.

**Après :** écriture temporaire + publication exclusive, réutilisation si strictement identique, refus d'écraser si différent, et avertissement avec état `A_VERIFIER`. Les PNG déjà fabriqués ne sont pas annulés. L'avertissement est propagé dans le message du nœud Express.

### P1 — Récupération des retouches lors d'une nouvelle exécution

**Avant :** `onExecuted` fermait une fenêtre ouverte sans demander confirmation ; les nouveaux traits non sauvegardés étaient perdus.

**Après :** l'éditeur capte un brouillon en mémoire lorsqu'une nouvelle exécution arrive, puis ne le restaure que si l'empreinte source+masques est identique. Une modification de segmentation invalide le brouillon, sans le rejouer silencieusement. Enregistrement ou abandon volontaire efface ce brouillon. **Le brouillon n'est pas persistant après fermeture/rechargement du navigateur : enregistrer explicitement reste indispensable.**

## Passes de contre-expertise

1. **Structure et installation** : ZIP, chemins sûrs, fichiers SHA-256, compatibilité des nœuds anciens, présence des workflows V21.10.
2. **Source image et transparence** : JPEG et captures, alpha de référence, piège des cartes rectangulaires. Les 7 exemples sont opaques en entrée.
3. **IA et séparation multi-sujets** : raccordement des masques prévu ; la justesse des sorties Florence-2/SAM2/RMBG non prouvée sans modèles et GPU réels.
4. **Éditeur** : dimensions limites, empreinte des retouches, pinceau ajout/retrait, sauvegarde déterministe et brouillon protégé contre la relance.
5. **Géométrie de découpe** : îlots, trous transparents, collisions, périmètre et petites attaches analysés ; les métriques restent des estimations préexport.
6. **Qualité image** : le module HD travaille sur le raster et ne doit pas être confondu avec un SVG multicouche éditable ni une résolution source réellement récupérée.
7. **Cricut** : un PNG RGBA en image aplatie permet le flux Print Then Cut ; un SVG auxiliaire superposé produit un risque de découpe en double.
8. **Résilience** : fabrication ≠ publication d'aperçus ; les pannes facultatives restent isolées ; copies protégées et diagnostic explicite.
9. **Ressources** : bornes images 5 Mp dans l'éditeur natif, 50 Mp cumulés de masques, dossiers d'aperçus bornés. Performance sous charge GPU 8 Go à confirmer.
10. **Données et sûreté** : chemins de fichiers confinés au projet, absence de dépendance réseau dans les moteurs, publication d'aperçus visible aux utilisateurs autorisés du serveur ComfyUI.

## Tests et limites de preuve

Tests spécifiques V21.10.2 : `tests/test_v21102_global.py` et tests historiques `test_v218`, `test_v2191`, `test_v2110`, ainsi que la suite JavaScript. Les anciens tests qui considéraient un rectangle comme une silhouette ont été corrigés explicitement. Le code des moteurs historiques n'est pas modifié.

**Non validés dans cet environnement :** vraie interface graphique du ComfyUI installé chez l'utilisateur, inférence sur RTX 3070, lecture effective par la version locale de Design Space, gestion des dimensions/repères pendant l'impression et découpe physique Explore 5.

## Conditions d'acceptation pratique (avant certification complète)

- Charger un workflow V21.10 depuis `example_workflows` sur le ComfyUI local, ouvrir l'éditeur, sauver puis recharger les retouches, refaire les mêmes sorties.
- Tester un masque transparent non rectangulaire et vérifier dans Design Space le panneau de découpes (une coupe externe attendue).
- Tester une planche multi-sujets et contrôler que leur nombre de silhouettes correspond au nombre voulu, sans découpe de lettres.
- Vérifier largeur en millimètres sur le canevas puis effectuer une découpe d'essai avec la Cricut Explore 5.

## Décision et suite conseillée

**V21.10.2 : GO pour essais locaux et poursuite raisonnée du développement, pas de certification physique.** Pour V21.11 : relier la largeur réelle de découpe aux alertes géométriques, fiabiliser le détourage de sources opaques sans repli rectangle silencieux, distinguer dans l'interface `CARTE / SILHOUETTE / À CORRIGER`, et tester l'intégration des PNG HD dans le flux de fabrication sans altérer la découpe.

Sources officielles consultées en octobre 2026 :
- https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space
