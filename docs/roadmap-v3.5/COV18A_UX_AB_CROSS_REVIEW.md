# V35-COV-18A — Contre-expertise croisée A01–A16 et B01–B14 (première passe)
**13/11/2026 — CANDIDAT, non normatif.** Références : [COV17A audit](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md), [COV17A review](COV17A_UX_A01_A16_SEMANTIC_REVIEW.md), [COV17B](COV17B_UX_B01_B14_SEMANTIC_AUDIT.md), [COV10C](COV10C_V1_TEXT_EXPORT_PORTS.md), [contrat 25 axes](AUTOMATION_QUALITY_CONTRACT.md), [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134). Les 30 IDs sont examinés comme décisions candidates, **non** comme 30 fonctions Windows livrées. HEAD main actuel NON_VÉRIFIÉ pendant cette passe : les SHA de blobs des fiches antérieures ne sont pas des preuves d'actualité.

## Divergences réelles et arbitrages proposés (non adoptés)
1. **A04 :** COV17A-AUDIT « RAFFINER / P1 », COV17A-REVIEW « REPORTER IA / GARDER CPU ». **Résolution proposée :** conserver le contrat A04 intégral (prompts grossiers, propositions de masque, incertitude, alternatives) en P1; différer uniquement l'accélération/modèle IA non prouvé, sans rétrograder l'obligation V3.4. L'option CPU doit afficher ses limites. Gate : identifier ticket/DoD historique et vérifier le chemin de consentement provider avant qualification.
2. **A08 :** AUDIT « RAFFINER / P1 », REVIEW « REPORTER HD / GARDER retouches CPU ». **Résolution proposée :** P1 pour diagnostic, netteté, débruitage et contraste; reporter uniquement une super-résolution IA non prouvée. `auto_hd` = dérivé CPU, ne prouve pas de détails retrouvés.
3. **A16 :** AUDIT « REPORTER AUTOMATISATION / P2 », REVIEW « REPORTER IA / GARDER métriques ». **Résolution proposée :** métriques explicables de fidélité, complexité et topologie au jalon pertinent, automatisation IA conditionnée à une validation indépendante. Le libellé A16 et son obligation historique ne disparaissent pas. Ne jamais annoncer « facilité de coupe certifiée ».
4. **A01–A03, A05–A07, A09–A15 :** les deux fiches sont compatibles sur l'intention, mais **pas certifiées équivalentes aux DoD V34** : l'absence de divergence visible entre deux résumés n'est pas une preuve de couverture sémantique.
5. **B01–B05 et B09–B14 :** `Subject`, `Artifact`, `editor_v216` et SVG à groupes ne sont **pas** un modèle natif persistant de calques/texte/objets. Interdire l'extension silencieuse de `editor_v216` (champs autorisés `version,width,height,count,source,strokes`). Une proposition `ObjectRef/LayerDraft/TextDraft` doit rester transitoire et non sauvegardable jusqu'à ADR schéma, reader/writer, migration explicite, rollback et revue propriétaire.
6. **B06–B08 :** les reports de perspective, articulation et reconstruction concernent des accélérations ou recherches **candidates**; comparer leurs exigences héritées avant toute décision de calendrier définitive. Aucune reconstruction générative sans opt-in, source hash, licence et annulation.

## Contrat d'intégration minimal à soumettre à revue
**Source de vérité** : un projet `.smartsvg` V1, writer CAS et identités `subject_id`, masques float32, `source_sha256`. Un brouillon UI peut contenir `project_revision`, `object_ref`, `transform_matrix` 3×3 finie, `bbox_px`, `selection_mask_ref` et `preview_generation`, sans écrire de nouveau champ V1. La géométrie machine doit avoir unités mm explicites et opération KNOWN/UNKNOWN; un calque visuel ne devient jamais une opération CUT. Tout résultat calculé sur une ancienne révision est rejeté avant commit. Undo du brouillon ne remplace pas récupération CAS. Un changement persistant de texte/calque exige décision de gouvernance préalable.

**UX novice** : import réel → sélection au canevas → retouche locale → avant/après → Undo → prévol → export distinct. **UX expert** : provenance, unités, IDs, topologie, métriques, profil UNKNOWN, conflit et rollback. Un seul atelier, panneau contextuel et poignées accessibles clavier; 1366×768/DPI 200 %, focus, contraste et mouvement réduit à mesurer sous Windows, pas réputés validés.

