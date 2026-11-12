# SmartSVG Studio V3.5 — Roadmap de conception candidate

> **NON NORMATIVE / DRAFT**, ouverte le 12 novembre 2026. La roadmap **V3.4 reste ACTIVE pour le développement** jusqu'à une promotion documentaire et de gouvernance séparée, vérifiée, revue et autorisée. Aucun nouveau code ni test produit n'est réputé livré par ce document.
>
> **Point de départ historique vérifié :** [main@aa0ff9e7](https://github.com/frenndak/SmartSVG-Studio/commit/aa0ff9e7d0c53dba3fdc429c02c6198736cfe935) (12/11/2026). La branche main continuera à évoluer : ne pas confondre ce repère documentaire avec le HEAD réel.
>
> **Issue maîtresse du programme :** [#142 — conception V3.5](https://github.com/frenndak/SmartSVG-Studio/issues/142). Source des propositions [#141](https://github.com/frenndak/SmartSVG-Studio/issues/141), source UX [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134).

## 1. Mission et contrat de non-régression

Produire une nouvelle roadmap complète, directement exécutable par micro-lots et plus approfondie que V3.4, **sans réécrire ni effacer les exigences héritées**. Objectif final : un véritable studio Windows autonome, local-first, express-first mais puissant, ComfyUI facultatif, traitement raster et vectoriel, fabrication Explore 5 avec prévols réalistes, quatre exports distincts, gestion de projets et automatisations IA facultatives.

La V3.5 hérite **intégralement et sans perte** des **24 documents de conception V3.4**, **141 exigences V3.3**, **140 tickets V34**, **437 scénarios proposés à inventorier en détail**, ainsi que des **80 fonctions candidates UX**. Voir [photographie indexée](INHERITANCE_REGISTER.md) : **24/141/140/80 identifiants inventoriés**, ce qui ne constitue **ni spécification V3.5 terminée, ni qualification fonctionnelle**.

Les archives V3.2/V3.3, la V21.14.1 figée et les spécifications V3.4 restent intactes. La V3.5 ne devient jamais l'autorité au seul motif de l'existence de cette branche.

## 2. Piliers de conception à approfondir

| Domaine V3.5 | Périmètre obligatoire et nouvelles possibilités | Sources V3.4 dominantes |
|---|---|---|
| 01. Contrats, sécurité, preuve | projet V1/CAS/identités/float32, reprise, révisions, traçabilité, format V2 uniquement explicitement migré ; tests et preuves | 01, 03–06, 22–24 |
| 02. Parcours débutant, expert et design system | accueil, Express, canevas, Undo/Redo, calques/objets/texte, inspection, accessibilité ; arbitrage mesuré Tk/Qt/Tauri | 02, 07, 18, annexe UX |
| 03. Import, détection et masques | PNG/JPEG/WebP/SVG, sécurité et quotas, miniatures, sujets multiples, masques et affinage CPU/IA | 04, 10, 12 |
| 04. Raster, vectorisation et édition | transparence, nettoyage/anti-halo, upscale conditionnel, courbes/topologie, centre de trait, vrai SVG éditable | 12, 13, 18 |
| 05. Fabrication physique | CUT/SCORE/DRAW/PRINT/FOIL distincts, Explore 5, patrons, Smart Cut Advisor, Smart Weeding contrôlé, suivi de compatibilité Design Space | 14–16, 22 |
| 06. Export et **Smart Delivery** | 4 rôles de sortie réels, premier ZIP dès un format sain, manifeste et hash, guide hors ligne, provenance, confidentialité, régénération | 05, 17, 20, 22 |
| 07. Planche, bibliothèque et personnalisation | nesting 12/24/50, reprise, CSV, collections, prénoms/numéros/QR, recettes, Smart Cost indicatif | 19, 20 |
| 08. Automatisation et IA locale | fournisseurs optionnels, conseil contextuel, consentement, modèles/licences/hash, CPU/GPU, génération/réparation locale, OOM/récupération | 08–11, 12 |
| 09. Expérience Windows, déploiement | Windows natif sans ComfyUI, installation/mises à jour/rollback, modes d'échec, hors ligne, profils et accessibilité | 04, 21 |
| 10. Validation réelle et orientations futures | corpus synthétique, Windows, RTX, Design Space, coupe physique distincts ; feedback photo, profils multimarques et optimiseur multicritère seulement P2 exploratoire | 15, 22, 24 |

**Important :** ces dix domaines sont une **navigation de la nouvelle conception**, **pas dix nouveaux stores/moteurs**. Le registre [INHERITANCE_REGISTER.md](INHERITANCE_REGISTER.md) conserve explicitement les 24 lots V3.4 sources, les 140 tickets, les 141 exigences et les 80 IDs UX.

## 3. Priorités et jalons de livraison

- **P0 socle réel :** import → projet → édition → sauvegarde/reprise → export avec vrais fichiers ; prévol/QA ; traçabilité code–ticket–interface–test ; aucun affaiblissement des 141 exigences.
- **P1 différenciation utile :** Smart Delivery SD0/SD1/SD2, Smart Cut Advisor, Print Then Cut Assistant, compatibilité Design Space versionnée, UX de sélection/nettoyage avancé, expertise UI mesurée, Smart Weeding en diagnostic non destructif.
- **P2 capacités avancées / à conditionner :** Smart Delivery reproductible/versions, Smart Cost, séries personnalisées poussées, Weeding générateur de chemins après preuve matérielle, recettes partageables ; R&D photo-feedback, autres machines, optimisation multicritère.
- **Jalon A :** une application Windows réellement utilisable ; **B :** studio complet avec quatre exports et workflows ; **C :** accélérations et intelligence locale. Les jalons A/B/C sont des **étapes de qualification**, pas une permission d'abandonner les obligations héritées.

## 4. Travail incrémental sans simplification destructrice

Chaque cycle horaire d'architecture reprend le **dernier micro-lot effectivement terminé** et :
1. Revalide le HEAD de `main`, les PR ouvertes, l'issue #142, les progrès de la branche et les sources V3.4 concernées ; ne traite pas un commentaire GitHub comme une fusion ou un test exécuté.
2. Établit **un progrès documentaire inspectable** : besoin réel, scénario novice et expert, conception UI interaction/erreur/reprise, contrats d'E/S/versions, architecture/autorités, sécurité/licences, mémoire/performance, preuves et micro-tickets avec DoD.
3. Fait une contre-expertise hostile, cherche les doublons contre #134/#141, V34 et OPPORTUNITIES ; ajoute des tickets V35 UNIQUEMENT pour véritables capacités nouvelles.
4. Met à jour la traçabilité **des 24 lots, 141 exigences, 140 tickets, 80 IDs** et inventorie les **437 recettes proposées** sans marquer de PASS fictif ; distingue code sur branche/main/Windows/RTX/Design Space/physique.
5. Publie un changement concret sur cette branche si les outils le permettent, sinon une fiche substantielle #142, et inscrit les preuves dans PROGRESS. Ne pas multiplier les PR documentaires ni perturber la tâche de développement.
6. Conserve **la profondeur de contre-expertise** : la réduction de longueur du prompt n'est jamais un résultat ; seules des lectures évitées à SHA inchangé, des fiches plus solides et une couverture explicitement contrôlée constituent une optimisation.

## 5. Documents et états

- [INHERITANCE_REGISTER.md](INHERITANCE_REGISTER.md) — photographie exhaustive des identifiants V3.4 + UX à conserver, non-qualification explicite.
- [SCENARIOS_V34_INDEX.md](SCENARIOS_V34_INDEX.md) — **437/437 scénarios historiques inventoriés individuellement**, avec sources, lignes, SHA et trois fichiers de copies ; **liens sémantiques aux exigences restant à qualifier**.
- [PROGRESS.md](PROGRESS.md) — journal de préparation et prochaines étapes.
- **Futurs livrables à créer progressivement :** `COVERAGE_V34_TO_V35.md`, `BACKLOG_AND_DEPENDENCIES.md`, `UX_ARCHITECTURE_AND_WORKFLOWS.md`, `QUALITY_TESTS_AND_EVIDENCE.md`, `ADR_RISKS_OPPORTUNITIES.md`, `PROMOTION_CHECKLIST.md`. Une mention FUTUR n'est pas un fichier déjà présent.

## 6. Condition stricte de promotion

**La V3.4 reste la roadmap principale en production.** Pour promouvoir V3.5 : vérifier 24/24, 141/141, 140/140, 80/80 et 437 scénarios traçables ; exécuter l'intégrité documentaire ; résoudre contradictions et dépendances ; obtenir revue/CI d'une PR documentaire contrôlée et, **séparément**, une modification autorisée et revue d'AGENTS.md et de la gouvernance. Aucune tâche horaire n'est autorisée à fusionner des docs normatives ou changer AGENTS.md automatiquement.

**Statut présent :** CANDIDATE / EN CONCEPTION. Aucune qualification Windows, GPU, Design Space ou coupe physique attribuée à V3.5.
