# COV-10B — Ports réels, propriétaires candidats et contre-expertise G6/G9 (13 novembre 2026)

**Statut : AUDITÉ_PARTIEL / NON_ADOPTÉ / NOT_RUN.** Ce dossier est documentaire, n'ajoute aucun ticket V34, ne modifie pas V1, et ne remplace pas COV-10. Les références de code sont des blobs lus sur `main` via GitHub ; **main HEAD exact NON_VÉRIFIÉ** (une recherche de commits ne prouve pas le HEAD). PR #138, #139 et #140 ouvertes au moment de la lecture, toutes distinctes et hors G6/G9.

## 1. Preuves techniques réellement consultées

| Port réel | Blob SHA lu sur main | Fonction et limite observées |
|---|---|---|
| `engine/smartsvg_core/template_geometry_v34.py` | `3142c2e379fd28c2b506c343527b932780d6fcee` | `folded_card(width_mm,height_mm)`, `open_tray(base_width_mm,base_depth_mm,wall_height_mm,tab_width_mm)`; proposition `smartsvg-template-preview/1-draft`, `points_mm`, CUT/SCORE séparés, `persisted=False`; aucune écriture/export/qualification machine |
| `engine/smartsvg_core/template_preflight_v34.py` | `4cf83b1a12d0fbaa4c0f7cd52576ceb1c50434dd` | `preflight_template(proposal, usable_sheet_mm=None)` ; whitelist stricte des deux `template_id`, géométrie recalculée, limites de points, `BLOCKED`, `NOT_TESTED`, `UNKNOWN`; pas de certification physique |
| `engine/native_templates_tk_v34.py` | `1eb27f8d9947f5bd31a71ddc0c14af47e7217936` | `TemplatePreviewContent`, aperçu Tk nominal, formulaire mm, invalidation après changement, prévol manuel, aucun export ni projet modifié |
| `engine/native_app_shell_v34.py` | `b5cc4f503791d6f24ac62027323cb726973b54a2` | `NativeAppShell` propriétaire des pages/état visuel, pas de writer ni queue ; ne pas créer une seconde application |
| Recherche code `font` | index main snapshot `aa0ff9e7` | `engine/engine_v17.py` emploie PIL/DejaVuSans avec fallback, **pas** un catalogue typographique éditable prouvé |
| Recherche code `ocr` | index main snapshot `aa0ff9e7` | `engine/smartsvg_ai/routing_v21121.py` déclare explicitement **No OCR** ; aucune API OCR native qualifiée dans cet audit |

**Réserve :** absence de résultat dans la recherche n'est pas preuve d'absence exhaustive. Les ports d'édition texte, de writer V1, d'export et de géométrie générale doivent être vérifiés avant toute spécification d'intégration définitive. PR #138 : récupération UI ; #139 : statut Undo/Redo lecture seule ; #140 : viewport Tk taille nulle. Aucun n'est une implémentation OCR, polices ou diorama. Les textes de PR ne remplacent pas une lecture de diff ni des logs.

## 2. Matrice des dix exigences : décision candidate, pas adoption

| Exigence | Domaine / propriétaire candidat | Décision et garde-fou |
|---|---|---|
| S-021 | OCR guidé / nouveau port d'analyse optionnelle derrière commande explicite | **AMÉLIORER** : résultat texte proposé, jamais substitution automatique ; fournisseur OCR, licence et modèles à vérifier |
| S-036 | Typographie / modèle objet texte à identifier | **RACCORDER** : taille, alignement et typographie dans objet éditable, sans stockage parallèle |
| S-037 | Polices / service d'inspection locale candidat | **AMÉLIORER** : absence de police, glyphes, licences et fallback signalés, aucun remplacement silencieux |
| S-044 | Diorama / famille de patrons à concevoir au-dessus du prévol existant | **AJOUTER sous condition** : quatre plans avec identité, ordre, alignement et tolérances ; ne pas forcer `folded-card` ou `open-tray` à accepter des ID non reconnus |
| S-047 | OCR / même port que S-021 | **FUSIONNER au niveau technique**, conserver deux exigences et leurs critères indépendants |
| S-064 | Gabarits métiers / extension future de catalogue | **RACCORDER** : ne pas confondre gabarits étiquette/topper/carte avec les deux patrons existants |
| S-066 | Diorama quatre plans / même moteur candidat S-044 | **FUSIONNER au niveau moteur**, garder les deux preuves de couverture |
| S-092 | Typographie et texte / même modèle éditable S-036 | **RACCORDER** : historique/Undo, sérialisation et exports séparés à valider |
| S-099 | Fabrication / guide de montage candidat | **AMÉLIORER** : ordre d'assemblage et instructions dérivés de géométrie qualifiée, pas certificat machine |
| R33-028 | G6/G9 transversal / coordination texte–gabarits–diorama | **GARDER** : conserver les critères source intégraux ; le découpage ci-dessus est un regroupement d'architecture, pas un remplacement du libellé historique |

Ces regroupements sont **hypothèses de propriétaires**, non attribution de tickets V34. Relire les libellés et critères source complets avant la revue finale, en particulier R33-028. Aucun nouveau ticket n'est créé pour combler artificiellement les dix écarts.

## 3. Contrats proposés pour le développeur (non implémentés)

**Texte/OCR.** Entrée : source image identifiée par SHA/CAS, sélection ou zone bornée, langue explicitée, version fournisseur et consentement ; sortie : propositions `{text, boxes_px, confidence?, engine_id, provenance}` en **pixels source**, sans writer. Le caractère facultatif de `confidence` interdit d'afficher une confiance fictive. L'utilisateur corrige, prévisualise, puis choisit d'insérer un objet texte via le writer V1 existant **après identification de son API**. Annuler ne touche ni image ni masque float32. Si police/glyphe absent, l'état reste `UNKNOWN` ou `BLOCKED`, jamais un fallback silencieux. La conversion en chemins est une action dérivée et distincte du texte éditable.

