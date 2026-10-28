# SmartSVG Studio Registre de traçabilité V3.3

## 1 Objet

Ce registre relie les exigences de la roadmap aux familles, parcours, lots, implémentations, tests et preuves. Il empêche trois erreurs : perdre une exigence lors d'une révision, confondre code et fonctionnalité raccordée, ou transformer une preuve partielle en validation générale.

À la publication, [la roadmap directrice V3.3](ROADMAP_MASTER_v3_3.md) devient l'unique point d'entrée normatif. L'[annexe d'héritage V3.3](ROADMAP_HERITAGE_v3_3.md) reproduit intégralement les engagements antérieurs, y compris les critères non répétés dans la synthèse. Le présent registre reprend individuellement S-001 à S-101 et ajoute R33-001 à R33-040 ; le document historique V3.2 reste conservé à titre d'archive gelée.

**Navigation :** [Maître V3.3](ROADMAP_MASTER_v3_3.md) · [Couverture V3.3](ROADMAP_COVERAGE_v3_3.md) · [Annexe d'héritage](ROADMAP_HERITAGE_v3_3.md).

## 2 Schéma d'un enregistrement

Chaque exigence suivie doit posséder les champs suivants :

| Champ | Contenu obligatoire |
|---|---|
| ID | `S-nnn` hérité ou `R33-nnn` nouveau |
| Intitulé | résultat attendu, formulé sans présumer son état |
| Source | document et section d'origine |
| Famille | une ou plusieurs familles F01-F15 |
| Parcours | P01-P10 ou `TRANSVERSE` |
| Jalon | G0-G9 et micro-lot concerné |
| Dépendances | exigences, contrats et preuves préalables |
| Autorité | projet, moteur, interface, ComfyUI ou système externe |
| statut_implementation | niveau du cycle de réalisation, sans présumer aucune preuve d'environnement |
| Implémentation | chemins et SHA exacts, si présents |
| Tests automatiques | commandes, suites et SHA exacts |
| preuve_auto | PASS, FAIL, NON_EXECUTE, BLOQUE ou NON_APPLICABLE avec SHA et commande |
| preuve_windows | PASS, FAIL, NON_EXECUTE, BLOQUE ou NON_APPLICABLE avec environnement |
| preuve_design_space | PASS, FAIL, NON_EXECUTE, BLOQUE ou NON_APPLICABLE avec version et protocole |
| preuve_physique | PASS, FAIL, NON_EXECUTE, BLOQUE ou NON_APPLICABLE avec machine, matière et mesures |
| Risques | liens vers les risques et scénarios d'échec |
| Rollback | revert, migration inverse ou restauration documentée |
| Décision | GO, NO-GO, expérimental ou non vérifié |

Un champ vide signifie `NON_RENSEIGNE`. Il ne doit jamais être interprété comme succès.

## 3 Maturité de réalisation et axes de preuve

| statut_implementation | Signification | Preuve minimale |
|---|---|---|
| SPECIFIE | besoin et critères décrits | section de roadmap approuvée |
| ARCHITECTURE | autorités, interfaces et risques définis | design ou ADR revu |
| IMPLEMENTE | code présent | diff et SHA |
| RACCORDE | accessible dans le parcours réel | test d'intégration ou E2E |
| QUALIFIE | les axes de preuve exigés par le gate possèdent chacun un résultat explicite | matrice de preuves et décision humaine lorsque nécessaire |
| STABILISE | gates applicables franchis sans blocage | décision de release et matrice complète |

Les axes `preuve_auto`, `preuve_windows`, `preuve_design_space` et `preuve_physique` sont indépendants du statut d'implémentation et indépendants entre eux. Par exemple, une exigence peut être `RACCORDE` avec `preuve_auto=PASS`, `preuve_windows=FAIL`, `preuve_design_space=NON_EXECUTE` et `preuve_physique=BLOQUE`. Aucun agrégat ne remplace ces quatre valeurs.

`NON_APPLICABLE` exige une justification reliée au contrat. `NON_EXECUTE` signifie seulement qu'aucune exécution qualifiante n'est disponible. `BLOQUE` exige la condition de déblocage. Un champ vide reste invalide.

## 4 Conservation exhaustive des tickets S-001 à S-101

Les intitulés, priorités, dépendances et preuves originales restent ceux de l'[annexe normative d'héritage](ROADMAP_HERITAGE_v3_3.md) ; les dossiers individuels ci-dessous les reprennent pour permettre une utilisation directe de V3.3.

### S-001 à S-022 fondations historiques

| IDs conservés | Domaines principaux | Raccordement V3.3 |
|---|---|---|
| S-001, S-002, S-003, S-004 | baseline, sorties, projet, compatibilité | G0-G2, F10, F15, P01-P02 |
| S-005, S-006, S-007, S-008 | IA réelle, vérité terrain, sujet, retouche | G0-G3, F02-F03, P03 |
| S-009, S-010, S-011, S-012 | QA Cricut, coupe physique, SVG, matières | G4-G5, F05-F07, P01-P02-P06 |
| S-013, S-014, S-015, S-016 | Express, multiobjets, halos, qualité raster | G2-G3, F02-F04-F14 |
| S-017, S-018, S-019 | projet, lots, benchmark | G1-G8, F10-F12, P04-P07-P08 |
| S-020, S-021, S-022 | dioramas, OCR, application autonome | G9, F09-F13-F14 |

