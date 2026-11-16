# SmartSVG V3.5 — COV-18E-1 : bibliothèque et Atelier (E01–E05)

**13 novembre 2026 — CANDIDATE, NON NORMATIVE.** Première tranche E issue de #134/COV17E, confrontée à V3.3 et lots 05/18/20/21 de V3.4. Aucune fonction déclarée livrée par ce texte. Snapshot code main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935.

## 1. Décisions par fonctionnalité

| UX | Critères historiques et références | Contre-expertise et DoD candidat |
|---|---|---|
| **E01 — Bibliothèque/miniatures/favoris/recherche** | **S-041 P1/G7.2** recherche/duplication/archivage fiables, dépend S-024 ; **S-091 P1** miniatures/filtres retrouver projet en test utilisateur ; **R33-010** index reconstructible ; lot 20 V34-136 | **RACCORDER P1** : index simple projection du projet V1. Une recherche par nom dans Workspace ne prouve pas filtres/miniatures ; reconstruire l'index sans détruire archive ni cacher projets corrompus. |
| **E02 — Collections/tags/modèles/duplication** | S-041 et S-091 ; **S-097 P2** refaire sur sélection, **S-098 P2** recettes/gabarits portables droits visibles ; V34-136/137 | **ÉTENDRE P1** : catégories et tags dérivés sans altérer l'autorité, duplication sous nouvel ID CAS/receipt. Droits/licences et provenance sur tout modèle exportable. Un lien de catalogue ne doit pas créer une deuxième copie cachée. |
| **E03 — Variantes/historique visuel** | **S-026 P0** Undo/redo/reload conforme, **S-053 P0** crash/reopen, V34-029 et V34-137, S-041 | **AMÉLIORER P1** : distinguer historique transactionnel d'un projet, clone et variantes comparables, avec sha source/parent. Undo n'annule pas un ZIP déjà livré. Corriger ou revenir à l'ancien projet sans corruption de la lignée. |
| **E04 — Atelier hybride raster/vecteur/objets** | **S-025 P0** sticker simple sans graphe, **S-035 P1** composition objets/textes éditable après réouverture, **S-070 P0** 12 sujets mêmes IDs ; V34-132/133 | **GARDER P0 UX** : canevas unique et états cohérents, mais le panneau Tk actuel ne prouve pas calques/texte/Bézier persistants. Outils non pris en charge restent désactivés/annoncés, V1 strict conservé. |
| **E05 — Zoom/pan/poignées/aimants/overlays** | **S-068 P0** 1366×768 et 1920×1080, pas d'action cachée ; **S-070 P0** vignettes ↔ sujets ; **S-086 P1** poignées/mesures mm (G6.6) | **GARDER P0 UX** : zoom/fit/pan déjà partiellement gérés par native_image_viewport_v34 ; poignées et guides restent à vérifier. Séparer coordonnées de canevas, px image et mm matière avec transformations inverses testées. |

## 2. Autorité, réemploi et états

**Ports inspectés lors du premier audit** : standalone_desktop_v34.py, native_app_shell_v34.py, native_image_viewport_v34.py, native_atelier_tk_v34.py, project_recovery.py, project_archive.py. Ce sont des preuves de composants disponibles dans le dépôt, pas une UX hybride ni un installateur complet. S-041/091 et R33-010 imposent **bibliothèque reconstructible** depuis les archives .smartsvg ; un cache de miniatures ne peut pas devenir le fichier maître.

**Machine d'état candidate** : `ProjectIndexSnapshot{archive_sha,project_id,display_metadata,thumbnail_sha,status}` (projection), `DraftSelection{source_revision,subject_id,coordinate_frame,transforms}` (non mutant), `VariantRef{parent_sha,derived_sha,created_from_receipt,license_notes}` (external). Ces noms ne désignent pas des APIs déjà codées. Les nouvelles données objet/texte nécessitent ADR/migration testée avant persistance ; pas de second store de projet.

**Novice** : bibliothèque → ouvrir projet → sélectionner par vignette ou canevas → retoucher et Undo → sauvegarder → retrouver version ; aucune magie d'import ou d'export. **Expert** : inspecter SHA/provenance, conflits CAS, types d'artefacts distincts et miniatures liées au bon document ; calques de vue sans mutation persistante.

## 3. Tests négatifs et qualification (TOUT NOT_RUN)

- Un index bibliothèque corrompu ou effacé → reconstruire les métadonnées sans modifier les projets ; les projets corrompus restent signalés individuellement.
- Une miniature pointe vers une ancienne révision → prévenir/rafraîchir, jamais modifier le projet ni montrer un autre sujet comme identique.
- Duplication ou renommage concurrrent → nouveau project_id unique, les octets de l'original et SHA restent intacts ; pas de collision Windows ou lien hors bibliothèque.
- Vue Atelier ouverte avec 12 sujets et ordre des vignettes inversé → clic conserve subject_id, pas une sélection sur index DOM périmé.
- Zoom DPI 200 % ou pan pendant déplacement → coordonnées monde conservées ; NaN/zoom zéro/reflet invalide rejetés, sans mouvement de géométrie.
- Calque/texte non pris en charge → avertissement et preview seulement ; ne pas ajouter de champ inconnu dans editor_v216.
- Panne disque, CAS périmé, crash/backup pending → récupération de la dernière révision saine, aucun succès annoncé.
- Tests UI sur Windows 1366×768 + 1920×1080, clavier/focus/motion réduit, temps de réponse et RAM mesurés. **Aucune mesure réellement produite par cette fiche.**

Les univers historiques 24/141/140/80/437 et 25 contrôles de qualité restent applicables. **État : E01–E05 cinq décisions auditées, zéro certification prête à coder, zéro test produit.** Prochaine étape COV-18E-2 : E06–E10 comparaisons, barre contextuelle, modes et accessibilité.
