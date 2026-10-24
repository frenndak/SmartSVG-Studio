# SmartSVG Studio V21.12.1 — Détection et validation guidées

**Base :** archive V21.12 (sans remplacement des moteurs historiques). Aucun modèle IA fourni dans le paquet.

## Installation

1. Fermer ComfyUI et sauvegarder ses workflows. Retirer les copies SmartSVG antérieures de `custom_nodes` avant d'y installer **un seul** dossier `ComfyUI-SmartSVG-Studio-V21.12.1`.
2. Redémarrer ComfyUI. Pour connaître le mode de traitement sans charger de modèle, ouvrir `SmartSVG_Studio_V21_12_1_04_Reconnaitre_Image.json`.
3. Pour exporter, ouvrir `SmartSVG_Studio_V21_12_1_01_Express_Auto_IA.json`. Le nœud conserve **les 5 réglages Express** et les sorties habituelles.
4. Pour une planche à corriger, prendre `..._02_Corriger_Exporter_IA.json`. Pour une capture, `..._03_Capture_IA_Guidee.json` ; l'export reste initialement désactivé jusqu'à validation du masque.
5. Si l'image opaque est complexe, le mode « Si disponible » demande un fournisseur ComfyUI-RMBG installé. L'autodiagnostic `..._00_Diagnostic_IA.json` ne prouve que la compatibilité apparente des contrats.

## Routage V21.12.1

- Alpha présent et valide : canal de transparence prioritaire, avec inversion correcte du `MASK` de `LoadImage` uniquement sur `alpha_loadimage`.
- Dessins multicolores séparés sur fond blanc : détection conservatrice V21.11.
- **Planche de visuels sur fond noir uniforme :** nouvelle détection sans IA des objets graphiques disjoints. Les contours sont proposés comme masques, les éléments détachés sont signalés comme potentiellement manquants. Aucun fond noir photo complexe n'est présumé détourable.
- Autres scènes : route IA si configurée, sinon refus explicite. Le routeur **ne fait pas d'OCR** et ne reconnaît pas sémantiquement les personnages. Le texte des affiches et couvertures ne peut être garanti par un simple masque.

## Contrôle de qualité

Le rapport `controle_qualite_v21121` donne le nombre d'objets, les cadres, composantes, occupation et complexité des contours, et le statut `PRECONTROLE_GEOMETRIQUE_SEULEMENT` ou `REVISION_VISUELLE_PRIORITAIRE`. Aucune mention « prêt » ne constitue une certification Design Space ou Cricut.

Il faut vérifier le bon sujet, les parties détachées, la dimension dans Cricut Design Space et le bon choix de l'opération **Imprimer puis découper**. Importer le PNG transparent de `00_IMPORTER_DANS_CRICUT` comme **Flat Graphic**. Le SVG de contour ne doit pas être superposé au même PNG (double découpe).

## Exemple Pokémon

Sur l'image fournie `1000077309.png`, le moteur sans IA trouve 24 composantes majeures, mais **3 petits éléments colorés isolés** restent signalés. Il faut inspecter les contours avant tout Print Then Cut. Lors d'un essai de fabrication complète de la planche, l'export 24 sujets n'a pas achevé son exécution dans le délai de contrôle ; **ne pas qualifier ce cas de validé de bout en bout**. La planche de 12 escargots, elle, a passé le précontrôle de fabrication local.

## Tests

```sh
python verify_package_v21121.py --integrity-only
python verify_package_v21121.py --new
python verify_package_v21121.py --javascript
python verify_package_v21121.py --suite 1
```

Les 12 suites historiques se lancent isolément avec `--suite N`. Les modèles IA réels (BiRefNet, RMBG, SAM2) et la carte RTX 3070 ne sont **pas validés matériellement** par ces commandes.
