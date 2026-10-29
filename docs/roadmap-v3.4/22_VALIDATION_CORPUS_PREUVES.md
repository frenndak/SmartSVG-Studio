# SmartSVG Studio V3.4 — Lot 22/24 : corpus, validation et preuves

**DRAFT — 29 octobre 2026.** V3.3 reste ACTIVE, avec ses **101 S + 40 R33**, F01–F15, P01–P10 et G0–G9 intacts. Ce lot améliore uniquement les protocoles de validation des fonctions déjà prévues : **aucune nouvelle fonction, aucun nouveau gate, aucun nouveau framework**. Références : main **fff374e5147689165839bd76e742713d714ff147**, branche avant lot **d5774c00c6a49f5fc3748e833aba8d55c249359f**, issue #72, PR #73 DRAFT. **Tous les tests T-V34-22 sont SPÉCIFIÉS / NON_EXECUTE**.

## 1. Contre-expertise du lot 21 et du code réel (3 précisions)

1. **Bootstrap ≠ sauvegarde.** T-V34-21-01 regroupe démarrage natif et save/reload V1. Le premier dépend de V34-019 ; l'écriture sûre de V34-018/022. Il faut enregistrer les résultats séparément : succès d'accueil n'implique pas succès de persistance. Cela ne bloque pas G3.3e-b2a.
2. **Présence de tests ≠ exécution réussie.** Le HEAD contient engine/tests/test_project_archive_g13.py (fixtures ZIP synthétiques), test_lossless_masks_g24.py (float32 exact), test_project_recovery_g14.py et test_v21153_cut_preflight.py (fail-closed SVG). engine/smartsvg_quality/release_gate_v21152.py fournit un prévol **non certifiant**. Les réutiliser et conserver leurs assertions ; aucun PASS attribué à ce lot.
3. **Installateur ≠ export qualifié.** NON_APPLICABLE Design Space/physique peut être motivé pour le seul installateur, jamais pour P01/P02/P04, Score+Cut ou les revendications de fabrication. Aucun nouveau système de preuve ne doit remplacer V34-003.

Aucune modification du lot 21 n'est nécessaire : cette interprétation évite de créer de fausses dépendances entre le bootstrap autonome, l'édition G3.3e et les fixtures G4.

## 2. Corpus minimal, autorité et réutilisation

| Corpus | Référence réutilisée ou donnée synthétique | Oracle | Limite |
| --- | --- | --- | --- |
| C1 — projet | Tests project_archive_g13, lossless_masks_g24, project_recovery_g14 | IDs Subject, SHA, bytes float32, dernier état sain | Pas de preuve Windows |
| C2 — géométrie | test_v21153_cut_preflight, patron du lot 16 | XML sûr, unités mm, contours, CUT distinct de SCORE | Pas de coupe certifiée |
| C3 — planches | 12 escargots géométriques synthétiques, 24 et 50 instances distinctes | IDs, collisions, marges, déterminisme, reprise | Pas de segmentation photo réelle |
| C4 — bibliothèque | 105 projets temporaires et CSV 30 lignes synthétiques du lot 20 | pagination, index, encodage, erreurs par ligne | Pas de police commerciale embarquée |
| C5 — adversarial | ZIP corrompus, symlinks, disque plein, fichiers verrouillés, réseau interdit, package modifié | refus sûr, aucune perte silencieuse | Pas de certification antivirus |
| C6 — terrain | Photos autorisées, captures Design Space et coupons papier/carton privés | mesures datées et protocole reproductible | **Ne jamais publier médias privés** |

L'original est immuable, le projet .smartsvg reste autorité, les masques float32 ne sont pas quantifiés, les sauvegardes conservent CAS SHA et rollback. Un cache, un rapport ou un PNG de prévisualisation n'est pas un deuxième store. Aucune dépendance à un modèle IA ni à un téléchargement pour C1–C5.

## 3. Exécution par tranches et dépendances réellement obligatoires

**Voie A — édition :** identité G1.2 et SHA/révision → preview b2a sur le vrai sujet → persistance b2b/Undo → UX Windows. Ne pas attendre la V3.4 ni reconstruire le moteur de pinceau.

**Voie B — fichiers :** fixtures SVG/PNG → validation des quatre contrats et prévol → import Design Space → coupon physique. Les deux premières étapes peuvent avancer **en parallèle** de G3.3/G3.4, sans prétendre valider la machine.

**Voie C — boîte :** calcul mm et CUT/SCORE → guide d'affectation Score et Attacher **manuels** dans Design Space → coupon. L'installateur natif et le format V2 ne sont pas des prérequis.

