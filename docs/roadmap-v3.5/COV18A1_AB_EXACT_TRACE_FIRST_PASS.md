# COV-18A-1 — Traçabilité A/B : première tranche vérifiée (13/11/2026)

**Statut : CANDIDAT, audit documentaire partiel, NON CERTIFIÉ.** Source de correspondances : `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md` sur main, blob `177a0ecff5edd816e1bf879fc93c2a49efd83690`, repris dans `COVERAGE_V34_TO_V35.md`. Décisions UX : `COV17A_UX_A01_A16_SEMANTIC_AUDIT.md`, `COV17B_UX_B01_B14_SEMANTIC_AUDIT.md`, et `COV18A_UX_AB_CROSS_REVIEW.md`. **Les associations UX↔exigence sont des hypothèses sémantiques de cette fiche**, contrairement aux liens S↔V34↔T-V34-22 ci-dessous, explicitement écrits dans le lot 23. Ne pas les présenter comme adoptés.

## Matrice de premier rapprochement (10/30 IDs A/B ; 20 en attente)
| UX #134 | Exigence source explicite | Ticket(s) V34 explicitement rattachés à cette exigence | Test transversal explicitement cité | Écart à vérifier avant validation |
|---|---|---|---|---|
| A02 gestes de sélection | S-070 | V34-075, V34-132 | T-V34-22-04 | lasso/ellipse et clavier non déduits du ticket |
| A03 multi-zones | R33-006 | V34-028, V34-133 | T-V34-22-04 | booléens trous/îlots et conservation float32 non prouvés |
| A04 intelligence sélection | S-007 | V34-069, V34-110, V34-007, V34-071, V34-082 | T-V34-22-05 | alternative CPU/IA, confiance et consentement à confronter au critère complet |
| A06 détourage | S-014 | V34-073 | T-V34-22-12 | segmentation ≠ chemin CUT ni qualité de détourage |
| A08 qualité/HD | S-016 | V34-089 | T-V34-22-05 | interpolation ≠ restitution de détail réel |
| A09 contrôle visuel | S-073 | V34-091, V34-095 | T-V34-22-05 | vérifier diff 1:1 et transparence |
| A12 vectorisation | S-032 | V34-098, V34-129, V34-112 | T-V34-22-01 | SVG d'édition distinct de Basic Cut et CUT multicouche |
| A15 optimisation | S-034 | V34-099 | T-V34-22-01 | conservation trous et fidélité après simplification |
| B04 poignées/transforms | S-086 | V34-133 | T-V34-22-04 | manipulation persistante non autorisée sans schéma revu |
| B09 texte éditable | S-036 | **AUCUN ticket V34 direct (G6/G9)** | Test V3.3 à relier | police, glyphes, licence, sauvegarde/reprise : blocage d'autorité |

**Important :** l'association A03↔R33-006 est limitée au contrat de masque, pas une preuve que les booléens multi-zones sont couverts. A06↔S-014 est une proximité fonctionnelle, pas un rattachement normatif UX établi. Pour B09, S-021/S-064/S-092/R33-028 restent également à rapprocher ; ne pas inventer de V34.

## Décisions de contre-expertise
1. **A04 :** garder la sélection intelligente candidate, mais ne pas substituer un masque IA à une sélection humaine sans preview et consentement. La segmentation et la sélection ne sont pas synonymes.
2. **A08 :** garder l'amélioration HD conditionnelle ; afficher interpolation et diagnostic sans prétendre créer du détail réel. Réutiliser le port CPU déjà audité.
3. **A12/A15 :** aucune optimisation topologique ne doit modifier le rôle de sortie. Les quatre sorties restent PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche et SVG d'édition, chacune avec QA distincte.
4. **B04/B09 :** brouillons réversibles en mémoire seulement tant que le schéma V1 et le writer CAS ne peuvent persister ces objets ; une évolution persistante exige ADR, migration explicite et accord propriétaire.

## Contrats de vérification pour le prochain passage
Chaque ligne est à enrichir avec **critère intégral V3.3**, DoD exact du ticket V34, scénario spécifique T-V34-lot-nn, port source exact au HEAD et consommateurs, statut de preuve indépendant. Les tests transversaux `T-V34-22-xx` ne sont **pas** les recettes spécifiques et ne prouvent pas les 437 tests PASS. Un lien de planification n'est pas une certification.

**Test positif à spécifier :** ouvrir PNG synthétique, sélectionner un sujet et son masque float32, modifier une copie, Undo, sauver/recharger via writer CAS et comparer SHA/identité. **Négatifs :** (N1) CAS révisé entre preview et commit → conflit sans écriture ; (N2) masque de mauvaise taille/trou disparu → refuser et conserver l'original ; (N3) SVG actif ou coordonnées non finies → rejeter sans export trompeur ; (N4) police absente/licence inconnue → diagnostic sans substitution ; (N5) GPU absent/téléchargement refusé → repli manuel sans réseau. **Récupération :** crash/disque plein/concurrence/rollback à tester séparément. Tests produits réellement exécutés dans cette fiche : **0** ; Windows, GPU, Design Space, coupe physique : **NOT_RUN**.

**UX cible :** découverte par un atelier unique, geste direct, feedback avant/après, Undo et reprise ; expert : SHA, mm, provenance et QA visibles. 1366×768, DPI 200 %, focus clavier, contraste et mouvement réduit : **protocoles requis, non exécutés**. Performance : instrumenter p50/p95, RAM et VRAM sur fixtures synthétiques, aucun seuil mesuré inventé.

## Contrôle 25 axes
01–05 : inventaires 24/141/140/80/437 hérités, **10/30 correspondances candidates** seulement ; 06 preuves distinctes ; 07 CAS/float32 ; 08 quatre exports ; 09 tri-state machine (N/A aux gestes mais conservé pour sortie) ; 10–13 geste/Undo/clavier/récupération spécifiés non testés ; 14 IA opt-in ; 15 raster HD ; 16 SVG/topologie ; 17 Fabrique/batch N/A à ce micro-lot, obligations inchangées ; 18 Delivery N/A, contrat inchangé ; 19 #141 N/A, arbitrages ailleurs ; 20 mesures futures ; 21 fixtures synthétiques/licences ; 22 branche docs uniquement ; 23 pas de second store ; 24 adoption/CI/revue ouvertes ; 25 aucune compression de critères.

**Prochaine action unique : COV-18A-1b** — compléter les **20 IDs A/B restants**, puis confronter **les 30** aux critères V3.3 intégraux, DoD V34 et scénarios spécifiques. Aucune certification 30/30 avant cette étape.
