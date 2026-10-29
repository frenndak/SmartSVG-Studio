# SmartSVG Studio V3.4 — Lot 12 : pipeline raster, alpha, anti-halo, HD conditionnelle et Print Then Cut

**DRAFT de conception — 29 octobre 2026.** V3.3 demeure ACTIVE. Issue #72, PR draft #73 ; base `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche documentaire observée avant ce lot `1e23a310df134c5939f3e8df107f57e6e4334c06`. Tous les chemins `engine/smartsvg_app/...` et `tests/raster/...` sont des **livrables FUTURS**, non des fichiers existants. Aucun test du produit, Windows, GPU, Design Space ni découpe physique exécuté ici.

## 1. Problème, héritage et état effectivement observé

**Objectif métier.** À partir d'un JPG/PNG, d'une photo smartphone ou de 12 illustrations, préparer une image imprimable propre et une silhouette de coupe vérifiable **sans modifier l'original**, sans prétendre qu'un agrandissement ajoute des détails réels, et sans confondre « PNG de Print Then Cut » avec « SVG de découpe » ou « SVG vectoriel éditable ». L'atelier doit fonctionner sans IA, sans réseau et sans ComfyUI. Le modèle IA du lot 11 n'est qu'une proposition facultative de pixels/masque, jamais l'autorité du contour de fabrication.

**Code réel relu dans `main` :**
- `engine/smartsvg_quality/prepare.py` : crop prudent avant segmentation, `MAX_PIXELS=5_000_000`, RGB(A) float borné, recadrage manuel en % entiers 0..45, fallback sans crop.
- `engine/production_v211.py` : `_resample_print` fait un redimensionnement RGBA prémultiplié et blanchit le RGB transparent ; `_new_subject_sticker` crée un support blanc, dilate l'alpha de 1,2 mm **dans cette version**, et `_rewrite_print` recalcule PNG/SVG à la même géométrie de destination. Le 1,2 mm n'est **pas** une valeur certifiée Cricut ni une règle universelle de V3.4.
- `engine/smartsvg_quality/auto_hd.py` : dérivés CPU **facultatifs**, cible 600 ppp, budgets 5 MP source / 6 MP dérivé / 50 MP total / 32 objets, provenance SHA ; son contrôle d'alpha compare des formes après redimensionnement, **pas une égalité bit à bit des contours**. L'original manufacturable reste inchangé.
- `engine/smartsvg_quality/white_sheet_v21152.py` : détourage heuristique de grilles blanches régulières 4×3/6×4 ; pas une segmentation universelle de photo.
- `engine/smartsvg_cricut/direct_import_v218.py` : audit statique PNG RGBA, `MAX_PIXELS=32_000_000`, `MAX_ITEMS=32`, bornes heuristiques 175×240 mm **non garanties** ; la silhouette Print Then Cut vient de l'alpha du PNG et le SVG diagnostic ne doit pas être superposé.
- `engine/smartsvg_governance/artifact_qa.py` : seuils alpha 0/20/128, topologie/rectangle, état final `REVIEW_REQUIRED` ou `BLOCKED`, jamais certification Design Space.
- `engine/smartsvg_quality/release_gate_v21152.py` : précontrôle d'exports publiés et rapports séparés ; aucun essai machine.
- `engine/smartsvg_ai/quality_v21121.py` : géométrie indicative et drapeaux de revue, non preuve sémantique.

**Exigences héritées directement :** S-002/003/006/009/010/015/016/017/018/022/023/027/029/041/042/050/053/058/062/067/070/073/074/079/080/084/093/095 ; R33-003/004/006/009/011/012/017/018/019/020/022/024/025/026/030/031/034/036/037/039. **Dépendances V34 :** V34-017/020/021/025/028/029/032/036/039/050/059/061/068..077/078..086. Les 141 IDs historiques restent conservés par `HERITAGE_INDEX.md` ; le mapping inverse global demeure à produire.

