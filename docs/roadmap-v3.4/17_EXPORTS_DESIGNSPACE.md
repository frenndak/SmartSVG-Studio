# SmartSVG V3.4 — Lot 17/24 : quatre exports distincts et transfert guidé Design Space

**DRAFT documentaire — 29 octobre 2026.** V3.3 reste **ACTIVE**. Coordination [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72), [PR draft #73](https://github.com/frenndak/SmartSVG-Studio/pull/73). Ce lot affine **F05/F06/F07/F10/F14/F15, P01/P02/P06/P09, G4/G5** sans fonction ni gate supplémentaire. Aucune écriture moteur, aucune intégration Cricut automatisée. **Toutes les recettes ci-dessous sont NON_EXECUTE.**

## 1. Contre-expertise du lot 16 et trois écarts réels dans le code

1. **Quatre contrats métier ≠ quatre valeurs `Artifact.use` actuellement sérialisables.** `engine/smartsvg_core/project_contracts.py:150` n'autorise dans `smartsvg-project/1` que `print_then_cut_png`, `basic_cut_svg`, `editable_svg` ; `project_archive.py:503-511` valide ces mêmes familles. Le **SVG Cut multicouche**, explicitement exigé par V3.3, ne doit donc **ni** être étiqueté `editable_svg` pour contourner le schéma, **ni** injecter une quatrième valeur dans V1. Le livrer comme projection externe typée dans le paquet de sortie, avec provenance, puis préparer une évolution de schéma explicite et réversible si sa persistance interne devient nécessaire. Les quatre contrats utilisateur restent disponibles et distincts ; seul le stockage interne V1 est limité.
2. **Le SVG diagnostic ne constitue pas le parcours Print Then Cut.** `engine/production_v211.py` peut produire PNG et SVG de contrôle à partir de l'alpha ; `engine/smartsvg_cricut/direct_import_v218.py:194` prépare des PNG et un guide, et interdit déjà de superposer le SVG contour comme une deuxième découpe. Pour P01, le livrable transféré est **un PNG imprimable** et sa découpe est configurée dans Design Space. Aucun « SVG de contour joint » n'est supposé être automatiquement associé à ce PNG. Le guide doit préciser l'orientation A4 particulière à l'Explore 5 et le fait que **l'upload initial dans Design Space nécessite Internet**, même si SmartSVG fonctionne localement.
3. **Les prévols et la copie ne forment pas un commit projet unique.** `cricut_preflight_v205.py` est un audit indicatif, `direct_import_v218.py` copie sans remplacer silencieusement les fichiers existants, et `project_archive.py` gère séparément l'archive `.smartsvg`. Le futur paquet de transfert doit conserver la même discipline : fichiers dérivés immuables, hashes, manifeste publié en dernier, échec partiel signalé, **aucune mutation du projet en cas d'export échoué**. Ne pas ajouter un second moteur d'export, de prévol ou de persistance.

**Dépendance vérifiée :** le patron du lot 16 (140 × 110 mm, 5 CUT et 8 SCORE) reste une fixture **de spécification**, pas une exportation déjà testée. Le présent lot n'affirme ni transfert de SCORE depuis SVG ni fabricabilité réelle des fentes.

## 2. Contrats de sortie conservés, sans confusion

| Contrat approuvé | Source et projection | Artefact externe / usage | Contrôles nécessaires | Ce que le fichier ne garantit PAS |
|---|---|---|---|---|
| **PNG Print Then Cut** (F07/P01) | Rendu raster RGBA/alpha validé ; bordure et résolution définies | `.png`, import comme **Flat Graphic** dans Design Space | dimensions physiques cibles, PPI explicite, transparence/halos, composition, orientation A4 et prévisualisation Design Space | ni marques capteur Cricut préfabriquées, ni découpe de contour SVG séparé, ni coupe validée |
| **SVG Basic Cut** (F06/P02) | silhouette topologique, trous/contours validés | `.svg` monochrome de découpe | `width/height` en mm, `viewBox`, chemins fermés, doublons, XML sûr, limites de complexité | couleurs d'origine, éditabilité couleur, matériau ou coupe garantie |
| **SVG Cut multicouche** (F06/F13/P09) | plusieurs groupes de chemins CUT avec identités et repères conservés | `.svg` à couches de découpe ; manifeste externe associant groupe/matière/couleur | ordre et transformations explicites, unité commune, absence de fusion silencieuse, nombre de chemins, guides d'alignement | transmission automatique d'outils, matières ou opérations ; enregistrement en `Artifact.use` V1 |
| **SVG d'édition** (F05/P06) | courbes, formes, couches et styles d'édition autorisés | `.svg` artistique/éditable, profil distinct | fidélité de style et structure, sécurité SVG, signalement des éléments non portables | compatibilité automatique Basic Cut ou possibilité de modifier des pixels comme des objets vectoriels |

**Invariant :** le choix du contrat précède le sérialiseur. Une extension `.svg` ne suffit jamais à identifier le contrat. Un SVG artistique non conforme au profil Cricut n'est pas automatiquement réécrit en SVG Cut. La source historique, les masques float32 et les `Subject` existants restent inchangés.

### Fabrication sémantique (lots 14–16) : couche supplémentaire, pas cinquième format

Les assignations `CUT/SCORE/DRAW/PRINT/FOIL` restent **dans le plan de fabrication** et dans le guide de transfert ; le SVG est une **projection géométrique**. Les groupes SCORE/DRAW/FOIL sont identifiés pour l'utilisateur, mais **Design Space importe les vecteurs comme lignes de coupe** : il faut sélectionner l'opération souhaitée, puis **Attacher** au groupe CUT pour conserver les positions relatives. `PRINT_THEN_CUT` est une intention composite d'impression + découpe, pas une trajectoire machine transmise. Le transfert n'est ni un driver, ni un script d'automatisation de Design Space.

## 3. Parcours utilisables et états UI

**Novice — 12 escargots → stickers.** Express → « Exporter » → choix **Stickers / Print Then Cut** → aperçu de la planche et dimensions → prévol indicatif → export PNG + guide → « Ouvrir le dossier » → importer le PNG en **Flat Graphic** dans Design Space, confirmer l'aperçu Print Then Cut et la taille, puis suivre le flux d'impression **dans Design Space**. Pour A4 sur Explore 5, le guide rappelle l'orientation **paysage sur le tapis**, flèche de repère en haut à gauche ; ne pas créer soi-même les repères de capteur. Les 12 escargots peuvent être préparés par lots, sans imposer un tenseur de 50 masques ni une segmentation IA réussie. Si une zone de coupe ou une capacité machine reste inconnue, afficher « Export brouillon — taille à vérifier dans Design Space ».

**Novice — boîte → Score + Basic Cut.** Fabrique → patron 80 × 50 × 30 mm / languettes 10 mm → aperçu 140 × 110 mm → export de **géométrie CUT + groupes de plis identifiés**, guide français ; après import du SVG, sélectionner les **8 plis**, choisir **Score**, sélectionner plis + coupe, **Attacher**, contrôler les dimensions, le tapis, le matériau, puis suivre les changements d'outil. Les **4 fentes CUT ouvertes** restent signalées pour essai : ni le prévol ni le SVG ne certifient la qualité de coupe.

**Expert.** Dans l'inspecteur existant : choisir explicitement le profil d'export, afficher groupes/IDs, unité et dimensions, digest du projet, budget de chemins, profils machine/matière et avertissements ; obtenir la liste des artefacts et SHA de sortie. Un changement de masque, de chemin, de matériau ou de profil après prévol invalide le prévol **concerné** ; ne pas invalider des sorties indépendantes sans raison.

**Wireframe textuel (réutilisation de l'écran existant) :**

```text
[Exporter]  Usage : (•) Stickers PNG  ( ) SVG Basic Cut
                     ( ) SVG Cut multicouche  ( ) SVG d'édition
Source : projet@SHA…  | Dimensions : [ 140 × 110 mm ]  | Profil : Explore 5 / inconnu
[Aperçu]  [Prévol : avertissements, aucune certification]
[Exporter brouillon] [Voir les étapes Design Space]
Résultat : 2 fichiers vérifiés / 1 guide / import Design Space : NON VÉRIFIÉ
[Ouvrir le dossier] [Copier le chemin] [Retour au projet]
```

**États :** `READY_TO_EXPORT` (prévol local sans erreur bloquante), `EXPORTED_UNVERIFIED` (fichiers créés, import externe inconnu), `EXPORT_PARTIAL` (fichiers déjà publiés intacts, manifeste de succès non publié), `EXPORT_FAILED` (source inchangée), `STALE_PREFLIGHT` (recalcul nécessaire). Jamais `READY_TO_CUT` sur simple succès de génération.

## 4. Autorité, interfaces et dépendances minimales

**Réemploi impératif :** `engine/production_v211.py` pour PNG/rendu historique, `engine/smartsvg_cricut/direct_import_v218.py` pour copie protégée et guide de transfert PNG, `engine/cricut_preflight_v205.py` pour QA indicative, `engine/web/js/smartsvg_cut_review_model_g27.mjs` pour son **sous-ensemble** d'inspection SVG (64 chemins, 1–300 mm ; ce n'est ni un exporteur général ni la limite de la machine), `engine/smartsvg_core/project_contracts.py` / `project_archive.py` / `project_recovery.py` pour autorité, SHA et récupération. Les propositions des lots 13–15 fournissent les projections et la sémantique **sans prétendre qu'elles existent déjà en code**.

**Interfaces minimales pressenties** (signatures conceptuelles, pas API existante) : `export(snapshot, contract, options) -> StagedArtifact[]` ; `preflight(snapshot, contract, profile) -> Report` ; `handoff(artifacts, assignments, profile) -> Guide`. Une seule orchestration d'export relie les modules actuels. Ne pas créer de base d'artefacts, de store UI ou de service de prévol parallèle.

**Obligatoires avant un export publiable :** source/projet et SHA vérifiés ; contrat choisi ; géométrie/raster contrôlés selon ce contrat ; dimensions et unité connues ; destination sûre ; vérification des bytes écrits. **Parallélisables :** retouches G3.3e-b2a, IA/ComfyUI, UI autonome, projet V2, bus de commandes V3.4, profils matériels avancés et planches 50 sujets. Ils ne bloquent **pas** les tests des quatre formats sur fixtures synthétiques. Les gates de fabrication G4/G5 restent exigés avant toute revendication de compatibilité physique.

**Persistance et concurrence :** snapshot immuable + SHA du projet au début, recalcul du SHA avant publication pour refuser un résultat périmé ; exports en fichiers externes nommés de manière stable et sans collision, vérifiés par SHA. Si le projet a changé, refuser la publication comme export « courant » ou le classer explicitement « basé sur ancienne révision », **jamais** l'associer silencieusement à la nouvelle. L'Undo ne supprime pas un export déjà publié. Le format `smartsvg-project/1` n'est pas modifié ; les quatre contrats de sortie sont des projections externes, et l'enregistrement de nouvelles métadonnées dans V1 reste interdit sans migration approuvée.

**Publication de paquet :** staging dans un dossier temporaire privé sur le même volume, validation de chaque artefact, puis publication sans remplacement de fichier différent. Manifeste/guide **après** les artefacts, avec statut `EXPORTED_UNVERIFIED`. En cas d'interruption, aucun manifeste « succès » n'est publié pour un paquet incomplet ; les fichiers déjà créés sont identifiables et ne sont pas effacés arbitrairement. Un ensemble de fichiers n'est **pas** une transaction atomique du système de fichiers : ne pas le promettre. Le paquet n'est pas une deuxième source de vérité du projet.

**Provenance minimale du manifeste externe :** `contract`, `source_project_sha256` ou empreinte d'entrée synthétique, `artifact_sha256`, `size_mm`, `profile_ref` si connu, `preflight_status`, `proof_axes` tous `NON_EXECUTE` initialement, `handoff_steps` et `warnings`. Les chemins absolus privés, captures utilisateur, poids IA et données sensibles n'ont pas leur place dans un dépôt public. Le manifeste externe n'est ni signé ni certifié par défaut.

## 5. Erreurs, rollback et règles de prévol

| Code proposé | Déclencheur | Réaction française / rollback |
|---|---|---|
| `EXPORT_CONTRACT_MISMATCH` | PNG demandé comme SVG éditable, ou multicouche classé Basic Cut/V1 | « Ce format ne conserve pas les mêmes informations. Choisissez le bon usage. » Aucun fichier publié. |
| `EXPORT_SVG_UNSAFE` | XML actif, ressource distante, géométrie ambiguë ou budget dépassé | Refuser la projection de coupe, conserver source et brouillon. |
| `EXPORT_SIZE_UNKNOWN` | mm/PPI absents ou incohérents | « Indiquez une taille physique avant d'exporter. » Pas de taille inventée. |
| `STALE_PROJECT_SHA` | projet changé depuis snapshot/prévol | « Le projet a changé ; relancez le contrôle. » Aucun écrasement. |
| `EXPORT_DESTINATION_CONFLICT` | chemin existant avec autre contenu, lien symbolique ou permission insuffisante | « Choisissez un autre dossier ou nom. » Ne pas remplacer l'ancien. |
| `EXPORT_PARTIAL` | interruption pendant paquet multi-fichiers | Garder artefacts validés, signaler absence de manifeste final, reprise explicite. |
| `HANDOFF_OPERATION_REQUIRED` | Score/Draw/Foil non assigné dans Design Space | Guide « choisir l'opération puis Attacher » ; pas de statut fabriqué. |
| `CAPABILITY_UNKNOWN` | profil matière/outil/zone non qualifié | Export brouillon possible ; aucune déclaration « prêt machine ». |

**Prévol ciblé :** XML SVG sûr, `width/height/viewBox` et mm, contours/trous, microformes et doublons, groupes CUT distincts des plis, raster RGBA/alpha/halo, dimensions/PPI, provenance. Les valeurs de pression, tolérances d'épaisseur, marge A4 universelle et calibrage machine **ne sont jamais déduits**. L'absence de preuve Design Space/physique reste visible après l'export.

## 6. Tests d'acceptation à implémenter — TOUS NON_EXECUTE

| ID | Assertion observable | Axe de preuve futur |
|---|---|---|
| T-V34-17-01 | Les quatre choix exportent des contrats distincts ; le SVG multicouche n'est jamais stocké sous `Artifact.use=editable_svg` V1 | auto |
| T-V34-17-02 | Un PNG Print Then Cut conserve pixels/alpha/empreinte ; aucun SVG de diagnostic n'est automatiquement ajouté comme seconde coupe | auto |
| T-V34-17-03 | Basic Cut refuse trou ambigu, contour ouvert non autorisé, double coupe, SVG actif et dimensions non physiques | auto |
| T-V34-17-04 | SVG multicouche conserve ordre, groupes, repère mm et IDs ; aucune conversion silencieuse en SVG d'édition | auto |
| T-V34-17-05 | SVG d'édition conserve styles/couches dans le profil autorisé ; pas de mention « Basic Cut prêt » | auto |
| T-V34-17-06 | Fixture boîte 140×110 : 5 CUT/8 SCORE identifiés, guide « Score → Attacher → vérifier mm/outils » ; aucune opération transmise par SVG | auto/UI |
| T-V34-17-07 | Stale SHA entre prévol et publication → refus sans mutation du projet ni remplacement d'un export antérieur | auto/concurrence |
| T-V34-17-08 | Échec au 2e artefact d'un paquet → manifeste succès absent, ancien paquet intact, reprise sans écrasement | auto/fault-injection |
| T-V34-17-09 | Guide A4 Explore 5 : paysage sur tapis, flèche haut-gauche, repères imprimés par Design Space, dimensions à confirmer | auto/UI |
| T-V34-17-10 | Novice clavier : choisir chacun des quatre formats, voir avertissements et ouvrir résultat sans perte de focus | UI/Windows |
| T-V34-17-11 | Import réel PNG Flat Graphic + SVG Basic/MultiCut : version Design Space, dimensions, calques et comportement constatés | DesignSpace |
| T-V34-17-12 | Import réel boîte : Score et Attacher manuels, outil/matière et positions vérifiés, capture privée de preuve | DesignSpace |
| T-V34-17-13 | Coupon Explore 5 : sticker et boîte testés, mesures et matière/outils/tapis/versions/SHA consignés | physique |

**Corpus :** fixtures synthétiques « 12 escargots », SVG à trou, SVG multicouche à deux couches, SVG d'édition à styles, boîte du lot 16, SVG malveillant/complexe, conflit de nom, coupure d'écriture, changement concurrent de SHA. Aucune image Pokémon, privée ou sous licence tierce dans le dépôt public. **DoD documentaire** : chaque test relié à un ticket et une exigence, contrats non confondus, références code réelles et preuves correctement marquées. **DoD produit futur** : assertions exécutées au SHA et à l'environnement, preuves auto/Windows/Design Space/physique séparées.

## 7. Micro-tickets réellement nécessaires (nouveaux IDs, sans nouveau périmètre)

| Ticket | Dépendances et livrable envisagé | Tests / preuve / DoD / rollback |
|---|---|---|
| **V34-129 P0** — projection des quatre contrats approuvés | S-002/029/030/032/075, R33-008, V34-100/101 ; **adapter** `production_v211.py`, `direct_import_v218.py` et les profils SVG du lot 13 ; éventuel routeur léger **futur** `engine/smartsvg_cricut/export_contracts.py` seulement si nécessaire | T01..05 ; auto, Design Space ultérieur ; DoD quatre projections distinctes, V1 non élargi ; rollback exporters historiques conservés |
| **V34-130 P1** — guide de transfert par opération | S-076/084, R33-022/034, V34-111/120/121/128 ; **réutiliser** `LIRE_AVANT_IMPORT.txt` et panneau Export existant, sans driver ni second assistant | T02/06/09/10/11/12 ; auto/UI/Windows/DesignSpace ; DoD guide FR, Score/Draw/Foil/Attach manuels, A4 précis ; rollback guide historique |
| **V34-131 P1** — provenance et reprise d'export sans écrasement | S-017/042/095, R33-025/027, V34-014/024 ; **réutiliser** SHA du projet, `direct_import_v218.py` et `project_recovery.py`, sans nouveau store | T07/08/11/13 ; auto/fault-injection, terrain ultérieur ; DoD SHA source+sortie, collision et panne récupérables, aucun faux succès ; rollback export brouillon simple |

**Mapping inverse local :** T01→129 ; T02→129/130 ; T03→129 ; T04→129 ; T05→129 ; T06→130 ; T07→131 ; T08→131 ; T09→130 ; T10→130 ; T11→129/130/131 ; T12→130 ; T13→131. Les 141 S/R33 restent dans [HERITAGE_INDEX](HERITAGE_INDEX.md), matrice bidirectionnelle finale au lot 23 ; **aucune nouvelle dépendance bloquante pour G3.3e-b2a**.

## 8. Limites, sources et passage au lot 18

- **Arbitrage maintenu :** ne pas réécrire les exporteurs existants ; conserver quatre contrats externes distincts et la V1 stricte. Une éventuelle persistance native du multicouche relève d'une migration versionnée **à qualifier**, pas d'un prérequis caché pour G4 ni pour ce lot.
- **Documentation officielle consultée le 29/10/2026 :** [Cricut — Upload images into Design Space](https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space) (SVG importés comme lignes de coupe ; upload nécessite Internet), [Explore 5 — Print Then Cut](https://help.cricut.com/hc/en-us/articles/38613592650903-How-to-Print-Then-Cut-with-Cricut-Explore-5) (Flat Graphic, orientation A4 paysage et flèche), [Explore 5 — Scoring Tool](https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool) (Score, Attach, changements d'outil), [Design Space — Selecting Operation](https://help.cricut.com/hc/fr/articles/26922998476183-Design-Space-nbsp-S%C3%A9lection-de-l-op%C3%A9ration) (modifié 15/09/2026). Sources = comportement documenté de Design Space, **pas** preuve d'import SmartSVG ni certification physique.
- **Risques ouverts :** absence de persistance V1 pour une quatrième valeur d'artefact, reprise de paquets multi-fichiers, SVG complexe/transformations, dépendance Internet de Design Space, dimensions et A4 réels, changements de version, aucune preuve Windows/Design Space/Explore 5. Tous les tests T-V34-17-* sont **NON_EXECUTE**.
- **Prochain lot 18 :** Atelier graphique, canevas/calques/propriétés/Undo et état projet unique ; réutiliser G2/G3 et le moteur de pinceau existant, ne pas imposer V2 ou assistant IA comme prérequis aux retouches V3.3.
