# Q04M — B13 OCR : repères PNG et concurrence latest-only (14/11/2026)

**Statut : SPÉCIFICATION CANDIDATE, NON CERTIFIÉE.** Succède à Q04L. Décision : **RACCORDER / AMÉLIORER**, sans ticket V34 rétroactif ni modification de projet. Source G9/S-021/S-047, UX B13 ; dépendance B09/G6.3 **non satisfaite** et B12 distinct. Sources main lues directement : `engine/smartsvg_core/source_preview_v34.py` blob `923caa23c1f6039f26a486768032b91a71b23ebf`, `engine/smartsvg_core/native_preview_jobs_v34.py` blob `a099c31c982ff683646fcc834f9dcde3a4b717db`, tests preview blob `4bf02ec1d61c1b7657a53f034f27a9d96a172054`, tests jobs blob `f09b099ec6db275848b232bcf335c1e6736769dc`. **main@HEAD NON_VÉRIFIÉ** : un fetch par ref main donne un blob, non le SHA du commit HEAD.

## 1. Résultat de contre-expertise : deux risques qualifiés, pas fermés

`select_source_png(project)` choisit le **premier PNG** admissible de `project.sources`, non nécessairement la source explicitement sélectionnée par l'utilisateur. Il lit `source_paths` et `resources`, contrôle suffixe PNG, signature/IHDR, octets <=8 MiB, axes <=4096 px, pixels <=5 000 000, dimensions et SHA256 source. `SourcePreview` contient `status,png,source_id,width_px,height_px,subsample`. Le PNG retourné est **l'octet source original**, sans redimensionnement ; `subsample=max(1,ceil(width/480),ceil(height/235))` n'est qu'un conseil d'affichage. Donc **le repère des octets PNG et ses dimensions est établi** mais **le repère écran→PNG, EXIF/orientation et la source explicitement choisie ne le sont pas**. Ne jamais prendre une ROI de souris en coordonnées écran pour une ROI PNG. Ne pas attribuer au module une correction EXIF.

`LatestOnlyJob(read)` possède un worker `ThreadPoolExecutor(max_workers=1)`, une seule requête pending, une génération monotone, `current(version)` et `close()`. `submit(path)` annule le précédent Future, remplace le pending et publie la nouvelle génération avant annulation hors verrou ; une lecture déjà démarrée **continue** jusqu'à son terme, même si son Future est annulé/obsolète. `close()` ne bloque pas la fin du worker (`shutdown(wait=False)`). Ce contrat est suffisant pour **ne pas afficher un ancien résultat si le consommateur vérifie current**, mais **ne constitue ni annulation du calcul OCR, ni contrôle de ressources, ni synchronisation avec un second job**. Tests existants vérifient génération, annulation pending, callbacks, concurrence, remplacement d'archive ; ce sont des tests source lus, **pas des PASS exécutés dans ce cycle**.

## 2. Décisions de conception exécutables

**Décision M1 — espace canonique.** Un OCR candidat n'accepte que `VERIFIED_PNG_PX` : origine (0,0) en haut à gauche, rectangles demi-ouverts `[x0,y0,x1,y1)`, coordonnées entières, `0<=x0<x1<=width_px`, `0<=y0<y1<=height_px`. Les octets PNG vérifiés sont ceux du `SourcePreview`; la transformation d'un geste écran doit être **calculée par le viewport** à partir du zoom/subsample/pan réels et testée indépendamment. Sans mapping inverse démontré, désactiver la ROI interactive et offrir la **transcription manuelle** ; ne pas approximer. `source_id` est obligatoire ; une autre source ou un autre PNG entraîne un nouveau snapshot. Le facteur subsample n'est **jamais** appliqué aux données OCR déjà en pixels source.

**Décision M2 — provenance et identité.** Enveloppe candidate `OCRRequest/1={project_sha256,project_id,source_id,source_sha256,preview_sha256,width_px,height_px,roi_xyxy_px,coordinate_space:"VERIFIED_PNG_PX",generation_id,provider_receipt?}`. `preview_sha256=SHA256(preview.png)` calculé explicitement ; vérifier qu'il correspond au SHA de la source. L'archive SHA et l'identité du projet doivent être revérifiées **au moment d'accepter ou exporter**, pas seulement à l'ouverture. SHA/CAS ne verrouille pas le fichier : si remplacement entre contrôle et publication, invalider la proposition et laisser le projet inchangé. Aucun TextNode, writer, ressource ou masque float32 V1 ajouté.

**Décision M3 — jobs et ressources.** Ne pas détourner le `LatestOnlyJob` de preview : garder sa responsabilité unique. Le futur orchestrateur OCR, s'il est approuvé, dispose de sa propre génération et d'une annulation coopérative vérifiable. À chaque livraison OCR, la UI valide simultanément `preview_generation`, `ocr_generation`, `project_sha256`, `source_id`, `preview_sha256`, `roi` et l'état de fermeture. Tout décalage => `STALE`, aucun overlay, aucune écriture. La fermeture doit invalider les générations et éviter les mutations Tk après destruction. Un worker bloqué ne doit pas permettre une accumulation illimitée de requêtes ou de VRAM ; les budgets et délais sont à mesurer. Aucun appel Tk dans les workers.

