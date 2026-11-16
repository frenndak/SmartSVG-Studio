# V35-Q04I — B13 OCR : matrice exhaustive lot 12, frontière de preuve et intégration candidate

**14 novembre 2026 — CANDIDAT NON NORMATIF. V3.4 ACTIVE.** Suite de Q04H. Sources lues : `docs/roadmap-v3.4/12_RASTER_PIPELINE.md` blob `30424177571a1e5c627cbdb0630c07c63ba344e0`, Q04H blob `3dd785bae320dc277925db1c819988c4006e6fa4`, PROGRESS et contrat qualité 25 axes. `main@HEAD NON_VÉRIFIÉ`. La recherche des PR via issue-search n'a pas fourni de PR code ; **absence de PR non démontrée**, leurs signatures OCR restent NON_VÉRIFIÉES.

## 1. Décision et frontières

**B13 OCR / S-021 / S-047 / G9 : RACCORDER, P2, NON CERTIFIÉ.** Le lot 12 définit neuf tickets **V34-087..095**, trente scénarios **T-V34-12-01..30**, raster/alpha/texture/Print Then Cut. Aucun ticket ne promet OCR. Le lien OCR→lot12 est une dépendance d'admission/ROI/provenance/export, **pas une couverture fonctionnelle OCR**, ni une affectation rétroactive. Le moteur OCR doit être recherché sur main et sur les PR exactes avant tout nouvel adaptateur. G6.3 texte modifiable dans le projet reste BLOQUÉ ; export-only n'est pas une substitution. Un projet `.smartsvg` V1, Subject/float32/CAS, writer historique, quatre rôles PNG PTC / SVG Basic Cut / SVG CUT multicouche / SVG édition sont intangibles.

## 2. Matrice TEST→TICKET exhaustive (liens historiques du lot 12)

| Scénario | Ticket(s) source explicitement cités | Raccordement OCR B13 candidat |
|---|---|---|
| 01 | 087,094 | SHA original immuable |
| 02 | 087,094 | EXIF et coordonnées ROI |
| 03 | 087,094 | ICC et source conservée |
| 04 | 087,094 | quota/décompression |
| 05 | 087,094 | masque float32 invalide |
| 06 | 088,095,094 | franges preview sans changement coupe |
| 07 | 088,094 | alpha de coupe immuable |
| 08 | 088,091,094 | approbation humaine |
| 09 | 088,090,095,094 | prévol multi-seuil |
| 10 | 088,090,091,094 | stale digest |
| 11 | 089,095,094 | unités mm/ppi |
| 12 | 089,091,095,094 | aucune taille garantie |
| 13 | 089,091,094 | pas de faux HD |
| 14 | 092,094 | moteur absent/refus, sans réseau |
| 15 | 092,094 | OOM et repli |
| 16 | 088,089,092,094 | texture distincte de coupe |
| 17 | 088,090,095,094 | PNG PTC, silhouette séparée |
| 18 | 088,090,094 | modification offset = nouveau prévol |
| 19 | 088,090,094 | alpha rectangle involontaire |
| 20 | 088,090,095,094 | composantes/trous |
| 21 | 093,094 | lot borné |
| 22 | 093,094 | cache déterministe |
| 23 | 093,094 | invalidation cache |
| 24 | 093,094 | tuilage/halo |
| 25 | 090,093,094 | concurrence, crash, no-clobber |
| 26 | 090,094 | chemins hostiles |
| 27 | 091,095,094 | clavier Windows |
| 28 | 090,094 | Design Space manuel |
| 29 | 094 | Explore 5 / coupe physique |
| 30 | 094 | SCORE jamais inféré du raster |

**Contrôle cardinalité :** 30/30 identifiants source présents ; 9/9 tickets V34-087..095 représentés. Les 30 liens sont **historiques**, mais aucun ne constitue un test d'OCR ; le lien OCR est seulement une proposition de consommation. Le ticket transversal V34-094 cite T01..30, ce qui n'établit pas l'exécution de trente tests.

## 3. Contrat candidat de consommation, sans API inventée

`OCRProposal/1` de Q04H consomme un `source_sha256`, une ROI en pixels **après orientation EXIF**, `expected_project_sha256`, `language_hints` et un consentement explicite ; produit segments `text_nfc`, boîtes bornées, révision et statuts `PROPOSED|REVIEWED|REJECTED|STALE`. Le texte reste une **surcouche non persistée** jusqu'à ADR V2 autorisée. L'admission réutilise conceptuellement V34-087 ; aucun appel de fonction précis n'est certifié. V34-088/090 garantissent seulement que l'OCR n'altère pas alpha/coupe ; V34-091 concerne la revue UX ; V34-092 est texture IA, **pas** moteur OCR ; V34-093 cache ROI, à ne pas réutiliser sans séparation de clé/version ; V34-094 corpus/QA, V34-095 franges. Éviter tout moteur/store parallèle. Une proposition périmée n'est ni appliquée ni exportée.

