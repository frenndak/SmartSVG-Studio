# Contre-expertise multipasses — SmartSVG V21.6.1

Date : 23 octobre 2026. Base : archive V21.6 déposée par l'utilisateur, 399 éléments. Périmètre du correctif : frontend de l'éditeur uniquement.

## Passe 1 — Géométrie d'écran et résolution

L'ancienne fonction `position()` convertissait la position du pointeur en coordonnées proportionnelles à un canevas statique. Un zoom CSS naïf aurait conduit à dessiner au mauvais endroit. Une géométrie explicite `(scale, x, y)` bornée transforme maintenant les positions écran vers les coordonnées UV. Les bornes pan assurent que les bords de la feuille restent accessibles et que l'image ne peut pas disparaître complètement. Le zoom autour du curseur conserve la position de l'objet pointé. Après redimensionnement, la feuille est recentrée ou recadrée.

Le modèle est isolé et testé dans `web/js/smartsvg_editor_model_v216.mjs`; aucune donnée de zoom ne pollue le workflow ou les fichiers SVG.

## Passe 2 — Expérience utilisateur et sécurité des interactions

Modes : « Ajouter », « Retirer », « Déplacer ». Le clic milieu et la touche Espace activent le déplacement. La molette et les raccourcis changent le zoom. La séquence pointerdown/move/up suit un seul identifiant de pointeur, et pointercancel jette le trait non terminé. Les mouvements de navigation ne sont pas sérialisés. Deux ouvertures simultanées de l'éditeur sont bloquées. Les gestionnaires clavier et d'observation sont libérés à la fermeture.

Les masques chargés asynchrones ont un jeton de session ; lorsqu'un autre sujet est sélectionné, l'ancienne réponse ne remplace pas le nouveau calque.

## Passe 3 — Performance et sécurité mémoire

La V21.6 recréait un calque graphique complet pour rejouer tous les traits à chaque mouvement. La V21.6.1 met en cache les traits achevés par sujet et révision. Lors du mouvement, elle ne compose que le trait actif. Les plafonds 400 traits, 1500 points/trait, 12000 points cumulés et 350 Ko JSON sont inchangés. Le zoom maximal est borné à 16× pour limiter les surfaces CSS agrandies ; la taille mémoire du canevas reste égale à la miniature (≤ 760 × 760).

## Passe 4 — Compatibilité, rendu de fabrication

Le nom de nœud `SmartSVGMaskEditorV216`, ses ports, le JSON version 1 et les deux workflows de la V21.6 sont inchangés. Les moteurs Python historiques et la sortie Express restent exactement identiques. Le test CPU existant de 24 sujets / deux planches vérifie la conservation des 101 PNG/SVG sans retouches et le changement du PNG et du SVG après application d'une retouche.

La sérialisation frontend suit les règles ComfyUI : `widget.serialize=false` pour le workflow et `widget.options.serialize=false` pour le prompt, sur le **widget d'aperçu uniquement**. Le champ `retouches_json` reste sérialisable.

## Passe 5 — Limites et risques ouverts

| Sujet | État |
|---|---|
| Position pinceau / zoom / pan / annulation | Testé par simulation JavaScript |
| Sauvegarde du JSON V21.6 | Conservée et testée |
| Algorithmes Python et suites historiques | Inchangés, tests verts |
| Exécution navigateur réel ComfyUI / Nodes 2.0 | Non testée |
| Vue à l'échelle native sur grands dessins (tuiles) | Non implémentée : **zoom sur miniature 760 px** |
| Pinch tactile à deux doigts / stylets avec pression | Non implémenté ; bouton Déplacer disponible |
| Affichage d'un curseur circulaire de rayon réel | À faire |
| IA SAM2 / Florence-2 sur RTX 3070 8 Go | Non testé |
| Import Design Space, découpe Explore 5 | Non testé |

## Résultats de validation

- 646 tests Python : 50 + 300 + 227 + 52 + 17.
- 35 tests JavaScript dont tests géométriques (zoom ancré, découpage/pan extrêmes, limites, courbes serrées), tests de non-retouche pendant le déplacement et de réouverture.
- Vérificateur autonome `verify_package_v2161.py` ; nouveau manifeste SHA-256 V21.6.1 ; 2 workflows historiques V21.6 contrôlés.
- Comparaison des fichiers hérités V21.6 : exactement trois fichiers existants sont intentionnellement modifiés (modèle JS, UI JS, simulation JS). Aucun fichier de moteur Python ou de workflow n'est modifié.

## Références techniques

- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/extensions/development.md
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/docs/WIDGET_SERIALIZATION.md
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/lib/litegraph/API.md

## Priorités de V21.7

1. Fournir une inspection native de détails par tuiles côté serveur (pas seulement l'agrandissement de la miniature), avec nettoyage et contrôle mémoire.
2. Afficher la silhouette exacte du pinceau et le contour de masque en temps réel.
3. Ajouter les diagnostics de découpe : îlots, trous non désirés, intersections, marges et simplification SVG.
4. Réaliser les essais de la vraie interface ComfyUI et d'une Cricut Explore 5 avant de considérer la chaîne « production » validée.
