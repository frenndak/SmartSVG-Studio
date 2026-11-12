# SmartSVG V3.5 — Couverture V3.4 → V3.5, réconciliation bidirectionnelle initiale

> **Contre-expertise documentaire COV-03 — 12 novembre 2026.** État **CANDIDAT NON NORMATIF**, point de départ historique `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` ; source `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md`, blob `177a0ecff5edd816e1bf879fc93c2a49efd83690`. Aucun code/CI/Windows/RTX/Design Space/coupe physique testé ici ; V3.4 demeure ACTIVE.
>
> **Frontières :** `INVENTORIE` ≠ `LIEN_DE_PLANIFICATION_RÉCIPROQUE` ≠ `CRITÈRE_SÉMANTIQUE_VALIDÉ` ≠ `SPÉCIFICATION_V3.5_APPROUVÉE` ≠ `CODE` ≠ `TEST_PASS`. Les colonnes issues du lot 23 sont des **renvois de conception**, pas des preuves de conformité produit. Les textes historiques intégraux V3.3 restent seuls normatifs.

## 1. Contrôles effectivement réalisés

| Contrôle | Résultat documentaire | Restriction |
|---|---|---|
| Exigences V3.3 uniques | **141/141** | Critères complets à rapprocher de `docs/ROADMAP_HERITAGE_v3_3.md` |
| Tickets V34 uniques | **140/140** | Pas de déclaration de fonction livrée |
| Relations directes exigence→ticket V34 | **314** distinctes | Liens de planification |
| Relations réciproques ticket V34→exigence | **314** distinctes | **0 relation unilatérale / 0 cible inexistante** |
| Tickets V34 sans exigence reliée | **0/140** | Le renvoi ne prouve pas la couverture de tous les critères |
| **Exigences héritées S/R33 sans ticket V34** | **10/141** | **Écart de traçabilité à compléter dans V3.5**, pas une suppression de V3.3 |
| Scénarios transversaux du lot 22 référencés | **14/14** | Ils ne qualifient pas automatiquement les **437 scénarios** spécifiques |
| Scénarios spécifiques historiques | [**437/437 identifiants inventoriés**](SCENARIOS_V34_INDEX.md) | **Lien fin scénario→critère/ticket non certifié**, tests NON_EXÉCUTÉS par ce travail |

### Distinction critique

Les **314 arêtes réciproques** assurent la cohérence du tableau V3.4 là où une relation existe. Elles **n'impliquent pas** une couverture totale : **10 exigences** n'ont **aucun** ticket V34 propre, par choix historique explicite (G6/G9). Elles doivent donc recevoir un traitement V3.5 sans être reclassées `COVERED` par facilité. Le lot 23 lui-même explique que les exigences G6/G9 restent exigibles.

## 2. Les 10 exigences V3.3 encore sans ticket V34 — reprise prioritaire et choix V3.5

| Exigence | Source historique, portée et critère | Axe V3.5 proposé | Statut |
|---|---|---|---|
| **S-021** | OCR et gestion de texte sur affiches ; texte préservé/averti (P2, G9) | OCR/texte vérifié avant substitution ; ne pas inventer un nouveau moteur de composition | **HÉRITÉ / À SPÉCIFIER** |
| **S-036** | Fonts → chemins ; pas de substitution silencieuse (P1, G6.3) | Contrat typographique, empreinte police, export éditable vs tracé, warning | **HÉRITÉ / À SPÉCIFIER** |
| **S-037** | Trois gabarits métiers (P1, G6.4) | Étiquette, topper, carte ; paramètres et save/reload prouvés | **HÉRITÉ / À SPÉCIFIER** |
| **S-044** | Dioramas multi-plans, prototype réellement assemblé (P2, G9) | **Parcours diorama 2.5D**, plans, superposition, ordre, assemblage ; garder le test physique | **HÉRITÉ / À SPÉCIFIER** |
| **S-047** | OCR texte de couverture ; vérifier avant remplacement (P2, G9) | OCR facultatif et confirmation des corrections | **HÉRITÉ / À SPÉCIFIER** |
| **S-064** | Contrat typographie/licence ; rendu reproductible ou avertissement précis (P1, G6) | Diagnostics glyphes, licences et fontes manquantes | **HÉRITÉ / À SPÉCIFIER** |
| **S-066** | Diorama à **quatre plans alignables** ; tolérances et assemblage réel (P2, G9) | Patrons papier multicouches, repères opt-in, découpe séparée, coupon matériel | **HÉRITÉ / À SPÉCIFIER** |
| **S-092** | Choix police/aperçu et glyphes ; français + fonte absente contrôlés (P1, G6.3) | Interface texte, preview et substitution explicite | **HÉRITÉ / À SPÉCIFIER** |
| **S-099** | Guide d'assemblage diorama dans l'UI ; prototype mesuré et assemblé (P2, G9) | Guide hors ligne, ordre des plans, épaisseur, assemblage, statut de preuve | **HÉRITÉ / À SPÉCIFIER** |
| **R33-028** | Licences et glyphes manquants visibles, G6–G8 | Contrôle transversal police/licence, preview non trompeuse | **HÉRITÉ / À SPÉCIFIER** |

