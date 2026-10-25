# SmartSVG Studio — V21.15.5 (candidat, G2.6 : zones à inspecter)

**Base requise :** V21.15.4 (inspecteur de silhouettes). **Nature :** amélioration additive, pas une certification Cricut ni un moteur de retouche automatique.

## Fonction développée

Lorsqu'une vignette affiche un masque contenant un sujet principal et d'autres composants disjoints, le panneau peut désormais **localiser visuellement jusqu'à 12 zones** à revoir :

- Distinction `FRAGMENT_SEPARE` (au moins 8 px) / `MICRO_FRAGMENT` (1–7 px). Seuil heuristique : aucun accessoire n'est effacé.
- Rectangles englobants dans les coordonnées **de l'image source** `[x0, y0, x1, y1)`, avec les bornes supérieures exclusives.
- Projection des rectangles sur la vignette historique 88×88, en conservant le recadrage et les marges de V21.13.1 ; repères orange superposés, sans modification des pixels.
- Coordonnées disponibles en texte accessible ; nombre de zones non affichées si les 12 repères sont dépassés.
- Liste des bords touchés : `GAUCHE`, `HAUT`, `DROITE`, `BAS`.
- Abandon prudent de l'inspection CPU si le masque contient plus de 20 000 composants connectés. La sélection historique du nœud est conservée.

## Compatibilité

Identifiants ComfyUI et ports inchangés. Le rapport de l'inspecteur `smartsvg_subjects_v21154` reçoit les champs facultatifs `zones_a_examiner`, `zones_non_affichees`, `bords_touches`. Les anciens rapports sans ces champs continuent à afficher les boutons de sélection. Aucun changement de moteur IA, d'export Cricut, de format `.smartsvg` ou de baseline.

## Vérification

```bash
cd engine
python -m unittest tests.test_v2113 tests.test_v21131 tests.test_v21151_image_qa tests.test_v21152 tests.test_v21154_subject_inspector tests.test_v21155_fragment_locations -q
for f in tests/*.mjs; do node --test "$f"; done
```

**Tests locaux :** 47 tests Python ciblés, 14 scripts JavaScript et compilation Python passés. La suite Python globale n'est pas comprise dans ces preuves ; les essais en interface native ComfyUI, l'import réel dans Design Space, la RTX 3070 et la découpe Explore 5 n'ont pas été effectués.

## Limites et sécurité

Un composant séparé peut être un accessoire, un œil, un signe typographique ou un décor voulu. **Ne rien supprimer sans vérifier l'original.** Les repères sur un aperçu de 88 px peuvent différer d'environ un pixel de la zone exacte ; les coordonnées source sont fournies pour un examen approfondi. Si aucune vignette n'est disponible, les informations restent textuelles. Les données UI sont bornées et leurs coordonnées validées avant affichage.

## Retour arrière

Restaurer seulement les deux fichiers modifiés depuis V21.15.4 :
`engine/smartsvg_core/subject_inspector_v21154.py` et
`engine/web/js/smartsvg_subject_inspector_v21154.js`.
Retirer les tests V21.15.5 et le présent document. La roadmap v3.2 et l'archive source V21.15.2 restent immuables.

## Travail suivant

Associer une zone signalée à l'éditeur de masques V21.6 avec confirmation explicite, reprise des versions du masque, et annuler/rétablir. Aucun clic sur une vignette ne doit déclencher une modification destructive ou une fabrication.
