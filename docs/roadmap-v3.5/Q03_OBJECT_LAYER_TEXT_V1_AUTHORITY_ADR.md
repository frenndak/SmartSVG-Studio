# V35-Q03 — ADR objets, calques, texte et transformations : autorité V1 et projections

**14 novembre 2026 · CANDIDAT / SPECIFIÉ partiellement · NON NORMATIF.** Décision proposée : **RACCORDER** les interactions aux identités, au writer et au CAS V1 ; **REPORTER** tout changement de schéma jusqu'à ADR de migration et approbation propriétaire. Aucune promesse d'implémentation Windows.

## 1. Preuves consultées et limites

Ports lus sur `main` par GitHub Contents : `project_archive.py` blob `141d825a`, `project_workspace_g22.py` blob `13b8e40d`, `editor_session_g23.py` blob `dda85369`, `subject_identity_g33e.py` blob `2d799a34`. Document V3.4 lot 06 `06_COMMAND_BUS.md` blob `074879c0`, Q02 et contrat 25 axes. Les blobs ne prouvent **pas** le HEAD courant ni le branchement UI. Les signatures de l'ensemble des consommateurs et les critères originaux G6/G9 restent à rapprocher ; ne pas marquer certifié. PR #144 Undo/Redo ouverte lors de la consultation, ne pas déduire fusion.

**Observations vérifiables :** `LoadedProject` contient `document: dict`, `operations: list`, ressources, sources, masques, sujets, artefacts et QA ; `SCHEMA_VERSION='smartsvg-project/1'`. `ManagedWorkspace` expose `save_editor_document`, `register_subject_identity`, `save_subject_brush`, `change_subject_brush_history`, `preview_subject_brush_readonly`. `parse_editor_document` n'admet que `version,width,height,count,source,strokes` et des strokes `object,mode,radius,points` ; **un stroke n'est ni un TextNode, ni un calque, ni un objet SVG**. `subject_identity_g33e` relie Subject au masque float32 exact, pas à un nom de calque libre. Le lot 06 décrit un bus générique V2 **proposé**, non une API V1 existante.

## 2. ADR de responsabilité, alternatives et refus

| Responsabilité | Autorité réellement identifiée | Contrat V3.5 candidat | Alternative refusée / condition |
|---|---|---|---|
| Source et masque | `LoadedProject.sources/masks`, snapshot float32, identité Subject | conserver octets, SHA, ordre et provenance ; sélection UI n'altère jamais le masque | utiliser indice de stroke comme identité objet : REJETER |
| Objet de canevas | Subject existant seulement si lié à masque | `CanvasObjectView` éphémère : `subject_id`, `source_revision_sha256`, géométrie de vue et état sélection ; aucun champ persistant supposé | inventer `objects[]` V1 sans preuve : REJETER |
| Calque | aucune autorité générale de calques certifiée dans les ports lus | `LayerProjection` dérivée des sujets/artefacts reconnus, tri visuel temporaire ; sauvegarde durable bloquée jusqu'à contrat | SQLite ou store UI deuxième vérité : REJETER |
| Transformation | aucune API persistante générique vérifiée | `TransformPreview` hors archive, coordonnées `px` source et `mm` sortie distinctes, matrice affine finie ; commit seulement via writer validé | écriture libre `document` ou `operations` : REJETER |
| Texte éditable / OCR | pas de TextNode dans le parseur de strokes | `TextDraft` local : Unicode NFC, contenu, famille/style/licence, glyphes manquants, provenance OCR, géométrie et statut ; édition persistante **NON DISPONIBLE** sans ADR | conversion en chemins prétendue éditable : REJETER |
| Sorties | `Artifact` V1 et exports par rôle à qualifier | PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG éditable sont **quatre rôles**, avec QA propre ; un artefact n'est pas le document source | SVG générique renommé CUT : REJETER |
| Undo | historique pinceau existant, bus général V2 proposé | Undo local des drafts ; Undo persistant uniquement si commande/writer existant et CAS confirmé | Undo d'export ou de coupe physique : REJETER |

**Décision de migration :** ne jamais sérialiser des calques/objets/texte dans `strokes` ou modifier `smartsvg-project/1` implicitement. Si la persistance V1 ne sait pas représenter l'opération, offrir un aperçu/une sortie explicite **sans** prétendre que le projet la rééditera, ou bloquer la fonction ; proposer une ADR de migration V2 séparée avec compatibilité, backup, rollback et validation propriétaire. Aucune mutation du schéma ici.

## 3. Contrats de données candidats — non APIs existantes

`CanvasObjectView {subject_id: string, project_sha256: hex64, source_width_px: int, source_height_px: int, selected: bool, transform_preview: Affine2D|null}`. `Affine2D {a,b,c,d,e,f: finite float, coordinate_space: 'SOURCE_PX', version:1}` ; multiplication/ordre et origine à fixer par test de roundtrip, pas d'interprétation automatique en mm. `LayerProjection {projection_id: ephemeral, source_subject_ids: string[], visibility: bool, order: int, revision_sha256: hex64}`. `TextDraft {draft_id: ephemeral, text_nfc: string, font_family: string, font_license: 'VERIFIED'|'UNKNOWN'|'RESTRICTED', missing_glyphs: string[], source: 'USER'|'OCR_PROPOSAL', project_sha256: hex64}`. **Aucun de ces types n'est une entrée acceptée par le writer actuel.**