**Sources :** `docs/ROADMAP_TRACEABILITY_v3_3.md` (lignes exactes de source), `docs/ROADMAP_HERITAGE_v3_3.md` (spécifications G6/G9 et tickets originaux), [lot 23 V3.4](../roadmap-v3.4/23_TRACEABILITE_BACKLOG.md) (décision historique « sans ticket V34 »). **Priorités P1/P2 citées ici sont historiques, non reclassées.** À conserver même si la version V3.5 décrit l'UX différemment.

**Analyse hostile :** supprimer les dioramas parce que Smart Delivery/Print Then Cut sont mieux détaillés créerait une **perte silencieuse** de fonctions promises dès V3.3. Inversement, ajouter dix moteurs ou dix nouveaux tickets sans étude de réemploi serait inutile. Décider pour chaque exigence si elle rejoint un **ticket V34 existant** après vérification de DoD ou justifie **un ticket V35 réellement additionnel** ; décrire tous les critères, pas seulement le titre.

### 2.1. Tests de recette à concevoir pour ces exigences (non exécutés)

- **Texte et polices G6 :** texte français accentué et glyphes indisponibles → avertissement local ; substitution de police uniquement confirmée ; conversion des textes en chemins avec relecture du SVG et rendu attendu, original/projet inchangés ; vérification licences de partage. Test négatif : police manquante, licence interdite, police incompatible.
- **Gabarits G6 :** projet étiquette, topper, carte chacun sauvegardé, fermé, rouvert et exporté suivant son **contrat de sortie réel**, avec dimensions exactes ; reprendre sans perte ou collision d'identité.
- **OCR G9 :** proposition de texte détecté, corrections manuelles et diff ; si reconnaissance échoue, ne rien remplacer ; source protégée. Vérifier les caractères et provenance des images de test (synthétiques).
- **Diorama G9 :** prototype papier **4 plans alignés** avec dimensions et ordre d'assemblage, calques/operations, contrôles de trous/fragilité et checklist matériaux ; coupure géométrique distincte du **montage réel** : version Design Space/Explore 5 et tolérances mesurées doivent être enregistrées uniquement après essai physique. Test négatif : mauvais ordre, repères non alignés, épaisseur non renseignée, dimensions incompatibles. La simulation 2D/3D n'est PAS un PASS physique.

### 2.2. Position dans le futur découpage V3.5

- **UX et édition :** texte, police, OCR et aperçu glyphes dans le domaine « Parcours débutant, expert » et « Raster/vectorisation/édition », sans créer de deuxième canevas.
- **Fabrique paramétrique :** gabarits métiers + diorama papier multi-plans dans un **sous-parcours identifié** de la rubrique fabrication (G9), avec recettes matérielles distinctes des patrons de boîte (G6/G9 et G4). Ce périmètre existe déjà dans l'héritage ; il ne doit pas être traité comme une proposition P2 purement facultative à laquelle le gel V3.4 permettrait de renoncer.
- **Conformité :** élargir la grille de couverture V3.5 et le gate de promotion pour vérifier explicitement **ces dix exigences**, sans les forcer artificiellement vers les 14 scénarios transversaux du lot 22.

## 3. Relations sources V3.4 — exigence vers ticket (141/141 lignes)

Les lignes ci-dessous reproduisent **les identifiants** et références **explicitement déclarés par le lot 23** ; aucune relation n'a été inférée à partir d'un mot-clé. Statut « RÉCIPROQUE_PLANIFICATION » indique uniquement la présence du lien exact dans les deux tableaux sources. Le texte est abrégé ici, le critère intégral reste dans V3.3.

