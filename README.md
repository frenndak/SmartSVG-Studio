# SmartSVG Studio — source privée

## Statut : V21.15.2 importée et vérifiée

- Archive binaire authentique : `source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip`.
- Moteur extrait : `engine/` (**652 fichiers**, vérifiés octet pour octet contre le ZIP).
- SHA-256 de l'archive : `9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54`.
- Manifeste : `INSTALLATION_MANIFEST_V21_15_2.json`, 651 empreintes internes conformes.
- GitHub : PR #6 fusionnée dans `main`, vérification G0 CI réussie.
- Régressions exécutées localement : **876 tests Python** (Python 3.13.5), **12 scripts de tests JavaScript** (Node 22.16.0), tous passés dans l'environnement contrôlé.
- Référence produit : `docs/ROADMAP_MASTER_v3_2.md`, figée avec SHA-256.
- Preuves et limites : `docs/IMPORT_V21_15_2.json` et `docs/SOURCE_V21_15_2_PROVENANCE.json`.

Ces tests ne prouvent pas une exécution des modèles IA sur RTX 3070, ni une ouverture réelle dans ComfyUI/Design Space, ni une découpe physique Cricut Explore 5.

## Développement contrôlé

Le marqueur `.automation/READY` atteste uniquement l'admission du code pour **proposer des pull requests de développement**. L'agent ne doit pas fusionner de PR ni déclarer des jalons de fabrication validés.

L'orchestration publique est dans `frenndak/SmartSVG-Automation` ; elle ne récupère plus les sources et ne fait que déclencher un événement. Le travail Codex se fait **dans ce dépôt privé** au moyen de `.github/workflows/private-ai-development.yml`.

Pour que l'automatisation effectue effectivement des changements, il faut encore, dans GitHub Settings :
1. Déposer `OPENAI_API_KEY` comme secret Actions **sur ce dépôt privé uniquement** (utilisation API facturée séparément).
2. Configurer la variable Actions privée `SMARTSVG_AUTOMATION_ENABLED=true`.
3. Configurer sur le dépôt public son jeton **SMARTSVG_DISPATCH_TOKEN** limité au dépôt privé et sa propre variable d'activation.
4. Lancer un cycle manuel de contrôle et relire les PRs privées générées avant de maintenir les déclenchements réguliers.

Tant que ces paramètres ne sont pas renseignés, les tâches GitHub de développement IA ne sont pas effectives. La revue GPT horaire est indépendante de l'exécution API de GitHub.

## Vérifications reproductibles

```bash
python tools/verify_source_integrity.py --repo .
python -m unittest discover -s tests -p 'test_*.py' -q
cd engine
python -m unittest discover -s tests -p 'test_*.py' -q
for f in tests/*.mjs; do node "$f"; done
```

Les tests applicatifs historiques peuvent nécessiter du temps et des dépendances variables suivant la machine ; conserver les journaux, versions et limites.

**Ne pas supprimer l'archive originale ni la roadmap figée.**
