# SmartSVG Studio V3.5 — Roadmap de conception candidate

> **NON NORMATIVE / DRAFT**, ouverte le 12 novembre 2026. La roadmap **V3.4 reste ACTIVE pour le développement** jusqu'à une promotion documentaire et de gouvernance séparée, vérifiée, revue et autorisée. Aucun nouveau code ni test produit n'est réputé livré par ce document.
>
> **Point de départ historique vérifié :** [main@aa0ff9e7](https://github.com/frenndak/SmartSVG-Studio/commit/aa0ff9e7d0c53dba3fdc429c02c6198736cfe935) (12/11/2026). La branche main continuera à évoluer : ne pas confondre ce repère documentaire avec le HEAD réel.
>
> **Issue maîtresse du programme :** [#142 — conception V3.5](https://github.com/frenndak/SmartSVG-Studio/issues/142). Source des propositions [#141](https://github.com/frenndak/SmartSVG-Studio/issues/141), source UX [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134).

## 1. Mission et contrat de non-régression

Produire une nouvelle roadmap complète, directement exécutable par micro-lots et plus approfondie que V3.4, **sans réécrire ni effacer les exigences héritées**. Objectif final : un véritable studio Windows autonome, local-first, express-first mais puissant, ComfyUI facultatif, traitement raster et vectoriel, fabrication Explore 5 avec prévols réalistes, quatre exports distincts, gestion de projets et automatisations IA facultatives.

La V3.5 hérite **intégralement et sans perte** des **24 documents de conception V3.4**, **141 exigences V3.3**, **140 tickets V34**, **437 scénarios proposés désormais inventoriés ligne par ligne, mais NON encore rapprochés sémantiquement des critères et tickets**, ainsi que des **80 fonctions candidates UX**. Voir [photographie indexée](INHERITANCE_REGISTER.md) : **24/141/140/80 identifiants inventoriés**, ce qui ne constitue **ni spécification V3.5 terminée, ni qualification fonctionnelle**.

Les archives V3.2/V3.3, la V21.14.1 figée et les spécifications V3.4 restent intactes. La V3.5 ne devient jamais l'autorité au seul motif de l'existence de cette branche.

## 2. Piliers de conception à approfondir

| Domaine V3.5 | Périmètre obligatoire et nouvelles possibilités | Sources V3.4 dominantes |
|---|---|---|
| 01. Contrats, sécurité, preuve | projet V1/CAS/identités/float32, reprise, révisions, traçabilité, format V2 uniquement explicitement migré ; tests et preuves | 01, 03–06, 22–24 |
| 02. Parcours débutant, expert et design system | accueil, Express, canevas, Undo/Redo, calques/objets/texte, inspection, accessibilité ; arbitrage mesuré Tk/Qt/Tauri | 02, 07, 18, annexe UX |
| 03. Import, détection et masques | PNG/JPEG/WebP/SVG, sécurité et quotas, miniatures, sujets multiples, masques et affinage CPU/IA | 04, 10, 12 |
| 04. Raster, vectorisation et édition | transparence, nettoyage/anti-halo, upscale conditionnel, courbes/topologie, centre de trait, vrai SVG éditable ; **texte éditable, polices, glyphes, licences, OCR contrôlé (G6/G9)** | 12, 13, 18 ; V3.3 G6/G9 |
| 05. Fabrication physique | CUT/SCORE/DRAW/PRINT/FOIL distincts, Explore 5, patrons, Smart Cut Advisor, Smart Weeding contrôlé, compatibilité Design Space ; **gabarits métiers étiquette/topper/carte et dioramas papier 4 plans, montage contrôlé** | 14–16, 22 ; V3.3 G6/G9 |
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

## 5. Documents et états — campagne de consolidation au 13 novembre 2026

**Les grandes rubriques de la roadmap V3.5 disposent maintenant d'un premier dossier de conception, mais leurs critères ne sont pas tous contre-expertisés individuellement.** En particulier, un inventaire 100 % ne signifie pas une adoption normative ni un produit Windows terminé.

- [INHERITANCE_REGISTER.md](INHERITANCE_REGISTER.md) — conservation des 24 lots, 141 exigences, 140 tickets et 80 capacités UX historiques.
- [SCENARIOS_V34_INDEX.md](SCENARIOS_V34_INDEX.md) — les 437/437 assertions originales, sources/SHAs, 3 inventaires ; **6 scénarios sans lien TEST→TICKET source direct**.
- [COVERAGE_V34_TO_V35.md](COVERAGE_V34_TO_V35.md) — 314 relations source réciproques, **10 exigences G6/G9 sans V34 direct**, lacunes explicitement maintenues.
- [COV10C_V1_TEXT_EXPORT_PORTS.md](COV10C_V1_TEXT_EXPORT_PORTS.md) — inspection du code réel, des API V1/CAS, édition/texte, des 4 rôles export et du packaging historique; correction d'une inversion S-037/S-064 dans COV-10B.
- [COV16_EXCEPTIONS_AND_G6_G9_OWNERS.md](COV16_EXCEPTIONS_AND_G6_G9_OWNERS.md) — **6 scénarios sans ticket explicite et 10 exigences G6/G9** étudiés individuellement avec propriétaire V3.5 **candidat**, non encore adopté.
- [BACKLOG_AND_DEPENDENCIES.md](BACKLOG_AND_DEPENDENCIES.md) — 17 unités candidates W00–W16, priorités, graphe de dépendances et jalons A/B/C sans création de 17 tickets artificiels.
- [UX_ARCHITECTURE_AND_WORKFLOWS.md](UX_ARCHITECTURE_AND_WORKFLOWS.md) — 8 parcours E2E, **80/80 capacités A01–E20** placées dans un domaine UX et une priorité de conception provisoire.
- **Contre-expertise UX individuelle V35-COV-17 (80/80 CANDIDATES, sans adoption ni exécution)** :
  - [A01–A16 — import, sélection, nettoyage, couleur, vectorisation](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md)
  - [B01–B14 — objets, calques, transformation, texte](COV17B_UX_B01_B14_SEMANTIC_AUDIT.md)
  - [C01–C18 — Cricut, fabrication, quatre exports, planches](COV17C_UX_C01_C18_SEMANTIC_AUDIT.md)
  - [D01–D12 — IA locale, modèles et consentement](COV17D_UX_D01_D12_SEMANTIC_AUDIT.md)
  - [E01–E20 — bibliothèque, Windows, UX, QA, récupération](COV17E_UX_E01_E20_SEMANTIC_AUDIT.md)
  - **Contrôle mécanique au SHA de branche** : 16+14+18+12+20 = **80 identifiants uniques**, zéro trou ou doublon ; **les 80 décisions restent proposées et leurs liens fins aux DoD historiques doivent encore être qualifiés**.
- [QUALITY_TESTS_AND_EVIDENCE.md](QUALITY_TESTS_AND_EVIDENCE.md) — tests positifs/négatifs, corruption/reprise, QA, Windows/CPU/GPU/Design Space/physique strictement séparés.
- [ADR_RISKS_OPPORTUNITIES.md](ADR_RISKS_OPPORTUNITIES.md) — ADR candidates, registres de risques, **33/33 opportunités historiques** préservées avec leurs rejets, arbitrage détaillé encore ouvert.
- [PROMOTION_CHECKLIST.md](PROMOTION_CHECKLIST.md) — **15 gates de NO-GO/GO** documentaires, revue contradictoire, PR docs puis promotion de gouvernance séparée.
- [AUTOMATION_QUALITY_CONTRACT.md](AUTOMATION_QUALITY_CONTRACT.md) — 25 contrôles obligatoires pour éviter la dégradation du prompt horaire.
- [PROGRESS.md](PROGRESS.md) — journal des opérations réellement écrites, des écarts et de la prochaine étape unique.

**État de la suite :** la **contre-expertise indépendante et la validation des 80 décisions UX candidates**, les **437 rapprochements sémantiques détaillés** (au-delà des 431 citations), l'arbitrage des **6+10 exceptions**, la validation complète des **33 opportunités**, les benchmarks UI, la contre-expertise croisée et la PR documentaire sont **encore ouverts**. Les tests produit restent distincts et ne sont PAS déduits de ces fichiers. Préserver la V3.4 active et la tâche de développement inchangée.

## 6. Condition stricte de promotion

**La V3.4 reste la roadmap principale en production.** Pour promouvoir V3.5 : vérifier 24/24, 141/141, 140/140, 80/80 et 437 scénarios traçables ; exécuter l'intégrité documentaire ; résoudre contradictions et dépendances ; obtenir revue/CI d'une PR documentaire contrôlée et, **séparément**, une modification autorisée et revue d'AGENTS.md et de la gouvernance. Aucune tâche horaire n'est autorisée à fusionner des docs normatives ou changer AGENTS.md automatiquement.

**Statut présent :** CANDIDATE / EN CONCEPTION. Aucune qualification Windows, GPU, Design Space ou coupe physique attribuée à V3.5.