| Exigence | Libellé abrégé du lot 23 | Ticket(s) explicite(s) | Recette transversale citée | Contrôle du lien |
|---|---|---|---|---|
| `S-001` | G0-G9 (cf. V3.2) · Geler archive V21.14.1 et corpus | `V34-001`, `V34-003`, `V34-002` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-002` | G0-G9 (cf. V3.2) · Spécifier les trois contrats de sortie | `V34-005`, `V34-129` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-003` | G0-G9 (cf. V3.2) · Définir modèle de projet/retouches sérialisables | `V34-032`, `V34-132`, `V34-010`, `V34-041`, `V34-048`, `V34-053`, `V34-059`, `V34-060`, `V34-063`, `V34-079`, `V34-087` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-004` | G0-G9 (cf. V3.2) · Réduire la complexité visible, conserver anciens IDs | `V34-041`, `V34-043`, `V34-006` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-005` | G0-G9 (cf. V3.2) · Test réel RMBG/SAM2/BiRefNet RTX 3070 | `V34-078`, `V34-080`, `V34-077`, `V34-084`, `V34-092` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-006` | G0-G9 (cf. V3.2) · Créer masques de référence des neuf images | `V34-068`, `V34-085`, `V34-094` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-007` | G0-G9 (cf. V3.2) · Validation sémantique du sujet désiré | `V34-069`, `V34-110`, `V34-007`, `V34-071`, `V34-082` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-008` | G0-G9 (cf. V3.2) · Éditeur pinceaux/undo/reload vérifié sur frontend | `V34-132`, `V34-133`, `V34-035`, `V34-038`, `V34-062`, `V34-102` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-009` | G0-G9 (cf. V3.2) · Assurance qualité Cricut par format | `V34-101`, `V34-129`, `V34-090` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-010` | G0-G9 (cf. V3.2) · Couper physiquement des exemplaires Explore 5 | `V34-124` | T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `S-011` | G0-G9 (cf. V3.2) · Fidélité SVG multicouche et analyse des formes | `V34-098`, `V34-099`, `V34-103` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-012` | G0-G9 (cf. V3.2) · Chemins SVG utilisables avec matériau choisi | `V34-106`, `V34-109`, `V34-008`, `V34-012`, `V34-107`, `V34-111`, `V34-113`, `V34-120`, `V34-127` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-013` | G0-G9 (cf. V3.2) · Écran Express unifié | `V34-043`, `V34-051`, `V34-091` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-014` | G0-G9 (cf. V3.2) · Segmentation objets et fragments associés | `V34-073` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-015` | G0-G9 (cf. V3.2) · Nettoyage des halos / découpe et offset | `V34-088`, `V34-095`, `V34-076` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-016` | G0-G9 (cf. V3.2) · HD conditionnelle + diagnostic d'artefacts | `V34-089` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-017` | G0-G9 (cf. V3.2) · Packaging « projet SmartSVG » | `V34-025`, `V34-137`, `V34-031`, `V34-131` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-018` | G0-G9 (cf. V3.2) · Queue/batch/cache avec reprise | `V34-074`, `V34-135`, `V34-070`, `V34-081`, `V34-093`, `V34-104` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `S-019` | G0-G9 (cf. V3.2) · Benchmark Canva/Design Space sur corpus identique | `V34-003` | T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `S-020` | G0-G9 (cf. V3.2) · Papier découpé multicouche / dioramas | `V34-126` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-021` | G0-G9 (cf. V3.2) · OCR et gestion du texte sur affiches | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-022` | G0-G9 (cf. V3.2) · App autonome hors ComfyUI, si justifiée | `V34-019`, `V34-139`, `V34-004`, `V34-011`, `V34-014`, `V34-017`, `V34-020`, `V34-024`, `V34-054`, `V34-064` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-023` | Identité de sujet stable | `V34-028`, `V34-132`, `V34-025`, `V34-044`, `V34-061`, `V34-072`, `V34-096`, `V34-115` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-024` | Projet `.smartsvg` v1 | `V34-025`, `V34-136` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-025` | Écran Express métier | `V34-043`, `V34-083` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-026` | Historique non destructif UI | `V34-033`, `V34-133`, `V34-029` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-027` | Contrôle GPU réel | `V34-074`, `V34-080`, `V34-016`, `V34-036`, `V34-039`, `V34-047` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-028` | Groupes sujet + accessoires | `V34-073` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-029` | Contrat PNG/alpha Cricut | `V34-087`, `V34-129`, `V34-122` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-030` | Contrat SVG Basic Cut | `V34-097`, `V34-129`, `V34-100`, `V34-108`, `V34-128` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-031` | Matrice d'essais Explore 5 | `V34-124` | T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `S-032` | Export SVG édition vs fabrication | `V34-098`, `V34-129`, `V34-112` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-033` | Préservation traits et petites régions | `V34-099` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-034` | Simplification de Bézier | `V34-099` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-035` | Canevas objets/textes | `V34-133` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-036` | Fonts et conversion textes → tracés | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-037` | Gabarits métiers | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-038` | Job manager et checkpoints | `V34-074`, `V34-135`, `V34-138` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `S-039` | Variables CSV | `V34-138` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-040` | Imposition mesurable | `V34-134` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-041` | Bibliothèque locale | `V34-136` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-042` | Audit de sécurité des projets | `V34-031`, `V34-139`, `V34-086` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `S-043` | Benchmark Canva/Design Space | `V34-003` | T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `S-044` | Dioramas multi-plans | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-045` | Vinyle multi-couleur | `V34-100`, `V34-112` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-046` | Application autonome | `V34-019`, `V34-139` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-047` | OCR texte de couverture | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-048` | Upscale IA artistique | `V34-089`, `V34-092` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-049` | `corpus_manifest` et droits d'usage des fixtures | `V34-001`, `V34-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-050` | Vérité terrain versionnée + protocole annotations | `V34-068`, `V34-085` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-051` | Rapprochement historique S-001–S-022 et inventaire réel workflows | `V34-001` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-052` | Schéma `Subject/Source/Artifact` avec identité et coordonnées | `V34-025`, `V34-028`, `V34-018`, `V34-026` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `S-053` | Format `.smartsvg` v1, migration et recovery | `V34-025`, `V34-027`, `V34-013`, `V34-022`, `V34-034`, `V34-040`, `V34-140` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `S-054` | Preuves orthogonales et sidecar `manifest.json` | `V34-003`, `V34-131` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-055` | Profil Explore 5 A4/Letter, imprimer portrait/poser A4 paysage | `V34-122`, `V34-130` | T-V34-22-06 | RÉCIPROQUE_PLANIFICATION |
| `S-056` | QA geometry Cut en mm : holes, islands, segments, offset | `V34-108`, `V34-109` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-057` | Registre matériel : machine, lame, tapis, matière, tests | `V34-107`, `V34-124` | T-V34-22-10 | RÉCIPROQUE_PLANIFICATION |
| `S-058` | Matrice environnement local et fournisseur IA | `V34-078`, `V34-080` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `S-059` | Audit accessibilité clavier/contraste/labels | `V34-045`, `V34-049` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-060` | Score qualité séparé silhouette/couleur/géométrie | `V34-101`, `V34-109` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-061` | Tests fichiers hostiles et bombes XML/ZIP | `V34-025`, `V34-139` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `S-062` | File de jobs avec identité, cache et pause/reprise | `V34-074`, `V34-135` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `S-063` | Matrice de compatibilité ComfyUI/frontend/node API | `V34-020`, `V34-139`, `V34-021`, `V34-023` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-064` | Contrat typographie et licence des polices | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-065` | Comparaison contrôlée Design Space/Canva/SmartSVG | `V34-003` | T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `S-066` | Prototype diorama à quatre plans alignables | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-067` | Accueil 4 objectifs + Reprendre | `V34-042`, `V34-043`, `V34-009`, `V34-015`, `V34-037`, `V34-050`, `V34-052`, `V34-105`, `V34-114` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-068` | Schéma unique d’écran responsive desktop | `V34-045` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-069` | États vide/chargement/erreur/export | `V34-009`, `V34-046`, `V34-030` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-070` | Sélection directe et croisée sujets↔vignettes | `V34-075`, `V34-132` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-071` | Erreurs cliquables avec région et correction réversible | `V34-065`, `V34-114`, `V34-056` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-072` | Flux Express souris + clavier | `V34-049`, `V34-066` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-073` | Aperçus original/masque/coupe séparés | `V34-091`, `V34-095` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-074` | Reprise dernier projet et contexte | `V34-044`, `V34-136`, `V34-055` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-075` | Panneau de validation du format par usage | `V34-043`, `V34-051` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `S-076` | Checklist d’export et transfert Design Space | `V34-130` | T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `S-077` | Alternative clavier aux gestes souris complexes | `V34-049` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-078` | Contrastes/focus/texte ajustable | `V34-045` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-079` | Loupe locale et comparaison glissante | `V34-095` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-080` | Pinceau correction tactile souris + aperçu effet | `V34-133` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-081` | Réglages récents et préréglages utilisateur | `V34-055`, `V34-057` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-082` | Disposition de panneaux persistante | `V34-046`, `V34-055` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-083` | Recherche d’action et aide contextuelle | `V34-050`, `V34-051` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-084` | Ouvrir dossier/export/rapport depuis la réussite | `V34-130`, `V34-140` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-085` | Aperçu cutter-only et repères micro-détails | `V34-108`, `V34-109`, `V34-118` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-086` | Toiles avec poignées et dimensions mm | `V34-133` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-087` | Multi-sélection, groupement et menu contextuel | `V34-133` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `S-088` | Trois gabarits de départ guidés | `V34-126` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `S-089` | Tableau de lot et reprise d’un échec isolé | `V34-135`, `V34-134` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `S-090` | Comparer deux dispositions de planche | `V34-134` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `S-091` | Bibliothèque avec miniatures et filtre métier | `V34-136` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-092` | Choix de police avec aperçu et alertes glyphes | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-093` | Protocole de test utilisateur novice/régulier | `V34-058`, `V34-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-094` | Tests d’accessibilité + vérification Windows zoom | `V34-045`, `V34-139` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-095` | Tests de récupération pendant export/IA | `V34-022`, `V34-140` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `S-096` | Instrumentation locale UX et latence (opt-in export rapport) | `V34-024`, `V34-140` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-097` | Commandes « refaire sur sélection » | `V34-137`, `V34-138` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-098` | Liste de recettes/gabarits personnels | `V34-137` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `S-099` | Guide d’assemblage de diorama dans l’UI | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `S-100` | Raccourcis personnalisables / commandes favorites | `V34-046` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `S-101` | Comparaison de variantes avec scores séparés | `V34-002`, `V34-134` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `R33-001` | Héritage intégral et vérifiable de V3.2 | `V34-001`, `V34-025` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `R33-002` | Échelle de maturité commune sans promotion implicite | `V34-003` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `R33-003` | Projet unique partagé par les six espaces | `V34-011`, `V34-132` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `R33-004` | Identités et révisions sur chaque commande asynchrone | `V34-028`, `V34-032` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `R33-005` | Résultat obsolète refusé ou isolé | `V34-036`, `V34-115` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `R33-006` | Masques float32 comme autorité de retouche | `V34-028`, `V34-133` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `R33-007` | Fallback manuel ou CPU pour le parcours essentiel | `V34-051`, `V34-086` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `R33-008` | Séparation permanente PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition | `V34-005`, `V34-129` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `R33-009` | Migration transactionnelle des projets | `V34-027` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `R33-010` | Index de bibliothèque reconstructible | `V34-136` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `R33-011` | Jobs idempotents avec succès partiel | `V34-074`, `V34-135` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `R33-012` | Annulation et reprise sans doublon | `V34-074`, `V34-135` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `R33-013` | Gestion explicite disque plein et lecture seule | `V34-022`, `V34-140` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `R33-014` | Gestion de sessions concurrentes et double activation | `V34-036`, `V34-125`, `V34-119` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `R33-015` | Rapport de diagnostic local expurgé | `V34-024`, `V34-140` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-016` | Inventaire des licences et provenances | `V34-001`, `V34-078` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `R33-017` | Mesure CPU RAM VRAM et temps par fournisseur | `V34-080`, `V34-085` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `R33-018` | Validation responsive et zoom Windows | `V34-045` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-019` | Alternative clavier à chaque geste complexe | `V34-049` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-020` | Localisation française cohérente et messages actionnables | `V34-050`, `V34-056` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-021` | Tests d'installation mise à jour et rollback | `V34-139` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-022` | Versions Design Space associées aux preuves | `V34-107`, `V34-130`, `V34-116`, `V34-117`, `V34-121` | T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `R33-023` | Contexte machine matière outil associé aux preuves physiques | `V34-107`, `V34-124` | T-V34-22-10 | RÉCIPROQUE_PLANIFICATION |
| `R33-024` | Données de preuve privées hors dépôt public | `V34-003`, `V34-140` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-025` | Tests de panne pendant sauvegarde export et IA | `V34-022`, `V34-140`, `V34-123` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `R33-026` | Budgets pour projets et lots volumineux | `V34-074`, `V34-135` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `R33-027` | Noms de fichiers sûrs et collisions contrôlées | `V34-131`, `V34-138` | T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `R33-028` | Polices licences et glyphes manquants visibles | **AUCUN V34 — V3.3 G6/G9** | **Test métier V3.3 à relier** | GAP_HÉRITAGE_G6_G9 |
| `R33-029` | Comparaison de rendu indépendante de la fabricabilité | `V34-098`, `V34-109` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `R33-030` | Aucune requête réseau implicite | `V34-079`, `V34-140` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `R33-031` | Rapport par objet pour planches et lots | `V34-135` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `R33-032` | Préférences UI séparées de l'état projet | `V34-055` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-033` | États vide chargement erreur annulation et reprise | `V34-046`, `V34-050` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-034` | Preuve liée au SHA exact et à l'environnement | `V34-003`, `V34-124` | T-V34-22-10 | RÉCIPROQUE_PLANIFICATION |
| `R33-035` | Gate humain pour toute certification matérielle | `V34-124` | T-V34-22-10 | RÉCIPROQUE_PLANIFICATION |
| `R33-036` | Rollback documenté pour chaque micro-lot | `V34-027`, `V34-140` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `R33-037` | Registre de risques relié aux tests | `V34-003`, `V34-109` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `R33-038` | Matrice de compatibilité versionnée | `V34-021`, `V34-139` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-039` | Observation utilisateur sans collecte excessive | `V34-055`, `V34-058` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `R33-040` | Gel fonctionnel avant déclaration stable | `V34-002`, `V34-003` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |

