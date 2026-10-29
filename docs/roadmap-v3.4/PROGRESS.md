# SmartSVG V3.4 — Journal de progression

## Cycle 01 / 24 — Référentiel et audit de base

- **Base main auditée :** fdbda304beb77d97340a8be4dd5c5e9cefde15f4 (28 octobre 2026).
- **Branche documentaire :** codex/docs-roadmap-v3-4-campaign.
- **Statut :** lot 01 documenté ; aucun code moteur modifié, aucune certification.
- **Sources consultées :** AGENTS.md, README.md, ROADMAP_MASTER/TRACEABILITY/COVERAGE/HERITAGE/AUDIT V3.3, ETAT_ACTUEL, fichiers code G2.2/G3.3e, fournisseur IA et Atelier.
- **Livrables :** README.md, 01_BASELINE_AUDIT.md, HERITAGE_INDEX.md, PROGRESS.md dans ce dossier.
- **Contrôle de couverture :** 101 S + 40 R33 = 141 IDs uniques sans lacune ; 40 intitulés R33 lus dans le maître.
- **Tickets proposés :** V34-001 à V34-005, tous SPECIFIES, non implémentés.
- **Décisions proposées :** V3.3 reste active ; réutilisation du noyau projet ; migration incrémentale ; ComfyUI comme adaptateur ; fabrication sémantique distincte du SVG.
- **Écarts ouverts :** G3.3e plus récent que ETAT_ACTUEL ; S-022/S-046 classent autonomie en G9/P2 ; IA dépendante de nœuds ; graphe imports incomplet ; aucune preuve Windows/RTX/Design Space/physique.
- **Superpowers :** skills recherchés, **aucune compétence Superpowers exposée** dans ce runtime ; méthodologie de conception/contre-expertise appliquée sans prétendre avoir chargé le plugin.
- **GitHub :** accès lecture/écriture OK ; branche documentaire, commits et PR draft à vérifier par relecture.
- **Prochain lot 02 :** vision, limites, personas, parcours « 12 escargots → stickers » et « boîte → Score + Cut », objectifs mesurables, états UX.
- **Reprise :** relire HEAD, issue #72, PR et ce journal ; ne pas dupliquer V34-001..005.

## Cycle 02 / 24 — Vision, personas, parcours et contrats d'acceptation

