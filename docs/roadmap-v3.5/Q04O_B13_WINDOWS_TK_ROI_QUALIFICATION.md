# V35-Q04O — Protocole Windows Tk pour ROI B13 (candidate, 2026-11-14)

## Autorité, sources et limites
Statut **SPÉCIFICATION CANDIDATE, NOT_RUN**. Héritage B13, G9/S-021/S-047, lot 12, Q04L–Q04N, sans ticket V34 ajouté. Sources relues : `engine/native_image_viewport_v34.py` blob `5f2a8bb1c85cf501d8bfd521a862c0e8e1ad0110`, Q04N blob `8b4b114bb8d15a50b628e201c9cfcec41bf8eed4`, contrat R3 blob `dd9b9d1051807239419ad5a989533f70017466b4`. Une recherche de commits révèle `0692f804ad21bd775cd0269dd92dc6e2b1cea01f` (packaging Windows #145), mais **main@HEAD NON_VÉRIFIÉ par lecture directe de ref** : ne pas assimiler recherche globale à HEAD. Aucun essai Windows exécuté ici.

## Contre-expertise : contradiction concrète à résoudre
Le port réel crée une image Tk à `(0,0)`, anchor `nw`, avec `subsample(k)`; `fit_scale=None` signifie 100 %. `scan_dragto` et les flèches déplacent le Canvas, `_show` supprime/recrée les items et restaure le centre approximativement. **L'item n'a pas d'ID conservé dans l'objet**, le code n'a pas de compteur de révision et `canvasx/canvasy` ne sont pas exposés en API. En conséquence, Q04N donne une hypothèse géométrique, pas un mapping certifié. Il faut distinguer `subsample(k)` (sélection d'échantillons) de couverture de pixels originaux ; la sélection ROI est un intervalle spatial, pas une liste des seuls pixels affichés. Toute précision inférieure à k pixels source est impossible au pointeur seul sans zoom 100 % ou saisie numérique.

## JTBD et décision
Novice : délimiter du texte visible, vérifier la zone source, corriger avant OCR ; expert : inspecter source/SHA, unités et rectangle canonique. Décision **AMÉLIORER** le viewport existant par un port lecture seule *après qualification*, et **REPORTER** le moteur OCR tant que ROI/source n'est pas démontrée. Alternative acceptable : OCR de la source entière après consentement séparé ou transcription manuelle. Rejet : second Canvas/store, crop sur miniature, migration Qt sans benchmark, écriture de TextNode dans .smartsvg V1.

## Oracle géométrique et états
Définir l'entrée future comme `(source_width_px,source_height_px,display_width_px,display_height_px,k,canvas_item_bbox,canvasx(event.x),canvasy(event.y),source_sha256,preview_generation,viewport_revision)`. Toutes dimensions sont entiers strictement positifs ; coordonnées Canvas flottantes en pixels logiques Tk. À 100 %, k=1 même si `fit_scale=None`. Le rectangle de sortie `[x0,y0,x1,y1)` est en pixels de **PNG original vérifié**, avec `0<=x0<x1<=W`, `0<=y0<y1<=H`. La transformation proposée est `u=canvasx(ex)-item_x`, `v=canvasy(ey)-item_y`, puis multiplication par k et bornage. **L'oracle ne doit pas supposer `ceil(W/k)` sans mesurer le PhotoImage réel** ; lire `display.width()/height()`, tester notamment `W=1001,k=3` et le bord droit. Pour chaque point intérieur d'une cellule affichée, comparer les coordonnées calculées à un damier source synthétique indexé ; pour un rectangle, comparer l'ensemble de pixels source couvert à l'intervalle attendu, non à la seule couleur échantillonnée. Si ambiguïté au dernier pixel ou arrondi Tk, état `MAPPING_UNVERIFIED`, aucune ROI OCR.

États : `EMPTY → READY → SELECTING → ROI_REVIEW → CONSENT_PENDING → OCR_PENDING → PROPOSED → REVIEWED`; toute mutation source, viewport, DPI, fermeture ou génération rend `SELECTING/ROI_REVIEW/OCR_PENDING → STALE`. `Escape` ramène à READY sans mutation ; Undo local retire la sélection, non le masque ni l'historique V1. La commande de commit OCR ne peut exister avant validation humaine et reste export externe ; projet V1 byte-identique.

## Protocole de qualification reproductible Windows (à exécuter, pas exécuté)
Enregistrer Windows version/build, Python/Tk patchlevel, SHA de code, DPI effectif 100 % et 200 %, dimensions Canvas réelles après `update_idletasks`, dimensions PNG, `PhotoImage.subsample`, `canvas.coords(image_item)`, `xview/yview`, `canvasx/canvasy`, facteurs k, événements press/release, résultat et capture locale anonymisée. Exécuter sur runner Windows natif avec écran virtuel/affichage réellement disponible ; **un skip Tk ou un faux Canvas ne vaut pas PASS UI**. Fixtures uniquement synthétiques : damier avec coordonnées codées, bordures 1 px, alphabet libre de droits, W/H (960,470), (1001,701), (4096,1221), ROI à zéro et à dernière colonne. Pas de contenu utilisateur ni données OCR personnelles dans le dépôt.