### S-023 à S-048 consolidation produit

| IDs conservés | Domaines principaux | Raccordement V3.3 |
|---|---|---|
| S-023, S-024, S-025, S-026 | identités, `.smartsvg`, Express, historique | G1-G2, R33-003-R33-006 |
| S-027, S-028 | contrôle GPU et groupes sujet-accessoires | G3, F02, P03 |
| S-029, S-030, S-031, S-032 | contrats PNG et SVG, Explore 5, sorties séparées | G4-G5, R33-008, P01-P02-P06 |
| S-033, S-034 | traits, petites régions et Bézier | G5, F05-F06 |
| S-035, S-036, S-037 | canevas, fontes et gabarits | G6, F08-F09, P05 |
| S-038, S-039, S-040, S-041 | jobs, CSV, imposition, bibliothèque | G7, F10-F12, P04-P07-P08 |
| S-042, S-043 | sécurité et benchmark | G8, F15 |
| S-044, S-045, S-046, S-047, S-048 | diorama, vinyle, application, OCR, upscale | G9, F04-F09-F13-F14 |

### S-049 à S-066 exigences de preuve et d'environnement

| IDs conservés | Domaines principaux | Raccordement V3.3 |
|---|---|---|
| S-049, S-050, S-051 | corpus, vérité terrain et inventaire | G0-G1, R33-001-R33-002 |
| S-052, S-053, S-054 | schémas, projet, migrations, preuves orthogonales | G1-G2, R33-004-R33-009 |
| S-055, S-056, S-057 | Explore 5, géométrie et registre matériel | G4, R33-022-R33-023 |
| S-058, S-059, S-060 | environnement IA, accessibilité, scores séparés | G2-G5, R33-017-R33-019-R33-029 |
| S-061, S-062, S-063 | fichiers hostiles, jobs, compatibilité | G1-G8, R33-011-R33-012-R33-038 |
| S-064, S-065, S-066 | typographie, comparaison, diorama | G6-G9, R33-028 |

### S-067 à S-101 intégration UX V3.2

| IDs conservés | Domaines principaux | Raccordement V3.3 |
|---|---|---|
| S-067, S-068, S-069 | accueil, responsive et états UI | G2, F14, R33-018-R33-033 |
| S-070, S-071, S-072, S-073, S-074, S-075 | sélection, erreurs, clavier, aperçus, reprise, formats | G2, P01-P03, R33-008-R33-019 |
| S-076 | transfert Design Space | G4, R33-022 |
| S-077, S-078, S-079, S-080, S-081, S-082, S-083, S-084 | accessibilité, correction, préférences, aide et sorties | G2, F03-F14, R33-018-R33-020-R33-032 |
| S-085 | prévol cutter-only | G4, F06-F07, P02 |
| S-086, S-087, S-088 | toile, multi-sélection et gabarits | G6, F08-F09, P05 |
| S-089, S-090, S-091, S-092 | lots, planches, bibliothèque et polices | G6-G7, F09-F12, P04-P07-P08 |
| S-093, S-094, S-095, S-096 | essais utilisateur, accessibilité, récupération, latence | G8, R33-015-R33-018-R33-025-R33-039 |
| S-097, S-098 | répétition et recettes personnelles | G7, F10-F12 |
| S-099, S-100, S-101 | diorama, raccourcis et variantes | G9, F13-F14, R33-029 |

### Index individuel de contrôle

Cet index doit rester complet dans toute révision suivante :

`S-001 S-002 S-003 S-004 S-005 S-006 S-007 S-008 S-009 S-010`
`S-011 S-012 S-013 S-014 S-015 S-016 S-017 S-018 S-019 S-020`
`S-021 S-022 S-023 S-024 S-025 S-026 S-027 S-028 S-029 S-030`
`S-031 S-032 S-033 S-034 S-035 S-036 S-037 S-038 S-039 S-040`
`S-041 S-042 S-043 S-044 S-045 S-046 S-047 S-048 S-049 S-050`
`S-051 S-052 S-053 S-054 S-055 S-056 S-057 S-058 S-059 S-060`
`S-061 S-062 S-063 S-064 S-065 S-066 S-067 S-068 S-069 S-070`
`S-071 S-072 S-073 S-074 S-075 S-076 S-077 S-078 S-079 S-080`
`S-081 S-082 S-083 S-084 S-085 S-086 S-087 S-088 S-089 S-090`
`S-091 S-092 S-093 S-094 S-095 S-096 S-097 S-098 S-099 S-100`
`S-101`

## 5 Registre des exigences R33

| Plage | Contenu | Familles et parcours | Validation dominante |
|---|---|---|---|
| R33-001 à R33-005 | héritage, maturité, état partagé, identités et obsolescence | F10-F15, tous parcours | structure, intégration, concurrence |
| R33-006 à R33-008 | masques, fallback, séparation des formats | F02-F07, P01-P03-P06 | tests pixels et contrats d'export |
| R33-009 à R33-016 | migration, bibliothèque, jobs, stockage, sessions, diagnostic, licences | F10-F15, P04-P07-P08-P10 | récupération et sécurité |
| R33-017 à R33-020 | mesures IA, responsive, clavier, français | F02-F14, P01-P05 | Windows, navigateur et accessibilité |
| R33-021 à R33-024 | installation, Design Space, matériel, confidentialité | F07-F15, P01-P02-P09 | terrain et preuves privées |
| R33-025 à R33-032 | pannes, budgets, noms, polices, scores, réseau, rapports, préférences | F04-F15, tous parcours | adversarial, performance et reprise |
| R33-033 à R33-040 | états UI, SHA, gate humain, rollback, risques, compatibilité, observation, gel | F14-F15, tous parcours | release et gouvernance |

