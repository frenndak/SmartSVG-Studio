# SmartSVG Studio V21.11.1 — Installation et utilisation

## Installation

1. **Fermer ComfyUI** ; déplacer les anciennes copies de SmartSVG hors de `custom_nodes` (ne pas conserver simultanément deux versions).
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.11.1` dans `ComfyUI/custom_nodes/`.
3. Redémarrer ComfyUI et rafraîchir la page (Ctrl+F5 si besoin).
4. Ouvrir un workflow `SmartSVG_Studio_V21_11_...` fourni sous `example_workflows`.

## Quel workflow ?

- `01_Auto_Simple.json` : image directe vers Express. Pour un **PNG transparent**, les fils IMAGE et MASK du nœud natif `LoadImage` sont déjà raccordés au nouveau nœud AutoExpress.
- `02_Auto_Corriger_Exporter.json` : image -> masque automatique -> éditeur unifié -> Express. L'entrée `alpha_loadimage` est raccordée au MASK de `LoadImage`, sans l'inverser manuellement.
- `03_Capture_Auto_Correction.json` : recadrage d'une capture d'écran opaque avant segmentation. L'alpha original n'est **pas** raccordé, car le recadrage modifierait les dimensions du masque ; pour un PNG transparent, privilégier les workflows 01/02.

### Sémantique des masques — important

| Port | Entrée attendue | Inversion à effectuer soi-même |
|---|---|---|
| `alpha_loadimage` (nouveau, facultatif) | Sortie **MASK** de `LoadImage` : `1=transparent` | **Aucune** (SmartSVG inverse automatiquement) |
| `masques_objets` (facultatif) | Masque de sujet déjà prêt : `1=à conserver` | **Aucune** (déjà orienté sujet) |

Ne jamais raccorder un MASK déjà corrigé à `alpha_loadimage` : il serait inversé. Et ne jamais relier le MASK natif inversé directement à `masques_objets`.

## Export Cricut

Le résultat des stickers est dans le dossier `00_IMPORTER_DANS_CRICUT`. Importer le PNG `STICKER_..._IMPRIMER_PUIS_DECOUPER.png` dans **Cricut Design Space** comme image aplatie (*Flat Graphic*) et choisir **Imprimer puis découper**. Vérifier visuellement le trait, la dimension réelle et l'absence de découpes parasites avant de lancer l'impression. Ne **pas** superposer le fichier SVG de contour. Un PNG n'est pas un SVG multicouche modifiable.

Si le rapport indique « cadre rectangulaire ou quasi rectangulaire », le PNG peut être importé comme **carte**, mais il **ne** constitue **pas** un personnage détouré. Les contours de sticker nécessitent un masque valide.

## Vérifier l'installation

Depuis le dossier de l'extension :

```sh
python verify_package_v21111.py --integrity-only
python verify_package_v21111.py --new
python verify_package_v21111.py --javascript
python verify_package_v21111.py --suite 1
# poursuivre --suite 2 jusqu'à --suite 12 séparément
```

Node.js est nécessaire pour les tests JavaScript uniquement, pas pour utiliser l'extension.

## Limites connues

Les modèles SAM2/GroundingDINO de ComfyUI-RMBG dépendent de leur installation, de leurs versions et de la mémoire GPU. Sans un fournisseur IA compatible, les photographies ou affiches complexes peuvent être refusées en mode automatique. Les sept exemples fournis n'ont pas été tous détourés par une IA réelle sur RTX 3070 ; seule la planche des 12 escargots a été confirmée par segmentation heuristique. Il faut aussi tester le résultat dans Design Space et par une découpe Explore 5.
