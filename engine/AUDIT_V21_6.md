# SmartSVG V21.6 — Contre-expertise ciblée multi-passes

Date : 23 octobre 2026. Base : archive utilisateur V21.5.1 (382 fichiers suivis au manifeste), suite antérieure 629 tests Python + 19 tests JS. **L'interface graphique réelle n'est pas validée**.

## Passe A — Non-régression de l'architecture

- `node_v216.py` ajoute le seul identifiant de nœud `SmartSVGMaskEditorV216`. `node_v2151.py` et l'ensemble du moteur existant restent à l'octet près identiques.
- Les cinq réglages Express, trois sorties Express, types de port ComfyUI et workflows V21.5.1 restent inchangés. Aucun endpoint HTTP personnalisé.
- Correctif de convention ComfyUI : le `MASK` de `LoadImage` est **1-alpha**. Le workflow PNG transparent passe par le nœud natif `InvertMask` pour que **1 = sujet** dans SmartSVG ; sans cela le contour aurait été inversé.
- Le nœud de retouche est aussi `OUTPUT_NODE=True` : le workflow manuel peut afficher son éditeur lorsque le nœud Express est provisoirement muet pour éviter une exportation erronée de masque vide.
- Les retouches sont des opérations sur un port `MASK` en amont de la fabrication ; le masque modifié par l'utilisateur est réellement utilisé pour produire les PNG/SVG.

## Passe B — Algorithme de retouche

- Traits ordonnés, sélection d'instance, coordonnée x/y normalisée entre 0 et 1, rayon relatif au plus petit côté de la source.
- Relecture déterministe à résolution native par PIL : remplissage ou retrait ; le dernier trait appliqué gagne. Les pixels non peints préservent exactement le masque flottant initial.
- Empreinte conjointe de l’image et des masques de départ, avec géométrie/version vérifiées, JSON strict et bornes de mémoire/complexité. Aucune retouche implicite si la source a changé.
- Pour les sources PNG transparentes, l’empreinte intègre les pixels alpha s’ils arrivent au nœud en RGBA, et le `MASK` de `LoadImage` après inversion : modifier seulement l’alpha est donc détecté. Pour les 24 objets, les masques restent séparés.

## Passe C — Interface et persistance

- Le widget d'affichage DOM n'est pas sérialisé. Les données de retouche sont conservées dans le widget `retouches_json` standard du nœud V21.6 ; elles survivent à la sauvegarde du workflow.
- Les actions sont explicites : sélectionner un sujet, ajouter/retirer, annuler/rétablir, enregistrer ; la fabrication demande ensuite une nouvelle exécution.
- Une erreur de miniature/UI ne doit pas invalider un `MASK` correctement calculé. Références `/view` validées et construites avec `api.apiURL('/view')` pour les proxys.
- Éviter l'éditeur bloqué par un JSON obsolète : bouton dédié de suppression des retouches enregistrées.
- Limitation actuelle : pas de zoom/panoramique pour l'édition fine, et les événements exceptionnels du frontend peuvent laisser des aperçus anciens jusqu'à la prochaine exécution réussie.

## Passe D — Coûts et sécurité

- 5 Mp max/image, 32 sujets, 50 M pixels cumulés, 400 traits, 12 000 points cumulés, 350 Ko JSON. Le moteur calcule les corrections sur CPU et transfère le tensor final vers le périphérique d'origine.
- Le frontend accepte uniquement les références de miniatures signées par une forme contrôlée (`ed_<id>_image.png` et `ed_<id>_maskXX.png`), pas de chemin de disque ni URL arbitraire ; toutes les chaînes de l'interface sont placées dans `textContent`.
- Prévisualisations temporaires au plus 96 fichiers, 72 h de rétention lors de la prochaine publication ; aucun fichier utilisateur non préfixé n'est supprimé.
- Les données de miniatures restent visibles par les utilisateurs déjà autorisés sur ComfyUI ; pas de promesse de confidentialité au-delà du serveur.

## Passe E — Vérification

- 629 tests historiques Python, 17 nouveaux tests V21.6, 19 tests historiques JS et 6 nouveaux tests V21.6 = **671 tests** à vérifier sur archive finale.
- Production réelle sur un jeu **synthétique** de 24 masques (6×4) et 2 planches : **101 fichiers PNG/SVG** comparés en SHA-256 avec et sans passage par le nouveau nœud, tous identiques en absence de retouches.
- Tests de bout en bout supplémentaires : masque peint sur image vierge → entrée `MASK` Express → fichiers Cricut ; masque effacé sur le bord d’un sujet → modifications constatées dans les empreintes PNG **et** SVG.
- Évaluation pas effectuée sur les dessins Pokémon originaux (non présents dans les sources jointes), ni sur le frontend graphique ComfyUI réel, RTX 3070 ou Cricut physique.

## Prochain chantier V21.6.x / V21.7

1. Validation manuelle frontend sur Windows/Nodes 2.0, navigateur Web et proxy réel.
2. Zoom, déplacement (pan) et loupe pixel pour bords et sujets étroits.
3. Masques de contours et intersections : QA par sujet, îlots, trous et simplification de chemins SVG.
4. Profil Cricut « stickers contour » calibré à l'export et avis de pré-découpe, découpe témoin sur la Explore 5.
5. Mesures VRAM / SAM2 / Florence-2 sur RTX 3070 8 Go, avec échantillons dessin/photo.
