# Contre-expertise V21.10 — fusion éditeur de masques + inspection native

## Périmètre

Source V21.9.1 fournie par l'utilisateur. Ajout d'un nœud V21.10 autonome dans la chaîne ComfyUI et d'un éditeur navigateur à résolution native. **Aucun moteur de segmentation IA, vectorisation, import Cricut, HD ou Print Then Cut précédent n'est modifié.** Les anciens nœuds restent enregistrés.

## Audit — architecture et non-régression

- `node_v2110.py` hérite du registre V21.9 et expose MASK, IMAGE, diagnostic JSON dans cet ordre.
- L'option MASK permet le premier détourage manuel sans IA (masque initial vide). Les anciens workflows demeurent inchangés.
- Trois nouveaux workflows ne nécessitent plus de charger simultanément le panneau V21.6 et le panneau V21.9 : ils dirigent directement le MASK corrigé vers SmartSVG Express V21.8.
- Aucun sixième réglage Express ajouté ; les cinq paramètres historiques restent inchangés.

## Audit — rendu et résolution

- Publication d'une copie de l'image et des **masques initiaux** à la résolution source dans le dossier d'aperçu V21.9. Cela évite de compter deux fois les retouches après sauvegarde puis réexécution.
- Canvas navigateur borné à 1 600 × 1 100 pixels ; seule la zone visible est rasterisée ; limitation des images source à 5 Mp et 50 Mp masques.
- Zoom 100 % utilise les pixels natifs, non l'agrandissement d'une miniature 760 px. Le zoom maximal est 1 600 %.
- La représentation JavaScript des traits est indicative : Pillow/Python rejoue les traits et produit l'unique masque de fabrication fiable. De légers écarts de rendu peuvent persister au pixel sur l'extrémité d'un pinceau.

## Audit — données, sécurité, sauvegarde

- Corrections sérialisées dans le JSON V21.6 existant, incluant l'empreinte SHA-256 de l'image **et du masque de départ**, coordonnées normalisées et limites strictes. Pas de conversion automatique ou de rejet silencieux des retouches incompatibles.
- Les références d'image d'aperçu `/view` sont contrôlées et utilisent `api.apiURL('/view')` pour les préfixes de reverse proxy ComfyUI.
- Le widget purement graphique ne se sérialise pas dans les workflows. Seuls les traits sont persistés.
- Les échecs de visualisation et des alertes QA ne provoquent pas une perte du MASK calculé. Les erreurs de calcul ou de rejeu des traits, elles, ne sont pas dissimulées.
- Ancienne fenêtre invalidée lors d'une nouvelle exécution et après suppression du nœud.

## Audit — Cricut et limites

- Pas de recompression ni retouche des sorties des moteurs Cricut. Avec zéro correction, les exports PNG/SVG sont comparés octet pour octet entre masque direct et masque V21.10.
- Le dossier `00_IMPORTER_DANS_CRICUT` et le contrôle topologique hérités de V21.8 restent présents.
- L'inspection ne démontre PAS que SAM2/RMBG a correctement segmenté les sept images, ni qu'un PNG importé dans Design Space produira un contour physique conforme. Vérification et essai imprimante requis.
- Le diagnostic `largeur_mm=40` est un **repère indicatif** dans le nœud unifié et n'est pas automatiquement couplé à la largeur choisie dans Express : les seuils en mm doivent être interprétés avec cette réserve.

## Tests et éléments de preuve

- Nouveaux tests Python : neuf tests (rejeu de retouches, empreinte, 1er masque vide, aperçu source original, erreurs du panneau, trois workflows, comparaison de PNG/SVG complets).
- Nouveaux tests JavaScript : deux tests (schéma/URL/JSON et simulation du panneau : pinceau, zoom, fermeture, réouverture et invalidation de l'ancien affichage).
- Suites de V21.9.1 conservées et exécutées par groupes séparés pour éviter les blocages du lanceur déjà documentés.

## Reste à valider sur PC

1. Affichage ComfyUI version installée, vérification des DOM widgets et Nodes 2.0.
2. Manipulation à la souris/stylet sur de grands visuels avec DPI Windows et plusieurs masques.
3. Segmentation IA réelle sur RTX 3070 8 Go ; suivi VRAM.
4. Import réel, prévisualisation des contours et découpe Cricut Explore 5.

**Verdict :** extension bêta prête pour essais fonctionnels, pas une certification matérielle ou un import Cricut garanti pour toute image.
