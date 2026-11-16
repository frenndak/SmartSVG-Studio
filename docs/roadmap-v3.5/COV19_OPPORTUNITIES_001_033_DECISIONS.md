# V35-COV-19 — Contre-expertise des 33 opportunités historiques

> 13 novembre 2026 — **CANDIDAT, NON NORMATIF**. Source : `docs/roadmap-v3.4/OPPORTUNITIES.md` sur main, #141 et #142. Le présent registre ne crée aucun ticket de code, ne change aucune priorité normative V3.4 et ne prouve aucun test. Les IDs O-001..O-033 restent tous identifiables. Les scores historiques sont heuristiques, pas des preuves.

## Matrice individuelle de décision

| ID | Décision candidate | Horizon | Destination/traitement | Contre-expertise contradictoire / risque principal |
|---|---|---|---|---|
| O-001 | **RACCORDER** | P1 | guide de transfert et journal local ; rapprocher O-032 | Déclaration utilisateur ≠ preuve DS |
| O-002 | **AMÉLIORER** | P1 | Print Then Cut Assistant ; rapprocher O-025 | Dimension imprimée non garantie |
| O-003 | **REJETER** | hors périmètre | pilotage Cricut direct ; rapprocher O-032 | API officielle non démontrée |
| O-004 | **RACCORDER** | P1 | prévol opérations et aperçu ; rapprocher O-031 | Ordre physique non certifié |
| O-005 | **REPORTER** | P2 | Fabrique 3D géométrique ; rapprocher C18 | Simulation ≠ comportement carton |
| O-006 | **AMÉLIORER** | P1 | comparateur migration opt-in ; rapprocher O-022 | Données privées et double calcul |
| O-007 | **RACCORDER** | P1 | diagnostic capacités ; rapprocher O-023 | Installé ≠ testé |
| O-008 | **AMÉLIORER** | P1 | audit portabilité/partage ; rapprocher E01 | Licence et chemins externes |
| O-009 | **RACCORDER** | P1 | Undo groupé ; rapprocher E12 | Exports externes non annulables |
| O-010 | **AMÉLIORER** | P1 | propositions IA périmées ; rapprocher D11 | CAS et durée de conservation |
| O-011 | **RACCORDER** | P1 | bac à sable import ; rapprocher A01 | ZIP et parsing hostiles |
| O-012 | **FUSIONNER** | P1 | légende accessible opérations ; rapprocher O-004 | Ne pas créer second panneau |
| O-013 | **FUSIONNER** | P1 | explicabilité de proposition ; rapprocher O-016 | Raison ≠ diff de mutation |
| O-014 | **AMÉLIORER** | P1 | préférences par intention ; rapprocher E07 | Ne jamais réutiliser matériau tacitement |
| O-015 | **REJETER** | hors périmètre | micro permanent ; rapprocher D12 | Confidentialité et complexité |
| O-016 | **RACCORDER** | P1 | diff exact avant commit ; rapprocher O-013 | Ne pas appliquer sur état périmé |
| O-017 | **FUSIONNER** | P1 | erreurs réparables ; rapprocher E14 | Pas de faux succès |
| O-018 | **REJETER** | hors périmètre | exécution automatique non consentie ; rapprocher O-016 | Mutation externe sans accord |
| O-019 | **AMÉLIORER** | P1 | relations accessoires/sujets ; rapprocher B03 | Conserver IDs et masques |
| O-020 | **RACCORDER** | P1 | inspection masques 100% ; rapprocher A09 | Float32 et alpha non équivalents |
| O-021 | **REJETER** | hors périmètre | cloud photos automatique ; rapprocher D01 | Réseau et confidentialité |
| O-022 | **AMÉLIORER** | P1 | comparaison IA/manuelle ROI ; rapprocher O-006 | Modèle absent / métriques inconnues |
| O-023 | **RACCORDER** | P1 | provenance modèles ; rapprocher D08 | Licence/hash et révocation |
| O-024 | **REJETER** | hors périmètre | installation modèle silencieuse ; rapprocher D08 | Consentement obligatoire |
| O-025 | **RACCORDER** | P1 | aperçu franges PNG ; rapprocher E15 | Aperçu ≠ impression réelle |
| O-026 | **AMÉLIORER** | P1 | diff topologie alpha ; rapprocher E15 | Seuils et interprétation |
| O-027 | **REJETER** | hors périmètre | upscale IA automatique ; rapprocher D04 | Interpolation ≠ détail acquis |
| O-028 | **AMÉLIORER** | P1 | budget paths SVG ; rapprocher C07 | Limites DS versionnées |
| O-029 | **RACCORDER** | P1 | verrouillage îlots/trous ; rapprocher C07 | Topologie après simplification |
| O-030 | **REJETER** | hors périmètre | coupe automatique par couleur ; rapprocher C06 | Couleur ≠ opération |
| O-031 | **RACCORDER** | P1 | conflit segments/opérations ; rapprocher C06 | Ambiguïté CUT/SCORE |
| O-032 | **FUSIONNER** | P1 | guide DS après import ; rapprocher O-001 | Validation manuelle seulement |
| O-033 | **REJETER** | hors périmètre | SCORE automatique couleur/pointillés ; rapprocher C06 | Sémantique non prouvée |

