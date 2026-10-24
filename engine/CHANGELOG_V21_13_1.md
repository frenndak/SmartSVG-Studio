# SmartSVG V21.13.1 — Changements

- Nouveau nœud `SmartSVGChooseSubjectV21131` : publie des vignettes réelles de 88 × 88 px, limitées à 32 et à 500 ko environ ; un clic choisit le numéro du sujet, et **nécessite une nouvelle exécution** du workflow. Repli garanti sur le champ numérique historique.
- Nouvelle interface JS `smartsvg_subject_picker_v21131.js`, sans données sérialisées dans les workflows, avec blocage des URLs de vignettes externes.
- Nouveau moteur `smartsvg_vector/qa_v21131.py` : décode de façon restrictive les chemins vectoriels générés (sans éléments externes) et recompose les régions remplies pour comparer avec l'image d'origine à la résolution de travail.
- Nouveau nœud `SmartSVGEditableColorsV21131` : exporte le SVG expérimental et deux aperçus (dont comparaison à trois panneaux), fournit un diagnostic JSON des zones manquantes, erreurs couleur, recouvrement de masque et fins détails potentiels.
- Deux workflows V21.13.1 intégrés : sélection vers Print Then Cut et sélection vers SVG multicouche avec `PreviewImage`.
- Le moteur historique d'export PNG/SVG Cricut et l'ancien moteur SVG multicouche V21.13 sont **inchangés** ; les anciens identifiants de nœuds sont enregistrés.
- Aucun modèle IA n'est installé par cette version ; les tests de segmentation GPU/Design Space restent nécessaires sur le poste cible.