## 4. Index inverse source — ticket vers exigences (140/140 lignes)

| Ticket | Lot source | Exigences reliées par le lot 23 | Scénarios transversaux cités | Contrôle du lien |
|---|---|---|---|---|
| `V34-001` | Lot 01 | `R33-001`, `R33-016`, `S-001`, `S-049`, `S-051` | T-V34-22-02, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-002` | Lot 01 | `R33-040`, `S-001`, `S-101` | T-V34-22-02, T-V34-22-05, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-003` | Lot 01 | `R33-002`, `R33-024`, `R33-034`, `R33-037`, `R33-040`, `S-001`, `S-019`, `S-043`, `S-049`, `S-054`, `S-065` | T-V34-22-01, T-V34-22-02, T-V34-22-07, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-004` | Lot 01 | `S-022` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-005` | Lot 01 | `R33-008`, `S-002` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-006` | Lot 02 | `S-004` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-007` | Lot 02 | `S-007` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-008` | Lot 02 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-009` | Lot 02 | `S-067`, `S-069` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-010` | Lot 02 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-011` | Lot 03 | `R33-003`, `S-022` | T-V34-22-14, T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-012` | Lot 03 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-013` | Lot 03 | `S-053` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-014` | Lot 03 | `S-022` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-015` | Lot 03 | `S-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-016` | Lot 03 | `S-027` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-017` | Lot 04 | `S-022` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-018` | Lot 04 | `S-052` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-019` | Lot 04 | `S-022`, `S-046` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-020` | Lot 04 | `S-022`, `S-063` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-021` | Lot 04 | `R33-038`, `S-063` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-022` | Lot 04 | `R33-013`, `R33-025`, `S-053`, `S-095` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-023` | Lot 04 | `S-063` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-024` | Lot 04 | `R33-015`, `S-022`, `S-096` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-025` | Lot 05 | `R33-001`, `S-017`, `S-023`, `S-024`, `S-052`, `S-053`, `S-061` | T-V34-22-02, T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-026` | Lot 05 | `S-052` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-027` | Lot 05 | `R33-009`, `R33-036`, `S-053` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-028` | Lot 05 | `R33-004`, `R33-006`, `S-023`, `S-052` | T-V34-22-02, T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-029` | Lot 05 | `S-026` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-030` | Lot 05 | `S-069` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-031` | Lot 05 | `S-017`, `S-042` | T-V34-22-02, T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-032` | Lot 06 | `R33-004`, `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-033` | Lot 06 | `S-026` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-034` | Lot 06 | `S-053` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-035` | Lot 06 | `S-008` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-036` | Lot 06 | `R33-005`, `R33-014`, `S-027` | T-V34-22-12, T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-037` | Lot 06 | `S-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-038` | Lot 06 | `S-008` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-039` | Lot 06 | `S-027` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-040` | Lot 06 | `S-053` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-041` | Lot 07 | `S-003`, `S-004` | T-V34-22-02, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-042` | Lot 07 | `S-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-043` | Lot 07 | `S-004`, `S-013`, `S-025`, `S-067`, `S-075` | T-V34-22-14, T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-044` | Lot 07 | `S-023`, `S-074` | T-V34-22-02, T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `V34-045` | Lot 07 | `R33-018`, `S-059`, `S-068`, `S-078`, `S-094` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-046` | Lot 07 | `R33-033`, `S-069`, `S-082`, `S-100` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-047` | Lot 07 | `S-027` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-048` | Lot 07 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-049` | Lot 07 | `R33-019`, `S-059`, `S-072`, `S-077` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-050` | Lot 08 | `R33-020`, `R33-033`, `S-067`, `S-083` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-051` | Lot 08 | `R33-007`, `S-013`, `S-075`, `S-083` | T-V34-22-14, T-V34-22-01, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-052` | Lot 08 | `S-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-053` | Lot 08 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-054` | Lot 08 | `S-022` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-055` | Lot 08 | `R33-032`, `R33-039`, `S-074`, `S-081`, `S-082` | T-V34-22-13, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-056` | Lot 08 | `R33-020`, `S-071` | T-V34-22-08, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-057` | Lot 08 | `S-081` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-058` | Lot 08 | `R33-039`, `S-093` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-059` | Lot 09 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-060` | Lot 09 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-061` | Lot 09 | `S-023` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-062` | Lot 09 | `S-008` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-063` | Lot 09 | `S-003` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-064` | Lot 09 | `S-022` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-065` | Lot 09 | `S-071` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-066` | Lot 09 | `S-072` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-067` | Lot 09 | `S-093` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-068` | Lot 10 | `S-006`, `S-050` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-069` | Lot 10 | `S-007` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-070` | Lot 10 | `S-018` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-071` | Lot 10 | `S-007` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-072` | Lot 10 | `S-023` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-073` | Lot 10 | `S-014`, `S-028` | T-V34-22-04, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-074` | Lot 10 | `R33-011`, `R33-012`, `R33-026`, `S-018`, `S-027`, `S-038`, `S-062` | T-V34-22-12, T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-075` | Lot 10 | `S-070` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-076` | Lot 10 | `S-015` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-077` | Lot 10 | `S-005` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-078` | Lot 11 | `R33-016`, `S-005`, `S-058` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-079` | Lot 11 | `R33-030`, `S-003` | T-V34-22-02, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-080` | Lot 11 | `R33-017`, `S-005`, `S-027`, `S-058` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-081` | Lot 11 | `S-018` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-082` | Lot 11 | `S-007` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-083` | Lot 11 | `S-025` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-084` | Lot 11 | `S-005` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-085` | Lot 11 | `R33-017`, `S-006`, `S-050` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-086` | Lot 11 | `R33-007`, `S-042` | T-V34-22-03, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-087` | Lot 12 | `S-003`, `S-029` | T-V34-22-02, T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-088` | Lot 12 | `S-015` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-089` | Lot 12 | `S-016`, `S-048` | T-V34-22-05, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-090` | Lot 12 | `S-009` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-091` | Lot 12 | `S-013`, `S-073` | T-V34-22-14, T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-092` | Lot 12 | `S-005`, `S-048` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-093` | Lot 12 | `S-018` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-094` | Lot 12 | `S-006` | T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |
| `V34-095` | Lot 12 | `S-015`, `S-073`, `S-079` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-096` | Lot 13 | `S-023` | T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-097` | Lot 13 | `S-030` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-098` | Lot 13 | `R33-029`, `S-011`, `S-032` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-099` | Lot 13 | `S-011`, `S-033`, `S-034` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-100` | Lot 13 | `S-030`, `S-045` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-101` | Lot 13 | `S-009`, `S-060` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-102` | Lot 13 | `S-008` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-103` | Lot 13 | `S-011` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-104` | Lot 13 | `S-018` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-105` | Lot 13 | `S-067` | T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-106` | Lot 14 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-107` | Lot 14 | `R33-022`, `R33-023`, `S-012`, `S-057` | T-V34-22-08, T-V34-22-10, T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `V34-108` | Lot 14 | `S-030`, `S-056`, `S-085` | T-V34-22-01, T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-109` | Lot 14 | `R33-029`, `R33-037`, `S-012`, `S-056`, `S-060`, `S-085` | T-V34-22-08, T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-110` | Lot 14 | `S-007` | T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-111` | Lot 14 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-112` | Lot 14 | `S-032`, `S-045` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-113` | Lot 14 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-114` | Lot 14 | `S-067`, `S-071` | T-V34-22-14, T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-115` | Lot 14 | `R33-005`, `S-023` | T-V34-22-02, T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-116` | Lot 15 | `R33-022` | T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `V34-117` | Lot 15 | `R33-022` | T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `V34-118` | Lot 15 | `S-085` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-119` | Lot 15 | `R33-014` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-120` | Lot 15 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-121` | Lot 15 | `R33-022` | T-V34-22-09 | RÉCIPROQUE_PLANIFICATION |
| `V34-122` | Lot 15 | `S-029`, `S-055` | T-V34-22-01, T-V34-22-06 | RÉCIPROQUE_PLANIFICATION |
| `V34-123` | Lot 15 | `R33-025` | T-V34-22-03 | RÉCIPROQUE_PLANIFICATION |
| `V34-124` | Lot 15 | `R33-023`, `R33-034`, `R33-035`, `S-010`, `S-031`, `S-057` | T-V34-22-10, T-V34-22-07 | RÉCIPROQUE_PLANIFICATION |
| `V34-125` | Lot 15 | `R33-014` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-126` | Lot 16 | `S-020`, `S-088` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-127` | Lot 16 | `S-012` | T-V34-22-08 | RÉCIPROQUE_PLANIFICATION |
| `V34-128` | Lot 16 | `S-030` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-129` | Lot 17 | `R33-008`, `S-002`, `S-009`, `S-029`, `S-030`, `S-032` | T-V34-22-01 | RÉCIPROQUE_PLANIFICATION |
| `V34-130` | Lot 17 | `R33-022`, `S-055`, `S-076`, `S-084` | T-V34-22-09, T-V34-22-06, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-131` | Lot 17 | `R33-027`, `S-017`, `S-054` | T-V34-22-02, T-V34-22-01, T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `V34-132` | Lot 18 | `R33-003`, `S-003`, `S-008`, `S-023`, `S-070` | T-V34-22-04, T-V34-22-02 | RÉCIPROQUE_PLANIFICATION |
| `V34-133` | Lot 18 | `R33-006`, `S-008`, `S-026`, `S-035`, `S-080`, `S-086`, `S-087` | T-V34-22-04 | RÉCIPROQUE_PLANIFICATION |
| `V34-134` | Lot 19 | `S-040`, `S-089`, `S-090`, `S-101` | T-V34-22-11, T-V34-22-05 | RÉCIPROQUE_PLANIFICATION |
| `V34-135` | Lot 19 | `R33-011`, `R33-012`, `R33-026`, `R33-031`, `S-018`, `S-038`, `S-062`, `S-089` | T-V34-22-11 | RÉCIPROQUE_PLANIFICATION |
| `V34-136` | Lot 20 | `R33-010`, `S-024`, `S-041`, `S-074`, `S-091` | T-V34-22-02, T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `V34-137` | Lot 20 | `S-017`, `S-097`, `S-098` | T-V34-22-02, T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `V34-138` | Lot 20 | `R33-027`, `S-038`, `S-039`, `S-097` | T-V34-22-11, T-V34-22-13 | RÉCIPROQUE_PLANIFICATION |
| `V34-139` | Lot 21 | `R33-021`, `R33-038`, `S-022`, `S-042`, `S-046`, `S-061`, `S-063`, `S-094` | T-V34-22-03, T-V34-22-14 | RÉCIPROQUE_PLANIFICATION |
| `V34-140` | Lot 21 | `R33-013`, `R33-015`, `R33-024`, `R33-025`, `R33-030`, `R33-036`, `S-053`, `S-084`, `S-095`, `S-096` | T-V34-22-03, T-V34-22-14, T-V34-22-12 | RÉCIPROQUE_PLANIFICATION |

