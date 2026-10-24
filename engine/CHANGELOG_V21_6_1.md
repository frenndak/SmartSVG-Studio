# SmartSVG Studio — V21.6.1 (23 octobre 2026)

## Portée

Mise à jour **du frontend uniquement** de l'éditeur de masques V21.6. Aucun changement des algorithmes Python de vectorisation, de la fabrication Cricut, du format `retouches_json`, des ports ComfyUI, des cinq réglages Express, ni des nœuds existants. Les deux workflows V21.6 restent réutilisables sans conversion.

## Ajouts

- Zoom de l'aperçu (molette, boutons + / −, 100 %, Adapter), centré sur le pointeur.
- Déplacement dans une fenêtre à dimensions bornées (outil Déplacer, ou Espace + glisser), avec retenue automatique de la feuille dans le champ visible.
- Position affichée en pixels de l'image source, distincte de la résolution de la miniature.
- Contrôles clavier : Ctrl+Z / Ctrl+Maj+Z, Ctrl+Y, +, −, 0, Échap ; fermeture nettoyant les écouteurs.
- Échantillonnage des traits adapté au zoom pour mieux tracer les courbes (limites de points conservées).
- Mise en cache de la couche de traits validés : seuls les coups en cours nécessitent une couche temporaire.
- Fermeture et chargements asynchrones mieux encadrés ; prévention des ouvertures multiples.
- Navigation isolée des outils de peinture : un déplacement n'est jamais enregistré comme trait.

## Limite importante

**Le zoom agrandit l'aperçu (maximum 760 px de côté), pas une tuile de l'image native.** Les coups de pinceau sont rejoués sur le masque à pleine résolution, mais les petits détails absents de la miniature ne peuvent pas être révélés par zoom. La future solution est un aperçu en tuiles à résolution source ; la V21.6.1 ne prétend pas le remplacer.

## Validation

- 646 tests Python historiques (50 + 300 + 227 + 52 + 17) exécutés en cinq processus séparés.
- 35 tests JavaScript au total (25 historiques, 10 nouveaux pour panoramique/zoom/persistance et les scénarios runtime).
- Aucune modification des fichiers Python de fabrication ni des workflows V21.6.
- Tests du frontend basés sur un DOM simulé ; **pas de test réel Windows / Nodes 2.0 / RTX 3070 / Cricut physique**.