**Limites de ce lot :** pas de segmentation sémantique (10), sélection définitive de modèle (11), géométrie vectorielle éditable (13), profil machine certifié (15), placement de planches (19), impression directe ni génération de marques capteur Cricut.

## 2. Contre-expertise du lot 11 et ADR-034-15 (PROPOSÉE)

**Correction de frontière :** un modèle Real-ESRGAN ne doit jamais devenir une étape implicite de Print Then Cut. L'option `enhance` s'applique à une **branche raster dérivée**, identifiée par `source_digest + transform_digest`, et non à l'original, au masque float32 autoritatif ou au contour SVG accepté. Si le modèle est absent, non qualifié, en OOM ou refusé, le pipeline CPU déterministe fonctionne toujours. `READY_QUALIFIED` du lot 11 ne prouve pas la fidélité visuelle d'un upscale sur une image donnée.

**ADR-034-15 : DAG de dérivés typés, géométrie de coupe figée séparément de la texture imprimée.**
- **A.** Réutiliser les fonctions `prepare/_resample_print/auto_hd/artifact_qa` via adaptateurs avec tests de parité : **recommandé pour un premier vertical slice**, sans import ComfyUI implicite (voir V34-017).
- **B.** Remplacer tout le pipeline par un unique modèle IA : **rejeté** (licences, VRAM, topologie non déterministe, offline).
- **C.** Garder une copie raster par opération en archive V1 sans schéma : **rejeté** (contrats ZIP V1 stricts, identité et révision non définies).
- **D.** DAG de transformations déterministes, cache de dérivés hors archive ou ressources V2 explicites, export atomique après prévol : **cible à prototyper**. L'algorithme peut varier par intention, mais le contour accepté est toujours révalidé après toute transformation affectant l'alpha.

**Invariants P0 :** (i) octets de la source intacts ; (ii) coordonnées source/ROI/EXIF et échelle physique explicites ; (iii) aucune génération de détails prétendument réels ; (iv) image imprimée et silhouette découpe associées à la **même révision** ; (v) alpha de découpe distinct de l'alpha de composition ; (vi) PNG de fabrication produit depuis une géométrie acceptée, jamais depuis une vignette ou une sortie IA non revue ; (vii) `Preview`/`Draft`/`ReviewRequired`/`Blocked` ne signifient jamais `QUALIFIE`.

## 3. Parcours novice, expert et wireframes textuels

**Novice, 12 escargots :** Importer → sélectionner « Stickers / Print Then Cut » → confirmer les 12 sujets proposés (lot 10) → « Nettoyer les bords » avec comparaison avant/après et contrôle de l'alpha → saisir largeur souhaitée en **mm** (ne jamais déduire une taille depuis DPI EXIF) → prévisualiser l'image et sa **silhouette de coupe distincte** → exporter PNG RGBA et guide Design Space. Si fond non fiable, proposer correction manuelle ; si la taille imprimée ou l'enveloppe Cricut est inconnue, export **brouillon à vérifier**, pas « prêt à couper ». Un SVG de contour diagnostic reste séparé.

**Expert :** choix `SOURCE/CROP/ALPHA_COMPOSE/PRINT_TEXTURE/CUT_SILHOUETTE`, gestion de profil colorimétrique et orientation EXIF, choix du rééchantillonnage CPU, visualisation de pixels RGBA prémultipliés, seuils de prévol 0/20/128, provenance, comparaison de topology avant/après, quotas, export manifeste et détection de cache périmé. IA optionnelle seulement après validation du catalogue du lot 11.

