# SmartSVG V3.5 — COV-04 : rapprochement explicite des scénarios V3.4, lots 02 à 04

> **Contre-expertise du 12 novembre 2026, NON NORMATIVE.** Snapshot : `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. **Ce document valide uniquement les références explicites TEST→TICKET dans les documents de conception V3.4.** Il ne certifie ni les critères historiques complets, ni une implémentation, ni des tests exécutés. Les liens TEST→EXIGENCE via tickets sont des **candidats transitifs** à contre-expertiser.

## A. Bilan des 52 recettes d'acceptation

| Source | Scénarios historiques | Avec rattachement TEST→TICKET explicite | Sans rattachement explicite |
|---|---:|---:|---:|
| [Lot 02](../roadmap-v3.4/02_VISION_PARCOURS.md) | 14 | 14 | 0 |
| [Lot 03](../roadmap-v3.4/03_ARCHITECTURE_ADR.md) | 16 | 15 | 1 |
| [Lot 04](../roadmap-v3.4/04_MIGRATION_AUTONOME.md) | 22 | 22 | 0 |
| **TOTAL** | **52** | **51** | **1** |

- **19 fiches de micro-tickets des trois lots inspectées** : V34-006..010, V34-011..016, V34-017..024. La fiche V34-006 est un contrôle documentaire de vision, sans identifiant de scénario `T-V34-02` explicitement désigné : elle n'est pas qualifiée par un scénario simplement parce qu'elle partage le lot.
- Les listes `T-V34-02-01..06`, `T-V34-03-02..05,13`, `T-V34-04-05..07,17,18,22`, `T-V34-02-07..09 et 14` ont été **déployées sans perte** en identifiants individuels et vérifiées contre les 52 lignes sources.
- **51/52** scénarios possèdent au moins un lien ticket explicitement écrit dans une micro-fiche. **Aucun test produit n'a été exécuté** dans cette opération. Les références explicites ne remplacent pas la lecture des véritables critères d'acceptation V3.3.

## B. Erreur de rattachement isolée et réparation proposée

**`T-V34-03-16` — « Une découpe réelle ne reçoit PASS physique qu'avec mesures/protocole »** est une recette historique du lot 03, mais **aucune des six micro-fiches V34-011..016 ne la cite directement** dans ses critères de recette. Ce n'est **PAS** une erreur de code produit prouvée ; c'est une **lacune documentaire locale** à ne pas masquer.

- **Risque** : un audit automatique pourrait conclure que les 16 scénarios du lot 03 sont affectés parce que les 6 tickets y figurent, puis laisser le contrôle d'une découpe réelle sans propriétaire explicite.
- **Correction de conception proposée, NON adoptée** : approfondir V34-012 (contrat fabrication) et V34-003 (preuves) comme propriétaires candidats du gate physique ; garder les recettes du lot 22 (T-V34-22-07/10) séparées et conserver le critère humain/protocole de la V3.3. **Ne pas modifier automatiquement la V3.4 normative.**
- **DoD V3.5** : lien ticket/critère explicite, référence au protocole réel (matière, outil, tapis, dimensions, date, version Design Space), opérateur humain et verdict `UNKNOWN` avant résultat mesuré. Aucun CI « auto PASS » physique.

## C. Matrice auditable : les 52 scénarios et leurs références source

Les textes des tests sont repris de la ligne historique. Les identifiants V34 ci-dessous ont été **extraits exclusivement des micro-tickets de leur lot**, jamais attribués par similarité de titre. `L##` = numéro de ligne du texte historique dans le lot ; `tL##` = ligne de la micro-fiche qui cite le scénario.

