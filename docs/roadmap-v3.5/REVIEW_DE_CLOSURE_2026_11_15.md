# REVIEW_DE — clôture contradictoire D01–D12 / E01–E20 (32 décisions)
**15/11/2026 — REVU au niveau des contrats candidats, NON ADOPTÉ ; V3.4 ACTIVE.** Relecture du curseur RUN_STATE, COV18C1/C2, COV18D1/D2/D3, REVIEW_DE_E13_E20 et DECISIONS_TRANSVERSALES. Main vérifié via `branches/main` : `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`. Branche candidate lue à `79bd86f1bdcafdf19d19b571c5d8f234b54d4e82`. Cette revue n'est **pas** une vérification intégrale des DoD 140 tickets, ni un test Windows/DS/physique. Les rapprochements source restent à certifier dans SOURCE_CLOSURE.

## Matrice des 32 arbitrages et oracles discriminants
| ID | Décision de conception | Correction hostile / oracle vérifiable et propriétaire |
|---|---|---|
| D01 | AMÉLIORER P1 | Registre modèle CPU/SAM selon version/licence/hash ; UNKNOWN interdit une promesse de segmentation. Lot 10/11, aucun download implicite. |
| D02 | RACCORDER P0 | Clic/lasso/pinceau/texte partagent le brouillon et la révision source ; masque float32 ≠ sélection. Prompt hostile non exécutable. |
| D03 | AMÉLIORER P1 | Variantes même ROI/SHA ; choisir une proposition produit un seul receipt CAS, résultat périmé rejeté. |
| D04 | RACCORDER P1 | Matting alpha translucide vérifié sur fonds clairs/sombres, sans confondre masque binaire et alpha continu. |
| D05 | AMÉLIORER P1 | Pixels inférés/interpolés, DPI déclaré et taille physique séparés ; aucune modification de CUT par upscale. |
| D06 | REPORTER P2 | Génératif raster/vector facultatif : licence/provenance/modèle qualifiés, preview non certifié machine. |
| D07 | RACCORDER manuel P0, REPORTER IA P2 | Réparation manuelle Undo immédiate ; inpainting jamais mutation silencieuse. |
| D08 | AMÉLIORER P1 | Hash = intégrité des octets, **pas signature/authenticité** ; source de confiance, licence, SBOM, consentements distincts ; aucun trust_remote_code implicite. |
| D09 | RACCORDER P0/P1 | Réservation CPU/VRAM et OOM ; budget estimé ≠ pic mesuré ; annulation libère worker et garde brouillon. |
| D10 | AMÉLIORER P1 base, P2 partage | **Corrige COV18C2** : preset déterministe simple P1, recette externe enrichie/partagée P2 ; aucune dépendance de D11 à P2. |
| D11 | RACCORDER P1 | **Corrige COV18C2** : `recipe_sha256` facultatif, `params_digest` et `capability_revision` obligatoires ; états READY_FOR_REVIEW/INTERRUPTED/NEEDS_REVIEW/STALE séparés ; reprise 17/30 sans duplication. |
| D12 | AMÉLIORER P1 | Suggestions règles locales sur catalogue fermé, non auto-exécutées ; données OCR/CSV/SVG traitées non fiables. |
| E01 | AMÉLIORER P0 | Index/miniatures reconstruisibles, pagination ; **tags/favoris non reconstruisibles** et stockés séparément avec sauvegarde atomique. |
| E02 | RACCORDER P1 | Collections locales non prétendues portables ; clone crée nouvel ID, politique de copie tags explicite. |
| E03 | AMÉLIORER P1/P2 | Variantes et reçus externes ≠ second projet canonique ; template et source SHA figés. |
| E04 | RACCORDER P0 | Canvas unique raster/vector ; composition/objets persistants nécessitent ADR_COMPOSITION_PERSISTENCE, pas simple export-only. |
| E05 | AMÉLIORER P0 | Matrice écran↔source, pan/zoom et snap non mutants ; DPI 200 % et clavier à qualifier. |
| E06 | FUSIONNER P0 | Avant/après = projection du même preview, pas deuxième cache/writer ; invalider sur source/révision. |
| E07 | RACCORDER P0 | Souris/menu/clavier → même CommandIntent ; survol non mutant ; sélection stale refusée. |
| E08 | AMÉLIORER P0 | Novice/expert ne change que divulgation, jamais moteur ni projet ; brouillon survit au basculement. |
| E09 | RACCORDER P1 | Préférences locales versionnées/backup ; corruption n'efface ni tags ni projet. |
| E10 | AMÉLIORER P0 | Focus, raccourcis, contraste, 1366×768 et DPI 200 % ; preuve Windows NOT_RUN. |
| E11 | RACCORDER P0 | Undo brouillon distinct d'Undo durable CAS ; PR #144 DRAFT a un port backend, **pas bouton Tk**. Aucun CODE_MAIN déduit. |
| E12 | GARDER/AMÉLIORER P0 | Writer V1 unique, masques float32, provenance, recovery et relecture après crash ; migration V2 explicite seulement. |
| E13 | AMÉLIORER P0 | PreviewKey inclut session, SHA, source, révision, paramètres, pipeline et génération ; réponse tardive rejetée. |
| E14 | RACCORDER P0 | Cause stable, traduction et remediation séparées ; UNKNOWN ≠ réparé. |
| E15 | AMÉLIORER P0 | QA sur PNG réellement exporté, ICC/EXIF/alpha/bleed/dimensions ; DPI ≠ détail réel. |
| E16 | AMÉLIORER P0 | SVG éditable peut être valide sans mm ; CUT non qualifié sans dimensions, trous, topologie et XML sûr. |
| E17 | GARDER P0 | Quatre gates LOCAL_GEOMETRY / PROFILE_CAPABILITY / DS_IMPORT / PHYSICAL_CUT indépendantes par SHA. |
| E18 | AMÉLIORER P0/P1 | Portable Windows #145 sur main ≠ updater/installateur/rollback ; opt-in et tests séparés. |
| E19 | AMÉLIORER P0 | Réseau update, modèle, télémétrie et transfert : consentements indépendants, export support expurgé. |
| E20 | RACCORDER P1 | Aide HTML locale selon commande/état/rôle/capacité ; ne jamais promettre coupe Explore 5 sans preuve. |

