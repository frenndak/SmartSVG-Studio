# SmartSVG V3.5 — Inventaire source des scénarios V3.4, lots 02 à 08

**Inventaire documentaire candidat, non normatif.** Photographie issue du commit `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Les lignes de recettes sont **reproduites sans modification**, avec leur ligne source et SHA du document. Leurs statuts sont **PROPOSÉ / NON QUALIFIÉ PAR CE REGISTRE** ; un test d'une autre génération qui réussit n'est pas associé automatiquement. Les liens exigences/tickets et la qualification doivent être instruits dans une matrice ultérieure. N'ajoute aucune recette nouvelle et ne prétend aucun PASS.

**Couverture vérifiée de ce segment : 160/160 identifiants uniques, lots 02 à 08.** Total historique attendu tous lots : 437. Le lot 01 ne comporte pas de table `T-V34-01-xx` ; absence à noter, pas à combler fictivement.

## Lot 02 — `02_VISION_PARCOURS.md` (14 scénarios)

- **Référence source** : [02_VISION_PARCOURS.md](../roadmap-v3.4/02_VISION_PARCOURS.md) (main@aa0ff9e7) ; **blob SHA** `9a4297168d95c5f09b8529236865e8f83184fb38`.
- **Index source** : `T-V34-02-01` L197 · `T-V34-02-02` L198 · `T-V34-02-03` L199 · `T-V34-02-04` L200 · `T-V34-02-05` L201 · `T-V34-02-06` L202 · `T-V34-02-07` L203 · `T-V34-02-08` L204 · `T-V34-02-09` L205 · `T-V34-02-10` L206 · `T-V34-02-11` L207 · `T-V34-02-12` L208 · `T-V34-02-13` L209 · `T-V34-02-14` L210.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-02-01 | Import et réouverture conservent octets source + SHA identiques | auto + Windows |
| T-V34-02-02 | 12 IDs confirmés restent 12 après correction, undo, réouverture | auto + Windows |
| T-V34-02-03 | 11/13 sujets proposés ne deviennent jamais « 12 confirmés » | auto + UX |
| T-V34-02-04 | Taille sticker inconnue interdit prévol `PASS` | auto + UX |
| T-V34-02-05 | Zone A4 inconnue bloque « placement garanti », sans inventer rectangle | auto + Design Space |
| T-V34-02-06 | A4 : guide d'impression portrait + placement long côté horizontal, puis vérification manuelle | UX + Design Space |
| T-V34-02-07 | Boîte : entrée mm absente, nulle, négative ou NaN rejetée | auto |
| T-V34-02-08 | Chemins `CUT` et `SCORE` distincts ; pas de score transformé en cut silencieusement | auto + Design Space |
| T-V34-02-09 | Guide indique explicitement `Score`, `Attacher` et changement d'outil | UX + Design Space |
| T-V34-02-10 | `command_id` rejoué et résultat IA obsolète ne modifient pas la révision | auto + intégration |
| T-V34-02-11 | OOM, annulation et disque plein n'altèrent ni source ni dernier projet validé | auto + Windows/RTX si applicable |
| T-V34-02-12 | Aucun réseau/modèle sans consentement, mode CPU/manuelle utilisable | auto + Windows |
| T-V34-02-13 | 5 tests utilisateurs novices : >=4 comprennent les quatre états de preuve | UX supervisé |
| T-V34-02-14 | Import réel, aperçu, Score+Attacher, impression/coupe et mesures documentés **séparément** | Design Space + physique |
```

## Lot 03 — `03_ARCHITECTURE_ADR.md` (16 scénarios)