## 5. Les 437 scénarios : point de jonction à compléter sans faux liens

**Conservés individuellement** dans [SCENARIOS_V34_INDEX.md](SCENARIOS_V34_INDEX.md) et ses trois inventaires. Le lot 23 n'encode que les **14 scénarios transversaux du lot 22**, utilisés comme points d'entrée ; il ne justifie **pas** les 423 autres liaisons fines par leur seul numéro de lot.

**Exigence du prochain audit V35-COV-04 :** pour chaque `T-V34-LL-NN`, vérifier la ligne/section source et rattacher le ou les tickets/exigences pertinents **après** lecture du critère et du consommateur réel ; sinon `À_RAPPROCHER` avec motif. Les relations V34 de ce document sont des **candidats**, elles ne suffisent pas à approuver un test ou une feature V3.5. Pour les dix exigences sans ticket V34, rechercher les tests métiers V3.3 originaux ou spécifier une recette V35 additionnelle **sans les inclure frauduleusement dans les 437**.

## 6. Optimisations, erreurs évitées et décision

1. **Éviter le faux 100 %** : les 141 lignes sont conservées mais **10/141 n'ont pas de V34** ; afficher deux métriques différentes « inventorié » vs « rapproché/sans-ticket G6/G9 ».
2. **Éviter le faux 437/437 relié** : compter uniquement les scénarios inventoriés comme tels ; traçabilité sémantique et tests restent ouverts.
3. **Ne pas dupliquer les 314 liens** dans un second gestionnaire de tickets. Ce document est une photographie auditée, pas un nouvel index normatif.
4. **Corriger la visibilité du périmètre** : typographie complète, gabarits et dioramas multi-plans doivent figurer explicitement dans les domaines V3.5, sinon leur omission devient probable lors d'un passage trop court.
5. **Gate P0 documentaire** : suivre séparément chaque exigence `GAP_HÉRITAGE_G6_G9` avant toute promotion V3.5 ; aucune interprétation permissive ne réduit les P1/P2 historiques.
6. **Gouvernance** : aucune modification des archives, AGENTS.md, format .smartsvg, PR code ni tâche de développement ; la promotion de V3.5 reste soumise à revue et procédure distincte.

**Prochain micro-lot :** générer une matrice scénario→ticket→exigence **qualifiée sur preuves** en commençant par les 52 scénarios des lots 02–04 ; identifier aussi les cas métier G6/G9 de V3.3. Puis contre-expertiser les dix domaines UX/produit et les nouvelles capacités #141, en évitant l'empilement d'outils.