## Résolution des contradictions et limites de la revue
1. **D10/D11** : priorité P1 des presets déterministes et recette facultative dans batch ; COV18C2 disait P2 obligatoire. Décision transversale D04 prévaut dans la candidate, sans modifier les archives.
2. **D08** : supprimer l'expression « signé par hash » de l'interprétation ; SHA vérifie intégrité, pas authenticité. Provenance de confiance distincte.
3. **E01/E02/E09** : index jetable vs métadonnées utilisateur durables, sauvegarde et recovery ; ne jamais purger favoris/tags avec miniatures.
4. **E04/E11/E12** : composition persistante future selon ADR ; pas d'Undo ou store de composition parallèle, pas de V2 silencieux. PR #144 reste code branche, non preuve d'exposition Windows.
5. **E13–E17** : rapports par artefact et rôle ; quatre sorties séparées PNG PTC / SVG Basic Cut / SVG CUT multicouche / SVG éditable ; prévol local ≠ Design Space ≠ coupe physique.
6. **E18/E19** : portable sur main ne prouve pas updater, télémétrie ni consentement ; aucun changement de packaging ou gouvernance dans cette revue.
7. **WIP** : PR ouvertes #144/#140 et autres à requalifier au HEAD avant intégration. Aucune modification du producteur ni fusion.

## Contrats d'acceptation, tests et réversibilité
**Source de vérité** : .smartsvg V1, project_id/revision/SHA CAS, Subject et masques float32 ; toutes previews, recettes, batch, index et rapports sont dérivés/externes. Les interfaces candidates sont celles des fiches COV18 et des décisions transversales, **pas des APIs affirmées existantes**. Geste local réversible sans popup ; IA/téléchargement/écriture externe avec consentement proportionné. États EMPTY/DRAFT/PENDING/READY/STALE/ERROR/RECOVERY_REQUIRED ; annulation avant commit sans mutation ; crash après commit = relecture et outcome UNKNOWN tant que non inspecté.

**Positifs proposés** : (P1) D02+D03 deux variantes même ROI, commit unique puis Undo float32 ; (P2) D11 reprise de 17 unités publiées sur 30 sans duplication ; (P3) E04/E11 sauvegarde→réouverture→Undo/Redo au SHA attendu ; (P4) E15–E17 quatre artefacts, quatre QA distinctes ; (P5) E01/E09 reconstruction miniatures conserve tags/favoris. **Négatifs proposés** : (N1) modèle hash/licence inconnus → aucun téléchargement ; (N2) résultat stale après modification CAS → zéro commit ; (N3) disque plein pendant batch/ZIP → sortie finale intacte, reçus PARTIAL honnêtes ; (N4) SVG XXE ou dimensions CUT inconnues → aucune certification ; (N5) changement session/génération → preview non réutilisé ; (N6) préférences corrompues → backup et projet intact ; (N7) annulation/OOM GPU → repli manuel explicite, aucun retry silencieux. Tests Windows clavier/DPI, GPU réel, DS versionné et coupe physique sont **NOT_RUN** et indépendants. Corpus synthétique sous licence ; mesures p50/p95, RSS/VRAM et temps recovery à collecter, aucune valeur inventée.

**Découpage TDD futur** : T1 vérifier ports/tickets/DoD et fixtures sur main HEAD ; T2 commandes, CAS et previews ; T3 QA typée/exporteurs ; T4 batch et préférences/recovery ; T5 IA consentie ; T6 parcours Windows/DS/physique séparés. Rollback : désactiver capacités non qualifiées, conserver V1 et V3.4 active ; aucune fusion, aucun nouveau schéma ou dépendance ici.

## Contrôle 25 axes et verdict
01–05 : 24 lots/141 exigences/140 tickets/80 UX/437 scénarios **inventoriés historiquement**, sémantique complète encore ouverte ; 06 : SHA main vérifié, preuves produit séparées ; 07–09 : V1/CAS/float32, 4 exports, profils KNOWN/UNKNOWN ; 10–13 : parcours, gestes, clavier/DPI, Undo, crash, stale ; 14 : IA optionnelle/licences/VRAM ; 15–16 : raster/alpha, SVG/topologie ; 17 : batch/CSV/bibliothèque ; 18 : Smart Delivery consommateur, ZIP hors lot ; 19 : opportunités à revoir ; 20 : performances protocoles, pas chiffres ; 21 : confidentialité/consentements ; 22 : branche documentaire seule, WIP inchangé ; 23 : aucun second moteur/store/writer ; 24 : revue globale/promotion ouvertes ; 25 : aucun axe supprimé. **REVU = 32 décisions au niveau architecture candidate**, pas 32 fonctions codées ou certifiées ; correspondances historiques exactes/critères intégraux restent SOURCE_CLOSURE. Aucun nouveau test exécuté.