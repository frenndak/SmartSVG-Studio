# Intégration P0 — Précontrôle SVG de découpe dans SmartSVG G1–G2

## Source de la réconciliation

Branche parente : `integration/g1-g2-archive-safety-r1` (PR #35).
Cette branche reprend deux travaux existants indépendants :

- **#25** — contrôle statique Basic Cut au moment de l'audit des artefacts réels, avec verdict `BLOCKED` sur chemins ouverts, dégénérés, fichiers actifs et dimensions inadaptées ; messages ciblés dans `release_gate_v21152.py`.
- **#31** — validation des SVG fournis par l'utilisateur et analyse de la géométrie visible : refus stylesheet et scripts, exclusions des symboles, définitions et géométries cachées des comptes de tracés, contrôles des unités et des liens.

Ces modules ont **deux points d'entrée** : le G2.7/G2.9 du navigateur construit des brouillons de sélection, tandis que le module Python d'audit inspecte les **artefacts réellement générés**. Le contrôle des dessins d'entrée est distinct de la qualité de l'export final.

## Fichiers et comportements

Les six fichiers de #25 et les deux de #31 sont portés sans réécrire le moteur historique, les nœuds ou les autres PR. Un test G0 léger vérifie que la fonction `inspect_cut_paths` bloque les formes pathologiques, conserve l'état « revue visuelle nécessaire » pour les courbes, et est reliée à l'audit qualité.

Les régressions #25 qui dépendent de Pillow, OpenCV ou du moteur réel sont présentes sous `engine/tests` mais **ne sont pas assimilées à une preuve d'exécution complète par la CI G0 standard**. Vérifier séparément dans l'installation cible.

## Livrable et limites

- Aucune certification d'import Design Space, de pression/lame, de dimensions physiques ou de découpe Explore 5.
- Aucune promesse de vectorisation intérieure : un SVG de contour ne remplace pas un SVG multicouche éditable.
- La route Express G2.7 utilise le navigateur ; Python V21.15.3 vérifie les sorties. Ils n'impliquent pas que les fichiers soient connectés automatiquement sans passer par un workflow.
- GitHub Actions vérifie des compilations/tests sur branches candidate via fusion synthétique ; les PR sources #25/#31 ne sont pas automatiquement fusionnées dans main.
- Le dépôt reste volontairement public ; aucune nouvelle ressource graphique, clé ou artwork personnel n'est ajoutée.

**Gate suivante :** revue des conflits avec le capteur G2.6 (#26–#28), puis tests Windows/ComfyUI et import physique Cricut.
