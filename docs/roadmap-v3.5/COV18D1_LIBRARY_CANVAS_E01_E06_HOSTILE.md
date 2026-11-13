# V35-COV-18D1 — Revue hostile E01–E06 : bibliothèque, atelier, canevas, comparaison

**Statut : CANDIDAT, non normatif, 13 novembre 2026.** V3.4 reste ACTIVE. Cette fiche n'est ni du code ni une preuve de test. Sources : INHERITANCE_REGISTER E01–E06 (libellés d'origine), V3.4 lots 05/06/07/18/20/21/22/23, issue #134 et #142. Sources de code citées dans les lots historiques, non requalifiées comme HEAD courant. Les associations UX→S/V34 ci-dessous sont des **candidatures sémantiques**, non des liens historiques certifiés.

## Revue et décisions ID par ID

| ID / original | Décision, priorité | Héritage candidat et limites | Delta V3.5 testable |
|---|---|---|---|
| E01 bibliothèque, récents, miniatures, recherche/favoris | AMÉLIORER P0 | Lot 20, V34-134/136 à vérifier dans lot 23, S-017/S-038 ; `ManagedWorkspace.list_projects` plafonné à 100 selon lot 20 | Pagination réelle, statut primaire/sidecars groupé, index dérivé reconstructible, récents calculés sans fausse date de dernière édition |
| E02 collections/tags/modèles/duplication | RACCORDER P1 | Lot 20, S-024/S-039/S-041, V34-134/136 à confronter aux DoD ; V1 n'a pas de champ portable garanti | Duplication via writer V1 avec **nouveau project_id** et CAS ; tags locaux explicitement non portables tant que round-trip V1 non prouvé |
| E03 variantes/historique de création | AMÉLIORER P1/P2 | Lots 19–20, S-091/S-097/S-098 ; historique ≠ receipts d'export | Variantes dérivées d'un template SHA figé ; historique d'exécution externe comme reçu, jamais second projet ou journal canonique |
| E04 atelier hybride raster/vector/objets/propriétés | RACCORDER P0 | Lot 18, V34-041/035/038/132 ; Subject float32 ≠ calque SVG | Vue unique sur projet@SHA, inspecteur d'objet typé, brouillon raster et géométrie séparés, Undo local puis durable seulement si qualifié |
| E05 canvas zoom/pan/poignées/aimants/overlays | AMÉLIORER P0 | Lots 07/18, S-032, V34-041/045/132 candidats ; G3.3b vs démo | Matrice écran↔document stable, snap preview non mutant, poignées accessibles au clavier, grille et guide en unités connues |
| E06 comparaison avant-après/sliders/superposition | FUSIONNER avec preview atelier P0 | Lots 12/18, G3.3e ; aperçu L8 ≠ masque float32 ni artefact CUT | Deux rendus épinglés à SHA et version de pipeline, slider/overlay et diff local, aucun faux commit ni certification |

**Contre-expertise contraire :** une base SQLite canonique de bibliothèque serait plus commode pour tags et recherche mais introduirait une seconde autorité, migrations et conflits : **rejetée pour P0**. Une application canvas indépendante offrirait une UI rapide mais dupliquerait sélection, session et Undo : **rejetée**. Un historique de variantes intégré au schéma V1 risquerait des pertes sur anciens writers : **reporté** jusqu'à preuve de round-trip et autorisation propriétaire. Aucun framework Qt/Tauri n'est imposé sans benchmark.

## Contrats candidats (non APIs existantes)

**Catalogue dérivé :** `CatalogQuery{schema_version:1,root_id,after_cursor?,limit:int[1..100],filter?,sort}` → `CatalogPage{items:[{project_id,path_handle,project_sha256,health,thumbnail_key?}],next_cursor?,snapshot_token}`. Source de vérité = archives V1 validées par `inspect_project`, pas le cache. `snapshot_token` invalidé si contenu du répertoire change ; un curseur périmé renvoie `CATALOG_CHANGED`, jamais omissions silencieuses. `path_handle` interne, pas chemin fourni par le navigateur. Les sidecars sont états de récupération, pas fiches projets.

**Dupliquer :** `DuplicateRequest{source_handle,expected_sha256,target_name,command_id}` → `DuplicateReceipt{new_project_id,new_sha256,source_sha256}` ou `STALE_SOURCE|TARGET_EXISTS|LOCKED|INVALID_ARCHIVE|NO_SPACE`. Préparer depuis `load_project` et publier avec le writer validé, identité distincte, vérification SHA et float32, no-clobber atomique. Si le writer ne sait pas garantir l'exclusivité, opération désactivée. Aucune mutation silencieuse de V1 ou migration V2.

**Atelier :** `CanvasViewState{project_sha256,selection:{subject_id?,path_ids?},zoom,pan,active_tool,overlay_mode,request_token}` éphémère ; transformations physiques en **mm seulement lorsque la calibration est connue**, sinon coordonnées source normalisées. `PREVIEW` prend une copie sous SHA, retourne `PreviewResult{source_sha256,pipeline_version,request_token,raster_preview_ref,quality_state}`; résultat tardif = rejet. `COMMIT` seulement via bus/writer existant et expected SHA, avec recovery ; les sorties PNG PTC, SVG Basic Cut, SVG CUT multicouche et SVG d'édition restent indépendantes et immuables après export. La vue ne transforme pas une couleur ou une ligne en opération machine.

## UX novice et expert, états et accessibilité

