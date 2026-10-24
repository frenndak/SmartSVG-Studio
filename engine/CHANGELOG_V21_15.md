# V21.15 — 24 octobre 2026

**Objectif du lot :** établir G0 et un pré-inventaire technique G1.1 sans refondre la conversion ou l'UX. Un correctif transversal de compatibilité est autorisé.

## Nouveaux composants

- `smartsvg_governance/corpus.py` : origines vérifiables, neuf tests T et deux fixtures synthétiques R avec masques de référence.
- `smartsvg_governance/inventory.py` : vérification des graphes, identifiants, signatures et fichiers de compatibilité.
- `tools/v2115_governance.py` : point d'entrée CLI et génération des rapports.
- `governance/evidence/*` : preuves actuelles, plus modèles et risques, sans images privées.
- `tests/test_v2115_governance.py` + `verify_package_v2115.py` : contrôles et vérification du lot.

## Correctif historique

- V19.2 `SmartSVGStudioV192Expert` et `SmartSVGStudioV192Express` étaient omis du registre courant ; rétablis sans remplacement d'ID existant.
- Le champ enregistré `ia_locale` du workflow Express V19.2 est restauré par un adaptateur, sans altérer le nœud V19.2 source.

## Non-modifications

Aucun moteur de calcul, fichier de workflow, script frontend, image utilisateur ni sortie existante changé. Le seul fichier hérité modifié est `__init__.py` pour charger `node_v2115.py`.

## Pas de revendication prématurée

G0.3 reste bloqué jusqu'aux annotations humaines. Les graphes analysés ne prouvent pas la capacité à charger les workflows dans l'environnement Windows/ComfyUI du destinataire. Les sorties ne sont pas déclarées certifiées Cricut.