Index individuel :

`R33-001 R33-002 R33-003 R33-004 R33-005 R33-006 R33-007 R33-008 R33-009 R33-010`
`R33-011 R33-012 R33-013 R33-014 R33-015 R33-016 R33-017 R33-018 R33-019 R33-020`
`R33-021 R33-022 R33-023 R33-024 R33-025 R33-026 R33-027 R33-028 R33-029 R33-030`
`R33-031 R33-032 R33-033 R33-034 R33-035 R33-036 R33-037 R33-038 R33-039 R33-040`

## 6 Dossiers individuels des exigences

Chaque ligne ci-dessous est un dossier individuel initial. La deuxième colonne réintègre la priorité, le jalon lorsqu'il existe, l'intitulé, les dépendances lorsqu'elles existent et le critère canonique relevé dans la V3.2 ; l'[annexe historique intégrale](ROADMAP_HERITAGE_v3_3.md) reste l'autorité pour les détails de contexte. Les valeurs historiques ne sont pas réécrites dans leur archive gelée. `A/W/D/P` représente dans l'ordre `preuve_auto`, `preuve_windows`, `preuve_design_space` et `preuve_physique`. Dans les dossiers, `N` signifie `NON_EXECUTE`. Les quatre axes sont initialisés à `N/N/N/N` : leur reconstruction exige des preuves liées à des SHA et environnements exacts.

Codes d'autorité : `SRC` source et provenance ; `PRJ` cœur projet ; `UI` commandes applicatives ; `IA` fournisseur et ComfyUI ; `GEO` géométrie et export ; `FAB` Design Space et machine ; `JOB` gestionnaire de jobs ; `LIB` bibliothèque ; `TYPE` polices et texte ; `SEC` sécurité ; `OPS` installation et exploitation.

Codes risque et rollback : `B` baseline ou preuve, revert documentaire ; `P` données projet, restaurer le dernier snapshot sain ; `U` interaction, annuler la commande et restaurer l'état ; `I` IA, annuler et basculer manuel ou CPU ; `E` export, refuser la sortie et préserver projet et exports valides ; `F` fabrication, arrêter la revendication et conserver les fichiers ; `J` lot, checkpoint et relance idempotente ; `L` bibliothèque, reconstruire l'index ; `T` typographie, conserver le rendu ou choisir explicitement ; `X` extension, désactiver ou revert sans migration du noyau.

Les colonnes `Impl/tests` restent `A_RECONSTRUIRE` jusqu'à un audit séparé des preuves actuelles. La décision initiale `NON_VERIFIE` ne dégrade pas une preuve existante : elle interdit seulement de la présumer actuelle.

### Dossiers S-001 à S-050

