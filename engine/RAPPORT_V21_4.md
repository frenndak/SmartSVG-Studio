# SmartSVG Studio V21.4 — rapport de développement et validation

Version : 21.4.0 · 23 octobre 2026

## Objectif atteint

Début de la refonte structurelle **progressive**, avec cinq zones fonctionnelles explicites et trois nœuds V21.4 mis en avant. Aucun ancien moteur de fabrication/IA n'a été déplacé ou modifié à ce stade : seuls `__init__.py`, de nouveaux modules, workflows, documentations et vérificateurs sont ajoutés. Les 314 autres fichiers répertoriés par le manifeste V21.3.2 restent bit à bit identiques.

## Architecture ajoutée

- `smartsvg_core/` : validation des choix de traitement, rapports lisibles, garde-fous de données.
- `smartsvg_ai/` : accès au diagnostic existant, sans chargement d'inférence.
- `smartsvg_vector/` : analyse SVG XML bornée et sans DTD.
- `smartsvg_cricut/` : audit non destructif des dimensions PNG/SVG déclarées.
- `smartsvg_compat/` : registre de nœuds conservant les identifiants historiques.
- `node_v214.py` : interface ComfyUI 21.4, ports identiques à 21.3.2.
- `audit_structure_v214.py` : analyse AST statique et indépendante de PyTorch.
- `verify_package_v214.py` : intégrité SHA-256, héritage et tests en quatre familles.

La structure historique reste volumineuse : l'audit compte **97 modules Python hors tests**, dont **30 `node_v*`** et **15 validateurs historiques**. Les sous-packages sont introduits sans migration brutale pour l'instant. La recherche ComfyUI expose toujours les anciennes classes : une réduction réelle du nombre de nœuds visibles n'est pas encore faite.

## Compatibilité

- 64 identifiants de classes ComfyUI exportés, anciennes classes incluses.
- Les trois nouvelles classes `SmartSVGExpressV214`, `SmartSVGInstancesV214`, `SmartSVGDiagnosticV214` reprennent exactement les anciens ports d'entrée/sortie.
- 8 workflows V21.4 validés (ports, widgets, valeurs de sélection, liens).
- 314 fichiers historiques de V21.3.2 (hors son point d'entrée racine) conservés à l'identique par SHA-256.
- Toutes les opérations d'image et de fabrication passent encore par les moteurs déjà testés.

## Résultats automatisés

| Famille | Tests réussis |
|---|---:|
| Vectorisation et anciennes versions | 50 |
| Moteurs photo/IA V19–V20.3 | 300 |
| Moteurs récents V20.4–V21.3.2 | 227 |
| Nouveaux tests structurels V21.4 | 20 |
| **Total** | **597** |

Les tests ont réussi depuis l'archive réinstallée. La troisième famille a été relancée isolément après un dépassement du temps disponible lors d'un enchaînement ; elle a réussi (227/227) en exécution directe, puis avec le vérificateur indépendant.

### Tests comparatifs des vrais fichiers

- Cas synthétique : V21.3.2 et V21.4 produisent les mêmes PNG et SVG par empreinte SHA-256.
- **Planche Pokémon réelle fournie** (1536 × 1097 pixels) : 24 sujets extraits dans les deux versions ; **77 fichiers PNG/SVG comparés, 77 fichiers identiques**.

Cela prouve la non-régression des scénarios contrôlés, pas la conformité d'une découpe physique.

## Correctifs et garde-fous supplémentaires

- Vérification préalable des paramètres UI, notamment interdiction des largeurs non finies (`NaN`, infini), hors limites et des résolutions inconnues.
- Messages qui ne confondent plus les masques fournis, une inférence simplement demandée et une validation réelle.
- Résumé UI borné pour ne pas afficher un rapport JSON complet dans une bulle de texte.
- Lecture SVG racine avec rejet des DTD, liens symboliques et fichiers excessifs.
- Avertissement sur les tailles incohérentes entre PNG/SVG quand ces mesures existent.
- Contrôle anti-collision des identifiants de nœuds.

## Limites importantes

1. **V21.4 n'est pas encore une refonte complète** : les moteurs restent à plat pour préserver l'import des anciens workflows.
2. **64 nœuds exposés** : la catégorie Legacy reste visible. Une interface réellement compacte reste à développer en V21.5.
3. Pas de test réel des poids Florence-2/SAM2/BiRefNet sur RTX 3070 8 Go.
4. Pas de test physique Cricut Explore 5. Les tailles d'import et le Print Then Cut doivent toujours être contrôlés dans Design Space.
5. Les PNG à 300/450 ppp ne créent pas des détails source inexistants ; les SVG entièrement modifiables par couleur restent un chantier séparé.

## Suite recommandée

**V21.5** : un panneau Express guidé, outils Experts masqués ou accessibles séparément, meilleure visualisation du statut de chaque objet et préparation du futur éditeur de contours. Migrer ensuite les moteurs vers les packages de façon incrémentale après tests dédiés, et effectuer les essais GPU réels.
