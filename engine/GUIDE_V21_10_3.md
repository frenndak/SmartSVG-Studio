# Installer SmartSVG Studio V21.10.3

1. Fermer ComfyUI. Déplacer toutes les anciennes versions SmartSVG hors de `ComfyUI/custom_nodes` (ne conserver qu'une seule extension active).
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.10.3` de l'archive dans `ComfyUI/custom_nodes/`.
3. Redémarrer ComfyUI puis recharger la page. Pour le premier essai, ouvrir l'un des trois workflows V21.10 du dossier `example_workflows/`.
4. Brancher la source et un masque correct pour obtenir un contour de personnage. Sans masque, l'éditeur unifié commence avec une sélection vide ; le nœud Express peut alors avoir besoin d'être désactivé pendant l'édition initiale.
5. Relancer le workflow après avoir enregistré les retouches. Dans le projet, ouvrir `00_IMPORTER_DANS_CRICUT` et téléverser le PNG correspondant dans Design Space en mode **Flat Graphic / Imprimer puis découper**.
6. Vérifier le contour, les dimensions et la disposition ; imprimer depuis Design Space puis faire une découpe d'essai. Ne pas superposer le SVG de contour au PNG.

## Amélioration HD

Les PNG de qualité HD restent dans `06_HD_AUTOMATIQUE_V21_7_1`. V21.10.3 crée une preuve `sujet_XXX_HD.provenance.json` pour vérifier un ancien dérivé lors d'une relance. Un fichier HD créé par une version antérieure sans cette preuve est conservé mais n'est pas réutilisé comme s'il venait du résultat actuel. Utiliser un nouveau dossier projet pour repartir de zéro.

## Diagnostic des contours

Les alertes en millimètres affichées dans l'éditeur supposent **40 mm**. Ce n'est pas nécessairement la largeur réellement réglée dans Express ; le contrôle final dans Design Space reste essentiel.

## Vérification

Depuis le dossier de l'extension :

```shell
python verify_package_v21103.py --integrity-only
python verify_package_v21103.py --targeted
python verify_package_v21103.py --javascript
python verify_package_v21103.py --suite 1
```

Les suites 1 à 12 s'exécutent séparément ; Node.js sert uniquement aux tests JavaScript. Les modèles IA et la découpe physique ne sont pas testés par ces commandes.
