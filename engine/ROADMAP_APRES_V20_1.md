# SmartSVG Studio — continuité du chantier après la parenthèse Line Art V20.1

## Statut de départ

- **Socle V20** : segmentation Florence-2/SAM2, raffinement BiRefNet ciblé, cartes d'incertitude, masque original toujours préservé, QA transactionnelle, 243 tests historiques (CPU et modèles simulés).
- **Ajout V20.1** : nouveau nœud CPU pour les dessins photographiés / scannés : cadre, perspective, correction de fond, traits, export monochrome SVG, proposition de silhouette.
- **Validation non acquise** : vraie segmentation sur RTX 3070 8 Go, qualité de séparation mains/chopes, matting cheveux/barbe, et import/découpe réelle Cricut.

## Ordre recommandé — **reprendre le chantier principal sans repartir de zéro**

### V20.1.1 — Contre-expertise spécialisée dessins

Évaluer au minimum un scan, une photo de feuille, une capture d'écran native et une photo d'écran ; mesurer taux de recadrage correct, qualité des traits, SVG rendu vs PNG, faux contours et performance CPU. Corriger à partir des échecs. Séparer explicitement les découpes vérifiées des propositions.

### V20.2 — Raccordement contrôlé Line Art ↔ segmentation IA V20

Quand le cadre est nettoyé, proposer l'envoi de l'image préparée au segmentateur pour demander *le personnage seul* ; coordonner les masques avec la transformation géométrique; refuser toute promotion automatique si ambiguïté. Conserver original et résultat non destructif. Aucun nouveau modèle obligatoire.

### V20.3 — Banc de validation GPU sur RTX 3070 8 Go

Faire tourner Florence-2 + SAM2 puis matting ciblé, capture des profils mémoire corrigés et de la durée ; tests froid/chaud, indisponibilité modèle, coût CPU/GPU, dérive de sorties et robustesse OOM. Exécuter séquentiellement ; ne pas annoncer de VRAM réelle sans avoir un vrai log sur ce PC.

### V20.4 — Qualité IA et détourage de photos complexes

Tester personnages/objets/cheveux/barbes/mains/chopes sur annotations manuelles alignées : IoU/Dice, F1 des contours, faux îlots, erreurs de superposition. Choix conservateur et annoté des masques, refus de faux progrès. Comparer SAM2 / BiRefNet / matting selon données disponibles.

### V20.5 — Fiabilisation Cricut en production

Tester ouverture des PNG/SVG dans Design Space, silhouette du contour extérieur, marges en mm à DPI maîtrisé, dimensions et Print Then Cut, essais réels sur Cricut Explore 5. Publier protocole de validation ; ne jamais annoncer « prêt Cricut certifié » uniquement après tests logiciels.

## Règles de continuité

1. Ne pas retirer les anciens nœuds ComfyUI avant migration vérifiée.
2. Ne jamais écraser les PNG historiques ou les masques d'origine.
3. Toujours marquer comme **brouillon** les silhouettes sans validation sémantique ni humaine.
4. Livrer à chaque itération archive installable, tests reproductibles et rapport de changement.
5. Vérifier les résultats sur les trois images de référence déjà utilisées (12 escargots, femme/cadeau, personnage/chopes), en ajoutant le nouveau dessin manga.