| ID | Intitulé/source/dépendances | Couverture F/P/G | Autorité | statut_implementation | Impl/tests | A/W/D/P | Risque/rollback | Décision |
|---|---|---|---|---|---|---|---|---|
| S-001 | **P0** · G0-G9 (cf. V3.2) · Geler archive V21.14.1 et corpus ; dépendances : non détaillées ; critère : SHA + manifeste ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P10/G0 | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-002 | **P0** · G0-G9 (cf. V3.2) · Spécifier les trois contrats de sortie ; dépendances : non détaillées ; critère : exemples importables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F07/P01-P02-P06/G1 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-003 | **P0** · G0-G9 (cf. V3.2) · Définir modèle de projet/retouches sérialisables ; dépendances : non détaillées ; critère : ouverture/reprise identique ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07-P10/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-004 | **P0** · G0-G9 (cf. V3.2) · Réduire la complexité visible, conserver anciens IDs ; dépendances : non détaillées ; critère : anciens workflows ouvrables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10-F14/P01-P02/G1-G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-005 | **P0** · G0-G9 (cf. V3.2) · Test réel RMBG/SAM2/BiRefNet RTX 3070 ; dépendances : non détaillées ; critère : logs et masques réels ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I | NON_VERIFIE |
| S-006 | **P0** · G0-G9 (cf. V3.2) · Créer masques de référence des neuf images ; dépendances : non détaillées ; critère : vérité terrain annotée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G0 | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-007 | **P0** · G0-G9 (cf. V3.2) · Validation sémantique du sujet désiré ; dépendances : non détaillées ; critère : rejet des faux sujets ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I | NON_VERIFIE |
| S-008 | **P0** · G0-G9 (cf. V3.2) · Éditeur pinceaux/undo/reload vérifié sur frontend ; dépendances : non détaillées ; critère : aucun trait perdu ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03/P03/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-009 | **P0** · G0-G9 (cf. V3.2) · Assurance qualité Cricut par format ; dépendances : non détaillées ; critère : dimensions/trajets précontrôlés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F06-F07/P01-P02/G4 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-010 | **P0** · G0-G9 (cf. V3.2) · Couper physiquement des exemplaires Explore 5 ; dépendances : non détaillées ; critère : photos et mesures ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F07/P01-P02/G4 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| S-011 | **P0** · G0-G9 (cf. V3.2) · Fidélité SVG multicouche et analyse des formes ; dépendances : non détaillées ; critère : mesures render standard ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05/P06/G5 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-012 | **P0** · G0-G9 (cf. V3.2) · Chemins SVG utilisables avec matériau choisi ; dépendances : non détaillées ; critère : découpes testées ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F06-F13/P02-P09/G4-G5 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-013 | **P1** · G0-G9 (cf. V3.2) · Écran Express unifié ; dépendances : non détaillées ; critère : test utilisateur ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-014 | **P1** · G0-G9 (cf. V3.2) · Segmentation objets et fragments associés ; dépendances : non détaillées ; critère : suites multiobjets ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I | NON_VERIFIE |
| S-015 | **P1** · G0-G9 (cf. V3.2) · Nettoyage des halos / découpe et offset ; dépendances : non détaillées ; critère : comparatifs zoom ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03-F07/P01-P02/G2-G4 | GEO-UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-E | NON_VERIFIE |
| S-016 | **P1** · G0-G9 (cf. V3.2) · HD conditionnelle + diagnostic d'artefacts ; dépendances : non détaillées ; critère : avant/après objectif ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F04/P01/G2 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-017 | **P1** · G0-G9 (cf. V3.2) · Packaging « projet SmartSVG » ; dépendances : non détaillées ; critère : relecture multi-version ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-018 | **P1** · G0-G9 (cf. V3.2) · Queue/batch/cache avec reprise ; dépendances : non détaillées ; critère : lot interrompu/repris ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F12/P04-P08/G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| S-019 | **P1** · G0-G9 (cf. V3.2) · Benchmark Canva/Design Space sur corpus identique ; dépendances : non détaillées ; critère : rapport chronométré ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P01-P02/G8 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-F | NON_VERIFIE |
| S-020 | **P2** · G0-G9 (cf. V3.2) · Papier découpé multicouche / dioramas ; dépendances : non détaillées ; critère : prototype assemblé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F13/P09/G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X-F | NON_VERIFIE |
| S-021 | **P2** · G0-G9 (cf. V3.2) · OCR et gestion du texte sur affiches ; dépendances : non détaillées ; critère : texte préservé / averti ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09/P05/G9 | TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T-X | NON_VERIFIE |
| S-022 | **P2** · G0-G9 (cf. V3.2) · App autonome hors ComfyUI, si justifiée ; dépendances : non détaillées ; critère : décision architecture chiffrée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P10/G9 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X | NON_VERIFIE |
| S-023 | **P0** · G1.2 · Identité de sujet stable ; dépendances : S-003 ; critère : Identité persistante après retouche et export ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P03-P07/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-024 | **P0** · G1.3 · Projet `.smartsvg` v1 ; dépendances : S-003 ; critère : Chargement exact des masques, sources et actions ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07-P10/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-025 | **P0** · G2.1 · Écran Express métier ; dépendances : S-004 ; critère : Sticker simple sans graphe ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-026 | **P0** · G2.3 · Historique non destructif UI ; dépendances : S-024 ; critère : Undo/redo/reload conformes ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03/P03-P05/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-027 | **P0** · G3.2 · Contrôle GPU réel ; dépendances : S-005 ; critère : VRAM et latence mesurées ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I | NON_VERIFIE |
| S-028 | **P0** · G3.3 · Groupes sujet + accessoires ; dépendances : S-006,S-027 ; critère : Pas de perte silencieuse des détails annotés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-P | NON_VERIFIE |
| S-029 | **P0** · G4.1 · Contrat PNG/alpha Cricut ; dépendances : S-002 ; critère : Import Design Space contrôlé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F07/P01/G4 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-030 | **P0** · G4.2 · Contrat SVG Basic Cut ; dépendances : S-002 ; critère : Chemins fermés, géométrie contrôlée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F06/P02/G4 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-031 | **P0** · G4.3 · Matrice d'essais Explore 5 ; dépendances : S-029,S-030 ; critère : Coupons fabriqués et documentés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F07/P01-P02/G4 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| S-032 | **P0** · G5.5 · Export SVG édition vs fabrication ; dépendances : S-011,S-030 ; critère : Aucun profil confondu ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F06/P02-P06/G5 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-033 | **P1** · G5.2 · Préservation traits et petites régions ; dépendances : S-011 ; critère : IoU, MAE et risques suivis ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05/P06/G5 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-034 | **P1** · G5.3 · Simplification de Bézier ; dépendances : S-033 ; critère : Courbes réduites à fidélité non dégradée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F06/P06/G5 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-035 | **P1** · G6.1 · Canevas objets/textes ; dépendances : S-024 ; critère : Composition éditable après réouverture ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08/P05/G6 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-036 | **P1** · G6.3 · Fonts et conversion textes → tracés ; dépendances : S-035 ; critère : Pas de substitution silencieuse ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09/P05/G6 | TYPE-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T-E | NON_VERIFIE |
| S-037 | **P1** · G6.4 · Gabarits métiers ; dépendances : S-035 ; critère : Trois gabarits testés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08-F09/P05/G6 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-038 | **P1** · G7.1 · Job manager et checkpoints ; dépendances : S-024 ; critère : Reprise 50/50 sans doublon ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F12/P04-P08/G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| S-039 | **P1** · G7.3 · Variables CSV ; dépendances : S-035,S-038 ; critère : 30 variantes sans texte manquant ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09-F12/P08/G7 | JOB-TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J-T | NON_VERIFIE |
| S-040 | **P1** · G7.4 · Imposition mesurable ; dépendances : S-029,S-030 ; critère : Zéro collision, dimensions cohérentes ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F11/P04/G7 | GEO-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J-E | NON_VERIFIE |
| S-041 | **P1** · G7.2 · Bibliothèque locale ; dépendances : S-024 ; critère : Recherche/duplication/archivage fiables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07/G7 | LIB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | L | NON_VERIFIE |
| S-042 | **P0** · G8.2 · Audit de sécurité des projets ; dépendances : S-024 ; critère : Entrées adversariales contenues ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P10/G8 | SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-P | NON_VERIFIE |
| S-043 | **P0** · G8.3 · Benchmark Canva/Design Space ; dépendances : S-031,S-032 ; critère : Procédure égale, répétée et auditée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P01-P02/G8 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-F | NON_VERIFIE |
| S-044 | **P2** · G9 · Dioramas multi-plans ; dépendances : S-030,S-035 ; critère : Prototype réel assemblé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F13/P09/G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X-F | NON_VERIFIE |
| S-045 | **P2** · G9 · Vinyle multi-couleur ; dépendances : S-030,S-031 ; critère : Test superposition concluant ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F06-F13/P09/G9 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X-F | NON_VERIFIE |
| S-046 | **P2** · G9 · Application autonome ; dépendances : S-025,S-038 ; critère : Étude de coût et de maintenance ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P10/G9 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X | NON_VERIFIE |
| S-047 | **P2** · G9 · OCR texte de couverture ; dépendances : S-028,S-036 ; critère : Texte vérifié avant tout remplacement ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09/P05/G9 | TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T-X | NON_VERIFIE |
| S-048 | **P2** · G9 · Upscale IA artistique ; dépendances : S-027,F04 ; critère : Audit des détails inventés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F04/P01/G9 | IA-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-X | NON_VERIFIE |
| S-049 | **P0** · G0.2 · `corpus_manifest` et droits d'usage des fixtures ; dépendances : non détaillées ; critère : original hashé, origine et statut de droit explicites ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/TRANSVERSE/G0 | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-050 | **P0** · G0.3 · Vérité terrain versionnée + protocole annotations ; dépendances : non détaillées ; critère : ambiguïtés documentées, silhouettes/accessoires cohérents ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/TRANSVERSE/G0 | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |

