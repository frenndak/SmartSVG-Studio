# SmartSVG Studio — projet public

SmartSVG Studio développe un atelier local de préparation d'illustrations, de SVG éditables, de contours de découpe et de planches pour Cricut. Le projet n'est **pas** une alternative au pilotage de la machine par Cricut Design Space.

## Source et état réel

- Dépôt canonique : `frenndak/SmartSVG-Studio` (public), branche d'intégration `main`.
- Archive source historique V21.15.2 : `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip` ; SHA-256 : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Moteur initial importé sous `engine/` (652 fichiers ; 651 empreintes internes vérifiées à l'admission).
- Feuille de route directrice **figée** : `docs/ROADMAP_MASTER_v3_2.md`. Elle décrit aussi la baseline historique V21.14.1 ; ce n'est pas la version actuellement importée.
- État des intégrations : `docs/INTEGRATION_STATUS.md` ; migration vers le dépôt unique : `docs/PUBLIC_SINGLE_REPO_MIGRATION.md`.
- Les fonctionnalités en PR (notamment G1/G2) **ne sont pas livrées** tant qu'elles ne sont pas intégrées à `main`. Certaines PR sont empilées sur d'autres branches ; leurs tests ne prouvent pas l'intégration de leurs parents.

## Développement et automatisation

- Les changements passent par des branches et des PR, avec tests et revue des contrats historiques ComfyUI.
- Le workflow candidat `.github/workflows/public-autonomous-cycle.yml` propose un **précontrôle gratuit** à :05 et :50 UTC, ainsi qu'un contrôle sur PR. Il ne devient planifié sur `main` qu'après fusion de sa PR ; il **ne développe pas de code**.
- L'ancien dépôt `frenndak/SmartSVG-Automation` et le workflow `.github/workflows/private-ai-development.yml` constituent une architecture héritée, non requise pour les contrôles publics gratuits. Leur retrait nécessite une migration vérifiée.
- Les tâches ChatGPT indépendantes peuvent analyser le dépôt et proposer des changements via le connecteur GitHub ; un contrôle CI vert n'atteste pas à lui seul une intervention de développement.
- Aucun secret OpenAI n'est requis pour les vérifications gratuites. Les appels API payants ne doivent pas être activés sans configuration et autorisation explicites.
- Le marqueur `.automation/READY` atteste l'admission de la source pour proposer des PR, **pas** une autorisation de fusion automatique ni une certification matérielle.

## Vérifications reproductibles

```bash
python tools/verify_source_integrity.py --repo . --archive-only
python -m compileall -q engine tools tests
python -m unittest discover -s tests -p 'test_*.py' -q
cd engine
python -m unittest discover -s tests -p 'test_*.py' -q
for f in tests/*.mjs; do node "$f"; done
```

Le mode `--archive-only` vérifie la source conservée sans interdire les évolutions du moteur. La comparaison intégrale `--repo .` sans ce drapeau concerne uniquement le snapshot d'import initial. Les suites historiques peuvent demander des dépendances supplémentaires.

## Niveaux de preuve

- **L1 :** tests unitaires/CPU et CI sur le bon commit ; nécessaire pour les lots logiciels concernés.
- **L2 :** ComfyUI et inférence IA réels, notamment RTX 3070 8 Go ; non attestés par une CI CPU.
- **L3 :** import Design Space et fabrication physique sur Cricut Explore 5 ; non attestés par une CI CPU.

L2/L3 sont requis pour revendiquer les capacités correspondantes, mais pas pour chaque PR de contrat ou d'interface. Aucun export ne doit être annoncé « prêt Cricut » sur la seule base de tests simulés.

## Publication responsable

Ne pas ajouter de photos utilisateur, de contenus tiers sans licence, de secrets ou de données personnelles. L'historique Git public doit être audité séparément ; supprimer un fichier ne retire pas les copies déjà publiées. Conserver l'archive historique et la roadmap figée intactes.