UX : novice sélectionne zone→transcription manuelle ou moteur local installé et consenti→compare original/segments→corrige→prévisualise→export externe explicite. Expert inspecte EXIF, SHA, modèle/licence, rectangles, glyphes, cache et rôle d'export. Un seul canevas, barre contextuelle, Undo/Redo de brouillon, clavier/focus/contraste/motion réduite, tests 1366×768/DPI 200 % futurs. Aucun téléchargement, réseau ou substitution muette. CPU/manuel obligatoire comme repli ; GPU 8 Go non garanti.

## 4. Critères OCR propres et tests TDD FUTURS, tous NOT_RUN

**Positifs :** P01 ROI EXIF6 remappée et source inchangée ; P02 segment accentué corrigé manuellement avant preview ; P03 sortie externe SVG édition avec police/licence/glyphes vérifiés ; P04 les quatre rôles d'export restent indépendants ; P05 refus OCR laisse PNG/masque et archive V1 inchangés.

**Négatifs :** N01 moteur absent/licence inconnue→manuel sans réseau ; N02 résultat faux à confiance élevée→jamais auto-accepté ; N03 ROI hors image/NaN/quotas→refus ; N04 changement source/ICC/EXIF/projet pendant traitement→STALE ; N05 glyphes/RTL non pris en charge→bloquer fidélité ; N06 DTD/XXE/script externe→refus ; N07 annulation puis réponse tardive→ignorée ; N08 deux exports même nom→no-clobber ; N09 crash/disque plein→staging nettoyé, original intact ; N10 tentative de persister TextNode V1→refus ; N11 logs de texte privé→échec confidentialité ; N12 OCR modifiant alpha CUT→prévol BLOCKED ; N13 résultat de modèle OOM→fallback manuel ; N14 import DS/physique non testé→aucune certification.

**Micro-lots candidats :** (1) inventorier ports et PR sur SHAs exacts ; (2) fixtures originales FR/RTL/EXIF et tests admission/ROI ; (3) saisie manuelle et approbation ; (4) moteur facultatif après licences/hashes ; (5) preview/Undo/stale ; (6) prévol externe et QA ; (7) UI Windows ; (8) DS/physique uniquement si fabrication concernée. DoD : aucune mutation du V1, consentement explicite, provenance, zéro faux PASS, contrôle 30/30, tests non-régression lot 12, mesures de latence p50/p95 et RAM/VRAM sur machine documentée (aucun chiffre inventé).

## 5. Revue hostile et contrôles 01–25

Alternative OCR obligatoire rejetée (licence/offline) ; texte aplati ≠ éditable rejeté (G6.3) ; OCR→CUT automatique rejeté (géométrie et sécurité) ; réutiliser V34-092 comme OCR rejeté (fonction texture différente). **Risques ouverts :** recherche des ports PR incomplète, exactitude OCR, bidi/polices, texte persistant V2 non autorisé, preuve physique absente.

01–05 inventaires historiques 24/141/140/80/437 conservés, 431/437 liens source explicites précédemment documentés, six exceptions et dix G6/G9 ouvertes ; 06 HEAD/PR non vérifiés, aucun PASS ; 07 V1/CAS/float32 préservés ; 08 quatre exports séparés ; 09 aucune machine inventée ; 10–12 novice/expert, UI/clavier/DPI à tester ; 13 stale/crash/concurrence/Undo ; 14 IA facultative, licence/consentement ; 15 EXIF/ICC/alpha ; 16 SVG sûr, unités/topologie ; 17 batch hors périmètre local, héritage conservé ; 18 Smart Delivery non modifié ; 19 autres opportunités #141 non arbitrées ici ; 20 performances seulement à mesurer ; 21 confidentialité ; 22 branche documentaire, aucun code/AGENTS/merge/automatisation ; 23 pas de doublon moteur/store ; 24 aucune promotion ; 25 profondeur et 30 liens individuels contrôlés.

**Statut : SPÉCIFIÉ PARTIELLEMENT, NON CERTIFIÉ ; tous nouveaux tests NOT_RUN, Windows/GPU/Design Space/physique NOT_RUN.** Prochaine action UNIQUE **Q04J** : obtenir la liste fiable des PR code ouvertes et lire leurs fichiers/signatures OCR, puis arbitrer l'interface d'adaptation réelle au SHA exact.