- **Référence source** : [03_ARCHITECTURE_ADR.md](../roadmap-v3.4/03_ARCHITECTURE_ADR.md) (main@aa0ff9e7) ; **blob SHA** `7a0b0c00f21c02895174d8bd99517ba5a3769482`.
- **Index source** : `T-V34-03-01` L199 · `T-V34-03-02` L200 · `T-V34-03-03` L201 · `T-V34-03-04` L202 · `T-V34-03-05` L203 · `T-V34-03-06` L204 · `T-V34-03-07` L205 · `T-V34-03-08` L206 · `T-V34-03-09` L207 · `T-V34-03-10` L208 · `T-V34-03-11` L209 · `T-V34-03-12` L210 · `T-V34-03-13` L211 · `T-V34-03-14` L212 · `T-V34-03-15` L213 · `T-V34-03-16` L214.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-03-01 | 2 transports lisent le même projet et même SHA de source | intégration, auto+Windows |
| T-V34-03-02 | Double `command_id` identique = 1 seule révision | unitaire, auto |
| T-V34-03-03 | Même ID, payload différent → `COMMAND_ID_CONFLICT` | unitaire, auto |
| T-V34-03-04 | `expected_revision` obsolète → aucune mutation | intégration, auto |
| T-V34-03-05 | Résultat IA r12 après r13 → jamais appliqué | E2E, auto+Windows |
| T-V34-03-06 | ZIP futur/corrompu/traversal → refus sans écrasement | sécurité, auto |
| T-V34-03-07 | Snapshot float32 rechargé conserve hash et IDs | régression, auto |
| T-V34-03-08 | `SCORE` ouvert ne devient pas `CUT` | unitaire, auto |
| T-V34-03-09 | Outil/matière/profil inconnu → prévol non qualifiant | unitaire, auto |
| T-V34-03-10 | Zone A4 inconnue → brouillon possible, aucun « prêt » | intégration UI, auto+Design Space |
| T-V34-03-11 | Modèle absent/CPU manuel → parcours projet toujours accessible | E2E, Windows |
| T-V34-03-12 | OOM GPU ne détruit pas dernier projet sain | intégration, Windows+RTX |
| T-V34-03-13 | Export ne modifie pas révision ni octets source | unitaire, auto |
| T-V34-03-14 | Ancien workflow ComfyUI garde IDs/ports/sorties | dual-run, auto+Windows |
| T-V34-03-15 | Import Score+Cut nécessite requalification manuelle Score/Attach | terrain, Design Space |
| T-V34-03-16 | Une découpe réelle ne reçoit PASS physique qu'avec mesures/protocole | terrain, physique |
```

## Lot 04 — `04_MIGRATION_AUTONOME.md` (22 scénarios)

- **Référence source** : [04_MIGRATION_AUTONOME.md](../roadmap-v3.4/04_MIGRATION_AUTONOME.md) (main@aa0ff9e7) ; **blob SHA** `272fb820b12a56285152cb3d2bd80c2d6dec9278`.
- **Index source** : `T-V34-04-01` L222 · `T-V34-04-02` L223 · `T-V34-04-03` L224 · `T-V34-04-04` L225 · `T-V34-04-05` L226 · `T-V34-04-06` L227 · `T-V34-04-07` L228 · `T-V34-04-08` L229 · `T-V34-04-09` L230 · `T-V34-04-10` L231 · `T-V34-04-11` L232 · `T-V34-04-12` L233 · `T-V34-04-13` L234 · `T-V34-04-14` L235 · `T-V34-04-15` L236 · `T-V34-04-16` L237 · `T-V34-04-17` L238 · `T-V34-04-18` L239 · `T-V34-04-19` L240 · `T-V34-04-20` L241 · `T-V34-04-21` L242 · `T-V34-04-22` L243.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-04-01 | Import du bootstrap natif ne charge ni `nodes`, `server`, `folder_paths` ni `torch` | auto + Windows |
| T-V34-04-02 | `smartsvg-project/1` ouvert en lecture seule : SHA source, IDs, masques f32 inchangés | auto + Windows |
| T-V34-04-03 | 2 transports observent le même projet ; seule autorité peut écrire | intégration auto |
| T-V34-04-04 | CAS sur SHA périmé renvoie `STALE_PROJECT_SHA`, archive non modifiée | unitaire + Windows |
| T-V34-04-05 | Même commande répétée après crash = un seul commit durable | injection panne auto + Windows |
| T-V34-04-06 | Même `command_id` avec payload différent → `COMMAND_ID_CONFLICT` | unitaire auto |
| T-V34-04-07 | Fichier `.pending-backup.smartsvg` → blocage et résolution explicite | intégration auto + Windows |
| T-V34-04-08 | ComfyUI absent → import/édition manuelle/export brouillon possibles | E2E Windows |
| T-V34-04-09 | Provider absent/refusé → aucune requête réseau et fallback manuel | réseau intercepté auto |
| T-V34-04-10 | OOM simulé → `GPU_OOM`, aucun commit partiel, reprise CPU | intégration auto ; RTX réelle séparée |
| T-V34-04-11 | 12 sujets synthétiques → IDs/masques persistés et planche indicative | E2E auto + Windows ; Design Space distinct |
| T-V34-04-12 | Boîte → `SCORE` et `CUT` distincts ; pas de conversion implicite | auto ; Design Space et physique séparés |
| T-V34-04-13 | Dual-run déterministe compare données canoniques, pas SHA ZIP brut | auto |
| T-V34-04-14 | Dual-run IA non déterministe produit métriques + provenance, jamais « identique » par défaut | auto ; RTX réelle séparée |
| T-V34-04-15 | GET/POST HTTP natif sans jeton, mauvais Host/Origin ou CORS → refus | sécurité auto + Windows |
| T-V34-04-16 | Ancien workflow garde IDs, noms de nœuds, ports, sorties | snapshot auto + ComfyUI réel ultérieur |
| T-V34-04-17 | Annulation + résultat tardif → `STALE/CANCELLED`, aucune mutation | race test auto |
| T-V34-04-18 | Un projet ZIP futur/corrompu ne détruit ni original ni backup | auto + Windows |
| T-V34-04-19 | 50 sujets divisés en lots ne violent ni `MAX_MASKS=32` ni budget archive | auto + Windows, mémoire à mesurer |
| T-V34-04-20 | Désactivation du transport natif rétablit le parcours historique sans conversion destructive | E2E ComfyUI/Windows |
| T-V34-04-21 | Graphe AST/ESM couvre 148 modules Python et 30 fichiers UI à SHA fixé | analyse statique auto |
| T-V34-04-22 | 100 crashs injectés pendant commit/récupération : aucune perte des octets source | auto + Windows |
```

