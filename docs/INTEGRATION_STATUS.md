# SmartSVG Studio — statut d'intégration (26 octobre 2026)

## Source authentique admise (G0)

- Archive historique V21.15.2 conservée dans `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
- SHA-256 de l'archive : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Import initial de **652 fichiers** sous `engine/` et **651 empreintes internes** du manifeste confirmées.
- Admission documentée par `docs/IMPORT_V21_15_2.json`, `docs/SOURCE_V21_15_2_PROVENANCE.json`, et CI G0.
- Les résultats d'admission consignent **876 tests Python** et **12 scripts JS** dans un environnement contrôlé ; leur réussite sur la machine finale reste à confirmer.
- `.automation/READY` présent : autorisation de **proposer des PR de développement**, pas de fusionner automatiquement ni de certifier un résultat matériel.
- Roadmap canonique `docs/ROADMAP_MASTER_v3_2.md` conservée et figée.

## Deux contrôles à ne plus confondre

1. **Provenance historique de V21.15.2** : `python tools/verify_source_integrity.py --repo .` compare strictement l'archive et l'intégralité du moteur *tel qu'importé*. Il n'est approprié qu'à un snapshot G0 inchangé.
2. **Intégrité de l'archive conservée durant le développement** : `python tools/verify_source_integrity.py --repo . --archive-only` vérifie le SHA-256 de l'archive et les 651 empreintes internes, sans exiger que le moteur en cours d'évolution reste identique à V21.15.2. Des tests applicatifs et la revue du diff doivent contrôler chaque évolution du moteur.

Les tests de provenance ne prouvent pas que des changements fonctionnels du moteur sont corrects. Une CI G0 verte n'est pas une certification GPU, ComfyUI ou Cricut.

## Dépôt public et automatisation (état constaté)

- Dépôt canonique `frenndak/SmartSVG-Studio` : **public** ; `main` contient la source historique admise. L'ancien dépôt `frenndak/SmartSVG-Automation` reste un orchestrateur hérité, non nécessaire au futur contrôle gratuit local au dépôt canonique.
- PR #30 : migration candidate du précontrôle public vers `.github/workflows/public-autonomous-cycle.yml`. Un run `pull_request` du workflow a réussi sur son HEAD `4f75f0ddb4b72fff70df4c7f59816cae80ae26ad` ; cela **ne prouve pas** que les cron sont actifs sur `main`, ni qu'un agent développe du code.
- Le workflow historique `.github/workflows/private-ai-development.yml` reste présent sur `main` et dépend de paramètres d'activation et éventuellement d'une API payante. Ne pas activer les dépenses ni les dispatch inter-dépôts à l'aveugle.
- Développement via tâches ChatGPT et connecteur GitHub : méthode distincte des GitHub Actions ; chaque écriture doit être confirmée par commit, PR et CI réelle.
- **PR G1/G2 empilées :** #14 à #28 incluent des bases intermédiaires. Vérifier l'ascendance, les variantes concurrentes et les tests de chaque HEAD avant intégration ; une PR fille verte ne valide pas automatiquement les parents.
- La roadmap `docs/ROADMAP_MASTER_v3_2.md` est une **spécification historique figée** ; son statut B0 V21.14.1 ne doit pas être confondu avec le moteur V21.15.2 actuellement importé.

## Vérifications L2/L3 encore requises

- ComfyUI chargé réellement, signatures des nœuds, compatibilités ;
- Inférence modèle et mémoire GPU de la RTX 3070 8 Go ;
- Import réel PNG Print Then Cut, SVG découpe et SVG multiforme éditable dans Design Space ;
- Découpe physique Cricut Explore 5, dimensions en mm et défauts constatés.

**Principe :** la source d'origine reste authentique et immuable ; le code actif peut évoluer dans des PR testées. Aucun avis automatisé ne vaut preuve matérielle.