**Cas positifs à instrumenter** :
- W01 : k=1, origine (0,0), point (10,20), ROI [10,20,30,40), oracle source exact.
- W02 : k=2, W=960 H=470, sans scroll ; point (10,20) → (20,40) seulement si Canvas/item mesurés concordent.
- W03 : k=3, W=1001, vérifier largeur affichée réelle, dernier échantillon et ROI touchant bord droit, avec borne exclusive ≤1001.
- W04 : pan par `scan_dragto`, xview/yview non nuls ; mêmes pixels source sous deux positions visuelles calculées par `canvasx/canvasy`.
- W05 : zoom 100 % → fit → 100 %, centre conservé selon contrat existant ; aucune ROI ancienne réutilisée.
- W06 : saisie clavier numérique d'une ROI source avec x/y/largeur/hauteur ; même oracle sans souris, focus visible.
- W07 : 1366×768 et DPI 200 %, texte/contrôles accessibles sans chevauchement, mouvement réduit et contraste contrôlés.

**Cas négatifs et récupérations** :
- N01 : press, puis pan/zoom/resize avant release → STALE, aucune proposition.
- N02 : item supprimé/recréé par `_show` pendant capture → invalidation même si SHA identique.
- N03 : point hors image, rectangle vide, négatif, NaN/infini, inversion, overflow → erreur typée sans crop.
- N04 : W=1001,k=3, dernier pixel tronqué ou arrondi indécidable → désactivation ROI, fallback explicite.
- N05 : changement de source/SHA/preview_generation ou conflit CAS → rejet, aucune écriture.
- N06 : fermeture de fenêtre, callback tardif OCR ou Canvas détruit → aucune commande Tk post-destruction.
- N07 : geste gauche en mode pan/ROI simultané → exclusivité vérifiée, aucun déplacement inattendu.
- N08 : échec disque/permission/collision export → staging externe nettoyé, no-clobber, V1 byte-identique.
- N09 : modèle OCR absent, licence inconnue, téléchargement refusé ou OOM → transcription manuelle ; aucun réseau silencieux.
- N10 : DPI modifié en cours de capture ou focus perdu → annulation, sans résultat stale.
- N11 : deux requêtes OCR concurrentes inversent leur ordre de retour → seule génération+SHA+ROI courante peut être proposée.
- N12 : source PNG malformée/surdimensionnée → refus avant allocation Tk ; aucun contournement des quotas existants.

## Mesures et gates
Mesurer temps de mapping p50/p95 sur W01–W07, pic mémoire avec k=1/2/3, nombre de callbacks Tk tardifs et précision des bornes en pixels source. Aucun seuil empirique déclaré atteint. Enregistrer PASS/FAIL/SKIP/NOT_RUN **par cas**, SHA, système et artefact de preuve. Tests CPU mathématiques ne certifient pas Tk Windows. GPU **N/A** au mapping seul ; Design Space et coupe physique **N/A** à ROI/OCR isolés, exigés séparément si l'export rejoint la fabrication. Les quatre sorties PNG Print Then Cut / SVG Basic Cut / SVG CUT multicouche / SVG d'édition restent des contrats séparés et non qualifiés ici.

## Micro-lots TDD proposés et DoD
T1 fixtures et oracle mathématique ; T2 harness Tk Windows et traces W01–W07/N01–N04 ; T3 port de conversion lecture seule avec compteur de révision et identité item ; T4 UI ROI exclusive, clavier, Escape/Undo ; T5 CAS, latest-only et destruction ; T6 OCR facultatif + manuel ; T7 export externe atomique. **Ordre strict : T2 doit exposer les écarts avant T3 ; aucun code développé par cette mission.** DoD de Q04O documentaire : protocole reproductible, ambiguïtés marquées, sources vérifiées, 25 axes examinés ; DoD produit : PASS Windows non-skip et revue indépendante au SHA exact, pas obtenu.

## Revue hostile et 25 axes R3
01 lots conservés (aucune requalification globale) ; 02 G9/S-021/S-047 ouverts ; 03 aucun ticket V34 créé ; 04 B13 non certifié ; 05 437 scénarios planifiés ≠ tests ; 06 main HEAD non vérifié, preuves de blobs seulement ; 07 V1/CAS/float32 intacts ; 08 quatre exports distincts ; 09 machine N/A ROI isolée ; 10 novice/expert et fallback ; 11 geste/canvas/Undo local ; 12 Windows/DPI/clavier/focus ; 13 stale/crash/concurrence ; 14 IA facultative/licence/CPU manuel ; 15 PNG original/ICC/EXIF non modifiés, dimensions bornées ; 16 topologie vectorielle N/A ROI ; 17 Fabrique/CSV N/A ROI ; 18 Smart Delivery N/A transcription seule ; 19 #141 préservée sans nouveau ticket ; 20 métriques protocolées non inventées ; 21 privacy et fixtures synthétiques ; 22 branche documentaire seule ; 23 viewport unique réutilisé ; 24 aucune promotion/merge ; 25 contrôle non-régression explicite. Contre-argument majeur : l'oracle k×coordonnée ne garantit pas le pixel sous le curseur au bord d'une image subsamplée ; **bloquer la certification tant que W03/N04 ne passent pas**.

Couverture héritée **non recalculée** : 24/141/140/80/437 identifiants historiques, 431/437 liens TEST→TICKET explicites, six exceptions, dix exigences G6/G9 sans ticket direct, 0/80 UX certifiées. Tous nouveaux tests NOT_RUN.

**Prochaine action UNIQUE Q04P :** auditer les tests Tk existants `tests/test_v34_native_image_viewport.py` au blob exact et construire une matrice de réemploi W01–W07/N01–N12, en distinguant ce qui tourne réellement sur Windows de ce qui est simulé.
