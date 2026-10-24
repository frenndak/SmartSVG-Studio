# Installation / utilisation — SmartSVG Studio V21.6.1

**Cette archive remplace V21.6. Elle conserve le nœud `SmartSVGMaskEditorV216` et les workflows précédents.**

## Installation propre

1. Fermer ComfyUI.
2. Déplacer tout ancien dossier SmartSVG **hors de** `ComfyUI/custom_nodes/` (une seule version à la fois).
3. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.6.1` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI, puis faire un rafraîchissement complet du navigateur (`Ctrl+F5`).
5. Charger l'un des workflows :
   - `example_workflows/SmartSVG_Studio_V21_6_01_Corriger_Alpha_PNG.json`, pour un PNG avec transparence (nœud natif `InvertMask` requis à cet endroit pour inverser la convention de `LoadImage`).
   - `example_workflows/SmartSVG_Studio_V21_6_02_Creer_Masque_Manuel.json`, pour partir sans masque. Express est désactivé dans ce second exemple pendant la première édition : le réactiver une fois le masque dessiné et sauvegardé.
6. Exécuter le nœud d'édition, cliquer sur **Ouvrir l'éditeur de masques** et choisir le sujet à retoucher.

## Gestes dans l'éditeur

| Action | Geste |
|---|---|
| Ajouter au masque | `+ Ajouter`, puis dessiner |
| Retirer du masque | `− Retirer`, puis dessiner |
| Naviguer | `Déplacer`, puis glisser ; ou maintenir `Espace` et glisser ; clic du milieu |
| Agrandir / réduire | Molette sur l'image, boutons `+ Zoom`, `− Zoom` ou touches `+` et `−` |
| Recentrer complètement | `Adapter` ou touche `0` |
| Zoom à 100 % de la miniature | Bouton `100 %` |
| Annuler / rétablir | Boutons dédiés ou `Ctrl+Z` / `Ctrl+Maj+Z` (`Ctrl+Y` fonctionne aussi) |
| Sujet suivant | Sélecteur « Sujet » |
| Sauver les traits | **Enregistrer les retouches** puis relancer le workflow |
| Quitter sans sauver | Bouton « Fermer sans enregistrer » ou `Échap` |

**Le masque final reste calculé à la résolution de l'image source.** Le zoom jusqu'à 16× agrandit cependant une **miniature de 760 px maximum** : il aide à pointer localement, mais ne permet pas de voir des détails absents de cette miniature. Une inspection par tuiles natives est prévue pour la version suivante.

## Cricut : points à contrôler

- Contrôler la sélection (pas de fond sélectionné), le sens du masque et les zones manquantes.
- Sur plusieurs personnages, sélectionner et corriger les masques **un par un**.
- Après sauvegarde, **relancer le workflow** pour produire le vrai PNG transparent et le SVG (aucun export automatique à la simple fermeture).
- Dans Design Space, contrôler la taille physique, les lignes de découpe et les éventuels trous ou îlots avant toute découpe de matériau.
- La compatibilité physique Cricut Explore 5 et les performances réelles SAM2 / Florence-2 sur RTX 3070 restent **à tester sur PC**.

## Vérification optionnelle

Dans le dossier de l'extension, lancer successivement :

```text
python verify_package_v2161.py --integrity-only
python verify_package_v2161.py --suite 1
python verify_package_v2161.py --suite 2
python verify_package_v2161.py --suite 3
python verify_package_v2161.py --suite 4
python verify_package_v2161.py --suite 5
python verify_package_v2161.py --javascript
```

Le contrôle attend 646 tests Python et 35 tests JavaScript. Node.js >= 18 est utilisé seulement pour les tests JavaScript, pas pour exécuter les nœuds ComfyUI. Les cinq suites Python sont à lancer séparément afin de limiter les interférences de mémoire.

**Limites :** pas encore validé graphiquement dans ton navigateur ComfyUI précis, notamment avec Nodes 2.0. Si l'éditeur n'apparaît pas, vérifier la console JS, l'installation en dossier unique, l'actualisation forcée et la présence du nœud `SmartSVGMaskEditorV216`.
