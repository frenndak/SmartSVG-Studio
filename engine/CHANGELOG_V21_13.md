# SmartSVG Studio V21.13 — Développement

- **Nouveau nœud `SmartSVGChooseSubjectV2113`** : sélection 1–32 parmi les masques proposés, rapport d'îlots potentiellement détachés et conservation sans mutation du masque initial.
- **Nouveau nœud `SmartSVGEditableColorsV2113`** : vectorisation expérimentale des dessins simples en groupes SVG de couleur `g/path` réellement éditables, 2–16 classes de couleur, trous intérieurs représentés en `fill-rule=evenodd`.
- Masques valides obligatoires pour les images opaques, rejet des photos complexes / masques rectangulaires, plafond de 5 MP entrée et 600 kpx de traitement vectoriel, 1200 formes/110 000 points/5 Mo de SVG.
- Recadrage automatique sur les limites du masque sélectionné avant attribution de la largeur physique ; une image de planche entière ne rend plus le personnage miniature.
- Sauvegarde des SVG sans écraser les fichiers existants, largeur physique explicite, rapport des formes omises et de la quantification.
- Deux nouveaux workflows de démonstration : sélectionner un personnage avant l'export Cricut / sélectionner un personnage puis fabriquer un SVG multicouche expérimental.
- **Aucune modification du moteur historique PNG, de l'IA RMBG ni de la production Print Then Cut** ; tous les anciens IDs de nœuds sont conservés.
- Des tests adversariaux couvrent chemins SVG réels, absence de PNG embarqué, refus des photos, dimensions, sélection de fragments et non-écrasement des sorties.