| ID original | Assertion historique (abrégée à la cellule, voir source) | Axe prévu | Références tickets explicites | Lignes source | Statut de traçabilité |
|---|---|---|---|---|---|
| `T-V34-02-01` | Import et réouverture conservent octets source + SHA identiques | auto + Windows | `V34-007` (tL219) | 02_VISION_PARCOURS.md L197 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-02` | 12 IDs confirmés restent 12 après correction, undo, réouverture | auto + Windows | `V34-007` (tL219) | 02_VISION_PARCOURS.md L198 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-03` | 11/13 sujets proposés ne deviennent jamais « 12 confirmés » | auto + UX | `V34-007` (tL219), `V34-009` (tL221) | 02_VISION_PARCOURS.md L199 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-04` | Taille sticker inconnue interdit prévol `PASS` | auto + UX | `V34-007` (tL219), `V34-009` (tL221) | 02_VISION_PARCOURS.md L200 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-05` | Zone A4 inconnue bloque « placement garanti », sans inventer rectangle | auto + Design Space | `V34-007` (tL219), `V34-009` (tL221) | 02_VISION_PARCOURS.md L201 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-06` | A4 : guide d'impression portrait + placement long côté horizontal, puis vérification manuelle | UX + Design Space | `V34-007` (tL219) | 02_VISION_PARCOURS.md L202 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-07` | Boîte : entrée mm absente, nulle, négative ou NaN rejetée | auto | `V34-008` (tL220) | 02_VISION_PARCOURS.md L203 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-08` | Chemins `CUT` et `SCORE` distincts ; pas de score transformé en cut silencieusement | auto + Design Space | `V34-008` (tL220) | 02_VISION_PARCOURS.md L204 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-09` | Guide indique explicitement `Score`, `Attacher` et changement d'outil | UX + Design Space | `V34-008` (tL220) | 02_VISION_PARCOURS.md L205 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-10` | `command_id` rejoué et résultat IA obsolète ne modifient pas la révision | auto + intégration | `V34-010` (tL222) | 02_VISION_PARCOURS.md L206 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-11` | OOM, annulation et disque plein n'altèrent ni source ni dernier projet validé | auto + Windows/RTX si applicable | `V34-010` (tL222) | 02_VISION_PARCOURS.md L207 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-12` | Aucun réseau/modèle sans consentement, mode CPU/manuelle utilisable | auto + Windows | `V34-010` (tL222) | 02_VISION_PARCOURS.md L208 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-13` | 5 tests utilisateurs novices : >=4 comprennent les quatre états de preuve | UX supervisé | `V34-009` (tL221) | 02_VISION_PARCOURS.md L209 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-02-14` | Import réel, aperçu, Score+Attacher, impression/coupe et mesures documentés **séparément** | Design Space + physique | `V34-008` (tL220) | 02_VISION_PARCOURS.md L210 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-01` | 2 transports lisent le même projet et même SHA de source | intégration, auto+Windows | `V34-011` (tL222), `V34-014` (tL225) | 03_ARCHITECTURE_ADR.md L199 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-02` | Double `command_id` identique = 1 seule révision | unitaire, auto | `V34-011` (tL222), `V34-013` (tL224) | 03_ARCHITECTURE_ADR.md L200 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-03` | Même ID, payload différent → `COMMAND_ID_CONFLICT` | unitaire, auto | `V34-013` (tL224) | 03_ARCHITECTURE_ADR.md L201 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-04` | `expected_revision` obsolète → aucune mutation | intégration, auto | `V34-011` (tL222), `V34-013` (tL224) | 03_ARCHITECTURE_ADR.md L202 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-05` | Résultat IA r12 après r13 → jamais appliqué | E2E, auto+Windows | `V34-013` (tL224), `V34-015` (tL226), `V34-016` (tL227) | 03_ARCHITECTURE_ADR.md L203 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-06` | ZIP futur/corrompu/traversal → refus sans écrasement | sécurité, auto | `V34-014` (tL225) | 03_ARCHITECTURE_ADR.md L204 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-07` | Snapshot float32 rechargé conserve hash et IDs | régression, auto | `V34-011` (tL222) | 03_ARCHITECTURE_ADR.md L205 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-08` | `SCORE` ouvert ne devient pas `CUT` | unitaire, auto | `V34-012` (tL223) | 03_ARCHITECTURE_ADR.md L206 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-09` | Outil/matière/profil inconnu → prévol non qualifiant | unitaire, auto | `V34-012` (tL223) | 03_ARCHITECTURE_ADR.md L207 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-10` | Zone A4 inconnue → brouillon possible, aucun « prêt » | intégration UI, auto+Design Space | `V34-015` (tL226) | 03_ARCHITECTURE_ADR.md L208 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-11` | Modèle absent/CPU manuel → parcours projet toujours accessible | E2E, Windows | `V34-015` (tL226), `V34-016` (tL227) | 03_ARCHITECTURE_ADR.md L209 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-12` | OOM GPU ne détruit pas dernier projet sain | intégration, Windows+RTX | `V34-016` (tL227) | 03_ARCHITECTURE_ADR.md L210 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-13` | Export ne modifie pas révision ni octets source | unitaire, auto | `V34-013` (tL224) | 03_ARCHITECTURE_ADR.md L211 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-14` | Ancien workflow ComfyUI garde IDs/ports/sorties | dual-run, auto+Windows | `V34-014` (tL225) | 03_ARCHITECTURE_ADR.md L212 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-15` | Import Score+Cut nécessite requalification manuelle Score/Attach | terrain, Design Space | `V34-012` (tL223) | 03_ARCHITECTURE_ADR.md L213 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-03-16` | Une découpe réelle ne reçoit PASS physique qu'avec mesures/protocole | terrain, physique | **NON ATTRIBUÉ EXPLICITEMENT** | 03_ARCHITECTURE_ADR.md L214 | GAP_PROPRIÉTAIRE_TEST |
| `T-V34-04-01` | Import du bootstrap natif ne charge ni `nodes`, `server`, `folder_paths` ni `torch` | auto + Windows | `V34-017` (tL251), `V34-019` (tL253) | 04_MIGRATION_AUTONOME.md L222 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-02` | `smartsvg-project/1` ouvert en lecture seule : SHA source, IDs, masques f32 inchangés | auto + Windows | `V34-018` (tL252) | 04_MIGRATION_AUTONOME.md L223 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-03` | 2 transports observent le même projet ; seule autorité peut écrire | intégration auto | `V34-018` (tL252), `V34-020` (tL254) | 04_MIGRATION_AUTONOME.md L224 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-04` | CAS sur SHA périmé renvoie `STALE_PROJECT_SHA`, archive non modifiée | unitaire + Windows | `V34-018` (tL252) | 04_MIGRATION_AUTONOME.md L225 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-05` | Même commande répétée après crash = un seul commit durable | injection panne auto + Windows | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L226 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-06` | Même `command_id` avec payload différent → `COMMAND_ID_CONFLICT` | unitaire auto | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L227 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-07` | Fichier `.pending-backup.smartsvg` → blocage et résolution explicite | intégration auto + Windows | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L228 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-08` | ComfyUI absent → import/édition manuelle/export brouillon possibles | E2E Windows | `V34-019` (tL253), `V34-024` (tL258) | 04_MIGRATION_AUTONOME.md L229 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-09` | Provider absent/refusé → aucune requête réseau et fallback manuel | réseau intercepté auto | `V34-023` (tL257) | 04_MIGRATION_AUTONOME.md L230 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-10` | OOM simulé → `GPU_OOM`, aucun commit partiel, reprise CPU | intégration auto ; RTX réelle séparée | `V34-023` (tL257) | 04_MIGRATION_AUTONOME.md L231 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-11` | 12 sujets synthétiques → IDs/masques persistés et planche indicative | E2E auto + Windows ; Design Space distinct | `V34-021` (tL255) | 04_MIGRATION_AUTONOME.md L232 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-12` | Boîte → `SCORE` et `CUT` distincts ; pas de conversion implicite | auto ; Design Space et physique séparés | `V34-021` (tL255) | 04_MIGRATION_AUTONOME.md L233 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-13` | Dual-run déterministe compare données canoniques, pas SHA ZIP brut | auto | `V34-021` (tL255) | 04_MIGRATION_AUTONOME.md L234 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-14` | Dual-run IA non déterministe produit métriques + provenance, jamais « identique » par défaut | auto ; RTX réelle séparée | `V34-021` (tL255) | 04_MIGRATION_AUTONOME.md L235 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-15` | GET/POST HTTP natif sans jeton, mauvais Host/Origin ou CORS → refus | sécurité auto + Windows | `V34-019` (tL253), `V34-023` (tL257) | 04_MIGRATION_AUTONOME.md L236 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-16` | Ancien workflow garde IDs, noms de nœuds, ports, sorties | snapshot auto + ComfyUI réel ultérieur | `V34-020` (tL254) | 04_MIGRATION_AUTONOME.md L237 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-17` | Annulation + résultat tardif → `STALE/CANCELLED`, aucune mutation | race test auto | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L238 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-18` | Un projet ZIP futur/corrompu ne détruit ni original ni backup | auto + Windows | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L239 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-19` | 50 sujets divisés en lots ne violent ni `MAX_MASKS=32` ni budget archive | auto + Windows, mémoire à mesurer | `V34-024` (tL258) | 04_MIGRATION_AUTONOME.md L240 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-20` | Désactivation du transport natif rétablit le parcours historique sans conversion destructive | E2E ComfyUI/Windows | `V34-020` (tL254), `V34-024` (tL258) | 04_MIGRATION_AUTONOME.md L241 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-21` | Graphe AST/ESM couvre 148 modules Python et 30 fichiers UI à SHA fixé | analyse statique auto | `V34-017` (tL251) | 04_MIGRATION_AUTONOME.md L242 | LIEN_EXPLICITE_DE_PLANIFICATION |
| `T-V34-04-22` | 100 crashs injectés pendant commit/récupération : aucune perte des octets source | auto + Windows | `V34-022` (tL256) | 04_MIGRATION_AUTONOME.md L243 | LIEN_EXPLICITE_DE_PLANIFICATION |

## D. Axes de preuve indépendants et contre-expertise

1. **Risque dual-run** : `T-V34-04-13/14` distinguent sortie déterministe canonique et IA non déterministe ; ne jamais comparer les SHA ZIP bruts ni réclamer une identité de pixels à l'IA sans protocole.
2. **Risque Windows et reprise** : `T-V34-04-05/07/22` demandent idempotence de la commande, restauration par CAS et jusqu'à 100 injections de panne — **objectifs de test futurs**, aucune validation ici.
3. **Risque fabrication** : `T-V34-02-14`, `03-15/16` et `04-12` imposent distinction prototype/Design Space/coupe physique. Un test unitaire XML/SVG ou une prévisualisation ne vérifie pas le geste réel sur la machine.
4. **Risque IA et confidentialité** : `T-V34-02-12`, `03-11/12`, `04-09/10/15` gardent les chemins réseau, le consentement et la repli CPU séparés de l'UI.
5. **Contradiction à éviter** : les mentions `auto+Windows` sont des **types de preuves attendues** dans la conception, pas la preuve qu'un test passe sous Windows aujourd'hui.

## E. Étapes suivantes et garde-fous

- **COV-05** : poursuivre les scénarios des lots 05–08 ; extraire les liens explicitement présents dans les micro-fiches (qui peuvent employer des formats différents), signaler les non-rattachés, ne pas déduire l'exactitude à partir du numéro de lot.
- **COV-06** : lire chaque exigence V3.3 originelle liée aux tickets concernés et qualifier les **arêtes sémantiques** ; ne pas traiter les 51 liens de planification comme 51 preuves de conformité.
- **G6/G9** : garder visibles les [10 obligations sans ticket V34](COVERAGE_V34_TO_V35.md#2-les-10-exigences-v33-encore-sans-ticket-v34--reprise-prioritaire-et-choix-v35), dont typographie, gabarits, OCR et dioramas. Aucune proposition Smart Delivery ou P2 ne les annule.
- **Conception générale** : poursuivre Smart Delivery, Smart Cut Advisor, Weeding, Print Then Cut, IA/UX, bibliothèque et Windows selon [#142](https://github.com/frenndak/SmartSVG-Studio/issues/142), sans créer une seconde infrastructure de tests/roadmap.

**Qualification de ce lot :** liens `TEST→TICKET` **51/52 établis par texte source**, 1 lacune documentée ; liens `TEST→EXIGENCE` à qualifier ; `TESTS_EXECUTÉS=0`. La V3.4 reste ACTIVE ; aucune PR, merge ni modification de code.