### Dossiers S-051 à S-101

| ID | Intitulé/source/dépendances | Couverture F/P/G | Autorité | statut_implementation | Impl/tests | A/W/D/P | Risque/rollback | Décision |
|---|---|---|---|---|---|---|---|---|
| S-051 | **P0** · G1.1 · Rapprochement historique S-001–S-022 et inventaire réel workflows ; dépendances : non détaillées ; critère : fiches source conservées ; contrats B0 réellement vérifiés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/TRANSVERSE/G1 | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-052 | **P0** · G1.2 · Schéma `Subject/Source/Artifact` avec identité et coordonnées ; dépendances : non détaillées ; critère : rotations/crop/alpha testés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F01-F10/P01-P03/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-053 | **P0** · G1.3 · Format `.smartsvg` v1, migration et recovery ; dépendances : non détaillées ; critère : crash/reopen/malveillance testés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07-P10/G1 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-054 | **P0** · G2.4 · Preuves orthogonales et sidecar `manifest.json` ; dépendances : non détaillées ; critère : aucune fausse certification dans PNG/SVG ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F07/P01-P02-P06/G2 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| S-055 | **P0** · G4.1 · Profil Explore 5 A4/Letter, imprimer portrait/poser A4 paysage ; dépendances : non détaillées ; critère : procédure suivie, captures et coupon ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F07/P01/G4 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| S-056 | **P0** · G4.2 · QA geometry Cut en mm : holes, islands, segments, offset ; dépendances : non détaillées ; critère : coupe simulée signalée comme telle et coupon réel ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F06/P02/G4 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-057 | **P0** · G4.3 · Registre matériel : machine, lame, tapis, matière, tests ; dépendances : non détaillées ; critère : valeurs étiquetées source/calibrée/hypothèse ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F13/P09/G4 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| S-058 | **P1** · G3.1 · Matrice environnement local et fournisseur IA ; dépendances : non détaillées ; critère : pas de promesse non exécutée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02/P03/G3 | IA-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-B | NON_VERIFIE |
| S-059 | **P1** · G2.1 · Audit accessibilité clavier/contraste/labels ; dépendances : non détaillées ; critère : scénario Express réalisable au clavier ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01-P03/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-060 | **P1** · G5.1 · Score qualité séparé silhouette/couleur/géométrie ; dépendances : non détaillées ; critère : benchmark reproductible/échantillon fixé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F04-F06/P01-P02-P06/G5 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-B | NON_VERIFIE |
| S-061 | **P0** · G1.4 · Tests fichiers hostiles et bombes XML/ZIP ; dépendances : non détaillées ; critère : aucune sortie hors projet ni épuisement incontrôlé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P10/G1 | SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-P | NON_VERIFIE |
| S-062 | **P1** · G7.1 · File de jobs avec identité, cache et pause/reprise ; dépendances : non détaillées ; critère : 50 objets après interruption sans duplication ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F12/P04-P08/G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| S-063 | **P1** · G8.1 · Matrice de compatibilité ComfyUI/frontend/node API ; dépendances : non détaillées ; critère : installation ancienne/nouvelle testées ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P10/G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-064 | **P1** · G6 · Contrat typographie et licence des polices ; dépendances : non détaillées ; critère : rendu reproductible ou avertissement précis ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09/P05/G6 | TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T | NON_VERIFIE |
| S-065 | **P1** · G8.3 · Comparaison contrôlée Design Space/Canva/SmartSVG ; dépendances : non détaillées ; critère : protocole temps/clics/qualité/correction commun ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F15/P01-P02/G8 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-F | NON_VERIFIE |
| S-066 | **P2** · G9 · Prototype diorama à quatre plans alignables ; dépendances : non détaillées ; critère : assemblage réel et tolérances reportées ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F13/P09/G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X-F | NON_VERIFIE |
| S-067 | **P0** · G2.1 · Accueil 4 objectifs + Reprendre ; dépendances : non détaillées ; critère : Choix d’usage sans graphe ni terminologie IA ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-068 | **P0** · G2.5 · Schéma unique d’écran responsive desktop ; dépendances : non détaillées ; critère : 1366×768 + 1920×1080, pas d’action cachée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01-P05/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-069 | **P0** · G2.5 · États vide/chargement/erreur/export ; dépendances : non détaillées ; critère : Aucun contrôle factice ; succès partiel signalé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-070 | **P0** · G2.2 · Sélection directe et croisée sujets↔vignettes ; dépendances : non détaillées ; critère : T-02 : 12 sujets identifiables, même ID ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F02-F14/P03/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-071 | **P0** · G2.6 · Erreurs cliquables avec région et correction réversible ; dépendances : non détaillées ; critère : Masque rectangle : refus ou reprise explicite ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03-F14/P03/G2 | UI-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-E | NON_VERIFIE |
| S-072 | **P0** · G2.7 · Flux Express souris + clavier ; dépendances : non détaillées ; critère : T-02/U-01 jusqu’à export sans drag obligatoire ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01-P03/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-073 | **P0** · G2.8 · Aperçus original/masque/coupe séparés ; dépendances : non détaillées ; critère : Dimensions constantes, aucune inversion confondue ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03-F06/P01-P03/G2 | UI-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-E | NON_VERIFIE |
| S-074 | **P0** · G2.9 · Reprise dernier projet et contexte ; dépendances : non détaillées ; critère : fermeture + réouverture identiques, pas de retouche perdue ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P01-P07/G2 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| S-075 | **P0** · G2.4 · Panneau de validation du format par usage ; dépendances : non détaillées ; critère : PNG Print Then Cut ≠ SVG Cut ≠ SVG Art ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F07/P01-P02-P06/G2 | UI-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-E | NON_VERIFIE |
| S-076 | **P0** · G4.6 · Checklist d’export et transfert Design Space ; dépendances : non détaillées ; critère : fichier recommandé, version, mise en garde A4/Letter ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F07/P01-P02/G4 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| S-077 | **P1** · G2.7 · Alternative clavier aux gestes souris complexes ; dépendances : non détaillées ; critère : sélection/déplacement/redimensionnement possible ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/P01-P05/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-078 | **P1** · G2.7 · Contrastes/focus/texte ajustable ; dépendances : non détaillées ; critère : audit WCAG applicable et test manuel ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-079 | **P1** · G2.8 · Loupe locale et comparaison glissante ; dépendances : non détaillées ; critère : détecter halo / trait coupé dans fixture ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03-F04/P01-P03/G2 | UI-GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-080 | **P1** · G2.3 · Pinceau correction tactile souris + aperçu effet ; dépendances : non détaillées ; critère : undo, zoom et sauvegarde sans incohérence ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F03/P03/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-081 | **P1** · G2.9 · Réglages récents et préréglages utilisateur ; dépendances : non détaillées ; critère : aucune application cachée sur nouveau projet ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10-F14/P01-P07/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-082 | **P1** · G2.5 · Disposition de panneaux persistante ; dépendances : non détaillées ; critère : contexte Express/Atelier conservé, reset disponible ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-083 | **P1** · G2.6 · Recherche d’action et aide contextuelle ; dépendances : non détaillées ; critère : utilisateur retrouve l’outil sans documentation externe ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G2 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-084 | **P1** · G2.9 · Ouvrir dossier/export/rapport depuis la réussite ; dépendances : non détaillées ; critère : fichiers corrects et artefacts immuables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P01-P02-P07/G2 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-085 | **P1** · G4.6 · Aperçu cutter-only et repères micro-détails ; dépendances : non détaillées ; critère : alertes pointent sur chemins précis ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F06-F07/P02/G4 | GEO-FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-F | NON_VERIFIE |
| S-086 | **P1** · G6.6 · Toiles avec poignées et dimensions mm ; dépendances : non détaillées ; critère : proportions, alignements, guides vérifiés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08/P05/G6 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-087 | **P1** · G6.6 · Multi-sélection, groupement et menu contextuel ; dépendances : non détaillées ; critère : batch d’objets sans perte d’identité ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08/P05/G6 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| S-088 | **P1** · G6.7 · Trois gabarits de départ guidés ; dépendances : non détaillées ; critère : étiquette, carte, topper sauvegardés et repris ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08-F09/P05/G6 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| S-089 | **P1** · G7.6 · Tableau de lot et reprise d’un échec isolé ; dépendances : non détaillées ; critère : 50 éléments, 1 échec, 49 conservés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F12/P04-P08/G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| S-090 | **P1** · G7.4 · Comparer deux dispositions de planche ; dépendances : non détaillées ; critère : aucune collision ; placements verrouillés stables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F11/P04/G7 | GEO-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J-E | NON_VERIFIE |
| S-091 | **P1** · G7.2 · Bibliothèque avec miniatures et filtre métier ; dépendances : non détaillées ; critère : retrouver un projet en test utilisateur ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07/G7 | LIB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | L | NON_VERIFIE |
| S-092 | **P1** · G6.3 · Choix de police avec aperçu et alertes glyphes ; dépendances : non détaillées ; critère : caractères FR et police absente contrôlés ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F09/P05-P08/G6 | TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T | NON_VERIFIE |
| S-093 | **P0** · G8.6 · Protocole de test utilisateur novice/régulier ; dépendances : non détaillées ; critère : tests scénarisés et observations anonymisées ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G8 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-094 | **P0** · G8.6 · Tests d’accessibilité + vérification Windows zoom ; dépendances : non détaillées ; critère : aucun blocage critique de la voie principale ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G8 | UI-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-B | NON_VERIFIE |
| S-095 | **P0** · G8.6 · Tests de récupération pendant export/IA ; dépendances : non détaillées ; critère : zéro perte de source/correction validée ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10-F15/P10/G8 | PRJ-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P-J | NON_VERIFIE |
| S-096 | **P1** · G8.6 · Instrumentation locale UX et latence (opt-in export rapport) ; dépendances : non détaillées ; critère : p50/p90 et cas d’erreur disponibles localement ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14-F15/TRANSVERSE/G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| S-097 | **P2** · G7 · Commandes « refaire sur sélection » ; dépendances : non détaillées ; critère : répétition sûre sur objets compatibles ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F08-F12/P04-P08/G7 | UI-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-J | NON_VERIFIE |
| S-098 | **P2** · G7 · Liste de recettes/gabarits personnels ; dépendances : non détaillées ; critère : modèle portable et droits visibles ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F10/P07/G7 | LIB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | L | NON_VERIFIE |
| S-099 | **P2** · G9 · Guide d’assemblage de diorama dans l’UI ; dépendances : non détaillées ; critère : prototype mesuré et assemblé ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F13/P09/G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | X-F | NON_VERIFIE |
| S-100 | **P2** · G9 · Raccourcis personnalisables / commandes favorites ; dépendances : non détaillées ; critère : conflits clavier détectés et restaurables ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F14/TRANSVERSE/G9 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-X | NON_VERIFIE |
| S-101 | **P2** · G9 · Comparaison de variantes avec scores séparés ; dépendances : non détaillées ; critère : rendu/coupe/coût non confondus ; [source intégrale](ROADMAP_HERITAGE_v3_3.md) | F05-F11/P04-P06/G9 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E-X | NON_VERIFIE |