- **Base `main` relue :** `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; **HEAD branche au début :** `fe5e649b54fe94f89d3e15cf765c2d0a30bfe6f9`. La branche était à 4 commits d'avance, 0 de retard par rapport à main avant écriture.
- **Lot produit :** `02_VISION_PARCOURS.md` — vision/non-objectifs, 4 personas, cibles UX/fiabilité mesurables à tester, parcours A 12 escargots → stickers et B boîte carton → Score+Cut, wireframes novice/expert, états, commandes/événements, exemple JSON, frontières modules, pseudo-code de spécification, fallbacks, sécurité, corpus, 14 tests proposés et sources Cricut datées.
- **Annexe :** `OPPORTUNITIES.md` — O-001 journal de transfert (P1), O-002 vérification d'échelle/orientation A4 (P1), O-003 pilotage direct Cricut (REJET) ; liens avec exigences historiques, scores heuristiques, UX, risques et recettes.
- **Tickets proposés :** V34-006 à V34-010 (P0/P1), tous `SPECIFIE` uniquement ; dépendances et DoD documentées. Les 141 exigences héritées restent actives ; la traçabilité V34 exhaustive reste ouverte.
- **Correction focalisée du lot 01 :** `01_BASELINE_AUDIT.md` — `proof_axes.auto: NON_EXECUTE` au lieu de `NON_VERIFIE`, distinction `source_sha` / `tested_code_sha` / `test_run_id`, suppression d'une égalité SHA conceptuellement incorrecte ; aucune modification des roadmaps actives.
- **README V3.4 :** liens vers le nouveau lot et le registre d'opportunités.
- **Vérifications réellement faites :** lecture des fichiers GitHub réels (AGENTS, README, V3.3 MASTER/TRACEABILITY/COVERAGE/HERITAGE/AUDIT, ETAT_ACTUEL, PROGRESS et code G3.3e/transport/UI), issue #72 et PR #73 ; contrôle statique par lecture GitHub : 141 identifiants uniques, V34-006..010 uniques, 14 tests T-V34-02-01..14, 3 opportunités distinctes, correction du vocabulaire de preuve, liens README présents.
- **Sources externes :** documentation officielle Cricut Explore 5 Print Then Cut et Score, zones de découpe (modifiée 19 août 2026), calibration (modifiée 3 septembre 2026), consultées le 29 octobre 2026. Aucune mesure physique ni version locale de Design Space vérifiée.
- **Superpowers : INDISPONIBLE** dans ce runtime (liste des skills vide, lecture des URI refusée) ; auto-revue structurée effectuée, sans prétendre avoir chargé le plugin. **GitHub : OK** lecture et écriture sur branche documentaire.
- **Preuves NON réalisées :** tests unitaires/CI sur le HEAD de la PR, Windows, RTX 3070, Design Space et Cricut physique. La vérification documentaire locale ne vaut pas CI.
- **Risques ouverts :** profil Print Then Cut admissible non mesuré, contrat Score encore conceptuel, besoin d'un graphe d'import réel, absence de CI V3.4, licences IA et contraintes matérielles non qualifiées, différence entre déclaration utilisateur et preuve indépendante.
- **Décision :** DRAFT uniquement ; ne pas fusionner, ne pas modifier main, AGENTS, workflows, archives, code moteur ou automatisations.
- **Prochain micro-lot 03 :** ADR et architecture cible, frontières exactes et schéma minimal `Path→Operation→Tool→Material→Machine`, inventaire des dépendances et comparaison d'options UI par critères/prototype. Ne pas déclarer le lot 03 terminé sans fichier vérifiable.

## Cycle 03 / 24 — Architecture, ADR, contrats et prévol minimal

- **Base main effectivement relue :** `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; **HEAD branche avant le cycle :** `5f82b88ef2d2c79f445bb0a6df6fe4dbcc434040` ; comparaison `main...codex/docs-roadmap-v3-4-campaign` : 10 commits d'avance, 0 de retard avant écriture. Commits du lot : `c62d03b45c0b1810f2ef0fda4dea47aab1098885` (architecture), `d1ae873611e1a4abc9f7a2e9179a51f1b3c50755` (opportunités). Ce journal constitue un commit supplémentaire.
- **Lot produit :** [03_ARCHITECTURE_ADR.md](03_ARCHITECTURE_ADR.md) — quatre ADR proposées : autorité projet unique, contrat de fabrication minimal `geometry→operation→tool→material→machine`, décision de framework différée à des spikes mesurés, IA proposant des changements sans écrire le projet. Schéma logique, JSON de référence validé syntaxiquement, enveloppes commande/événement, concurrence/CAS, idempotence, annulation, sécurité, rollback, deux parcours verticaux et 16 tests **à créer**.
- **Inventaire réel de code relu :** `project_contracts.py`, `project_archive.py`, `project_workspace_g22.py`, `project_recovery.py`, `mask_snapshot_g24.py`, `subject_identity_g33e.py`, `project_routes_g22.py`, `provider_v2112.py`, `auto_masks_v2111.py`, `smartsvg_express_atelier_preview.html`, `engine/__init__.py`. Dépendances directes principales recensées ; graphe exhaustif encore à établir.
- **Contre-expertise du cycle 02 :** clarifié la différence entre export **brouillon** et planche Print Then Cut garantie lorsque région A4 inconnue ; états `preflight` distincts des preuves V3.3 ; Score ≠ Cut et aucun pilotage machine ; limitation actuelle `MAX_MASKS=32` incompatible avec l'hypothèse naïve d'un unique traitement de 50 sujets.
- **Nouveaux tickets proposés :** `V34-011..V34-016` (six IDs uniques, `SPECIFIE`, non implémentés). Tests `T-V34-03-01..16` (16 IDs uniques, **non exécutés**). Opportunités `O-004` (prévisualisation par opération, P1 retenue) et `O-005` (simulation 3D indicative de pliage, P2 reportée) ajoutées au registre sans doubler `O-001..003`.
- **Contrôles réellement exécutés :** relecture GitHub des fichiers du lot ; vérification des 6 IDs tickets, 16 IDs tests, 5 opportunités distinctes, 12 sections et parsing JSON du contrat de fabrication ; contrôle du périmètre de la PR (chemins documentaires). Aucun script de test logiciel ni CI du HEAD n'a été exécuté.
- **Preuves NON obtenues :** tests automatisés de produit, Windows, RTX 3070, Design Space, Cricut physique ; aucun prototype Qt/Tauri ; aucune licence IA qualifiée. La roadmap V3.3 et les archives sont inchangées.
- **Outils :** GitHub **OK** en lecture/écriture sur la branche ; Superpowers **INDISPONIBLE** dans ce runtime (liste des skills vide et lectures URI refusées) ; discipline ADR/alternatives/tests/contre-expertise appliquée sans prétendre avoir chargé les skills. Sources Cricut du lot 02 réutilisées, sans nouvelle certification matérielle.
- **Risques ouverts :** choix UI différé, compatibilité archive `smartsvg-project/1`, journal de commandes persistant à définir, sécurité du transport natif, graphe imports incomplet, CI V3.4 absente, profils machine et zone A4 non qualifiés, mapping bidirectionnel 141 exigences à compléter.
- **Décision :** architecture proposée en DRAFT uniquement ; aucune implémentation, aucune fusion, aucune modification de main/AGENTS/workflows/.automation/automatisations.
- **Prochain lot 04 :** graphe des imports exhaustif, contrats adaptateur natif/ComfyUI, protocole dual-run sur corpus synthétique, séquence de migration, authentification locale, gates de parité et rollback ; contre-expertiser ADR-034-01..04 avant de les figer.

## Cycles 04–24

À renseigner seulement après production et vérification effective des livrables de chaque cycle.