**Quatre rôles conservés** : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. Ne pas ajouter un quatrième `Artifact.use` V1. Aucun prévol logiciel ne certifie Design Space ni découpe physique.

## Tests proposés — aucun exécuté
- **Positif P1** : sélection A02→A03, trou conservé, preview A09, Undo, source SHA et masque float32 identiques après annulation.
- **Positif P2** : groupe couleur A11/A12 converti en SVG d'édition sans le présenter comme SVG CUT; inspecter rôle, unités et provenance.
- **Positif P3** : B04 déplacement/rotation sur brouillon, géométrie finie, identité inchangée; sortie persistante interdite tant que schéma non validé.
- **Négatif N1** : source CAS modifiée entre preview et commit → conflit, zéro écriture et proposition de reprise.
- **Négatif N2** : masque de dimensions différentes ou trou absorbé par booléen → erreur et original conservé.
- **Négatif N3** : texte avec police/glyphe manquant ou licence inconnue → diagnostic, aucune substitution silencieuse.
- **Négatif N4** : XML SVG actif, coordonnées NaN ou profil machine UNKNOWN → refus de certification et aucun export trompeur.
- **Négatif N5** : modèle absent, OOM GPU, téléchargement refusé → repli CPU/manuel sans réseau implicite.
- **Récupération** : crash avant/après writer, concurrence entre deux fenêtres, disque plein, Undo/Redo, fermeture durant job, sortie externe no-clobber; fixtures synthétiques uniquement. UI Windows, GPU RTX, Design Space et coupe réelle sont des **gates indépendants NOT_RUN**.
- **Performance** : instrumenter latence p50/p95 et pic RAM/VRAM sur corpus déclaré, fixer seuils avant exécution; aucun chiffre inventé.

## Micro-lots TDD et critères de sortie
1. **18A-1** : retrouver pour A01–A16/B01–B14 chaque ID historique S/R33, ticket V34, test T-V34 et DoD; statut UNASSIGNED tant que non confirmé. *DoD : 30 lignes avec liens exacts et absence de contradiction vérifiée.*
2. **18A-2** : valider au HEAD courant les ports de code et tous consommateurs de `editor_v216`, `project_workspace_g22`, `NativeAtelierPanel`, exporteurs. *DoD : blobs et diff main/PR exacts, absence de second writer.*
3. **18A-3** : confronter les trois divergences A04/A08/A16 et les dix exigences G6/G9 à une revue indépendante; documenter décision contraire et coût/dépendances. *DoD : acceptation ou rejet motivé, sans suppression historique.*
4. **18A-4** : tests contractuels et adversariaux ci-dessus, puis UI Windows/DS/physique séparément par producteur autorisé. *DoD : preuves exact SHA et statuts PASS/FAIL/SKIP/NOT_RUN, jamais inférés.*

## Contrôle des 25 axes — revue documentaire
01–05 : inventaires 24/141/140/80/437 conservés, **30 IDs examinés**, liens exacts et critères complets **OUVERTS**; 06 preuves séparées; 07 projet V1/CAS/float32; 08 quatre exports; 09 profils tri-state; 10–13 parcours, Undo, clavier, erreurs et reprise proposés, UI non testée; 14 IA opt-in; 15 raster/alpha/HD; 16 géométrie et topologie; 17 batch/Fabrique **N/A à cette tranche** (sans suppression du programme); 18 Delivery **N/A à cette tranche**; 19 propositions #141 hors arbitrage de cette tranche; 20 protocole performance sans résultat; 21 fixtures synthétiques, licence et confidentialité; 22 branche documentaire uniquement; 23 refus de second store/writer; 24 adoption/revue/CI **OUVERTES**; 25 aucune compression d'obligation, les trois divergences restent visibles jusqu'à décision.

**Bilan honnête :** 30/80 décisions candidates passées en revue croisée initiale, **0/30 certifiées par rapprochement exhaustif**, 431/437 liens TEST→TICKET historiques (six exceptions conservées), dix exigences G6/G9 sans ticket V34 explicite; 24/141/140/80/437 inventoriés, non validés sémantiquement. Aucune exécution de tests ni modification produit.

**Prochaine action unique : COV-18A-1**, établir les 30 correspondances exactes A/B vers exigences, tickets, scénarios et DoD, puis confronter les arbitrages A04/A08/A16 aux critères historiques. Ne pas refaire les cinq audits COV17.