### Dossiers R33-001 à R33-040

| ID | Intitulé/source/dépendances | Couverture F/P/G | Autorité | statut_implementation | Impl/tests | A/W/D/P | Risque/rollback | Décision |
|---|---|---|---|---|---|---|---|---|
| R33-001 | V3.3 maître §11 ; V3.2 complète | TRANSVERSE/tous/tous | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-002 | V3.3 maître §2.4 | TRANSVERSE/tous/tous | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-003 | V3.3 maître §5.1 | F10-F14/tous/G1-G7 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| R33-004 | V3.3 maître §5.2 | F02-F10/P03-P10/G1-G3 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P-U | NON_VERIFIE |
| R33-005 | V3.3 maître §5.2 | F02-F14/P03/G3 | PRJ-IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-U | NON_VERIFIE |
| R33-006 | V3.3 maître F03 | F03/P03/G2-G3 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| R33-007 | V3.3 maître F02 | F02-F14/P01-P03/G2-G3 | IA-UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-U | NON_VERIFIE |
| R33-008 | V3.3 maître §2.1 | F05-F07/P01-P02-P06/G2-G6 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| R33-009 | V3.3 maître §5.4 | F10/P07-P10/G1-G8 | PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P | NON_VERIFIE |
| R33-010 | V3.3 maître §5.4 | F10/P07/G7 | LIB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | L | NON_VERIFIE |
| R33-011 | V3.3 maître §5.5 | F12/P04-P08/G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| R33-012 | V3.3 maître §5.5 | F02-F12/P03-P04-P08/G3-G7 | JOB-IA | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J-I | NON_VERIFIE |
| R33-013 | V3.3 maître §8 | F10-F15/P10/G1-G8 | PRJ-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P-B | NON_VERIFIE |
| R33-014 | V3.3 maître §8 | F14-F15/P03/G2-G3 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| R33-015 | V3.3 maître P10 | F15/P10/G8 | OPS-SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-016 | V3.3 maître §8 | F09-F15/TRANSVERSE/G0-G8 | SRC-SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-T | NON_VERIFIE |
| R33-017 | V3.3 maître G3 | F02/P03/G3 | IA-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | I-B | NON_VERIFIE |
| R33-018 | V3.3 maître F14 | F14/tous/G2-G8 | UI-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-B | NON_VERIFIE |
| R33-019 | V3.3 maître F14 | F14/tous/G2-G8 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| R33-020 | V3.3 maître F14 | F14/tous/G2-G8 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| R33-021 | V3.3 maître §8 | F15/P10/G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-022 | V3.3 maître G4 | F07/P01-P02/G4-G8 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| R33-023 | V3.3 maître G4-G9 | F06-F13/P02-P09/G4-G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| R33-024 | V3.3 maître §8 | F15/tous/tous | SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-025 | V3.3 maître §8 | F02-F15/P10/G1-G8 | PRJ-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P-J | NON_VERIFIE |
| R33-026 | V3.3 maître §8 | F01-F12/P03-P04-P08/G2-G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-J | NON_VERIFIE |
| R33-027 | V3.3 maître §8 | F10-F12/P04-P08/G1-G7 | PRJ-JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | P-J | NON_VERIFIE |
| R33-028 | V3.3 maître F09 | F09/P05-P08/G6-G8 | TYPE | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | T | NON_VERIFIE |
| R33-029 | V3.3 maître F05-F06 | F05-F06/P02-P06/G4-G6 | GEO | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | E | NON_VERIFIE |
| R33-030 | V3.3 maître §2.3 | F15/tous/tous | SEC-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-031 | V3.3 maître F11-F12 | F11-F12/P04-P08/G4-G7 | JOB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | J | NON_VERIFIE |
| R33-032 | V3.3 maître §5.4 | F10-F14/P07/G2-G8 | UI-PRJ | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-P | NON_VERIFIE |
| R33-033 | V3.3 maître §5.5 | F14/tous/G2-G8 | UI | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U | NON_VERIFIE |
| R33-034 | V3.3 maître §10 | F15/tous/tous | SRC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-035 | V3.3 maître §10 | F07-F13/P01-P02-P09/G4-G9 | FAB | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | F | NON_VERIFIE |
| R33-036 | V3.3 maître §10 | TRANSVERSE/tous/tous | PRJ-OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B-P | NON_VERIFIE |
| R33-037 | V3.3 maître §10 | TRANSVERSE/tous/tous | SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-038 | V3.3 maître G8 | F15/P10/G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |
| R33-039 | V3.3 maître §10 | F14/tous/G2-G8 | UI-SEC | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | U-B | NON_VERIFIE |
| R33-040 | V3.3 maître G8 | TRANSVERSE/tous/G8 | OPS | SPECIFIE | A_RECONSTRUIRE | N/N/N/N | B | NON_VERIFIE |

