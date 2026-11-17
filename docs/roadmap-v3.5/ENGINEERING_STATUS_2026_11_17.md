# SmartSVG V3.5 — reprise d'ingénierie du 17 novembre 2026

**Photographie vérifiée :** `main@8586f81819eff5828ba862d48e0f1469fd49f21e` (17/11/2026, 19:39:49 UTC) ; cette fiche documente un état constaté, pas un verrou de branche permanent. Toujours relire le HEAD actuel avant nouvelle action.

## Résultat de la réconciliation initiale WIP

- PR [#138](https://github.com/frenndak/SmartSVG-Studio/pull/138), [#139](https://github.com/frenndak/SmartSVG-Studio/pull/139), [#140](https://github.com/frenndak/SmartSVG-Studio/pull/140) : **fusionnées** sur `main`, vérification de leurs métadonnées GitHub.
- PR [#144](https://github.com/frenndak/SmartSVG-Studio/pull/144) : **fermée sans fusion**. Les deux blobs introduits, `engine/smartsvg_core/native_brush_history_command_v34.py` (`5939909d31c8f433d39221a33c551b8ad3cd1d34`) et `tests/test_v34_native_brush_history_command.py` (`9a1fec8a99740e80a00e4fcb3253921405a53644`), correspondent **exactement** entre le HEAD de #144 et `main@8586f81819eff5828ba862d48e0f1469fd49f21e`. Le code et le test sont donc préservés ; le numéro de PR non fusionné ne constitue pas un manque de ces deux fichiers.
- Recherche des PR ouvertes à la photographie ci-dessus : **0**, WIP code **0/3**. La limite de trois PR code demeure applicable.

**Conclusion :** la phase ponctuelle `RECONCILE_EXISTING_CODE_WIP` peut être clôturée pour cette photographie. Elle ne doit pas redevenir un prétexte pour refaire le même audit au cycle suivant. Une nouvelle PR ou divergence impose une nouvelle lecture ciblée, pas une réouverture mécanique.

## Code déjà livré et preuves ciblées

- [#139](https://github.com/frenndak/SmartSVG-Studio/pull/139) : commandes d'historique pinceau et contrôles Tk avec relecture projet/identité, cas Windows réels dans la CI du candidat.
- [#155](https://github.com/frenndak/SmartSVG-Studio/pull/155) à [#159](https://github.com/frenndak/SmartSVG-Studio/pull/159) : preview multizones, persistance groupée, composition et Annuler/Rétablir locaux, avec correctif brouillon.
- [#160](https://github.com/frenndak/SmartSVG-Studio/pull/160) : scénario d'isolation de sujets voisins superposés, suite ciblée pinceau CPU **55/55 PASS** dans la PR ; les checks G0, prévol, CPU et stabilité Windows/Node/navigateur du HEAD PR sont SUCCESS. [G0 post-fusion](https://github.com/frenndak/SmartSVG-Studio/actions/runs/44161000593) SUCCESS pour `main@8586f81819eff5828ba862d48e0f1469fd49f21e`.
- [#145](https://github.com/frenndak/SmartSVG-Studio/pull/145) : premier ZIP Windows **Alpha** construit et smoke-testé sur runner ; [artefact du 14/11](https://github.com/frenndak/SmartSVG-Studio/actions/runs/43621278755) ancien, **pas** une compilation des retouches du 17/11.
- Ce ne sont **pas** des preuves d'installation sur le PC utilisateur, de GPU/RTX réel, de Design Space ou de coupe Cricut. Les quatre exports et le parcours total « source → sélection → sauvegarde → sortie machine » ne sont **pas** certifiés.

## Prochaine tranche prioritaire : W02 / W13, sélection native utile

**But observable :** dans le panneau Tk actuel, sélectionner/combiner plusieurs zones d'un *même Subject vérifié*, choisir explicitement l'intention garder/exclure, prévisualiser le résultat sans mutation, annuler une zone, sauvegarder via **l'unique writer CAS**, rouvrir et contrôler identité/révision et absence d'impact sur les Subjects voisins. Ne pas prétendre que les gestes rectangle/lasso, la segmentation IA ou les calques complets existent si non prouvés au HEAD.

**Méthode à chaque cycle :** relire `AGENTS.md`, READY, politique V35, SHA actuel, `MASTER_PRIORISE.md`, `PRODUCER_TASK_V35.md`, le code Tk et les tests actuellement invoqués ; identifier l'écart UX réel encore non couvert. Prendre **un micro-lot code+tests** sur branche PR initialement DRAFT. Vérifier positif, négatifs (mauvais Subject, révision périmée, masque invalide/sujet voisin, interruption), Undo et réouverture. Revue adverse du HEAD lors d'un cycle **ultérieur**, max un squash code/cycle lorsque tous les gates sont prouvés, puis G0 post-merge. Aucune fusion de docs, packaging, dépendances ou gouvernance par la tâche horaire.

**Suite après W02 borné :** W03, obtenir le premier export réellement déclenchable depuis le bureau pour un projet/Subject vérifié, sans confondre PNG Print Then Cut, SVG Basic Cut, SVG multicouche CUT et SVG éditable ; W04 QA/prévol et W05/06 Smart Delivery dès un export sain. Respecter les critères complets, sans roadmap supplémentaire.

**États de preuve :** code exact `main` vérifié pour les intégrations listées ; CI ciblée **PASS** lorsque décrite avec run/HEAD ; installation réelle, GPU, Design Space, découpe et assemblage **NOT_RUN** dans cette vérification. Les 24 lots, 141 critères, 140 tickets, 80 UX et 437 scénarios sont **inventaires**, pas pourcentages de produit réalisé.
