# SmartSVG Studio — V21.12.1 : plan, corrections et critères de validation

## P0 — Fonctionnalités mises en place

- Routage d'image **sans modèle** : bord blanc uni, bord noir uni, transparence potentielle, scène opaque complexe. Il ne reconnaît pas les personnages ou le texte.
- Planche multicolore sur fond noir : 24 composants principaux du visuel Pokémon détectés en tant que propositions de silhouettes. Trois petites zones secondaires potentiellement manquantes sont signalées.
- Planche de 12 escargots préservée : 12 masques obtenus et 12 PNG localement précontrôlés au cours du développement.
- Cas JPEG / alpha vide 64×64 de `LoadImage` correctement ignoré pour laisser fonctionner la voie fond noir.
- Aucun fichier Cricut généré lorsqu'un masque sûr manque.

## P1 — Sécurité et ergonomie

- Rapport de contrôle géométrique par sujet : cadre, surface, nombre d'îlots, complexité du contour et informations d'échelle indicative.
- Deux états lisibles : **précontrôle géométrique uniquement** et **révision visuelle prioritaire** ; aucun état n'affirme une découpe physique réussie.
- Cinq workflows guidés, dont un diagnostic rapide du type d'image sans charger les modèles GPU.
- Conservation des cinq réglages Express et des IDs historiques.

## P2 — Évolutions suivantes

- Ajouter un choix explicite « sujet principal / tous les sujets / conserver le texte » dans les scènes complexes, sans prétendre qu'un texte est lu par OCR.
- Profil de marge et d'offset plus robuste pour les éléments très fins (membres, feuilles, appendices).
- Simplifier la recherche de nœuds historiques dans ComfyUI, sans casser les workflows existants.

## Critères sur les neuf images réelles

| Test | Exigence | Statut |
|---|---|---|
| 12 escargots sur blanc | 12 masques | **Atteint sans IA** |
| 24 Pokémon sur noir | 24 masques distincts et détection des fragments | **Atteint pour les masques**, détails à inspecter |
| Manga photo | Pas de faux détourage | **Refus prudent sans IA** |
| Cadeau et texte | Pas de faux détourage / OCR fictif | **Refus prudent sans IA** |
| Leprechaun photo | Exiger IA ou intervention | **Refus prudent sans IA** |
| Affiche fantasy A | Texte / personnages non certifiés | **Refus prudent sans IA** |
| Affiche fantasy B | Texte / personnages non certifiés | **Refus prudent sans IA** |
| Homme dans atelier | Ne pas confondre environnement et sujet | **Refus prudent sans IA** |
| Couverture coréenne | Ne pas fabriquer un contour rectangulaire trompeur | **Refus prudent sans IA** |

## Points à régler avant une validation complète

**P0 en attente :** l'essai de fabrication complète de 24 sujets a dépassé la limite de temps du contrôle local. Les PNG individuels avaient commencé à être générés, mais l'export complet n'a pas été certifié. La prochaine passe doit profiler les planches, les rééchantillonnages et l'amélioration HD, puis optimiser le traitement par lots.

**P0 matériel :** charger au moins un fournisseur réellement installé (BiRefNet / RMBG / SAM2) dans le ComfyUI de l'utilisateur, mesurer RAM/VRAM avec RTX 3070 8 Go, et comparer visuellement les résultats sur les sept images opaques.

**P0 fabrication :** importer les PNG finis dans Cricut Design Space et tester au moins une découpe réelle Explore 5 ; le logiciel n'émule pas son moteur propriétaire.

**Définition de réussite :** n'affirmer « fonctionnement de bout en bout validé » que lorsque le ZIP s'installe, le workflow s'exécute, le masque est confirmé sur le bon sujet, les PNG/SVG sont complets, Design Space importe au bon format et la découpe physique se termine correctement.