## 7 Modèle de preuve

Une preuve minimale contient :

```text
requirement_id:
status_claimed:
repository:
branch:
commit_sha:
tree_sha:
environment:
versions:
command_or_protocol:
input_fixture_or_private_evidence_id:
result:
limitations:
created_at:
reviewed_by:
```

Les médias utilisateur et photographies de fabrication restent dans un emplacement privé. Le dépôt public ne reçoit qu'un identifiant, des mesures non personnelles et une synthèse expurgée.

## 8 Règles de transition

### Vers IMPLEMENTE

Le diff est identifié, limité au micro-lot, réversible et ne modifie pas les autorités sans migration approuvée.

### Vers RACCORDE

L'action est accessible depuis le parcours réel, utilise les données réelles attendues et ne dépend pas d'une démonstration fictive non signalée.

### Vers TESTE_AUTO

Les tests pertinents sont verts sur le head exact. Une exécution sautée, annulée ou issue d'un autre SHA ne compte pas.

### Vers TESTE_WINDOWS

L'installation cible, les versions, les routes ComfyUI, le navigateur, les chemins et les droits sont enregistrés. Une maquette statique seule ne compte pas.

### Vers TESTE_DESIGN_SPACE

Le fichier réel est importé dans une version précisée de Design Space. L'apparence, la taille, les chemins et les avertissements sont consignés.

