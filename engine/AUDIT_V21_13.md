# SmartSVG Studio V21.13 — Contre-expertise technique

**Source :** archive V21.12.2 extraite dans un dossier vierge. Le code historique est conservé ; un nouveau point d'entrée enregistre les nouveaux nœuds.

## Vérifications positives

- Contrat ComfyUI : deux nouveaux nœuds déclarés, les anciens identifiants conservent les mêmes classes et ports.
- Sélection sur des masques réels : planche Pokémon fond noir = **24 sujets** reconnus, planche escargots fond blanc = **12 sujets** reconnus ; le 3e sujet a été sélectionné sans altérer les masques.
- Premier SVG éditable : une illustration de référence synthétique produit **quatre groupes colorés et six formes** SVG, avec largeur explicite de 50 mm et sans balise image raster. Les calques sont techniquement modifiables.
- Rejet contrôlé : masque absent, masque transposé, trop rectangulaire, photo trop riche en couleurs, sujet hors index.
- Recadrage du masque sélectionné : le SVG représente la zone du personnage avec marge, pas la page d’origine ; largeur physique liée à ce recadrage.
- Dossier de sortie : création unique `O_EXCL`, pas de remplacement silencieux du SVG existant.
- Aucun changement aux modules de génération PNG/SVG Cricut antérieurs ; la fabrication de Print Then Cut repose toujours sur leur validation locale précédente.

## Limites et risques

- SVG multicouche = **quantification de couleur et formes**, pas reconstruction sémantique de cheveux, texte, visage ou objets distincts. Les trous, les dégradés et les contours fins demandent une inspection manuelle.
- Le nouveau sélecteur **ne récupère pas automatiquement les petits fragments** oubliés par le segmentateur IA : il signale les fragments déjà présents dans le masque sélectionné.
- Les sorties SVG vectorielles ne sont pas certifiées compatibles avec le procédé Print Then Cut ; utiliser les PNG du dossier Cricut pour imprimer/découper.
- Aucun test réel du frontend Nodes 2.0, des modèles sur RTX 3070 ou de la découpe de la Cricut Explore 5.

## Chantier prioritaire V21.13.1

1. Inspection visuelle côte à côte raster/vecteur, suivi de la précision des détails et prévisualisation du parcours de lame.
2. Sélection graphique à la souris au lieu d'un numéro lorsque les masques ont des noms.
3. Réconciliation assistée des accessoires détachés, sans fusion automatique irréversible.
4. Test d'import réel dans Design Space et banc de tests RTX 3070 pour l'IA.