## Analyse des dépendances et des non-doublons

Les regroupements O-001/O-032 (transfert Design Space), O-004/O-012/O-031 (sémantique et accessibilité des opérations), O-013/O-016/O-017 (explication, diff exact, refus réparable), O-006/O-022 (comparaison, mais **axes de comparaison différents**), O-020/O-025/O-026 (masque source, PNG publié, diff de topologie) partagent une **surface UX** mais conservent des critères distincts. « FUSIONNER » désigne la surface et le parcours, jamais la disparition d'un ID ou d'un critère historique. Chaque implémentation doit rester une extension de ticket existant lorsque son DoD couvre le besoin ; un ticket neuf exige une lacune explicitement prouvée.

**Dépendances P0 inchangées :** projet unique .smartsvg V1, SHA/CAS, identités Subject et masques float32, writer/Undo, preview/QA, quatre exports séparés (PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG éditable). Les rôles de Smart Delivery sont des consommateurs d'artefacts existants et non de nouveaux exporteurs. Les profils machine restent KNOWN/UNKNOWN et la coupe physique ne peut être déclarée PASS par un guide.

**Revue hostile / alternative simple :** commencer par le prévol et une checklist manuelle plutôt que par une intégration Cricut non documentée ; par un diagnostic local et un mode CPU/manuel plutôt que par un téléchargement de modèle ; par une comparaison déterministe et des rapports expurgés plutôt que par un cloud. Une amélioration « Smart » n'oblige jamais à ajouter un bouton dédié. La solution minimale doit être testée avant une architecture nouvelle.

## Contrat d'exécution à approfondir avant certification

Pour chaque opportunité retenue : lier exactement l'exigence V3.3 et son texte intégral, le ticket V34 et son DoD, le scénario T-V34 et la preuve réelle, les consommateurs Windows ; définir l'interface typée (unités, version, erreurs, provenance), transitions PREVIEW→ACCEPT→CAS_COMMIT→UNDO, cas vide/pending/erreur, clavier/focus/1366×768/DPI 200 %, permissions/licences, mesures de latence sur fixtures autorisées. **Tests négatifs minimaux transversaux :** (N1) source ou révision CAS changée, refus sans mutation ; (N2) profil machine/licence inconnue, statut UNKNOWN sans instruction inventée ; (N3) entrée SVG/PNG/ZIP hostile, refus sans écriture ; (N4) annulation/disque plein et relance concurrente, aucun artefact corrompu ; (N5) absence IA/VRAM insuffisante, parcours manuel disponible sans réseau. Tests unitaires non-skip, UI Windows, GPU, Design Space et coupe réelle constituent cinq preuves disjointes ; tous **NOT_RUN dans cette fiche**.

## Revue des 25 axes qualité — état de cette fiche

La fiche est un **arbitrage d'opportunités**, pas une spécification individuelle prête à coder. Axes inventaire, non-perte, anti-doublon, priorité, risques, frontière d'autorité, confidentialité et non-fausse-preuve : **revus au niveau de la matrice**. Axes architecture détaillée, contrats API vérifiés sur HEAD, JTBD et parcours par ID, TDD par ID, tests positifs/négatifs par ID, mesure de performance, accessibilité instrumentée, preuve Windows/DS/physique, contre-expertise de licence par modèle : **OUVERTS**, et non « non applicables » ; aucune certification n'est attribuée. Un contrôle du contrat source de 25 critères reste obligatoire lors de la consolidation finale.

## Couverture et prochaine action

33/33 opportunités **décidées à titre candidat** ; 25 retenues ou reportées et 8 rejetées (comptage à revérifier depuis la table). Les 24 lots, 141 exigences, 140 tickets, 80 UX et 437 scénarios restent inventoriés ; 431/437 liens historiques explicites et dix G6/G9 sans ticket direct ne deviennent pas des preuves sémantiques. **Prochaine action unique : COV-20**, rapprocher individuellement les opportunités P1 O-001/O-002/O-004/O-028/O-032 de #141 Smart Delivery V1/V2 et des DoD exacts des lots fabrication, avec un protocole Windows/Design Space distinct.