**Décision M4 — interaction.** Novice : projet→PNG vérifié→ROI (si mapping testé)→manuel ou consentement OCR local→proposition visible→correction→approbation segment par segment→copie/export externe. Expert : SHA/source/repère, fournisseur/licence/hash et avertissements. Une barre contextuelle unique, clavier/focus et Undo local de correction ; états `EMPTY/PREVIEW_READY/ROI_READY/RUNNING/PROPOSED/REVIEWED/STALE/CANCELLED/FAILED`. Le bouton d'export reste inactif si segments non revus. Sans fournisseur installé, **aucun téléchargement silencieux**, aucun GPU exigé. Pas de garantie d'exactitude OCR ni d'équivalence CPU/GPU. 1366×768/DPI 200 %, contraste, motion réduite à qualifier Windows.

**Décision M5 — sortie et frontières.** Sortie de transcription hors archive, atomique, no-clobber et sans EXIF ; ne pas confondre texte OCR et texte éditable G6.3. Les quatre exports natifs restent distincts : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. Design Space/coupe physique sont **N/A pour la transcription isolée**, obligatoires si une future chaîne utilise le texte en fabrication. Le port source PNG n'est pas un export Cricut.

## 3. TDD et scénarios de qualification — tous NOT_RUN

| ID | Stimulus et oracle |
|---|---|
| M-P01 | PNG 1000×400, `subsample=3` ; ROI canonique reste en pixels PNG 1000×400, pas pixels écran |
| M-P02 | Source PNG SHA/dimensions valides ; sortie OCR éphémère, projet V1 byte-identique |
| M-P03 | Deux sources PNG ; source_id explicitement choisie ou refus si sélection ambiguë, jamais substitution silencieuse |
| M-N01 | ROI écran sans mapping inverse prouvé => commande OCR ROI désactivée, fallback manuel |
| M-N02 | x0 négatif, x1>width, rectangle vide => rejet sans lancer worker |
| M-N03 | Nouveau projet même project_id mais SHA différent => résultat stale rejeté |
| M-N04 | Preview génération n+1 pendant OCR n => résultat OCR ignoré |
| M-N05 | OCR generation n+1 et vieux callback n => aucun overlay |
| M-N06 | close() pendant OCR actif => aucune mutation Tk après fermeture, travail résiduel borné |
| M-N07 | Source corrompue, >8MiB, >5Mpx ou SHA divergent => refus avant OCR |
| M-N08 | Refus de consentement, modèle absent, licence/hash manquants => manuel, zéro réseau |
| M-N09 | OOM GPU ou annulation tardive => proposition non publiée, CPU/manuel explicite |
| M-N10 | Disque plein, collision cible, crash staging => ancien export inchangé, aucun résidu publié |
| M-N11 | Texte OCR incertain/glyphes manquants => avertissement et validation humaine, jamais substitution directe |
| M-N12 | Deux fenêtres ou source remplacée pendant validation/export => CAS échoue sans écriture projet |

Micro-lots **futurs, non implémentés ici** : T1 test inverse viewport→PNG sur pan/zoom/subsample ; T2 contrat `OCRRequest/1` et fixtures synthétiques ; T3 garde d'identité composite et stale ; T4 manuel/Undo ; T5 fournisseur local opt-in ; T6 export externe atomique ; T7 Windows UI/DPI, CPU/GPU mesurés et reprise. DoD : tous négatifs pertinents PASS non-skip + Windows réel séparé + aucun changement V1 ; aucun statut `REVU` avant contre-expertise des consommateurs viewport au HEAD.

## 4. Audit hostile des 25 axes R3

01 24 lots hérités intacts, décision ciblée ; 02 S-021/S-047 et G6.3 maintenus ; 03 140 tickets inchangés ; 04 B13 non certifié ; 05 437 scénarios historiques non exécutés ; 06 sources blobs vérifiés, main HEAD non vérifié ; 07 V1/CAS/float32 préservés ; 08 quatre exports distincts ; 09 machine N/A à l'OCR isolé ; 10 novice/expert explicités ; 11 ROI/Undo éphémères ; 12 DPI/focus tests Windows à faire ; 13 stale/close/crash/concurrence spécifiés ; 14 IA locale opt-in + manuel ; 15 limites PNG et orientation ; 16 géométrie SVG N/A à OCR isolé ; 17 Fabrique/CSV N/A au port OCR ; 18 Smart Delivery N/A à transcription isolée ; 19 aucune proposition #141 supprimée ; 20 mesures latence/RAM/VRAM à définir par fixtures, non relevées ; 21 confidentialité/licence ; 22 branche documentaire uniquement ; 23 réutiliser source preview, aucun second writer ; 24 pas de promotion ni modification AGENTS ; 25 contrat R3 non raccourci. **Audit de fiche PARTIEL**, certification de campagne ouverte.

**Couverture historique NON RECALCULÉE :** 24/141/140/80/437 inventoriés ; 431/437 liens TEST→TICKET historiques ; 6 exceptions ; 10 exigences G6/G9 sans ticket V34 direct ; 0/80 UX certifiées. Nouveaux tests NOT_RUN ; Windows/GPU/Design Space/physique NOT_RUN.

**Prochaine action UNIQUE Q04N :** lire `NativeImageViewport` et son consommateur Tk au blob exact, établir formule et tests de transformation écran↔PNG avec pan/zoom/subsample et arbitrer si B13 peut exposer une ROI sûre sans nouveau store.