~~~text
[Express · Stickers] [Hors ligne ✓] [Source conservée ✓]
[Original | Nettoyage proposé | Différence]  [Zoom 100 %] [Fond damier]
[Sujets 12/12] [Taille : ___ mm, obligatoire] [A4 : À VÉRIFIER]
[Coupe extérieure : 12] [Îlots/trous : 0 attendu] [Alertes : 1]
[Corriger le bord] [Revenir à l'original] [Exporter un brouillon]
Guide : importer le PNG en Flat Graphic ; vérifier taille et contour dans Design Space.
~~~

~~~text
[Expert / Raster DAG] Source sha... → Crop ROI → Mask float32 → Alpha compose
                              ↘ Print texture (CPU/IA opt-in) ↘ PNG export
Accepted cut geometry digest... ─────────────────────────────→ Alpha CUT
[EXIF/orientation] [RGB/ICC] [Alpha 0/20/128] [Pixels source/cible]
[Mesures: bord/ΔE/SSIM si référence] [Budget RAM/temps] [Provenance]
[Comparer] [Commit non destructif] [Prévol] [Rollback]
~~~

**États UX :** `SOURCE_READY`, `ROI_PENDING`, `MASK_REVIEW`, `RASTER_DRAFT`, `PREVIEW_READY`, `EXPORT_REVIEW_REQUIRED`, `EXPORT_BLOCKED`, `EXTERNAL_VALIDATION_PENDING`. Les transitions `EXPORT_BLOCKED→EXTERNAL_VALIDATION_PENDING` sont interdites sans correction et nouveau prévol. Les boutons de validation sont accessibles clavier, erreurs localisées FR, avertissements textuels indépendants des couleurs.

## 4. Contrats de données, types et événements (SPÉCIFICATION, pas code exécuté)

`RasterTransformSpec` immuable : `schema_version: "v34-raster-transform/1"`; `source_asset_id: UUID`; `source_sha256: hex64`; `source_dimensions_px: [int>0,int>0]`; `exif_orientation_applied: bool`; `orientation_transform: enum`; `roi_source_xyxy: [int,int,int,int]` borné dans la source après orientation ; `mask_ref: {resource_id, float32_sha256, roi_sha256}` ou `null` si image opaque explicitement choisie ; `intent: PRINT_THEN_CUT|RASTER_PREVIEW|PRINT_ONLY`; `physical_width_mm: decimal>0|null`; `target_ppi: int|null` (métadonnée de rendu, pas preuve d'échelle Design Space) ; `alpha_policy: KEEP|COMPOSE_WHITE_BACKING|MANUAL`; `texture_enhancement: NONE|CPU_RESAMPLE|LOCAL_AI`; `cut_geometry_ref: UUID|null`; `model_receipt_id: UUID|null`; `expected_project_sha256: hex64`; `algorithm_version: string`; `options_digest: hex64`. Les options inconnues sont rejetées ; dimensions nulles empêchent l'export physique revendiqué.

`RasterArtifactReceipt` : `artifact_sha256`, `source_sha256`, `transform_digest`, `project_revision_digest`, `width_px`, `height_px`, `width_mm|null`, `ppi_metadata|null`, `color_space`, `icc_digest|null`, `alpha_composition_digest`, `cut_alpha_digest|null`, `topology_report_id`, `status`, `warnings[]`, `model_receipt_id|null`, `validation_axes: {auto,windows,gpu,design_space,physical}`. Le SHA final est un **sidecar externe** si nécessaire ; ne jamais introduire d'auto-référence dans une archive.

Exemple de demande **syntaxiquement JSON, valeurs illustratives** :

~~~json
{
  "schema_version":"v34-raster-transform/1",
  "source_asset_id":"b65ed128-833b-45f9-9bd3-0c802f1c4c6f",
  "source_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_dimensions_px":[2400,1600],
  "exif_orientation_applied":true,
  "orientation_transform":"EXIF_TO_TOP_LEFT",
  "roi_source_xyxy":[100,80,900,880],
  "mask_ref":{"resource_id":"mask-roi-02","float32_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","roi_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"},
  "intent":"PRINT_THEN_CUT",
  "physical_width_mm":40,
  "target_ppi":300,
  "alpha_policy":"COMPOSE_WHITE_BACKING",
  "texture_enhancement":"CPU_RESAMPLE",
  "cut_geometry_ref":"e66c6dca-3ec6-4f12-9a91-9e7f5e8dc882",
  "model_receipt_id":null,
  "expected_project_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "algorithm_version":"raster-v34-proposed-1",
  "options_digest":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
}
~~~

**Commandes (CommandPort du lot 06) :** `ProposeCrop`, `ProposeAlphaCleanup`, `AcceptRasterTransform`, `SetPrintDimensions`, `SelectPrintTexture`, `RequestRasterPreview`, `PreflightRasterExport`, `PublishRasterExport`, `DiscardRasterProposal`. **Événements :** `RasterProposalCreated`, `RasterPreviewReady`, `RasterProposalStale`, `RasterCommitAccepted`, `RasterExportBlocked`, `RasterExportPublished`, `RasterJobOOM`. Les événements transportent digests et IDs, jamais une image privée complète. `PublishRasterExport` exige CAS, masque/contour accepté et prévol sur les mêmes digests ; le worker de rendu ne mute pas le projet.

**Interfaces FUTURES :** `RasterPort.propose(request)->Proposal`, `RasterPort.render(proposal, budget)->Derivative`, `RasterQAPort.inspect(derivative, accepted_cut)->Report`, `ExportPort.publish(manifest, expected_sha)->Receipt`, `ModelRuntimePort.infer(qualified_handle, ROI)->Proposal`. Les consumers sont respectivement Express/Atelier, file Jobs, Fabrique, Delivery et assistant ; aucun import direct de nœuds ComfyUI depuis ces ports.

## 5. Déroulé déterministe, alpha et couleur

1. **Admission :** valider format, taille, décompression, chemins autorisés, pixels/ICC/EXIF et quota avant décodage coûteux. SHA des octets originaux ; décoder dans sandbox local. Les images ICC/CMYK sont converties vers une représentation de travail documentée (sRGB ou profil explicite) sans jeter le profil d'origine ; pas de promesse de correspondance imprimante.
2. **Orientation et ROI :** appliquer l'orientation EXIF exactement une fois dans la vue logique, enregistrer transformation inverse et repères ; aucun masque antérieur ne reste valide si la transformation change. Conserver `source_sha256` original.
3. **Masque :** charger le float32 exact de la ROI V2 (lot 10) ou mode manuel ; vérifier bornes [0,1], finite, dimensions et liaison à l'identité. Refuser les masques legacy dont la preuve manque. Le seuillage est **une dérivation**, pas une réécriture du masque.
4. **Nettoyage :** érosion/dilatation et suppression d'îlots uniquement en **proposition réversible**, avec unités px/mm explicites, conservation des accessoires et trous choisis. Prévisualiser l'alpha de composition séparément de la silhouette `CUT` ; comparer nombre de composantes, trous, contact bord et distance de Hausdorff approximée sur mêmes repères.
5. **Anti-halo :** compositing en alpha prémultiplié (linéaire ou espace choisi et déclaré) puis démultiplication sûre ; définir RGB des pixels alpha zéro pour éviter le noir parasite sans influencer le contour. Contrôler RGB des franges sur fond blanc, noir et damier ; aucun « anti-halo » ne doit détruire une bordure de dessin voulue.
6. **Texture impression :** redimensionner à une cible px calculée de `mm × ppi / 25.4` avec arrondi documenté. Si résolution source insuffisante, afficher `SOURCE_RESOLUTION_LIMITED` et proposer conserver, CPU ou IA **déjà installée et consentie**. Ne pas afficher « 600 ppp natifs » pour une interpolation 300→600. Le DPI PNG est une métadonnée ; Design Space peut redimensionner après import.
7. **Coupe :** appliquer une géométrie de contour acceptée, éventuellement support blanc/offset explicitement paramétré, puis construire l'alpha final Print Then Cut depuis **ce contour**. Vérifier correspondance alpha↔cut à la résolution finale. Un contour d'une planche ne doit pas devenir un cadre rectangulaire par accident. Les trous internes sont un choix d'intention, pas une conséquence cachée du lissage.
8. **Prévol et publication :** seuils alpha 0/20/128 + composantes + trous + bords + dimensions mm/px + provenance + budget + fichiers sans liens/sortie hors racine ; écrire dérivés en staging, valider hash et publier atomiquement selon writer du lot 06. Sur erreur, conserver ancien export et original, supprimer staging après preuve ; jamais écraser un export validé sous même nom sans transaction.
9. **Transfert :** PNG RGBA pour import `Flat Graphic` dans Design Space, réglage Print Then Cut et taille à **vérifier manuellement**. Ne pas imprimer un PDF de marques de capteur fabriqué par SmartSVG ; les marques sont produites par Design Space pendant son flux. L'A4 est imprimé en portrait, puis placé **grand côté horizontal** sur le tapis Explore 5 conformément au guide officiel ; impression/découpe dans une même session Design Space.

**Cas adversariaux :** EXIF 6/8, ICC inconnu, CMYK, alpha prémultiplié mal encodé, PNG palettisé/tRNS, pixels alpha 1..20, fond blanc avec ombres, blanc légitime du sujet, sujet touchant le bord, microtrous, cheveux/antennes, accessoires disjoints, photos bruitées, logos à aplats, 50 ROI, masque 32/5 MP legacy, OOM, source modifiée, collision de nom, deux jobs sur même projet, crash après publication avant receipt, cache obsolète. Fallback : source intacte, export `REVIEW_REQUIRED` ou `BLOCKED`, correction manuelle et réexécution avec nouveau digest.

## 6. Performance, qualité et stratégie de preuve

**Objectifs proposés, à mesurer et non garantis :** première preview 12 ROI synthétiques ≤3 s p50 sur PC de référence CPU (définir CPU/RAM au protocole), réponse UI aux actions locales ≤150 ms p95 hors rendu, aucune allocation d'un tenseur 50×image complète, pic mémoire par job et temps p50/p95 mesurés. Ne pas adopter ces seuils comme gate final avant mesure baseline. GPU RTX 3070 8 Go : **aucune mesure** ; CPU reste disponible. Cache indexé par source SHA + ROI + masque float32 digest + algorithme + options + profil couleur + version ; invalidation sur toute variation, écriture temporaire et purge bornée. Les traitements par tuiles imposent recouvrement/halo mesuré et test de jointures ; pas de tuilage silencieux d'une opération morphologique dont la portée dépasse le halo.

**Mesures qualité :** avec référence autorisée, comparer IoU/Dice des masques et Hausdorff 95/erreur de bord en px, comptage composantes/trous, ΔE colorimétrique si gestion ICC maîtrisée, SSIM/PSNR sur texture **uniquement si vérité terrain disponible**. Sans référence, afficher histogrammes et warnings, jamais un score de fidélité fictif. Mesurer seuils alpha sur le PNG exporté et non seulement le masque float32 source. Comparer source/CPU/IA sur même ROI et même taille physique, avec méthode et provenance.

**Corpus synthétique FUTUR :** `R12-A` 12 escargots sur fond blanc (formes originales dessinées pour tests, pas d'œuvres protégées) ; `R12-B` PNG RGBA avec halo noir semi-transparent ; `R12-C` dessin complexe multi-îlots et trous ; `R12-D` photo smartphone EXIF 6, profil ICC et bruit ; `R12-E` planche 24/50 ROI avec budget mémoire ; `R12-F` carton opaque pour parcours Score+Cut (aucun upscale requis) ; `R12-G` PNG adversarial très grand/palettisé/CMYK/alpha faible. Chaque fixture doit avoir hash, licence/provenance, masque de référence lorsque pertinent et dimensions attendues.

## 7. Tests de recette à implémenter (T-V34-12-01..30 ; tous NON_EXECUTE)

| Test | Assertion exacte attendue | Axe futur |
|---|---|---|
| T-V34-12-01 | Source byte SHA inchangé après crop/nettoyage/export | auto |
| T-V34-12-02 | EXIF 6/8 : ROI, masque et inverse de coordonnées coïncident sans double rotation | auto |
| T-V34-12-03 | Source ICC/CMYK : conversion déclarée, original et ICC d'origine préservés | auto |
| T-V34-12-04 | Image surdimensionnée ou bombe de décompression refusée avant rendu | auto sécurité |
| T-V34-12-05 | Float32 NaN/Inf ou shape incorrect → BLOCKED, aucun projet muté | auto |
| T-V34-12-06 | Alpha prémultiplié : pas de halo noir sur fond blanc/noir aux points témoins | auto visuel |
| T-V34-12-07 | Alpha zéro RGB blanc n'altère pas l'alpha de coupe accepté | auto |
| T-V34-12-08 | Bord/antenne volontaire non supprimé sans confirmation d'une proposition | auto + UX |
| T-V34-12-09 | 0/20/128 : composantes/trous détectés et rapportés sur export réel | auto |
| T-V34-12-10 | Masque changé après preview → stale, export interdit sous ancien digest | auto concurrence |
| T-V34-12-11 | `mm×ppi/25.4` : largeur px arrondie explicitement, metadata ppi conservée | auto |
| T-V34-12-12 | Taille mm absente → aucune mention « taille physique garantie » | auto + UX |
| T-V34-12-13 | CPU interpolation 300→600 ne porte jamais badge « détails natifs augmentés » | auto + UX |
| T-V34-12-14 | IA absente/refusée → rendu CPU/manuel sans réseau | auto sécurité |
| T-V34-12-15 | IA OOM → source et contour inchangés, fallback et unload | auto + Windows/GPU |
| T-V34-12-16 | Image texture IA différente ne change pas le digest de coupe accepté | auto |
| T-V34-12-17 | PNG RGBA Print Then Cut : alpha final lié à cut digest, SVG diagnostic non superposé | auto |
| T-V34-12-18 | Support blanc/offset modifié → nouveau prévol, ancien export non certifié | auto |
| T-V34-12-19 | Alpha rectangulaire involontaire → BLOCKED ; carte rectangulaire explicite → revue | auto |
| T-V34-12-20 | 12 sujets → 12 silhouettes extérieures attendues, trous selon choix, sans faux cadre | auto |
| T-V34-12-21 | 24/50 ROI : lots bornés, ordre stable, pas de 50 masques full-frame | auto mémoire |
| T-V34-12-22 | Cache identique → dérivé byte-identique ou divergence explicitée par version | auto |
| T-V34-12-23 | Cache source/ICC/ROI/masque/version modifié → invalidation | auto |
| T-V34-12-24 | Tuilage : jointures/halo sous tolérance définie ou fallback non tuilé | auto |
| T-V34-12-25 | Deux exports concurrents et crash staging → un receipt cohérent, aucun overwrite | auto + Windows/NTFS |
| T-V34-12-26 | Fichier symlink/path traversal ou nom collision → refus sans toucher original | auto sécurité |
| T-V34-12-27 | UX clavier FR : avant/après, taille, warnings et rollback accessibles | Windows UX |
| T-V34-12-28 | Import Flat Graphic : taille/contour/opération vérifiés manuellement, preuve liée version | DesignSpace (NON_EXECUTE) |
| T-V34-12-29 | A4 Explore 5 : imprimer portrait, placer paysage sur tapis, session unique, résultat documenté | DesignSpace + physique (NON_EXECUTE) |
| T-V34-12-30 | Parcours boîte Score+Cut : aucune texture raster n'infère un outil Score ni une opération machine | auto + DesignSpace futur |

**Recette de chaque test :** SHA code et fixture, environnement, assertions, artefact de rapport, axes `auto/Windows/GPU/DesignSpace/physique` séparés ; `PASS` seulement après exécution. Une preuve auto ne remplit jamais les cases Design Space/physique. Les tolérances colorimétriques et les seuils de bord ne sont pas arbitrairement figés : une fixture de référence et un protocole d'évaluation doivent être approuvés avant de les déclarer PASS.

## 8. Tickets de développement FUTURS (tous SPECIFIE ; pas de code livré)

**DoD commune :** contrat versionné, fichier source non muté, tests associés réellement exécutés sur SHA, absence de régression V1/ComfyUI, logs sans données privées, fallback manuel, preuve par axe et rollback documenté. Aucune qualification par simple existence de cette spec.

| Ticket / priorité | Dépendances S/R33/V34 | Fichiers futurs, test précis, preuve, DoD spécifique, rollback |
|---|---|---|
| **V34-087 P0** admission, orientation, ICC/ROI | S-003/023/042 ; R33-003/025 ; V34-025/068/070 | `engine/smartsvg_app/raster/ingest.py`, `tests/raster/test_ingest.py` ; T01..05 ; preuve auto/sécurité ; DoD SHA source+transform inverse corrects ; rollback import brut sans transformation |
| **V34-088 P0** moteur alpha composition vs cut | S-015/073/079 ; R33-004/026 ; V34-070/071/075/087 | `engine/smartsvg_app/raster/alpha.py`, `tests/raster/test_alpha.py` ; T06..10/16..20 ; preuve auto/visuelle ; DoD cut digest stable si texture change ; rollback masque original |
| **V34-089 P0** tailles, rééchantillonnage et texture CPU | S-016/029/050 ; R33-018/022 ; V34-087/088 | `engine/smartsvg_app/raster/resize.py`, `tests/raster/test_resize.py` ; T11..13/16 ; preuve auto/Windows ; DoD unité mm explicite, pas de faux HD natif ; rollback texture originale |
| **V34-090 P0** prévol raster et publication atomique | S-009/010/017/084 ; R33-009/022/034 ; V34-032/039/088/089 | `engine/smartsvg_app/raster/preflight.py`, `tests/raster/test_export.py` ; T09/10/17..20/25/26/28 ; preuve auto + DesignSpace séparée ; DoD pas de publication `BLOCKED`, receipts CAS ; rollback ancien export |
| **V34-091 P1** preview/diff novice/expert | S-013/071/080 ; R33-019/020 ; V34-041/049/076/088 | `engine/web/js/v34_raster_review.mjs`, `tests/raster/test_raster_ui.mjs` ; T08/10/12/13/27 ; preuve Windows UX ; DoD messages FR, clavier et états stales ; rollback écran statique |
| **V34-092 P1** texture IA conditionnelle | S-005/016/027 ; R33-017/018/031 ; V34-078..086/089 | `engine/smartsvg_app/raster/ai_texture.py`, `tests/raster/test_ai_texture.py` ; T14..16 ; preuve auto + GPU Windows future ; DoD aucun modèle requis, OOM non mutant ; rollback CPU |
| **V34-093 P1** cache/ROI/tuilage | S-018/050/062 ; R33-011/012/031 ; V34-036/039/070/087/088 | `engine/smartsvg_app/raster/cache.py`, `tests/raster/test_cache.py` ; T21..25 ; preuve auto mémoire/Windows ; DoD cache invalide jamais réutilisé ; rollback rendu sans cache |
| **V34-094 P1** corpus/benchmarks et guide Cricut | S-006/010/029/093 ; R33-018/022/034 ; V34-009/076/090 | `tests/fixtures/v34_raster_synthetic/`, `tests/raster/benchmark_raster.py`, `docs/roadmap-v3.4/benchmarks/12_raster_validation.md` ; T01..30 ; preuve auto/Windows/DesignSpace/physique **distinctes** ; DoD résultats mesurés et non inventés ; rollback gate non qualifiée |
| **V34-095 P1** analyse comparative du rendu imprimé (O-025/O-026) | S-015/016/073 ; R33-019/022 ; V34-088/089/090/091 | `engine/smartsvg_app/raster/print_review.py`, `tests/raster/test_print_review.py` ; T06/09/11/12/17/20/27 ; preuve auto/UX ; DoD contrôle de franges et seuils, sans faux score physique ; rollback preview simple |

**Mapping inverse du lot :** T01..05→087 ; T06..10→088 ; T11..13→089 ; T09/10/17..20/25/26/28→090 ; T08/10/12/13/27→091 ; T14..16→092 ; T21..25→093 ; T01..30→094 ; T06/09/11/12/17/20/27→095. Tous les tests remontent à un ticket, et chaque ticket remonte à S/R33 ; aucune exigence historique n'est supprimée. La matrice inverse **globale** 141→V34→tests reste ouverte.

## 9. Opportunités nouvelles, risques et non-objectifs

- **O-025 P1, retenue :** « aperçu de franges sur fonds blanc/noir/damier et échelle physique indicative » ; différent de O-002 (orientation/transfert A4) et O-020 (inspection du masque avant acceptation) car examine la **texture imprimée finale**. Ticket V34-095, T06/11/12/27.
- **O-026 P1, retenue :** « comparaison topologique multi-seuil alpha avant/après export » ; différent de la QA historique car affiche la **régression entre deux versions** et rattache une correction ciblée. Ticket V34-095, T09/17/20.
- **O-027 REJET :** upscale IA automatique systématique à 600 ppp ; peut créer des artefacts et ne prouve pas de détails réels ; alternative CPU sans IA + modèle installé sur demande. Aucun ticket de cette fonction rejetée.

**Risques ouverts P0 :** budget mémoire des ROI et alpha dérivés ; fidélité de l'alpha après interpolation et surimpression du support blanc ; colorimétrie/ICC/printer ; choix des tolérances et corpus ; cycle de vie V2/receipts ; source ComfyUI et imports `engine/__init__` ; limite réelle de la zone Print Then Cut A4 dépendante de machine/version/forme ; preuve Windows/GPU/Design Space/physique absente. La valeur `175×240 mm` du legacy n'est pas une garantie d'enveloppe ; aucune marque de capteur ne doit être générée par SmartSVG.

**Contrôle de cohérence inverse :** aucune commande IA ne peut muter `.smartsvg` ; `RasterArtifactReceipt` lie la texture et la coupe à la même révision ; `cut_geometry_ref` n'est pas un SVG d'édition ; `Score` n'est jamais une couleur ou un trait raster ; Print Then Cut conserve son contrat PNG ; l'agrandissement ne change pas la dimension physique sans commande explicite. Tout test réel manquant est `NON_EXECUTE`.

## 10. Sources officielles et traçabilité (consultées le 29 octobre 2026)

- Cricut Explore 5, procédure Print Then Cut, `Flat Graphic`, impression A4 portrait puis placement A4 **paysage** sur tapis, flèche en haut à gauche, même session Design Space, et bleed : https://help.cricut.com/hc/fr/articles/38613592650903-Comment-imprimer-puis-d%C3%A9couper-avec-la-Cricut-Explore-5
- Cricut, import raster PNG vs SVG vectoriel et options Flat Graphic : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- Cricut, bleed/Flatten et Print Then Cut : https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space
- Cricut, zone de découpe non rectangulaire, dépendant de la taille et de la forme : https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut
- Cricut, calibration Explore 5 (modifiée le 3 septembre 2026) : https://help.cricut.com/hc/fr/articles/360009424974-Calibrage-de-votre-machine-pour-l-impression-puis-la-d%C3%A9coupe

**Sources internes relues :** AGENTS.md, README, V3.3 MASTER/TRACEABILITY/COVERAGE/HERITAGE/AUDIT, ETAT_ACTUEL, lots 10–11, PROGRESS, OPPORTUNITIES, modules `prepare/production_v211/auto_hd/white_sheet/direct_import/artifact_qa/release_gate/quality_v21121` ; `main` au SHA précité. Les sources officielles n'établissent **aucune** validation physique de nos exports.

**Prochain lot 13 :** SVG vectoriel : fidélité visuelle, courbes et topologie, couches, distinction SVG d'édition vs SVG de coupe, import Design Space, éditeur non destructif et tests de chemin. Réexaminer les contradictions de seuil alpha/ICC et le coût de QA du lot 12 avant tout arbitrage final.
