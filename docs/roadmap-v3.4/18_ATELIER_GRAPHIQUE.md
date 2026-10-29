# SmartSVG Studio V3.4 — Lot 18/24 : Atelier, canevas, calques, propriétés et Undo

**DRAFT documentaire — 29 octobre 2026.** V3.3 reste **ACTIVE** ; coordination [issue #72](https://github.com/frenndak/SmartSVG-Studio/issues/72) et [PR #73](https://github.com/frenndak/SmartSVG-Studio/pull/73). Base du code relue : `main@fff374e5147689165839bd76e742713d714ff147`, branche avant ce lot : `c7dbd7ffd0fed5c4dc56a04e77997f343384876d`. Domaine approuvé F03/F05/F08/F10/F14, P03/P05/P06/P10, G2/G3/G5/G6. **Aucune fonction supplémentaire, aucune modification du moteur.** Tout test ci-dessous est **NON_EXECUTE**.

## 1. Contre-expertise du lot 17 et trois écarts réels

1. **L'Atelier montre des sélections distinctes, pas encore un état de projet partagé.** Dans `engine/web/js/smartsvg_express_atelier_preview.html`, `selected` pilote les **12 escargots fictifs** (lignes 145–188), tandis que `chosenRealSubjects`/G3.3b et le panneau G2.2 sont chargés séparément (lignes 253–470 et 500+). Le panneau G2.2 sait enregistrer des notes sous SHA, mais sélectionner un escargot fictif ne sélectionne pas un `Subject` G1.2. **Correction :** différencier explicitement `DEMO` et `PROJECT@SHA` ; toutes les vues réelles consomment la même projection du projet et le même `subject_id`. Aucun sujet fictif ne devient une entité persistante.
2. **Le pinceau historique cible un index de tenseur, pas un sujet stable.** `engine/smartsvg_editor/strokes.py:64–143` utilise `strokes[].object` (index 0..N-1) et un tableau float32 `[N,H,W]` borné à 32. G3.3e-b1 apporte `Subject` et preuve `subject_id ↔ mask_id ↔ mask_sha256_float32` via `subject_identity_g33e.py` et `mask_binding_g33e.py`. **Correction :** l'UI sélectionne un `subject_id` ; l'adaptateur de preview résout l'index **uniquement sous révision et preuve exactes**, puis réutilise `decode/apply_strokes`. Ni PNG L8 ni position de vignette ne sont l'autorité.
3. **Enregistrer les traits ne signifie ni modifier les masques de base ni fournir Undo global.** `project_workspace_g22.py:389–445` enregistre `editor_v216` avec CAS et renvoie `base_masks_persisted:false` ; la lecture de session n'est pas un historique réversible complet. **Correction :** distinguer Annuler un brouillon local, immédiatement possible, de Undo/Redo d'un commit durable, à implémenter et qualifier avec G3.3e-b2b et V34-035/038. Le lot 17 garde les exports externes immuables : Undo ne les retire pas.

**Réconciliation lot 17 :** export sur snapshot + SHA figé, jamais sur la sélection locale non enregistrée ; PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition restent quatre contrats distincts. Les tests G4 sur fixtures peuvent progresser en parallèle de G3.3e.

## 2. Autorité, réemploi et dépendances proportionnées

| Usage | Réemploi du code existant | Obligatoire | Parallélisable / non bloquant |
|---|---|---|---|
| Projet et propriétés | `smartsvg_core/project_contracts.py` (SourceAsset/Mask/Subject/Artifact), `project_workspace_g22.py`, `project_archive.py`, `project_recovery.py`, `smartsvg_project_panel_g22.mjs` | Archive saine et SHA courant | V2, shell autonome, IA |
| Canevas/choix | `smartsvg_express_atelier_preview.html`, G3.3b/G3.3e, `smartsvg_cut_review_model_g27.mjs` | Démo/projet distincts, sélection source et échelle explicites | Nouveau framework UI, modèles IA |
| Aperçu pinceau | `smartsvg_editor/strokes.py`, `editor_session_g23.py`, `mask_snapshot_g24.py`, `mask_binding_g33e.py`, `subject_identity_g33e.py` | `subject_id`, `mask_id`, SHA masque float32, SHA projet et preuve b1 ; b2a pour preview | Exports G4, planches 50, GPU |
| Calques et opérations | `Subject` et chemins SVG G2.7 ; sémantique CUT/SCORE du lot 14, SVG du lot 13 | Types d'objets et unités explicites | Format V2 et éditeur vectoriel avancé |
| Undo persistant | `save_with_recovery`/CAS et writer existants ; V34-035/038 | Commit réellement inversible, réouverture et révision vérifiées (b2b) | Bus V2 complet et receipts universels non imposés à b2a |

**Anti-doublon :** V34-041 définit déjà la session commune ; V34-044 la récupération ; V34-045 l'accessibilité ; V34-035/038 Undo et son UI. Ne pas créer de deuxième store, bus, moteur de pinceau, writer, prévol ni exporteur. Les fichiers `v34_*` proposés ailleurs sont futurs et **ne bloquent pas** le code G3.3e-b2a en cours.

## 3. Parcours novice/expert et wireframe de référence

**Novice — 12 escargots → stickers :** Accueil/Express → importer → « Image chargée, sujets non analysés » jusqu'au diagnostic réel ; les 12 escargots d'exemple portent le bandeau « Démonstration, non exportable ». Après rattachement d'un diagnostic réel au projet et à son SHA, sélectionner la vignette d'un vrai `Subject`, enregistrer explicitement son identité si nécessaire, ouvrir Retouches, choisir Ajouter/Effacer, dessiner un geste borné, afficher original/avant/après et « Aperçu non enregistré ». Annuler sans écrire ; n'autoriser Valider qu'après raccordement et qualification b2b. Exporter ensuite le PNG Print Then Cut via le lot 17, avec prévol et guide Design Space, jamais depuis les escargots fictifs.

**Novice — boîte → Score + Cut :** ouvrir le patron paramétrique du lot 16, choisir « Coupe » ou « Plis », afficher la taille en mm, les avertissements et la légende accessible. La fixture **140×110 mm, 5 CUT/8 SCORE** est un exemple géométrique de spécification, non une coupe réelle. L'export SVG et le guide rappellent **Score puis Attacher manuellement dans Design Space** (lots 14–17), sans bouton de pilotage Cricut.

**Expert :** voir `project_sha256`, `subject_id`, `mask_id`, empreinte float32 et statut de prévol ; isoler un sujet, comparer original/masque/coupe, sélectionner un chemin G2.7, régler les propriétés physiques connues. Une révision concurrente oblige à recharger les preuves ; aucun rebind silencieux par index. Les contrôles experts consomment **la même autorité**.

~~~text
[Importer | Créer | Reprendre]  [Atelier]  Projet: atelier_01 @ SHA... [Enregistré]
[Objets / calques]              [Canevas / zoom / pan]       [Propriétés]
 ▸ Sujet A (ID stable)          Original | Masque | Coupe    Taille : mm [si connue]
 ▸ Contour CUT                  [Sélection + avant/après]    Opération : CUT
 ▸ Plis SCORE                  [Avertissements]             Opération : SCORE
[Ajouter] [Effacer] [Annuler le brouillon] [Valider si disponible]
Statut : « Aperçu non enregistré » / « Conflit de révision » / « Export externe non annulable »
~~~

**Calques :** les listes de sujets, contours, plis, textes et opérations sont des **vues dérivées** des contrats approuvés. Visibilité, solo, sélection, zoom et ordre d'affichage restent des états temporaires tant qu'un writer versionné ne les persiste pas. Ne pas injecter `layers`/`history` arbitraires dans `smartsvg-project/1`. Les couleurs et pointillés ne créent jamais automatiquement une opération Score/Draw/Foil.

## 4. Commandes, événements, persistance et Undo

- **État canonique :** `project_name`, `project_sha256`, `Subject`, masques et artefacts lus dans l'archive. **État UI éphémère :** `active_subject_id`, `selected_path_ids`, zoom, pan, visibilité, geste et `request_token`. Le panneau de projet et le canevas affichent la même révision ; aucun deuxième fichier projet.
- **Sélection :** `SELECT_SUBJECT(subject_id)` est une intention UI sans écriture. Vignette, canevas et propriétés suivent la même sélection. Sujet ambigu ou sans preuve b1 : inspection seule, retouche désactivée.
- **Preview :** `PREVIEW_STROKE` est une **commande future de spécification**, pas une API déjà disponible. Sous SHA projet et empreintes b1 valides, l'adaptateur calcule l'index depuis l'archive, appelle le replay V21.6 sur **copie** et ne publie qu'un aperçu. Les octets float32 restent côté moteur de confiance ; aucun POST de sauvegarde, aucune exécution de graphe ComfyUI implicite. Changement de sélection/révision ou réponse tardive : résultat ignoré.
- **Commit :** uniquement b2b, via writer existant `save_with_recovery` et `expected_sha256`, avec relecture et preuve d'identité. `editor_v216` est une liste de gestes ; le snapshot float32 exact est une autre ressource, à ne pas confondre.
- **Undo :** avant commit, retirer le geste local sans writer ; après commit, seulement si V34-035/038 est effectivement raccordé et testé (nouvelle révision, identité et SHA vérifiés). Undo ne supprime pas un PNG/SVG déjà exporté ni une action Design Space.

**Enveloppe future de preview (exemple de spécification JSON, NON_EXECUTE)** : l'interface ne transmet **pas** `mask_index` :

~~~json
{
  "project_name": "atelier_demo",
  "expected_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "subject_id": "subject-001",
  "mask_id": "base-mask-00",
  "mask_sha256_float32": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "request_token": "preview-0001",
  "stroke": {"mode": "add", "radius": 0.01, "points": [[0.25, 0.25], [0.26, 0.26]]}
}
~~~

Le serveur vérifie également `source_id`/`source_sha256` depuis le projet et la preuve b1 ; il ne fait jamais confiance au seul `mask_id` client. `request_token` sert à ignorer les réponses périmées, **pas** de reçu de commit durable. Aucune modification du schéma de `strokes.py` n'est imposée.

## 5. Erreurs, fallback, sécurité et performances à mesurer

| Situation | Comportement attendu |
|---|---|
| Démo / image sans segmentation | Bandeau distinct, aucune mutation de `Subject`, pas de faux export |
| Sujet non enregistré, preuve ambiguë, SHA masque erroné | Inspection seule, message « Vérifier l'identité du sujet » ; aucun index deviné |
| Projet modifié pendant aperçu ou validation | `PROJECT_CHANGED`/`STALE_PROJECT_SHA` ; annuler preview, recharger, ne pas appliquer sur un autre sujet |
| Double clic, annulation, navigation, réponse asynchrone tardive | Token + état de requête ; ignorer résultat périmé, ne pas committer deux fois |
| Disque plein, backup pending, projet en lecture seule | G2.2/recovery existants, erreur FR actionnable, sauvegarde précédente intacte |
| Zoom, pan, DPI ou changement d'onglet | Convertir coordonnées écran en points source normalisés `[0,1]`, vérifier bornes ; zoom n'altère pas les pixels |
| Masque float32 souple | Hors pixels réellement peints, conserver les valeurs bit à bit ; PNG/L8 = aperçu uniquement |
| 50 sujets ou image au-delà des budgets historiques | Refuser/segmenter les traitements en lots bornés ; ne pas créer un tenseur de 50 dans `apply_strokes` limité à 32 |
| SVG et opération de fabrication | Pinceau raster ≠ courbe SVG ; CUT ≠ SCORE ; prévol/exports des lots 13–17 inchangés |
| Undo après export | Avertissement « Le projet change, les fichiers déjà exportés restent inchangés » |

**Budgets historiques constatés :** `strokes.py` accepte au plus 400 gestes, 1 500 points/geste, 12 000 points cumulés, 5 Mpx/masque et 50 Mpx agrégés. Ces limites ne constituent **ni** une mesure de performance, **ni** une limite générale des planches futures de 50 objets. Mesurer sur fixtures : sélection→aperçu, rendu zoom/pan, mémoire float32, sauvegarde et récupération, clavier/lecteur d'écran sous Windows. Mode CPU/manuellement utilisable ; pas d'IA ni GPU obligatoire.

**Sécurité :** réutiliser le workspace à chemins bornés, contrôles de même origine G2.2, validation stricte des gestes, filtrage SVG G2.7 et original immuable. Ne jamais publier d'image personnelle, de poids IA ni de chemin local dans le dépôt public.

## 6. Tests d'acceptation proposés — tous NON_EXECUTE

| Test | Assertion précise | Preuve future / tickets |
|---|---|---|
| T-V34-18-01 | Sélection des 12 escargots de démonstration : aucun `Subject` ni archive créée, aucune fonction réelle prétendue | auto/UI ; V34-041/132 |
| T-V34-18-02 | Choisir `subject_id` synchronise vignette/canevas/propriétés ; réordonner les vignettes ne change jamais la cible | auto/UI ; V34-132 |
| T-V34-18-03 | Deux masques float32 A/B : `add` et `erase` sur A préservent B et tous les pixels non peints bit à bit ; SHA archive inchangé en preview | auto/CPU ; V34-132 |
| T-V34-18-04 | Preuve b1 absente/ambiguë ou SHA masque invalide : preview refusé, aucun `mask_index` déduit du DOM | auto/CPU ; V34-132 |
| T-V34-18-05 | SHA modifié, double clic, changement de sélection, réponse tardive : aucun commit ni cible différente, message et reprise | auto/UI ; V34-041/132 |
| T-V34-18-06 | Annuler un brouillon n'écrit rien ; Undo/Redo **après b2b** relit les révisions et n'efface jamais les exports | auto/intégration ; V34-035/038 |
| T-V34-18-07 | Boîte 140×110 : CUT et SCORE restent deux groupes sémantiques distincts, aucun transfert Score automatique | auto/UI ; V34-133 |
| T-V34-18-08 | Visibilité, solo, zoom et calques temporaires ne créent aucun champ V1 ; mm inconnus non inventés | auto/UI ; V34-133 |
| T-V34-18-09 | Sélection, outils, erreurs, validation et retour accessibles au clavier avec focus et annonces FR | UI/a11y puis Windows ; V34-045/133 |
| T-V34-18-10 | Conflit de notes G2.2, panne d'écriture ou backup pending : pas de faux succès, projet précédent conservé, récupération explicite | auto/fault-injection puis Windows ; V34-044/132 |

**Corpus autorisé :** projet V1 synthétique avec deux `Subject` b1 et masques souples float32, SHA de référence, gestes V21.6, révision concurrente, 12 escargots **fictifs**, boîte du lot 16, SVG G2.7. Aucun média Pokémon ou privé dans le dépôt public. Preuves `auto`, `Windows`, `DesignSpace` et `physique` restent **séparées** ; aucune n'est acquise par cette spécification.

## 7. Tickets minimaux (ne pas redéfinir les tickets existants)

| Ticket | Exigences et dépendances | Fichiers, test, DoD, rollback |
|---|---|---|
| **V34-132 P0 — Canevas raccordé au vrai sujet et à son aperçu** | S-008/023/070/073/080, R33-003/006/014/033, V34-041 ; preuve G3.3e-b1, preview b2a ; b2b **uniquement pour persister**. Aucun V2/assistant requis. | **Adapter** `engine/web/js/smartsvg_express_atelier_preview.html` et `smartsvg_subject_identity_g33e.mjs` ; consommer `strokes.py` via adaptateur minimal futur **si nécessaire**. T-V34-18-01..05/10, preuves auto/UI puis Windows. **DoD :** cible exacte, preview sans écriture, conflit sûr ; **rollback :** revenir à l'inspection G3.3e-b1. |
| **V34-133 P1 — Calques/propriétés dérivés du projet unique** | S-035/068/071/073/077/078, R33-003/008/018/020, V34-041/045 et contrats V34-100/106/129 selon type de projet ; aucun second store. | **Réutiliser** le canevas existant, `smartsvg_cut_review_model_g27.mjs`, `Subject` et opérations déjà prévues ; panneau futur seulement si utile. T-V34-18-07..09, auto/UI puis Windows. **DoD :** propriétés mm explicites, CUT≠SCORE, calques non destructifs, clavier ; **rollback :** panneau existant en lecture seule. |

**Déjà couverts, pas de nouveaux tickets :** V34-041 (session), V34-044 (récupération), V34-045 (accessibilité), V34-035 (Undo persistant) et V34-038 (historique UI). Mapping inverse : T01→041/132 ; T02→132 ; T03→132 ; T04→132 ; T05→041/132 ; T06→035/038 ; T07→133 ; T08→133 ; T09→045/133 ; T10→044/132. Tickets V34-132/133 au statut **SPECIFIE**, non implémentés.

## 8. Limites et prochain lot

**Blocages réels seulement :** preuve `Subject`/float32 et SHA pour retoucher ; CAS/recovery pour enregistrer ; géométrie et unités pour propriétés vectorielles ; preuves terrain avant revendication Cricut. **Non bloquants :** bootstrap autonome complet, `.smartsvg` V2, bus universel, assistant, GPU/IA, planches 50. G3.3e-b2a et les quatre exports G4 sur fixtures avancent indépendamment.

**Risques ouverts :** raccordement des vraies sélections, adaptation index→ID, Undo durable b2b non qualifié, concurrence entre onglets, accessibilité/latence Windows, calques vectoriels/texte encore non raccordés. Aucun nouveau gate V3.3. Sources internes relues le **29/10/2026** : `AGENTS.md`, V3.3 master/traceability/coverage/heritage/fastpath, `ETAT_ACTUEL_SMARTSVG.md`, code G2.2/G2.3/G2.4/G2.7/G3.3e, lots 05–07 et 13–17. Les instructions officielles Cricut Score/Attacher sont citées au [lot 17](17_EXPORTS_DESIGNSPACE.md) ; aucune nouvelle compatibilité matérielle revendiquée.

**Prochain lot 19 :** planches 12/24/50, nesting/cache/jobs, mémoire et reprise par lots bornés. Tous les tests du lot 18 restent **NON_EXECUTE** (logiciel, CPU, Windows, RTX 3070, Design Space, Cricut physique).