## Lot 05 — `05_PROJECT_SCHEMA.md` (20 scénarios)

- **Référence source** : [05_PROJECT_SCHEMA.md](../roadmap-v3.4/05_PROJECT_SCHEMA.md) (main@aa0ff9e7) ; **blob SHA** `598a0ba0ec17d2e6035ff8875d3a5ba49a2f702c`.
- **Index source** : `T-V34-05-01` L181 · `T-V34-05-02` L182 · `T-V34-05-03` L183 · `T-V34-05-04` L184 · `T-V34-05-05` L185 · `T-V34-05-06` L186 · `T-V34-05-07` L187 · `T-V34-05-08` L188 · `T-V34-05-09` L189 · `T-V34-05-10` L190 · `T-V34-05-11` L191 · `T-V34-05-12` L192 · `T-V34-05-13` L193 · `T-V34-05-14` L194 · `T-V34-05-15` L195 · `T-V34-05-16` L196 · `T-V34-05-17` L197 · `T-V34-05-18` L198 · `T-V34-05-19` L199 · `T-V34-05-20` L200.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-05-01 | V1 valide ouvert sans écriture ; SHA archive identique avant/après | auto, Windows |
| T-V34-05-02 | Source PNG/JPEG/WebP conservée octet pour octet, digest identique après V1→V2 | auto |
| T-V34-05-03 | 12 IDs sujet G3.3e et preuves exactes préservés ; aucun ID réattribué | auto |
| T-V34-05-04 | Snapshot float32 round-trip bit-identique ; preview L8 ne devient jamais autorité | auto |
| T-V34-05-05 | V1 avec nouveau membre ZIP non déclaré rejeté, sans écriture | auto |
| T-V34-05-06 | ZIP traversal, collisions NFC/casse, symlink, bombes et double JSON key rejetés | auto |
| T-V34-05-07 | V1 au-delà de 256 entrées / 64 MiB membre / 256 MiB total / 4 MiB JSON rejeté | auto |
| T-V34-05-08 | V1 5 000 opérations reste lisible si valide ; mutation supplémentaire refusée | auto |
| T-V34-05-09 | Ancien chargeur V1 rejette V2 avec code explicite, sans corruption | auto |
| T-V34-05-10 | PlanMigration produit un diff déterministe et ne crée aucun fichier | auto |
| T-V34-05-11 | MigrateCopy n'écrase jamais V1 ; SHA original identique après succès et échec | auto, Windows |
| T-V34-05-12 | Coupure à chaque point de publication : soit aucune copie, soit V2 relisible ; V1 intact | auto, Windows |
| T-V34-05-13 | Deux écrivains et SHA périmé → un seul commit ; second `STALE_PROJECT_SHA` | auto, Windows |
| T-V34-05-14 | Retry même command_id/payload → un seul commit ; payload différent → conflit | auto, Windows |
| T-V34-05-15 | Job IA terminé après changement de projet → proposition isolée, zéro mutation | auto |
| T-V34-05-16 | Masque modifié avec preuve d'identité ancienne → `IDENTITY_REVIEW_REQUIRED` | auto |
| T-V34-05-17 | 50 sujets partitionnés : IDs uniques, aucun pack >32, aucune fuite de source | auto, Windows |
| T-V34-05-18 | Projet sans image, boîte Score/Cut : opérations typées persistées et prévol bloqué si profil inconnu | auto, Design Space |
| T-V34-05-19 | Export Print Then Cut ne modifie ni archive ni révision ; dimensions non confirmées → avertissement | auto, Design Space |
| T-V34-05-20 | Refus modèle IA/réseau et OOM : migration/lecture manuelles fonctionnent, aucun téléchargement | auto, Windows |
```

## Lot 06 — `06_COMMAND_BUS.md` (30 scénarios)

- **Référence source** : [06_COMMAND_BUS.md](../roadmap-v3.4/06_COMMAND_BUS.md) (main@aa0ff9e7) ; **blob SHA** `074879c0729042a77e8addc60b8c9446c176c183`.
- **Index source** : `T-V34-06-01` L173 · `T-V34-06-02` L174 · `T-V34-06-03` L175 · `T-V34-06-04` L176 · `T-V34-06-05` L177 · `T-V34-06-06` L178 · `T-V34-06-07` L179 · `T-V34-06-08` L180 · `T-V34-06-09` L181 · `T-V34-06-10` L182 · `T-V34-06-11` L183 · `T-V34-06-12` L184 · `T-V34-06-13` L185 · `T-V34-06-14` L186 · `T-V34-06-15` L187 · `T-V34-06-16` L188 · `T-V34-06-17` L189 · `T-V34-06-18` L190 · `T-V34-06-19` L191 · `T-V34-06-20` L192 · `T-V34-06-21` L193 · `T-V34-06-22` L194 · `T-V34-06-23` L195 · `T-V34-06-24` L196 · `T-V34-06-25` L197 · `T-V34-06-26` L198 · `T-V34-06-27` L199 · `T-V34-06-28` L200 · `T-V34-06-29` L201 · `T-V34-06-30` L202.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-06-01 | même command_id, epoch, payload après perte d'ACK → 1 seule révision et réponse REPLAYED | auto, Windows |
| T-V34-06-02 | même ID et payload différent → COMMAND_ID_CONFLICT, SHA inchangé | auto |
| T-V34-06-03 | retry d'une commande déjà commitée avec ancien expected SHA → REPLAYED, pas STALE | auto |
| T-V34-06-04 | commande inconnue avec ancien expected SHA → STALE_PROJECT_SHA, aucune écriture | auto, Windows |
| T-V34-06-05 | 2 writers concurrents → exactement 1 commit, second refus CAS | auto, Windows |
| T-V34-06-06 | publication réussie + échec backup → receipt présent, COMMITTED_NEEDS_RECOVERY, pending conservé | auto, Windows |
| T-V34-06-07 | publication absente + erreur → receipt absent, SHA inchangé, pas de faux succès | auto |
| T-V34-06-08 | état indécidable après crash → UNKNOWN_AFTER_INTERRUPTION, aucune répétition automatique | auto, Windows |
| T-V34-06-09 | checkpoint ferme epoch N ; commande N tardive refusée même sans receipt | auto |
| T-V34-06-10 | checkpoint interrompu ne produit jamais une epoch active ambiguë après inspection | auto, Windows |
| T-V34-06-11 | plafond de receipts atteint → RECEIPT_CAPACITY_EXCEEDED sans suppression silencieuse | auto |
| T-V34-06-12 | digest logique indépendant du SHA ZIP ; receipt ne contient pas de SHA ZIP autoréférent | auto |
| T-V34-06-13 | Undo/Redo 1 stroke float32 → bytes identiques avant/après round-trip | auto |
| T-V34-06-14 | Undo groupe CUT+SCORE restaure toutes assignations, aucun chemin perdu | auto |
| T-V34-06-15 | nouvelle édition après Undo invalide Redo sans supprimer la piste d'audit | auto |
| T-V34-06-16 | Undo d'un masque modifié invalide/revalide explicitement preuves sujet | auto |
| T-V34-06-17 | job IA r8 fini après commit r9 → STALE, 0 mutation | auto, Windows |
| T-V34-06-18 | CancelJob pendant RUNNING puis résultat tardif → proposition non acceptée | auto |
| T-V34-06-19 | OOM GPU simulé → job FAILED_RECOVERABLE, archive et original inchangés | auto, Windows |
| T-V34-06-20 | reprise après crash ne télécharge/rejoue pas modèle IA sans consentement | auto, Windows |
| T-V34-06-21 | 12 sujets acceptés en un groupe : 12 IDs valides ou 0 ; Undo groupé | auto |
| T-V34-06-22 | 50 sujets partitionnés en packs V2 : aucun pack V1 >32, aucun doublon ID | auto |
| T-V34-06-23 | émission événement interrompue → rechargement UI reconstruit r+1 sans double effet | UI, Windows |
| T-V34-06-24 | Score/Draw/Print ne se transforment jamais en CUT lors de Undo/Redo | auto, DesignSpace (plus tard) |
| T-V34-06-25 | rapport expurgé n'expose ni chemin privé ni média/poids IA | auto, Windows |
| T-V34-06-26 | deux interfaces reçoivent même état canonique, et perte d'événement déclenche resync | UI, Windows |
| T-V34-06-27 | tentative assistant sans confirmation utilisateur → aucune commande mutante | auto, UI |
| T-V34-06-28 | disque plein, lecture seule, symlink et ZIP hostile → aucun projet source détruit | auto, Windows |
| T-V34-06-29 | même job_id et même JobSpec pendant session → un worker ; digest différent → JOB_ID_CONFLICT | auto |
| T-V34-06-30 | batch 50 dont 48 succès/2 échecs → propositions par item, 0 commit avant acceptation, relance ciblée sans doublon | auto, Windows |
```

