# Audit de développement SmartSVG V21.11

**Base :** archive vérifiée `ComfyUI_SmartSVG_Studio_V21_10_3_Installation.zip`, extraite indépendamment avant modifications.

## 1. Problème résolu

Les images opaques sans segmentation préalable donnaient parfois une carte rectangulaire ou un message ambigu. La V21.11 introduit une porte de décision stricte : toute fabrication de **sticker automatiquement détouré** passe d'abord par une proposition de masques non rectangulaires et non vides ; sinon l'opération est arrêtée.

## 2. Options de segmentation, par niveau de preuve

1. Alpha déjà valide : réutilisation des pixels d'origine ; aucune inférence revendiquée.
2. Dessins sur **fond blanc uniforme**, avec sujets séparés par bandes visuellement détectables : extraction déterministe OpenCV ; les cadres pointillés noirs sont exclus du repérage, les contours sombres liés au dessin sont conservés.
3. Images complexes : pont optionnel vers `SAM2Segment` de ComfyUI-RMBG, contrôlé au runtime. Des mises à jour du fournisseur peuvent invalider son contrat ; erreur explicite, pas de faux résultat.
4. Si l'image n'entre dans aucune catégorie : arrêt avec diagnostic. Le moteur ne simule ni modèle IA ni qualité physique.

## 3. Tests sur les sept images utilisateur

| Sujet | Sans IA | Portée |
|---|---|---|
| Planche 12 escargots, JPG | 12 propositions de masques, 12 composantes principales isolées | Test de fabrication complet positif : 12 PNG et 12 SVG + 1 planche, précontrôle local Cricut positif |
| Manga photographié sur écran | refus prudent | Fond non uniforme et trames de capture |
| Illustration cadeau avec texte | refus prudent | Décor et détails à segmenter via IA ou masque externe |
| Photo du leprechaun | refus prudent | Arrière-plan réel, finesse des objets |
| Affiche « Le malaise est en toi » | refus prudent | Entrelacements et texte multiples |
| Capture du canard musclé | refus prudent | Recadrage recommandé avant IA |
| Dessin Psyduck devant PC | refus prudent | Personnage / ordinateur / feu à définir explicitement |

**Important :** les six refus sont des résultats attendus du garde-fou sans IA, et non des preuves d'échec d'un modèle IA. Aucun SAM2 réel n'a été exécuté sur ces six images dans l'environnement de construction.

## 4. Non-régression et architecture

- Nouvelles classes `SmartSVGAutoMasksV2111`, `SmartSVGAutoExpressV2111`, sans remplacer les anciens IDs.
- Les ports et widgets des nœuds historiques restent inchangés ; le nouvel Express possède les mêmes 5 choix et 3 sorties.
- Fabrication PNG/SVG, génération HD, précontrôle Cricut et édition manuelle sont encore orchestrés par les modules déjà testés de V21.10.3.
- La carte rectangulaire explicitement choisie reste possible sans détourage.

## 5. Limites ouvertes avant certification

- Test frontend réel ComfyUI, Nodes 2.0 et plugins tiers.
- Test sur RTX 3070 8 Go (contrat SAM2/Florence2, mémoire, temps d'inférence, qualité visuelle).
- Import réel Design Space et découpe physique Explore 5 ; qualité des marges, angles et zones fines.
- Les SVG historiques représentent principalement les **contours**, pas des couches internes totalement éditables.
- Un détourage même non rectangulaire peut rester sémantiquement faux : l'éditeur et l'inspection restent nécessaires.

**Verdict :** V21.11 est une bêta fonctionnelle de détourage automatique prudent, non une certification universelle « toutes images ».
