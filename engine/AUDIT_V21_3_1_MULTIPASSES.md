# SmartSVG V21.3.1 — Contre-expertise en cinq passes

## 1 — Reproductibilité et provenance
- Base issue de l'archive d'installation V21.3 (aucune réécriture du moteur historique).
- Défaut reproduit : `segment_instances(detector=lambda ...)` annonçait `source_boites=FLORENCE_2_EXECUTE` malgré un détecteur injecté. **Corrigé** dans le nouveau moteur; les démonstrations ne sont pas présentées comme de vraies inférences.
- Vérification des nœuds V21.3 conservés et des nœuds V21.3.1 séparément enregistrés.

## 2 — Qualité des instances
- Défaut reproduit : une collision entre deux masques était signalée uniquement sur la deuxième instance. **Corrigé symétriquement**.
- Nouveau contrôle sur les pixels d'une proposition empiétant dans la boîte d'un autre sujet, hors boîte du sujet concerné : **avertissement, pas suppression automatique**, car les superpositions sont possibles.
- Les boîtes et masques demeurent des hypothèses nécessitant inspection visuelle.

## 3 — Erreurs et ressources GPU
- Défaut reproduit : la boucle pouvait avaler une véritable erreur `CUDA out of memory` comme échec d'un objet et poursuivre le lot. **Arrêt immédiat** pour cette catégorie d'erreur.
- Les erreurs locales non critiques continuent de permettre une sortie partielle *explicitement signalée*.
- Le contrôle d'empiètement utilise des cartes de taille recadrage, non des copies plein format supplémentaires.
- Le seuil libre de mémoire GPU reste préventif; **aucune preuve de tenue sous 8 Go** sans exécution sur la RTX 3070.

## 4 — Exports Cricut et non-régression
- Le chemin de production V21.2/V21.1 reste inchangé; le correctif ne remplace pas les masques source ni les SVG de contours historiques.
- Tests de comparaison d'array des masques V21.3 et V21.3.1 sur scènes contrôlées sans défaut.
- Conservation des modules historiques dans l'archive, validation des workflows et manifeste SHA-256.
- Les bords fins, l'échelle physique et la découpe physique nécessitent toujours un test de Design Space.

## 5 — Ergonomie et cas réels
- Saisie possible des noms français (ex. `renard`) dans la boîte JSON du guidage avancé.
- Tous les profils Express continuent avec cinq réglages après l'entrée image; nouveaux nœuds versionnés et sept nouveaux workflows corrigés.
- Prévisualisations de guidage sur des images réelles : **ce ne sont pas des masques IA**.

## Risques encore ouverts
1. Critique : qualité réelle et compatibilité de l'interface RMBG chargée sur la version ComfyUI de l'utilisateur.
2. Élevé : recouvrement des trois renards et risque de segmentation de plusieurs sujets dans un même masque.
3. Élevé : qualité des bords fins (fourrure, cheveux, mains) et résolution native de l'image.
4. Moyen : performances GPU/VRAM sur RTX 3070 8 Go non mesurées.
5. Moyen : import SVG/PNG, dimensions et découpe physique sur Cricut Explore 5 non vérifiés.

Voir `README_V21_3_1.md` et `verify_package_v2131.py`.