Novice : accueil « Reprendre » → recherche paginée → statut sain/à examiner → ouverture → sélection sujet réel → zoom/poignées ou avant-après → prévisualisation non enregistrée → corriger/annuler → valider seulement si mutation qualifiée → sauvegarder → reprendre. Expert : inspecteur de SHA, source/masque float32, chemin SVG, dimensions et opérations KNOWN/UNKNOWN, raccourcis clavier et panneau de diagnostic ; même session, aucune deuxième autorité.

États : `EMPTY` (importer/créer), `INDEXING` (progression et annuler), `HEALTH_REVIEW` (lecture seule/récupération explicite), `READY`, `PREVIEW_PENDING`, `DIRTY_DRAFT`, `STALE`, `COMMIT_PENDING`, `RECOVERY_REQUIRED`. Transition `STALE` invalide poignées, previews et commit ; recharger puis choisir manuellement la reprise. Un slider ne modifie jamais le projet. À 1366×768 et DPI 200 %, panneaux repliables, focus visible, clavier sans piège, contraste, réduction de mouvement, légendes textuelles des couleurs/opérations. Gestes locaux de faible risque immédiatement réversibles ; sauvegarde externe et récupération demandent confirmation proportionnée.

## Tests TDD précis — PROPOSÉS, NOT_RUN

1. **Positif E01** : créer 125 archives V1 synthétiques ; pages successives retournent 125 IDs distincts, aucun sidecar comme projet, supprimer le cache puis reconstruire → mêmes identités/santés.
2. **Positif E02/E03** : dupliquer une fixture avec deux masques float32 et source SHA ; vérifier nouveau project_id, octets source et masques identiques, original intact ; variante à SHA modèle figé ne mute pas le modèle.
3. **Positif E04–E06** : sélection par subject_id malgré réordonnancement, zoom/pan/snap non mutants, slider à deux SHA épinglés ; Undo brouillon restitue exactement le rendu antérieur.
4. **Négatif 1** : cursor périmé et changement externe du dossier → `CATALOG_CHANGED`, pas de perte silencieuse.
5. **Négatif 2** : cible de duplication créée entre contrôle et publication → `TARGET_EXISTS`, aucun écrasement ni doublon.
6. **Négatif 3** : projet V1 corrompu/sidecar pending → lecture seule et recovery explicite, aucune duplication « saine ».
7. **Négatif 4** : source SHA modifié pendant preview ou réponse hors ordre → `STALE`, aucune mutation.
8. **Négatif 5** : masque float32 avec alpha intermédiaire, comparaison L8 → jamais remplacer les octets du masque par la miniature.
9. **Crash/annulation** : injection disque plein pendant clone/commit ; primaire et backup relisibles, aucune cible partielle annoncée ; relance avec même command_id sans double commit.
10. **Windows UI** : focus, clavier, DPI 200 %, écran 1366×768, chemin Unicode, verrou Windows/OneDrive ; **NOT_RUN**. GPU : non requis pour E01–E06, fallback CPU ; **NOT_RUN**. Design Space/coupe physique : non applicables aux gestes de catalogue/canvas ; les exports de fabrication gardent leurs gates séparés **NOT_RUN**.

**Performance à mesurer**, sans chiffres prétendument acquis : latence p50/p95 pagination 100/1000/10000 projets, mémoire de miniatures, zoom/pan sur image 5 Mpx, temps d'annulation et relecture SHA, en Windows CPU, disque lent et synchronisé. Fixtures synthétiques uniquement, aucune image personnelle/licence tierce dans le repo.

## Micro-lots, gates et revue hostile

TDD-1 catalog pagination/rebuild ; TDD-2 clone exclusif V1/CAS/recovery ; TDD-3 projection unique sélection et coordonnées ; TDD-4 compare non mutant ; TDD-5 UI clavier/DPI et injection de pannes ; TDD-6 qualification Windows. Réemploi à **vérifier dans HEAD** : `project_workspace_g22.py`, `project_archive.py`, `project_recovery.py`, `editor_session_g23.py`, `mask_snapshot_g24.py`, `smartsvg_express_atelier_preview.html`. Aucun nouveau fichier de code prescrit comme existant. DoD : tests non-skip, SHA de code, preuve UI Windows, aucun changement V1, zéro régression des quatre exports ; DoD historiques V34 et critères V3.3 intégraux restent à rapprocher ID par ID avant certification.

**Contrat 25 axes :** 01–06 héritage et preuve : inventaires conservés, pas de certification ; 07 V1/CAS/float32 couvert ; 08–09 exports/machine distincts, essais physiques non applicables à cette fiche ; 10–13 UX/canvas/accessibilité/recovery couverts ; 14 IA opt-in non requise, CPU manuel ; 15–16 raster/vector séparés, pas de modification de pipeline ; 17 bibliothèque/variantes couvert ; 18 Smart Delivery hors périmètre (consomme exports seulement) ; 19 autres idées conservées sans décision dans cette fiche ; 20 performance protocole non mesuré ; 21 sécurité/licences/chemins contrôlés ; 22–24 gouvernance, anti-doublon, revue non finalisée ; 25 aucune réduction des obligations. **Statuts : AUDITÉ candidat E01–E06, SPÉCIFIÉ partiel, REVU indépendant non démontré, PR_DOCS non créée, ADOPTÉ non, CODE/Windows/tests/GPU/DS/physique non revendiqués.**

**Prochaine action unique : V35-COV-18D2 — E07–E12**, reprendre descriptions originales et confronter exigences V3.3, DoD et tests locaux avant certification.