### Vers TESTE_PHYSIQUE

La machine, le firmware si disponible, la lame, le tapis, la matière, les réglages, l'impression, le résultat et les écarts sont consignés. Une simulation ou un aperçu ne compte pas.

### Vers STABILISE

Les gates de la famille et du jalon sont franchis, les risques P0 ou P1 sont fermés ou explicitement bloquants, les migrations et rollbacks sont testés et la documentation correspond au produit.

## 9 Statut initial de la V3.3

La création de ce registre ne change aucun statut fonctionnel existant. Tous les statuts doivent être reconstruits à partir des preuves associées à leurs SHA. Les documents d'état ou anciennes CI servent d'index de recherche, pas de preuve automatiquement actuelle.

## 10 Contrôle de cohérence par micro-lot

Avant ouverture : vérifier ID, parcours, autorité, dépendances, risques et données autorisées.
Avant commit : vérifier tests ciblés, migration, sécurité, accessibilité et rollback.
Avant PR : vérifier diff complet, head, base, conflits et liens de preuve.
Avant fusion : vérifier contre-expertise indépendante, CI fraîche, matrice de couverture et absence de blocage.
Après fusion : mettre à jour l'état opérationnel depuis le commit fusionné, sans modifier rétroactivement la preuve d'un ancien head.
