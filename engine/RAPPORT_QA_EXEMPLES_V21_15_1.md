# Résultat du banc d'essai utilisateurs — 24 images

24 images cataloguées et comparées (15 images de la galerie et 9 du corpus ancien).
- 20 essais à résolution source entière et 4 en version de travail réduite, en raison de la limite d'exécution pour une image lourde.
- 24 rapports de diagnostic raster/SVG générés. Aucun algorithme IA GPU n'a été exécuté.
- 2 cas de planches Pokémon : nombre d'objets correct (24), silhouettes non rectangulaires, mais faibles fragments alpha et agrandissement à surveiller.
- 2 cas de planches escargots : 12 objets trouvés, **contours rectangulaires** dans les cellules (remplissage ~99,3 % de leur bounding box), donc rejet.
- Les 20 autres cas exportés sans masque IA se replient majoritairement en découpe rectangulaire ; ce repli ne satisfait pas une demande de sticker au contour du personnage.
- 22/24 scénarios de sticker contour analysés sont `BLOCKED`; 2/24 `REVIEW_REQUIRED`. **Ce résultat concerne les essais sans IA/masque, pas les autres usages carte/print.**
- Les 162 îlots alpha (>0) d'une planche escargots se réduisent à 12 au seuil alpha >20, distinction indispensable : ne pas déclarer 162 coupes réelles sur cette seule mesure.

Banc interne sur Linux, ni ComfyUI cible, ni RTX 3070, ni Design Space, ni Cricut Explore 5. G0.3 masques humains reste bloqué.
