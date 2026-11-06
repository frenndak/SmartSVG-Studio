# SmartSVG V3.4 — reprise après stabilisation et premier lot exports

6 novembre 2026, Europe/Paris. Registre opérationnel **non normatif** : ni nouvelle roadmap ni qualification globale. Référence code intégrée : `main@a34f2af1d65378c6f6f279ca53446833e7a2f74a`, arbre `31832ea6e68a07681a7a2c43eeb9d6b786d4cd99`, [PR #115](https://github.com/frenndak/SmartSVG-Studio/pull/115). Revalider `main`, les PR ouvertes et les checks avant une prochaine mutation. La V3.4 adoptée et les 141 exigences héritées restent inchangées.

## Reprise effective

Le [point précédent](G3_3E_REPRISE_2026_11_06.md) désignait la **tranche B : quatre contrats de sortie**. La conception des 24 lots n'est pas une implémentation de 24 lots. La pagination récemment livrée contribue à V34-136 sans livrer tags, favoris, index, duplication ou CSV.

Depuis la photographie des PR #85–94 :

- Les PR #95–106 ont notamment apporté géométrie de gabarits en mémoire, prototype natif de lecture/aperçu, thèmes et qualification de stabilisation. Voir la [matrice datée](STABILIZATION_BASELINE_2026_11_06.md), qui borne précisément les preuves Windows et navigateur.
- Les PR #107–110 ont renforcé la file de lecture, les commandes du pinceau, la syntaxe SVG du contrôle technique et le chargement des préférences.
- Les PR #111–114 ont réduit les validations répétées de l'aperçu, lié les instantanés aux octets réellement validés, corrigé les erreurs des gestes invalides, sécurisé le chargement des retouches, rendu les empreintes de fichier progressives et ajouté la navigation des projets par pages.
- La PR #115 reprend B avec un manque reproduit dans le **contrôle qualité Basic Cut de production** : groupes de coordonnées incomplets et indicateurs d'arcs invalides auparavant acceptés. Le validateur existant vérifie maintenant ces commandes ; les arcs compacts se lisent sans décalages quadratiques de liste.

## Preuves du lot #115

Candidat revu : `fc6d3e35d1d4f31ccb052a8996b22fb36e2256b4`, code local équivalent `cc5a5988e716262e4fe023248ceb4528c3b4563e` (les historiques Git local et distant ont des SHA différents). Les arbres de code utilisés pour l'intégration correspondent.

| Axe | Exécution et résultat | Limite |
| --- | --- | --- |
| Local Python 3.12 | `python -m unittest discover -s tests -p 'test_*.py' -q` : **592 tests, aucun skip** | Pas de GUI Windows |
| Local CPU | `python tools/test_engine_cpu_smoke.py` : **9 PASS** ; qualification pinceau : **46 PASS, aucun skip** | Images synthétiques, aucun modèle IA |
| Linux CI | [G0 42217194245](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42217194245) et [prévol 42217194307](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42217194307) PASS | Les skips CPU du G0 ne sont pas des réussites implicites |
| CPU CI | [42217194257](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42217194257) : **9 + 46 PASS** | Aucun essai GPU |
| Windows, Node, Chromium | [42217194306](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42217194306) : trois jobs PASS ; Windows **592, 48 skips** | Chromium : maquette DEMO sur cinq fenêtres, pas les panneaux ComfyUI réels |
| Revue indépendante | 8 tests ciblés PASS ; 5 000 séquences de tokens mutées comparées sans différence d'acceptation après optimisation | Aucun audit exhaustif de topologie SVG |
| Performance ciblée | 32 000 arcs : 0,052 s ; 64 000 : 0,108 s pour le validateur, sur le runtime de revue | Mesure synthétique, pas temps total d'ouverture ni garantie matérielle |

Le nouveau test CPU traverse `artifact_qa.audit_project` sur de vrais fichiers PNG/SVG synthétiques. Les tracés incorrects sont `BLOCKED`, les exemples valides restent `REVIEW_REQUIRED`. Sources, rapports et fichiers sont inchangés. Les polygones M/L/Z gardent leur contrôle de surface ; les chemins non polygonaux exigent toujours une revue visuelle. La borne numérique héritée reste conservatrice pour certaines grandes coordonnées compactes.

Le G0 post-fusion du code [42217338132](https://github.com/frenndak/SmartSVG-Studio/actions/runs/42217338132) est `completed/success` sur `a34f2af1d65378c6f6f279ca53446833e7a2f74a`. Revalider la révision et ses checks avant une intégration ultérieure.

## Prochaine action de code

**Poursuivre B sur les exporteurs réellement utilisés, pas créer un nouvel exporteur pour un test.** Compléter la qualification de bout en bout qui relie un contour produit par l'exporteur historique au contrôle qualité, à ses dimensions en mm et à son empreinte, puis rapprocher les sorties couleur de `smartsvg_vector/layers_v2113.py` et le PNG de `smartsvg_cricut/direct_import_v218.py`. Réutiliser `tools/test_engine_cpu_smoke.py`, `artifact_qa.py`, le manifeste de livraison et les contrôles existants ; conserver les artefacts antérieurs lors d'un échec.

Ne pas confondre les quatre contrats : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche, SVG d'édition. Le diagnostic SVG auxiliaire du transfert PNG ne prouve pas à lui seul le contrat Basic Cut. La qualification transversale des quatre sorties reste **partielle**, pas terminée par #115. Aucun changement de format `.smartsvg` n'est décidé ici.

La tranche C peut ensuite réutiliser la géométrie carte/boîte existante pour prévol et transfert CUT/SCORE guidé. Les calques/propriétés A/D, volumes E, variantes/CSV F, application Windows éditable et packaging G gardent leurs critères. Le prototype natif reste un lecteur ; pas d'installeur, de retouche native ou d'export natif complet revendiqués.

## Axes encore non qualifiés

Aucun essai utilisateur ComfyUI/GPU, rendu Tk Windows à DPI élevé, import Design Space ou découpe Explore 5 n'est prouvé par ce lot. Les quatre sorties restent distinctes et aucun résultat de contrôle local ne devient une certification physique. Les tâches planifiées n'ont pas été réactivées par cette session.