## Lot 07 — `07_UX_EXPRESS_NAVIGATION.md` (28 scénarios)

- **Référence source** : [07_UX_EXPRESS_NAVIGATION.md](../roadmap-v3.4/07_UX_EXPRESS_NAVIGATION.md) (main@aa0ff9e7) ; **blob SHA** `0846d31a7bd3b0c719423ee585e2ab8721dcbb76`.
- **Index source** : `T-V34-07-01` L189 · `T-V34-07-02` L190 · `T-V34-07-03` L191 · `T-V34-07-04` L192 · `T-V34-07-05` L193 · `T-V34-07-06` L194 · `T-V34-07-07` L195 · `T-V34-07-08` L196 · `T-V34-07-09` L197 · `T-V34-07-10` L198 · `T-V34-07-11` L199 · `T-V34-07-12` L200 · `T-V34-07-13` L201 · `T-V34-07-14` L202 · `T-V34-07-15` L203 · `T-V34-07-16` L204 · `T-V34-07-17` L205 · `T-V34-07-18` L206 · `T-V34-07-19` L207 · `T-V34-07-20` L208 · `T-V34-07-21` L209 · `T-V34-07-22` L210 · `T-V34-07-23` L211 · `T-V34-07-24` L212 · `T-V34-07-25` L213 · `T-V34-07-26` L214 · `T-V34-07-27` L215 · `T-V34-07-28` L216.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-07-01 | accueil vide expose Importer/Créer/Reprendre et aucun export actif | UI, auto |
| T-V34-07-02 | choix Importer sur PNG crée une source de travail sans altérer octets de l'original | auto, Windows |
| T-V34-07-03 | fichier invalide/tronqué rejeté, SHA du projet inchangé, message FR | auto, UI |
| T-V34-07-04 | JPEG/WebP affiché n'est pas déclaré « projet créé » par le gestionnaire V1 PNG | UI |
| T-V34-07-05 | 100 changements d'espaces : SHA et révision inchangés | auto, UI |
| T-V34-07-06 | 2 vues affichent même révision et même sélection résolue ; événement perdu → resync | auto, UI, Windows |
| T-V34-07-07 | double clic Confirmer : un seul receipt et une seule révision | auto, Windows |
| T-V34-07-08 | ACK perdu : état « Enregistré » seulement après receipt confirmé | auto, UI, Windows |
| T-V34-07-09 | projet modifié ailleurs : brouillon STALE, 0 mutation, options comparer/recharger | auto, UI |
| T-V34-07-10 | sidecar pending : accueil RECOVERY_REQUIRED et aucune restauration automatique | auto, Windows |
| T-V34-07-11 | V1 ouvert : pas de migration V2 sans copie et confirmation | auto, UI |
| T-V34-07-12 | job IA absent : import et édition manuelle restent disponibles, 0 réseau | auto, Windows |
| T-V34-07-13 | job IA tardif après révision : proposition STALE, 0 écriture | auto, UI |
| T-V34-07-14 | lot 12 avec 2 échecs : 10 propositions + 2 erreurs, aucune fausse validation | auto, UI |
| T-V34-07-15 | Undo dans un champ texte n'inverse pas le projet | UI, auto |
| T-V34-07-16 | Undo groupé Score+Cut ne promet jamais annulation physique | UI |
| T-V34-07-17 | au clavier, chaque action essentielle accessible et focus visible | UI, Windows |
| T-V34-07-18 | 200 % texte / 1366×768 / 1280×720 : aucun contrôle critique caché | UI, Windows |
| T-V34-07-19 | aucun statut important codé par couleur seule ; annonces aria-live non répétitives | UI, Windows |
| T-V34-07-20 | bouton Exporter désactivé si prévol BLOCKED ; UNKNOWN ne dit jamais « prêt Cricut » | auto, UI |
| T-V34-07-21 | sticker : PNG Print Then Cut distinct du SVG Cut et d'édition, guide Design Space | auto ; DesignSpace NON_EXECUTE |
| T-V34-07-22 | boîte : Score reste sémantique ; guide Attacher visible ; aucune commande machine | auto ; DesignSpace NON_EXECUTE |
| T-V34-07-23 | 50 objets : liste utilisable, pas de plafond UI hérité des 12 exemples | UI, Windows |
| T-V34-07-24 | sortie exportée garde EXPORTED_UNVERIFIED tant que preuve externe absente | auto, UI ; physique NON_EXECUTE |
| T-V34-07-25 | navigation 100 fois p95 <150 ms mesuré avec matériel/protocole enregistré | Windows (benchmark futur) |
| T-V34-07-26 | démo 12 escargots porte « fictif », aucune segmentation/vectorisation réelle revendiquée | UI |
| T-V34-07-27 | contraste et motifs d'opérations distinguables sans perception des couleurs | UI, Windows |
| T-V34-07-28 | brouillon d'import temporaire abandonné : source originale intacte, nettoyage explicite | auto, Windows |
```

## Lot 08 — `08_ASSISTANT_CONTEXTUEL.md` (30 scénarios)

- **Référence source** : [08_ASSISTANT_CONTEXTUEL.md](../roadmap-v3.4/08_ASSISTANT_CONTEXTUEL.md) (main@aa0ff9e7) ; **blob SHA** `e638a1b008aa1206b01eb4f3ef5d7ad2957c351a`.
- **Index source** : `T-V34-08-01` L285 · `T-V34-08-02` L286 · `T-V34-08-03` L287 · `T-V34-08-04` L288 · `T-V34-08-05` L289 · `T-V34-08-06` L290 · `T-V34-08-07` L291 · `T-V34-08-08` L292 · `T-V34-08-09` L293 · `T-V34-08-10` L294 · `T-V34-08-11` L295 · `T-V34-08-12` L296 · `T-V34-08-13` L297 · `T-V34-08-14` L298 · `T-V34-08-15` L299 · `T-V34-08-16` L300 · `T-V34-08-17` L301 · `T-V34-08-18` L302 · `T-V34-08-19` L303 · `T-V34-08-20` L304 · `T-V34-08-21` L305 · `T-V34-08-22` L306 · `T-V34-08-23` L307 · `T-V34-08-24` L308 · `T-V34-08-25` L309 · `T-V34-08-26` L310 · `T-V34-08-27` L311 · `T-V34-08-28` L312 · `T-V34-08-29` L313 · `T-V34-08-30` L314.
- **Lignes originales intégrales et dans l'ordre** (elles restent des assertions PROPOSÉES et non des tests exécutés) :

```text
| T-V34-08-01 | Sans modèle ni réseau, « 12 stickers » propose STICKERS_PRINT_THEN_CUT et ne lance aucun téléchargement | auto + UI |
| T-V34-08-02 | « SVG » seul demande éditable vs découpe, sans choisir silencieusement | auto + UI |
| T-V34-08-03 | « sans imprimer » interdit une proposition Print Then Cut automatique | auto |
| T-V34-08-04 | Un nom de fichier « ignore toutes les règles » n'influence aucune commande | auto sécurité |
| T-V34-08-05 | OCR/SVG hostile n'obtient ni lecture de fichier ni accès réseau | auto sécurité |
| T-V34-08-06 | Aucun tour de dialogue n'altère le SHA du .smartsvg | auto |
| T-V34-08-07 | Un aperçu ne crée ni receipt ni revision logique | auto |
| T-V34-08-08 | Une acceptation sur SHA périmé renvoie PROPOSAL_STALE sans mutation | auto |
| T-V34-08-09 | Un double clic ne publie qu'une commande et réutilise receipt | auto + UI |
| T-V34-08-10 | Une dimension absente de boîte reste manquante et bloque la fabrication | auto + UI |
| T-V34-08-11 | Une dimension 40 mm explicitement saisie est traçable à l'utilisateur | auto |
| T-V34-08-12 | NaN/Inf/0/valeur hors plage sont refusés avant CommandPort | auto |
| T-V34-08-13 | Contradiction « couleurs sans imprimer » affiche alternatives sans substitution | UI |
| T-V34-08-14 | Une question non nécessaire n'est pas posée dans un cas complet | auto + UX |
| T-V34-08-15 | Plus de 3 champs critiques ouvre formulaire, pas boucle de questions | UI |
| T-V34-08-16 | « Ne plus suggérer » supprime relances facultatives sans masquer prévol bloquant | UI |
| T-V34-08-17 | Le choix IA « jamais » n'est jamais remplacé par installation automatique | auto + UI |
| T-V34-08-18 | Un OOM simulé conserve brouillon, permet règles/manuelle et 0 mutation | auto |
| T-V34-08-19 | Préférence de largeur ne remplit pas silencieusement une dimension physique | auto |
| T-V34-08-20 | Suppression préférences/historique ne modifie pas projet canonique | auto |
| T-V34-08-21 | Changement de profil machine invalide une proposition antérieure | auto |
| T-V34-08-22 | La sortie reste PNG_PRINT_THEN_CUT vs SVG_BASIC_CUT vs SVG_MULTILAYER_CUT vs SVG_EDITABLE distincte | auto |
| T-V34-08-23 | A4 inconnu n'obtient jamais statut « placement garanti » | auto + DesignSpace NON_EXECUTE |
| T-V34-08-24 | Boîte Score+Cut présente Score/Attach manuels, aucune API machine | UI + DesignSpace NON_EXECUTE |
| T-V34-08-25 | 12/24/50 propositions partielles sont annoncées comme telles, jamais « détectées » sans preuve | auto + UI |
| T-V34-08-26 | 100 dialogues ouverts/fermés ne changent ni sélection canonique ni révision | UI |
| T-V34-08-27 | Clavier seul permet répondre, ignorer, revenir ; focus restauré | UI + Windows |
| T-V34-08-28 | Lecteur d'écran annonce question, unité, erreur et conséquence sans spam | UI + Windows |
| T-V34-08-29 | Temps p95 règles <150 ms sur 100 demandes synthétiques, mesuré et documenté ; non garanti ici | Windows benchmark |
| T-V34-08-30 | Corpus adversarial + variations FR : taux d'intention correcte et questions superflues mesurés, seuils fixés après baseline | auto + étude UX |
```