**Voie D — IA :** chemin manuel/CPU disponible ; GPU et modèle uniquement opt-in après licence/version/hash et test mémoire. OOM = repli ou erreur récupérable, pas perte de projet.

À chaque PR de code future : tests ciblés sur contrat modifié, puis CI pertinente sur le SHA exact ; ne pas refaire systématiquement des essais physiques sans modification affectant l'artefact ou le procédé. Les gates V3.3 restent inchangés ; un axe BLOQUE n'arrête pas les travaux indépendants.

## 4. Recettes vérifiables proposées — aucun test exécuté

| ID | Cas | Assertion observable / protocole | Axe de preuve | Tickets V34 existants |
| --- | --- | --- | --- | --- |
| T-V34-22-01 | Quatre sorties | 4 artefacts synthétiques : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition restent typés distinctement, mm/viewBox vérifiés et aucun statut machine-ready. | auto | V34-005/129/130 |
| T-V34-22-02 | Projet float32 | Save/reload V1 avec 2 Subject : identités, sources, SHA et octets float32 strictement identiques, aucune mutation du fichier source. | auto | V34-018/022/132 |
| T-V34-22-03 | Crash et archive hostile | ZIP hostile, disque plein, lock et interruption de sauvegarde : refus sans perte du dernier projet sain ni effacement des sidecars ; recovery sous CAS et confirmation. | auto + Windows | V34-022/140 |
| T-V34-22-04 | Retouche du bon sujet | Geste add/erase sur Subject A : B inchangé bit-à-bit ; A inchangé hors zone ; révision obsolète refusée, cancel sans écriture. | auto + UI | V34-132/133 |
| T-V34-22-05 | Planches 12 escargots | 12 sujets synthétiques distincts : 12 IDs uniques, pas de collision/hors-page, dimensions mm ; PNG Print Then Cut sans faux repères capteur SmartSVG. | auto + UI | V34-129/134/135 |
| T-V34-22-06 | A4 et Design Space | Importer PNG, relever version Design Space et taille ; feuille A4 placée en paysage sur tapis, repères imprimés par Design Space et non SmartSVG. | Design Space + Windows | V34-122/129/130 |
| T-V34-22-07 | Coupon stickers | Imprimer et découper 12 stickers en une session Design Space ; relever 12 contours, erreurs, mesures, matière, tapis, imprimante et calibration ; critères pré-déclarés. | physique | V34-124/129/135 |
| T-V34-22-08 | Boîte paramétrique | Boîte 80×50×30 mm, languettes 10 mm : développé 140×110 mm ; CUT extérieur/fentes ≠ SCORE plis ; conflit de segments détecté. | auto + UI | V34-106/109/126/127/128 |
| T-V34-22-09 | Boîte Score/Attach | Importer SVG, sélectionner manuellement Score, garder Basic Cut, Attacher ; contrôler dimensions et superposition, version Design Space, capture expurgée. | Design Space + Windows | V34-111/120/124/130 |
| T-V34-22-10 | Coupon carton | Couper/rainurer/plier un coupon : consigner changement d'outil, matière, tapis, dimensions de plis et coupes, écarts et tolérances déclarées avant essai. | physique | V34-124/128 |
| T-V34-22-11 | Batch 50 et reprise | 12/24/50 instances par lots bornés ; interruption après 17/50 puis reprise sans doublon au même SHA ; SHA modifié = refus ; pic RAM/VRAM mesuré. | auto + Windows (+ GPU si activé) | V34-074/134/135 |
| T-V34-22-12 | IA facultative | Aucun modèle installé : mode manuel/CPU ; téléchargement refusé/corrompu, OOM et interruption : projet intact, réseau jamais implicite, fallback explicite. | auto + Windows (+ GPU si modèle) | V34-078/079/086/140 |
| T-V34-22-13 | Bibliothèque et CSV | 105 projets synthétiques sans troncature ; index corrompu reconstruit ; 30 lignes CSV (accents, formules, erreurs) et reprise 17/30 sans exécution de formule ni doublon. | auto + UI + Windows | V34-136/137/138 |
| T-V34-22-14 | Windows et UX | Démarrage natif sans ComfyUI, offline intercepté, package altéré refusé, rollback sans perte ; clavier, zoom 125/150 %, messages FR et rapport expurgé. | auto + Windows + UX | V34-019/020/139/140 |

**Parcours novice A :** Importer → identifier 12 sujets (ou indiquer explicitement « synthétiques ») → vérifier contours et planche → exporter PNG Print Then Cut → importer dans Design Space → vérifier taille/orientation A4 → imprimer et découper dans une même session → mesurer. La démonstration des 12 escargots fictifs ne prouve ni détourage ni coupe.

