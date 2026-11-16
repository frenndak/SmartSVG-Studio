# SmartSVG V3.5 — COV-18E-3 : Undo, sauvegarde, caches, diagnostics et QA (E11–E15)

**13 novembre 2026 — CANDIDATE, NON NORMATIVE.** Troisième tranche E issue de UX #134/COV17E. Les exigences historiques S-024/S-026/S-053/S-074/S-095/S-096 et R33-013/R33-025 restent intactes. La V3.4 ACTIVE garde l'autorité. Tests produits, Windows, GPU et Design Space = NOT_RUN dans ce document.

## 1. Contrôle individuel des responsabilités

| UX | Contrat hérité précis | Contre-expertise et décision |
|---|---|---|
| **E11 — Undo/Redo, brouillons et transactions** | **S-026 P0** historique UI « Undo/redo/reload conformes », S-080 pinceau corrigé/sauvegardé sans incohérence ; V34-029/033/133 | **AMÉLIORER P0** : Undo du brouillon avant CAS, journal durable après commit, répéter une action idempotente avec receipt et sans double application ; Undo ne supprime pas un export déjà livré. Un bouton undo en lecture seule ne prouve pas rétablissement raster + objets + projet. |
| **E12 — Intégrité projet V1 et recovery** | **S-024 P0** « chargement exact masques, sources et actions » ; **S-053 P0** crash/reopen/malveillance testés ; **S-095 P0** zéro perte de source/correction validée ; **R33-013** gestion disque plein/lecture seule | **GARDER P0** : une seule autorité archive .smartsvg et writer/CAS, sauvegarde atomique, vérifier ZIP contenu/hash, préserver backup sain et guider récupération après crash, sans écraser silencieusement. |
| **E13 — Previews async, cache et résultats périmés** | **S-074 P0** réouverture contexte identique, **S-096 P1** instrumentation latence/erreur locale ; R33-025 pannes export/IA | **AMÉLIORER P0** : cache borné par source_SHA/projet/subject_id/expected_revision ; job `STALE` ignoré avant UI, et toute file VRAM/RAM reste sous budget. Un LatestOnlyJob local n'est pas une politique globale de persistance/cache. |
| **E14 — Erreurs exploitables et réparations** | **S-071 P0** erreurs cliquables avec région/correction réversible (masque rectangle refusé ou reprise explicite) ; **S-084 P1** ouvrir dossier/export/rapport depuis réussite réelle | **AMÉLIORER P0** : code erreur, localisation objet/chemin, cause et action vraiment disponible ; ne pas proposer un bouton « réparer » sans remède implémenté. Exclure chemins privés/EXIF du rapport partageable. |
| **E15 — QA raster/alpha/couleur/résolution** | **S-073 P0** vues originales/masque/coupe non confondues, **S-016 P1** avant/après objectif, **S-054 P0** sidecar preuves orthogonales ; V34-090/091/095 | **RACCORDER P0** : tests de color profile/ICC, halo RGB et alpha, ppi/mm, et qualité de bord sur fixtures ; séparer `QA_LOCAL` de `DESIGN_SPACE_PASS` et `PHYSICAL_PASS`. Un dérivé PNG HD n'a pas gagné de détails natifs. |

## 2. Architecture minimaliste, UX novice/expert et micro-lots

**Réemploi** : project_archive.save/load, project_recovery.save_with_recovery, project_workspace_g22.save_editor_document, editor_session_g23, native_notes_tk_v34, standalone_desktop_v34, LatestOnlyJob et artifact_qa. Leurs fonctions sont référencées comme **ports existants à qualifier**, et non comme preuve que tout le parcours marche sous Windows. Aucune seconde base de données métier, aucun nouveau writer et aucune migration de schéma imposée.

**DraftMutation (conception)** : expected_project_sha, command_id, target_subject_id, preview_digest, safe_abort; **RecoveryRecord** : last_valid_project_sha, pending_write, verified_backup, user_action; **QAReport** : artifact_role, checks, local_status, provenance, external_status=UNKNOWN. Les rapports de QA ne doivent jamais changer les artefacts.

**Novice** : corriger le masque → comparer → Undo/Redo → enregistrer → si panne, rouvrir la version vérifiée avec message français indiquant ce qui n'a pas été sauvegardé. **Expert** : SHA/CAS, journal de receipts, comparaison source/preview, logs expurgés et diagnostics par région/chemin.

## 3. Recettes positives et adversariales à exécuter (NOT_RUN)

1. Deux pinceaux sur sujets distincts, Undo et Redo, crash/reload ; aucune opération sur mauvais subject_id.
2. Reprise d'un projet où le backup est pending et le primaire intact ; aucune restauration forcée, ancien SHA conservé.
3. Disk full au flush, antivirus lock du fichier Windows, read-only target → FAIL et source précédente lisible, pas de succès fantôme.
4. Résultat async d'un projet A après ouverture du B → rejet STALE, aucun aperçu ni QA de A sur B.
5. Cache avec 50 miniatures et budget mémoire dépassé → éviction contrôlée, jamais auto-acceptation d'un masque tronqué.
6. HTML SVG/ZIP hostile et EXIF privé → aucun parseur externe sans contrôle, sortie rapport sans fuite.
7. PNG avec alpha semi-transparent mais halo RGB opaque → rapport qualité local identifiant les bords, sans faux score matériel.
8. Aperçu de 300→600 ppi après interpolation CPU → même digest Cut, étiquette « interpolation », pas « 600ppi de détail natif ».
9. Windows 1366×768/DPI200/lecteur d'écran/raccourcis : tests de focus, position messages et récupération. Aucun test dans cette fiche.

**Performance** : mesurer p50/p95 et RAM sur le matériel réel avant de fixer seuil. Chaque transaction garde source/masques float32/Artifact.use V1, quatre exports métier distincts, aucune validation physique issue de CI. Conformité aux 25 axes de vérification V3.5.

**État** : E11–E15 revus, zéro certifié ; travail produit et PR code non modifiés. **Prochaine étape COV-18E-4** : E16–E20 SVG/coupe, installation Windows, confidentialité et aide, puis contre-expertise croisée et opportunités.
