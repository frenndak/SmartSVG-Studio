# SmartSVG Studio — statut d'intégration (24 octobre 2026)

## Source authentique admise (G0)

- Archive V21.15.2 sauvegardée en privé dans `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
- SHA-256 de l'archive : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Import initial de **652 fichiers** sous `engine/` et **651 empreintes internes** du manifeste confirmées.
- Admission documentée par `docs/IMPORT_V21_15_2.json`, `docs/SOURCE_V21_15_2_PROVENANCE.json`, et CI G0.
- Les résultats d'admission consignent **876 tests Python** et **12 scripts JS** dans un environnement contrôlé ; leur réussite sur la machine finale reste à confirmer.
- `.automation/READY` présent : autorisation de **proposer des PR privées de développement**, pas de fusionner ou publier automatiquement.
- Roadmap canonique `docs/ROADMAP_MASTER_v3_2.md` conservée et figée.

## Deux contrôles à ne plus confondre

1. **Provenance historique de V21.15.2** : `python tools/verify_source_integrity.py --repo .` compare strictement l'archive et l'intégralité du moteur *tel qu'importé*. Il n'est approprié qu'à un snapshot G0 inchangé.
2. **Intégrité de l'archive conservée durant le développement** : `python tools/verify_source_integrity.py --repo . --archive-only` vérifie le SHA-256 de l'archive et les 651 empreintes internes, sans exiger que le moteur en cours d'évolution reste identique à V21.15.2. Des tests applicatifs et la revue du diff doivent contrôler chaque évolution du moteur.

Les tests de provenance ne prouvent pas que des changements fonctionnels du moteur sont corrects. Une CI G0 verte n'est pas une certification GPU, ComfyUI ou Cricut.

## Automatisation effective

- Orchestrateur public : `frenndak/SmartSVG-Automation`, strictement limité au dispatch, sans code ni secrets privés.
- Runner d'édition : `.github/workflows/private-ai-development.yml` dans ce dépôt privé, avec branches `smartsvg/auto-*`, WIP limité aux PR autonomes et revue indépendante.
- Configuration requise dans GitHub Actions : secret privé `OPENAI_API_KEY` (facturation API distincte), variable privée `SMARTSVG_AUTOMATION_ENABLED=true` ; dans le dépôt public, secret restreint `SMARTSVG_DISPATCH_TOKEN` et variable publique d'activation.
- Ces paramètres ne sont **pas certifiés présents** par les documents. Le dernier déclenchement public observé était `skipped` : il faut confirmer les paramètres effectifs et réussir un dispatch manuel de bout en bout avant d'affirmer que le développement autonome fonctionne.

## Vérifications L2/L3 encore requises

- ComfyUI chargé réellement, signatures des nœuds, compatibilités ;
- Inférence modèle et mémoire GPU de la RTX 3070 8 Go ;
- Import réel PNG Print Then Cut, SVG découpe et SVG multiforme éditable dans Design Space ;
- Découpe physique Cricut Explore 5, dimensions en mm et défauts constatés.

**Principe :** la source d'origine reste authentique et immuable ; le code actif peut évoluer dans des PR testées. Aucun avis automatisé ne vaut preuve matérielle.
