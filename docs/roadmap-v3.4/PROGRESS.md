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

## Cycles 03–24

À renseigner seulement après production et vérification effective des livrables de chaque cycle.