**Gabarits/diorama.** Réutiliser la convention nominale `mm`, la séparation `CUT`/`SCORE`, le statut `UNKNOWN` machine et le prévol statique existant. Ne **pas** injecter des `template_id` dans `preflight_template` sans ADR, tests de whitelist et validation du propriétaire si contrat/sécurité changent. Pour quatre plans, proposition de contrat externe versionné `{plane_id, order, registration_marks_mm, material_thickness_mm?, paths, assembly_step}`, validation topologique, marges et alignement inter-plans ; aucune machine/épaisseur supposée. Un guide est indicatif tant que la coupe physique n'est pas mesurée.

**UX.** Réutiliser `NativeAppShell` : un atelier, une session, un brouillon Undo local, inspection de polices/texte et guide de montage contextuel, sans dix nouveaux boutons. À 1366×768 et 200 % DPI : barre contextuelle repliable, focus clavier stable, messages d'erreur textuels, pas de dépendance couleur seule, animations réduites. Ne pas annoncer les boutons avant tests Tk réels.

**Sorties.** Conserver **quatre rôles distincts** : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. OCR n'est pas un export, un aperçu n'est pas un artefact ; aucun guide d'assemblage ne transforme une validation statique en `DESIGN_SPACE_PASS` ou `COUPE_PHYSIQUE_PASS`. Aucune migration implicite du projet `.smartsvg` V1.

## 4. Tests TDD et gates, tous NON EXÉCUTÉS dans ce lot

- Positifs : insertion manuelle d'un texte OCR corrigé avec conservation source SHA ; réouverture V1 sans substitution de police ; prévol quatre plans en mm avec correspondance des repères ; guide d'assemblage dérivé des plans validés.
- Négatif 1 : police absente / glyphe non pris en charge → avertissement et absence de remplacement silencieux.
- Négatif 2 : OCR indisponible, licence refusée, téléchargement non consenti ou OOM RTX 8 Go → fallback manuel sans perte de brouillon ni requête réseau implicite.
- Négatif 3 : diorama avec plan dupliqué, ordre incohérent, trous inversés ou géométrie dégénérée → `BLOCKED`, aucun export déclaré qualifié.
- Négatif 4 : révision SHA périmée ou modification concurrente pendant prévisualisation → abandon de commit, aucun writer parallèle.
- Récupération : crash après prévisualisation mais avant confirmation → V1 intact ; crash/échec disque au commit → état vérifié par writer/CAS, résultat incertain affiché sans faux succès.
- Terrain : Windows Tk réel, Design Space version notée, Explore 5 et coupe physique mesurée sont **gates séparés**, `NOT_RUN` ici. Tests unitaires éventuels sur les ports historiques ne sont pas réexécutés dans cette contre-expertise.

Micro-lots candidats : (1) cartographie exhaustive des API V1/texte/export et consommateurs ; (2) fixtures texte/licences/glyphes + échec sans modification ; (3) proposition OCR sans writer ; (4) géométrie quatre plans et prévol indépendant ; (5) UI brouillon/Undo ; (6) exporteur existant, QA et tests physiques séparés. Chaque micro-lot exige revue contradictoire, réversibilité et DoD fondée sur un test réel non-SKIP.

## 5. Revue hostile et 25 contrôles

**Alternative rejetée :** un moteur de patron neuf ou un deuxième writer « plus simple » ; il doublerait le contrat de géométrie et l'état V1. **Alternative à étudier :** extension contrôlée des producteurs de propositions, sans élargir silencieusement la whitelist du prévol. **Risques ouverts :** licence police/OCR, caractères non latins, métriques de texte, tolérance de matière, fiabilité de l'alignement, évolution de schéma, UX DPI, tests physiques.

Contrôles 01–05 : héritage 24/141/140/80/437 conservé, aucune certification ; 06 : statuts disjoints ; 07–09 : V1/CAS, quatre exports et tri-state conservés ; 10–13 : UX/Undo/erreurs/reprise proposés, tests Tk non faits ; 14 : OCR facultatif et sans réseau implicite ; 15 : raster/float32 non modifié, non applicable au code de ce lot ; 16 : géométrie/topologie et mm à valider ; 17 : gabarits visés, bibliothèque/CSV non applicables à cette fiche ; 18 : Smart Delivery non modifié ; 19 : O-001..033 non arbitrées ici, registre global reste ouvert ; 20 : protocole de performance à mesurer, aucun chiffre inventé ; 21 : fixtures synthétiques, pas de polices/médias tiers ajoutés ; 22 : branche documentaire, pas de merge/code/AGENTS ; 23 : ports existants examinés, inventaire API incomplet signalé ; 24 : promotion conditionnelle, aucun transfert d'autorité ; 25 : contrat non réduit, preuves non extrapolées.

**Couverture documentaire historique :** 24 lots, 141 exigences, 140 tickets, 80 UX, 437 scénarios indexés ; 431/437 liens scénarios→tickets explicites, six exceptions ; dix G6/G9 sans ticket V34 direct. Aucun des dix n'est déclaré clos. Aucun PASS produit revendiqué.

**Prochaine action unique : COV-10C** — lire les APIs réelles de projet V1, objets/texte, exporteurs et tests associés, puis remplacer les propriétaires candidats ci-dessus par des ports vérifiés ou `ABSENT_NON_PROUVÉ`, sans créer de code.
