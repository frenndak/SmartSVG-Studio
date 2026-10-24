# SmartSVG Studio V21.12 — Démarrage rapide

## IA : état exact

La V21.12 intègre **un orchestrateur réellement capable d'appeler les nœuds installés de ComfyUI-RMBG** : `BiRefNetRMBG` (`BiRefNet_lite`, puis `BiRefNet-general`), `RMBG` (`RMBG-2.0`), et `SAM2Segment` (`sam2.1_hiera_tiny` + `GroundingDINO_SwinT_OGC (694MB)`). Les signatures de ces trois nœuds ont été comparées avec les sources de ComfyUI-RMBG 3.3.0 (20 octobre 2026).

**Ce ZIP ne contient aucun modèle IA** et ne garantit pas que leurs poids soient installés. La présence d'un nœud ne confirme pas que l'inférence réussira. Les tests de cette livraison utilisent des modèles simulés, pas la RTX 3070 de l'utilisateur.

## Installation

1. Fermer ComfyUI.
2. Retirer les anciennes copies de SmartSVG de `ComfyUI/custom_nodes` (les conserver ailleurs en sauvegarde).
3. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.12` dans `ComfyUI/custom_nodes`.
4. Depuis ComfyUI-Manager, installer ou mettre à jour **ComfyUI-RMBG** et ses dépendances dans **le même environnement Python** que ComfyUI. Les téléchargements éventuels des poids de modèles sont gérés par RMBG lors de la première exécution.
5. Redémarrer ComfyUI et rafraîchir le navigateur.
6. Ouvrir `example_workflows/SmartSVG_Studio_V21_12_00_Diagnostic_IA.json`, puis exécuter. *Contrat compatible* ne signifie pas *modèle testé*.
7. Ouvrir `SmartSVG_Studio_V21_12_01_Express_Auto_IA.json`, choisir un fichier avec `LoadImage`, laisser le mode `Si disponible` et exécuter.

## Quand utiliser les autres workflows

- `..._02_Corriger_Exporter_IA.json` : segmentation, vérification/correction du masque puis export. **Relancer le workflow après sauvegarde des retouches**.
- `..._03_Capture_IA_Guidee.json` : prérecadrage des captures d'écran avant détourage. L'export est **désactivé au départ** ; ne l'activer qu'après validation du masque.
- PNG transparent : connecter la sortie `MASK` de `LoadImage` à l'entrée optionnelle `alpha_loadimage` ; sa polarité est inversée automatiquement par SmartSVG. Un masque utilisateur de type *sujet=blanc* doit au contraire arriver par `masques_objets`.

## Trois modes IA, inchangés

- `Désactivée` : alpha + dessins sur fond blanc uniquement.
- `Si disponible` (par défaut) : d'abord alpha / heuristique, puis IA si nécessaire. Essais: BiRefNet, RMBG, SAM2, avec contrôle des masques et repli sans faux rectangle.
- `Obligatoire` : forcer une nouvelle inférence IA, même si une solution simple existe. Demande une extension IA installée.

Le mécanisme automatique **ne comprend pas forcément quel objet tu souhaites conserver** ; même avec un masque valide, vérifier l'aperçu avant la découpe Cricut.

## Cricut Explore 5

Importer un PNG transparent du dossier `00_IMPORTER_DANS_CRICUT` dans Design Space comme **image aplatie / Flat Graphic**, puis choisir **Imprimer puis découper**. Ne pas superposer le SVG de contour au PNG pour ce même Print Then Cut. Contrôler les dimensions, les trous, les îlots et la silhouette après import.

Un SVG contour seul sert à découper, pas à conserver les couleurs imprimées ; un PNG aplati ne rend pas indépendamment modifiables les détails internes de l'illustration.

## Limites et sécurité

- Maximum 5 MP par image dans l'étape automatique ; 12 résultats au maximum par tentative IA ; masque de sortie limité et contrôlé. Éviter d'autres charges GPU sur la RTX 3070 8 Go.
- L'adaptateur n'invente jamais un masque pour masquer un échec : mode sticker = **erreur explicite** si aucun contour crédible ; le mode carte rectangulaire demandé reste disponible.
- Le contrôle topologique vérifie forme et dimensions, **pas le bon choix du sujet**. Aucun modèle ni découpe physique n'a été testé dans cette archive.
- Les poids des modèles peuvent être téléchargés par ComfyUI-RMBG lors du premier essai : surveiller l'espace disque et les connexions réseau si nécessaires.

## Tests

Dans le dossier de l'extension :

```bash
python verify_package_v2112.py --integrity-only
python verify_package_v2112.py --quick
python verify_package_v2112.py --suite 1
# Répéter --suite 2 ... --suite 12 pour les anciens tests, séparément.
```

`node` (Node.js) sert uniquement aux tests frontend JavaScript.
