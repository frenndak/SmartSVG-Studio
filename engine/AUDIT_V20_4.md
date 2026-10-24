# SmartSVG V20.4 — Contre-expertise V20.3 et développements

## Socle vérifié

- Archive source V20.3 : `ComfyUI_SmartSVG_Studio_V20_3_Installation.zip` ; tests hérités : 350/350.
- Architecture héritée inspectée : `gpu_budget_v203.py`, `node_v203.py`, `lineart_ai_v202.py`, `adaptive_refiner_v199.py`.
- Le prévol CUDA vérifie seulement une quantité instantanée de mémoire libre avant l'appel IA. **Il ne garantit ni l'absence d'OOM, ni la précision des masques, ni la sécurité physique du tracé.**
- En V20.3, la sélection de masques utilise une surface/centralité heuristique : un mauvais objet peut être retenu même avec un score important. Ce comportement historique est conservé pour la compatibilité ; la V20.4 fournit un contrôle indépendant.
- Les photos avec masque absent ne doivent pas fabriquer de silhouettes IA.

## Nouveautés réalisées V20.4

- Nœud `SmartSVGLineArtV204`: hérite du V20.3, analyse le masque exporté et l'encre du dessin, produit un aperçu et un rapport dans `QA_QUALITE_V20_4`. Les exports historiques restent inchangés.
- Nœud indépendant `SmartSVGMaskQualityV204`: reçoit des masques SAM2/BiRefNet/externe, transmet exactement le tenseur reçu et fournit un rapport de géométrie/chevauchement.
- Contrôles: masque vide, surface improbable, composantes/îlots, trous internes, contact au bord, complexité périmétrique, proportion de traits exclus, chevauchement et doublons potentiels.
- Deux codes de sortie prudents : `A_VERIFIER` (aucune preuve d'exactitude) et `RISQUE_ELEVE` (anomalie géométrique). Pas de notation «validé Cricut».
- Contraintes: contrôle de dimensions/types/NaN et budget de 8 millions de pixels de masques; rapports atomiques, sauvegarde des aperçus en fichier temporaire puis renommage; pas d'altération automatique du masque.

## Vérifications

- 350 tests hérités V20.3 réexécutés.
- 33 nouveaux tests V20.4, dont masques 0/1, 0/255, NaN, trous, bord, chevauchement, panne QA et **comparaison octet par octet** de la sortie Cricut V20.3/V20.4.
- Validation depuis extraction neuve du ZIP avec `python verify_package_v204.py` ; manifeste et six workflows contrôlés.

## Limites importantes

- Une forme géométriquement correcte peut être le mauvais personnage, un accessoire ou un arrière-plan. Aucun modèle ne peut inférer la certitude de justesse d'après ces scores seuls.
- Les tests IA utilisent des masques synthétiques ou fournis. **Aucune inférence CUDA sur la RTX 3070 réelle ni test physique Cricut n'a été réalisé** ici.
- Le matting alpha des cheveux n'est pas amélioré par ces vérifications ; il faudra des masques réels et des annotations de référence pour décider d'un raffinement automatique.
- Le nœud «choix Cricut» reste distinct : «contour extérieur» n'est pas «tous les traits». Aucun changement des opérations précédentes.

## Suite du chantier

- V20.5 : normalisation physique des contours et vérification des chemins à importer dans Design Space, sans confusion entre impression-découpe et coupe de chaque trait.
- V21 : intégration des modules photo/line-art/planches multicouches et évaluation des modèles locaux avec véritables annotations et relevés GPU.