**Parcours expert A :** inspecter Subject/masque SHA, placements verrouillés, rapports de collision, empreinte d'export, mémoire et reprise. **Parcours novice B :** Créer boîte aux mm déclarés → prévol CUT/SCORE → SVG → Design Space : Score, Basic Cut, Attacher → vérifier échelle → coupon. **Parcours expert B :** inspecter fentes, plis, profils, provenance des outils et écart mesuré. Un trait pointillé ou une couleur SVG ne transporte jamais automatiquement Score.

**Erreurs et rollback :** afficher en français cause, fichier/opération concerné, action corrective et état conservé ; refuser projet/révision périmés, annuler les jobs sans doublons, préserver original, snapshot et backups. Ne jamais transformer un échec d'import ou un appareil absent en PASS.

## 5. Registre de preuve : utiliser V34-003, sans stockage parallèle

Chaque exécution future relie **test_id → ticket_id → exigence S/R33 → code_sha → fixture_sha → environnement/version → protocole → résultat → preuve → limites**. Source normative et code testé portent des SHA différents ; le test a un identifiant d'exécution distinct. États par axe : **PASS, FAIL, NON_EXECUTE, NON_APPLICABLE (motif), BLOQUE (motif)**. Maturité SPECIFIE/IMPLEMENTE/RACCORDE/QUALIFIE/STABILISE indépendante. Axes **automatique, Windows, RTX/GPU, Design Space, physique** orthogonaux ; la CI ne certifie jamais une coupe.

Les preuves publiques sont **expurgées** : aucun secret, chemin utilisateur complet, photographie privée, illustration tierce, poids de modèle ou identifiant personnel. Conserver les preuves sensibles hors dépôt avec une référence opaque, et seulement leur résumé admissible dans GitHub.

**Métriques à mesurer, sans seuil inventé :** latences p50/p95, pic RAM/VRAM sur 12/24/50, durée de reprise, objets manquants/doublons, collisions/hors-page, erreurs et étapes novice, écarts mm après import, qualité du pli et de la coupe. Déclarer les seuils/tolérances **avant** le coupon et à partir du matériau/profil réellement testé ; aucune précision universelle.

## 6. Backlog minimal et Definition of Done

**Zéro nouveau ticket V34 :** les tickets existants couvrent preuve (V34-003), non-régression des sorties (V34-005/129/130), projet/recovery (V34-018/022/140), fabrication (V34-106/109/124/128), Atelier (V34-132/133), planches (V34-134/135), bibliothèque/CSV (V34-136..138), Windows (V34-139/140). Les T-V34-22-01..14 sont des **tests de référence transversaux**, non des gates additionnels.

**DoD de chaque future PR d'implémentation :** consommateur réel et module existant identifié ; assertions ciblées vertes au SHA exact ; régression des projets/IDs/ports et quatre sorties ; erreur UX actionnable ; rollback vérifié ; axe matériel qualifié **seulement** avec preuve matérielle correspondante. Les tickets restent SPECIFIE tant que non implémentés. Les tests du présent lot restent NON_EXECUTE.

## 7. Risques et suite

Les limites historiques 32 masques/snapshot V1, la disponibilité d'une application Windows autonome, l'import réel Design Space, la RTX 3070 et les essais Cricut Explore 5 **ne sont pas levés**. Versions outils, matière, firmware, Design Space et tolérances doivent être consignées à l'essai. **Lot 23 :** réconcilier exhaustivement les 141 exigences S/R33 ↔ tickets V34 ↔ tests ou justification, supprimer les dépendances fictives, ordonner le backlog par vertical slices et code déjà là, sans nouveaux tickets de simple traçabilité.

**Sources internes vérifiées le 29/10/2026 :** AGENTS.md, V3.3 MASTER/TRACEABILITY/COVERAGE/HERITAGE/FASTPATH, README/PROGRESS/HERITAGE_INDEX V3.4, lots 01/15/16/17/19/20/21 et tests de main nommés plus haut. **Sources Cricut officielles revues le 29/10/2026 :** [Explore 5 Print Then Cut](https://help.cricut.com/hc/fr/articles/38613592650903-Comment-imprimer-puis-d%C3%A9couper-avec-la-Cricut-Explore-5) (A4 paysage sur tapis et même session), [Explore 5 Scoring Tool](https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool) (Score et Attacher manuels), [Calibration Print Then Cut](https://help.cricut.com/hc/en-us/articles/360009424974-Calibrating-your-machine-for-Print-Then-Cut). Sources fabricant ≠ preuve SmartSVG.
