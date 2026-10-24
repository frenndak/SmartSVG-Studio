# Matrice de recette SmartSVG — V3.2

> La mise en œuvre ci-dessous est une **liste de tests**, pas un procès-verbal de validation de la dernière version du moteur.

| ID | Entrée | Sortie attendue | Contrôle automatique | Validation réelle requise |
|---|---|---|---|---|
| S-01 | PNG RGBA transparent | contour non rectangulaire, PNG préservé | alpha et masque, 1 contour | import Print Then Cut, taille réelle |
| S-02 | JPG fond blanc / 12 sujets | 12 objets distincts sans fusion | quantité, bbox, absence de recouvrement | aperçus individuels et découpe |
| S-03 | image complexe avec décor | IA optionnelle ou demande de retouche | refus honnête, aucune fausse promesse | inférence locale si disponible |
| S-04 | JPG photographié sur écran | pré-recadrage / sélection sûre | pas de masques inventés | sélection et visibilité |
| S-05 | SVG coeur simple | silhouette Basic Cut | XML, unités, chemin | ouverture dans Design Space |
| S-06 | SVG multicouche | géométries séparées par couleur | plusieurs objets, pas de raster encapsulé | éditabilité réelle Design Space / Inkscape |
| S-07 | SVG anneau avec trou | conserver trou intérieur | topologie de chemins | découpe intérieure réelle |
| S-08 | passage fin | alerte de fragilité | épaisseur physique avec taille mm | essais matériaux et lame |
| S-09 | 24 objets | performances, séparation, reprise | 24 sorties nommées et contrôle SHA | inspection sur machine de découpe |
| S-10 | grand raster | diagnostic mémoire lisible | seuils OOM / budget pixel | RTX 3070 8 Go |
| S-11 | workflow ComfyUI hérité | anciens IDs/ports conservés | chargement, signature, snapshots | ComfyUI récent avec frontend réel |
| S-12 | erreur, interruption, dossier occupé | sortie atomique et reprise | injection de panne | reprise utilisateur |
| S-13 | SVG lien externe ou script | refuser le contenu actif | `inspect_svg_contracts.py` | vérifier retour UI clair |
| S-14 | ZIP malveillant | refuser extraction | `validate_release_archive.py` | aucune donnée écrasée |

## Niveaux de preuve

- **L0 — Documenté** : cas et résultats attendus, sans exécution.
- **L1 — Synthétique** : tests unitaires sur fixtures originales, GitHub Actions CPU.
- **L2 — Application locale** : import réel sous ComfyUI, modules IA installés et versions notées.
- **L3 — Fabrication** : tests Design Space + impression/découpe avec machine, réglages et matériaux consignés.

On ne peut pas déduire L2/L3 d'un résultat L1. Le rapport de test doit mentionner la version SmartSVG, le SHA de commit, l'image, les versions de dépendances, les réglages, les limites et le résultat mesuré. Aucun téléchargement automatique de modèles IA sans consentement et sans suivi des poids et licences.

## Commandes G0 depuis la racine du dépôt privé

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tools/inspect_svg_contracts.py examples/synthetic/02_decoupe_coeur.svg --profile cut --json
python tools/inspect_svg_contracts.py examples/synthetic/03_multicouche_editable.svg --profile editable --json
mkdir -p examples/generated
python tools/make_synthetic_pngs.py --out examples/generated
```

**Ne pas présenter la création des PNG comme une certification Cricut.**