Erreurs proposées : `STALE_PROJECT_SHA`, `UNKNOWN_SUBJECT`, `UNSUPPORTED_PERSISTENT_EDIT`, `MISSING_GLYPH`, `FONT_LICENSE_UNKNOWN`, `INVALID_AFFINE`, `CANCELLED`, `RECOVERY_REQUIRED`. Adapter aux erreurs effectivement exposées avant développement, sans créer de second protocole.

États : `EMPTY → SELECTED → PREVIEW → COMMIT_REQUESTED → COMMITTED` si port compatible ; sinon `PREVIEW → EXPORT_ONLY|BLOCKED`. `STALE`, `CANCELLED` et `RECOVERY_REQUIRED` n'écrivent pas. Relecture de SHA avant commit, verrou/writer unique ; résultat async ancien rejeté. Une opération Undo ne promet jamais de retirer une sortie externe.

## 4. UX novice/expert et accessibilité

Novice : ouvrir projet → cliquer sujet → poignée et aperçu non mutant → corriger / annuler → enregistrer seulement si capacité persistante réelle, sinon message « aperçu non enregistrable dans ce format » et choix de sortie externe. Expert : inspecter identité Subject, empreinte source, dimensions px/mm, avertissement de topologie, licence de police, statut de capacité et provenance. Barre contextuelle unique (pas un bouton par Smart X) ; tab/focus et raccourcis documentés, Undo disponible seulement quand réellement applicable ; tester 1366×768 et DPI 200 %, contraste, clavier, réduction de mouvement, états vide/pending/erreur. Une preview typographique n'implique ni OCR fiable ni conversion police→chemins. Aucun réseau ou téléchargement IA implicite ; fallback saisie manuelle.

## 5. Protocole TDD et contre-exemples (tous NOT_RUN)

Positifs : P1 sélection Subject stable après save/reopen ; P2 transformation preview affine inverse et dimensions source inchangées ; P3 texte accentué avec glyphes/licence connus rendu et avertissements vérifiables ; P4 quatre exports identifiés et QA indépendantes **seulement si exporteurs réels disponibles**.

Négatifs : N1 indice de stroke réordonné ≠ identité Subject : rejet de liaison ; N2 changement SHA pendant drag → `STALE`, aucune écriture ; N3 police absente/licence UNKNOWN → pas de substitution silencieuse ; N4 transformation NaN/infini ou mm/px confondus → rejet ; N5 tentative TextNode dans `strokes` → rejet du parseur ; N6 crash avant commit → archive intacte ; N7 crash après publication avant accusé → inspection recovery avant retry, pas double mutation ; N8 Undo après ZIP/découpe → seulement projet local, aucune prétention physique ; N9 deux fenêtres éditent le même SHA → second commit refusé CAS ; N10 OCR sans consentement / résultat tardif → pas de mutation.

Micro-lots futurs : (a) tests de contrat et inventaire consommateurs, (b) projections read-only, (c) preview/Undo éphémère, (d) ADR persistance et autorisation si indispensable, (e) implémentation via writer existant seulement après gate, (f) Windows UI, (g) Design Space et coupe physique séparés. Performance : mesurer latence interaction p50/p95 et mémoire sur corpus fixé, machine/DPI consignés ; aucun chiffre observé. Fixtures synthétiques sans polices redistribuées ni données privées.

## 6. Revue hostile et contrôle 25 axes

**Objection principale :** une projection éphémère ne répond pas au JTBD « réouvrir et modifier un texte ». **Réponse :** c'est une lacune explicite à arbitrer, non une fonction certifiée ; le format V1 est préservé jusqu'à preuve d'un port autorisé ou migration propriétaire. **Objection 2 :** un SVG éditable peut contenir des chemins mais perdre la sémantique du texte. **Réponse :** qualifier séparément « éditable en chemins » et « texte rééditable ». **Objection 3 :** PR #144 peut fournir un Undo plus large ; à vérifier après fusion et test Windows, sans le présumer.

Contrôles : 01–05 inventaires historiques inchangés, rapprochement sémantique ouvert ; 06 preuve disjointe ; 07 V1/SHA/float32 préservés ; 08 quatre exports séparés ; 09 opérations machine non inventées ; 10–12 UX novice/expert, clavier/DPI spécifiés ; 13 stale/crash/concurrence couverts en tests proposés ; 14 IA OCR facultative, non applicable au cœur de projection ; 15 raster non modifié ; 16 SVG/topologie et unités explicites ; 17 Fabrique/batch hors portée, non modifiés ; 18 Smart Delivery hors portée, non modifié ; 19 opportunités hors portée, non supprimées ; 20 métriques protocolisées non mesurées ; 21 licences et privacy ; 22 aucune gouvernance/code/PR modifié ; 23 pas de store ni moteur doublon ; 24 adoption suspendue ; 25 delta réel : distinction persisté/projeté/exporté et refus TextNode-in-strokes.

**Statuts :** document candidat ; tests unitaires nouveaux, Windows, GPU, Design Space, physique **NOT_RUN**. 24/141/140/80/437 inventaires historiques, 431/437 liens source, six exceptions et dix G6/G9 toujours ouverts ; 0/80 UX certifiées. **Prochaine action unique : Q04**, qualification sémantique des fiches UX existantes et de leurs critères/tests exacts, sans recommencer les 80 audits.
